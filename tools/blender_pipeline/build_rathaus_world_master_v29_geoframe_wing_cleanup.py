import bpy,json
from pathlib import Path
SRC=Path(r"C:\Users\dezen\Desktop\135er-Spandau-Defeat\tools\blender_pipeline\builds\rathaus_spandau\SpandauStrike_Rathaus_WORLD_MASTER_v28_CENTRAL_CLEAN.blend")
OUT=SRC.with_name('SpandauStrike_Rathaus_WORLD_MASTER_v29_GEOFRAME_CLEAN.blend');REP=OUT.with_suffix('.json')
bpy.ops.wm.open_mainfile(filepath=str(SRC));sc=bpy.context.scene
ret=[];col=bpy.data.collections.get('PRODUCTION_MODELS')
for o in col.objects if col else []:
 if o.get('ss_export',True) and ('EastWing' in o.name or 'WestWing' in o.name):
  o.hide_viewport=True;o.hide_render=True;o['ss_export']=False;o['ss_role']='reference';o['ss_tag']='replaced_v29_wrong_geoframe_wing';ret.append(o.name)
sc['ss_master_version']='v29_GEOFRAME_CLEAN';sc['rathaus_cleanup_pass_v29']='retire unrotated P_EastWing/P_WestWing family; keep verified 47.5deg SM wing geometry'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT));REP.write_text(json.dumps({'source':str(SRC),'output':str(OUT),'retired_count':len(ret),'retired':ret},indent=2),encoding='utf-8');print('V29_READY',len(ret),str(OUT),flush=True)
