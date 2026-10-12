import unreal,json,os,traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_nav_relevance_audit.json')
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
out={'ok':False,'actors':[],'errors':[]}
try:
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
    for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        c=a.get_component_by_class(unreal.StaticMeshComponent)
        if not c or not c.static_mesh: continue
        p=c.static_mesh.get_path_name()
        if any(k in p for k in ['DGM1_DOP','ROADS_DGM','BERLIN3D_REAL_v70','NAV_PROXY_v73']):
            row={'label':a.get_actor_label(),'mesh':p}
            for name in ['can_ever_affect_navigation','is_navigation_relevant','navigation_relevancy','can_affect_navigation_generation']:
                try:
                    attr=getattr(c,name)
                    row[name]=attr() if callable(attr) else str(attr)
                except Exception as e: row[name+'_error']=str(e)
            try:
                row['nav_methods']=[x for x in dir(c) if 'nav' in x.lower()]
            except: pass
            out['actors'].append(row)
    out['ok']=True
except Exception as e:
    out['errors'].append(str(e));out['traceback']=traceback.format_exc()
with open(REPORT,'w',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2)
unreal.log('[RATHAUS_NAV_RELEVANCE] '+json.dumps(out))
