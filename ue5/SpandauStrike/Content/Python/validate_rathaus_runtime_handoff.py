import json
import os
import unreal


def log(message):
    unreal.log(f"[SPANDAU_RUNTIME_HANDOFF] {message}")


def fail(message):
    unreal.log_error(f"[SPANDAU_RUNTIME_HANDOFF] {message}")
    raise RuntimeError(message)


def project_path(*parts):
    return os.path.normpath(os.path.join(unreal.Paths.project_dir(), *parts))


def main():
    handoff_path = project_path("Design", "RathausSpandau", "runtime_gameplay_handoff_v48.json")
    report_path = os.path.join(unreal.Paths.project_saved_dir(), "Reports", "rathaus_runtime_handoff_validation.json")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    if not os.path.isfile(handoff_path):
        fail(f"handoff file missing: {handoff_path}")

    with open(handoff_path, "r", encoding="utf-8-sig") as handle:
        data = json.load(handle)

    if data.get("schema") != "SpandauStrike.RuntimeGameplayHandoff.v1":
        fail(f"unexpected schema: {data.get('schema')}")

    objectives = data.get("objectives", [])
    spawns = data.get("spawns", [])
    cover = data.get("cover", [])

    if len(objectives) != 5:
        fail(f"expected 5 objectives, got {len(objectives)}")
    if len(spawns) != 8:
        fail(f"expected 8 spawns, got {len(spawns)}")
    if len(cover) < 20:
        fail(f"expected at least 20 cover objects, got {len(cover)}")

    sequences = sorted(int(item.get("metadata", {}).get("ss_sequence", -1)) for item in objectives)
    if sequences != [1, 2, 3, 4, 5]:
        fail(f"objective sequence mismatch: {sequences}")

    center = next((item for item in objectives if int(item.get("metadata", {}).get("ss_sequence", -1)) == 3), None)
    if not center:
        fail("center objective missing")
    if center.get("metadata", {}).get("ss_zone") != "rathaus":
        fail("center objective is not tagged as Rathaus")
    if int(center.get("metadata", {}).get("ss_capture_players", 0)) != 2:
        fail("Rathaus objective must require two players")

    west = [item for item in spawns if item.get("metadata", {}).get("ss_team") == "west"]
    east = [item for item in spawns if item.get("metadata", {}).get("ss_team") == "east"]
    if len(west) != 4 or len(east) != 4:
        fail(f"spawn split must be 4/4, got west={len(west)} east={len(east)}")

    player_start_class = unreal.load_class(None, "/Script/LyraGame.LyraPlayerStart")
    class_checks = {
        "LyraPlayerStart": bool(player_start_class),
        "StaticMeshActor": bool(unreal.StaticMeshActor),
    }

    report = {
        "ok": all(class_checks.values()),
        "schema": data.get("schema"),
        "source_master_version": data.get("source_master_version"),
        "counts": {
            "objectives": len(objectives),
            "spawns": len(spawns),
            "cover": len(cover),
        },
        "class_checks": class_checks,
        "objective_order": [item.get("source_name") for item in sorted(objectives, key=lambda x: int(x.get("metadata", {}).get("ss_sequence", 0)))],
        "note": "Dry-run only. No map actors were created or modified.",
    }

    with open(report_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)

    log(json.dumps(report, ensure_ascii=False))
    if not report["ok"]:
        fail(f"runtime class validation failed; see {report_path}")

    return report


if __name__ == "__main__":
    main()
