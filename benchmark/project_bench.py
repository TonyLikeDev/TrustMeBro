#!/usr/bin/env python3
"""Project benchmark: working on a half-finished project, with and without tricklord.

The project is benchmark/fixture/shoplite (35 files, 16 passing tests): three features done, two open (discount
codes, low-stock alerts) and one known bug (orders over $50 still pay shipping). Three setups get identical code:

  base       the code and its README (which lists the two planned features, not the bug)
  docs       + LAYOUT.md and ROADMAP.md from benchmark/fixture/docs, no plugin
  tricklord  + the same two files and the tricklord plugin

Every session is a fresh `claude -p` with project settings only (--setting-sources project), so the user's own
plugins stay out; tricklord comes in through --plugin-dir. Each run is scored by tests and checks on the files it
leaves behind, and timed from the stream: total, and until its first file edit ("orientation").

  python3 benchmark/project_bench.py run [--reps 3] [--model sonnet] [--workers 6]
  python3 benchmark/project_bench.py report    # prints the table, writes benchmark/project-chart-{light,dark}.svg
"""
import argparse
import csv
import json
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

import bench  # chart helpers and palette from the small benchmark

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
FIXTURE = HERE / "fixture"
RESULTS = HERE / "project_results.csv"
LOGS = HERE / "logs"
SETUPS = ["base", "docs", "tricklord"]
FIELDS = ["scenario", "setup", "rep", "success", "roadmap_updated", "seconds", "orient_seconds", "tokens",
          "orient_tokens", "output_tokens", "cost", "tool_calls", "orient_tool_calls", "model", "date"]
TOKEN_KEYS = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")
EDIT_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}

SCENARIOS = {  # name: prompts, one fresh session each, run in order on the same project copy
    "resume": ["Continue the project: do the next open task, and only that one."],
    "locate": ["When checkout leaves a product with fewer than 5 units in stock, email the admin a low-stock alert."],
    "status": ["What is done in this project and what is left to do? Answer briefly and don't change any files."],
    "chain": ['Add discount codes: place_order(conn, customer_id, cart, discount_code="SAVE10") should take 10% '
              "off the subtotal before tax.",
              "Orders over $50 should ship free, but customers are still being charged shipping. Fix it."],
}
CHAIN_REPS = 2  # the chain runs two sessions per repeat

SETUP_CODE = '''
from shoplite.db.connection import connect, init_db
from shoplite.catalog.products import add_product
from shoplite.customers.accounts import create_customer
from shoplite.orders.cart import Cart
from shoplite.orders.checkout import place_order
from shoplite.notifications import email
conn = connect(":memory:")
init_db(conn)
c = create_customer(conn, "Ann", "ann@example.com")
'''
CHECKS = {
    "discount": SETUP_CODE + '''
p = add_product(conn, "Mug", 2000, stock=50)
a = Cart(); a.add(p, 2); plain = place_order(conn, c, a)
b = Cart(); b.add(p, 2); off = place_order(conn, c, b, discount_code="SAVE10")
assert 400 <= plain["total"] - off["total"] <= 440, (plain, off)
''',
    "shipping": '''
from shoplite.orders.pricing import shipping_cents
assert shipping_cents(6000) == 0 and shipping_cents(3000) == 599
''',
    "low_stock": SETUP_CODE + '''
lamp = add_product(conn, "Lamp", 3000, stock=6)
desk = add_product(conn, "Desk", 9000, stock=40)
alerts = lambda: [m for m in email.OUTBOX if "stock" in (m["subject"] + m["body"]).lower()]
email.OUTBOX.clear()
x = Cart(); x.add(desk, 1); place_order(conn, c, x)
assert not alerts(), "alert although stock is fine"
y = Cart(); y.add(lamp, 2); place_order(conn, c, y)
assert alerts() and alerts()[0]["to"] == "admin@shoplite.test", email.OUTBOX
''',
}
OPEN_ITEMS = [r"discount", r"low[- ]?stock|stock alert", r"free[- ]?shipping|shipping (bug|issue|fix)|charged shipping"]


