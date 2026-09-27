#!/usr/bin/env python3
"""Benchmark: the same coding tasks with and without TrustMeBro.

Every run gets a fresh copy of a small project (app.py and a TrustMeBro LAYOUT.md, no roadmap). The two setups
differ only in TrustMeBro: `base` is the agent as it is, `trustmebro` adds the plugin (Claude Code) or the .bob/
folder (IBM Bob). Each run is scored from the files it leaves behind and the order of its edits.

  python3 benchmark/bench.py run --agent claude [--reps 2] [--model sonnet]
  python3 benchmark/bench.py run --agent bob [--reps 1]     # needs BOB_API_KEY in the environment
  python3 benchmark/bench.py report                           # prints the table, writes benchmark/chart-{light,dark}.svg
"""
import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
RESULTS = HERE / "results.csv"
LOGS = HERE / "logs"
FIELDS = ["agent", "model", "setup", "task", "rep", "recorded", "recorded_first", "layout_current", "correct",
          "cost", "seconds", "tool_calls", "date"]

APP = '''def add(a, b):
    return a + b


def subtract(a, b):
    return b - a
'''
LAYOUT = '''<!-- trustmebro -->
# Project layout

Last updated: 2026-09-27.

## Folder tree

```
app.py      math helpers
```

## Logic

- **add**: adds two numbers -> `app.py:add`
- **subtract**: subtracts b from a -> `app.py:subtract`
'''
# name: (prompt, roadmap keyword, correctness check, layout keyword or None when the layout need not change)
TASKS = {
    "feature": ("Add a function multiply(a, b) to app.py that returns a * b.",
                "multiply", "from app import multiply; assert multiply(2, 3) == 6", "multiply"),
    "fix": ("subtract(5, 3) returns -2 instead of 2. Fix it.",
            "subtract", "from app import subtract; assert subtract(5, 3) == 2", None),
    "module": ("Add a new file stats.py with a function mean(numbers) that returns the average.",
               "mean", "from stats import mean; assert mean([1, 2, 3]) == 2", "stats"),
}
CODE_FILES = {"app.py", "stats.py"}
BOB_WRITE_TOOLS = {"write_to_file", "write_file", "apply_diff", "insert_content", "search_and_replace"}


def fixture(setup, agent):
    d = Path(tempfile.mkdtemp(prefix=f"trustmebro-bench-{agent}-{setup}-"))
    (d / "app.py").write_text(APP)
    (d / "LAYOUT.md").write_text(LAYOUT)
    if agent == "bob" and setup == "trustmebro":
        shutil.copytree(REPO / ".bob", d / ".bob", ignore=shutil.ignore_patterns(".DS_Store"))
    git = ["git", "-c", "user.name=bench", "-c", "user.email=bench@example.com"]
    subprocess.run(git[:1] + ["init", "-q"], cwd=d, check=True)
    subprocess.run(git + ["add", "-A"], cwd=d, check=True)
    subprocess.run(git + ["commit", "-qm", "fixture"], cwd=d, check=True)
    return d


def run_claude(d, setup, prompt, model):
    cmd = ["claude", "-p", prompt, "--model", model, "--permission-mode", "acceptEdits", "--allowedTools", "Bash",
           "--output-format", "stream-json", "--verbose"]
    if setup == "trustmebro":
        cmd += ["--plugin-dir", str(REPO / "src")]
    out = subprocess.run(cmd, cwd=d, capture_output=True, text=True, stdin=subprocess.DEVNULL).stdout
    edits, tools, cost, seconds = [], 0, 0.0, 0.0
    for line in out.splitlines():
        e = json.loads(line)
        if e.get("type") == "assistant":
            for c in e["message"]["content"]:
                if c.get("type") == "tool_use":
                    tools += 1
                    path = c["input"].get("file_path") or c["input"].get("notebook_path")
                    if path and c["name"] in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
                        edits.append(Path(path).name)
        if e.get("type") == "result":
            cost, seconds = e.get("total_cost_usd", 0.0), e.get("duration_ms", 0) / 1000
    return out, edits, tools, cost, seconds


