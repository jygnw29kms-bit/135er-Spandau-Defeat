#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GAMEPLAY = ROOT / "ue5" / "SpandauStrike" / "Design" / "Gameplay"
LANE_FLOW = GAMEPLAY / "rathaus_lane_flow_v1.json"
STATE_MACHINE = GAMEPLAY / "objective_state_machine_v1.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def fail(message):
    raise SystemExit("VALIDATION ERROR: " + message)


def attackable(owners):
    sequences = sorted(owners)
    west_owned = [seq for seq in sequences if owners[seq] == "west"]
    east_owned = [seq for seq in sequences if owners[seq] == "east"]
    neutral = [seq for seq in sequences if owners[seq] == "neutral"]

    result = {"west": None, "east": None, "winner": None}
    if len(west_owned) == len(sequences):
        result["winner"] = "west"
        return result
    if len(east_owned) == len(sequences):
        result["winner"] = "east"
        return result

    highest_west = max(west_owned) if west_owned else 0
    lowest_east = min(east_owned) if east_owned else len(sequences) + 1

    west_target = highest_west + 1
    east_target = lowest_east - 1
    if west_target in owners and owners[west_target] != "west":
        result["west"] = west_target
    if east_target in owners and owners[east_target] != "east":
        result["east"] = east_target

    # A neutral objective between fronts is the shared contested target.
    if neutral:
        for seq in neutral:
            if seq == west_target == east_target:
                result["west"] = seq
                result["east"] = seq
    return result


def main():
    lane = load(LANE_FLOW)
    state_machine = load(STATE_MACHINE)
    objectives = lane["objectives"]
    if [int(item["sequence"]) for item in objectives] != [1, 2, 3, 4, 5]:
        fail("frontline validator requires objective sequence 1..5")
    if state_machine["capture_rules"].get("backcap_allowed") is not False:
        fail("frontline validation assumes backcap disabled")

    cases = [
        ({1: "west", 2: "west", 3: "neutral", 4: "east", 5: "east"}, {"west": 3, "east": 3, "winner": None}),
        ({1: "west", 2: "west", 3: "west", 4: "east", 5: "east"}, {"west": 4, "east": 3, "winner": None}),
        ({1: "west", 2: "west", 3: "east", 4: "east", 5: "east"}, {"west": 3, "east": 2, "winner": None}),
        ({1: "west", 2: "west", 3: "west", 4: "west", 5: "east"}, {"west": 5, "east": 4, "winner": None}),
        ({1: "west", 2: "east", 3: "east", 4: "east", 5: "east"}, {"west": 2, "east": 1, "winner": None}),
        ({1: "west", 2: "west", 3: "west", 4: "west", 5: "west"}, {"west": None, "east": None, "winner": "west"}),
        ({1: "east", 2: "east", 3: "east", 4: "east", 5: "east"}, {"west": None, "east": None, "winner": "east"}),
    ]

    results = []
    for index, (owners, expected) in enumerate(cases, 1):
        actual = attackable(owners)
        if actual != expected:
            fail(f"frontline case {index} failed: expected {expected}, got {actual}")
        results.append({
            "case": index,
            "owners": {str(k): v for k, v in owners.items()},
            "attackable": actual,
        })

    print(json.dumps({"cases": len(results), "status": "ok"}, sort_keys=True))


if __name__ == "__main__":
    main()
