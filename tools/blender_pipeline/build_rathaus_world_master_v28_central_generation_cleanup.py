import bpy,json
from pathlib import Path
SRC=Path(r"C:\Users\dezen\Desktop\135er-Spandau-Defeat\tools\blender_pipeline\builds\rathaus_spandau\SpandauStrike_Rathaus_WORLD_MASTER_v27_RISALIT_CLEAN.blend")
OUT=SRC.with_name('SpandauStrike_Rathaus_WORLD_MASTER_v28_CENTRAL_CLEAN.blend');REP=OUT.with_suffix('.json')
bpy.ops.wm.open_mainfile(filepath=str(SRC));sc=bpy.context.scene
legacy=[]
for o in bpy.data.objects:
    n=o.name
    retire=False
    if n.startswith('P_') and any(k in n for k in ('CentralRisalit','CentralColumn','CentralWindow')): retire=True
    if n.startswith('SM_') and 'CentralWindow' in n: retire=True
    if retire and o.get('ss_export',True):
        o.hide_viewport=True;o.hide_render=True;o['ss_export']=False;o['ss_role']='reference';o['ss_tag']='replaced_v28_central_generation';legacy.append(n)
sc['ss_master_version']='v28_CENTRAL_CLEAN';sc['rathaus_cleanup_pass_v28']='retire legacy central risalit/column/window generation; retain v25/v26 accurate facade only'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT));REP.write_text(json.dumps({'source':str(SRC),'output':str(OUT),'retired_count':len(legacy),'retired':legacy},indent=2),encoding='utf-8');print('V28_READY',len(legacy),str(OUT),flush=True)
