import bpy, math, json
from pathlib import Path
from mathutils import Vector
SRC=Path(r"C:\Users\dezen\Desktop\135er-Spandau-Defeat\tools\blender_pipeline\builds\rathaus_spandau\SpandauStrike_Rathaus_WORLD_MASTER_v30_PRODUCTION_CLEAN.blend")
OUT=SRC.with_name('SpandauStrike_Rathaus_WORLD_MASTER_v31_FENESTRATION.blend'); REP=OUT.with_suffix('.json')
bpy.ops.wm.open_mainfile(filepath=str(SRC));sc=bpy.context.scene
A=math.radians(47.5);C=math.cos(A);S=math.sin(A)
def wxy(u,v):return (u*C-v*S,u*S+v*C)
def mat(name,color,rough=.55,metal=0):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal;return m
STONE=mat('M_V31_WindowStone',(0.60,0.55,0.47),.72); FRAME=mat('M_V31_WindowFrame',(0.72,0.69,0.62),.48); GLASS=mat('M_V31_WindowGlass',(0.055,0.11,0.13),.18,.05)
COL=bpy.data.collections.get('PRODUCTION_RATHAUS_V31_FENESTRATION') or bpy.data.collections.new('PRODUCTION_RATHAUS_V31_FENESTRATION')
if COL.name not in sc.collection.children:sc.collection.children.link(COL)
# Build one multi-material modular window mesh in local coordinates x=horizontal, y=depth(front-back), z=vertical.
def add_box(verts,faces,midx,cx,cy,cz,sx,sy,sz,mi):
 base=len(verts);x0,x1=cx-sx/2,cx+sx/2;y0,y1=cy-sy/2,cy+sy/2;z0,z1=cz-sz/2,cz+sz/2
 verts += [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
 fs=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
 for f in fs:faces.append(tuple(base+i for i in f));midx.append(mi)
verts=[];faces=[];mi=[]
# dimensions based on old measured 1.7 x 2.65 opening, made slightly taller/slender like reference.
W,H,D=1.75,2.85,.18
# recessed dark glass
add_box(verts,faces,mi,0,.055,0,W-0.34,.08,H-0.32,2)
# stone outer surround: 4 pieces
add_box(verts,faces,mi,-W/2+.09,0,0,.18,D,H,0);add_box(verts,faces,mi,W/2-.09,0,0,.18,D,H,0)
add_box(verts,faces,mi,0,0,H/2-.09,W-.18,D,.18,0);add_box(verts,faces,mi,0,0,-H/2+.09,W-.18,D,.18,0)
# wooden/light frame inset and cross mullions
add_box(verts,faces,mi,-.52,.07,0,.09,.09,H-.38,1);add_box(verts,faces,mi,.52,.07,0,.09,.09,H-.38,1)
add_box(verts,faces,mi,0,.07,0,.08,.09,H-.38,1);add_box(verts,faces,mi,0,.07,.28,W-.42,.09,.08,1)
# sill and subtle cap
add_box(verts,faces,mi,0,-.02,-H/2-.08,W+.34,.34,.16,0);add_box(verts,faces,mi,0,-.02,H/2+.07,W+.18,.27,.14,0)
mesh=bpy.data.meshes.new('MESH_V31_Window_Module');mesh.from_pydata(verts,[],faces);mesh.materials.append(STONE);mesh.materials.append(FRAME);mesh.materials.append(GLASS)
for idx,p in enumerate(mesh.polygons):p.material_index=mi[idx]
mesh.update()
def instance(name,u,v,z,tag='front_window'):
 x,y=wxy(u,v);o=bpy.data.objects.new(name,mesh);COL.objects.link(o);o.location=(x,y,z);o.rotation_euler[2]=A;o['ss_role']='landmark';o['ss_tag']='rathaus_v31_'+tag;o['ss_export']=True;return o
created=[]
# Symmetric main front wings: measured legacy raster, now rebuilt cleanly.
side_u=[-48,-43,-38,-33,-28,-23,-18,18,23,28,33,38,43,48]
levels=[4.2,8.4,12.6,16.8]
for z in levels:
 for u in side_u:created.append(instance(f'V31_FrontWindow_u{u}_z{z:.1f}',u,-27.94,z))
# Central five axes: keep the tall vertical recess language but add defined window frames at four levels.
central_u=[-8,-4,0,4,8]
central_levels=[5.0,9.2,13.4,17.6]
for z in central_levels:
 for u in central_u:created.append(instance(f'V31_CentralWindow_u{u}_z{z:.1f}',u,-34.47,z,'central_window'))
# Add vertical facade field pilasters between outer window groups, restrained to match reference rhythm.
def cube(name,u,v,z,su,sv,sz,material,tag):
 x,y=wxy(u,v);bpy.ops.mesh.primitive_cube_add(location=(x,y,z),rotation=(0,0,A));o=bpy.context.object;o.name=name;o.dimensions=(su,sv,sz);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 COL.objects.link(o);o.data.materials.append(material);o['ss_role']='landmark';o['ss_tag']='rathaus_v31_'+tag;o['ss_export']=True;return o
# major field pilasters roughly every 10m, avoiding central risalit.
for u in [-53,-43,-33,-23,23,33,43,53]:
 created.append(cube(f'V31_FacadePilaster_{u}',u,-28.05,10.65,.58,.42,19.2,STONE,'facade_pilaster'))
# continuous belt courses at floor divisions
for z in [2.2,6.35,10.55,14.75,19.0]:
 created.append(cube(f'V31_FacadeCourse_{z:.2f}',0,-28.1,z,111.2,.44,.20,STONE,'facade_course'))
sc['ss_master_version']='v31_FENESTRATION';sc['rathaus_detail_pass']='clean instanced facade fenestration + measured 5m/4.2m rhythm';sc['rathaus_reference_note']='front facade aligned to current/historical Rathaus Spandau photo references; legacy positions used only as measured raster'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT));REP.write_text(json.dumps({'source':str(SRC),'output':str(OUT),'created_count':len(created),'window_instances':len(side_u)*len(levels)+len(central_u)*len(central_levels),'shared_window_mesh':mesh.name,'side_u':side_u,'levels':levels,'central_u':central_u,'central_levels':central_levels},indent=2),encoding='utf-8');print('V31_READY',len(created),'windows',len(side_u)*len(levels)+len(central_u)*len(central_levels),str(OUT),flush=True)
