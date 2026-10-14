import bpy, json, math
from pathlib import Path
from mathutils import Vector
SRC=Path(r"C:\Users\dezen\Desktop\135er-Spandau-Defeat\tools\blender_pipeline\builds\rathaus_spandau\SpandauStrike_Rathaus_WORLD_MASTER_v17_GAMEPLAY_TAGGED.blend")
DGM=Path(r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\SourceData\DGM1\rathaus_dgm_fullmap_1000m_513.obj")
META=DGM.with_suffix('.json')
OUT=SRC.with_name('SpandauStrike_Rathaus_WORLD_MASTER_v21_GEOFRAME.blend')
REP=OUT.with_suffix('.json')
# Current FULLMAP coordinate frame from build_spandau_full_map_v1.py
CX,CY=377931.576,5822067.058
OE,ON=377897.8969272321,5822086.91786854
BASELINE,GROUND=33.45,31.0
DX=CX-OE; DY=ON-CY; DZ=BASELINE-GROUND
bpy.ops.wm.open_mainfile(filepath=str(SRC)); sc=bpy.context.scene
# Capture source roads before deleting legacy objects.
oldroad=bpy.data.objects.get('SM_REAL_OSM_Roads')
if not oldroad: raise RuntimeError('SM_REAL_OSM_Roads missing')
road_materials=[m for m in oldroad.data.materials]
road_faces=[tuple(p.vertices) for p in oldroad.data.polygons]
# Raw road mesh coordinates are E-OE, N-ON, Z-BASELINE after scale application.
road_world=[]
for v in oldroad.data.vertices:
    c=v.co; road_world.append(Vector((float(c.x-DX),float(c.y+DY),float(c.z+DZ))))
# Remove legacy terrain/road objects from current production master; v17 in Git is recovery source.
for name in ('SM_REAL_DGM_Terrain','UCX_COL_FULLMAP_Terrain','SM_REAL_OSM_Roads'):
    o=bpy.data.objects.get(name)
    if o:
        me=o.data if o.type=='MESH' else None
        bpy.data.objects.remove(o,do_unlink=True)
        if me and me.users==0:bpy.data.meshes.remove(me)
# Production collections.
terr_col=bpy.data.collections.get('WORLD_TERRAIN_V21') or bpy.data.collections.new('WORLD_TERRAIN_V21')
road_col=bpy.data.collections.get('WORLD_ROADS_V21') or bpy.data.collections.new('WORLD_ROADS_V21')
for col in (terr_col,road_col):
    if col.name not in sc.collection.children:sc.collection.children.link(col)
# Import corrected high-res DGM. OBJ stores local X/Y/Z already in FULLMAP frame.
bpy.ops.wm.obj_import(filepath=str(DGM))
terrain=[o for o in bpy.context.selected_objects if o.type=='MESH'][0]
terrain.rotation_euler=(0,0,0);terrain.location=(0,0,0);terrain.scale=(1,1,1);bpy.context.view_layer.update()
terrain.name='SM_Rathaus_DGM1_1000m_v21';terrain.data.name='SM_Rathaus_DGM1_1000m_v21_Mesh'
for c in list(terrain.users_collection):c.objects.unlink(terrain)
terr_col.objects.link(terrain)
terrain['ss_role']='world';terrain['ss_tag']='terrain';terrain['ss_export']=True;terrain['source']='Berlin DGM1 513x513 / FULLMAP origin';terrain['grid_step_m']=1.953125
mat=bpy.data.materials.get('M_REAL_Ground') or bpy.data.materials.get('M_Ground')
if not mat:
    mat=bpy.data.materials.new('M_REAL_Ground');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(0.12,0.15,0.10,1);bs.inputs['Roughness'].default_value=.9
terrain.data.materials.clear();terrain.data.materials.append(mat)
for p in terrain.data.polygons:p.use_smooth=True
# Terrain collision 129x129 sampled from high-res source.
N=513;STRIDE=4;idxs=list(range(0,N,STRIDE));M=len(idxs)
verts=[tuple(terrain.data.vertices[j*N+i].co) for j in idxs for i in idxs]
faces=[]
for j in range(M-1):
    for i in range(M-1):
        a=j*M+i;b=a+1;c=a+M;d=c+1;faces.extend(((a,c,b),(b,c,d)))
me_col=bpy.data.meshes.new('UCX_Rathaus_DGM1_1000m_v21_Mesh');me_col.from_pydata(verts,[],faces);me_col.update();me_col.materials.append(mat)
terr_collision=bpy.data.objects.new('UCX_Rathaus_DGM1_1000m_v21',me_col);terr_col.objects.link(terr_collision);terr_collision['ss_role']='collision';terr_collision['ss_tag']='terrain_collision';terr_collision['ss_export']=True;terr_collision.display_type='WIRE';terr_collision.hide_render=True
# Bilinear terrain sampler in the same identity local/world frame.
HALF=500.;STEP=1000./(N-1);OFFSET=.03
def tz(x,y):
    if x<-HALF or x>HALF or y<-HALF or y>HALF:return None
    fx=(x+HALF)/STEP;fy=(y+HALF)/STEP;i0=int(math.floor(fx));j0=int(math.floor(fy));i1=min(N-1,i0+1);j1=min(N-1,j0+1);tx=fx-i0;ty=fy-j0
    def z(i,j):return float(terrain.data.vertices[j*N+i].co.z)
    return (z(i0,j0)*(1-tx)+z(i1,j0)*tx)*(1-ty)+(z(i0,j1)*(1-tx)+z(i1,j1)*tx)*ty
# Build normalized road mesh directly in FULLMAP world coordinates.
newverts=[];projected=outside=0
for w in road_world:
    z=tz(float(w.x),float(w.y))
    if z is None:newverts.append((w.x,w.y,w.z));outside+=1
    else:newverts.append((w.x,w.y,z+OFFSET));projected+=1
me_road=bpy.data.meshes.new('SM_Rathaus_ROADS_DGM_v21_Mesh');me_road.from_pydata(newverts,[],road_faces);me_road.update()
for m in road_materials:
    if m:me_road.materials.append(m)
road=bpy.data.objects.new('SM_Rathaus_ROADS_DGM_v21',me_road);road_col.objects.link(road);road['ss_role']='world';road['ss_tag']='road';road['ss_export']=True;road['source']='OSM roads normalized to FULLMAP frame and projected to DGM1';road['surface_offset_m']=OFFSET
# Scene provenance.
meta=json.loads(META.read_text(encoding='utf-8'))
sc['ss_master_version']='v21_GEOFRAME';sc['ss_engine']='UE5 only';sc['ss_policy']='Blender world master -> tagged modular UE5 export';sc['coordinate_frame']='EPSG25833 local origin CX/CY, Z relative 31m';sc['origin_e']=CX;sc['origin_n']=CY;sc['ground_reference_m']=GROUND;sc['terrain_grid']=513;sc['terrain_step_m']=meta['step_m'];sc['roads_projection']='all roads inside playable 1km projected to DGM +0.03m'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
rep={'source':str(SRC),'output':str(OUT),'coordinate_frame':{'origin_epsg25833':[CX,CY],'source_gis_origin':[OE,ON],'legacy_alignment_offset':[float(-DX),float(DY),float(DZ)],'ground_reference_m':GROUND},'terrain':{'name':terrain.name,'vertices':len(terrain.data.vertices),'polygons':len(terrain.data.polygons),'dimensions_m':[float(x) for x in terrain.dimensions]},'terrain_collision':{'name':terr_collision.name,'vertices':len(me_col.vertices),'polygons':len(me_col.polygons)},'roads':{'name':road.name,'vertices':len(me_road.vertices),'polygons':len(me_road.polygons),'projected_inside':projected,'outside_preserved':outside,'surface_offset_m':OFFSET}}
REP.write_text(json.dumps(rep,indent=2),encoding='utf-8');print('V21_READY',json.dumps(rep),flush=True)
