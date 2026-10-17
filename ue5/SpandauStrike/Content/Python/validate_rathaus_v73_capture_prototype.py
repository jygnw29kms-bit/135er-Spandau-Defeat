import json
import os
import unreal

MAP = '/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v73_CAPTURE_PROTO'
OUT = os.path.join(unreal.Paths.project_saved_dir(), 'Reports', 'rathaus_v73_capture_validation.json')

level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actorsub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

if not level.load_level(MAP):
    raise RuntimeError('failed to load v73 capture prototype')

actors = actorsub.get_all_level_actors()
starts = [a for a in actors if 'PlayerStart' in a.get_class().get_name()]
points = [a for a in actors if a.get_class().get_name() == 'SpandauCapturePoint']
directors = [a for a in actors if a.get_class().get_name() == 'SpandauCaptureDirector']

report = {
    'map': MAP,
    'player_starts': len(starts),
    'capture_points': len(points),
    'capture_directors': len(directors),
    'labels': [a.get_actor_label() for a in points + directors],
    'ok': len(starts) == 8 and len(points) == 2 and len(directors) == 1,
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w', encoding='utf-8') as handle:
    json.dump(report, handle, indent=2, ensure_ascii=False)

unreal.log('[SS_V73_VALIDATE] ' + json.dumps(report, ensure_ascii=False))
if not report['ok']:
    raise RuntimeError('v73 capture prototype validation failed')
print('V73_CAPTURE_PROTO_VALIDATE_OK')
