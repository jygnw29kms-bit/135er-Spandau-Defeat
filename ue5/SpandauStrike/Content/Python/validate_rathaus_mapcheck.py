import os
import unreal

DEFAULT_MAP='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_REAL_v77_GAMEPLAY_ROADS_V85_QA'
MAP=os.environ.get('SPANDAU_VALIDATION_MAP', DEFAULT_MAP)
level=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not level.load_level(MAP):
    raise RuntimeError('failed to load map for MapCheck: '+MAP)
world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
unreal.SystemLibrary.execute_console_command(world, 'MAP CHECKDEP NOCLEARLOG')
unreal.log('SPANDAU_MAPCHECK_TRIGGERED='+MAP)
