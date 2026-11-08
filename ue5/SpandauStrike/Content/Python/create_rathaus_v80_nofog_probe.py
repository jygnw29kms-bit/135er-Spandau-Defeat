import json, os, traceback, unreal
SRC='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_REAL_v79_VISUAL_PLAYABLE_QA'
DST='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_REAL_v80_NOFOG_PROBE'
REP=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_v80_nofog_probe.json')
out={'ok':False,'errors':[],'fog_disabled':False}
try:
    asset=unreal.EditorAssetLibrary
    if asset.does_asset_exist(DST): asset.delete_asset(DST)
    if not asset.duplicate_asset(SRC,DST): raise RuntimeError('duplicate v79 -> v80 failed')
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not lvl.load_level(DST): raise RuntimeError('load v80 failed')
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    for a in actors:
        if a.get_actor_label()=='TECH_Fog_v64':
            c=a.get_component_by_class(unreal.ExponentialHeightFogComponent)
            if not c: raise RuntimeError('fog component missing')
            c.set_editor_property('fog_density',0.0)
            c.set_editor_property('fog_max_opacity',0.0)
            out['fog_disabled']=True
    if not out['fog_disabled']: raise RuntimeError('TECH_Fog_v64 missing')
    if not lvl.save_current_level(): raise RuntimeError('save v80 failed')
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    out['ok']=True
except Exception as e:
    out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(REP),exist_ok=True)
with open(REP,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False)
print(json.dumps(out,indent=2,ensure_ascii=False))
if not out['ok']: raise RuntimeError('v80 nofog probe failed')
