#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "tools" / "gameplay" / "build_balance_report.py"


class BalanceReportTests(unittest.TestCase):
    def test_current_baseline_metrics(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "balance.json"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--out", str(out)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + "\n" + result.stderr)
            data = json.loads(out.read_text(encoding="utf-8"))

            self.assertEqual(data["schema"], "SpandauStrike.GameplayBalanceReport.v1")
            self.assertEqual(data["warning_count"], 0, msg=str(data["warnings"]))
            self.assertGreaterEqual(data["stamina_metrics"]["full_sprint_seconds_at_base_drain"], 4.0)
            self.assertLessEqual(data["stamina_metrics"]["full_sprint_seconds_at_base_drain"], 8.0)
            self.assertLess(data["class_metrics"]["MG"]["run_speed_cm_s"], data["class_metrics"]["Rifleman"]["run_speed_cm_s"])
            self.assertTrue(data["weapon_metrics"]["BoltRifle"]["upper_torso_lethal_100hp"])
            self.assertTrue(data["weapon_metrics"]["ScopedRifle"]["upper_torso_lethal_100hp"])
            self.assertLess(data["weapon_metrics"]["HeavyMG"]["deployed_to_undeployed_spread_ratio"], 0.2)


if __name__ == "__main__":
    unittest.main()
