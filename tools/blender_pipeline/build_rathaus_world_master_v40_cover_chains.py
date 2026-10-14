import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SRC=Path(r"C:\Users\dezen\Desktop\135er-Spandau-Defeat\tools\blender_pipeline\builds\rathaus_spandau\SpandauStrike_Rathaus_WORLD_MASTER_v39_CLASSIC_COMBAT_FLOW.blend")
OUT=SRC.with_name('SpandauStrike_Rathaus_WORLD_MASTER_v40_COVER_CHAINS.blend');REP=OUT.with_suffix('.json')
bpy.ops.wm.open_mainfile(filepath=str(SRC));sc=bpy.context.scene
COL=bpy.data.collections.get('GAMEPLAY_COVER_V40') or bpy.data.collections.new('GAMEPLAY_COVER_V40')
if COL.name not in sc.collection.children:sc.collection.children.link(COL)
terr=bpy.data.objects['SM_Rathaus_DGM1_1000m_v21']
def tree(o):
 deps=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(deps);me=ev.to_mesh();vs=[o.matrix_world@v.co for v in me.vertices];ps=[p.vertices[:] for p in me.polygons];t=BVHTree.FromPolygons(vs,ps,all_triangles=False);ev.to_mesh_clear();return t
T=tree(terr)
def z(x,y):
 h=T.ray_cast(Vector((x,y,100)),Vector((0,0,-1)),200);return h[0].z if h[0] else 0
# selected clear candidates; sparse by design to preserve lethal open crossings
pts={
'north':[(-122.0,-10.3),(-23.6,103.0),(96.7,123.6),(198.2,48.2)],
'mid':[(-244.1,-53.9),(-184.9,-69.9),(-40.9,-84.6),(10.0,-49.8),(80.7,48.1),(172.3,39.3)],
'south':[(-281.9,-61.0),(-201.2,-100.2),(-120.5,-139.4),(-39.8,-178.6),(38.0,-156.9),(129.4,-77.9),(174.7,2.7)],
'cross':[(-88.9,-91.5),(-49.0,44.9),(83.4,96.5)]}
def mat(name,color):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.diffuse_color=(*color,1);return m
LOW=mat('M_GP_COVER_LOW',(.25,.55,.75));HIGH=mat('M_GP_COVER_HIGH',(.18,.35,.55))
created=[]
for lane,arr in pts.items():
 for i,(x,y) in enumerate(arr):
  cls='low' if i%2==0 else 'high'; h=.85 if cls=='low' else 1.45; w=2.8 if cls=='low' else 2.3; d=.55
  # orient roughly alternating 20 degrees to avoid arcade-grid look
  yaw=math.radians((i*23 + {'north':15,'mid':-10,'south':8,'cross':35}[lane])%70-35)
  bpy.ops.mesh.primitive_cube_add(location=(x,y,z(x,y)+h/2+.03),rotation=(0,0,yaw));o=bpy.context.object;o.name=f'V40_COVER_{lane.upper()}_{i:02d}';o.dimensions=(w,d,h);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
  for c in list(o.users_collection):c.objects.unlink(o)
  COL.objects.link(o);o.data.materials.append(LOW if cls=='low' else HIGH)
  o['ss_role']='gameplay_planning';o['ss_tag']='cover_blockout';o['ss_export']=False;o['ss_runtime']=False;o['ss_lane']=lane;o['ss_cover_class']=cls;o['ss_cover_intent']='classic_push_chain';o['ss_replace_with']='urban_real_asset';o['ss_preserve_open_crossings']=True
  created.append({'name':o.name,'lane':lane,'class':cls,'x':x,'y':y,'z':z(x,y)})
sc['ss_master_version']='v40_COVER_CHAINS';sc['ss_cover_design']='sparse 30-60m classic push cover; alternating low/high; retain lethal open crossings'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT));REP.write_text(json.dumps({'source':str(SRC),'output':str(OUT),'created':created,'count':len(created)},indent=2),encoding='utf-8');print('V40_READY',len(created),flush=True)

