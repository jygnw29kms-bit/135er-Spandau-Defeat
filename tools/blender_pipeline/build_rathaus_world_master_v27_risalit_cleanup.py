import bpy,json
from pathlib import Path
SRC=Path(r"C:\Users\dezen\Desktop\135er-Spandau-Defeat\tools\blender_pipeline\builds\rathaus_spandau\SpandauStrike_Rathaus_WORLD_MASTER_v26_CLEAN_SILHOUETTE.blend")
OUT=SRC.with_name('SpandauStrike_Rathaus_WORLD_MASTER_v27_RISALIT_CLEAN.blend'); REP=OUT.with_suffix('.json')
bpy.ops.wm.open_mainfile(filepath=str(SRC));sc=bpy.context.scene
changed=[]
for n in ('P_CentralRisalit','SM_CentralRisalit'):
 o=bpy.data.objects.get(n)
 if o:
  o.hide_viewport=True;o.hide_render=True;o['ss_export']=False;o['ss_role']='reference';o['ss_tag']='replaced_v27_risalit';changed.append(n)
sc['ss_master_version']='v27_RISALIT_CLEAN';sc['rathaus_cleanup_pass_v27']='remove remaining legacy central risalit mass behind v25/v26 accurate facade'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT));REP.write_text(json.dumps({'source':str(SRC),'output':str(OUT),'changed':changed},indent=2),encoding='utf-8');print('V27_READY',changed,str(OUT),flush=True)
