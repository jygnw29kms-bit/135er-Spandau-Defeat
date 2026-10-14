#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAPPING = ROOT / "ue5" / "SpandauStrike" / "Design" / "Gameplay" / "ue_asset_mapping_v1.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def fail(message):
    raise SystemExit("VALIDATION ERROR: " + message)


def main():
    data = load(MAPPING)
    if data.get("schema") != "SpandauStrike.UEAssetMapping.v1":
        fail("unexpected UE asset mapping schema")

    policy = data["policy"]
    if policy.get("production_map_overwrite_allowed") is not False:
        fail("production map overwrite must remain forbidden")
    if policy.get("first_import_uses_separate_test_map") is not True:
        fail("first import must use a separate validation map")
    if policy.get("blender_world_master_is_spatial_authority") is not True:
        fail("Blender world master must remain spatial authority")

    maps = data["maps"]
    production = maps["current_production_reference"]
    test_map = maps["runtime_validation_target"]
    promotion = maps["promotion_target"]
    if production == test_map or production == promotion or test_map == promotion:
        fail("production, validation and promotion map paths must be distinct")
    if "/Validation/" not in test_map or not test_map.endswith("_TEST"):
        fail("runtime validation map must live under /Validation/ and end in _TEST")
    if "FINAL" in test_map.upper():
        fail("validation map must never use FINAL naming")
    if not all(path.startswith("/Game/SpandauStrike/") for path in maps.values()):
        fail("all Spandau map paths must stay under /Game/SpandauStrike/")

    tables = data["data_assets"]
    required_tables = {
        "classes_table", "weapon_archetypes_table", "movement_table",
        "objectives_table", "combat_anchors_table"
    }
    if set(tables) != required_tables:
        fail(f"DataTable mapping mismatch: {sorted(tables)}")
    if len(set(tables.values())) != len(tables):
        fail("DataTable asset paths must be unique")
    if any(not path.startswith("/Game/SpandauStrike/Data/Gameplay/") for path in tables.values()):
        fail("all gameplay DataTables must stay under /Game/SpandauStrike/Data/Gameplay/")

    actor_classes = data["runtime_actor_classes"]
    if actor_classes.get("spawn") != "/Script/LyraGame.LyraPlayerStart":
        fail("runtime spawn mapping must reuse LyraPlayerStart")
    if actor_classes.get("cover") != "/Script/Engine.StaticMeshActor":
        fail("runtime cover mapping must use StaticMeshActor baseline")
    objective_class = actor_classes.get("objective", "")
    if not objective_class.startswith("/Script/LyraGame.SpandauStrike"):
        fail("objective class must be a Spandau Strike class in LyraGame")

    folders = data["runtime_folders"]
    if any(not path.startswith("/Game/SpandauStrike/") for path in folders.values()):
        fail("generated runtime folders must stay under /Game/SpandauStrike/")

    labels = data["generated_labels"]
    if len({labels["runtime_objective_prefix"], labels["runtime_spawn_prefix"], labels["runtime_cover_prefix"]}) != 3:
        fail("generated actor prefixes must be unique")
    if labels.get("generated_actor_tag") != "SpandauStrike.Generated.Runtime":
        fail("generated actor tag contract changed")

    order = data["import_order"]
    required_order = [
        "gameplay_tags", "datatable_seeds", "runtime_handoff", "coordinate_validation",
        "runtime_test_map", "objectives", "spawns", "cover", "navigation_validation",
        "combat_flow_validation", "promotion_review"
    ]
    if order != required_order:
        fail("UE import order contract changed unexpectedly")
    if order.index("runtime_test_map") > order.index("objectives"):
        fail("runtime test map must exist before objective placement")
    if order[-1] != "promotion_review":
        fail("promotion review must remain the final import step")

    print(json.dumps({
        "maps": len(maps),
        "datatables": len(tables),
        "runtime_actor_classes": len(actor_classes),
        "import_steps": len(order),
        "status": "ok"
    }, sort_keys=True))


if __name__ == "__main__":
    main()
