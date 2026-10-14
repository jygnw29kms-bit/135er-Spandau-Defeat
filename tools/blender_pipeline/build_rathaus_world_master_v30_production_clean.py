import bpy,json
from pathlib import Path
SRC=Path(r"C:\Users\dezen\Desktop\135er-Spandau-Defeat\tools\blender_pipeline\builds\rathaus_spandau\SpandauStrike_Rathaus_WORLD_MASTER_v29_GEOFRAME_CLEAN.blend")
OUT=SRC.with_name('SpandauStrike_Rathaus_WORLD_MASTER_v30_PRODUCTION_CLEAN.blend');REP=OUT.with_suffix('.json')
bpy.ops.wm.open_mainfile(filepath=str(SRC));sc=bpy.context.scene
ret=[]
def retire(o,tag):
 if o.type=='MESH' and o.get('ss_export',True):
  o.hide_viewport=True;o.hide_render=True;o['ss_export']=False;o['ss_role']='reference';o['ss_tag']=tag;ret.append(o.name)
# These two collections are legacy Rathaus-only detail generations.
for cn in ('REAL_Rebuilt_Detail','ARCH_MICRODETAIL'):
 c=bpy.data.collections.get(cn)
 if c:
  for o in c.objects: retire(o,'replaced_v30_legacy_rathaus_detail')
# Old P_* architectural generation only; keep unrelated full-map production models.
c=bpy.data.collections.get('PRODUCTION_MODELS')
arch_prefixes=('P_Window','P_Column','P_Flute','P_Central','P_EastWing','P_WestWing','P_Facade','P_Pilaster','P_Door')
if c:
 for o in c.objects:
  if o.name.startswith(arch_prefixes): retire(o,'replaced_v30_legacy_rathaus_production')
# Old Rathaus-specific urban detail only; tram/other urban assets stay live.
c=bpy.data.collections.get('FULLMAP_UrbanDetail')
if c:
 for o in c.objects:
  if 'RathausGroundWindow' in o.name or 'RathausInteriorGlow' in o.name: retire(o,'replaced_v30_legacy_rathaus_urban')
sc['ss_master_version']='v30_PRODUCTION_CLEAN';sc['rathaus_production_policy']='clean architecture + v16/v24+ only; legacy Rathaus detail retained reference-only'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT));REP.write_text(json.dumps({'source':str(SRC),'output':str(OUT),'retired_count':len(ret),'retired_sample':ret[:200]},indent=2),encoding='utf-8');print('V30_READY',len(ret),str(OUT),flush=True)
