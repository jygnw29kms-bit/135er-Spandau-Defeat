#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "tools" / "gameplay" / "build_spawn_safety_report.py"


class SpawnSafetyReportTests(unittest.TestCase):
    def test_spawn_safety_report_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "spawn_safety.json"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--out", str(out)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + "\n" + result.stderr)
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(data["schema"], "SpandauStrike.RathausSpawnSafetyReport.v1")
            self.assertEqual(data["summary"]["spawn_count"], 8)
            self.assertEqual(data["summary"]["west_spawns"], 4)
            self.assertEqual(data["summary"]["east_spawns"], 4)
            self.assertGreater(data["summary"]["minimum_enemy_spawn_distance_m"], 180.0)
            self.assertGreater(len(data["spawns"]), 0)
            names = {row["spawn"] for row in data["spawns"]}
            self.assertEqual(len(names), 8)
            # W4 is intentionally kept as a review warning until UE LOS/nav validation.
            self.assertTrue(any(warning.startswith("SM_SPAWN_WEST_4:objective_under_80m") for warning in data["warnings"]))


if __name__ == "__main__":
    unittest.main()
