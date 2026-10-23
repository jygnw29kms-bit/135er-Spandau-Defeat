from __future__ import annotations
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--distances-cm", default="350,700,1200")
    parser.add_argument("--runs-per-distance", type=int, default=1)
    parser.add_argument("--runtime-seconds", type=int, default=45)
    parser.add_argument("--num-bots", type=int, default=15)
    args = parser.parse_args()

    distances = [float(v.strip()) for v in args.distances_cm.split(",") if v.strip()]
    repo = Path(__file__).resolve().parents[2]
    runner = Path(__file__).with_name("run_rathaus_v75_front_spawn_headless_check.py")
    gate_report = repo / "ue5" / "SpandauStrike" / "Saved" / "Reports" / "v75_front_spawn_headless_workflow.json"
    output = repo / "ue5" / "SpandauStrike" / "Saved" / "Reports" / "spawn_to_combat_distance_matrix.json"

    samples: list[dict] = []
    for distance in distances:
        for run in range(1, max(1, args.runs_per_distance) + 1):
            command = [
                sys.executable,
                str(runner),
                "--runtime-seconds", str(args.runtime_seconds),
                "--num-bots", str(args.num_bots),
                "--combat-probe",
                "--combat-probe-distance-cm", str(distance),
            ]
            completed = subprocess.run(command, cwd=repo, check=False)
            report = json.loads(gate_report.read_text(encoding="utf-8")) if gate_report.exists() else {}
            sample = {
                "requested_distance_cm": distance,
                "run": run,
                "passed": bool(report.get("passed")),
                "actual_distance_cm": report.get("combat_probe_distance_cm"),
                "seconds": report.get("spawn_to_combat_seconds"),
                "damage": report.get("spawn_to_combat_damage"),
                "target": report.get("spawn_to_combat_target"),
                "combat_hold_seen": report.get("combat_hold_seen"),
                "unexpected_bad_count": report.get("unexpected_bad_count"),
                "runner_exit_code": completed.returncode,
            }
            samples.append(sample)
            print("COMBAT_DISTANCE_SAMPLE=" + json.dumps(sample, separators=(",", ":")))

    grouped = []
    for distance in distances:
        distance_samples = [s for s in samples if s["requested_distance_cm"] == distance]
        grouped.append({
            "requested_distance_cm": distance,
            "runs": len(distance_samples),
            "passes": sum(1 for s in distance_samples if s["passed"]),
            "all_passed": all(s["passed"] for s in distance_samples),
            "samples": distance_samples,
        })

    summary = {
        "timestamp": datetime.now(timezone.utc).astimezone().isoformat(),
        "runtime_seconds": args.runtime_seconds,
        "num_bots": args.num_bots,
        "runs_per_distance": max(1, args.runs_per_distance),
        "distances": grouped,
        "all_passed": all(group["all_passed"] for group in grouped),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("COMBAT_DISTANCE_MATRIX=" + json.dumps(summary, separators=(",", ":")))
    return 0 if summary["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
