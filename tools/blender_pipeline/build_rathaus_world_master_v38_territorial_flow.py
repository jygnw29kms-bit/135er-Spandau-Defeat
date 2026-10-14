import bpy, json, math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SRC=Path(r"C:\Users\dezen\Desktop\135er-Spandau-Defeat\tools\blender_pipeline\builds\rathaus_spandau\SpandauStrike_Rathaus_WORLD_MASTER_v37_TOWER_TRANSITION.blend")
OUT=SRC.with_name('SpandauStrike_Rathaus_WORLD_MASTER_v38_TERRITORIAL_FLOW.blend'); REP=OUT.with_suffix('.json')
bpy.ops.wm.open_mainfile(filepath=str(SRC)); sc=bpy.context.scene
COL=bpy.data.collections.get('GAMEPLAY_TERRITORIAL_V38') or bpy.data.collections.new('GAMEPLAY_TERRITORIAL_V38')
if COL.name not in sc.collection.children: sc.collection.children.link(COL)
# terrain projection
terr=bpy.data.objects['SM_Rathaus_DGM1_1000m_v21']
def bvh_world(o):
 deps=bpy.context.evaluated_depsgraph_get(); ev=o.evaluated_get(deps); me=ev.to_mesh(); verts=[o.matrix_world@v.co for v in me.vertices]; polys=[p.vertices[:] for p in me.polygons]; t=BVHTree.FromPolygons(verts,polys,all_triangles=False); ev.to_mesh_clear(); return t
T=bvh_world(terr)
def z_at(x,y):
 h=T.ray_cast(Vector((x,y,100)),Vector((0,0,-1)),200); return h[0].z if h[0] else 0.0
# materials
def mat(name,color):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.diffuse_color=(*color,1); return m
MW=mat('M_GP_WEST',(0.12,0.30,0.70)); MM=mat('M_GP_MID',(0.75,0.68,0.10)); ME=mat('M_GP_EAST',(0.70,0.16,0.12)); MR=mat('M_GP_ROUTE',(0.20,0.80,0.80)); MX=mat('M_GP_CROSSLINK',(0.75,0.35,0.85))
def tag(o,role,tag,export=False,**meta):
 o['ss_role']=role;o['ss_tag']=tag;o['ss_export']=export
 for k,v in meta.items():o[k]=v
 return o
def move_to_col(o):
 for c in list(o.users_collection): c.objects.unlink(o)
 COL.objects.link(o); return o
# five linear objectives
flags=[
 ('FLAG_1_WEST_HOME',-275.0,0.0,1,'west','home'),
 ('FLAG_2_WEST_STREET',-145.0,-97.3,1,'west','street'),
 ('FLAG_3_RATHAUS',5.0,-68.0,2,'neutral','rathaus'),
 ('FLAG_4_EAST_STREET',130.0,73.7,1,'east','street'),
 ('FLAG_5_EAST_HOME',235.0,-10.0,1,'east','home')]
created=[]
for i,(name,x,y,req,side,zone) in enumerate(flags,1):
 z=z_at(x,y)+.04
 bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=6.0,depth=.12,location=(x,y,z))
 o=move_to_col(bpy.context.object);o.name=name;o.data.materials.append(MW if side=='west' else ME if side=='east' else MM)
 tag(o,'gameplay_planning','territorial_objective',False,ss_objective_id=str(i),ss_capture_players=req,ss_sequence=i,ss_linear=True,ss_zone=zone,ss_initial_side=side,ss_frontline=True,ss_runtime=False)
 created.append(o.name)
# Existing route splines become authoritative planning lanes
for n,lane in [('ROUTE_NORTH_REAR','north'),('ROUTE_CENTER_RATHAUS','mid'),('ROUTE_SOUTH_PLAZA','south')]:
 o=bpy.data.objects.get(n)
 if o:
  tag(o,'gameplay_planning','route',False,ss_lane=lane,ss_route_type='primary',ss_runtime=False,ss_flow='west_east')
# Crosslinks use known route vertices; keep simple polylines and terrain-project each point.
cross={
 'CROSSLINK_WEST':[(-156.63,-59.92),(-66.33,-101.99),(-12.87,-191.66)],
 'CROSSLINK_MID':[(-70.04,64.18),(35.39,-32.43),(114.28,-104.72)],
 'CROSSLINK_EAST':[(46.04,161.26),(95.82,74.96),(189.81,29.52)]}
def curve_obj(name,pts,material,tagname,**meta):
 cu=bpy.data.curves.new(name+'_Curve','CURVE');cu.dimensions='3D';cu.bevel_depth=.55;cu.bevel_resolution=2
 sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,(x,y) in zip(sp.points,pts): p.co=(x,y,z_at(x,y)+.35,1)
 o=bpy.data.objects.new(name,cu);COL.objects.link(o);cu.materials.append(material);tag(o,'gameplay_planning',tagname,False,ss_runtime=False,**meta);created.append(name);return o
for n,pts in cross.items():curve_obj(n,pts,MX,'crosslink',ss_route_type='crosslink',ss_flow='lane_switch')
# Choke candidates classify by lane/role
chokes={
 'CHOKE_RATHAUS_FRONT':('mid','hard'),
 'CHOKE_RATHAUS_WEST':('south','medium'),
 'CHOKE_RATHAUS_EAST':('mid','medium'),
 'CHOKE_RATHAUS_REAR':('north','medium')}
for n,(lane,severity) in chokes.items():
 o=bpy.data.objects.get(n)
 if o: tag(o,'gameplay_planning','chokepoint',False,ss_lane=lane,ss_choke_severity=severity,ss_runtime=False,ss_counterplay_required=True)
# sightline risks -> weapon-role planning
for n in ['SIGHTLINE_RISK_00','SIGHTLINE_RISK_01','SIGHTLINE_RISK_02']:
 o=bpy.data.objects.get(n)
 if o: tag(o,'gameplay_planning','sightline_risk',False,ss_runtime=False,ss_role_hint='mg_sniper',ss_counterplay='cover_smoke_flank')
# cover zones tag lane by location heuristics
for o in sc.objects:
 if o.name.startswith('COVER_ZONE_'):
  y=o.location.y; lane='north' if y>25 else 'south' if y<-45 else 'mid'
  tag(o,'gameplay_planning','cover_candidate',False,ss_lane=lane,ss_runtime=False,ss_cover_intent='dod_lane_break')
sc['ss_master_version']='v38_TERRITORIAL_FLOW';sc['ss_gameplay_basis']='Day of Defeat Source territorial control';sc['ss_territorial_flags']=5;sc['ss_primary_lanes']=3;sc['ss_crosslinks']=3;sc['ss_center_capture_players']=2;sc['ss_policy']='Blender world master -> DoD:S-like tagged territorial layout -> UE5 Lyra'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
REP.write_text(json.dumps({'source':str(SRC),'output':str(OUT),'flags':[{'name':n,'x':x,'y':y,'z':z_at(x,y),'required_players':r,'side':s,'zone':zn} for n,x,y,r,s,zn in flags],'crosslinks':cross,'created':created,'design':'5-flag linear frontline, 3 primary lanes, 3 crosslinks, central 2-player Rathaus capture'},indent=2),encoding='utf-8')
print('V38_READY',len(created),str(OUT),flush=True)
