import bpy, math, json
from pathlib import Path
SRC=Path(r"C:\Users\dezen\Desktop\135er-Spandau-Defeat\tools\blender_pipeline\builds\rathaus_spandau\SpandauStrike_Rathaus_WORLD_MASTER_v33_HISTORIC_FACADE.blend")
OUT=SRC.with_name('SpandauStrike_Rathaus_WORLD_MASTER_v34_FACADE_RELIEF_FIX.blend');REP=OUT.with_suffix('.json')
bpy.ops.wm.open_mainfile(filepath=str(SRC));sc=bpy.context.scene
A=math.radians(47.5);C=math.cos(A);S=math.sin(A)
def wxy(u,v):return (u*C-v*S,u*S+v*C)
def mat(name,color,rough=.55,metal=0):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;bs.inputs['Metallic'].default_value=metal;return m
STONE=mat('M_V34_Stone',(0.56,0.50,0.42),.70);DARKTRIM=mat('M_V34_Inscription',(0.34,0.28,0.20),.60)
COL=bpy.data.collections.get('PRODUCTION_RATHAUS_V34_RELIEF_FIX') or bpy.data.collections.new('PRODUCTION_RATHAUS_V34_RELIEF_FIX')
if COL.name not in sc.collection.children:sc.collection.children.link(COL)
def tag(o,k):o['ss_role']='landmark';o['ss_tag']='rathaus_v34_'+k;o['ss_export']=True;return o
def link(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 COL.objects.link(o);return o
def box(name,u,v,z,su,sv,sz,ma,k='facade',bev=.025):
 x,y=wxy(u,v);bpy.ops.mesh.primitive_cube_add(location=(x,y,z),rotation=(0,0,A));o=bpy.context.object;o.name=name;o.dimensions=(su,sv,sz);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);link(o);o.data.materials.append(ma);tag(o,k)
 if bev:md=o.modifiers.new('EdgeBevel','BEVEL');md.width=bev;md.segments=2
 return o
ret=[]
for o in bpy.data.objects:
 if o.name.startswith('V33_FacadeBay_') or o.name.startswith('V33_PedimentInscription') or o.name in ('V33_PedimentMedallion','V33_PedimentShield'):
  o.hide_viewport=True;o.hide_render=True;o['ss_export']=False;o['ss_role']='reference';o['ss_tag']='replaced_v34_relief_fix';ret.append(o.name)
created=[]
# Slender vertical strips between the 5m window axes; no window occlusion.
for u in (-50.5,-45.5,-40.5,-35.5,-30.5,-25.5,-20.5,20.5,25.5,30.5,35.5,40.5,45.5,50.5):
 created.append(box(f'V34_FacadePier_{u}',u,-28.36,10.65,.42,.26,18.4,STONE,'facade_pier',.018))
# Slight projecting base/capital blocks to strengthen historical rhythm.
for u in (-50.5,-45.5,-40.5,-35.5,-30.5,-25.5,-20.5,20.5,25.5,30.5,35.5,40.5,45.5,50.5):
 created.append(box(f'V34_FacadePierBase_{u}',u,-28.48,2.0,.72,.44,.32,STONE,'facade_pier',.02))
 created.append(box(f'V34_FacadePierCap_{u}',u,-28.48,19.75,.82,.44,.34,STONE,'facade_pier',.02))
# Clearer central medallion and inscription relief.
def cyl(name,u,v,z,r,depth,ma):
 x,y=wxy(u,v);bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=r,depth=depth,location=(x,y,z),rotation=(math.radians(90),0,A));o=bpy.context.object;o.name=name;link(o);o.data.materials.append(ma);tag(o,'pediment');return o
created.append(cyl('V34_PedimentMedallion',0,-35.12,24.55,1.48,.18,DARKTRIM))
created.append(box('V34_PedimentShield',0,-35.25,24.50,1.08,.10,1.58,STONE,'pediment',.07))
def txt(name,text,u,z,size):
 x,y=wxy(u,-35.20);bpy.ops.object.text_add(location=(x,y,z),rotation=(math.radians(90),0,A));o=bpy.context.object;o.name=name;o.data.body=text;o.data.align_x='CENTER';o.data.align_y='CENTER';o.data.size=size;o.data.extrude=.032;o.data.bevel_depth=.008;o.data.materials.append(DARKTRIM);link(o);tag(o,'pediment_text');bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');return o
created.append(txt('V34_InscriptionLeft','ERBAUT UNTER DER REGIERUNG',-6.3,24.45,.48))
created.append(txt('V34_InscriptionRight','DER BUERGERSCHAFT',6.2,24.45,.48))
sc['ss_master_version']='v34_FACADE_RELIEF_FIX';sc['rathaus_detail_pass']='restore facade windows; relief only between bays; stronger pediment medallion/inscription'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT));REP.write_text(json.dumps({'source':str(SRC),'output':str(OUT),'created_count':len(created),'retired':ret},indent=2),encoding='utf-8');print('V34_READY',len(created),'retired',len(ret),str(OUT),flush=True)
