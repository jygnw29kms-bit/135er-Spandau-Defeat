import unreal
m=unreal.EditorAssetLibrary.load_asset("/ShooterMaps/Maps/SpandauStrikeGIS/Assets/SM_Falkenhagener_DGM1")
if not m: raise RuntimeError("mesh missing")
b=m.get_bounds()
unreal.log("[DGM_BOUNDS] origin=%s extent=%s radius=%s"%(b.origin,b.box_extent,b.sphere_radius))
mat=unreal.EditorAssetLibrary.load_asset("/ShooterMaps/Maps/SpandauStrikeGIS/Assets/M_Falkenhagener_Terrain")
unreal.log("[DGM_BOUNDS] material=%s"%mat)
