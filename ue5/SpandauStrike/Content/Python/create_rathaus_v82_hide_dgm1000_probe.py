import json, os, traceback, unreal
SRC='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_REAL_v81_DGM_SPAWNS_PROBE'
DST='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_REAL_v82_HIDE_DGM1000_PROBE'
REP=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_v82_hide_dgm1000_probe.json')
out={'ok':False,'errors':[],'hidden':False}
try:
    asset=unreal.EditorAssetLibrary
    if asset.does_asset_exist(DST): asset.delete_asset(DST)
    if not asset.duplicate_asset(SRC,DST): raise RuntimeError('duplicate v81 -> v82 failed')
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not lvl.load_level(DST): raise RuntimeError('load v82 failed')
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    for a in actors:
        if a.get_actor_label()=='Rathaus_DGM1_GAMEPLAY1000_v86_EXT':
            c=a.get_component_by_class(unreal.StaticMeshComponent)
            if not c: raise RuntimeError('DGM1000 component missing')
            c.set_visibility(False, True)
            c.set_editor_property('hidden_in_game', True)
            out['hidden']=True
    if not out['hidden']: raise RuntimeError('DGM1000 actor missing')
    if not lvl.save_current_level(): raise RuntimeError('save v82 failed')
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    out['ok']=True
except Exception as e:
    out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(REP),exist_ok=True)
with open(REP,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False)
print(json.dumps(out,indent=2,ensure_ascii=False))
if not out['ok']: raise RuntimeError('v82 hide DGM1000 probe failed')
