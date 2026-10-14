import bpy, math, json
from pathlib import Path
SRC=Path(r"C:\Users\dezen\Desktop\135er-Spandau-Defeat\tools\blender_pipeline\builds\rathaus_spandau\SpandauStrike_Rathaus_WORLD_MASTER_v24_PROFILE.blend")
OUT=SRC.with_name('SpandauStrike_Rathaus_WORLD_MASTER_v25_FACADE_ACCURACY.blend'); REP=OUT.with_suffix('.json')
bpy.ops.wm.open_mainfile(filepath=str(SRC)); sc=bpy.context.scene
ANG=math.radians(47.5); C=math.cos(ANG); S=math.sin(ANG)
def wxy(u,v): return (u*C-v*S,u*S+v*C)
def mat(name,color,rough=.55,metal=0):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes=True; bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal; return m
STONE=mat('M_V25_Sandstone',(0.50,0.43,0.34),.7); TRIM=mat('M_V25_Trim',(0.64,0.57,0.47),.58); DARK=mat('M_V25_Recess',(0.025,0.028,0.03),.9); COPPER=mat('M_V25_CopperPatina',(0.10,0.28,0.22),.42,.35); GLASS=mat('M_V25_DarkGlass',(0.02,0.035,0.045),.24,.05)
COL=bpy.data.collections.get('PRODUCTION_RATHAUS_V25_ACCURACY') or bpy.data.collections.new('PRODUCTION_RATHAUS_V25_ACCURACY');
if COL.name not in sc.collection.children: sc.collection.children.link(COL)
def tag(o,k): o['ss_role']='landmark';o['ss_tag']='rathaus_v25_'+k;o['ss_export']=True;return o
def link(o):
 for c in list(o.users_collection): c.objects.unlink(o)
 COL.objects.link(o); return o
def box(name,u,v,z,su,sv,sz,ma,k='facade',bev=.05):
 x,y=wxy(u,v);bpy.ops.mesh.primitive_cube_add(location=(x,y,z),rotation=(0,0,ANG));o=bpy.context.object;o.name=name;o.dimensions=(su,sv,sz);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);link(o);o.data.materials.append(ma);tag(o,k)
 if bev: md=o.modifiers.new('EdgeBevel','BEVEL');md.width=bev;md.segments=3
 return o
def cyl(name,u,v,z,r,depth,ma,k='facade',verts=32):
 x,y=wxy(u,v);bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=(x,y,z));o=bpy.context.object;o.name=name;link(o);o.data.materials.append(ma);tag(o,k);return o
def prism(name,pts,z0,z1,ma,k):
 vs=[]
 for z in (z0,z1):
  for u,v in pts:
   x,y=wxy(u,v);vs.append((x,y,z))
 n=len(pts);fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
 for i in range(n): j=(i+1)%n;fs.append((i,j,n+j,n+i))
 me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata(vs,[],fs);me.update();me.materials.append(ma);o=bpy.data.objects.new(name,me);COL.objects.link(o);tag(o,k);return o
def arch_pediment(name,u,v,zspring,width,rise,depth,ma,k='pediment',segments=40):
 pts=[(u-width/2,v)]
 for i in range(segments+1):
  t=math.pi-(math.pi*i/segments); pts.append((u+(width/2)*math.cos(t),v))
 pts.append((u+width/2,v))
 # make 2d front outline in u/z then extrude in v manually
 verts=[]
 outline=[(u-width/2,zspring)] + [(u+(width/2)*math.cos(math.pi-math.pi*i/segments), zspring+rise*math.sin(math.pi-math.pi*i/segments)) for i in range(segments+1)] + [(u+width/2,zspring)]
 for vv in (v-depth/2,v+depth/2):
  for uu,zz in outline:
   x,y=wxy(uu,vv);verts.append((x,y,zz))
 n=len(outline);faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
 for i in range(n-1):faces.append((i,i+1,n+i+1,n+i))
 me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata(verts,[],faces);me.update();me.materials.append(ma);o=bpy.data.objects.new(name,me);COL.objects.link(o);tag(o,k);return o
def frustum_rect(name,u,v,z0,z1,su0,sv0,su1,sv1,ma,k='tower'):
 verts=[]
 for z,su,sv in ((z0,su0,sv0),(z1,su1,sv1)):
  for du,dv in ((-su/2,-sv/2),(su/2,-sv/2),(su/2,sv/2),(-su/2,sv/2)):
   x,y=wxy(u+du,v+dv);verts.append((x,y,z))
 faces=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
 me=bpy.data.meshes.new(name+'_Mesh');me.from_pydata(verts,[],faces);me.update();me.materials.append(ma);o=bpy.data.objects.new(name,me);COL.objects.link(o);tag(o,k);return o
