import unreal
PKG="/ShooterMaps/__ExternalActors__/Maps/SpandauStrikeGIS/falkenhagener_feld/E/7Y/RT66P6SCHLODYKA6I7X18V"
reg=unreal.AssetRegistryHelpers.get_asset_registry()
for a in reg.get_assets_by_package_name(PKG):
    unreal.log("[HLODACTOR] asset="+str(a.asset_name)+" class="+str(a.asset_class_path))
    for k in ["ActorLabel","ActorFolderPath","ActorIsSpatiallyLoaded","HLODLayer"]:
        unreal.log("[HLODACTOR] "+k+"="+str(a.get_tag_value(k)))
    obj=a.get_asset()
    if obj:
        unreal.log("[HLODACTOR] objectclass="+obj.get_class().get_name())
        for p in ["hlod_layer","source_cell_guid","source_actors","lod_level"]:
            try: unreal.log("[HLODACTOR] "+p+"="+str(obj.get_editor_property(p)))
            except Exception as e: unreal.log("[HLODACTOR] "+p+" ERR "+str(e))
