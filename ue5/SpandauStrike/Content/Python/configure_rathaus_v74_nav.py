import json, os, traceback
import unreal

MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v74_CAPTURE_ROUND'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_v74_nav_config.json')
out={'ok':False,'map':MAP,'errors':[]}
try:
    level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actorsub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    editor=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    if not level.load_level(MAP): raise RuntimeError('v74 load failed')
    world=editor.get_editor_world()
    actors=actorsub.get_all_level_actors()
    bounds=[a for a in actors if 'NavMeshBoundsVolume' in a.get_class().get_name()]
    if not bounds:
        cls=getattr(unreal,'NavMeshBoundsVolume',None)
        if cls is None: cls=unreal.load_class(None,'/Script/NavigationSystem.NavMeshBoundsVolume')
        if not cls: raise RuntimeError('NavMeshBoundsVolume class unavailable')
        b=actorsub.spawn_actor_from_class(cls,unreal.Vector(0,0,500),unreal.Rotator(0,0,0),False)
        if not b: raise RuntimeError('failed spawning nav bounds')
        b.set_actor_label('SS_NAV_RATHAUS_V74')
        b.set_actor_scale3d(unreal.Vector(520,520,25))
        try: b.set_editor_property('is_spatially_loaded',False)
        except: pass
        bounds=[b]
    for b in bounds:
        b.set_actor_location(unreal.Vector(0,0,500), False, False)
        b.set_actor_scale3d(unreal.Vector(520,520,25))
    unreal.SystemLibrary.execute_console_command(world,'RebuildNavigation')
    recasts=[a for a in actorsub.get_all_level_actors() if a.get_class().get_name()=='RecastNavMesh']
    for nav in recasts:
        for prop,val in [('runtime_generation',unreal.RuntimeGenerationType.DYNAMIC),('force_rebuild_on_load',True),('can_be_main_nav_data',True)]:
            try: nav.set_editor_property(prop,val)
            except Exception as e: out.setdefault('recast_property_errors',[]).append(f'{prop}: {e}')
        try: nav.set_editor_property('is_spatially_loaded',False)
        except: pass
    out['bounds_count']=len(bounds)
    out['bounds']=[{'label':b.get_actor_label(),'location':str(b.get_actor_location()),'scale':str(b.get_actor_scale3d())} for b in bounds]
    out['recast_count']=len(recasts)
    out['recasts']=[a.get_actor_label() for a in recasts]
    out['save_current_level']=bool(level.save_current_level())
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    out['ok']=out['save_current_level'] and len(bounds)>0
except Exception as e:
    out['errors'].append(str(e)); out['traceback']=traceback.format_exc()
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
with open(REPORT,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False)
unreal.log('[SS_V74_NAV] '+json.dumps(out))
if not out['ok']: raise RuntimeError('v74 navigation configuration failed')
print('V74_NAV_CONFIG_OK')
