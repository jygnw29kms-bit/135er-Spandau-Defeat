"""Prepare downloaded Berlin 3D OBJ tiles for a Source 2 reference scene.

Run inside Blender's Python environment:
    blender --background --python tools/blender_prepare_berlin_mesh.py -- <site-id> <obj-dir>

The script imports every OBJ in <obj-dir>, groups them in a collection and
moves the combined selection to a local working origin while preserving a
record of the offset. It intentionally does not decimate or export final game
geometry: the dense Berlin mesh is a reference source, not a drop-in Source 2
asset.
"""

import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector

REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / "source2" / "geodata" / "school_sites.json"


def args_after_double_dash():
    if "--" not in sys.argv:
        return []
    return sys.argv[sys.argv.index("--") + 1:]


def import_obj(path: Path):
    before = set(bpy.data.objects)
    try:
        bpy.ops.wm.obj_import(filepath=str(path))
    except AttributeError:
        bpy.ops.import_scene.obj(filepath=str(path))
    return [o for o in bpy.data.objects if o not in before]


def main():
    args = args_after_double_dash()
    if len(args) != 2:
        raise SystemExit("Usage: <site-id> <obj-dir>")

    site_id, obj_dir = args
    obj_dir = Path(obj_dir).expanduser().resolve()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    site = next((s for s in manifest["sites"] if s["id"] == site_id), None)
    if not site:
        raise SystemExit(f"Unknown site id: {site_id}")

    objs = sorted(obj_dir.rglob("*.obj"))
    if not objs:
        raise SystemExit(f"No OBJ files found below {obj_dir}")

    collection = bpy.data.collections.new(f"BERLIN_REF_{site_id}")
    bpy.context.scene.collection.children.link(collection)

    imported = []
    for p in objs:
        new_objs = import_obj(p)
        imported.extend(new_objs)
        for o in new_objs:
            for c in list(o.users_collection):
                c.objects.unlink(o)
            collection.objects.link(o)

    mesh_objs = [o for o in imported if o.type == "MESH"]
    if not mesh_objs:
        raise SystemExit("OBJ files imported, but no mesh objects were created")

    mins = Vector((float("inf"),) * 3)
    maxs = Vector((float("-inf"),) * 3)
    for o in mesh_objs:
        for corner in o.bound_box:
            w = o.matrix_world @ Vector(corner)
            mins.x, mins.y, mins.z = min(mins.x, w.x), min(mins.y, w.y), min(mins.z, w.z)
            maxs.x, maxs.y, maxs.z = max(maxs.x, w.x), max(maxs.y, w.y), max(maxs.z, w.z)

    center_xy = Vector(((mins.x + maxs.x) / 2.0, (mins.y + maxs.y) / 2.0, 0.0))
    for o in imported:
        o.location -= center_xy

    metadata = {
        "site_id": site_id,
        "address": site["address"],
        "obj_files": [str(p) for p in objs],
        "source_bbox_before_localization": {
            "min": list(mins),
            "max": list(maxs)
        },
        "local_origin_offset": list(center_xy),
        "note": "Reference scene only. Rebuild/retopologize game geometry for Source 2."
    }

    out = obj_dir / f"{site_id}_import_metadata.json"
    out.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