created=[]; hidden=[]
# Retire coarse central/pediment and v24 four-column solution.
for n in ['SM_CentralSegmentPediment','V16_CentralPedimentOuter','V16_CentralPedimentInner']+[f'V24_RisalitColumn_{i}' for i in range(4)]+[f'V24_RisalitBase_{i}' for i in range(4)]+[f'V24_RisalitCapital_{i}' for i in range(4)]+[f'V24_RisalitAbacus_{i}' for i in range(4)]:
 o=bpy.data.objects.get(n)
 if o: o.hide_viewport=True;o.hide_render=True;o['ss_export']=False;o['ss_role']='reference';o['ss_tag']='replaced_v25_accuracy';hidden.append(n)
# Accurate broad central risalit skin and six vertical orders.
created.append(box('V25_CentralRisalitSkin',0,-34.05,11.1,27.2,.62,20.8,STONE,'facade',.04))
for i,u in enumerate((-10.2,-6.1,-2.0,2.0,6.1,10.2)):
 created += [cyl(f'V25_RisalitColumn_{i}',u,-34.48,12.0,.48,16.8,TRIM,'facade',28),cyl(f'V25_RisalitBase_{i}',u,-34.48,3.45,.68,.55,TRIM,'facade',28),cyl(f'V25_RisalitCapital_{i}',u,-34.48,20.55,.73,.62,TRIM,'facade',28)]
# Tall window recess rhythm between orders.
for i,u in enumerate((-8.15,-4.05,0,4.05,8.15)):
 created.append(box(f'V25_RisalitTallRecess_{i}',u,-34.39,12.1,2.35,.20,11.7,GLASS,'window',.03))
# Broad semicircular pediment and inset panel.
created.append(arch_pediment('V25_CentralRoundPediment',0,-34.18,21.0,28.4,7.7,.78,TRIM))
created.append(arch_pediment('V25_CentralPedimentInset',0,-34.62,21.55,24.8,5.9,.16,STONE))
created.append(cyl('V25_PedimentMedallion',0,-34.75,24.25,1.25,.18,TRIM,'pediment',48))
# Tower crown: retire v24 frustum crown and old cap/lantern silhouette.
for n in ['V24_TowerCrownLower','V24_TowerCrownMid','V24_TowerCrownUpper','V24_TowerLantern','V24_TowerFinialBase','SM_LanternTopRing','SM_CopperCapTop','SM_V6_CopperCapTop']:
 o=bpy.data.objects.get(n)
 if o: o.hide_viewport=True;o.hide_render=True;o['ss_export']=False;o['ss_role']='reference';o['ss_tag']='replaced_v25_tower';hidden.append(n)
# Heavy top cornice, four open-bay piers, deep dark openings, low copper hipped roof.
created.append(box('V25_TowerUpperCornice',0,5,70.35,17.3,18.1,.72,TRIM,'tower',.08))
for iu,u in enumerate((-6.1,6.1)):
 for iv,v in enumerate((-.7,10.7)):
  created.append(box(f'V25_TowerLanternPier_{iu}_{iv}',u,v,75.2,1.35,1.35,8.8,STONE,'tower',.05))
# openings on four sides
created += [box('V25_TowerOpeningFront',0,-1.36,75.2,10.7,.20,7.0,DARK,'tower',.02),box('V25_TowerOpeningRear',0,11.36,75.2,10.7,.20,7.0,DARK,'tower',.02),box('V25_TowerOpeningWest',-6.76,5,75.2,.20,10.8,7.0,DARK,'tower',.02),box('V25_TowerOpeningEast',6.76,5,75.2,.20,10.8,7.0,DARK,'tower',.02)]
created.append(box('V25_TowerRoofEave',0,5,79.95,15.0,15.8,.48,COPPER,'tower',.06))
created.append(frustum_rect('V25_TowerCopperHip',0,5,80.0,83.5,14.2,15.0,8.2,8.8,COPPER,'tower'))
created.append(box('V25_TowerFinial',0,5,84.0,.22,.22,1.1,COPPER,'tower',.02))
sc['ss_master_version']='v25_FACADE_ACCURACY';sc['rathaus_accuracy_pass']='real-reference round pediment + six-order risalit + open lantern + low copper hip';sc['rathaus_reference']='Rathaus Spandau current/historical facade reference; preserve verified 47.5deg geoframe'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT)); REP.write_text(json.dumps({'source':str(SRC),'output':str(OUT),'created_count':len(created),'created_names':[o.name for o in created],'hidden_replaced':hidden,'collection':COL.name},indent=2),encoding='utf-8');print('V25_READY',len(created),len(hidden),str(OUT),flush=True)
