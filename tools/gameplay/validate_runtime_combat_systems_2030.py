#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GAMEPLAY = ROOT / "ue5" / "SpandauStrike" / "Design" / "Gameplay"
RUNTIME = GAMEPLAY / "runtime_combat_systems_2030_v1.json"
CAPTURE = GAMEPLAY / "capture_frontline_64p_v1.json"
IDENTITY = GAMEPLAY / "combat_identity_2030_v1.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def fail(message):
    raise SystemExit("VALIDATION ERROR: " + message)


def main():
    runtime = load(RUNTIME)
    capture = load(CAPTURE)
    identity = load(IDENTITY)

    if runtime.get("schema") != "SpandauStrike.RuntimeCombatSystems2030.v1":
        fail("unexpected runtime combat schema")

    respawn = runtime["respawn"]
    if respawn.get("squad_spawn") is not False:
        fail("squad spawn must stay disabled")
    if not 6.0 <= float(respawn["base_wave_interval_s"]) <= 15.0:
        fail("respawn wave outside fast-action baseline")
    if respawn["spawn_to_action_target_s"] != identity["map_pressure"]["spawn_to_action_target_s"]:
        fail("spawn-to-action target disagrees with combat identity")
    if float(respawn["frontline_spawn_shift_delay_s"]) != float(capture["front"]["transition_delay_s"]):
        fail("spawn shift delay disagrees with Capture Frontline")

    hud = runtime["hud"]
    forbidden = set(hud.get("forbidden", []))
    required_forbidden = {"damage_numbers", "floating_enemy_markers", "persistent_enemy_outline"}
    if not required_forbidden.issubset(forbidden):
        fail("minimal HUD exclusions weakened")

    scoring = runtime["scoring"]
    if int(scoring["capture_complete"]) <= int(scoring["kill"]):
        fail("capture completion must score above a normal kill")
    if int(scoring["defense_kill"]) <= int(scoring["kill"]):
        fail("defense kill must reward objective play")
    if scoring.get("objective_actions_weighted_above_kd") is not True:
        fail("objective-first scoring rule weakened")

    ammo = runtime["ammo_resupply"]
    if ammo.get("finite_ammo") is not True or ammo.get("auto_refill_during_life") is not False:
        fail("finite ammo contract weakened")
    if float(ammo["grenade_resupply_cooldown_s"]) < float(ammo["support_pack_cooldown_s"]):
        fail("grenade resupply must not be faster than general support resupply")

    suppression = runtime["suppression"]
    if suppression.get("forced_blindness") is not False or suppression.get("input_lock") is not False:
        fail("suppression may not remove player control")
    if not 1.0 <= float(suppression["max_aim_instability_multiplier"]) <= 1.25:
        fail("suppression aim instability outside subtle band")

    voice = runtime["voice_and_callouts"]
    if voice.get("squad_voice") is not False:
        fail("squad voice must remain disabled")
    if voice.get("team_voice") is not True or voice.get("proximity_voice") is not True:
        fail("team and proximity voice are required")

    flow = runtime["round_flow"]
    if float(flow["sector_transition_s"]) != float(capture["front"]["transition_delay_s"]):
        fail("round flow sector transition disagrees with capture spec")
    if flow["target_match_duration_min"] != capture["target_match_duration_min"]:
        fail("match duration target disagrees with capture spec")

    print(json.dumps({
        "respawn_wave_s": respawn["base_wave_interval_s"],
        "score_capture": scoring["capture_complete"],
        "score_kill": scoring["kill"],
        "suppression_max": suppression["max_aim_instability_multiplier"],
        "status": "ok"
    }, sort_keys=True))


if __name__ == "__main__":
    main()
