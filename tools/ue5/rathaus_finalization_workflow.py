from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PROJECT = REPO / "ue5" / "SpandauStrike"
REPORT_DIR = PROJECT / "Saved" / "Reports"
STATE_FILE = REPORT_DIR / "rathaus_finalization_state.json"
PYTHON = Path(sys.executable)


def now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat()


def run(name: str, command: list[str], cwd: Path = REPO) -> dict:
    started = now()
    state = load_state()
    state["current_phase"] = name
    state["phase_started"] = started
    state["status"] = "running"
    state["updated"] = started
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    item = {
        "name": name,
        "started": started,
        "finished": now(),
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-8000:],
        "stderr_tail": completed.stderr[-8000:],
        "passed": completed.returncode == 0,
    }
    save_phase(item)
    if completed.returncode != 0:
        raise RuntimeError(f"{name} failed with exit code {completed.returncode}")
    return item


def save_phase(item: dict) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    state = load_state()
    state.setdefault("history", []).append(item)
    state["updated"] = now()
    state["current_phase"] = item["name"]
    state["last_phase_passed"] = item["passed"]
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {"created": now(), "history": []}
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {"created": now(), "history": [], "recovered_from_invalid_state": True}


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Resumable Rathaus finalization gate workflow")
    parser.add_argument("--runtime-seconds", type=int, default=60)
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--skip-matrix", action="store_true")
    args = parser.parse_args()

    state = load_state()
    state["workflow_started"] = now()
    state["git_head"] = git_head()
    state["status"] = "running"
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")

    try:
        run("python_compile", [str(PYTHON), "-m", "py_compile",
            "tools/ue5/run_rathaus_v75_front_spawn_headless_check.py",
            "tools/ue5/collect_spawn_to_combat_distance_matrix.py",
            "tools/ue5/rathaus_finalization_workflow.py"])
        run("git_diff_check", ["git", "diff", "--check"])
        run("gameplay_runtime_validator", [str(PYTHON), "tools/gameplay/validate_runtime_combat_systems_2030.py"])
        run("gameplay_bundle_validator", [str(PYTHON), "tools/gameplay/validate_gameplay_bundle.py"])
        run("gameplay_unit_tests", [str(PYTHON), "-m", "unittest", "discover", "-s", "tools/gameplay/tests", "-p", "test_*.py", "-q"])
        run("rathaus_normal_runtime_gate", [str(PYTHON), "tools/ue5/run_rathaus_v75_front_spawn_headless_check.py",
            "--runtime-seconds", str(args.runtime_seconds), "--num-bots", "15"])
        if not args.skip_matrix:
            run("spawn_to_combat_distance_matrix", [str(PYTHON), "tools/ue5/collect_spawn_to_combat_distance_matrix.py",
                "--runtime-seconds", "45", "--num-bots", "15"])
        if not args.skip_build:
            build = Path(r"C:\Program Files\Epic Games\UE_5.8\Engine\Build\BatchFiles\Build.bat")
            run("ue5_lyra_editor_build", ["cmd.exe", "/d", "/c", "call", str(build), "LyraEditor", "Win64", "Development",
                f"-Project={PROJECT / 'SpandauStrike.uproject'}", "-WaitMutex", "-NoHotReload"])
        final = load_state()
        final["status"] = "green"
        final["completed"] = now()
        final["git_head"] = git_head()
        final["next_required"] = "interactive_visual_and_playability_qa"
        STATE_FILE.write_text(json.dumps(final, indent=2), encoding="utf-8")
        print("RATHAUS_FINALIZATION=GREEN")
        return 0
    except Exception as exc:
        failed = load_state()
        failed["status"] = "blocked"
        failed["failed_at"] = now()
        failed["error"] = str(exc)
        failed["next_required"] = "diagnose_last_failed_phase_then_resume"
        STATE_FILE.write_text(json.dumps(failed, indent=2), encoding="utf-8")
        print("RATHAUS_FINALIZATION=BLOCKED " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
