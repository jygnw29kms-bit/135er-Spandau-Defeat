import bpy, math, json
from pathlib import Path
SRC=Path(r"C:\Users\dezen\Desktop\135er-Spandau-Defeat\tools\blender_pipeline\builds\rathaus_spandau\SpandauStrike_Rathaus_WORLD_MASTER_v32_TOWER_ACCURACY.blend")
OUT=SRC.with_name('SpandauStrike_Rathaus_WORLD_MASTER_v33_HISTORIC_FACADE.blend'); REP=OUT.with_suffix('.json')
bpy.ops.wm.open_mainfile(filepath=str(SRC)); sc=bpy.context.scene
A=math.radians(47.5); C=math.cos(A); S=math.sin(A)
def wxy(u,v): return (u*C-v*S,u*S+v*C)
def mat(name,color,rough=.55,metal=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal
    return m
STONE=mat('M_V33_Stone',(0.53,0.47,0.39),.72);TRIM=mat('M_V33_Trim',(0.67,0.60,0.49),.6);GOLD=mat('M_V33_ClockGold',(0.78,0.56,0.13),.26,.58);COPPER=mat('M_V33_CopperPatina',(0.14,0.34,0.29),.40,.30);DARK=mat('M_V33_Opening',(0.028,0.032,0.032),.90)
COL=bpy.data.collections.get('PRODUCTION_RATHAUS_V33_HISTORIC') or bpy.data.collections.new('PRODUCTION_RATHAUS_V33_HISTORIC')
if COL.name not in sc.collection.children: sc.collection.children.link(COL)
def tag(o,k):
    o['ss_role']='landmark';o['ss_tag']='rathaus_v33_'+k;o['ss_export']=True;return o
def link(o):
    for c in list(o.users_collection): c.objects.unlink(o)
    COL.objects.link(o);return o
def box(name,u,v,z,su,sv,sz,ma,k='facade',bev=.03):
    x,y=wxy(u,v);bpy.ops.mesh.primitive_cube_add(location=(x,y,z),rotation=(0,0,A));o=bpy.context.object;o.name=name;o.dimensions=(su,sv,sz);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);link(o);o.data.materials.append(ma);tag(o,k)
    if bev: md=o.modifiers.new('EdgeBevel','BEVEL');md.width=bev;md.segments=2
    return o
def cyl(name,u,v,z,r,depth,ma,k='facade',verts=48,axis='Z'):
    x,y=wxy(u,v);bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=(x,y,z));o=bpy.context.object;o.name=name
    if axis=='Y': o.rotation_euler=(math.radians(90),0,A)
    elif axis=='X': o.rotation_euler=(0,math.radians(90),A)
    link(o);o.data.materials.append(ma);tag(o,k);return o
def textmesh(name,text,u,v,z,size,extrude,ma):
    x,y=wxy(u,v);bpy.ops.object.text_add(location=(x,y,z),rotation=(math.radians(90),0,A))
    o=bpy.context.object;o.name=name;o.data.body=text;o.data.align_x='CENTER';o.data.align_y='CENTER';o.data.size=size;o.data.extrude=extrude;o.data.bevel_depth=0.006;o.data.materials.append(ma)
    link(o);tag(o,'pediment_text');bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');return o
ret=[]
# Replace dark-face v32 clock treatment with exposed gold markers/hands directly on stone.
for o in bpy.data.objects:
    if o.name.startswith('V32_ClockFace_') or o.name.startswith('V32_ClockRing_') or o.name.startswith('V32_ClockTick_') or o.name.startswith('V32_ClockHand'):
        o.hide_viewport=True;o.hide_render=True;o['ss_export']=False;o['ss_role']='reference';o['ss_tag']='replaced_v33_exposed_clock';ret.append(o.name)
# Rebuild four exposed clocks. Hour marks and hands only.
created=[]
def clock(side,z=61.1,r=2.25):
    if side=='Front': u,v,axis,out=0,-2.86,'Y',-1
    elif side=='Rear': u,v,axis,out=0,12.86,'Y',1
    elif side=='West': u,v,axis,out=-7.36,5,'X',-1
    else: u,v,axis,out=7.36,5,'X',1
    # slim central boss
    if side in ('Front','Rear'): created.append(cyl(f'V33_ClockBoss_{side}',u,v+.12*out,z,.20,.18,GOLD,'clock',24,'Y'))
    else: created.append(cyl(f'V33_ClockBoss_{side}',u+.12*out,v,z,.20,.18,GOLD,'clock',24,'X'))
    for i in range(12):
        ang=2*math.pi*i/12; dx=math.sin(ang)*(r-.20); dz=math.cos(ang)*(r-.20)
        long=.46 if i%3==0 else .28
        if side in ('Front','Rear'): created.append(box(f'V33_ClockMark_{side}_{i}',u+dx,v+.14*out,z+dz,.13,.10,long,GOLD,'clock',.008))
        else: created.append(box(f'V33_ClockMark_{side}_{i}',u+.14*out,v+dx,z+dz,.10,.13,long,GOLD,'clock',.008))
    # vertical minute hand
    if side in ('Front','Rear'): created.append(box(f'V33_ClockMinute_{side}',u,v+.16*out,z+.72,.13,.10,1.55,GOLD,'clock',.01))
    else: created.append(box(f'V33_ClockMinute_{side}',u+.16*out,v,z+.72,.10,.13,1.55,GOLD,'clock',.01))
    # short hour hand, slightly left/down for 10-ish
    if side in ('Front','Rear'): h=box(f'V33_ClockHour_{side}',u-.46,v+.17*out,z+.12,.13,.10,1.22,GOLD,'clock',.01); h.rotation_euler.rotate_axis('Y',math.radians(-38*out))
    else: h=box(f'V33_ClockHour_{side}',u+.17*out,v-.46,z+.12,.10,.13,1.22,GOLD,'clock',.01); h.rotation_euler.rotate_axis('X',math.radians(38*out))
