import os
import unreal

SRC = '/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v72_FIRST_PLAY'
DST = '/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v73_CAPTURE_PROTO'
REPORT = os.path.join(unreal.Paths.project_saved_dir(), 'Reports', 'rathaus_v73_capture_build.txt')

POINTS = [
    ('A', unreal.Vector(-14500.0, -9730.0, 235.0)),
    ('B', unreal.Vector(500.0, -6800.0, 285.0)),
]

asset = unreal.EditorAssetLibrary
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

if asset.does_asset_exist(DST):
    asset.delete_asset(DST)
if not asset.duplicate_asset(SRC, DST):
    raise RuntimeError('duplicate v72 -> v73 failed')
if not level.load_level(DST):
    raise RuntimeError('load v73 failed')

point_cls = unreal.load_class(None, '/Script/LyraGame.SpandauCapturePoint')
director_cls = unreal.load_class(None, '/Script/LyraGame.SpandauCaptureDirector')
if not point_cls or not director_cls:
    raise RuntimeError('Spandau capture runtime classes missing; compile LyraGame first')

for actor in list(actors.get_all_level_actors()):
    if actor.get_actor_label().startswith('SS_CAPTURE_'):
        actors.destroy_actor(actor)

created = []
for idx, (letter, loc) in enumerate(POINTS, 1):
    point = actors.spawn_actor_from_class(point_cls, loc, unreal.Rotator(0, 0, 0), False)
    if not point:
        raise RuntimeError(f'failed to spawn capture point {letter}')
    point.set_actor_label(f'SS_CAPTURE_S01_{letter}')
    point.set_editor_property('sector_index', 1)
    point.set_editor_property('point_index', idx)
    point.set_editor_property('attacker_team_id', 1)
    point.set_editor_property('defender_team_id', 2)
    point.set_editor_property('capture_duration_seconds', 45.0)
    point.set_editor_property('speedup_cap_players', 4)
    point.set_editor_property('decay_delay_seconds', 3.0)
    created.append(point.get_actor_label())

director = actors.spawn_actor_from_class(director_cls, unreal.Vector(500.0, -6800.0, 950.0), unreal.Rotator(0, 0, 0), False)
if not director:
    raise RuntimeError('failed to spawn capture director')
director.set_actor_label('SS_CAPTURE_DIRECTOR')
director.set_editor_property('starting_sector', 1)
director.set_editor_property('total_sectors', 1)
director.set_editor_property('starting_attacker_tickets', 300)
director.set_editor_property('sector_ticket_refund', 50)
director.set_editor_property('sector_transition_seconds', 20.0)
created.append(director.get_actor_label())

if not level.save_current_level():
    raise RuntimeError('save v73 failed')

starts = [a for a in actors.get_all_level_actors() if 'PlayerStart' in a.get_class().get_name()]
lines = [
    f'SOURCE={SRC}',
    f'DEST={DST}',
    f'PLAYERSTARTS={len(starts)}',
    'CAPTURE_POINTS=2',
    'SECTORS=1',
    'EXPERIENCE=B_ShooterGame_Elimination',
    'NUM_BOTS=15',
] + [f'CREATED={x}' for x in created]
os.makedirs(os.path.dirname(REPORT), exist_ok=True)
with open(REPORT, 'w', encoding='utf-8') as handle:
    handle.write('\n'.join(lines))

unreal.log('[SS_V73_CAPTURE] ' + ' | '.join(lines))
print('V73_CAPTURE_PROTO_BUILD_OK')
