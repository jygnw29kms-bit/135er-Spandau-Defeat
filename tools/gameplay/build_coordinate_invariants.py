#!/usr/bin/env python3
import argparse
import itertools
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HANDOFF_GENERATOR = ROOT / "tools" / "gameplay" / "build_runtime_gameplay_handoff.py"
DEFAULT_OUT = ROOT / "ue5" / "SpandauStrike" / "Design" / "Generated" / "rathaus_coordinate_invariants_v1.json"


def distance3(a, b):
    return math.sqrt(sum((float(b[i]) - float(a[i])) ** 2 for i in range(3)))


def main():
    parser = argparse.ArgumentParser(description="Build axis-independent coordinate invariants for Rathaus UE import validation.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--handoff", type=Path)
    args = parser.parse_args()

    if args.handoff:
        handoff_path = args.handoff
    else:
        tmp = tempfile.NamedTemporaryFile(prefix="spandau_handoff_", suffix=".json", delete=False)
        tmp.close()
        handoff_path = Path(tmp.name)
        result = subprocess.run(
            [sys.executable, str(HANDOFF_GENERATOR), "--out", str(handoff_path)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode:
            raise SystemExit(result.stdout + "\n" + result.stderr)

    handoff = json.loads(handoff_path.read_text(encoding="utf-8-sig"))
    actors = handoff["objectives"] + handoff["spawns"]
    anchors = {
        actor["source_name"]: [round(float(v), 6) for v in actor["transform"]["location_m"]]
        for actor in actors
    }

    names = sorted(anchors)
    pairs = []
    for a, b in itertools.combinations(names, 2):
        pairs.append({
            "a": a,
            "b": b,
            "distance_m": round(distance3(anchors[a], anchors[b]), 6),
        })

    xs = [value[0] for value in anchors.values()]
    ys = [value[1] for value in anchors.values()]
    zs = [value[2] for value in anchors.values()]
    extents = {
        "x_span_m": round(max(xs) - min(xs), 6),
        "y_span_m": round(max(ys) - min(ys), 6),
        "z_span_m": round(max(zs) - min(zs), 6),
    }

    distances = [pair["distance_m"] for pair in pairs]
    payload = {
        "schema": "SpandauStrike.CoordinateInvariants.v1",
        "world_master_version": handoff.get("source_master_version"),
        "anchor_count": len(anchors),
        "pair_count": len(pairs),
        "anchors_source_m": anchors,
        "pairwise_distances": pairs,
        "source_extents": extents,
        "distance_signature": {
            "min_pair_m": round(min(distances), 6),
            "max_pair_m": round(max(distances), 6),
            "mean_pair_m": round(sum(distances) / len(distances), 6),
        },
        "validation_policy": {
            "distance_relative_tolerance": 0.005,
            "distance_absolute_tolerance_m": 0.25,
            "uniform_scale_expected": 1.0,
            "ue_centimeters_per_source_meter": 100.0,
            "rotation_translation_reflection_invariant": True,
            "axis_mapping_must_be_verified_separately": True,
        },
        "note": "Pairwise distances detect scale/frame corruption without assuming an Unreal axis mapping. Reflection can preserve distances and therefore requires a separate orientation check in UE."
    }

    if payload["anchor_count"] != 13:
        raise SystemExit(f"expected 13 objective/spawn anchors, got {payload['anchor_count']}")
    expected_pairs = payload["anchor_count"] * (payload["anchor_count"] - 1) // 2
    if payload["pair_count"] != expected_pairs:
        raise SystemExit("pair-count invariant failed")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "anchors": payload["anchor_count"],
        "pairs": payload["pair_count"],
        "max_pair_m": payload["distance_signature"]["max_pair_m"],
        "status": "ok"
    }, sort_keys=True))
    print(args.out)


if __name__ == "__main__":
    main()
