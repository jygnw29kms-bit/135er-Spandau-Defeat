#!/usr/bin/env python3
import argparse
import json
import math
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HANDOFF_GENERATOR = ROOT / "tools" / "gameplay" / "build_runtime_gameplay_handoff.py"
DEFAULT_OUT = ROOT / "ue5" / "SpandauStrike" / "Design" / "Generated" / "rathaus_spawn_safety_report_v1.json"


def distance_xy(a, b):
    return math.hypot(float(b[0]) - float(a[0]), float(b[1]) - float(a[1]))


def main():
    parser = argparse.ArgumentParser(description="Analyze Rathaus spawn distance from territorial objectives and opposing spawns.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--handoff", type=Path)
    args = parser.parse_args()

    if args.handoff:
        handoff_path = args.handoff
    else:
        import subprocess, sys
        tmp = tempfile.NamedTemporaryFile(prefix="spandau_handoff_", suffix=".json", delete=False)
        tmp.close()
        handoff_path = Path(tmp.name)
        result = subprocess.run(
            [sys.executable, str(HANDOFF_GENERATOR), "--out", str(handoff_path)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode:
            raise SystemExit(result.stdout + "\n" + result.stderr)

    data = json.loads(handoff_path.read_text(encoding="utf-8-sig"))
    objectives = data["objectives"]
    spawns = data["spawns"]

    objective_positions = {
        int(obj["metadata"]["ss_sequence"]): obj["transform"]["location_m"]
        for obj in objectives
    }

    team_spawns = {"west": [], "east": []}
    for spawn in spawns:
        team = spawn["metadata"]["ss_team"]
        team_spawns[team].append(spawn)

    rows = []
    warnings = []
    for spawn in spawns:
        team = spawn["metadata"]["ss_team"]
        pos = spawn["transform"]["location_m"]
        objective_distances = {
            str(seq): round(distance_xy(pos, obj_pos), 2)
            for seq, obj_pos in objective_positions.items()
        }
        nearest_seq = min(objective_distances, key=objective_distances.get)
        nearest_dist = objective_distances[nearest_seq]

        enemy_team = "east" if team == "west" else "west"
        enemy_distances = [
            distance_xy(pos, enemy["transform"]["location_m"])
            for enemy in team_spawns[enemy_team]
        ]
        nearest_enemy_spawn = round(min(enemy_distances), 2)

        row = {
            "spawn": spawn["source_name"],
            "team": team,
            "lane": spawn["metadata"].get("ss_lane"),
            "nearest_objective_sequence": int(nearest_seq),
            "nearest_objective_distance_m": nearest_dist,
            "nearest_enemy_spawn_distance_m": nearest_enemy_spawn,
            "objective_distances_m": objective_distances,
        }
        rows.append(row)

        if nearest_dist < 80.0:
            warnings.append(f"{spawn['source_name']}:objective_under_80m")
        if nearest_enemy_spawn < 180.0:
            warnings.append(f"{spawn['source_name']}:enemy_spawn_under_180m")

    report = {
        "schema": "SpandauStrike.RathausSpawnSafetyReport.v1",
        "thresholds": {
            "min_objective_distance_m": 80.0,
            "min_enemy_spawn_distance_m": 180.0,
            "note": "Distance checks are geometry-only review signals. UE line of sight, navigation and spawn scoring remain authoritative runtime checks."
        },
        "spawns": sorted(rows, key=lambda row: (row["team"], row["spawn"])),
        "summary": {
            "spawn_count": len(rows),
            "west_spawns": len(team_spawns["west"]),
            "east_spawns": len(team_spawns["east"]),
            "warning_count": len(warnings),
            "minimum_objective_distance_m": round(min(row["nearest_objective_distance_m"] for row in rows), 2),
            "minimum_enemy_spawn_distance_m": round(min(row["nearest_enemy_spawn_distance_m"] for row in rows), 2),
        },
        "warnings": warnings,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], sort_keys=True))
    if warnings:
        print("WARNINGS " + ",".join(warnings))
    print(args.out)


if __name__ == "__main__":
    main()
