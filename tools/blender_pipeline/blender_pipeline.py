import bpy
import os
import sys
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CFG = ROOT / "config.json"

def load_cfg():
    with CFG.open("r", encoding="utf-8") as f:
        return json.load(f)

def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)

def import_asset(path: Path):
    ext = path.suffix.lower()
    if ext == ".obj":
        bpy.ops.wm.obj_import(filepath=str(path))
    elif ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=str(path))
    else:
        raise RuntimeError(f"Unsupported input: {path}")
def mesh_objects():
    return [o for o in bpy.context.scene.objects if o.type == "MESH"]

def apply_transforms():
    for o in mesh_objects():
        bpy.context.view_layer.objects.active = o
        o.select_set(True)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        o.select_set(False)

def move_to_local_origin():
    objs = mesh_objects()
    if not objs:
        return
    minx=min(v.co.x+o.location.x for o in objs for v in o.data.vertices)
    miny=min(v.co.y+o.location.y for o in objs for v in o.data.vertices)
    minz=min(v.co.z+o.location.z for o in objs for v in o.data.vertices)
    maxx=max(v.co.x+o.location.x for o in objs for v in o.data.vertices)
    maxy=max(v.co.y+o.location.y for o in objs for v in o.data.vertices)
    cx=(minx+maxx)/2.0
    cy=(miny+maxy)/2.0
    for o in objs:
        o.location.x -= cx
        o.location.y -= cy
        o.location.z -= minz

def clean_meshes():
    for o in mesh_objects():
        bpy.context.view_layer.objects.active=o
        o.select_set(True)
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.remove_doubles(threshold=0.001)
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode="OBJECT")
        o.select_set(False)

def duplicate_lod(src, name, ratio):
    lod=src.copy()
    lod.data=src.data.copy()
    lod.name=name
    bpy.context.collection.objects.link(lod)
    bpy.context.view_layer.objects.active=lod
    mod=lod.modifiers.new("Decimate","DECIMATE")
    mod.ratio=ratio
    bpy.ops.object.modifier_apply(modifier=mod.name)
    return lod

def make_collision(src):
    col=src.copy()
    col.data=src.data.copy()
    col.name="UCX_"+src.name
    bpy.context.collection.objects.link(col)
    bpy.context.view_layer.objects.active=col
    mod=col.modifiers.new("CollisionHull","DECIMATE")
    mod.ratio=0.08
    bpy.ops.object.modifier_apply(modifier=mod.name)
    return col

def build_lods(cfg):
    originals=[o for o in mesh_objects() if not o.name.startswith(("LOD","UCX_"))]
    for src in originals:
        src.name = src.name.replace(" ","_")
        for i,ratio in enumerate(cfg["lod_ratios"][1:], start=1):
            duplicate_lod(src, f"{src.name}_LOD{i}", ratio)
        make_collision(src)

def select_for_export(prefix=None):
    bpy.ops.object.select_all(action="DESELECT")
    for o in mesh_objects():
        if prefix is None or o.name.startswith(prefix):
            o.select_set(True)

def export_fbx(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.fbx(
        filepath=str(path), use_selection=True,
        apply_unit_scale=True, bake_space_transform=False,
        object_types={'MESH'}, add_leaf_bones=False,
        mesh_smooth_type='FACE', axis_forward='-Z', axis_up='Y'
    )

def save_master(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(path))

def run(input_path: Path):
    cfg=load_cfg()
    clear_scene()
    import_asset(input_path)
    apply_transforms()
    move_to_local_origin()
    clean_meshes()
    build_lods(cfg)
    stem=input_path.stem.replace(" ","_")
    save_master(ROOT/"output"/"master"/f"{stem}_master.blend")
    select_for_export()
    export_fbx(ROOT/"output"/"ue5"/f"{stem}_UE5.fbx")
    select_for_export()
    export_fbx(ROOT/"output"/"source2"/f"{stem}_SOURCE2.fbx")
    print(f"PIPELINE_OK::{stem}")

if __name__ == "__main__":
    args=sys.argv
    src=None
    if "--" in args:
        extra=args[args.index("--")+1:]
        if extra:
            src=Path(extra[0])
    if src is None:
        cfg=load_cfg()
        candidates=[]
        for ext in ("*.obj","*.fbx"):
            candidates.extend((ROOT/"input").glob(ext))
        if not candidates:
            raise SystemExit("No OBJ/FBX found in input")
        src=candidates[0]
    run(src.resolve())
