#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "tools" / "gameplay" / "build_coordinate_invariants.py"


class CoordinateInvariantTests(unittest.TestCase):
    def test_coordinate_signature_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "coordinate_invariants.json"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--out", str(out)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + "\n" + result.stderr)
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(data["schema"], "SpandauStrike.CoordinateInvariants.v1")
            self.assertEqual(data["world_master_version"], "v45_MAIN_ROOF_RIDGE_ALIGNMENT")
            self.assertEqual(data["anchor_count"], 13)
            self.assertEqual(data["pair_count"], 78)
            self.assertEqual(len(data["anchors_source_m"]), 13)
            self.assertEqual(len(data["pairwise_distances"]), 78)
            self.assertGreater(data["distance_signature"]["max_pair_m"], 500.0)
            self.assertLess(data["distance_signature"]["min_pair_m"], 200.0)
            self.assertGreater(data["source_extents"]["x_span_m"], 800.0)
            self.assertGreater(data["source_extents"]["y_span_m"], 800.0)
            self.assertEqual(data["validation_policy"]["ue_centimeters_per_source_meter"], 100.0)
            self.assertTrue(data["validation_policy"]["rotation_translation_reflection_invariant"])


if __name__ == "__main__":
    unittest.main()
