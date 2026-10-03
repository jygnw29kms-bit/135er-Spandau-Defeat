import bpy, json
from pathlib import Path

ROOT=Path(r"C:\Users\dezen\Documents\Codex\lyra-ue5-gis-worktree\tools\blender_pipeline\rathaus_final")
BLEND=ROOT/"SpandauStrike_Rathaus_FULLMAP_v2.blend"
OUT=ROOT/"fullmap_engine"
OUT.mkdir(exist_ok=True)

bpy.ops.wm.open_mainfile(filepath=str(BLEND))
sc=bpy.context.scene

def select_objects(objs):
    bpy.ops.object.select_all(action='DESELECT')
    valid=[]
    for o in objs:
        if o.type in {'MESH','CURVE','FONT'}:
            o.hide_viewport=False
            o.select_set(True)
            valid.append(o)
    if valid:
        bpy.context.view_layer.objects.active=valid[0]
    return valid

# Visible render/game geometry excludes collision + gameplay markers.
visible=[]
for o in sc.objects:
    if o.type not in {'MESH','CURVE','FONT'}: continue
    if o.hide_render: continue
    if o.name.startswith(('COL_','NAV_BLOCK_','SPAWN_','OBJECTIVE_','V8_A','V8_B','GAME_A','GAME_B')): continue
    visible.append(o)

select_objects(visible)
bpy.ops.export_scene.fbx(
    filepath=str(OUT/"SpandauStrike_Rathaus_FULLMAP_Visible.fbx"),
    use_selection=True,
    apply_scale_options='FBX_SCALE_ALL',
    axis_forward='-Y',
    axis_up='Z'
)
bpy.ops.wm.obj_export(
    filepath=str(OUT/"SpandauStrike_Rathaus_FULLMAP_Visible.obj"),
    export_selected_objects=True,
    forward_axis='NEGATIVE_Z',
    up_axis='Y',
    export_materials=True
)

# Collision objects.
collision=[o for o in sc.objects if o.type=='MESH' and (o.name.startswith('COL_') or o.name.startswith('MAPBOUND_') or o.name.startswith('NAV_BLOCK_'))]
for i,o in enumerate(collision):
    o.name=f"UCX_Spandau_FULLMAP_{i:03d}"
select_objects(collision)
if collision:
    bpy.ops.export_scene.fbx(
        filepath=str(OUT/"SpandauStrike_Rathaus_FULLMAP_Collision.fbx"),
        use_selection=True,
        apply_scale_options='FBX_SCALE_ALL',
        axis_forward='-Y',
        axis_up='Z'
    )
    bpy.ops.wm.obj_export(
        filepath=str(OUT/"SpandauStrike_Rathaus_FULLMAP_Collision.obj"),
        export_selected_objects=True,
        forward_axis='NEGATIVE_Z',
        up_axis='Y',
        export_materials=False
    )

# Gameplay marker package.
gameplay=[]
for o in sc.objects:
    if o.type in {'MESH','CURVE','FONT'} and (
        o.name.startswith(('SPAWN_','OBJECTIVE_','V8_A','V8_B','GAME_A','GAME_B'))
    ):
        gameplay.append(o)
select_objects(gameplay)
if gameplay:
    bpy.ops.export_scene.fbx(
        filepath=str(OUT/"SpandauStrike_Rathaus_FULLMAP_GameplayMarkers.fbx"),
        use_selection=True,
        apply_scale_options='FBX_SCALE_ALL',
        axis_forward='-Y',
        axis_up='Z'
    )

stats={
    "source":BLEND.name,
    "visible_objects":len(visible),
    "collision_objects":len(collision),
    "gameplay_objects":len(gameplay),
    "outputs":[p.name for p in OUT.iterdir() if p.is_file()]
}
(OUT/"SpandauStrike_Rathaus_FULLMAP_Export.json").write_text(json.dumps(stats,indent=2),encoding='utf-8')
print(json.dumps(stats,indent=2))
print("EXPORT_READY",OUT)
