import unreal, json, os, traceback
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_FINAL'
OLD='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v32/SM_RathausSpandau_BUILDING_v32.SM_RathausSpandau_BUILDING_v32'
NEW='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v70/SM_RathausSpandau_BERLIN3D_REAL_v70.SM_RathausSpandau_BERLIN3D_REAL_v70'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_final_v70_replace.json')
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
res={'map':MAP,'old':OLD,'new':NEW,'ok':False,'actions':[],'errors':[]}
try:
    level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actorsub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if not level.load_level(MAP): raise RuntimeError('FINAL map could not be loaded')
    new_mesh=unreal.load_asset(NEW)
    if not new_mesh: raise RuntimeError('v70 mesh could not be loaded')
    matches=[]
    for a in actorsub.get_all_level_actors():
        c=a.get_component_by_class(unreal.StaticMeshComponent)
        if c and c.static_mesh and c.static_mesh.get_path_name()==OLD:
            matches.append((a,c))
    if len(matches)!=1: raise RuntimeError('Expected exactly one v32 building actor, found %d'%len(matches))
    a,c=matches[0]
    before={'label':a.get_actor_label(),'mesh':c.static_mesh.get_path_name(),'location':[a.get_actor_location().x,a.get_actor_location().y,a.get_actor_location().z],'rotation':[a.get_actor_rotation().pitch,a.get_actor_rotation().yaw,a.get_actor_rotation().roll],'scale':[a.get_actor_scale3d().x,a.get_actor_scale3d().y,a.get_actor_scale3d().z]}
    c.set_static_mesh(new_mesh)
    a.set_actor_label('Rathaus_BERLIN3D_REAL_v70', mark_dirty=True)
    res['actions'].append({'before':before,'after_label':a.get_actor_label(),'after_mesh':c.static_mesh.get_path_name()})
    if not level.save_current_level(): raise RuntimeError('save_current_level returned false')
    # Reload persisted level and verify.
    if not level.load_level(MAP): raise RuntimeError('Could not reload saved FINAL map')
    old_count=0; new_rows=[]
    for x in actorsub.get_all_level_actors():
        cc=x.get_component_by_class(unreal.StaticMeshComponent)
        if cc and cc.static_mesh:
            p=cc.static_mesh.get_path_name()
            if p==OLD: old_count+=1
            if p==NEW:
                new_rows.append({'label':x.get_actor_label(),'location':[x.get_actor_location().x,x.get_actor_location().y,x.get_actor_location().z],'rotation':[x.get_actor_rotation().pitch,x.get_actor_rotation().yaw,x.get_actor_rotation().roll],'scale':[x.get_actor_scale3d().x,x.get_actor_scale3d().y,x.get_actor_scale3d().z]})
    res['old_count_after']=old_count
    res['new_count_after']=len(new_rows)
    res['new_actor_after']=new_rows
    res['ok']=(old_count==0 and len(new_rows)==1)
    if not res['ok']: raise RuntimeError('Post-save validation failed')
except Exception as e:
    res['errors'].append(str(e)); res['traceback']=traceback.format_exc()
with open(REPORT,'w',encoding='utf-8') as f: json.dump(res,f,indent=2,ensure_ascii=False)
unreal.log('[RATHAUS_FINAL_REPLACE] '+json.dumps({'ok':res['ok'],'old_after':res.get('old_count_after'),'new_after':res.get('new_count_after'),'report':REPORT}))
if not res['ok']: raise RuntimeError('FINAL replacement failed; see '+REPORT)
