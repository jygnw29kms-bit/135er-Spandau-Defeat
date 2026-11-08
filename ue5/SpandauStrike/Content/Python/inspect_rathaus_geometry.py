import json
import os
import unreal

DEFAULT_MAP='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_REAL_v77_GAMEPLAY_ROADS_V85_QA'
MAP=os.environ.get('SPANDAU_VALIDATION_MAP', DEFAULT_MAP)
REPORT=os.environ.get('SPANDAU_GEOMETRY_REPORT','')
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not level.load_level(MAP):
    raise RuntimeError('failed to load map: '+MAP)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
rows=[]
keys=('rathaus','road','dgm','berlin','env','ground','playerstart','spawn','capture','nav_proxy')
for actor in actors:
    try:
        name=actor.get_name()
        label=actor.get_actor_label()
        cls=actor.get_class().get_name()
        mesh_path=''
        try:
            smc=actor.get_component_by_class(unreal.StaticMeshComponent)
            if smc and smc.static_mesh:
                mesh_path=smc.static_mesh.get_path_name()
        except Exception:
            pass
        hay=(name+' '+label+' '+cls+' '+mesh_path).lower()
        if not any(k in hay for k in keys):
            continue
        loc=actor.get_actor_location()
        try:
            origin,extent=actor.get_actor_bounds(False, False)
        except Exception:
            origin,extent=actor.get_actor_bounds(False)
        tags=[str(t) for t in actor.tags]
        row={
            'name':name,'label':label,'class':cls,'mesh_path':mesh_path,'tags':tags,
            'location':[round(loc.x,2),round(loc.y,2),round(loc.z,2)],
            'bounds_origin':[round(origin.x,2),round(origin.y,2),round(origin.z,2)],
            'bounds_extent':[round(extent.x,2),round(extent.y,2),round(extent.z,2)],
        }
        rows.append(row)
        unreal.log('SPANDAU_GEOMETRY '+json.dumps(row,separators=(',',':')))
    except Exception as exc:
        unreal.log_warning('SPANDAU_GEOMETRY_SKIP '+str(exc))
payload={'map':MAP,'count':len(rows),'actors':rows}
if REPORT:
    os.makedirs(os.path.dirname(REPORT),exist_ok=True)
    with open(REPORT,'w',encoding='utf-8') as f:
        json.dump(payload,f,indent=2)
unreal.log('SPANDAU_GEOMETRY_DONE count='+str(len(rows)))
