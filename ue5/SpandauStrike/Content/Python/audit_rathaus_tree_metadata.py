import unreal, os, json, traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
R=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_tree_metadata.json')
out={'ok':False,'errors':[]}
try:
    lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); assert lvl.load_level(MAP)
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    a=next((x for x in eas.get_all_level_actors() if x.get_actor_label()=='Rathaus_TREE_DATA_v57'),None)
    if not a: raise RuntimeError('tree metadata actor missing')
    out['label']=a.get_actor_label(); out['class']=a.get_class().get_name(); out['tags']=[str(x) for x in a.tags]
    try: out['folder']=str(a.get_folder_path())
    except: pass
    comps=[]
    for c in a.get_components_by_class(unreal.ActorComponent):
        row={'name':c.get_name(),'class':c.get_class().get_name()}
        for p in ['component_tags','asset_user_data']:
            try: row[p]=str(c.get_editor_property(p))
            except: pass
        comps.append(row)
    out['components']=comps; out['ok']=True
except Exception as e: out['errors']=[str(e),traceback.format_exc()]
os.makedirs(os.path.dirname(R),exist_ok=True)
with open(R,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False,default=str)
print(json.dumps(out,indent=2,ensure_ascii=False,default=str))
unreal.SystemLibrary.execute_console_command(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(),'QUIT_EDITOR')