def run_bob(d, setup, prompt, model):
    cmd = ["bob", "run", "--workspace", str(d), "--trust", "--max-cost", "3", "--max-turns", "25", prompt]
    out = subprocess.run(cmd, cwd=d, capture_output=True, text=True, stdin=subprocess.DEVNULL).stdout
    edits, tool = [], None
    for line in out.splitlines():
        m = re.match(r"Tool: (\w+)", line.strip())
        if m:
            tool = m.group(1)
        m = re.match(r"- path: (.+)", line.strip())
        if m and tool in BOB_WRITE_TOOLS:
            edits.append(Path(m.group(1).strip()).name)
    num = lambda pat: float((re.search(pat, out) or [0, 0])[1])
    return out, edits, int(num(r"Tool Calls:\s+(\d+)")), num(r"Total Cost:\s+([\d.]+)"), num(r"Total Duration:\s+([\d.]+)")


def score(d, task, edits):
    prompt, key, check, layout_key = TASKS[task]
    roadmap = d / "ROADMAP.md"
    recorded = roadmap.exists() and any(line.lstrip().startswith("- [") and key in line.lower()
                                        for line in roadmap.read_text().splitlines())
    first_code = next((i for i, f in enumerate(edits) if f in CODE_FILES), len(edits))
    recorded_first = recorded and "ROADMAP.md" in edits[:first_code]
    layout = None if layout_key is None else layout_key in (d / "LAYOUT.md").read_text().lower()
    correct = subprocess.run([sys.executable, "-c", check], cwd=d, capture_output=True).returncode == 0
    return recorded, recorded_first, layout, correct


def one(agent, setup, task, rep, model):
    d = fixture(setup, agent)
    try:
        out, edits, tools, cost, seconds = (run_claude if agent == "claude" else run_bob)(d, setup, TASKS[task][0], model)
        LOGS.mkdir(exist_ok=True)
        (LOGS / f"{agent}-{setup}-{task}-{rep}.log").write_text(out)
        recorded, recorded_first, layout, correct = score(d, task, edits)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    return {"agent": agent, "model": model, "setup": setup, "task": task, "rep": rep,
            "recorded": int(recorded), "recorded_first": int(recorded_first), "layout_current": "" if layout is None else int(layout),
            "correct": int(correct), "cost": round(cost, 4), "seconds": round(seconds, 1), "tool_calls": tools,
            "date": date.today().isoformat()}


def run(args):
    model = args.model if args.agent == "claude" else "bob default"
    jobs = [(args.agent, s, t, r, model) for r in range(1, args.reps + 1) for t in TASKS for s in ("base", "trustmebro")]
    with ThreadPoolExecutor(args.workers) as pool:
        rows = list(pool.map(lambda j: one(*j), jobs))
    new = not RESULTS.exists()
    with RESULTS.open("a", newline="") as f:
        w = csv.DictWriter(f, FIELDS)
        if new:
            w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(r)


def summary():
    rows = list(csv.DictReader(RESULTS.open()))
    groups = {}
    for r in rows:
        groups.setdefault((r["agent"], r["setup"]), []).append(r)
    out = []
    for (agent, setup), rs in sorted(groups.items()):
        pct = lambda k: 100 * sum(int(r[k]) for r in rs if r[k] != "") / max(1, sum(r[k] != "" for r in rs))
        avg = lambda k: sum(float(r[k]) for r in rs) / len(rs)
        out.append({"agent": agent, "setup": setup, "runs": len(rs), "recorded": pct("recorded"), "recorded_first": pct("recorded_first"),
                    "layout_current": pct("layout_current"), "correct": pct("correct"),
                    "cost": avg("cost"), "seconds": avg("seconds"), "tool_calls": avg("tool_calls")})
    return out


THEMES = {  # dataviz reference palette: chart chrome + categorical slots 1-2, validated light and dark
    "light": dict(surface="#fcfcfb", primary="#0b0b0b", secondary="#52514e", muted="#898781",
                  grid="#e1e0d9", baseline="#c3c2b7", s1="#2a78d6", s2="#eb6834"),
    "dark": dict(surface="#1a1a19", primary="#ffffff", secondary="#c3c2b7", muted="#898781",
                 grid="#2c2c2a", baseline="#383835", s1="#3987e5", s2="#d95926"),
}
METRICS = [("recorded", "Task put on the roadmap"), ("recorded_first", "... before any code was written"),
           ("layout_current", "LAYOUT.md kept up to date"), ("correct", "Task done correctly")]
SETUPS = [("trustmebro", "With TrustMeBro", "s1"), ("base", "Without TrustMeBro (base agent)", "s2")]
AGENTS = {"claude": "Claude Code", "bob": "IBM Bob"}
FONT = 'font-family="system-ui, -apple-system, Segoe UI, sans-serif"'


def svg_text(x, y, s, size, fill, weight=400, anchor="start"):
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{s}</text>'


