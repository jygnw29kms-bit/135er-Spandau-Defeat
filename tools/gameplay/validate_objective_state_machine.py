#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GAMEPLAY = ROOT / "ue5" / "SpandauStrike" / "Design" / "Gameplay"
STATE_MACHINE = GAMEPLAY / "objective_state_machine_v1.json"
CORE_TUNING = GAMEPLAY / "core_gameplay_tuning_v1.json"
LANE_FLOW = GAMEPLAY / "rathaus_lane_flow_v1.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def fail(message):
    raise SystemExit("VALIDATION ERROR: " + message)


def main():
    machine = load(STATE_MACHINE)
    tuning = load(CORE_TUNING)["territorial_control"]
    lane = load(LANE_FLOW)

    expected_states = {
        "Locked", "Active", "CapturingWest", "CapturingEast",
        "Contested", "OwnedWest", "OwnedEast"
    }
    states = set(machine.get("states", []))
    if states != expected_states:
        fail(f"state set mismatch: {sorted(states)}")

    rules = machine["capture_rules"]
    if float(rules["capture_duration_s"]) != float(tuning["capture_duration_s"]):
        fail("capture duration disagrees with core tuning")
    if rules["contested_behavior"] != tuning["contested_behavior"]:
        fail("contested behavior disagrees with core tuning")
    if rules["backcap_allowed"] != tuning["backcap_allowed"]:
        fail("backcap rule disagrees with core tuning")
    if rules["frontline_mode"] != tuning["frontline_mode"]:
        fail("frontline mode disagrees with core tuning")
    if rules.get("server_authoritative") is not True:
        fail("objective state machine must remain server authoritative")

    required = {int(k): int(v) for k, v in machine["required_players_by_sequence"].items()}
    lane_required = {int(item["sequence"]): int(item["required_players"]) for item in lane["objectives"]}
    if required != lane_required:
        fail(f"required-player map disagrees with lane flow: {required} vs {lane_required}")
    if required.get(3) != 2:
        fail("Rathaus center capture must require two players")

    transitions = machine.get("transitions", [])
    if not transitions:
        fail("state machine has no transitions")
    seen = set()
    for transition in transitions:
        source = transition.get("from")
        target = transition.get("to")
        event = transition.get("event")
        if source not in states or target not in states:
            fail(f"transition uses unknown state: {transition}")
        if not event:
            fail(f"transition missing event: {transition}")
        key = (source, event)
        if key in seen:
            fail(f"nondeterministic duplicate transition: {key}")
        seen.add(key)

    required_transitions = {
        ("Locked", "FrontlineOpened", "Active"),
        ("Active", "WestThresholdMet", "CapturingWest"),
        ("Active", "EastThresholdMet", "CapturingEast"),
        ("CapturingWest", "BothTeamsPresent", "Contested"),
        ("CapturingEast", "BothTeamsPresent", "Contested"),
        ("CapturingWest", "CaptureComplete", "OwnedWest"),
        ("CapturingEast", "CaptureComplete", "OwnedEast"),
    }
    actual = {(item["from"], item["event"], item["to"]) for item in transitions}
    missing = sorted(required_transitions - actual)
    if missing:
        fail(f"required transitions missing: {missing}")

    frontline = machine["frontline_rules"]
    if frontline.get("capturing_non_adjacent_objective_forbidden") is not True:
        fail("non-adjacent captures must remain forbidden")

    replication = machine["replication_contract"]
    required_replication = ["replicate_state", "replicate_owner", "replicate_progress", "replicate_contesting_counts"]
    if any(replication.get(key) is not True for key in required_replication):
        fail("all objective runtime state must be replicated")
    if replication.get("client_prediction") is not False:
        fail("capture state must not be client-predicted")

    print(json.dumps({
        "states": len(states),
        "transitions": len(transitions),
        "objective_player_rules": len(required),
        "status": "ok"
    }, sort_keys=True))


if __name__ == "__main__":
    main()
