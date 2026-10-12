import unreal
ROOT="/ShooterMaps/__ExternalActors__/Maps/SpandauStrikeGIS/falkenhagener_feld"
assets=unreal.EditorAssetLibrary.list_assets(ROOT, recursive=True, include_folder=False)
unreal.log("[EXT] count=%d"%len(assets))
for p in assets[:40]:
    try:
        o=unreal.EditorAssetLibrary.load_asset(p)
        if not o:
            unreal.log("[EXT] NONE "+p); continue
        cls=o.get_class().get_name()
        label=""
        folder=""
        if isinstance(o,unreal.Actor):
            try: label=o.get_actor_label()
            except: pass
            try: folder=str(o.get_folder_path())
            except: pass
        unreal.log("[EXT] %s | %s | %s | %s"%(p,cls,label,folder))
    except Exception as e:
        unreal.log_warning("[EXT] ERR %s %s"%(p,e))
