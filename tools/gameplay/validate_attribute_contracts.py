#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GAMEPLAY = ROOT / "ue5" / "SpandauStrike" / "Design" / "Gameplay"
CONTRACTS = GAMEPLAY / "attribute_contracts_v1.json"
TUNING = GAMEPLAY / "core_gameplay_tuning_v1.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def fail(message):
    raise SystemExit("VALIDATION ERROR: " + message)


def lookup(data, dotted):
    parts = dotted.split(".")
    if parts and parts[0].endswith("_v1"):
        parts = parts[1:]
    current = data
    for part in parts:
        if not isinstance(current, dict) or part not in current:
            fail(f"attribute source path missing: {dotted}")
        current = current[part]
    return current


def main():
    contracts = load(CONTRACTS)
    tuning = load(TUNING)
    sets = contracts.get("attribute_sets", {})

    expected_sets = {"StaminaSet", "MovementProfileSet", "WeaponHandlingSet"}
    if set(sets) != expected_sets:
        fail(f"attribute set mismatch: {sorted(sets)}")

    stamina = sets["StaminaSet"]["attributes"]
    required_stamina = {"Stamina", "MaxStamina", "StaminaRegenRate", "SprintDrainRate", "JumpStaminaCost"}
    if set(stamina) != required_stamina:
        fail(f"stamina attribute mismatch: {sorted(stamina)}")

    for attribute_name, definition in stamina.items():
        source = definition.get("source")
        if source:
            lookup(tuning, source)
        clamp_source = definition.get("clamp_max_source")
        if clamp_source:
            lookup(tuning, clamp_source)
        if definition.get("replication") not in {"owner_and_server", "all_clients", "server_only"}:
            fail(f"unsupported replication policy on {attribute_name}")

    max_stamina = float(tuning["stamina"]["max"])
    if float(stamina["Stamina"]["initial"]) != max_stamina:
        fail("initial Stamina must equal max stamina baseline")
    if float(stamina["Stamina"]["clamp_min"]) != 0.0:
        fail("Stamina clamp minimum must remain zero")

    movement = sets["MovementProfileSet"]["attributes"]
    required_movement = {"ClassSpeedMultiplier", "ClassAccelerationMultiplier", "ClassStaminaDrainMultiplier"}
    if set(movement) != required_movement:
        fail(f"movement profile attribute mismatch: {sorted(movement)}")

    classes = tuning["classes"]
    for class_name, class_values in classes.items():
        for attribute_name, definition in movement.items():
            pattern = definition.get("source_pattern", "")
            key = {
                "ClassSpeedMultiplier": "speed_multiplier",
                "ClassAccelerationMultiplier": "acceleration_multiplier",
                "ClassStaminaDrainMultiplier": "stamina_drain_multiplier",
            }[attribute_name]
            if "<Class>" not in pattern:
                fail(f"movement source pattern missing <Class>: {attribute_name}")
            if key not in class_values:
                fail(f"class {class_name} missing {key}")

    handling = sets["WeaponHandlingSet"]["attributes"]
    if set(handling) != {"SpreadMultiplier", "RecoilMultiplier", "SwayMultiplier"}:
        fail("weapon handling attributes must remain Spread/Recoil/Sway multipliers")
    if any(float(definition.get("initial", 0.0)) != 1.0 for definition in handling.values()):
        fail("weapon handling multipliers must initialize to 1.0")

    modifier_sources = sets["WeaponHandlingSet"].get("modifier_sources", [])
    if len(modifier_sources) < 3:
        fail("WeaponHandlingSet must preserve stance, stamina and bipod modifier sources")
    for source in modifier_sources:
        lookup(tuning, source)

    lyra = contracts.get("existing_lyra_contracts", {})
    if "reuse" not in lyra.get("health", "").lower():
        fail("health contract must reuse Lyra health")
    if "disabled" not in lyra.get("shield", "").lower():
        fail("shield must remain disabled for this gameplay mode")
    if "reuse" not in lyra.get("team", "").lower():
        fail("team contract must reuse Lyra team system")

    authority = contracts.get("authority_rules", {})
    required_true = [
        "server_owns_final_stamina",
        "server_owns_damage",
        "server_owns_hit_confirmation",
        "movement_prediction_must_use_character_network_prediction",
        "blueprint_velocity_hacks_forbidden",
    ]
    if any(authority.get(key) is not True for key in required_true):
        fail("attribute/network authority contract weakened")

    print(json.dumps({
        "attribute_sets": len(sets),
        "stamina_attributes": len(stamina),
        "movement_attributes": len(movement),
        "weapon_handling_attributes": len(handling),
        "status": "ok"
    }, sort_keys=True))


if __name__ == "__main__":
    main()
