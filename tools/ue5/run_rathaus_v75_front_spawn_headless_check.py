from __future__ import annotations
import argparse
import json
import os
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine-root", default=r"C:\Program Files\Epic Games\UE_5.8")
    parser.add_argument("--startup-timeout", type=int, default=120)
    parser.add_argument("--runtime-seconds", type=int, default=45)
    parser.add_argument("--num-bots", type=int, default=15)
    parser.add_argument("--map-path", default="/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v75_FRONTSPAWNS")
    parser.add_argument("--combat-probe", action="store_true")
    parser.add_argument("--combat-probe-distance-cm", type=float, default=0.0)
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[2]
    project_root = repo / "ue5" / "SpandauStrike"
    uproject = project_root / "SpandauStrike.uproject"
    engine_root = Path(args.engine_root)
    editor = engine_root / "Engine" / "Binaries" / "Win64" / "UnrealEditor.exe"
    cmd = engine_root / "Engine" / "Binaries" / "Win64" / "UnrealEditor-Cmd.exe"
    validator = project_root / "Content" / "Python" / "validate_rathaus_v75_front_spawns.py"
    report = project_root / "Saved" / "Reports" / "v75_front_spawn_headless_workflow.json"
    run_stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    log = project_root / "Saved" / "Logs" / f"SpandauStrike_headless_{run_stamp}.log"
    validator_log = project_root / "Saved" / "Logs" / f"SpandauStrike_validator_{run_stamp}.log"
    url = f"{args.map_path}?Experience=B_ShooterGame_Elimination?NumBots={args.num_bots}"
    bad = re.compile(r"FellOutOfWorld|KillZ|WorldBounds|Accessed None|Zugriff auf [„\"]Keine|Failed to spawn|SpawnActor failed|Fatal error|Unhandled Exception|Ensure condition failed|Handled ensure", re.I)
    known_nullrhi_spawn_cue = re.compile(r"Zugriff auf [„\"]Keine.*(?:CallFunc_SpawnSystemAttached_ReturnValue|NS_ShellEject|NS_MuzzleFlash|NS_Tracer|Decal)|Accessed None.*(?:CallFunc_SpawnSystemAttached_ReturnValue|NS_ShellEject|NS_MuzzleFlash|NS_Tracer|Decal)", re.I)
    result = {
        "timestamp": datetime.now(timezone.utc).astimezone().isoformat(),
        "map": url,
        "runtime_log": str(log),
        "validator_log": str(validator_log),
        "static_validation": False,
        "startup_ready": False,
        "front_spawn_seen": False,
        "respawn_probe_armed": False,
        "respawn_probe_triggered": False,
        "death_heat_seen": False,
        "respawn_queued": False,
        "spawn_selected": False,
        "safety_fallback": False,
        "respawn_completed": False,
        "spawn_to_action_seen": False,
        "spawn_to_combat_seen": False,
        "spawn_to_combat_seconds": None,
        "spawn_to_combat_damage": None,
        "spawn_to_combat_target": None,
        "combat_probe_distance_cm": None,
        "combat_probe_target_is_bot": None,
        "combat_probe_triggered": False,
        "combat_hold_seen": False,
        "warmup_to_playing_seen": False,
        "non_death_restart_bypass_seen": False,
        "round_reset_ticket_loss_seen": False,
        "known_nullrhi_spawn_cue_warnings": 0,
        "bad_count": -1,
        "unexpected_bad_count": -1,
        "passed": False,
    }
    proc: subprocess.Popen[str] | None = None
    try:
        validator_env = dict(os.environ)
        validator_env["SPANDAU_VALIDATION_MAP"] = args.map_path
        validator_run = subprocess.run(
            [str(cmd), str(uproject), "-run=pythonscript", f"-script={validator}", "-unattended", "-nop4", "-nosplash", "-nullrhi", f"-abslog={validator_log}"],
            cwd=project_root,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=validator_env,
        )
        if validator_run.returncode != 0:
            raise RuntimeError(f"v75 validator failed: {validator_run.returncode}")
        result["static_validation"] = True
        log.parent.mkdir(parents=True, exist_ok=True)
        launch_args = [str(editor), str(uproject), url, "-game", "-nullrhi", "-nosound", "-unattended", "-nop4", f"-abslog={log}", "-SpandauRespawnProbe"]
        if args.combat_probe:
            launch_args.append("-SpandauCombatProbe")
            if args.combat_probe_distance_cm > 0.0:
                launch_args.append(f"-SpandauCombatProbeDistanceCm={args.combat_probe_distance_cm:.1f}")
        proc = subprocess.Popen(launch_args, cwd=project_root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline = time.time() + args.startup_timeout
        while time.time() < deadline:
            if proc.poll() is not None:
                raise RuntimeError(f"Unreal exited during startup: {proc.returncode}")
            text = read_text(log)
            result["startup_ready"] = "SpandauCaptureDirector teams resolved" in text and "Spandau objective routing: sector=1 routed=15 failed=0" in text
            if result["startup_ready"]:
                break
            time.sleep(1)
        if not result["startup_ready"]:
            raise RuntimeError("v75 runtime not ready")
        end = time.time() + args.runtime_seconds
        while time.time() < end and proc.poll() is None:
            time.sleep(1)
        text = read_text(log)
        result["front_spawn_seen"] = "Spandau front spawn candidates:" in text
        result["respawn_probe_armed"] = "Spandau respawn probe armed:" in text
        result["respawn_probe_triggered"] = "Spandau respawn probe trigger:" in text
        result["death_heat_seen"] = "Spandau death heat event:" in text
        result["respawn_queued"] = "Spandau respawn queued:" in text
        result["spawn_selected"] = "Spandau spawn selected:" in text
        result["safety_fallback"] = "Spandau front spawn safety rejected all candidates; falling back to base starts:" in text
        result["respawn_completed"] = "Spandau respawn completed:" in text
        result["spawn_to_action_seen"] = "Spandau spawn-to-action:" in text
        combat_match = re.search(r"Spandau spawn-to-combat:.*?seconds=([0-9.]+).*?damage=([0-9.]+).*?target=([^\r\n]+)", text)
        result["spawn_to_combat_seen"] = combat_match is not None
        if combat_match:
            result["spawn_to_combat_seconds"] = float(combat_match.group(1))
            result["spawn_to_combat_damage"] = float(combat_match.group(2))
            result["spawn_to_combat_target"] = combat_match.group(3).strip()
        probe_match = re.search(r"Spandau combat probe trigger:.*?distance=([0-9.]+)cm.*?targetBot=([01])", text)
        result["combat_probe_triggered"] = probe_match is not None
        if probe_match:
            result["combat_probe_distance_cm"] = float(probe_match.group(1))
            result["combat_probe_target_is_bot"] = probe_match.group(2) == "1"
        result["combat_hold_seen"] = re.search(r"combatHeld=[1-9][0-9]*", text) is not None
        result["warmup_to_playing_seen"] = "Warmup Phase Ended" in text and "Playing Phase" in text
        result["non_death_restart_bypass_seen"] = "Spandau non-death restart bypassed:" in text
        result["round_reset_ticket_loss_seen"] = "Spandau respawn wave: spawned=16 attackerTicketSpawns=8" in text
        result["known_nullrhi_spawn_cue_warnings"] = len(known_nullrhi_spawn_cue.findall(text))
        result["bad_count"] = len(bad.findall(text))
        result["unexpected_bad_count"] = max(0, result["bad_count"] - result["known_nullrhi_spawn_cue_warnings"])
        required = [
            "static_validation", "startup_ready", "front_spawn_seen", "respawn_probe_armed",
            "respawn_probe_triggered", "death_heat_seen", "respawn_queued", "respawn_completed",
        ]
        spawn_path_ok = result["spawn_selected"] or result["safety_fallback"]
        round_reset_ok = not result["round_reset_ticket_loss_seen"]
        if args.runtime_seconds >= 45:
            round_reset_ok = round_reset_ok and result["warmup_to_playing_seen"] and result["non_death_restart_bypass_seen"]
        activity_path_ok = result["spawn_to_action_seen"]
        combat_probe_ok = True
        if args.combat_probe:
            combat_probe_ok = result["combat_probe_triggered"] and result["combat_hold_seen"] and result["spawn_to_combat_seen"]
            activity_path_ok = result["spawn_to_combat_seen"]
        result["passed"] = all(result[key] for key in required) and spawn_path_ok and activity_path_ok and round_reset_ok and combat_probe_ok and result["unexpected_bad_count"] == 0
        if not result["passed"]:
            raise RuntimeError("v75 runtime gate failed")
        return 0
    except Exception as exc:
        result["error"] = str(exc)
        return 1
    finally:
        if proc and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=8)
            except subprocess.TimeoutExpired:
                proc.kill()
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print("V75_FRONTSPAWN_HEADLESS=" + json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    raise SystemExit(main())
