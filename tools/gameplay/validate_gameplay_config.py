#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TAGS = ROOT / "tools" / "gameplay" / "spandau_strike_gameplay_tags.json"
TUNING = ROOT / "ue5" / "SpandauStrike" / "Design" / "Gameplay" / "core_gameplay_tuning_v1.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def fail(message):
    raise SystemExit("VALIDATION ERROR: " + message)


def main():
    tags = load(TAGS)
    tuning = load(TUNING)

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
        fail(f"class set mismatch: {sorted(classes)}")
    if classes["MG"]["speed_multiplier"] >= classes["Assault"]["speed_multiplier"]:
        fail("MG must remain slower than Assault")

    if territorial["objective_count"] != 5:
        fail("Rathaus territorial baseline requires 5 objectives")
    if territorial["center_objective_sequence"] != 3 or territorial["center_required_players"] != 2:
        fail("Rathaus center objective invariant broken")
    if territorial["backcap_allowed"] is not False:
        fail("back-capping must remain disabled")

    print(json.dumps({
        "tags": len(values),
        "classes": len(classes),
        "objective_count": territorial["objective_count"],
        "status": "ok"
    }, sort_keys=True))


if __name__ == "__main__":
    main()
