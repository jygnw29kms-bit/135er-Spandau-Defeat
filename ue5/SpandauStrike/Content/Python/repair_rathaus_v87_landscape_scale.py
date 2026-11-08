"""Repair the native v87 Landscape world transform only. Run in an exclusive UE editor session."""
import json
import os
import unreal

MAP = '/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_REAL_v87_NATIVE_LANDSCAPE_QA'
LABEL = 'Rathaus_R16_NativeLandscape_Collision'
REPORT = os.path.join(unreal.Paths.project_saved_dir(), 'Reports', 'rathaus_v87_landscape_scale_repair.json')
EXPECTED_SCALE_XY = 100000.0 / 504.0

def run():
    level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not level.load_level(MAP):
        raise RuntimeError('Could not load v87 map')
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    landscapes = [a for a in actors if isinstance(a, unreal.Landscape)]
    if len(landscapes) != 1 or landscapes[0].get_actor_label() != LABEL:
        raise RuntimeError('Expected exactly one labeled native Landscape; found {}'.format(len(landscapes)))
    land = landscapes[0]
    old = land.get_actor_scale3d()
    old_position = land.get_actor_location()
    if abs(old_position.x + 50000) > 1 or abs(old_position.y + 50000) > 1:
        raise RuntimeError('Unexpected Landscape origin: {}'.format(old_position))
    if not (abs(old.x - 1000.0 / 504.0) < 0.01 and abs(old.y - 1000.0 / 504.0) < 0.01 and abs(old.z - 1.0) < 0.01):
        raise RuntimeError('Unexpected scale, refusing overwrite: {}'.format(old))
    new_scale = unreal.Vector(EXPECTED_SCALE_XY, EXPECTED_SCALE_XY, 100.0)
    land.set_actor_scale3d(new_scale)
    land.set_actor_enable_collision(True)
    if not level.save_current_level():
        raise RuntimeError('Could not save repaired map')
    return {'ok': True, 'map': MAP, 'old_scale': [old.x, old.y, old.z], 'new_scale': [new_scale.x, new_scale.y, new_scale.z], 'origin': [old_position.x, old_position.y, old_position.z]}

try:
    result = run()
except Exception as exc:
    result = {'ok': False, 'error': str(exc)}
os.makedirs(os.path.dirname(REPORT), exist_ok=True)
with open(REPORT, 'w', encoding='utf-8') as handle:
    json.dump(result, handle, indent=2)
print(json.dumps(result))
if not result['ok']:
    raise RuntimeError(result['error'])
