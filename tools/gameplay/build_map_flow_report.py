#!/usr/bin/env python3
import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GAMEPLAY = ROOT / "ue5" / "SpandauStrike" / "Design" / "Gameplay"
LANE_FLOW = GAMEPLAY / "rathaus_lane_flow_v1.json"
COMBAT_FLOW = GAMEPLAY / "rathaus_combat_flow_v1.json"
DEFAULT_OUT = ROOT / "ue5" / "SpandauStrike" / "Design" / "Generated" / "rathaus_map_flow_report_v1.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def distance(a, b):
    return math.hypot(float(b[0]) - float(a[0]), float(b[1]) - float(a[1]))


def polyline_length(points):
    return sum(distance(a, b) for a, b in zip(points, points[1:]))


def rounded(value):
    return round(float(value), 2)


def main():
    parser = argparse.ArgumentParser(description="Analyze Rathaus objective/lane/combat flow without opening Blender or UE.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    lane = load(LANE_FLOW)
    combat = load(COMBAT_FLOW)

    objectives = sorted(lane["objectives"], key=lambda item: int(item["sequence"]))
    objective_legs = []
    for a, b in zip(objectives, objectives[1:]):
        objective_legs.append({
            "from": a["id"],
            "to": b["id"],
            "straight_line_m": rounded(distance(a["position_m"], b["position_m"])),
        })

    lane_lengths = {
        name: rounded(polyline_length(data["points_m"]))
        for name, data in lane["primary_lanes"].items()
    }
    crosslink_lengths = {
        name: rounded(polyline_length(data["points_m"]))
        for name, data in lane["crosslinks"].items()
    }

    choke_by_lane = {name: 0 for name in lane["primary_lanes"]}
    for choke in combat["chokes"]:
        choke_by_lane[choke["lane"]] += 1

    power_by_lane = {name: 0 for name in lane["primary_lanes"]}
    for power in combat["power_positions"]:
        power_by_lane[power["lane"]] += 1

    warnings = []
    if max(lane_lengths.values()) / min(lane_lengths.values()) > 1.45:
        warnings.append("primary_lane_length_imbalance")
    if any(count == 0 for count in power_by_lane.values()):
        warnings.append("lane_without_power_position")
    if any(count == 0 for count in choke_by_lane.values()):
        warnings.append("lane_without_choke")
    if max(leg["straight_line_m"] for leg in objective_legs) > 250.0:
        warnings.append("objective_gap_over_250m")
    if min(leg["straight_line_m"] for leg in objective_legs) < 60.0:
        warnings.append("objective_gap_under_60m")

    report = {
        "schema": "SpandauStrike.RathausMapFlowReport.v1",
        "objective_legs": objective_legs,
        "primary_lane_lengths_m": lane_lengths,
        "crosslink_lengths_m": crosslink_lengths,
        "chokes_by_lane": choke_by_lane,
        "power_positions_by_lane": power_by_lane,
        "summary": {
            "objective_count": len(objectives),
            "primary_lane_count": len(lane_lengths),
            "crosslink_count": len(crosslink_lengths),
            "shortest_lane_m": rounded(min(lane_lengths.values())),
            "longest_lane_m": rounded(max(lane_lengths.values())),
            "lane_length_ratio": rounded(max(lane_lengths.values()) / min(lane_lengths.values())),
            "warning_count": len(warnings),
        },
        "warnings": warnings,
        "interpretation": {
            "lane_length_warning_threshold_ratio": 1.45,
            "objective_gap_warning_min_m": 60.0,
            "objective_gap_warning_max_m": 250.0,
            "note": "Warnings are design-review signals, not automatic balance failures. Real walkable path length and sightline exposure must be verified in UE navigation/playtests."
        }
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], sort_keys=True))
    if warnings:
        print("WARNINGS " + ",".join(warnings))
    print(args.out)


if __name__ == "__main__":
    main()
