import json, os, unreal
MAP='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v75_FRONTSPAWNS'
OUT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_v75_front_spawns_validation.json')
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actorsub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if not level.load_level(MAP): raise RuntimeError('failed to load v75')
actors=actorsub.get_all_level_actors()
starts=[a for a in actors if 'PlayerStart' in a.get_class().get_name()]
front=[a for a in starts if a.get_actor_label().startswith('SS_FRONTSPAWN_')]
points=[a for a in actors if a.get_class().get_name()=='SpandauCapturePoint']
directors=[a for a in actors if a.get_class().get_name()=='SpandauCaptureDirector']
rows=[]
coverage={}
for a in front:
    tags={str(x) for x in a.get_editor_property('tags')}
    role='Attacker' if 'SSSpawn.Attacker' in tags else ('Defender' if 'SSSpawn.Defender' in tags else None)
    sector=next((s for s in range(1,5) if f'SSSpawn.Sector.{s}' in tags),None)
    rows.append({'label':a.get_actor_label(),'role':role,'sector':sector,'tags':sorted(tags)})
    if role and sector: coverage[f'{role}.S{sector}']=coverage.get(f'{role}.S{sector}',0)+1
expected={f'{r}.S{s}':2 for r in ('Attacker','Defender') for s in range(1,5)}
report={'map':MAP,'player_starts':len(starts),'front_spawns':len(front),'capture_points':len(points),'capture_directors':len(directors),'coverage':coverage,'expected':expected,'front':rows}
report['ok']=len(starts)==24 and len(front)==16 and len(points)==8 and len(directors)==1 and coverage==expected
os.makedirs(os.path.dirname(OUT),exist_ok=True)
with open(OUT,'w',encoding='utf-8') as f: json.dump(report,f,indent=2,ensure_ascii=False)
unreal.log('[SS_V75_VALIDATE] '+json.dumps(report,ensure_ascii=False))
if not report['ok']: raise RuntimeError('v75 front spawn validation failed')
print('V75_FRONTSPAWN_VALIDATE_OK')
