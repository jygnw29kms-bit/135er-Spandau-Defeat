import unreal, json
ROOT="/ShooterMaps/__ExternalActors__/Maps/SpandauStrikeGIS/falkenhagener_feld"
DATA=r"C:\Users\dezen\Documents\Unreal Projects\SpandauStrike\DerivedData\safe_spawns.json"
targets={r["name"]:r for r in json.load(open(DATA))}
changed=0
found=0
for p in unreal.EditorAssetLibrary.list_assets(ROOT,recursive=True,include_folder=False):
    o=unreal.EditorAssetLibrary.load_asset(p)
    if isinstance(o,unreal.LyraPlayerStart):
        name=o.get_actor_label()
        if name not in targets: continue
        found+=1
        r=targets[name]
        old=o.get_actor_location()
        new=unreal.Vector(r["x"],r["y"],r["z"])
        if (old-new).length()>1.0:
            o.set_actor_location(new,False,True)
            unreal.EditorAssetLibrary.save_loaded_asset(o,only_if_is_dirty=False)
            changed+=1
            unreal.log("[SAFE_SPAWN] moved %s shift=%.1fm -> %.0f %.0f %.0f"%(name,r["shift_m"],new.x,new.y,new.z))
unreal.log("[SAFE_SPAWN] found=%d changed=%d"%(found,changed))
if found!=8: raise RuntimeError("Expected 8 LyraPlayerStarts")
