import bpy, math
from pathlib import Path
from mathutils import Vector

OBJ=Path(r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS\RathausSpandau_v1\Berlin3D_2025_3775_58218_-002\Mesh_3775_58218_-002.obj")
OUT=Path(r"C:\Users\dezen\Documents\Codex\lyra-ue5-gis-worktree\tools\blender_pipeline\rathaus_final\Berlin3D_2025_tile_overview.png")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=str(OBJ),forward_axis='NEGATIVE_Z',up_axis='Y')
objs=[o for o in bpy.context.selected_objects if o.type=='MESH']
for o in objs:
    o.name='Berlin3D_2025_Mesh'

# world coordinates stay intact
sc=bpy.context.scene
sc.render.engine='BLENDER_EEVEE_NEXT'
sc.render.resolution_x=1200
sc.render.resolution_y=1200
sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'
world=bpy.data.worlds.new('World');sc.world=world;world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.2,0.22,0.25,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8

# top-down ortho over tile
cx=(377561.3797+377950.8885)/2
cy=(5821815.8428+5822201.0649)/2
bpy.ops.object.camera_add(location=(cx,cy,500))
cam=bpy.context.object
cam.data.type='ORTHO'
cam.data.ortho_scale=420
cam.rotation_euler=(0,0,0)
cam.rotation_euler=(Vector((cx,cy,35))-cam.location).to_track_quat('-Z','Y').to_euler()
sc.camera=cam

# daylight
bpy.ops.object.light_add(type='SUN',location=(cx,cy,300))
sun=bpy.context.object;sun.data.energy=2.2;sun.rotation_euler=(math.radians(35),0,math.radians(135))

sc.render.filepath=str(OUT)
bpy.ops.render.render(write_still=True)
print('OVERVIEW_READY',OUT)
