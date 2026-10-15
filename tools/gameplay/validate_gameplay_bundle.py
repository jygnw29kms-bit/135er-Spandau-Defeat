#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "ue5" / "SpandauStrike" / "Design" / "Gameplay" / "gameplay_bundle_v1.json"


def fail(message):
    raise SystemExit("VALIDATION ERROR: " + message)


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main():
    bundle = load(BUNDLE)
    if bundle.get("schema") != "SpandauStrike.GameplayBundle.v1":
        fail("unexpected gameplay bundle schema")

    referenced = []
    world = bundle.get("world_master", {})
    referenced.append(world.get("manifest"))
    referenced.extend(bundle.get("gameplay_sources", {}).values())
    referenced.extend(bundle.get("generators", {}).values())
    referenced.extend(bundle.get("validators", {}).values())

    missing = []
    for rel in referenced:
        if not rel:
            fail("bundle contains an empty path reference")
        if not (ROOT / rel).is_file():
            missing.append(rel)
    if missing:
        fail("bundle references missing files: " + ", ".join(missing))

    if world.get("version") != "v48_DORMER_ALIGNMENT":
        fail("bundle must currently point at v48_DORMER_ALIGNMENT")

    inv = bundle.get("required_invariants", {})
    expected = {
        "objective_count": 5,
        "spawn_count": 8,
        "primary_lane_count": 3,
        "crosslink_count": 3,
        "choke_count": 4,
        "power_position_groups": 3,
        "center_objective_sequence": 3,
        "center_required_players": 2,
        "backcap_allowed": False,
        "project_tag_namespace": "SpandauStrike.",
    }
    for key, value in expected.items():
        if inv.get(key) != value:
            fail(f"bundle invariant {key} mismatch: expected {value!r}, got {inv.get(key)!r}")

    tuning = load(ROOT / bundle["gameplay_sources"]["core_tuning"])
    lane_flow = load(ROOT / bundle["gameplay_sources"]["lane_flow"])
    combat_flow = load(ROOT / bundle["gameplay_sources"]["combat_flow"])
    tags = load(ROOT / bundle["gameplay_sources"]["tags"])

    territorial = tuning["territorial_control"]
    if territorial["objective_count"] != inv["objective_count"]:
        fail("bundle objective count disagrees with core tuning")
    if territorial["center_objective_sequence"] != inv["center_objective_sequence"]:
        fail("bundle center sequence disagrees with core tuning")
    if territorial["center_required_players"] != inv["center_required_players"]:
        fail("bundle center capture-player count disagrees with core tuning")
    if territorial["backcap_allowed"] != inv["backcap_allowed"]:
        fail("bundle backcap rule disagrees with core tuning")

    if len(lane_flow.get("primary_lanes", {})) != inv["primary_lane_count"]:
        fail("bundle primary lane count disagrees with lane flow")
    if len(lane_flow.get("crosslinks", {})) != inv["crosslink_count"]:
        fail("bundle crosslink count disagrees with lane flow")
    if len(combat_flow.get("chokes", [])) != inv["choke_count"]:
        fail("bundle choke count disagrees with combat flow")
    if len(combat_flow.get("power_positions", [])) != inv["power_position_groups"]:
        fail("bundle power-position count disagrees with combat flow")

    tag_values = tags.get("tags", [])
    if any(not tag.startswith(inv["project_tag_namespace"]) for tag in tag_values):
        fail("canonical gameplay tag namespace disagrees with bundle")

    print(json.dumps({
        "bundle_version": bundle["bundle_version"],
        "world_master": world["version"],
        "references": len(referenced),
        "status": "ok"
    }, sort_keys=True))


if __name__ == "__main__":
    main()
