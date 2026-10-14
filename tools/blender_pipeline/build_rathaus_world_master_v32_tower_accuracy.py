import bpy, math, json
from pathlib import Path
from mathutils import Vector
SRC=Path(r"C:\Users\dezen\Desktop\135er-Spandau-Defeat\tools\blender_pipeline\builds\rathaus_spandau\SpandauStrike_Rathaus_WORLD_MASTER_v31_FENESTRATION.blend")
OUT=SRC.with_name('SpandauStrike_Rathaus_WORLD_MASTER_v32_TOWER_ACCURACY.blend');REP=OUT.with_suffix('.json')
bpy.ops.wm.open_mainfile(filepath=str(SRC));sc=bpy.context.scene
A=math.radians(47.5);C=math.cos(A);S=math.sin(A)
def wxy(u,v):return (u*C-v*S,u*S+v*C)
def mat(name,color,rough=.55,metal=0):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal;return m
STONE=mat('M_V32_TowerStone',(0.52,0.47,0.40),.74);TRIM=mat('M_V32_TowerTrim',(0.67,0.60,0.49),.58);GLASS=mat('M_V32_TowerGlass',(0.035,0.065,0.075),.20,.05);GOLD=mat('M_V32_ClockGold',(0.72,0.50,0.12),.28,.55);DARK=mat('M_V32_ClockFace',(0.055,0.045,0.035),.72)
COL=bpy.data.collections.get('PRODUCTION_RATHAUS_V32_TOWER') or bpy.data.collections.new('PRODUCTION_RATHAUS_V32_TOWER');
if COL.name not in sc.collection.children:sc.collection.children.link(COL)
ret=[]
for o in bpy.data.objects:
 if o.name.startswith('P_CopperCap') or (o.name.startswith('P_Clock') and o.get('ss_export',True)):
  o.hide_viewport=True;o.hide_render=True;o['ss_export']=False;o['ss_role']='reference';o['ss_tag']='replaced_v32_tower_accuracy';ret.append(o.name)
def tag(o,k):o['ss_role']='landmark';o['ss_tag']='rathaus_v32_'+k;o['ss_export']=True;return o
def link(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 COL.objects.link(o);return o
def box(name,u,v,z,su,sv,sz,ma,k='tower',bev=.04):
 x,y=wxy(u,v);bpy.ops.mesh.primitive_cube_add(location=(x,y,z),rotation=(0,0,A));o=bpy.context.object;o.name=name;o.dimensions=(su,sv,sz);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);link(o);o.data.materials.append(ma);tag(o,k)
 if bev:md=o.modifiers.new('EdgeBevel','BEVEL');md.width=bev;md.segments=2
 return o
# Corner articulation on the 46m shaft.
created=[]
for u in (-6.65,6.65):
 for v in (-2.1,12.1): created.append(box(f'V32_TowerCorner_{u}_{v}',u,v,44,.42,.42,45.0,TRIM,'tower_shaft',.03))
# Small vertical windows: front/rear and side faces, four levels below clock.
# front/rear modules are shallow in v; side modules shallow in u.
for zi,z in enumerate((35.0,41.0,47.0,53.0)):
 for side,v in (('Front',-2.67),('Rear',12.67)):
  created.append(box(f'V32_TowerWindow_{side}_{zi}',0,v,z,1.45,.16,1.85,GLASS,'tower_window',.02))
  created.append(box(f'V32_TowerWindowSill_{side}_{zi}',0,v-.03 if side=='Front' else v+.03,z-1.03,1.85,.30,.14,TRIM,'tower_window',.02))
 for side,u in (('West',-7.17),('East',7.17)):
  created.append(box(f'V32_TowerWindow_{side}_{zi}',u,5,z,.16,1.45,1.85,GLASS,'tower_window',.02))
  created.append(box(f'V32_TowerWindowSill_{side}_{zi}',u-.03 if side=='West' else u+.03,5,z-1.03,.30,1.85,.14,TRIM,'tower_window',.02))
