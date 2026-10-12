import unreal, collections
EXT="/Game/__ExternalActors__/Maps/BerlinSpandau/falkenhagener_feld_prod_v2"
reg=unreal.AssetRegistryHelpers.get_asset_registry()
assets=reg.get_assets_by_path(EXT,recursive=True)
c=collections.Counter()
for a in assets:
    lab=str(a.get_tag_value("ActorLabel") or "")
    if lab.startswith("BLN_"): c["buildings"]+=1
    elif lab.startswith("Road_"): c["roads"]+=1
    elif lab.startswith("Water_"): c["water"]+=1
    elif lab.startswith("SS_PlayerStart_"): c["spawns"]+=1
    elif lab: c[lab]+=1
unreal.log("[PROD_INSPECT] assets=%d"%len(assets))
for k,v in c.most_common(40):
    unreal.log("[PROD_INSPECT] %s=%d"%(k,v))
