import bpy, json
from pathlib import Path
SRC=Path(r"C:\Users\dezen\Desktop\135er-Spandau-Defeat\tools\blender_pipeline\builds\rathaus_spandau\SpandauStrike_Rathaus_WORLD_MASTER_v25_FACADE_ACCURACY.blend")
OUT=SRC.with_name('SpandauStrike_Rathaus_WORLD_MASTER_v26_CLEAN_SILHOUETTE.blend'); REP=OUT.with_suffix('.json')
bpy.ops.wm.open_mainfile(filepath=str(SRC)); sc=bpy.context.scene
hidden=[]
# Retire overlapping central-risalit generations.
exact=['SM_CentralRisalit','SM_CentralSegmentPediment','SM_PedimentBand','SM_PedimentCrestBack','SM_PedimentCrestInset','SM_PedimentMedallion','SM_TowerTopCornice','SM_LanternTopRing']
prefixes=('SM_CentralColumn_','SM_CentralPilaster_','V16_TowerCornice_','V16_TowerBal','V16_TowerRail','SM_V6_LanternRail','SM_V6_LanternPost_','SM_LanternPost_')
for o in bpy.data.objects:
    if o.name in exact or o.name.startswith(prefixes):
        if o.get('ss_export',True): hidden.append(o.name)
        o.hide_viewport=True; o.hide_render=True; o['ss_export']=False; o['ss_role']='reference'; o['ss_tag']='replaced_v26_clean_silhouette'
# Harmonize central risalit and v25 front materials to sandstone/trim.
stone=bpy.data.materials.get('M_V25_Sandstone'); trim=bpy.data.materials.get('M_V25_Trim')
for n in ('V25_CentralRisalitSkin',):
    o=bpy.data.objects.get(n)
    if o and stone:
        o.data.materials.clear(); o.data.materials.append(stone)
# Add shallow stone shoulder masses so the risalit joins the main facade cleanly without the old dark block.
import math
ANG=math.radians(47.5);C=math.cos(ANG);S=math.sin(ANG)
def wxy(u,v):return (u*C-v*S,u*S+v*C)
COL=bpy.data.collections.get('PRODUCTION_RATHAUS_V26_CLEAN') or bpy.data.collections.new('PRODUCTION_RATHAUS_V26_CLEAN')
if COL.name not in sc.collection.children:sc.collection.children.link(COL)
def box(name,u,v,z,su,sv,sz,ma,tag):
 x,y=wxy(u,v);bpy.ops.mesh.primitive_cube_add(location=(x,y,z),rotation=(0,0,ANG));o=bpy.context.object;o.name=name;o.dimensions=(su,sv,sz);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 COL.objects.link(o);o.data.materials.append(ma);o['ss_role']='landmark';o['ss_tag']=tag;o['ss_export']=True;md=o.modifiers.new('EdgeBevel','BEVEL');md.width=.05;md.segments=3;return o
created=[]
created.append(box('V26_RisalitCore',0,-31.0,11.2,27.4,5.9,22.4,stone,'rathaus_v26_risalit'))
created.append(box('V26_RisalitShoulderL',-15.2,-28.6,10.7,3.0,1.8,21.4,stone,'rathaus_v26_risalit'))
created.append(box('V26_RisalitShoulderR',15.2,-28.6,10.7,3.0,1.8,21.4,stone,'rathaus_v26_risalit'))
# Reduce overly bright pediment mass by giving inset a slightly darker sandstone instead of flat white/trim dominance.
for n in ('V25_CentralRoundPediment','V25_CentralPedimentInset'):
 o=bpy.data.objects.get(n)
 if o and stone:
  o.data.materials.clear(); o.data.materials.append(stone)
# Keep the trim as a narrow visual edge by adding an outer arch ring-like lip via duplicate slight depth is not needed here.
sc['ss_master_version']='v26_CLEAN_SILHOUETTE';sc['rathaus_cleanup_pass']='remove overlapping legacy risalit/tower generations; unify front silhouette'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT));REP.write_text(json.dumps({'source':str(SRC),'output':str(OUT),'hidden_count':len(hidden),'hidden':hidden,'created':[o.name for o in created]},indent=2),encoding='utf-8');print('V26_READY',len(hidden),len(created),str(OUT),flush=True)
