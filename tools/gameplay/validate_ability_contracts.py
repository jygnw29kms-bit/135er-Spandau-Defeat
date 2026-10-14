#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GAMEPLAY = ROOT / "ue5" / "SpandauStrike" / "Design" / "Gameplay"
TAGS = ROOT / "tools" / "gameplay" / "spandau_strike_gameplay_tags.json"
ABILITIES = GAMEPLAY / "ability_contracts_v1.json"
LOADOUTS = GAMEPLAY / "class_loadouts_v1.json"
WEAPONS = GAMEPLAY / "weapon_archetypes_v1.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def fail(message):
    raise SystemExit("VALIDATION ERROR: " + message)


def collect_project_tags(value, out):
    if isinstance(value, dict):
        for child in value.values():
            collect_project_tags(child, out)
    elif isinstance(value, list):
        for child in value:
            collect_project_tags(child, out)
    elif isinstance(value, str) and value.startswith("SpandauStrike."):
        out.add(value)


def main():
    canonical_tags = set(load(TAGS)["tags"])
    contracts = load(ABILITIES)["abilities"]
    loadouts = load(LOADOUTS)["classes"]
    archetypes = load(WEAPONS)["archetypes"]

    expected = {
        "Sprint", "Prone", "BipodDeploy", "BipodUndeploy", "BoltCycle",
        "Scope", "Grenade", "RocketReload", "Capture"
    }
    if set(contracts) != expected:
        fail(f"ability contract set mismatch: {sorted(contracts)}")

    referenced_tags = set()
    collect_project_tags(contracts, referenced_tags)
    missing_tags = sorted(referenced_tags - canonical_tags)
    if missing_tags:
        fail("ability contracts reference non-canonical tags: " + ", ".join(missing_tags))

    for class_name, loadout in loadouts.items():
        for ability_id in loadout.get("ability_focus", []):
            if ability_id not in contracts:
                fail(f"class {class_name} references unknown ability contract: {ability_id}")

    for ability_id, contract in contracts.items():
        expected_tag = f"SpandauStrike.Ability.{ability_id}"
        if contract.get("ability_tag") != expected_tag:
            fail(f"ability {ability_id} tag mismatch: expected {expected_tag}")

        weapon = contract.get("requires_weapon_archetype")
        if weapon and weapon not in archetypes:
            fail(f"ability {ability_id} references unknown weapon archetype: {weapon}")
        for weapon in contract.get("valid_weapon_archetypes", []):
            if weapon not in archetypes:
                fail(f"ability {ability_id} references unknown valid weapon archetype: {weapon}")

    bipod = contracts["BipodDeploy"]
    if bipod.get("requires_weapon_archetype") != "HeavyMG":
        fail("BipodDeploy must remain tied to HeavyMG baseline")
    if len(bipod.get("surface_tags_any", [])) < 3:
        fail("BipodDeploy must support multiple explicit surface classes")
    if bipod.get("prone_ground_support_allowed") is not True:
        fail("BipodDeploy must support prone ground deployment")

    capture = contracts["Capture"]
    if capture.get("server_authoritative") is not True:
        fail("Capture must remain server authoritative")

    bolt = contracts["BoltCycle"]
    if set(bolt.get("valid_weapon_archetypes", [])) != {"BoltRifle", "ScopedRifle"}:
        fail("BoltCycle weapon set must be BoltRifle + ScopedRifle")
    if bolt.get("blocks_fire") is not True or bolt.get("blocks_reload") is not True:
        fail("BoltCycle must block fire and reload")

    print(json.dumps({
        "ability_contracts": len(contracts),
        "referenced_tags": len(referenced_tags),
        "class_loadouts": len(loadouts),
        "status": "ok"
    }, sort_keys=True))


if __name__ == "__main__":
    main()
