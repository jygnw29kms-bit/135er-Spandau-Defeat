#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TAGS = ROOT / "tools" / "gameplay" / "spandau_strike_gameplay_tags.json"
TUNING = ROOT / "ue5" / "SpandauStrike" / "Design" / "Gameplay" / "core_gameplay_tuning_v1.json"
WEAPONS = ROOT / "ue5" / "SpandauStrike" / "Design" / "Gameplay" / "weapon_archetypes_v1.json"
LOADOUTS = ROOT / "ue5" / "SpandauStrike" / "Design" / "Gameplay" / "class_loadouts_v1.json"
COMBAT_FLOW = ROOT / "ue5" / "SpandauStrike" / "Design" / "Gameplay" / "rathaus_combat_flow_v1.json"
LANE_FLOW = ROOT / "ue5" / "SpandauStrike" / "Design" / "Gameplay" / "rathaus_lane_flow_v1.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def fail(message):
    raise SystemExit("VALIDATION ERROR: " + message)


def main():
    tags = load(TAGS)
    tuning = load(TUNING)
    weapons = load(WEAPONS)
    loadouts = load(LOADOUTS)
    combat_flow = load(COMBAT_FLOW)
    lane_flow = load(LANE_FLOW)

    values = tags.get("tags", [])
    if not values:
        fail("gameplay tag list is empty")
    if len(values) != len(set(values)):
        fail("duplicate gameplay tags detected")
    if any(not tag.startswith("SpandauStrike.") for tag in values):
        fail("all project gameplay tags must use the SpandauStrike.* namespace")

    movement = tuning["movement"]
    stamina = tuning["stamina"]
    classes = tuning["classes"]
    territorial = tuning["territorial_control"]
    archetypes = weapons["archetypes"]
    class_loadouts = loadouts["classes"]

    if not (0.0 <= movement["air_control"] <= 0.35):
        fail("air_control outside heavy-movement baseline")
    if movement["prone_speed_cm_s"] >= movement["crouch_speed_cm_s"]:
        fail("prone speed must be below crouch speed")
    if movement["crouch_speed_cm_s"] >= movement["run_speed_cm_s"]:
        fail("crouch speed must be below run speed")
    if stamina["max"] <= 0 or stamina["sprint_drain_per_s"] <= 0 or stamina["jump_cost"] <= 0:
        fail("invalid stamina resource values")

    expected_classes = {"Rifleman", "Assault", "Support", "Sniper", "MG", "Rocket"}
    if set(classes) != expected_classes:
        fail(f"class tuning mismatch: {sorted(classes)}")
    if set(class_loadouts) != expected_classes:
        fail(f"class loadout mismatch: {sorted(class_loadouts)}")
    if classes["MG"]["speed_multiplier"] >= classes["Assault"]["speed_multiplier"]:
        fail("MG must remain slower than Assault")

    expected_archetypes = {"BoltRifle", "AssaultSMG", "SupportAutomatic", "ScopedRifle", "HeavyMG", "RocketLauncher"}
    if set(archetypes) != expected_archetypes:
        fail(f"weapon archetype mismatch: {sorted(archetypes)}")

    for class_name, definition in class_loadouts.items():
        tag = definition["gameplay_tag"]
        if tag not in values:
            fail(f"missing canonical class tag for {class_name}: {tag}")
        primary = definition["primary_archetype"]
        if primary not in archetypes:
            fail(f"unknown primary archetype for {class_name}: {primary}")

    bolt = archetypes["BoltRifle"]
    bolt_upper_torso_damage = bolt["base_damage"] * bolt["hit_zone_multipliers"]["upper_torso"]
    if bolt_upper_torso_damage < 100.0:
        fail("BoltRifle upper-torso baseline must remain one-hit lethal against 100 health")

    scoped = archetypes["ScopedRifle"]
    scoped_upper_torso_damage = scoped["base_damage"] * scoped["hit_zone_multipliers"]["upper_torso"]
    if scoped_upper_torso_damage < 100.0:
        fail("ScopedRifle upper-torso baseline must remain one-hit lethal against 100 health")

    mg = archetypes["HeavyMG"]
    if mg["deployed_spread_deg"] >= mg["undeployed_spread_deg"]:
        fail("HeavyMG deployed spread must be lower than undeployed spread")
    if mg["deployed_recoil_multiplier"] >= mg["undeployed_recoil_multiplier"]:
        fail("HeavyMG deployed recoil must be lower than undeployed recoil")

    rocket = archetypes["RocketLauncher"]
    if rocket["direct_damage"] <= rocket["splash_damage"]:
        fail("Rocket direct damage must exceed splash damage")

    if territorial["objective_count"] != 5:
        fail("Rathaus territorial baseline requires 5 objectives")
    if territorial["center_objective_sequence"] != 3 or territorial["center_required_players"] != 2:
        fail("Rathaus center objective invariant broken")
    if territorial["backcap_allowed"] is not False:
        fail("back-capping must remain disabled")

    lanes = set(combat_flow.get("lanes", []))
    if lanes != {"north", "mid", "south"}:
        fail(f"Rathaus lane set mismatch: {sorted(lanes)}")

    chokes = combat_flow.get("chokes", [])
    if len(chokes) != 4:
        fail(f"expected 4 Rathaus chokes, got {len(chokes)}")
    for choke in chokes:
        if choke.get("lane") not in lanes:
            fail(f"choke {choke.get('id')} has invalid lane")
        if not choke.get("smoke_anchor_m") or not choke.get("flank_anchor_m"):
            fail(f"choke {choke.get('id')} must provide smoke and flank counterplay")

    positions = combat_flow.get("power_positions", [])
    if len(positions) != 3:
        fail(f"expected 3 MG/sniper power-position groups, got {len(positions)}")
    for position in positions:
        if position.get("lane") not in lanes:
            fail(f"power position {position.get('id')} has invalid lane")
        counterplay = set(position.get("counterplay", []))
        if "smoke" not in counterplay:
            fail(f"power position {position.get('id')} must allow smoke counterplay")
        if not ({"flank", "alternate_lane"} & counterplay):
            fail(f"power position {position.get('id')} must allow flank or alternate-lane counterplay")
        if position.get("mg_requires_bipod") is not True:
            fail(f"power position {position.get('id')} MG must require bipod")
        if not (20.0 <= float(position.get("mg_arc_deg", 0.0)) <= 90.0):
            fail(f"power position {position.get('id')} MG arc outside tactical baseline")

    lane_objectives = lane_flow.get("objectives", [])
    if len(lane_objectives) != 5:
        fail(f"lane flow must contain 5 objectives, got {len(lane_objectives)}")
    sequences = [int(item.get("sequence", -1)) for item in lane_objectives]
    if sequences != [1, 2, 3, 4, 5]:
        fail(f"lane-flow objective sequence mismatch: {sequences}")
    center = lane_objectives[2]
    if center.get("zone") != "rathaus" or int(center.get("required_players", 0)) != 2:
        fail("lane-flow center objective must be the 2-player Rathaus capture")

    primary_lanes = lane_flow.get("primary_lanes", {})
    if set(primary_lanes) != lanes:
        fail(f"lane-flow primary lanes mismatch: {sorted(primary_lanes)}")
    for lane_name, lane in primary_lanes.items():
        if len(lane.get("points_m", [])) < 5:
            fail(f"primary lane {lane_name} must preserve at least 5 route points")

    crosslinks = lane_flow.get("crosslinks", {})
    if len(crosslinks) != 3:
        fail(f"expected 3 crosslinks, got {len(crosslinks)}")
    for crosslink_name, crosslink in crosslinks.items():
        if len(crosslink.get("points_m", [])) < 3:
            fail(f"crosslink {crosslink_name} must preserve at least 3 route points")

    lane_rules = lane_flow.get("rules", {})
    if lane_rules.get("lane_tunnels_forbidden") is not True:
        fail("lane tunnels must remain forbidden")
    if lane_rules.get("backcap_allowed") is not False:
        fail("lane flow must keep back-capping disabled")

    print(json.dumps({
        "tags": len(values),
        "classes": len(classes),
        "weapon_archetypes": len(archetypes),
        "objective_count": territorial["objective_count"],
        "chokes": len(chokes),
        "power_positions": len(positions),
        "primary_lanes": len(primary_lanes),
        "crosslinks": len(crosslinks),
        "status": "ok"
    }, sort_keys=True))


if __name__ == "__main__":
    main()