# clock helper: thin cylinders on each side + ticks/hands as shallow bars.
def clock_face(side,z=61.1,r=2.25):
 if side=='Front': u,v=0,-2.82; axis='Y'; outward=-1
 elif side=='Rear':u,v=0,12.82;axis='Y';outward=1
 elif side=='West':u,v=-7.32,5;axis='X';outward=-1
 else:u,v=7.32,5;axis='X';outward=1
 x,y=wxy(u,v)
 # cylinder axis local Y or X. Start cylinder axis Z then rotate into local axis, plus world yaw.
 bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=r,depth=.14,location=(x,y,z))
 o=bpy.context.object;o.name=f'V32_ClockFace_{side}'
 if axis=='Y':o.rotation_euler=(math.radians(90),0,A)
 else:o.rotation_euler=(0,math.radians(90),A)
 link(o);o.data.materials.append(DARK);tag(o,'clock');created.append(o)
 bpy.ops.mesh.primitive_torus_add(major_radius=r,minor_radius=.10,major_segments=64,minor_segments=10,location=(x,y,z))
 ring=bpy.context.object;ring.name=f'V32_ClockRing_{side}'
 if axis=='Y':ring.rotation_euler=(math.radians(90),0,A)
 else:ring.rotation_euler=(0,math.radians(90),A)
 link(ring);ring.data.materials.append(GOLD);tag(ring,'clock');created.append(ring)
 # local face coordinate placement for tick bars and hands slightly outward.
 def face_point(dx,dz,depthoff=.12):
  if side in ('Front','Rear'):
   vv=v + (depthoff*outward); uu=u+dx
  else:
   uu=u + (depthoff*outward); vv=v+dx
  xx,yy=wxy(uu,vv);return xx,yy,z+dz
 for i in range(12):
  ang=2*math.pi*i/12;dx=math.sin(ang)*(r-.28);dz=math.cos(ang)*(r-.28)
  px,py,pz=face_point(dx,dz,.13)
  if side in ('Front','Rear'): created.append(box(f'V32_ClockTick_{side}_{i}',u+dx,v+.13*outward,z+dz,.13,.09,.38,GOLD,'clock',0))
  else: created.append(box(f'V32_ClockTick_{side}_{i}',u+.13*outward,v+dx,z+dz,.09,.13,.38,GOLD,'clock',0))
 # hands: approximate 12:10 silhouette; vertical + diagonal bar composed in face plane
 # minute hand near vertical
 if side in ('Front','Rear'):
  created.append(box(f'V32_ClockHandMin_{side}',u,v+.16*outward,z+.62,.12,.10,1.38,GOLD,'clock',.01))
 else:created.append(box(f'V32_ClockHandMin_{side}',u+.16*outward,v,z+.62,.10,.12,1.38,GOLD,'clock',.01))
 # hour hand angled via cube rotation around face normal: create and adjust after
 if side in ('Front','Rear'):
  h=box(f'V32_ClockHandHour_{side}',u-.42,v+.17*outward,z+.17,.12,.10,1.12,GOLD,'clock',.01);h.rotation_euler.rotate_axis('Y',math.radians(-35*outward))
 else:
  h=box(f'V32_ClockHandHour_{side}',u+.17*outward,v-.42,z+.17,.10,.12,1.12,GOLD,'clock',.01);h.rotation_euler.rotate_axis('X',math.radians(35*outward))
for s in ('Front','Rear','West','East'):clock_face(s)
# Strong cornice directly below clock zone and above it.
created.append(box('V32_TowerClockCorniceLower',0,5,57.3,15.6,16.6,.34,TRIM,'tower_cornice',.04))
created.append(box('V32_TowerClockCorniceUpper',0,5,65.8,15.9,16.9,.38,TRIM,'tower_cornice',.04))
sc['ss_master_version']='v32_TOWER_ACCURACY';sc['rathaus_tower_pass']='four clock faces + shaft windows + corner articulation; legacy P_CopperCap retired in favor of v25 copper hip/open stage'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT));REP.write_text(json.dumps({'source':str(SRC),'output':str(OUT),'created_count':len(created),'retired':ret},indent=2),encoding='utf-8');print('V32_READY',len(created),'retired',len(ret),str(OUT),flush=True)
