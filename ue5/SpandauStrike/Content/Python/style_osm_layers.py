import unreal, traceback
AS="/ShooterMaps/Maps/SpandauStrikeGIS/Assets"
EXT="/ShooterMaps/__ExternalActors__/Maps/SpandauStrikeGIS/falkenhagener_feld"
def log(s): unreal.log("[GISSTYLE] "+str(s))
def mat(name,rgb,rough):
    p=AS+"/"+name
    m=unreal.EditorAssetLibrary.load_asset(p)
    if not m:
        m=unreal.AssetToolsHelpers.get_asset_tools().create_asset(name,AS,unreal.Material,unreal.MaterialFactoryNew())
    try: unreal.MaterialEditingLibrary.delete_all_material_expressions(m)
    except: pass
    c=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant3Vector,-300,0)
    c.constant=unreal.LinearColor(rgb[0],rgb[1],rgb[2],1)
    rr=unreal.MaterialEditingLibrary.create_material_expression(m,unreal.MaterialExpressionConstant,-300,150)
    rr.r=rough
    unreal.MaterialEditingLibrary.connect_material_property(c,"",unreal.MaterialProperty.MP_BASE_COLOR)
    unreal.MaterialEditingLibrary.connect_material_property(rr,"",unreal.MaterialProperty.MP_ROUGHNESS)
    try: m.set_editor_property("used_with_nanite",True)
    except: pass
    unreal.MaterialEditingLibrary.recompile_material(m)
    unreal.EditorAssetLibrary.save_loaded_asset(m,only_if_is_dirty=False)
    return m
def main():
    road=mat("M_Falkenhagener_Road",(0.055,0.060,0.067),0.93)
    water=mat("M_Falkenhagener_Water",(0.018,0.10,0.22),0.34)
    terrain=mat("M_Falkenhagener_Terrain",(0.08,0.16,0.055),0.97)
    reg=unreal.AssetRegistryHelpers.get_asset_registry()
    changed_r=changed_w=changed_t=0
    for a in reg.get_assets_by_path(EXT,recursive=True):
        lab=str(a.get_tag_value("ActorLabel") or "")
        if not (lab.startswith("GIS_Road_") or lab.startswith("GIS_Water_") or lab=="SS_DGM1_Terrain"):
            continue
        obj=a.get_asset()
        if not obj: continue
        try:
            c=obj.static_mesh_component
            if lab.startswith("GIS_Road_"):
                c.set_material(0,road); c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION); changed_r+=1
            elif lab.startswith("GIS_Water_"):
                c.set_material(0,water); c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION); changed_w+=1
            else:
                c.set_material(0,terrain); c.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS); c.set_collision_profile_name("BlockAll"); changed_t+=1
            obj.modify()
            unreal.EditorAssetLibrary.save_asset(str(a.package_name),only_if_is_dirty=False)
        except Exception as e:
            unreal.log_warning("[GISSTYLE] "+lab+" "+str(e))
    log("roads="+str(changed_r)+" water="+str(changed_w)+" terrain="+str(changed_t))
    log("READY")
if __name__=="__main__":
    try: main()
    except Exception as e:
        unreal.log_error("[GISSTYLE] FAILED "+str(e)); unreal.log_error(traceback.format_exc()); raise
