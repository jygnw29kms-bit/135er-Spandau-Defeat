import os
import unreal

SRC='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v73_CAPTURE_PROTO'
DST='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v74_CAPTURE_ROUND'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_v74_capture_build.txt')

POINTS=[
    (1,'A',unreal.Vector(-28000.0,-12000.0,260.0)),
    (1,'B',unreal.Vector(-22000.0,8000.0,260.0)),
    (2,'A',unreal.Vector(-14500.0,-9730.0,235.0)),
    (2,'B',unreal.Vector(500.0,-6800.0,285.0)),
    (3,'A',unreal.Vector(9000.0,5000.0,180.0)),
    (3,'B',unreal.Vector(15000.0,-12500.0,120.0)),
    (4,'A',unreal.Vector(26000.0,10000.0,150.0)),
    (4,'B',unreal.Vector(36000.0,5000.0,110.0)),
]
asset=unreal.EditorAssetLibrary
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

if asset.does_asset_exist(DST): asset.delete_asset(DST)
if not asset.duplicate_asset(SRC,DST): raise RuntimeError('duplicate v73 -> v74 failed')
if not level.load_level(DST): raise RuntimeError('load v74 failed')

point_cls=unreal.load_class(None,'/Script/LyraGame.SpandauCapturePoint')
director_cls=unreal.load_class(None,'/Script/LyraGame.SpandauCaptureDirector')
if not point_cls or not director_cls: raise RuntimeError('capture runtime classes missing')

for a in list(actors.get_all_level_actors()):
    if a.get_actor_label().startswith('SS_CAPTURE_'): actors.destroy_actor(a)

created=[]
for sector,letter,loc in POINTS:
    point=actors.spawn_actor_from_class(point_cls,loc,unreal.Rotator(0,0,0),False)
    if not point: raise RuntimeError(f'failed point S{sector} {letter}')
    point.set_actor_label(f'SS_CAPTURE_S{sector:02d}_{letter}')
    point.set_editor_property('sector_index',sector)
    point.set_editor_property('point_index',1 if letter=='A' else 2)
    point.set_editor_property('capture_duration_seconds',45.0)
    point.set_editor_property('speedup_cap_players',4)
    point.set_editor_property('decay_delay_seconds',3.0)
    point.set_editor_property('decay_per_second',0.035)
    created.append(point.get_actor_label())

director=actors.spawn_actor_from_class(director_cls,unreal.Vector(500.0,-6800.0,950.0),unreal.Rotator(0,0,0),False)
if not director: raise RuntimeError('director spawn failed')
director.set_actor_label('SS_CAPTURE_DIRECTOR')
director.set_editor_property('starting_sector',1)
director.set_editor_property('total_sectors',4)
director.set_editor_property('starting_attacker_tickets',300)
director.set_editor_property('sector_ticket_refund',50)
director.set_editor_property('sector_transition_seconds',20.0)
director.set_editor_property('respawn_wave_seconds',10.0)
director.set_editor_property('bot_objective_pulse_seconds',2.0)
director.set_editor_property('route_bots_to_objectives',True)
created.append(director.get_actor_label())

if not level.save_current_level(): raise RuntimeError('save v74 failed')
starts=[a for a in actors.get_all_level_actors() if 'PlayerStart' in a.get_class().get_name()]
lines=[f'SOURCE={SRC}',f'DEST={DST}',f'PLAYERSTARTS={len(starts)}','CAPTURE_POINTS=8','SECTORS=4','RESPAWN_WAVE=10','TICKETS=300','SECTOR_REFUND=50','EXPERIENCE=B_ShooterGame_Elimination','NUM_BOTS=15']+[f'CREATED={x}' for x in created]
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
with open(REPORT,'w',encoding='utf-8') as f: f.write('\n'.join(lines))
unreal.log('[SS_V74_CAPTURE] '+' | '.join(lines))
print('V74_CAPTURE_ROUND_BUILD_OK')
