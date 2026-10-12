import unreal, json, os, traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_nav_sources_v73.json')
TARGETS={
'DGM':'/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v61/SM_RathausSpandau_DGM1_DOP_v60',
'ROADS':'/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v55/SM_RathausSpandau_ROADS_DGM_v54',
'BUILDING':'/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v70/SM_RathausSpandau_BERLIN3D_REAL_v70',
'PROXY':'/Game/SpandauStrike/Maps/Rathaus/Navigation/REAL_v73/SM_RathausSpandau_NAV_PROXY_v73'}
out={'ok':False,'assets':{},'errors':[]}
try:
    for name,path in TARGETS.items():
        mesh=unreal.EditorAssetLibrary.load_asset(path)
        if not mesh: raise RuntimeError('missing '+name)
        row={}
        for prop in ['has_navigation_data','nav_collision','body_setup']:
            try: row['before_'+prop]=str(mesh.get_editor_property(prop))
            except Exception as e: row['before_'+prop+'_error']=str(e)
        desired = name in ['BUILDING','PROXY']
        try:
            mesh.set_editor_property('has_navigation_data',desired)
            row['desired_has_navigation_data']=desired
            row['after_has_navigation_data']=str(mesh.get_editor_property('has_navigation_data'))
        except Exception as e: row['set_error']=str(e)
        unreal.EditorAssetLibrary.save_loaded_asset(mesh,only_if_is_dirty=False)
        out['assets'][name]=row
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not lvl.load_level(MAP): raise RuntimeError('map load failed')
    if not lvl.save_current_level(): raise RuntimeError('map save failed')
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    out['ok']=True
except Exception as e:
    out['errors'].append(str(e)); out['traceback']=traceback.format_exc()
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False)
unreal.log('[RATHAUS_NAV_SOURCES_V73] '+json.dumps(out))
if not out['ok']: raise RuntimeError('nav source configuration failed')
