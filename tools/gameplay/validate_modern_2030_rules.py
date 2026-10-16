#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GAMEPLAY = ROOT / "ue5" / "SpandauStrike" / "Design" / "Gameplay"
RULES = GAMEPLAY / "modern_2030_rules_v1.json"
CAPTURE = GAMEPLAY / "capture_frontline_64p_v1.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def fail(message):
    raise SystemExit("VALIDATION ERROR: " + message)


def main():
    rules = load(RULES)
    capture = load(CAPTURE)

    cap = rules["player_cap"]
    if cap["max_players"] != 64 or cap["players_per_team"] != 32 or cap["teams"] != 2:
        fail("2030 player cap must remain 64 = 32v32")
    if cap["squads_enabled"] is not False or capture["squads_enabled"] is not False:
        fail("squads must remain disabled for the core mode")

    factions = rules["factions"]
    if set(factions) != {"135er", "opposition"}:
        fail("modern faction set mismatch")
    if factions["135er"]["language"] != "de":
        fail("135er radio language must remain German")
    if factions["135er"]["primary_mark"] != "Spandau_coat_of_arms":
        fail("135er primary identity mark must remain the Spandau coat of arms")
    if factions["opposition"]["language"] != "en":
        fail("opposition radio language must remain English")

    expected_roles = {"Operator", "Scout", "Support", "Marksman"}
    if set(rules["modern_roles"]) != expected_roles:
        fail("modern role set mismatch")

    model = rules["player_model_direction"]
    if model.get("humans_not_team_color_mannequins") is not True:
        fail("player models must remain human character variants")
    if model.get("no_sci_fi_body_modifications") is not True:
        fail("2030 visual direction must remain non-sci-fi")

    combat = rules["combat"]
    if combat.get("low_time_to_kill") is not True:
        fail("high lethality baseline weakened")
    if combat.get("regenerating_health") is not False:
        fail("automatic health regeneration must remain disabled")
    if combat.get("anti_bunnyhop") is not True:
        fail("anti-bunnyhop movement rule weakened")

    if capture["max_players"] != 64 or capture["team_size"] != 32:
        fail("capture mode player count mismatch")
    front = capture["front"]
    if front["type"] != "sector_by_sector" or front["only_current_sector_active"] is not True:
        fail("capture must use a shifting sector front")
    if front["backcap_allowed"] is not False:
        fail("capture back-cap must remain disabled")
    if front["capture_points_per_sector_default"] != 2:
        fail("default capture sector must keep two points")

    tickets = capture["tickets"]
    if tickets["attacker_start"] != 300 or tickets["respawn_cost"] != 1:
        fail("attacker ticket baseline mismatch")
    if tickets["sector_capture_refund"] != 50:
        fail("sector ticket refund must remain 50")
    if tickets["defender_respawns"] != "unlimited":
        fail("defender respawn baseline mismatch")

    capture_rules = capture["capture"]
    if float(capture_rules["single_attacker_capture_s"]) != 45.0:
        fail("single-attacker capture baseline must remain 45 seconds")
    if capture_rules["contested_behavior"] != "pause":
        fail("contested capture must pause")

    design = capture["map_design"]
    if int(design["minimum_attack_routes_per_sector"]) < 2:
        fail("every sector needs at least two attack routes")
    if design["additional_risky_flank_required"] is not True:
        fail("every sector needs an additional risky flank")
    if design["reality_is_layout_basis_not_constraint"] is not True:
        fail("map design must preserve reality-as-basis rule")

    print(json.dumps({
        "players": cap["max_players"],
        "team_size": cap["players_per_team"],
        "roles": len(expected_roles),
        "capture_points_per_sector": front["capture_points_per_sector_default"],
        "status": "ok"
    }, sort_keys=True))


if __name__ == "__main__":
    main()
