#!/usr/bin/env python3
import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GAMEPLAY_DIR = ROOT / "ue5" / "SpandauStrike" / "Design" / "Gameplay"
DEFAULT_OUT = ROOT / "ue5" / "SpandauStrike" / "Design" / "Generated"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_csv(path: Path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Generate Unreal-friendly CSV seeds from Spandau Strike gameplay JSON.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    tuning = load(GAMEPLAY_DIR / "core_gameplay_tuning_v1.json")
    weapons = load(GAMEPLAY_DIR / "weapon_archetypes_v1.json")["archetypes"]
    loadouts = load(GAMEPLAY_DIR / "class_loadouts_v1.json")["classes"]

    class_rows = []
    for class_name, values in tuning["classes"].items():
        loadout = loadouts[class_name]
        class_rows.append({
            "Name": class_name,
            "GameplayTag": loadout["gameplay_tag"],
            "PrimaryArchetype": loadout["primary_archetype"],
            "Role": loadout["role"],
            "SpeedMultiplier": values["speed_multiplier"],
            "AccelerationMultiplier": values["acceleration_multiplier"],
            "StaminaDrainMultiplier": values["stamina_drain_multiplier"],
            "AbilityFocus": ";".join(loadout.get("ability_focus", [])),
        })

    write_csv(
        args.out_dir / "DT_SpandauStrike_Classes.csv",
        ["Name", "GameplayTag", "PrimaryArchetype", "Role", "SpeedMultiplier", "AccelerationMultiplier", "StaminaDrainMultiplier", "AbilityFocus"],
        class_rows,
    )

    weapon_rows = []
    for name, values in weapons.items():
        hit = values.get("hit_zone_multipliers", {})
        weapon_rows.append({
            "Name": name,
            "Role": values.get("role", ""),
            "FireMode": values.get("fire_mode", ""),
            "BaseDamage": values.get("base_damage", values.get("direct_damage", 0.0)),
            "RateRPM": values.get("rate_rpm", 0.0),
            "BoltCycleSeconds": values.get("bolt_cycle_s", 0.0),
            "ReloadSeconds": values.get("reload_s", 0.0),
            "HeadMultiplier": hit.get("head", 1.0),
            "UpperTorsoMultiplier": hit.get("upper_torso", 1.0),
            "LowerTorsoMultiplier": hit.get("lower_torso", 1.0),
            "ArmMultiplier": hit.get("arm", 1.0),
            "LegMultiplier": hit.get("leg", 1.0),
            "RequiresBipodForPrecision": str(bool(values.get("requires_bipod_for_precision", False))).lower(),
        })

    write_csv(
        args.out_dir / "DT_SpandauStrike_WeaponArchetypes.csv",
        ["Name", "Role", "FireMode", "BaseDamage", "RateRPM", "BoltCycleSeconds", "ReloadSeconds", "HeadMultiplier", "UpperTorsoMultiplier", "LowerTorsoMultiplier", "ArmMultiplier", "LegMultiplier", "RequiresBipodForPrecision"],
        weapon_rows,
    )

    movement = tuning["movement"]
    stamina = tuning["stamina"]
    movement_rows = [{
        "Name": "Default",
        "WalkSpeedCmS": movement["walk_speed_cm_s"],
        "RunSpeedCmS": movement["run_speed_cm_s"],
        "CrouchSpeedCmS": movement["crouch_speed_cm_s"],
        "ProneSpeedCmS": movement["prone_speed_cm_s"],
        "SprintSpeedLightCmS": movement["sprint_speed_light_cm_s"],
        "SprintSpeedHeavyCmS": movement["sprint_speed_heavy_cm_s"],
        "AirControl": movement["air_control"],
        "DirectionReversalAccelerationMultiplier": movement["direction_reversal_acceleration_multiplier"],
        "LandingRecoverySeconds": movement["landing_recovery_s"],
        "ProneEnterSeconds": movement["prone_enter_s"],
        "ProneExitSeconds": movement["prone_exit_s"],
        "MaxStamina": stamina["max"],
        "SprintDrainPerSecond": stamina["sprint_drain_per_s"],
        "JumpStaminaCost": stamina["jump_cost"],
        "StaminaRegenDelaySeconds": stamina["regen_delay_s"],
        "StaminaRegenPerSecond": stamina["regen_per_s"],
    }]
    write_csv(
        args.out_dir / "DT_SpandauStrike_Movement.csv",
        list(movement_rows[0].keys()),
        movement_rows,
    )

    summary = {
        "classes": len(class_rows),
        "weapon_archetypes": len(weapon_rows),
        "movement_profiles": len(movement_rows),
        "out_dir": args.out_dir.as_posix(),
    }
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
