import bpy, math
from pathlib import Path
from mathutils import Vector
OBJ=Path(r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\Saved\GIS\RathausSpandau_v1\Berlin3D_2025_3779_58218_-002\Mesh_3779_58218_-002.obj")
OUT=Path(r"C:\Users\dezen\Documents\Codex\lyra-ue5-gis-worktree\tools\blender_pipeline\rathaus_final\RathausSpandau_Berlin3D_top.png")
OX=377956.8271307037; OY=5822062.184676066
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=str(OBJ))
for o in bpy.context.selected_objects:
    if o.type=='MESH': o.rotation_euler=(0,0,0)
sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE_NEXT';sc.render.resolution_x=1200;sc.render.resolution_y=1200;sc.render.resolution_percentage=100
w=bpy.data.worlds.new('World');sc.world=w;w.use_nodes=True;w.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
bpy.ops.object.camera_add(location=(OX,OY,350))
cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=240;cam.rotation_euler=(Vector((OX,OY,30))-cam.location).to_track_quat('-Z','Y').to_euler();sc.camera=cam
bpy.ops.object.light_add(type='SUN',location=(OX,OY,300));sun=bpy.context.object;sun.data.energy=2.2;sun.rotation_euler=(math.radians(40),0,math.radians(135))
sc.render.filepath=str(OUT);bpy.ops.render.render(write_still=True);print('TOP_READY',OUT)
