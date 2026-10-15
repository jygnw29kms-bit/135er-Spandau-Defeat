import unreal, os
SRC='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v71_PEDIMENT_QA'
DST='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v72_FIRST_PLAY'
CUBE='/Engine/BasicShapes/Cube.Cube'
OUT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_v72_first_play_build.txt')
asset=unreal.EditorAssetLibrary
if asset.does_asset_exist(DST): asset.delete_asset(DST)
if not asset.duplicate_asset(SRC,DST): raise RuntimeError('duplicate v71->v72 failed')
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not level.load_level(DST): raise RuntimeError('load v72 failed')
actorsub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors=actorsub.get_all_level_actors()
starts=[a for a in actors if 'PlayerStart' in a.get_class().get_name()]
if len(starts)!=8: raise RuntimeError('expected 8 PlayerStarts, got '+str(len(starts)))
cube=unreal.load_asset(CUBE)
if not cube: raise RuntimeError('engine cube missing')
# UE character capsules use root-at-center; 90 cm is the Lyra mannequin half-height baseline.
# Pads are 6x6 m and 20 cm thick, with their top ~90 cm below each PlayerStart origin.
created=[]
for i,s in enumerate(starts,1):
    loc=s.get_actor_location()
    pad_loc=unreal.Vector(loc.x,loc.y,loc.z-100.0)
    a=actorsub.spawn_actor_from_class(unreal.StaticMeshActor,pad_loc,unreal.Rotator(0,0,0))
    if not a: raise RuntimeError('failed to spawn safety pad '+str(i))
    a.set_actor_label('SS_FIRSTPLAY_SPAWN_SAFETY_PAD_%02d'%i)
    a.set_actor_scale3d(unreal.Vector(6.0,6.0,0.2))
    comp=a.static_mesh_component
    comp.set_editor_property('static_mesh',cube)
    comp.set_collision_profile_name('BlockAll')
    a.set_actor_hidden_in_game(True)
    created.append(a)
if not level.save_current_level(): raise RuntimeError('save v72 failed')
lines=['SRC='+SRC,'DST='+DST,'PLAYERSTARTS='+str(len(starts)),'SAFETY_PADS='+str(len(created)),'EXPERIENCE_OPTION=B_ShooterGame_Elimination']
os.makedirs(os.path.dirname(OUT),exist_ok=True)
open(OUT,'w',encoding='utf-8').write('\n'.join(lines))
print('V72_FIRST_PLAY_BUILD_OK starts=%d pads=%d'%(len(starts),len(created)))

