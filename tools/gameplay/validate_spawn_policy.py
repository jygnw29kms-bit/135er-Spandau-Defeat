#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GAMEPLAY = ROOT / "ue5" / "SpandauStrike" / "Design" / "Gameplay"
POLICY = GAMEPLAY / "spawn_policy_v1.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def fail(message):
    raise SystemExit("VALIDATION ERROR: " + message)


def main():
    policy = load(POLICY)
    if policy.get("schema") != "SpandauStrike.SpawnPolicy.v1":
        fail("unexpected spawn policy schema")

    selection = policy["selection"]
    if selection.get("authority") != "server":
        fail("spawn selection must remain server authoritative")
    if selection.get("candidate_source") != "LyraPlayerStart":
        fail("spawn policy must reuse LyraPlayerStart")

    hard_reject = set(selection.get("hard_reject", []))
    required_rejects = {
        "wrong_team",
        "outside_active_front_spawn_band",
        "inside_enemy_capture_radius",
        "blocked_spawn_capsule",
        "direct_enemy_line_of_sight_under_min_distance",
    }
    if not required_rejects.issubset(hard_reject):
        fail("spawn hard-reject contract weakened")

    terms = selection["score_terms"]
    required_terms = {"enemy_distance", "enemy_line_of_sight", "frontline_distance", "friendly_density", "recent_death_heat"}
    if set(terms) != required_terms:
        fail(f"spawn score terms mismatch: {sorted(terms)}")

    enemy = terms["enemy_distance"]
    if not 0 < float(enemy["reject_under_m"]) < float(enemy["preferred_min_m"]) < float(enemy["preferred_max_m"]):
        fail("enemy-distance scoring thresholds invalid")

    los = terms["enemy_line_of_sight"]
    if not 0 < float(los["hard_reject_under_m"]) < float(los["penalty_under_m"]):
        fail("enemy LOS thresholds invalid")
    if float(los["weight"]) >= 0.0:
        fail("enemy LOS must remain a negative score term")

    front = terms["frontline_distance"]
    if not 0 < float(front["preferred_min_m"]) < float(front["preferred_max_m"]):
        fail("frontline distance scoring thresholds invalid")

    heat = terms["recent_death_heat"]
    if float(heat["weight"]) >= 0.0 or float(heat["memory_s"]) <= 0.0:
        fail("recent death heat must be a time-limited penalty")

    frontline = policy["frontline"]
    required_true = [
        "use_current_objective_ownership",
        "spawn_band_follows_team_front",
        "never_spawn_beyond_enemy_owned_front",
        "home_spawns_remain_fallback",
    ]
    if any(frontline.get(key) is not True for key in required_true):
        fail("frontline spawn safety rule weakened")

    protection = policy["protection"]
    duration = float(protection["duration_s"])
    if not 0.0 <= duration <= 2.0:
        fail("spawn protection must remain short (0..2s)")
    if protection.get("ends_on_fire") is not True or protection.get("ends_on_offensive_ability") is not True:
        fail("spawn protection must end on offensive action")

    flags = policy["review_flags"]
    if flags.get("w4_objective_distance_warning_acknowledged") is not True:
        fail("known W4 objective-distance review warning must remain acknowledged")

    print(json.dumps({
        "hard_reject_rules": len(hard_reject),
        "score_terms": len(terms),
        "spawn_protection_s": duration,
        "status": "ok"
    }, sort_keys=True))


if __name__ == "__main__":
    main()
