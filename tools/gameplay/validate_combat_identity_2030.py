#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GAMEPLAY = ROOT / "ue5" / "SpandauStrike" / "Design" / "Gameplay"
IDENTITY = GAMEPLAY / "combat_identity_2030_v1.json"
MODERN = GAMEPLAY / "modern_2030_rules_v1.json"
CAPTURE = GAMEPLAY / "capture_frontline_64p_v1.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def fail(message):
    raise SystemExit("VALIDATION ERROR: " + message)


def main():
    identity = load(IDENTITY)
    modern = load(MODERN)
    capture = load(CAPTURE)

    if identity.get("schema") != "SpandauStrike.CombatIdentity2030.v1":
        fail("unexpected combat identity schema")

    exclusions = set(identity.get("hard_exclusions", []))
    required_exclusions = {
        "squads_required", "squad_spawn", "commander_dependency",
        "fob_logistics_loop", "arcade_health_regen", "bullet_sponge_damage"
    }
    if not required_exclusions.issubset(exclusions):
        fail("combat identity lost a required anti-milsim/anti-arcade exclusion")

    if modern["player_cap"]["max_players"] != 64 or modern["player_cap"]["players_per_team"] != 32:
        fail("modern rules must remain 64 players / 32 per team")
    if modern["player_cap"]["squads_enabled"] is not False:
        fail("modern rules unexpectedly enabled squads")
    if capture["squads_enabled"] is not False:
        fail("capture unexpectedly enabled squads")

    communication = identity["communication"]
    if communication.get("team_channel") is not True or communication.get("proximity_channel") is not True:
        fail("team and proximity communication are required")
    if communication.get("squad_channel") is not False:
        fail("squad voice channel must remain disabled")

    readability = identity["combat_readability"]
    if readability.get("damage_numbers") is not False:
        fail("damage numbers must remain disabled")
    if readability.get("floating_enemy_markers") is not False:
        fail("floating enemy markers must remain disabled")

    ammo = identity["ammo_and_resupply"]
    if ammo.get("ammo_is_finite") is not True or ammo.get("auto_refill_during_life") is not False:
        fail("finite ammunition contract weakened")
    if ammo.get("resupply_must_not_create_infinite_grenade_spam") is not True:
        fail("grenade-spam protection missing")

    suppression = identity["suppression"]
    if suppression.get("enabled") is not True:
        fail("suppression contract disabled")
    if suppression.get("forced_blindness") is not False:
        fail("suppression must not rely on forced blindness")

    pressure = identity["map_pressure"]
    low, high = pressure["spawn_to_action_target_s"]
    if not (10 <= low < high <= 45):
        fail("spawn-to-action target outside intended accessible tactical band")
    if int(pressure["minimum_viable_routes"]) < 3:
        fail("front sectors require at least three meaningful route patterns")

    asymmetry = identity["faction_asymmetry"]
    if asymmetry.get("allowed") is not True or asymmetry.get("no_strict_mirror_loadouts") is not True:
        fail("2030 faction asymmetry contract weakened")

    score = identity["objective_scoring"]
    if score.get("kill_death_is_not_primary_progression_metric") is not True:
        fail("objective-first scoring contract weakened")

    print(json.dumps({
        "players": modern["player_cap"]["max_players"],
        "squads": modern["player_cap"]["squads_enabled"],
        "audio_features": len(identity["audio"]["features"]),
        "route_minimum": pressure["minimum_viable_routes"],
        "status": "ok"
    }, sort_keys=True))


if __name__ == "__main__":
    main()
