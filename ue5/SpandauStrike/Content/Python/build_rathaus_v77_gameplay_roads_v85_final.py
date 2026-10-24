import json, os, unreal
SRC='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v75_FRONTSPAWNS'
DST='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_REAL_v77_GAMEPLAY_ROADS_V85_QA'
MESH='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v85/SM_RathausSpandau_ROADS_DGM_v85_PROJECTED_V83'
MAT='/Game/SpandauStrike/Maps/Rathaus/Materials/REAL_v80/M_Rathaus_ROADS_Asphalt_v80'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_v77_build_final.json')
asset=unreal.EditorAssetLibrary
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actorsub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
created=False
if not asset.does_asset_exist(DST):
    if not asset.duplicate_asset(SRC,DST): raise RuntimeError('duplicate v75->v77 failed')
    if not asset.save_asset(DST,only_if_is_dirty=False): raise RuntimeError('save duplicated v77 failed')
    created=True
if not level.load_level(DST): raise RuntimeError('load v77 failed')
mesh=unreal.load_asset(MESH); mat=unreal.load_asset(MAT)
if not mesh or not mat: raise RuntimeError('v85 roads asset/material missing')
actors=actorsub.get_all_level_actors()
road_candidates=[]
for a in actors:
    c=getattr(a,'static_mesh_component',None)
    sm=c.get_editor_property('static_mesh') if c else None
    path=sm.get_path_name() if sm else ''
    label=a.get_actor_label().upper()
    if 'ROADS' in label or 'ROADS_DGM' in path.upper(): road_candidates.append(a)
if len(road_candidates)!=1: raise RuntimeError(f'expected one roads actor, got {len(road_candidates)}')
road=road_candidates[0]; comp=road.static_mesh_component
comp.set_editor_property('static_mesh',mesh)
comp.set_material(0,mat)
comp.set_collision_profile_name('NoCollision')
comp.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
comp.set_editor_property('can_ever_affect_navigation',False)
road.set_actor_label('Rathaus_ROADS_VISUAL_v85_GAMEPLAY')
actors=actorsub.get_all_level_actors()
starts=[a for a in actors if 'PlayerStart' in a.get_class().get_name()]
front=[a for a in starts if a.get_actor_label().startswith('SS_FRONTSPAWN_')]
points=[a for a in actors if a.get_class().get_name()=='SpandauCapturePoint']
directors=[a for a in actors if a.get_class().get_name()=='SpandauCaptureDirector']
coverage={}
for a in front:
    tags={str(x) for x in a.get_editor_property('tags')}
    role='Attacker' if 'SSSpawn.Attacker' in tags else ('Defender' if 'SSSpawn.Defender' in tags else None)
    sector=next((s for s in range(1,5) if f'SSSpawn.Sector.{s}' in tags),None)
    if role and sector: coverage[f'{role}.S{sector}']=coverage.get(f'{role}.S{sector}',0)+1
expected={f'{r}.S{s}':2 for r in ('Attacker','Defender') for s in range(1,5)}
if not level.save_current_level(): raise RuntimeError('save v77 failed')
unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
out={'ok':len(starts)==24 and len(front)==16 and len(points)==8 and len(directors)==1 and coverage==expected and comp.get_collision_enabled()==unreal.CollisionEnabled.NO_COLLISION and not bool(comp.get_editor_property('can_ever_affect_navigation')),
     'created':created,'src':SRC,'dst':DST,'player_starts':len(starts),'front_spawns':len(front),'capture_points':len(points),'capture_directors':len(directors),'coverage':coverage,
     'roads_mesh':mesh.get_path_name(),'roads_material':mat.get_path_name(),'roads_collision':str(comp.get_collision_enabled()),'roads_navigation':bool(comp.get_editor_property('can_ever_affect_navigation'))}
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
open(REPORT,'w',encoding='utf-8').write(json.dumps(out,indent=2))
print('V77_BUILD_FINAL='+json.dumps(out,separators=(',',':')))
if not out['ok']: raise RuntimeError('v77 build validation failed')
