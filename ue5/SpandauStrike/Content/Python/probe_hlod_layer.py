import unreal
unreal.log("[HLODPROBE] enum="+str([(n,getattr(unreal.HLODLayerType,n)) for n in dir(unreal.HLODLayerType) if n.isupper()]))
factory=unreal.HLODLayerFactory()
tools=unreal.AssetToolsHelpers.get_asset_tools()
tmp="/Game/__TempHLODProbe"
if unreal.EditorAssetLibrary.does_asset_exist(tmp):
    unreal.EditorAssetLibrary.delete_asset(tmp)
a=tools.create_asset("__TempHLODProbe","/Game",unreal.HLODLayer,factory)
unreal.log("[HLODPROBE] asset="+str(a))
for p in ["layer_type","hlod_builder_class","hlod_builder_settings","parent_layer","cell_size","loading_range","always_loaded","is_spatially_loaded","editor_loading_behavior"]:
    try:
        unreal.log("[HLODPROBE] "+p+"="+str(a.get_editor_property(p)))
    except Exception as e:
        unreal.log("[HLODPROBE] "+p+" ERR "+str(e))
unreal.EditorAssetLibrary.delete_asset(tmp)
