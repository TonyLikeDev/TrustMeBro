#!/usr/bin/env python3
"""
test_tools.py - Lean unit test suite for RoadmapFlow tools.

# ponytail: Zero-dependency stdlib unittest; tests core logic without mocks or heavy test frameworks.
"""

import sys
import unittest
from pathlib import Path

# Add src and local dir to sys.path
_current_dir = Path(__file__).resolve().parent
_repo_root = _current_dir.parent
for _candidate in [_repo_root / "src", _current_dir]:
    if _candidate.exists() and str(_candidate) not in sys.path:
        sys.path.insert(0, str(_candidate))

from roadmap import (
    estimate_tokens,
    render_ascii_bar,
    parse_phase_sections,
    extract_tier2_snapshot,
    validate_roadmap,
)
from benchmark import run_benchmark


class TestRoadmapTools(unittest.TestCase):

    def setUp(self):
        self.repo_root = Path(__file__).resolve().parent.parent
        self.roadmap_path = self.repo_root / "teamsource/ROADMAP.md"

    def test_estimate_tokens_bounds(self):
        self.assertEqual(estimate_tokens(""), 0)
        self.assertGreater(estimate_tokens("Hello world"), 1)
        # 100 words should be ~100-130 tokens
        sample = "word " * 100
        tokens = estimate_tokens(sample)
        self.assertTrue(90 <= tokens <= 140, f"Unexpected token count: {tokens}")

    def test_render_ascii_bar(self):
        self.assertEqual(render_ascii_bar(0.0), "[░░░░░░░░░░░░░░░░░░░░]")
        self.assertEqual(render_ascii_bar(1.0), "[████████████████████]")
        self.assertEqual(render_ascii_bar(0.5), "[██████████░░░░░░░░░░]")
        # Test clamping
        self.assertEqual(render_ascii_bar(-0.5), "[░░░░░░░░░░░░░░░░░░░░]")
        self.assertEqual(render_ascii_bar(1.5), "[████████████████████]")

    def test_parse_real_roadmap(self):
        self.assertTrue(self.roadmap_path.exists(), "teamsource/ROADMAP.md must exist")
        content = self.roadmap_path.read_text(encoding="utf-8")
        sections = parse_phase_sections(content)

        self.assertGreaterEqual(len(sections), 3, "Should parse at least Weeks 1, 2, 3")
        w1 = sections[0]
        self.assertIn("Week 1", w1["title"])
        self.assertEqual(w1["total"], 17)
        self.assertEqual(w1["done"], 14)

        w2 = sections[1]
        self.assertIn("Week 2", w2["title"])
        self.assertEqual(w2["total"], 11)
        self.assertEqual(w2["done"], 11)
        self.assertTrue(w2["is_complete"])

    def test_tier2_snapshot_budget(self):
        res = extract_tier2_snapshot(self.roadmap_path)
        self.assertEqual(res["status"], "OK")
        self.assertIn("Week 1", res["phase"])
        self.assertIn("## Open Tasks", res["markdown"])
        # Crucial Hackathon constraint: Budget <= 200 tokens
        self.assertLessEqual(
            res["tokens"],
            200,
            f"Snapshot must be <= 200 tokens to prevent context bloat! Got: {res['tokens']}",
        )

    def test_validate_roadmap_rules(self):
        content = self.roadmap_path.read_text(encoding="utf-8")
        errors = validate_roadmap(content)
        # Real roadmap should have exit criteria in weeks 1-3
        self.assertEqual(errors, [])

    def test_benchmark_metrics(self):
        results = run_benchmark(self.repo_root)
        ss = results["single_session"]
        ms = results["multi_session_10_turns"]

        # Assert savings > 85%
        self.assertGreater(ss["savings_percent"], 85.0)
        self.assertGreater(ms["cumulative_savings_percent"], 85.0)
        self.assertLessEqual(ss["tier2_tokens"], 200)


    def test_scaffold_init_and_audit(self):
        import tempfile
        import shutil
        from scaffold import scaffold_standard_project, audit_standard_project

        temp_dir = Path(tempfile.mkdtemp(prefix="roadmapflow_test_"))
        try:
            created = scaffold_standard_project(temp_dir, "TestApp", "Python", 3)
            self.assertGreater(len(created), 5)
            compliant, reports = audit_standard_project(temp_dir)
            self.assertTrue(compliant, f"Scaffolded project must be compliant! Reports: {reports}")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
