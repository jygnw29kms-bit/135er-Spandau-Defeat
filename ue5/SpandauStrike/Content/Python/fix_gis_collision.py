import unreal,traceback
ASSETS={
"/ShooterMaps/GeneratedGIS/FalkenhagenerFeld/SM_Falkenhagener_Buildings_OBB":"complex",
"/ShooterMaps/GeneratedGIS/FalkenhagenerFeld/SM_Falkenhagener_DGM10m":"complex",
"/ShooterMaps/GeneratedGIS/FalkenhagenerFeld/SM_Falkenhagener_Roads_DGM":"none",
"/ShooterMaps/GeneratedGIS/FalkenhagenerFeld/SM_Falkenhagener_Water_DGM":"none",
"/ShooterMaps/GeneratedGIS/FalkenhagenerFeld/SM_SS_TreeTrunks":"none",
"/ShooterMaps/GeneratedGIS/FalkenhagenerFeld/SM_SS_TreeBroadleaf":"none",
"/ShooterMaps/GeneratedGIS/FalkenhagenerFeld/SM_SS_TreeConifer":"none",
}
def log(s): unreal.log("[COLFIX] "+str(s))
for path,mode in ASSETS.items():
    m=unreal.EditorAssetLibrary.load_asset(path)
    if not m:
        log("missing "+path); continue
    bs=m.get_editor_property("body_setup")
    if not bs:
        log("no body setup "+path); continue
    if mode=="complex":
        bs.set_editor_property("collision_trace_flag",unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    else:
        bs.set_editor_property("collision_trace_flag",unreal.CollisionTraceFlag.CTF_USE_DEFAULT)
        try:
            m.set_editor_property("customized_collision",False)
        except: pass
    unreal.EditorAssetLibrary.save_loaded_asset(m,False)
    log(path+" -> "+str(bs.get_editor_property("collision_trace_flag")))
log("DONE")