def make_project(setup):
    d = Path(tempfile.mkdtemp(prefix=f"shoplite-{setup}-"))
    shutil.copytree(FIXTURE / "shoplite", d, dirs_exist_ok=True)
    if setup != "base":
        for name in ("LAYOUT.md", "ROADMAP.md"):
            shutil.copy(FIXTURE / "docs" / name, d / name)
    git = ["git", "-c", "user.name=shoplite", "-c", "user.email=dev@shoplite.test"]
    subprocess.run(["git", "init", "-q"], cwd=d, check=True)
    subprocess.run(git + ["add", "-A"], cwd=d, check=True)
    subprocess.run(git + ["commit", "-qm", "shoplite: catalog, accounts, cart and checkout"], cwd=d, check=True)
    return d


def session(d, setup, prompt, model, log):
    cmd = ["claude", "-p", prompt, "--model", model, "--setting-sources", "project", "--permission-mode",
           "acceptEdits", "--allowedTools", "Bash", "--output-format", "stream-json", "--verbose"]
    if setup == "tricklord":
        cmd += ["--plugin-dir", str(REPO / "src")]
    t0 = time.monotonic()
    proc = subprocess.Popen(cmd, cwd=d, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                            stdin=subprocess.DEVNULL, text=True)
    m = {"tokens": 0, "output_tokens": 0, "cost": 0.0, "tool_calls": 0, "answer": "",
         "orient_seconds": None, "orient_tokens": None, "orient_tool_calls": None}
    seen, running = set(), 0
    for line in proc.stdout:
        log.write(line)
        e = json.loads(line)
        if e.get("type") == "assistant":
            msg = e["message"]
            if msg.get("id") not in seen:  # one API call can arrive as several events carrying the same usage
                seen.add(msg.get("id"))
                running += sum(msg.get("usage", {}).get(k) or 0 for k in TOKEN_KEYS)
            for c in msg["content"]:
                if c.get("type") == "tool_use":
                    if c["name"] in EDIT_TOOLS and m["orient_seconds"] is None:
                        m.update(orient_seconds=time.monotonic() - t0, orient_tokens=running,
                                 orient_tool_calls=m["tool_calls"])
                    m["tool_calls"] += 1
        elif e.get("type") == "result":
            u = e.get("usage", {})
            m.update(tokens=sum(u.get(k) or 0 for k in TOKEN_KEYS), output_tokens=u.get("output_tokens") or 0,
                     cost=e.get("total_cost_usd") or 0.0, answer=e.get("result") or "")
    proc.wait()
    m["seconds"] = time.monotonic() - t0
    if m["orient_seconds"] is None:  # never edited (status questions): orientation is the whole session
        m.update(orient_seconds=m["seconds"], orient_tokens=m["tokens"], orient_tool_calls=m["tool_calls"])
    return m


def passes(d, check):
    return subprocess.run([sys.executable, "-c", CHECKS[check]], cwd=d, capture_output=True).returncode == 0


def base_commit(d):
    """The fixture commit. Diff against it, not HEAD, so a run that commits its own work is still seen."""
    return subprocess.run(["git", "rev-list", "--max-parents=0", "HEAD"], cwd=d, capture_output=True,
                          text=True).stdout.split()[0]


def score(d, scenario, answer):
    tests = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "."], cwd=d,
                           capture_output=True).returncode == 0
    if scenario == "resume":  # the next open task is discount codes: did the code change touch them?
        subprocess.run(["git", "add", "-A", "-N"], cwd=d)
        diff = subprocess.run(["git", "diff", base_commit(d), "--", ".", ":!ROADMAP.md", ":!LAYOUT.md"], cwd=d,
                              capture_output=True, text=True).stdout
        added = "\n".join(l for l in diff.splitlines() if l.startswith("+"))
        return float(tests and "discount" in added.lower())
    if scenario == "locate":
        return float(tests and passes(d, "low_stock"))
    if scenario == "status":
        return sum(bool(re.search(p, answer, re.I)) for p in OPEN_ITEMS) / len(OPEN_ITEMS)
    return float(tests and passes(d, "discount") and passes(d, "shipping"))  # chain


