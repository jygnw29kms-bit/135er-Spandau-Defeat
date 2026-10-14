import bpy, math, json
from pathlib import Path
SRC=Path(r"C:\Users\dezen\Desktop\135er-Spandau-Defeat\tools\blender_pipeline\builds\rathaus_spandau\SpandauStrike_Rathaus_WORLD_MASTER_v36_GAMEPLAY_CLEAN.blend")
OUT=SRC.with_name('SpandauStrike_Rathaus_WORLD_MASTER_v37_TOWER_TRANSITION.blend'); REP=OUT.with_suffix('.json')
bpy.ops.wm.open_mainfile(filepath=str(SRC)); sc=bpy.context.scene
A=math.radians(47.5); C=math.cos(A); S=math.sin(A)
def wxy(u,v): return (u*C-v*S,u*S+v*C)
def mat(name,color,rough=.55,metal=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
    return m
STONE=mat('M_V37_TowerStone',(0.55,0.49,0.40),.72); TRIM=mat('M_V37_TowerTrim',(0.68,0.61,0.50),.58); DARK=mat('M_V37_Opening',(0.026,0.03,0.032),.9); COPPER=mat('M_V37_Copper',(0.14,0.34,0.29),.4,.3)
COL=bpy.data.collections.get('PRODUCTION_RATHAUS_V37_TOWER') or bpy.data.collections.new('PRODUCTION_RATHAUS_V37_TOWER')
if COL.name not in sc.collection.children: sc.collection.children.link(COL)
def link(o):
    for c in list(o.users_collection): c.objects.unlink(o)
    COL.objects.link(o); return o
def tag(o,k): o['ss_role']='landmark';o['ss_tag']='rathaus_v37_'+k;o['ss_export']=True;return o
def box(name,u,v,z,su,sv,sz,ma,k='tower',bev=.04):
    x,y=wxy(u,v);bpy.ops.mesh.primitive_cube_add(location=(x,y,z),rotation=(0,0,A));o=bpy.context.object;o.name=name;o.dimensions=(su,sv,sz);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);link(o);o.data.materials.append(ma);tag(o,k)
    if bev: md=o.modifiers.new('EdgeBevel','BEVEL');md.width=bev;md.segments=2
    return o
def oct_prism(name,u,v,z0,z1,w,d,ch,ma,k='tower'):
    pts=[(-w/2+ch,-d/2),(w/2-ch,-d/2),(w/2,-d/2+ch),(w/2,d/2-ch),(w/2-ch,d/2),(-w/2+ch,d/2),(-w/2,d/2-ch),(-w/2,-d/2+ch)]
    vs=[]
    for z in (z0,z1):
        for du,dv in pts:
            x,y=wxy(u+du,v+dv);vs.append((x,y,z))
    n=8; fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    for i in range(n): j=(i+1)%n;fs.append((i,j,n+j,n+i))
    me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata(vs,[],fs);me.materials.append(ma);me.update();o=bpy.data.objects.new(name,me);COL.objects.link(o);tag(o,k);return o
ret=[]
# Retire v33 open crown and redundant upper transition profiles, but keep clocks and shaft windows.
for o in bpy.data.objects:
    n=o.name
    if n.startswith('V33_Crown') or n in ('V33_TowerCrownBase','V33_TowerFinial') or n in ('V24_TowerProfile_699','V24_TowerProfile_749','V25_TowerUpperCornice'):
        if o.get('ss_export',True):
            o.hide_viewport=True;o.hide_render=True;o['ss_export']=False;o['ss_role']='reference';o['ss_tag']='replaced_v37_tower_transition';ret.append(n)
created=[]
# Massive chamfered transition above the square shaft: closes the 66.5-70.2m visual gap.
created.append(oct_prism('V37_TowerTransitionCore',0,5,66.45,69.45,15.4,16.4,1.15,STONE,'tower_transition'))
created.append(box('V37_TowerTransitionLowerBand',0,5,66.72,16.1,17.1,.42,TRIM,'tower_transition',.05))
created.append(box('V37_TowerTransitionUpperBand',0,5,69.45,17.0,18.0,.52,TRIM,'tower_transition',.06))
# Open upper stage: four broad corner masses, creating four clear cardinal openings rather than 8 thin gazebo posts.
for iu,u in enumerate((-5.55,5.55)):
    for iv,v in enumerate((-.55,10.55)):
        created.append(box(f'V37_CrownCorner_{iu}_{iv}',u,v,74.0,2.15,2.15,8.5,STONE,'tower_crown',.10))
# deep dark opening planes behind each cardinal opening
created += [
    box('V37_CrownOpeningFront',0,-1.68,74.0,8.8,.16,6.9,DARK,'tower_crown',.01),
    box('V37_CrownOpeningRear',0,11.68,74.0,8.8,.16,6.9,DARK,'tower_crown',.01),
    box('V37_CrownOpeningWest',-7.18,5,74.0,.16,8.8,6.9,DARK,'tower_crown',.01),
    box('V37_CrownOpeningEast',7.18,5,74.0,.16,8.8,6.9,DARK,'tower_crown',.01)
]
# base and upper ring frame the open stage
created.append(box('V37_CrownBase',0,5,69.95,17.1,18.1,.72,TRIM,'tower_crown',.07))
created.append(box('V37_CrownTopBand',0,5,78.25,16.4,17.4,.55,TRIM,'tower_crown',.06))
# low chamfered copper roof
x,y=wxy(0,5);bpy.ops.mesh.primitive_cone_add(vertices=8,radius1=8.2,radius2=6.55,depth=2.25,location=(x,y,79.65),rotation=(0,0,A+math.pi/8));roof=bpy.context.object;roof.name='V37_CopperOctagonalRoof';link(roof);roof.data.materials.append(COPPER);tag(roof,'tower_roof');created.append(roof)
created.append(box('V37_TowerFinial',0,5,81.3,.18,.18,1.15,COPPER,'tower_roof',.01))
sc['ss_master_version']='v37_TOWER_TRANSITION';sc['rathaus_tower_pass']='closed shaft-to-crown transition; four broad open-stage corner masses; low octagonal copper roof; v33 clocks retained'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT));REP.write_text(json.dumps({'source':str(SRC),'output':str(OUT),'created_count':len(created),'retired':ret,'created':[o.name for o in created]},indent=2),encoding='utf-8');print('V37_READY',len(created),'retired',len(ret),str(OUT),flush=True)