for s in ('Front','Rear','West','East'): clock(s)
# Retire square v25 upper lantern/roof parts; replace with chamfered octagonal crown.
for o in bpy.data.objects:
    if o.name.startswith('V25_TowerLanternPier_') or o.name.startswith('V25_TowerOpening') or o.name in ('V25_TowerRoofEave','V25_TowerCopperHip','V25_TowerFinial'):
        o.hide_viewport=True;o.hide_render=True;o['ss_export']=False;o['ss_role']='reference';o['ss_tag']='replaced_v33_octagonal_crown';ret.append(o.name)
# heavy balcony/cornice base
created.append(cyl('V33_TowerCrownBase',0,5,70.55,8.7,.72,TRIM,'tower_crown',8))
# eight piers around chamfered crown, leaving four broad cardinal openings visually open.
for i in range(8):
    ang=2*math.pi*i/8+math.pi/8
    u=6.25*math.cos(ang);v=5+6.25*math.sin(ang)
    created.append(box(f'V33_CrownPier_{i}',u,v,75.0,1.10,1.10,8.5,STONE,'tower_crown',.04))
# deep dark inner open chamber
created.append(cyl('V33_CrownInnerVoid',0,5,75.0,5.75,7.0,DARK,'tower_crown',8))
# roof eave + shallow octagonal copper roof
created.append(cyl('V33_CrownEave',0,5,79.55,8.15,.44,COPPER,'tower_roof',8))
x,y=wxy(0,5);bpy.ops.mesh.primitive_cone_add(vertices=8,radius1=7.75,radius2=6.55,depth=2.25,location=(x,y,80.85),rotation=(0,0,A+math.pi/8))
roof=bpy.context.object;roof.name='V33_CopperOctagonalRoof';link(roof);roof.data.materials.append(COPPER);tag(roof,'tower_roof');created.append(roof)
created.append(box('V33_TowerFinial',0,5,82.45,.18,.18,1.05,COPPER,'tower_roof',.01))
# Add facade plasticity: shallow vertical panels behind the side-wing window bays.
for u in (-48,-43,-38,-33,-28,-23,-18,18,23,28,33,38,43,48):
    created.append(box(f'V33_FacadeBay_{u}',u,-28.20,10.7,3.45,.18,18.0,STONE,'facade_relief',.015))
# Reinforce six central orders with shallow fluting strips.
for ci,u in enumerate((-10.2,-6.1,-2.0,2.0,6.1,10.2)):
    for fi,du in enumerate((-.19,0,.19)):
        created.append(box(f'V33_RisalitFlute_{ci}_{fi}',u+du,-34.99,12.1,.055,.07,15.1,TRIM,'facade_relief',.005))
    created.append(box(f'V33_RisalitAbacus_{ci}',u,-34.72,20.92,1.48,.62,.18,TRIM,'facade_relief',.02))
# Pediment medallion + inscription lines.
created.append(cyl('V33_PedimentMedallion',0,-34.92,24.45,1.42,.20,TRIM,'pediment',64,'Y'))
created.append(box('V33_PedimentShield',0,-35.05,24.40,1.15,.10,1.58,STONE,'pediment',.08))
created.append(textmesh('V33_PedimentInscriptionL','ERBAUT UNTER DER REGIERUNG',-6.0,-35.02,24.35,.43,.025,TRIM))
created.append(textmesh('V33_PedimentInscriptionR','DER BUERGERSCHAFT',6.1,-35.02,24.35,.43,.025,TRIM))
# Subtle stone plinth along front.
created.append(box('V33_FrontPlinth',0,-28.42,1.05,112.0,.72,2.10,STONE,'facade_relief',.03))
sc['ss_master_version']='v33_HISTORIC_FACADE'
sc['rathaus_detail_pass']='historic facade refinement: exposed gold clocks, octagonal open crown, pediment relief/text, central fluting, bay relief'
sc['rathaus_reference_note']='aligned to current/historic Rathaus Spandau front references; preserved 47.5deg geoframe and v32 gameplay/world data'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
REP.write_text(json.dumps({'source':str(SRC),'output':str(OUT),'created_count':len(created),'retired_count':len(ret),'retired':ret,'collection':COL.name},indent=2),encoding='utf-8')
print('V33_READY',len(created),'retired',len(ret),str(OUT),flush=True)
