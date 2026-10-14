import bpy, math, json
from pathlib import Path
from mathutils import Vector
SRC=Path(r"C:\Users\dezen\Desktop\135er-Spandau-Defeat\tools\blender_pipeline\builds\rathaus_spandau\SpandauStrike_Rathaus_WORLD_MASTER_v16_ARCH_DETAIL.blend")
OUT=SRC.with_name('SpandauStrike_Rathaus_WORLD_MASTER_v17_GAMEPLAY_TAGGED.blend')
REP=OUT.with_suffix('.json')
bpy.ops.wm.open_mainfile(filepath=str(SRC))
sc=bpy.context.scene
AX=math.radians(47.5); CA,SA=math.cos(AX),math.sin(AX)
def xy(u,v,z=2.0): return Vector((u*CA-v*SA,u*SA+v*CA,z))
COL=bpy.data.collections.get('GAMEPLAY_PLANNING_V17') or bpy.data.collections.new('GAMEPLAY_PLANNING_V17')
if COL.name not in sc.collection.children: sc.collection.children.link(COL)
# existing spawn sets; use world-space translation
west=[]; east=[]
for o in sc.objects:
    n=o.name.upper()
    if n.startswith('SM_SPAWN_WEST_') and 'RING' not in n: west.append(o.matrix_world.translation.copy())
    if n.startswith('SM_SPAWN_EAST_') and 'RING' not in n: east.append(o.matrix_world.translation.copy())
def centroid(arr):
    if not arr: return Vector((0,0,2))
    return sum(arr,Vector())/len(arr)
W=centroid(west); E=centroid(east)
def empty(name,loc,tag,**props):
    o=bpy.data.objects.new(name,None); o.empty_display_type='SPHERE'; o.empty_display_size=3.0; o.location=loc; COL.objects.link(o)
    o['ss_role']='gameplay_planning'; o['ss_tag']=tag; o['ss_export']=False
    for k,v in props.items(): o[k]=v
    return o
def route(name,points,lane):
    cu=bpy.data.curves.new(name+'_Curve','CURVE'); cu.dimensions='3D'; cu.bevel_depth=.35; cu.bevel_resolution=2
    spl=cu.splines.new('POLY'); spl.points.add(len(points)-1)
    for p,co in zip(spl.points,points): p.co=(*co,1)
    o=bpy.data.objects.new(name,cu); COL.objects.link(o); o['ss_role']='gameplay_planning'; o['ss_tag']='route'; o['lane']=lane; o['ss_export']=False
    return o
# Main three-lane planning routes around Rathaus. These are planning aids only, not final navigation.
routes={
 'NORTH_REAR':[W,xy(-150,75),xy(0,95),xy(150,75),E],
 'CENTER_RATHAUS':[W,xy(-120,-20),xy(0,-48),xy(120,-20),E],
 'SOUTH_PLAZA':[W,xy(-150,-120),xy(0,-155),xy(150,-120),E],
}
for lane,pts in routes.items(): route('ROUTE_'+lane,pts,lane)
# Choke candidates anchored to recognizable map geometry.
chokes=[
 ('CHOKE_RATHAUS_FRONT',xy(0,-66,2.0),'front plaza / main entrance'),
 ('CHOKE_RATHAUS_WEST',xy(-68,-35,2.0),'west facade corner'),
 ('CHOKE_RATHAUS_EAST',xy(68,-35,2.0),'east facade corner'),
 ('CHOKE_RATHAUS_REAR',xy(0,58,2.0),'rear courtyard approach'),
]
for name,loc,desc in chokes: empty(name,loc,'chokepoint_candidate',description=desc,radius_m=12.0)
# Cover candidate zones: deliberately metadata-only, to be validated against sightlines before props are placed.
cover_pts=[(-45,-82),(-20,-100),(20,-100),(45,-82),(-80,-25),(80,-25),(-45,45),(45,45)]
for i,(u,v) in enumerate(cover_pts): empty(f'COVER_ZONE_{i:02d}',xy(u,v,1.5),'cover_candidate',cover_height_class='mixed',radius_m=8.0)
# Observation / sniper-risk markers on long plaza sightlines.
for i,(u,v) in enumerate(((-105,-125),(105,-125),(0,115))): empty(f'SIGHTLINE_RISK_{i:02d}',xy(u,v,4.0),'sightline_risk',radius_m=20.0)
# Keep existing spawn objects but enrich semantics rather than moving them.
for o in sc.objects:
    n=o.name.upper()
    if n.startswith('SM_SPAWN_WEST_'):
        o['team_hint']='WEST'; o['spawn_group']='WEST'; o['ss_tag']='spawn'
    elif n.startswith('SM_SPAWN_EAST_'):
        o['team_hint']='EAST'; o['spawn_group']='EAST'; o['ss_tag']='spawn'
sc['ss_master_version']='v17_GAMEPLAY_TAGGED'
sc['gameplay_planning_note']='Routes/chokes/cover zones are planning metadata; validate in UE before final placement.'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
report={'source':str(SRC),'output':str(OUT),'west_spawn_count':len(west),'east_spawn_count':len(east),'west_centroid_m':[round(x,2) for x in W],'east_centroid_m':[round(x,2) for x in E],'routes':{k:[[round(float(x),2) for x in p] for p in v] for k,v in routes.items()},'chokes':len(chokes),'cover_candidates':len(cover_pts),'sightline_risks':3,'planning_collection':COL.name}
REP.write_text(json.dumps(report,indent=2),encoding='utf-8')
print('V17_READY',json.dumps(report))

