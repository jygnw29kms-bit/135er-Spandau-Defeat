import json, os, traceback, unreal
SRC='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_REAL_v78_GAMEPLAY_DGM1000_QA'
DST='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_REAL_v79_VISUAL_PLAYABLE_QA'
REP=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_v79_visual_playable_create.json')
out={'ok':False,'errors':[],'front_spawns_fixed':0,'fog':None}
try:
    asset=unreal.EditorAssetLibrary
    if asset.does_asset_exist(DST): asset.delete_asset(DST)
    if not asset.duplicate_asset(SRC,DST): raise RuntimeError('duplicate v78 -> v79 failed')
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not lvl.load_level(DST): raise RuntimeError('load v79 failed')
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    for a in actors:
        label=a.get_actor_label()
        if label.startswith('SS_FRONTSPAWN_'):
            yaw=180.0 if '_DEFENDER_' in label else 0.0
            a.set_actor_rotation(unreal.Rotator(roll=0.0,pitch=0.0,yaw=yaw),False)
            out['front_spawns_fixed']+=1
        if label=='TECH_Fog_v64':
            c=a.get_component_by_class(unreal.ExponentialHeightFogComponent)
            if c:
                c.set_editor_property('fog_density',0.0025)
                c.set_editor_property('start_distance',10000.0)
                c.set_editor_property('fog_max_opacity',0.65)
                out['fog']={'density':0.0025,'start_distance':10000.0,'max_opacity':0.65}
    if out['front_spawns_fixed']!=16: raise RuntimeError('expected 16 front spawns, got '+str(out['front_spawns_fixed']))
    if not out['fog']: raise RuntimeError('TECH_Fog_v64 missing')
    if not lvl.save_current_level(): raise RuntimeError('save v79 failed')
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    out['ok']=True
except Exception as e:
    out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(REP),exist_ok=True)
with open(REP,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False)
print(json.dumps(out,indent=2,ensure_ascii=False))
if not out['ok']: raise RuntimeError('v79 visual playable build failed')
