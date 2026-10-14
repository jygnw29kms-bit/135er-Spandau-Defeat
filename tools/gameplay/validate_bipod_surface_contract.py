#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GAMEPLAY = ROOT / "ue5" / "SpandauStrike" / "Design" / "Gameplay"
CONTRACT = GAMEPLAY / "bipod_surface_contract_v1.json"
TUNING = GAMEPLAY / "core_gameplay_tuning_v1.json"
ABILITIES = GAMEPLAY / "ability_contracts_v1.json"
TAGS = ROOT / "tools" / "gameplay" / "spandau_strike_gameplay_tags.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def fail(message):
    raise SystemExit("VALIDATION ERROR: " + message)


def lookup(data, dotted):
    parts = dotted.split(".")
    if parts and parts[0].endswith("_v1"):
        parts = parts[1:]
    current = data
    for part in parts:
        if not isinstance(current, dict) or part not in current:
            fail(f"bipod source path missing: {dotted}")
        current = current[part]
    return current


def main():
    contract = load(CONTRACT)
    tuning = load(TUNING)
    abilities = load(ABILITIES)["abilities"]
    tags = set(load(TAGS)["tags"])

    surfaces = contract.get("supported_surface_classes", {})
    if set(surfaces) != {"Ground", "WindowSill", "WallTop", "Generic"}:
        fail(f"surface class set mismatch: {sorted(surfaces)}")
    surface_tags = {entry.get("gameplay_tag") for entry in surfaces.values()}
    if None in surface_tags or not surface_tags.issubset(tags):
        fail("bipod surface contract references non-canonical gameplay tags")

    for name in ("WindowSill", "WallTop"):
        entry = surfaces[name]
        if not 30.0 <= float(entry["min_height_cm"]) < float(entry["max_height_cm"]) <= 180.0:
            fail(f"{name} support height band invalid")

    ground = surfaces["Ground"]
    if not 0.0 < float(ground["max_surface_angle_from_up_deg"]) <= 45.0:
        fail("ground support angle outside baseline")

    trace = contract["trace_contract"]
    if not 60.0 <= float(trace["forward_trace_cm"]) <= 150.0:
        fail("forward support trace outside review band")
    if not 40.0 <= float(trace["down_trace_cm"]) <= 120.0:
        fail("down support trace outside review band")
    if int(trace["minimum_support_points"]) < 2:
        fail("bipod requires at least two support points")
    if trace.get("collision_channel") != "WorldStatic":
        fail("bipod support must default to WorldStatic")
    if trace.get("reject_moving_dynamic_support_by_default") is not True:
        fail("moving dynamic support must remain rejected by default")

    deployment = contract["deployment"]
    if deployment.get("ability") != "BipodDeploy":
        fail("deployment must use BipodDeploy ability contract")
    if deployment.get("weapon_archetype") != "HeavyMG":
        fail("deployment must remain tied to HeavyMG")
    if not 0.1 <= float(deployment["deploy_time_s"]) <= 1.5:
        fail("bipod deploy time outside baseline")
    if not 0.1 <= float(deployment["undeploy_time_s"]) <= 1.0:
        fail("bipod undeploy time outside baseline")

    for key in [
        "yaw_limit_source", "pitch_min_source", "pitch_max_source",
        "spread_multiplier_source", "recoil_multiplier_source", "sway_multiplier_source"
    ]:
        lookup(tuning, deployment[key])

    ability = abilities["BipodDeploy"]
    if ability.get("requires_weapon_archetype") != deployment["weapon_archetype"]:
        fail("BipodDeploy weapon archetype disagrees with surface contract")
    ability_surfaces = set(ability.get("surface_tags_any", []))
    if ability_surfaces != surface_tags:
        fail("BipodDeploy surface tag set disagrees with surface contract")

    breaks = set(contract.get("break_conditions", []))
    required_breaks = {"support_lost", "weapon_changed", "character_falls", "forced_movement"}
    if not required_breaks.issubset(breaks):
        fail("bipod break-condition contract weakened")

    metadata = contract["map_metadata"]
    if metadata.get("blender_property") != "ss_bipod" or metadata.get("surface_type_property") != "ss_bipod_type":
        fail("Blender bipod metadata property names changed")
    if set(metadata.get("accepted_types", [])) != {"ground", "window_sill", "wall_top", "generic"}:
        fail("bipod metadata type set mismatch")

    network = contract["network_policy"]
    if network.get("server_validates_support_trace") is not True:
        fail("server must validate support trace")
    if network.get("server_owns_deployed_state") is not True:
        fail("server must own deployed state")
    if network.get("server_revalidates_support_while_deployed") is not True:
        fail("server must revalidate bipod support")

    print(json.dumps({
        "surface_classes": len(surfaces),
        "surface_tags": len(surface_tags),
        "break_conditions": len(breaks),
        "status": "ok"
    }, sort_keys=True))


if __name__ == "__main__":
    main()
