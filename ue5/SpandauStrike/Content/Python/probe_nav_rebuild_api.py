import unreal,json,os
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','nav_rebuild_api_probe.json')
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
recasts=[a for a in actors if 'RecastNavMesh' in a.get_class().get_name()]
out={'NavigationSystemV1_methods':[x for x in dir(unreal.NavigationSystemV1) if any(k in x.lower() for k in ['build','path','project','nav'])]}
for i,a in enumerate(recasts):
    out['recast_'+str(i)]={'label':a.get_actor_label(),'class':a.get_class().get_name(),'methods':[x for x in dir(a) if any(k in x.lower() for k in ['build','tile','nav','path','dirty'])]}
with open(REPORT,'w',encoding='utf-8') as f:json.dump(out,f,indent=2,ensure_ascii=False)
unreal.log('[NAV_API_PROBE] '+json.dumps(out))
