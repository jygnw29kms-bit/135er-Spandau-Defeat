import unreal
mat=unreal.EditorAssetLibrary.load_asset("/Game/SpandauStrikeGIS/Materials/M_SS_Terrain.M_SS_Terrain")
if not mat: raise RuntimeError("terrain material missing")
usage=None
for n in dir(unreal.MaterialUsage):
    if "NANITE" in n.upper():
        unreal.log("[NANITE_FIX] enum "+n+"="+str(getattr(unreal.MaterialUsage,n)))
        usage=getattr(unreal.MaterialUsage,n)
        break
if usage is None: raise RuntimeError("Nanite MaterialUsage enum not found")
unreal.log("[NANITE_FIX] before="+str(unreal.MaterialEditingLibrary.has_material_usage(mat,usage)))
result=unreal.MaterialEditingLibrary.set_material_usage(mat,usage)
unreal.MaterialEditingLibrary.recompile_material(mat)
unreal.EditorAssetLibrary.save_loaded_asset(mat)
unreal.log("[NANITE_FIX] set_result="+str(result))
unreal.log("[NANITE_FIX] after="+str(unreal.MaterialEditingLibrary.has_material_usage(mat,usage)))
unreal.log("[NANITE_FIX] READY")
