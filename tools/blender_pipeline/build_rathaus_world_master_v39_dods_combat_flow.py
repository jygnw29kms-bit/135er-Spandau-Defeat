import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SRC=Path(r"C:\Users\dezen\Desktop\135er-Spandau-Defeat\tools\blender_pipeline\builds\rathaus_spandau\SpandauStrike_Rathaus_WORLD_MASTER_v38_TERRITORIAL_FLOW.blend")
OUT=SRC.with_name('SpandauStrike_Rathaus_WORLD_MASTER_v39_DODS_COMBAT_FLOW.blend');REP=OUT.with_suffix('.json')
bpy.ops.wm.open_mainfile(filepath=str(SRC));sc=bpy.context.scene
COL=bpy.data.collections.get('GAMEPLAY_COMBAT_V39') or bpy.data.collections.new('GAMEPLAY_COMBAT_V39')
if COL.name not in sc.collection.children:sc.collection.children.link(COL)
# retire legacy 2-objective prototype
ret=[]
for n in ['SM_OBJECTIVE_A','SM_OBJECTIVE_B']:
 o=bpy.data.objects.get(n)
 if o:
  o['ss_role']='reference';o['ss_tag']='legacy_objective';o['ss_export']=False;o['ss_runtime']=False;o['ss_replaced_by']='FLAG_1..FLAG_5_v38';ret.append(n)
# terrain BVH
terr=bpy.data.objects['SM_Rathaus_DGM1_1000m_v21']
def tree(o):
 deps=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(deps);me=ev.to_mesh();vs=[o.matrix_world@v.co for v in me.vertices];ps=[p.vertices[:] for p in me.polygons];t=BVHTree.FromPolygons(vs,ps,all_triangles=False);ev.to_mesh_clear();return t
T=tree(terr)
def z(x,y):
 h=T.ray_cast(Vector((x,y,100)),Vector((0,0,-1)),200);return h[0].z if h[0] else 0
# helper planning marker
def material(name,color):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.diffuse_color=(*color,1);return m
M_MG=material('M_GP_MG',(0.85,.2,.12));M_SN=material('M_GP_SNIPER',(.45,.2,.8));M_SM=material('M_GP_SMOKE',(.65,.65,.65));M_FL=material('M_GP_FLANK',(.1,.75,.35))
def marker(name,x,y,kind,mat,rad=2.2,**meta):
 bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=rad,depth=.18,location=(x,y,z(x,y)+.12));o=bpy.context.object;o.name=name
 for c in list(o.users_collection):c.objects.unlink(o)
 COL.objects.link(o);o.data.materials.append(mat);o['ss_role']='gameplay_planning';o['ss_tag']=kind;o['ss_export']=False;o['ss_runtime']=False
 for k,v in meta.items():o[k]=v
 return o
made=[]
# Chokes: each gets smoke counterplay + one flank target near alternate lane
chokes={
 'FRONT':((48.66,-44.59),'mid',(75,-90)),
 'WEST':((-20.14,-73.78),'south',(-65,-110)),
 'EAST':((71.74,26.49),'mid',(110,65)),
 'REAR':((-42.76,39.18),'north',(-80,95))}
for n,(p,lane,fl) in chokes.items():
 o=marker(f'SMOKE_{n}',p[0],p[1],'smoke_anchor',M_SM,2.8,ss_lane=lane,ss_counter='smoke',ss_choke=n.lower());made.append(o.name)
 o=marker(f'FLANK_{n}',fl[0],fl[1],'flank_anchor',M_FL,2.5,ss_lane=lane,ss_counter='flank',ss_choke=n.lower());made.append(o.name)
# sightline risks -> MG and sniper control candidates, never hard-safe: pair with flank/smoke counters
risks=[('00',(21.22,-161.86),'south'),('01',(163.10,-7.03),'mid'),('02',(-84.79,77.69),'north')]
for rid,p,lane in risks:
 o=marker(f'MG_NEST_{rid}',p[0],p[1],'mg_candidate',M_MG,2.4,ss_lane=lane,ss_weapon_role='MG',ss_requires_bipod=True,ss_counterplay='smoke+flank',ss_arc_degrees=70);made.append(o.name)
 # offset sniper candidate ~18m back/side to avoid exact overlap
 sx=p[0]-18 if p[0]>0 else p[0]+18; sy=p[1]+14
 o=marker(f'SNIPER_POS_{rid}',sx,sy,'sniper_candidate',M_SN,2.0,ss_lane=lane,ss_weapon_role='Sniper',ss_counterplay='smoke+alternate_lane',ss_exposed=True);made.append(o.name)
# tag 5 flags with DoD:S capture semantics
for o in sc.objects:
 if o.name.startswith('FLAG_'):
  o['ss_capture_rule']='contested_stops_progress';o['ss_capture_decay']='hold_then_slow_decay';o['ss_frontline_mode']='linear_adjacent';o['ss_backcap_allowed']=False
# spawn metadata: current edge spawns are initial/home wave anchors, not arbitrary front spawns
for o in sc.objects:
 if o.name.startswith('SM_SPAWN_WEST_') and 'RING' not in o.name:
  o['ss_spawn_role']='team_anchor';o['ss_frontline_side']='west';o['ss_spawn_safety']='los_distance_check'
 if o.name.startswith('SM_SPAWN_EAST_') and 'RING' not in o.name:
  o['ss_spawn_role']='team_anchor';o['ss_frontline_side']='east';o['ss_spawn_safety']='los_distance_check'
sc['ss_master_version']='v39_DODS_COMBAT_FLOW';sc['ss_combat_design']='DoD:S lane control: MG/sniper power positions always paired with smoke/flank counterplay; legacy A/B retired';sc['ss_runtime_objectives']=5
bpy.ops.wm.save_as_mainfile(filepath=str(OUT));REP.write_text(json.dumps({'source':str(SRC),'output':str(OUT),'retired':ret,'created':made,'rules':{'flags':5,'center_players':2,'contested':'stop','backcap':False,'mg_counterplay':'smoke+flank'}},indent=2),encoding='utf-8');print('V39_READY',len(made),'retired',ret,flush=True)
