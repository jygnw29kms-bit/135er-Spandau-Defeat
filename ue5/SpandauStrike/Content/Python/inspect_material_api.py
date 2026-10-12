import unreal
for n in sorted(dir(unreal.MaterialEditingLibrary)):
    if "usage" in n.lower() or "nanite" in n.lower(): unreal.log("[MATAPI] "+n)
sm=unreal.EditorAssetLibrary.load_asset("/Game/SpandauStrikeGIS/Terrain/falkenhagener_dgm_257.falkenhagener_dgm_257")
if sm:
    for n in sorted(dir(sm)):
        if "nanite" in n.lower(): unreal.log("[SMAPI] "+n)
    try: unreal.log("[SMAPI] nanite_settings="+str(sm.get_editor_property("nanite_settings")))
    except Exception as e: unreal.log("[SMAPI] err="+str(e))
