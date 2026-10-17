#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GAMEPLAY = ROOT / "ue5" / "SpandauStrike" / "Design" / "Gameplay"
BALANCE = GAMEPLAY / "modern_balance_baseline_v1.json"
CAPTURE = GAMEPLAY / "capture_frontline_64p_v1.json"
RUNTIME = GAMEPLAY / "runtime_combat_systems_2030_v1.json"
RULES = GAMEPLAY / "modern_2030_rules_v1.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def fail(message):
    raise SystemExit("VALIDATION ERROR: " + message)


def main():
    b = load(BALANCE)
    capture = load(CAPTURE)
    runtime = load(RUNTIME)
    rules = load(RULES)

    if b.get("schema") != "SpandauStrike.ModernBalanceBaseline.v1":
        fail("unexpected modern balance schema")
    if int(b["health"]["base"]) != 100 or b["health"]["regeneration"] is not False:
        fail("health baseline must remain 100 with no regeneration")

    expected = {"AssaultRifle", "PDWCarbine", "LightMachineGun", "DMR", "ServicePistol"}
    if set(b["weapon_families"]) != expected:
        fail("weapon family set mismatch")
    ar = b["weapon_families"]["AssaultRifle"]
    if not 3 <= (100 + ar["damage"] - 1) // ar["damage"] <= 4:
        fail("assault rifle body-shot lethality outside target")
    dmr = b["weapon_families"]["DMR"]
    if dmr["damage"] * dmr["upper_torso_multiplier"] >= 100:
        fail("DMR must not upper-torso one-shot")
    if dmr["damage"] * dmr["head_multiplier"] < 100:
        fail("DMR headshot must be lethal")

    mobility = b["class_mobility"]
    if set(mobility) != set(rules["modern_roles"]):
        fail("class mobility roles disagree with modern roles")
    if mobility["Scout"]["speed_multiplier"] <= mobility["Operator"]["speed_multiplier"]:
        fail("Scout must remain more mobile than Operator")
    if mobility["Support"]["speed_multiplier"] >= mobility["Operator"]["speed_multiplier"]:
        fail("Support must remain slower than Operator")

    cap = b["capture_scaling"]
    if float(cap["base_single_attacker_s"]) != float(capture["capture"]["single_attacker_capture_s"]):
        fail("capture base time disagrees with Capture Frontline")
    multipliers = [float(cap["attackers"][str(i)]) for i in range(1, 5)]
    if multipliers != sorted(multipliers) or multipliers[0] != 1.0:
        fail("capture scaling must increase from 1.0")
    four_player_time = cap["base_single_attacker_s"] / multipliers[-1]
    if four_player_time < float(cap["minimum_capture_time_s"]):
        fail("capture scaling violates minimum capture time")

    spawn = b["spawn_balance"]
    if float(spawn["wave_interval_s"]) != float(runtime["respawn"]["base_wave_interval_s"]):
        fail("spawn wave interval disagrees with runtime systems")
    if spawn["hard_reject_enemy_distance_m"] >= spawn["preferred_enemy_distance_m"][0]:
        fail("spawn hard reject must be below preferred enemy distance")

    suppression = b["suppression_balance"]
    if float(suppression["max_aim_instability_multiplier"]) != float(runtime["suppression"]["max_aim_instability_multiplier"]):
        fail("suppression baseline disagrees with runtime systems")
    if suppression["forced_blindness"] is not False:
        fail("forced blindness must remain disabled")

    pacing = b["match_pacing"]
    if pacing["target_duration_min"] != capture["target_match_duration_min"]:
        fail("match duration disagrees with capture spec")
    if int(pacing["attacker_start_tickets"]) != int(capture["tickets"]["attacker_start"]):
        fail("attacker tickets disagree with capture spec")
    if int(pacing["sector_ticket_refund"]) != int(capture["tickets"]["sector_capture_refund"]):
        fail("sector refund disagrees with capture spec")

    score = b["score"]
    if int(score["capture_complete"]) <= int(score["kill"]):
        fail("capture completion must outscore kill")

    print(json.dumps({
        "weapon_families": len(b["weapon_families"]),
        "classes": len(mobility),
        "four_player_capture_s": round(four_player_time, 2),
        "ideal_match_min": pacing["ideal_duration_min"],
        "status": "ok"
    }, sort_keys=True))


if __name__ == "__main__":
    main()
