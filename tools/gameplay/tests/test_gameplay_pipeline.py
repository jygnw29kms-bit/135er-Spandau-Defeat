#!/usr/bin/env python3
import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / "tools" / "gameplay"


class GameplayPipelineTests(unittest.TestCase):
    def run_python(self, script, *args):
        result = subprocess.run(
            [sys.executable, str(TOOLS / script), *map(str, args)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + "\n" + result.stderr)
        return result

    def test_core_validators(self):
        self.run_python("validate_gameplay_config.py")
        self.run_python("validate_gameplay_bundle.py")
        self.run_python("validate_ability_contracts.py")
        self.run_python("validate_objective_state_machine.py")
        self.run_python("validate_frontline_flow.py")

    def test_runtime_handoff_generation(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "handoff.json"
            self.run_python("build_runtime_gameplay_handoff.py", "--out", out)
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(data["schema"], "SpandauStrike.RuntimeGameplayHandoff.v1")
            self.assertEqual(data["summary"]["objectives"], 5)
            self.assertEqual(data["summary"]["spawns"], 8)
            self.assertGreaterEqual(data["summary"]["cover_objects"], 20)
            self.assertFalse(Path(data["source_manifest"]).is_absolute())
            self.assertEqual([int(o["metadata"]["ss_sequence"]) for o in data["objectives"]], [1, 2, 3, 4, 5])
            center = data["objectives"][2]
            self.assertEqual(center["metadata"]["ss_zone"], "rathaus")
            self.assertEqual(int(center["metadata"]["ss_capture_players"]), 2)

    def test_datatable_generation(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "tables"
            self.run_python("build_ue_datatable_csv.py", "--out-dir", out_dir)

            with (out_dir / "DT_SpandauStrike_Classes.csv").open(encoding="utf-8", newline="") as handle:
                classes = list(csv.DictReader(handle))
            with (out_dir / "DT_SpandauStrike_WeaponArchetypes.csv").open(encoding="utf-8", newline="") as handle:
                weapons = list(csv.DictReader(handle))
            with (out_dir / "DT_SpandauStrike_Movement.csv").open(encoding="utf-8", newline="") as handle:
                movement = list(csv.DictReader(handle))
            with (out_dir / "DT_SpandauStrike_Objectives.csv").open(encoding="utf-8", newline="") as handle:
                objectives = list(csv.DictReader(handle))
            with (out_dir / "DT_SpandauStrike_CombatAnchors.csv").open(encoding="utf-8", newline="") as handle:
                combat = list(csv.DictReader(handle))

            self.assertEqual(len(classes), 6)
            self.assertEqual({row["Name"] for row in classes}, {"Rifleman", "Assault", "Support", "Sniper", "MG", "Rocket"})
            self.assertEqual(len(weapons), 6)
            self.assertEqual(len(movement), 1)
            self.assertEqual(len(objectives), 5)
            self.assertEqual([int(row["Sequence"]) for row in objectives], [1, 2, 3, 4, 5])
            self.assertEqual(int(objectives[2]["RequiredPlayers"]), 2)
            self.assertEqual(objectives[2]["Zone"], "rathaus")
            self.assertEqual(len(combat), 18)
            anchor_types = {row["AnchorType"] for row in combat}
            self.assertEqual(anchor_types, {"Choke", "Smoke", "Flank", "MG", "Sniper"})
            self.assertEqual(sum(1 for row in combat if row["AnchorType"] == "MG"), 3)
            self.assertEqual(sum(1 for row in combat if row["AnchorType"] == "Sniper"), 3)
            self.assertTrue(all(row["RequiresBipod"] == "true" for row in combat if row["AnchorType"] == "MG"))
            self.assertLess(float(next(row for row in classes if row["Name"] == "MG")["SpeedMultiplier"]),
                            float(next(row for row in classes if row["Name"] == "Assault")["SpeedMultiplier"]))

    def test_gameplay_tag_snippet(self):
        result = self.run_python("generate_ue_gameplay_tag_snippet.py")
        lines = [line for line in result.stdout.splitlines() if line.startswith("+GameplayTagList=")]
        self.assertGreaterEqual(len(lines), 20)
        self.assertTrue(all('Tag="SpandauStrike.' in line for line in lines))

    def test_import_plan_generation(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "import_plan.json"
            self.run_python("build_ue_import_plan.py", "--out", out)
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(data["schema"], "SpandauStrike.UEImportPlan.v1")
            self.assertEqual(data["world_master_version"], "v45_MAIN_ROOF_RIDGE_ALIGNMENT")
            self.assertFalse(data["safety"]["overwrite_current_final_map"])
            self.assertTrue(data["safety"]["use_separate_test_map_first"])
            self.assertGreaterEqual(len(data["sources"]), 7)
            for source in data["sources"]:
                self.assertFalse(Path(source["path"]).is_absolute())
                self.assertEqual(len(source["sha256"]), 64)
                int(source["sha256"], 16)
                self.assertGreater(source["size_bytes"], 0)
            orders = [step["order"] for step in data["ordered_steps"]]
            self.assertEqual(orders, list(range(1, len(orders) + 1)))
            self.assertFalse(any(step["mutates_map"] for step in data["ordered_steps"][:5]))

    def test_map_flow_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "map_flow_report.json"
            self.run_python("build_map_flow_report.py", "--out", out)
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(data["schema"], "SpandauStrike.RathausMapFlowReport.v1")
            self.assertEqual(data["summary"]["objective_count"], 5)
            self.assertEqual(data["summary"]["primary_lane_count"], 3)
            self.assertEqual(data["summary"]["crosslink_count"], 3)
            self.assertEqual(set(data["chokes_by_lane"]), {"north", "mid", "south"})
            self.assertEqual(set(data["power_positions_by_lane"]), {"north", "mid", "south"})
            self.assertTrue(all(count >= 1 for count in data["chokes_by_lane"].values()))
            self.assertTrue(all(count >= 1 for count in data["power_positions_by_lane"].values()))
            self.assertLessEqual(data["summary"]["lane_length_ratio"], 1.45)


if __name__ == "__main__":
    unittest.main()
