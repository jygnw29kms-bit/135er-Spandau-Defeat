import json, os, traceback, unreal
SRC='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_REAL_v82_HIDE_DGM1000_PROBE'
DST='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_REAL_v83_BUILDING_ONLY_VISUAL_PROBE'
REP=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_v83_building_only_visual_probe.json')
HIDE={'Rathaus_DGM1_DOP2025_v61','Rathaus_ROADS_VISUAL_v85_GAMEPLAY'}
out={'ok':False,'errors':[],'hidden':[]}
try:
    asset=unreal.EditorAssetLibrary
    if asset.does_asset_exist(DST): asset.delete_asset(DST)
    if not asset.duplicate_asset(SRC,DST): raise RuntimeError('duplicate v82 -> v83 failed')
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not lvl.load_level(DST): raise RuntimeError('load v83 failed')
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    for a in actors:
        if a.get_actor_label() in HIDE:
            c=a.get_component_by_class(unreal.StaticMeshComponent)
            if not c: raise RuntimeError('missing component '+a.get_actor_label())
            c.set_visibility(False, True)
            c.set_editor_property('hidden_in_game', True)
            out['hidden'].append(a.get_actor_label())
    if set(out['hidden'])!=HIDE: raise RuntimeError('did not hide expected layers: '+str(out['hidden']))
    if not lvl.save_current_level(): raise RuntimeError('save v83 failed')
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    out['ok']=True
except Exception as e:
    out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(REP),exist_ok=True)
with open(REP,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False)
print(json.dumps(out,indent=2,ensure_ascii=False))
if not out['ok']: raise RuntimeError('v83 building-only visual probe failed')
