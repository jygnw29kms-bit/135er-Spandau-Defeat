#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GAMEPLAY = ROOT / "ue5" / "SpandauStrike" / "Design" / "Gameplay"
CONTRACT = GAMEPLAY / "damage_contract_v1.json"
WEAPONS = GAMEPLAY / "weapon_archetypes_v1.json"
TAGS = ROOT / "tools" / "gameplay" / "spandau_strike_gameplay_tags.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def fail(message):
    raise SystemExit("VALIDATION ERROR: " + message)


def main():
    contract = load(CONTRACT)
    weapons = load(WEAPONS)["archetypes"]
    tags = set(load(TAGS)["tags"])

    if contract.get("schema") != "SpandauStrike.DamageContract.v1":
        fail("unexpected damage contract schema")
    health = float(contract.get("health_baseline", 0.0))
    if health != 100.0:
        fail("health baseline must remain 100")

    zones = contract.get("hit_zones", {})
    expected_zones = {"Head", "UpperTorso", "LowerTorso", "Arm", "Leg"}
    if set(zones) != expected_zones:
        fail(f"hit zone set mismatch: {sorted(zones)}")
    for name, definition in zones.items():
        tag = definition.get("gameplay_tag")
        if tag not in tags:
            fail(f"hit zone {name} references non-canonical tag: {tag}")
        if float(definition.get("default_multiplier", 0.0)) <= 0.0:
            fail(f"hit zone {name} has invalid default multiplier")

    policy = contract.get("weapon_damage_policy", {})
    if set(policy) != set(weapons):
        fail("damage policy must cover every weapon archetype exactly once")

    for weapon_name in ("BoltRifle", "ScopedRifle"):
        values = weapons[weapon_name]
        hit = values.get("hit_zone_multipliers", {})
        upper_damage = float(values["base_damage"]) * float(hit["upper_torso"])
        head_damage = float(values["base_damage"]) * float(hit["head"])
        arm_damage = float(values["base_damage"]) * float(hit["arm"])
        leg_damage = float(values["base_damage"]) * float(hit["leg"])
        rules = policy[weapon_name]
        if rules.get("upper_torso_must_be_lethal") is not True or upper_damage < health:
            fail(f"{weapon_name} upper-torso one-shot contract broken")
        if rules.get("head_must_be_lethal") is not True or head_damage < health:
            fail(f"{weapon_name} head lethality contract broken")
        if rules.get("limb_one_shot_forbidden") is not True:
            fail(f"{weapon_name} limb one-shot policy weakened")
        if arm_damage >= health or leg_damage >= health:
            fail(f"{weapon_name} limb damage became one-shot lethal")

    for weapon_name in ("AssaultSMG", "SupportAutomatic", "HeavyMG"):
        values = weapons[weapon_name]
        base = float(values["base_damage"])
        rules = policy[weapon_name]
        if rules.get("upper_torso_must_be_lethal") is not False:
            fail(f"{weapon_name} must not require upper-torso one-shot lethality")
        if base >= health:
            fail(f"{weapon_name} base damage cannot one-shot 100 health")
        if rules.get("limb_one_shot_forbidden") is not True:
            fail(f"{weapon_name} limb one-shot policy weakened")

    rocket_rules = policy["RocketLauncher"]
    if rocket_rules.get("uses_radial_damage") is not True or rocket_rules.get("direct_hit_uses_direct_damage") is not True:
        fail("RocketLauncher direct/radial damage contract weakened")
    rocket = weapons["RocketLauncher"]
    if float(rocket["direct_damage"]) <= float(rocket["splash_damage"]):
        fail("RocketLauncher direct damage must exceed splash damage")

    authority = contract.get("authority", {})
    required_true = [
        "server_owns_final_damage",
        "server_resolves_hit_zone",
        "client_hitmarker_is_feedback_only",
        "damage_numbers_disabled",
        "shield_damage_disabled",
    ]
    if any(authority.get(key) is not True for key in required_true):
        fail("damage authority/presentation contract weakened")

    print(json.dumps({
        "hit_zones": len(zones),
        "weapon_policies": len(policy),
        "health_baseline": health,
        "status": "ok"
    }, sort_keys=True))


if __name__ == "__main__":
    main()
