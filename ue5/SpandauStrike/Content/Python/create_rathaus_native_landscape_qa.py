"""Non-destructive v84 clone with native Landscape; do not claim gameplay PASS."""
import json
import os
import traceback
import unreal

SRC = '/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_REAL_v84_GROUND_LOCK_QA'
DST = '/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_REAL_v87_NATIVE_LANDSCAPE_QA'
R16 = os.path.join(unreal.Paths.project_dir(), 'SourceData', 'Rathaus', 'rathaus_dgm1_height_513.r16')
REPORT = os.path.join(unreal.Paths.project_saved_dir(), 'Reports', 'rathaus_v87_native_landscape_import.json')
result = {'ok': False, 'source': SRC, 'destination': DST, 'r16': R16}
try:
    assets = unreal.EditorAssetLibrary
    if not assets.does_asset_exist(DST):
        raise RuntimeError('Destination missing; duplicate v84 first: ' + DST)
    if not os.path.isfile(R16) or os.path.getsize(R16) != 513 * 513 * 2:
        raise RuntimeError('R16 missing or wrong length')
    level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not level.load_level(DST):
        raise RuntimeError('Unable to load v87 in editor')
    world = unreal.EditorLevelLibrary.get_editor_world()
    before = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Landscape)
    if before:
        raise RuntimeError('Landscape already present before import')
    unreal.SystemLibrary.execute_console_command(world, 'Rathaus.ImportLandscapeR16 ' + R16)
    after = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Landscape)
    result['landscape_actor_count'] = len(after)
    if len(after) != 1:
        raise RuntimeError('Importer did not create exactly one native Landscape')
    landscape = after[0]
    result['landscape_label'] = landscape.get_actor_label()
    result['landscape_components'] = len(landscape.get_components_by_class(unreal.LandscapeComponent))
    result['landscape_collision_components'] = len(landscape.get_components_by_class(unreal.LandscapeHeightfieldCollisionComponent))
    if result['landscape_components'] < 1 or result['landscape_collision_components'] < 1:
        raise RuntimeError('Native Landscape components/collision absent')
    if not level.save_current_level():
        raise RuntimeError('Unable to save v87')
    result['ok'] = True
except Exception as exc:
    result['error'] = str(exc)
    result['traceback'] = traceback.format_exc()
os.makedirs(os.path.dirname(REPORT), exist_ok=True)
with open(REPORT, 'w', encoding='utf-8') as stream:
    json.dump(result, stream, indent=2)
print('RATHAUS_LANDSCAPE_IMPORT_REPORT=' + REPORT)
print(json.dumps(result))
if not result['ok']:
    raise RuntimeError('Rathaus native Landscape import failed; see report')
