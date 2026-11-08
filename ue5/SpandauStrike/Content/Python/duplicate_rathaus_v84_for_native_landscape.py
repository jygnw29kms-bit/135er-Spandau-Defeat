"""Phase 1: duplicate v84 into v87 without loading either level."""
import unreal
src='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_REAL_v84_GROUND_LOCK_QA'
dst='/Game/SpandauStrike/Maps/Rathaus/Validation/LV_RathausSpandau_REAL_v87_NATIVE_LANDSCAPE_QA'
assets=unreal.EditorAssetLibrary
if assets.does_asset_exist(dst):
    raise RuntimeError('Destination exists; refusing overwrite')
duplicated = assets.duplicate_asset(src,dst)
if not duplicated:
    raise RuntimeError('Duplicate failed')
if not assets.save_loaded_asset(duplicated, False):
    raise RuntimeError('Failed to save duplicate asset')
print('RATHAUS_V87_DUPLICATED=' + dst)
