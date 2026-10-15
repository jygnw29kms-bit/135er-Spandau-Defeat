import unreal, os
SRC='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v66_PLAYABLE'
DST='/Game/SpandauStrike/Maps/Rathaus/LV_RathausSpandau_REAL_v67_LIGHTING'
OUT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_v67_lighting_build.txt')
asset=unreal.EditorAssetLibrary
if asset.does_asset_exist(DST): asset.delete_asset(DST)
if not asset.duplicate_asset(SRC,DST): raise RuntimeError('duplicate v66->v67 failed')
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not level.load_level(DST): raise RuntimeError('load v67 failed')
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
sun=sky=None
for a in actors:
    if a.get_actor_label()=='TECH_Sun_v64': sun=a
    elif a.get_actor_label()=='TECH_Sky_v64': sky=a
if not sun or not sky: raise RuntimeError('technical sun/sky missing')
sun.set_actor_rotation(unreal.Rotator(-35.0,-137.5,0.0),False)
sc=sun.get_component_by_class(unreal.DirectionalLightComponent)
sc.set_editor_property('intensity',4.0)
sk=sky.get_component_by_class(unreal.SkyLightComponent)
sk.set_editor_property('intensity',2.3)
try: sk.recapture_sky()
except Exception: pass
starts=[a for a in actors if 'PlayerStart' in a.get_class().get_name()]
if len(starts)!=8: raise RuntimeError('expected 8 PlayerStarts, got '+str(len(starts)))
if not level.save_current_level(): raise RuntimeError('save v67 failed')
os.makedirs(os.path.dirname(OUT),exist_ok=True)
open(OUT,'w',encoding='utf-8').write('SRC='+SRC+'\nDST='+DST+'\nSUN_ROT=-35,-137.5,0\nSUN_INTENSITY=4.0\nSKY_INTENSITY=2.3\nPLAYERSTARTS='+str(len(starts))+'\n')