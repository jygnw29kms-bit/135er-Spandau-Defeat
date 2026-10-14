#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "ue5" / "SpandauStrike" / "Design" / "Gameplay" / "gameplay_bundle_v1.json"
DEFAULT_OUT = ROOT / "ue5" / "SpandauStrike" / "Design" / "Generated" / "runtime_import_plan_v1.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def add_source(entries, role, rel):
    path = ROOT / rel
    if not path.is_file():
        raise SystemExit(f"missing import source: {rel}")
    entries.append({"role": role, "path": rel, "sha256": sha256(path), "size_bytes": path.stat().st_size})


def main():
    parser = argparse.ArgumentParser(description="Generate a fingerprinted Unreal import plan for the current gameplay bundle.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    bundle = load(BUNDLE)
    sources = []
    add_source(sources, "world_manifest", bundle["world_master"]["manifest"])
    for role, rel in sorted(bundle["gameplay_sources"].items()):
        add_source(sources, role, rel)

    plan = {
        "schema": "SpandauStrike.UEImportPlan.v1",
        "bundle_schema": bundle["schema"],
        "bundle_version": bundle["bundle_version"],
        "world_master_version": bundle["world_master"]["version"],
        "sources": sources,
        "preconditions": [
            "repository validators pass",
            "runtime handoff is regenerated from the current world manifest",
            "canonical gameplay tag snippet is generated from the current tag source",
            "UE dry-run handoff validation passes",
            "current Rathaus production map is not modified before dry-run validation"
        ],
        "ordered_steps": [
            {"order": 1, "action": "reconcile_local_git_state", "mutates_map": False},
            {"order": 2, "action": "validate_repository_scope_and_gameplay_bundle", "mutates_map": False},
            {"order": 3, "action": "generate_gameplay_tags_and_datatable_seeds", "mutates_map": False},
            {"order": 4, "action": "generate_runtime_gameplay_handoff", "mutates_map": False},
            {"order": 5, "action": "run_ue_runtime_handoff_dry_run", "mutates_map": False},
            {"order": 6, "action": "create_separate_rathaus_runtime_test_map", "mutates_map": True},
            {"order": 7, "action": "spawn_or_place_runtime_objectives_and_spawns_in_test_map", "mutates_map": True},
            {"order": 8, "action": "validate_capture_flow_spawn_safety_and_navigation", "mutates_map": True},
            {"order": 9, "action": "promote_only_after_visual_and_gameplay_acceptance", "mutates_map": True}
        ],
        "safety": {
            "overwrite_current_final_map": False,
            "use_separate_test_map_first": True,
            "axis_conversion_must_be_verified_in_ue": True,
            "blender_world_master_remains_spatial_authority": True
        }
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"sources": len(sources), "world_master": plan["world_master_version"], "status": "ok"}, sort_keys=True))
    print(args.out)


if __name__ == "__main__":
    main()
