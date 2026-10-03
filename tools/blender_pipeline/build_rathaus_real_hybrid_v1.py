import bpy, bmesh, math
from pathlib import Path
from mathutils import Vector

OUT=Path(r"C:\Users\dezen\Documents\Codex\lyra-ue5-gis-worktree\tools\blender_pipeline\rathaus_final")
BLEND=OUT/"RathausSpandau_Real3D_GameMaster.blend"
NEW=OUT/"RathausSpandau_Real3D_Hybrid_Master.blend"
PNG=OUT/"RathausSpandau_Real3D_Hybrid_preview.png"

bpy.ops.wm.open_mainfile(filepath=str(BLEND))
sc=bpy.context.scene

raw=bpy.data.objects.get("RathausSpandau_REAL_2025")
opt=bpy.data.objects.get("RathausSpandau_REAL_2025_OPT")
if not raw or not opt: raise RuntimeError("real mesh missing")
raw.hide_render=True
opt.hide_render=False
opt.hide_set(False)

# hide gameplay/collision for visual validation
for cname in ("80_COLLISION","90_GAMEPLAY"):
    col=bpy.data.collections.get(cname)
    if col:
        col.hide_render=True
        for o in col.objects:o.hide_render=True

SUP=bpy.data.collections.get("70_SUPPORT")
if not SUP:
    SUP=bpy.data.collections.new("70_SUPPORT")
    sc.collection.children.link(SUP)

# duplicate actual crop as source for clean support
support=raw.copy()
support.data=raw.data.copy()
support.name="Rathaus_REAL_Support"
for cc in list(support.users_collection): cc.objects.unlink(support)
SUP.objects.link(support)
support.hide_render=False
support.hide_set(False)

# make coordinates local around Rathaus
bpy.context.view_layer.objects.active=support
support.select_set(True)
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)

# delete low ground faces + non-Rathaus spatial fringe.
# This retains walls/roofs but removes most roads/trees/context.
bm=bmesh.new();bm.from_mesh(support.data)
tod=[]
for f in bm.faces:
    c=f.calc_center_median()
    # main Rathaus crop around verified tower center
    outside=(c.x < -36 or c.x > 82 or c.y < -78 or c.y > 72)
    too_low=(c.z < 4.0)
    if outside or too_low: tod.append(f)
bmesh.ops.delete(bm,geom=tod,context='FACES')
bm.to_mesh(support.data);bm.free();support.data.update()

# Voxel remesh converts scan fragments to a coherent real-shape shell
support.data.remesh_voxel_size=0.85
support.data.remesh_voxel_adaptivity=0.12
bpy.context.view_layer.objects.active=support
bpy.ops.object.voxel_remesh()

# Separate disconnected scan islands; keep largest/highest building component(s)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.separate(type='LOOSE')
bpy.ops.object.mode_set(mode='OBJECT')

parts=[o for o in bpy.context.selected_objects if o.type=='MESH']
def score(o):
    # prefer large component with tall Rathaus tower
    zs=[(o.matrix_world@v.co).z for v in o.data.vertices]
    if not zs:return 0
    return len(o.data.vertices)*(1+max(zs)/120.0)
parts.sort(key=score,reverse=True)
keep=parts[:3]
for q in parts[3:]:
    bpy.data.objects.remove(q,do_unlink=True)
# join top components in case courtyard wings separated
bpy.ops.object.select_all(action='DESELECT')
for q in keep:
    q.select_set(True)
bpy.context.view_layer.objects.active=keep[0]
if len(keep)>1:bpy.ops.object.join()
support=bpy.context.object
support.name="Rathaus_REAL_Support"

# smooth geometry, decimate modestly
for p in support.data.polygons:p.use_smooth=True
dec=support.modifiers.new("SupportDecimate","DECIMATE")
dec.ratio=.55
dec.use_collapse_triangulate=True
bpy.context.view_layer.objects.active=support
bpy.ops.object.modifier_apply(modifier=dec.name)

# materials
def mat(name,col,rough):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*col,1)
    bs.inputs["Roughness"].default_value=rough
    return m
STONE=mat("M_REAL_Support_Stone",(0.34,0.29,0.23),.72)
ROOF=mat("M_REAL_Support_Roof",(0.34,0.055,0.026),.72)
COPPER=mat("M_REAL_Support_Copper",(0.07,0.28,0.22),.50)
support.data.materials.clear()
support.data.materials.append(STONE);support.data.materials.append(ROOF);support.data.materials.append(COPPER)

# assign by face normal/height: sloped roofs red, highest tower cap copper
for f in support.data.polygons:
    z=f.center.z
    if z>63 and f.normal.z>.28:f.material_index=2
    elif z>16 and f.normal.z>.35:f.material_index=1
    else:f.material_index=0

# tuck support slightly behind raw photogrammetry surface
support.scale=(.996,.996,.997)

# camera from actual Rathaus plaza side (west/southwest)
cam=bpy.data.objects.get("Rathaus_Real_Master_Camera")
cam.location=(-115,-48,24)
cam.data.lens=36
cam.rotation_euler=(Vector((4,2,34))-cam.location).to_track_quat('-Z','Y').to_euler()
sc.camera=cam

sun=bpy.data.objects.get("Sun")
if sun:
    sun.data.energy=3.4
    sun.rotation_euler=(math.radians(48),math.radians(-10),math.radians(-62))

sc.render.resolution_x=1600;sc.render.resolution_y=900;sc.render.resolution_percentage=100
sc.render.filepath=str(PNG)
bpy.ops.wm.save_as_mainfile(filepath=str(NEW))
bpy.ops.render.render(write_still=True)
print("HYBRID_READY",NEW)
print("SUPPORT_VERTS",len(support.data.vertices),"SUPPORT_POLYS",len(support.data.polygons))
print("PREVIEW",PNG)