def bar(x, y, w, h, fill, tip, r=4):
    """Horizontal bar: square at the baseline, 4px rounded at the data end."""
    r = min(r, w, h / 2)
    d = f"M{x},{y}h{w - r:.1f}a{r},{r} 0 0 1 {r},{r}v{h - 2 * r}a{r},{r} 0 0 1 {-r},{r}h{-(w - r):.1f}z"
    return f'<path d="{d}" fill="{fill}"><title>{tip}</title></path>'


def chart(theme):
    c = THEMES[theme]
    stats = {(s["agent"], s["setup"]): s for s in summary()}
    agents = [a for a in AGENTS if any(k[0] == a for k in stats)]
    W, LX, X0, XW, ROW, BAR, GAP = 720, 250, 262, 400, 54, 16, 4
    out = [svg_text(24, 34, "Does the agent keep the roadmap and layout up to date?", 17, c["primary"], 600),
           svg_text(24, 56, "Share of runs. Same 3 tasks (feature, bug fix, new module), fresh project every run.", 13, c["secondary"])]
    lx = 24
    for _, label, slot in SETUPS:  # legend: swatch beside ink text, never colored text
        out.append(f'<rect x="{lx}" y="72" width="12" height="12" rx="2" fill="{c[slot]}"/>')
        out.append(svg_text(lx + 18, 82, label, 13, c["secondary"]))
        lx += 18 + len(label) * 7 + 28
    y = 118
    for agent in agents:
        runs = max(stats.get((agent, s), {}).get("runs", 0) for s, _, _ in SETUPS)
        out.append(svg_text(24, y, f"{AGENTS[agent]} ({runs} runs per setup)", 14, c["primary"], 600))
        top = y + 18
        bottom = top + len(METRICS) * ROW - (ROW - 2 * BAR - GAP)
        for pct in (0, 25, 50, 75, 100):  # recessive hairline grid, drawn under the bars
            x = X0 + XW * pct / 100
            out.append(f'<line x1="{x}" y1="{top - 6}" x2="{x}" y2="{bottom + 6}" stroke="{c["baseline"] if pct == 0 else c["grid"]}" stroke-width="1"/>')
            out.append(svg_text(x, bottom + 22, f"{pct}%", 11, c["muted"], anchor="middle"))
        for i, (metric, mlabel) in enumerate(METRICS):
            ry = top + i * ROW
            out.append(svg_text(LX, ry + BAR + GAP / 2 + 4, mlabel, 13, c["secondary"], anchor="end"))
            for j, (setup, slabel, slot) in enumerate(SETUPS):
                s = stats.get((agent, setup))
                if not s:
                    continue
                v, by = s[metric], ry + j * (BAR + GAP)
                w = XW * v / 100
                if w > 0:
                    out.append(bar(X0, by, w, BAR, c[slot], f"{slabel}: {mlabel.strip('. ')} {v:.0f}%"))
                out.append(svg_text(X0 + w + 6, by + 12, f"{v:.0f}%", 12, c["primary"]))
        y = bottom + 58
    out.append(svg_text(24, y - 12, "Scored from the files each run leaves and the order of its edits. Source: benchmark/bench.py, benchmark/results.csv", 11, c["muted"]))
    H = y + 4
    body = "\n  ".join(out)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" {FONT} role="img" '
            f'aria-label="Benchmark: agent with and without TrustMeBro">\n  <rect width="{W}" height="{H}" rx="8" fill="{c["surface"]}"/>\n  {body}\n</svg>\n')


def report(args):
    for theme in THEMES:
        (HERE / f"chart-{theme}.svg").write_text(chart(theme))
    print("| Agent | Setup | Runs | Task on roadmap | Task on roadmap before code | LAYOUT.md kept current | Task correct | Avg cost | Avg time | Avg tool calls |")
    print("| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for s in summary():
        print(f"| {s['agent']} | {s['setup']} | {s['runs']} | {s['recorded']:.0f}% | {s['recorded_first']:.0f}% | {s['layout_current']:.0f}% | "
              f"{s['correct']:.0f}% | {s['cost']:.3f} | {s['seconds']:.0f} s | {s['tool_calls']:.1f} |")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--agent", choices=["claude", "bob"], required=True)
    r.add_argument("--reps", type=int, default=1)
    r.add_argument("--model", default="sonnet")
    r.add_argument("--workers", type=int, default=6)
    sub.add_parser("report")
    a = p.parse_args()
    {"run": run, "report": report}[a.cmd](a)
