import bpy, math, json
from pathlib import Path
from mathutils import Vector
SRC=Path(r"C:\Users\dezen\Desktop\135er-Spandau-Defeat\tools\blender_pipeline\builds\rathaus_spandau\SpandauStrike_Rathaus_WORLD_MASTER_v15_OPTIMIZED.blend")
OUT=SRC.with_name('SpandauStrike_Rathaus_WORLD_MASTER_v16_ARCH_DETAIL.blend')
REP=OUT.with_suffix('.json')
bpy.ops.wm.open_mainfile(filepath=str(SRC))
sc=bpy.context.scene
AX=math.radians(47.5); CA,SA=math.cos(AX),math.sin(AX)
def xy(u,v): return (u*CA-v*SA,u*SA+v*CA)
def mat(name,color,rough=.6,metal=0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
    return m
STONE=mat('M_V16_StoneTrim',(0.52,0.45,0.36),.62)
ROOF=mat('M_V16_RedTile',(0.30,0.055,0.028),.72)
GLASS=mat('M_V16_Glass',(0.025,0.055,0.07),.18,.04)
METAL=mat('M_V16_DarkMetal',(0.03,0.032,0.035),.34,.55)
COL=bpy.data.collections.get('PRODUCTION_RATHAUS_V16_DETAIL') or bpy.data.collections.new('PRODUCTION_RATHAUS_V16_DETAIL')
if COL.name not in sc.collection.children: sc.collection.children.link(COL)
def link(o):
    for c in list(o.users_collection): c.objects.unlink(o)
    COL.objects.link(o); o['ss_role']='landmark'; o['ss_tag']='rathaus_v16_detail'; o['ss_export']=True; return o
def box(name,u,v,z,su,sv,sz,ma,bev=.04):
    x,y=xy(u,v); bpy.ops.mesh.primitive_cube_add(location=(x,y,z),rotation=(0,0,AX)); o=bpy.context.object; o.name=name; o.dimensions=(su,sv,sz); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(ma)
    if bev: md=o.modifiers.new('Bevel','BEVEL'); md.width=bev; md.segments=2
    return link(o)
def wedge(name,u,v,z,w,d,h,ma):
    pts=[(-w/2,-d/2,0),(w/2,-d/2,0),(0,-d/2,h),(-w/2,d/2,0),(w/2,d/2,0),(0,d/2,h)]
    verts=[]
    for uu,vv,zz in pts:
        x,y=xy(u+uu,v+vv); verts.append((x,y,z+zz))
    faces=[(0,1,2),(5,4,3),(0,3,4,1),(1,4,5,2),(2,5,3,0)]
    me=bpy.data.meshes.new(name+'_Mesh'); me.from_pydata(verts,[],faces); me.update(); me.materials.append(ma)
    o=bpy.data.objects.new(name,me); COL.objects.link(o); o['ss_role']='landmark';o['ss_tag']='rathaus_v16_detail';o['ss_export']=True; return o
def arch_ring(name,u,v,z,w,h,depth,thick,ma,segments=18):
    # extruded semicircular stone ring facing plaza (-V)
    r=w/2; inner=max(.1,r-thick); base=z-h/2+r
    verts=[]
    for side in (-depth/2,depth/2):
        # outer from left spring to right spring over top
        for i in range(segments+1):
            a=math.pi-math.pi*i/segments; uu=math.cos(a)*r; zz=base+math.sin(a)*r; x,y=xy(u+uu,v+side); verts.append((x,y,zz))
        for i in range(segments+1):
            a=math.pi*i/segments; uu=math.cos(a)*inner; zz=base+math.sin(a)*inner; x,y=xy(u+uu,v+side); verts.append((x,y,zz))
    n=(segments+1)*2; faces=[]
    # front/back ring strip
    for off in (0,n):
        for i in range(segments): faces.append((off+i,off+i+1,off+(segments+1)+(segments-i-1),off+(segments+1)+(segments-i)))
    # connect outer/inner shells
    for i in range(segments): faces.append((i,i+1,n+i+1,n+i)); a=(segments+1)+i; faces.append((a,a+1,n+a+1,n+a))
    me=bpy.data.meshes.new(name+'_Mesh'); me.from_pydata(verts,[],faces); me.update(); me.materials.append(ma)
    o=bpy.data.objects.new(name,me); COL.objects.link(o); o['ss_role']='landmark';o['ss_tag']='rathaus_v16_detail';o['ss_export']=True; return o
created=[]
# Main entrance: stronger three-portal identity on front risalit.
FRONT_V=-37.0
for i,u in enumerate((-5.2,0,5.2)):
    created += [box(f'V16_PortalPierL_{i}',u-2.0,FRONT_V-3.55,3.1,.5,.8,6.2,STONE,.07), box(f'V16_PortalPierR_{i}',u+2.0,FRONT_V-3.55,3.1,.5,.8,6.2,STONE,.07)]
    created += [arch_ring(f'V16_PortalArch_{i}',u,FRONT_V-3.55,5.3,4.5,4.2,.75,.38,STONE)]
    created += [box(f'V16_PortalGlass_{i}',u,FRONT_V-3.62,2.8,3.25,.18,4.7,GLASS,.02)]
# Front roof dormers, distributed around central risalit; gable + window + cheek mass.
front_us=[-50,-42,-34,-26,-18,18,26,34,42,50]
for i,u in enumerate(front_us):
    created += [box(f'V16_DormerFrontBody_{i}',u,FRONT_V+6.2,23.1,2.8,3.0,2.5,STONE,.05)]
    created += [wedge(f'V16_DormerFrontGable_{i}',u,FRONT_V+6.0,24.35,3.3,3.4,2.0,ROOF)]
    created += [box(f'V16_DormerFrontWindow_{i}',u,FRONT_V+4.47,23.35,1.15,.14,1.55,GLASS,.02)]
# Rear dormers for skyline completeness.
REAR_V=24.0
for i,u in enumerate((-48,-36,-24,-12,0,12,24,36,48)):
    created += [box(f'V16_DormerRearBody_{i}',u,REAR_V-6.0,19.3,2.6,2.8,2.2,STONE,.05)]
    created += [wedge(f'V16_DormerRearGable_{i}',u,REAR_V-5.9,20.4,3.0,3.2,1.8,ROOF)]
    created += [box(f'V16_DormerRearWindow_{i}',u,REAR_V-4.53,19.5,1.05,.14,1.4,GLASS,.02)]
# Roofline/cornice bands giving continuous silhouette.
created += [box('V16_FrontRoofCornice',0,FRONT_V-.5,20.15,116.8,.75,.55,STONE,.08)]
created += [box('V16_RearRoofCornice',0,REAR_V+.35,16.6,116.8,.65,.45,STONE,.07)]
# Central pediment layered trim.
created += [wedge('V16_CentralPedimentOuter',0,FRONT_V-3.75,24.4,26.5,1.2,7.1,STONE)]
created += [wedge('V16_CentralPedimentInner',0,FRONT_V-4.05,25.0,22.2,.45,5.7,ROOF)]
# Tower clock-stage cornices and balustrade rhythm.
for z,su,sv in ((55.0,17.0,18.0),(69.9,23.2,22.4),(75.2,20.0,20.6)):
    created += [box(f'V16_TowerCornice_{int(z*10)}',-.8,2.5,z,su,sv,.55,STONE,.08)]
# Balustrade posts around crown using local U/V axes.
for i,u in enumerate([-8,-6,-4,-2,0,2,4,6,8]):
    for v in (-8.8,8.8): created += [box(f'V16_TowerBalU_{i}_{int(v*10)}',-.8+u,2.5+v,73.7,.28,.28,2.2,STONE,.03)]
for i,v in enumerate([-7,-5,-3,-1,1,3,5,7]):
    for u in (-9.0,9.0): created += [box(f'V16_TowerBalV_{i}_{int(u*10)}',-.8+u,2.5+v,73.7,.28,.28,2.2,STONE,.03)]
# Continuous balustrade rails.
for v in (-8.8,8.8): created += [box(f'V16_TowerRailV_{int(v*10)}',-.8,2.5+v,74.55,18.3,.25,.25,METAL,.03)]
for u in (-9.0,9.0): created += [box(f'V16_TowerRailU_{int(u*10)}',-.8+u,2.5,74.55,.25,17.9,.25,METAL,.03)]
# Classification and scene metadata.
sc['ss_master_version']='v16_ARCH_DETAIL'; sc['ss_policy']='Blender world master -> tagged modular export -> UE5'; sc['rathaus_detail_pass']='entrance+dormers+cornices+pediment+tower crown'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
report={'source':str(SRC),'output':str(OUT),'created_count':len(created),'collection':COL.name,'groups':{'front_portals':12,'front_dormer_parts':len(front_us)*3,'rear_dormer_parts':27,'cornice_pediment':4,'tower_detail':len(created)-12-len(front_us)*3-27-4}}
REP.write_text(json.dumps(report,indent=2),encoding='utf-8')
print('V16_READY',json.dumps(report))

