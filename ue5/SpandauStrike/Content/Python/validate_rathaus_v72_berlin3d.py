import unreal, json, os, traceback
MAP = '/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_REAL_v72_BERLIN3D'
TARGET = '/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v70/SM_RathausSpandau_BERLIN3D_REAL_v70.SM_RathausSpandau_BERLIN3D_REAL_v70'
REPORT = os.path.join(unreal.Paths.project_saved_dir(), 'Reports', 'rathaus_v72_validation.json')
os.makedirs(os.path.dirname(REPORT), exist_ok=True)
result = {'map': MAP, 'target_mesh': TARGET, 'ok': False, 'actors': [], 'errors': []}
try:
    level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not level.load_level(MAP):
        raise RuntimeError('Could not load v72 validation map')
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    for a in actors:
        item = {
            'label': a.get_actor_label(),
            'class': a.get_class().get_name(),
            'location': [a.get_actor_location().x, a.get_actor_location().y, a.get_actor_location().z],
            'rotation': [a.get_actor_rotation().pitch, a.get_actor_rotation().yaw, a.get_actor_rotation().roll],
            'scale': [a.get_actor_scale3d().x, a.get_actor_scale3d().y, a.get_actor_scale3d().z],
            'mesh': ''
        }
        try:
            smc = a.get_component_by_class(unreal.StaticMeshComponent)
            if smc and smc.static_mesh:
                item['mesh'] = smc.static_mesh.get_path_name()
        except Exception as e:
            item['mesh_error'] = str(e)
        result['actors'].append(item)
    matches = [x for x in result['actors'] if x['mesh'] == TARGET]
    old_v32 = [x for x in result['actors'] if 'REAL_v32' in x['mesh'] or 'BUILDING_v32' in x['mesh']]
    result['actor_count'] = len(result['actors'])
    result['target_matches'] = matches
    result['old_v32_matches'] = old_v32
    result['ok'] = len(matches) == 1 and len(old_v32) == 0
except Exception as e:
    result['errors'].append(str(e))
    result['traceback'] = traceback.format_exc()
with open(REPORT, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
unreal.log('[RATHAUS_V72_VALIDATE] '+json.dumps({'ok': result['ok'], 'actor_count': result.get('actor_count'), 'target_matches': len(result.get('target_matches', [])), 'old_v32_matches': len(result.get('old_v32_matches', [])), 'report': REPORT}))
if not result['ok']:
    raise RuntimeError('Rathaus v72 validation failed; see '+REPORT)
