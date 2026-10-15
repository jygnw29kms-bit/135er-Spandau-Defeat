#!/usr/bin/env python3
import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "tools" / "blender_pipeline" / "builds" / "rathaus_spandau" / "SpandauStrike_Rathaus_WORLD_MASTER_v46_RETIRE_LEGACY_TOWER_ROOF_EXPORT_MANIFEST.json"
DEFAULT_OUT = ROOT / "ue5" / "SpandauStrike" / "Design" / "RathausSpandau" / "runtime_gameplay_handoff_v46.json"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def require(condition: bool, message: str):
    if not condition:
        raise SystemExit("VALIDATION ERROR: " + message)


def vec_cm(values):
    return [round(float(value) * 100.0, 4) for value in values]


def deg(values):
    return [round(math.degrees(float(value)), 4) for value in values]


def pack_actor(obj, actor_type, gameplay_tags):
    return {
        "source_name": obj["name"],
        "actor_type": actor_type,
        "gameplay_tags": gameplay_tags,
        "transform": {
            "location_m": [round(float(value), 6) for value in obj.get("location_m", [0, 0, 0])],
            "location_cm": vec_cm(obj.get("location_m", [0, 0, 0])),
            "rotation_deg_xyz": deg(obj.get("rotation_rad_xyz", [0, 0, 0])),
            "scale_xyz": [round(float(value), 6) for value in obj.get("scale_xyz", [1, 1, 1])],
        },
        "metadata": obj.get("metadata", {}),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Validate Blender gameplay metadata and generate the UE5 gameplay handoff JSON."
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    data = load_json(args.manifest)
    gameplay = data.get("gameplay", [])
    objectives = [obj for obj in gameplay if obj.get("tag") == "territorial_objective" and obj.get("export")]
    spawns = [obj for obj in gameplay if obj.get("tag") == "spawn" and obj.get("export")]
    covers = [obj for obj in gameplay if obj.get("tag") == "cover" and obj.get("export")]

    require(len(objectives) == 5, f"expected 5 runtime objectives, got {len(objectives)}")
    sequences = sorted(int(obj.get("metadata", {}).get("ss_sequence", -1)) for obj in objectives)
    require(sequences == [1, 2, 3, 4, 5], f"objective sequence must be 1..5, got {sequences}")
    require(all(obj.get("metadata", {}).get("ss_runtime") is True for obj in objectives), "all objectives must be runtime=true")

    center = next(obj for obj in objectives if int(obj["metadata"]["ss_sequence"]) == 3)
    require(int(center["metadata"].get("ss_capture_players", 0)) == 2, "center objective must require 2 players")
    require(center["metadata"].get("ss_zone") == "rathaus", "center objective must be the Rathaus objective")
    require(all(obj["metadata"].get("ss_backcap_allowed") is False for obj in objectives), "backcap must be disabled on all objectives")

    require(len(spawns) == 8, f"expected 8 runtime team spawns, got {len(spawns)}")
    teams = {obj.get("metadata", {}).get("ss_team") for obj in spawns}
    require(teams == {"west", "east"}, f"expected west/east spawn teams, got {sorted(teams)}")
    require(len(covers) >= 20, f"expected at least 20 runtime cover objects, got {len(covers)}")

    objectives_sorted = sorted(objectives, key=lambda obj: int(obj["metadata"]["ss_sequence"]))
    source_path = args.manifest.resolve()
    try:
        source_manifest = source_path.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        source_manifest = args.manifest.name

    payload = {
        "schema": "SpandauStrike.RuntimeGameplayHandoff.v1",
        "source_manifest": source_manifest,
        "source_master_version": data.get("master_version"),
        "coordinate_policy": "Blender world coordinates are authoritative; location_cm is meters*100. Axis/handedness conversion remains importer-owned.",
        "rules": {
            "mode": "linear_territorial",
            "objective_count": 5,
            "center_capture_players": 2,
            "contested_behavior": "pause",
            "backcap_allowed": False,
        },
        "objectives": [
            pack_actor(obj, "SpandauStrikeCapturePoint", ["SpandauStrike.Objective.Territorial"])
            for obj in objectives_sorted
        ],
        "spawns": [
            pack_actor(
                obj,
                "LyraPlayerStart",
                [
                    f"SpandauStrike.Spawn.Team.{obj['metadata']['ss_team'].title()}",
                    f"SpandauStrike.Lane.{obj['metadata']['ss_lane'].title()}",
                ],
            )
            for obj in spawns
        ],
        "cover": [
            pack_actor(
                obj,
                "StaticMeshActor",
                [
                    "SpandauStrike.Gameplay.Cover",
                    f"SpandauStrike.Cover.{str(obj.get('metadata', {}).get('ss_cover_class', 'Generic')).title()}",
                ],
            )
            for obj in covers
        ],
        "summary": {
            "objectives": len(objectives),
            "spawns": len(spawns),
            "cover_objects": len(covers),
        },
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], sort_keys=True))
    print(args.out)


if __name__ == "__main__":
    main()
