import unreal
GEN="/ShooterMaps/GeneratedGIS/RathausSpandauFinal"
print("[PROBE] LIST",unreal.EditorAssetLibrary.list_assets(GEN,recursive=True,include_folder=False))
for p in [GEN+"/SM_Rathaus_Buildings_NoLandmark",GEN+"/SM_Rathaus_Landmark_Final"]:
    print("[PROBE] EXISTS",p,unreal.EditorAssetLibrary.does_asset_exist(p))
    try: print("[PROBE] LOAD",p,unreal.load_asset(p))
    except Exception as e: print("[PROBE] ERR",p,e)
