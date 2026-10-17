import os
import unreal

SRC='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v74_CAPTURE_ROUND'
DST='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v75_FRONTSPAWNS'
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_v75_front_spawns_build.txt')

# Two starts per side and sector. X follows the west->east frontline.
BASE={
  1:{'Attacker':(-33000,-2000,420),'Defender':(-17000,-2000,420)},
  2:{'Attacker':(-16000,-8200,420),'Defender':(2500,-8200,420)},
  3:{'Attacker':(3500,-3800,360),'Defender':(20500,-3800,360)},
  4:{'Attacker':(22500,7500,340),'Defender':(40000,7500,340)},
}
Y_OFFSETS=(-1400,1400)
asset=unreal.EditorAssetLibrary
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
easu=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

if asset.does_asset_exist(DST): asset.delete_asset(DST)
if not asset.duplicate_asset(SRC,DST): raise RuntimeError('duplicate v74 -> v75 failed')
if not level.load_level(DST): raise RuntimeError('load v75 failed')

start_cls=unreal.load_class(None,'/Script/LyraGame.LyraPlayerStart')
if not start_cls: raise RuntimeError('LyraPlayerStart class missing')
for a in list(easu.get_all_level_actors()):
    if a.get_actor_label().startswith('SS_FRONTSPAWN_'):
        easu.destroy_actor(a)

created=[]
for sector,sides in BASE.items():
    for role,(x,y,z) in sides.items():
        for idx,dy in enumerate(Y_OFFSETS,1):
            loc=unreal.Vector(float(x),float(y+dy),float(z))
            rot=unreal.Rotator(0.0, 0.0 if role=='Attacker' else 180.0, 0.0)
            start=easu.spawn_actor_from_class(start_cls,loc,rot,False)
            if not start: raise RuntimeError(f'failed spawn S{sector} {role} {idx}')
            label=f'SS_FRONTSPAWN_S{sector:02d}_{role.upper()}_{idx:02d}'
            start.set_actor_label(label)
            start.set_editor_property('tags',[unreal.Name(f'SSSpawn.{role}'),unreal.Name(f'SSSpawn.Sector.{sector}')])
            created.append(label)

if not level.save_current_level(): raise RuntimeError('save v75 failed')
all_starts=[a for a in easu.get_all_level_actors() if 'PlayerStart' in a.get_class().get_name()]
front=[a for a in all_starts if a.get_actor_label().startswith('SS_FRONTSPAWN_')]
lines=[f'SOURCE={SRC}',f'DEST={DST}',f'PLAYERSTARTS_TOTAL={len(all_starts)}',f'FRONTSPAWNS={len(front)}','SECTORS=4','STARTS_PER_SIDE_PER_SECTOR=2']+[f'CREATED={x}' for x in created]
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
with open(REPORT,'w',encoding='utf-8') as f:f.write('\n'.join(lines))
unreal.log('[SS_V75_FRONTSPAWN] '+' | '.join(lines))
print('V75_FRONTSPAWN_BUILD_OK')
