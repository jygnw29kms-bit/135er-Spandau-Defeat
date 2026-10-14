#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GAMEPLAY = ROOT / "ue5" / "SpandauStrike" / "Design" / "Gameplay"
CONTRACT = GAMEPLAY / "movement_contract_v1.json"
TUNING = GAMEPLAY / "core_gameplay_tuning_v1.json"
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
        if part == "<Class>":
            return current
        if not isinstance(current, dict) or part not in current:
            fail(f"movement source path missing: {dotted}")
        current = current[part]
    return current


def collect_tags(value, out):
    if isinstance(value, dict):
        for child in value.values():
            collect_tags(child, out)
    elif isinstance(value, list):
        for child in value:
            collect_tags(child, out)
    elif isinstance(value, str) and value.startswith("SpandauStrike."):
        out.add(value)


def main():
    contract = load(CONTRACT)
    tuning = load(TUNING)
    canonical_tags = set(load(TAGS)["tags"])

    axes = contract["axes"]
    if set(axes) != {"stance", "gait", "locomotion"}:
        fail("movement axes must be stance/gait/locomotion")
    if set(axes["stance"]) != {"Standing", "Crouched", "ProneTransitionDown", "Prone", "ProneTransitionUp"}:
        fail("stance state set mismatch")
    if set(axes["gait"]) != {"Walk", "Run", "Sprint"}:
        fail("gait state set mismatch")
    if set(axes["locomotion"]) != {"Grounded", "Airborne", "LandingRecovery"}:
        fail("locomotion state set mismatch")

    referenced_tags = set()
    collect_tags(contract, referenced_tags)
    missing_tags = sorted(referenced_tags - canonical_tags)
    if missing_tags:
        fail("movement contract references non-canonical tags: " + ", ".join(missing_tags))

    sprint = contract["sprint"]
    if sprint["allowed_stances"] != ["Standing"]:
        fail("sprint must remain standing-only")
    if sprint["allowed_locomotion"] != ["Grounded"]:
        fail("sprint must remain grounded-only")
    if float(sprint["minimum_stamina"]) <= 0.0:
        fail("sprint minimum stamina must be positive")
    lookup(tuning, sprint["drain_source"])
    class_source = sprint["class_drain_multiplier_source"]
    if "<Class>" not in class_source:
        fail("sprint class drain source must remain class-dependent")
    for values in tuning["classes"].values():
        if "stamina_drain_multiplier" not in values:
            fail("every class requires stamina_drain_multiplier")

    jump = contract["jump"]
    if jump.get("ends_sprint") is not True:
        fail("jump must end sprint")
    lookup(tuning, jump["stamina_cost_source"])
    air_control = float(lookup(tuning, jump["air_control_source"]))
    if not 0.0 <= air_control <= 0.35:
        fail("air control outside heavy-movement contract")

    prone = contract["prone"]
    if prone.get("requires_clearance_sweep") is not True:
        fail("prone must require a clearance sweep")
    for key in [
        "enter_duration_source", "exit_duration_source", "movement_speed_source",
        "view_yaw_limit_source", "view_pitch_min_source", "view_pitch_max_source"
    ]:
        lookup(tuning, prone[key])

    reversal = contract["direction_reversal"]
    if float(reversal["velocity_input_dot_threshold"]) >= 0.0:
        fail("direction reversal threshold must be negative")
    reversal_multiplier = float(lookup(tuning, reversal["acceleration_multiplier_source"]))
    if not 0.5 <= reversal_multiplier < 1.0:
        fail("direction reversal acceleration multiplier outside heavy-movement band")

    landing = contract["landing"]
    landing_duration = float(lookup(tuning, landing["recovery_duration_source"]))
    if not 0.1 <= landing_duration <= 0.5:
        fail("landing recovery duration outside baseline review band")
    if landing.get("sprint_blocked_during_recovery") is not True:
        fail("sprint must remain blocked during landing recovery")

    prediction = contract["network_prediction"]
    if prediction.get("must_use_character_movement_prediction") is not True:
        fail("movement must use character network prediction")
    if set(prediction.get("saved_move_flags", [])) != {"WantsSprint", "WantsProne"}:
        fail("saved move flags must preserve sprint/prone intent")
    if prediction.get("server_reconciles_stamina_costs") is not True:
        fail("server must reconcile stamina costs")
    if prediction.get("direct_blueprint_velocity_writes_forbidden") is not True:
        fail("direct Blueprint velocity writes must remain forbidden")

    print(json.dumps({
        "stance_states": len(axes["stance"]),
        "gait_states": len(axes["gait"]),
        "locomotion_states": len(axes["locomotion"]),
        "referenced_tags": len(referenced_tags),
        "status": "ok"
    }, sort_keys=True))


if __name__ == "__main__":
    main()