lock = threading.Lock()


def job(scenario, setup, rep, model):
    d = make_project(setup)
    total = {"seconds": 0.0, "orient_seconds": 0.0, "tokens": 0, "orient_tokens": 0, "output_tokens": 0,
             "cost": 0.0, "tool_calls": 0, "orient_tool_calls": 0}
    try:
        LOGS.mkdir(exist_ok=True)
        with open(LOGS / f"project-{scenario}-{setup}-{rep}.log", "w") as log:
            for prompt in SCENARIOS[scenario]:
                m = session(d, setup, prompt, model, log)
                for k in total:
                    total[k] += m[k]
        success = score(d, scenario, m["answer"])
        changed = subprocess.run(["git", "diff", "--quiet", base_commit(d), "--", "ROADMAP.md"], cwd=d).returncode == 1
        roadmap = "" if setup == "base" or scenario == "status" else int(changed)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    row = {"scenario": scenario, "setup": setup, "rep": rep, "success": round(success, 3), "roadmap_updated": roadmap,
           **{k: round(v, 4) if isinstance(v, float) else v for k, v in total.items()},
           "model": model, "date": date.today().isoformat()}
    with lock:  # append as each run finishes, so a crash keeps what already ran
        new = not RESULTS.exists()
        with RESULTS.open("a", newline="") as f:
            w = csv.DictWriter(f, FIELDS)
            if new:
                w.writeheader()
            w.writerow(row)
    print(f"{scenario:<7}{setup:<10}rep {rep}  success {row['success']}  {row['seconds']:.0f}s  "
          f"{row['tokens'] / 1000:.0f}k tok  ${row['cost']:.3f}", flush=True)
    return row


def run(args):
    jobs = [(s, setup, r, args.model) for s in SCENARIOS for r in range(1, (CHAIN_REPS if s == "chain" else args.reps) + 1)
            for setup in SETUPS]
    with ThreadPoolExecutor(args.workers) as pool:
        list(pool.map(lambda j: job(*j), jobs))


def summary():
    rows = list(csv.DictReader(RESULTS.open()))
    out = {}
    for scenario in SCENARIOS:
        for setup in SETUPS:
            rs = [r for r in rows if r["scenario"] == scenario and r["setup"] == setup]
            if not rs:
                continue
            med = lambda k: statistics.median(float(r[k]) for r in rs)
            upd = [int(r["roadmap_updated"]) for r in rs if r["roadmap_updated"] != ""]
            out[(scenario, setup)] = {
                "runs": len(rs), "success": 100 * statistics.mean(float(r["success"]) for r in rs),
                "roadmap": 100 * statistics.mean(upd) if upd else None,
                **{k: med(k) for k in ("seconds", "orient_seconds", "tokens", "orient_tokens", "cost", "tool_calls",
                                       "orient_tool_calls")}}
    return out


SETUP_LABELS = {"tricklord": ("With tricklord", "s1"), "docs": ("Docs only, no plugin", "s3"),
                "base": ("Base agent", "s2")}
SCENARIO_LABELS = {"resume": "Resume: do the next task", "locate": "Add a cross-module feature",
                   "status": "What's done and what's left?", "chain": "Two tasks, two sessions"}
THEMES = {t: {**bench.THEMES[t], "s3": s3} for t, s3 in (("light", "#1baf7a"), ("dark", "#199e70"))}


