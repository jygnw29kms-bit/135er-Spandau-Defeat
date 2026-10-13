import unreal,json,os,traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_VISUAL_v77_TEST'
out={'ok':False,'rows':[],'errors':[]}
try:
 lvl=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem); assert lvl.load_level(MAP)
 for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
  if hasattr(a,'static_mesh_component'):
   c=a.static_mesh_component; m=c.get_editor_property('static_mesh') if c else None
   p=m.get_path_name() if m else None
   if p and ('Rathaus' in p or 'DGM' in p or 'Road' in p or 'REAL_v' in p): out['rows'].append({'label':str(a.get_actor_label()),'class':a.get_class().get_name(),'mesh':p})
 out['ok']=True
except Exception as e: out['errors']=[str(e),traceback.format_exc()]
p=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_v77_testmap_actors.json');os.makedirs(os.path.dirname(p),exist_ok=True);open(p,'w',encoding='utf-8').write(json.dumps(out,indent=2,ensure_ascii=False));print(json.dumps(out,indent=2,ensure_ascii=False));unreal.SystemLibrary.execute_console_command(None,'QUIT_EDITOR')