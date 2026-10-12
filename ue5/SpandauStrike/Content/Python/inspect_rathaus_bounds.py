import unreal
for path in [
"/ShooterMaps/GeneratedGIS/RathausSpandauFinal/SM_Rathaus_Landmark_Final",
"/ShooterMaps/GeneratedGIS/RathausSpandau/SM_Rathaus_Buildings",
"/ShooterMaps/GeneratedGIS/RathausSpandau/SM_Rathaus_DGM"]:
    m=unreal.load_asset(path)
    print("[BOUNDS] ASSET",path,m)
    if m:
        for meth in ("get_bounding_box","get_bounds"):
            try:
                fn=getattr(m,meth)
                print("[BOUNDS]",meth,fn())
            except Exception as e: print("[BOUNDS] ERR",meth,e)
        try: print("[BOUNDS] EXT",m.get_editor_property("extended_bounds"))
        except Exception as e: print("[BOUNDS] EXTERR",e)