def chart(theme):
    c, stats = THEMES[theme], summary()
    order = ["tricklord", "docs", "base"]
    W, LX, X0, XW, BAR, GAP, PAD = 720, 214, 226, 420, 13, 3, 20
    ROW = 3 * BAR + 2 * GAP + PAD
    panels = [("seconds", "Median time per run (seconds)", lambda v: f"{v:.0f} s"),
              ("tokens", "Median tokens per run (thousands, incl. cached)", lambda v: f"{v / 1000:.0f}k"),
              ("cost", "Median cost per run (US dollars)", lambda v: f"${v:.2f}")]
    out = [bench.svg_text(24, 34, "tricklord vs the base agent on a half-finished project", 17, c["primary"], 600),
           bench.svg_text(24, 56, "shoplite: 35 files, 3 features done, 2 open, 1 known bug. Claude Code, Sonnet 5, "
                                  "fresh session per task.", 13, c["secondary"])]
    lx = 24
    for key in order:
        label, slot = SETUP_LABELS[key]
        out.append(f'<rect x="{lx}" y="72" width="12" height="12" rx="2" fill="{c[slot]}"/>')
        out.append(bench.svg_text(lx + 18, 82, label, 13, c["secondary"]))
        lx += 18 + len(label) * 7 + 28
    y = 120
    for metric, title, fmt in panels:
        out.append(bench.svg_text(24, y, title, 14, c["primary"], 600))
        top = y + 18
        vmax = 100 if metric == "success" else max(s[metric] for s in stats.values()) * 1.1
        rows = [s for s in SCENARIOS if any((s, k) in stats for k in order)]
        bottom = top + len(rows) * ROW - PAD
        for frac in (0, 0.25, 0.5, 0.75, 1):
            x = X0 + XW * frac
            out.append(f'<line x1="{x}" y1="{top - 6}" x2="{x}" y2="{bottom + 6}" '
                       f'stroke="{c["baseline"] if frac == 0 else c["grid"]}" stroke-width="1"/>')
        for i, scenario in enumerate(rows):
            ry = top + i * ROW
            out.append(bench.svg_text(LX, ry + ROW / 2 - PAD / 2 + 4, SCENARIO_LABELS[scenario], 13, c["secondary"],
                                      anchor="end"))
            for j, key in enumerate(order):
                s = stats.get((scenario, key))
                if not s:
                    continue
                v, by = s[metric], ry + j * (BAR + GAP)
                w = XW * v / vmax
                label = SETUP_LABELS[key][0]
                if w > 0:
                    out.append(bench.bar(X0, by, w, BAR, c[SETUP_LABELS[key][1]], f"{label}, {SCENARIO_LABELS[scenario]}: {fmt(v)}"))
                out.append(bench.svg_text(X0 + w + 6, by + 10.5, fmt(v), 11, c["primary"]))
        y = bottom + 50
    out.append(bench.svg_text(24, y - 14, "Medians over 3 runs per cell (2 for the two-session chain). Source: "
                                          "benchmark/project_bench.py, benchmark/project_results.csv", 11, c["muted"]))
    H = y
    body = "\n  ".join(out)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" {bench.FONT} '
            f'role="img" aria-label="Project benchmark: tricklord, docs only and base agent">\n'
            f'  <rect width="{W}" height="{H}" rx="8" fill="{c["surface"]}"/>\n  {body}\n</svg>\n')


def report(args):
    stats = summary()
    print("| Scenario | Setup | Runs | Success | Roadmap updated | Time | Time to first edit | Tokens | "
          "Tokens before first edit | Cost | Tool calls |")
    print("| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for (scenario, setup), s in stats.items():
        roadmap = "n/a" if s["roadmap"] is None else f"{s['roadmap']:.0f}%"
        print(f"| {scenario} | {setup} | {s['runs']} | {s['success']:.0f}% | {roadmap} | {s['seconds']:.0f} s | "
              f"{s['orient_seconds']:.0f} s | {s['tokens'] / 1000:.0f}k | {s['orient_tokens'] / 1000:.0f}k | "
              f"${s['cost']:.3f} | {s['tool_calls']:.0f} |")
    for theme in THEMES:
        (HERE / f"project-chart-{theme}.svg").write_text(chart(theme))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--reps", type=int, default=3)
    r.add_argument("--model", default="sonnet")
    r.add_argument("--workers", type=int, default=6)
    sub.add_parser("report")
    a = p.parse_args()
    {"run": run, "report": report}[a.cmd](a)
