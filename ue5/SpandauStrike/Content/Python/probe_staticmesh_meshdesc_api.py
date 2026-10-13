import unreal, json, os
out='C:/Users/dezen/Documents/Unreal Projects/SpandauStrike/Saved/Reports/staticmesh_meshdesc_api.json'
sm=unreal.load_asset('/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v61/SM_RathausSpandau_DGM1_DOP_v60')
sub=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
r={'sub_methods':[x for x in dir(sub) if 'mesh' in x.lower() or 'lod' in x.lower() or 'uv' in x.lower()], 'sm_methods':[x for x in dir(sm) if 'mesh' in x.lower() or 'lod' in x.lower() or 'uv' in x.lower()]}
os.makedirs(os.path.dirname(out),exist_ok=True)
open(out,'w',encoding='utf-8').write(json.dumps(r,indent=2))
print(json.dumps(r,indent=2))
unreal.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')