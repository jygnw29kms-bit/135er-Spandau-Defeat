#!/usr/bin/env python3
import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GAMEPLAY = ROOT / "ue5" / "SpandauStrike" / "Design" / "Gameplay"
TUNING = GAMEPLAY / "core_gameplay_tuning_v1.json"
WEAPONS = GAMEPLAY / "weapon_archetypes_v1.json"
DEFAULT_OUT = ROOT / "ue5" / "SpandauStrike" / "Design" / "Generated" / "gameplay_balance_report_v1.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def round2(value):
    return round(float(value), 2)


def shots_to_kill(damage, health=100.0):
    return int(math.ceil(health / float(damage))) if damage > 0 else None


def main():
    parser = argparse.ArgumentParser(description="Derive review metrics from the current Spandau Strike gameplay tuning baseline.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    tuning = load(TUNING)
    weapons = load(WEAPONS)["archetypes"]
    movement = tuning["movement"]
    stamina = tuning["stamina"]

    full_sprint_s = stamina["max"] / stamina["sprint_drain_per_s"]
    full_regen_s = stamina["regen_delay_s"] + stamina["max"] / stamina["regen_per_s"]
    full_jumps = int(stamina["max"] // stamina["jump_cost"])

    class_metrics = {}
    for name, values in tuning["classes"].items():
        speed_mult = float(values["speed_multiplier"])
        run_cm_s = movement["run_speed_cm_s"] * speed_mult
        sprint_base = movement["sprint_speed_heavy_cm_s"] if name in {"MG", "Rocket"} else movement["sprint_speed_light_cm_s"]
        sprint_cm_s = sprint_base * speed_mult
        class_metrics[name] = {
            "run_speed_cm_s": round2(run_cm_s),
            "sprint_speed_cm_s": round2(sprint_cm_s),
            "run_100m_seconds": round2(10000.0 / run_cm_s),
            "sprint_100m_seconds": round2(10000.0 / sprint_cm_s),
            "stamina_drain_multiplier": values["stamina_drain_multiplier"],
        }

    weapon_metrics = {}
    for name, values in weapons.items():
        base = values.get("base_damage")
        metric = {"role": values.get("role")}
        if base:
            metric["base_shots_to_kill_100hp"] = shots_to_kill(base)
        hit = values.get("hit_zone_multipliers", {})
        if base and "upper_torso" in hit:
            upper = base * hit["upper_torso"]
            metric["upper_torso_damage"] = round2(upper)
            metric["upper_torso_lethal_100hp"] = upper >= 100.0
        if name == "HeavyMG":
            metric["deployed_to_undeployed_spread_ratio"] = round2(values["deployed_spread_deg"] / values["undeployed_spread_deg"])
            metric["deployed_to_undeployed_recoil_ratio"] = round2(values["deployed_recoil_multiplier"] / values["undeployed_recoil_multiplier"])
        if name == "RocketLauncher":
            metric["direct_damage"] = values["direct_damage"]
            metric["splash_damage"] = values["splash_damage"]
            metric["splash_radius_m"] = values["splash_radius_m"]
        weapon_metrics[name] = metric

    warnings = []
    if not 4.0 <= full_sprint_s <= 8.0:
        warnings.append("full_sprint_duration_outside_4_8s_review_band")
    if full_regen_s > 8.0:
        warnings.append("full_stamina_recovery_over_8s")
    if full_jumps > 5:
        warnings.append("too_many_full_stamina_jumps")
    if class_metrics["MG"]["run_speed_cm_s"] >= class_metrics["Rifleman"]["run_speed_cm_s"]:
        warnings.append("mg_not_slower_than_rifleman")
    if not weapon_metrics["BoltRifle"].get("upper_torso_lethal_100hp"):
        warnings.append("bolt_rifle_upper_torso_not_lethal")
    if not weapon_metrics["ScopedRifle"].get("upper_torso_lethal_100hp"):
        warnings.append("scoped_rifle_upper_torso_not_lethal")

    report = {
        "schema": "SpandauStrike.GameplayBalanceReport.v1",
        "stamina_metrics": {
            "full_sprint_seconds_at_base_drain": round2(full_sprint_s),
            "full_recovery_seconds_including_delay": round2(full_regen_s),
            "full_cost_jumps_before_empty": full_jumps,
        },
        "class_metrics": class_metrics,
        "weapon_metrics": weapon_metrics,
        "warnings": warnings,
        "warning_count": len(warnings),
        "note": "Derived metrics are review aids. Final values require controlled UE playtests and networked combat validation."
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "full_sprint_s": report["stamina_metrics"]["full_sprint_seconds_at_base_drain"],
        "full_recovery_s": report["stamina_metrics"]["full_recovery_seconds_including_delay"],
        "warnings": len(warnings),
        "status": "ok"
    }, sort_keys=True))
    print(args.out)


if __name__ == "__main__":
    main()
