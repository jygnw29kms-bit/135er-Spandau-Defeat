from __future__ import annotations
import argparse
import json
import statistics
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--runtime-seconds", type=int, default=45)
    parser.add_argument("--num-bots", type=int, default=15)
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[2]
    runner = Path(__file__).with_name("run_rathaus_v75_front_spawn_headless_check.py")
    report_path = repo / "ue5" / "SpandauStrike" / "Saved" / "Reports" / "v75_front_spawn_headless_workflow.json"
    output_path = repo / "ue5" / "SpandauStrike" / "Saved" / "Reports" / "spawn_to_combat_baseline.json"

    samples: list[dict] = []
    for index in range(max(1, args.runs)):
        command = [
            sys.executable,
            str(runner),
            "--runtime-seconds", str(args.runtime_seconds),
            "--num-bots", str(args.num_bots),
            "--combat-probe",
        ]
        completed = subprocess.run(command, cwd=repo, check=False)
        if not report_path.exists():
            raise RuntimeError(f"run {index + 1}: report missing")
        report = json.loads(report_path.read_text(encoding="utf-8"))
        sample = {
            "run": index + 1,
            "passed": bool(report.get("passed")),
            "seconds": report.get("spawn_to_combat_seconds"),
            "damage": report.get("spawn_to_combat_damage"),
            "target": report.get("spawn_to_combat_target"),
            "unexpected_bad_count": report.get("unexpected_bad_count"),
            "runner_exit_code": completed.returncode,
        }
        samples.append(sample)
        print("COMBAT_BASELINE_SAMPLE=" + json.dumps(sample, separators=(",", ":")))
        if completed.returncode != 0 or not sample["passed"]:
            raise RuntimeError(f"run {index + 1}: combat gate failed")

    seconds = [float(s["seconds"]) for s in samples if s["seconds"] is not None]
    damage = [float(s["damage"]) for s in samples if s["damage"] is not None]
    summary = {
        "timestamp": datetime.now(timezone.utc).astimezone().isoformat(),
        "runs": len(samples),
        "runtime_seconds": args.runtime_seconds,
        "num_bots": args.num_bots,
        "seconds_min": min(seconds),
        "seconds_mean": statistics.fmean(seconds),
        "seconds_median": statistics.median(seconds),
        "seconds_max": max(seconds),
        "damage_min": min(damage),
        "damage_mean": statistics.fmean(damage),
        "damage_median": statistics.median(damage),
        "damage_max": max(damage),
        "samples": samples,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("COMBAT_BASELINE=" + json.dumps(summary, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
