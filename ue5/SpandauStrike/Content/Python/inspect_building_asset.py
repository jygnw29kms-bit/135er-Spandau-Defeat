import unreal
p="/ShooterMaps/Maps/SpandauStrikeGIS/Assets/SM_Falkenhagener_ExactBuildings.SM_Falkenhagener_ExactBuildings"
m=unreal.EditorAssetLibrary.load_asset(p)
unreal.log("[BLDG_AUDIT] asset="+str(m))
if m:
 b=m.get_bounds()
 unreal.log("[BLDG_AUDIT] extent="+str(b.box_extent)+" radius="+str(b.sphere_radius))
 try:
  bs=m.get_editor_property("body_setup")
  unreal.log("[BLDG_AUDIT] collision="+str(bs.get_editor_property("collision_trace_flag")))
 except Exception as e: unreal.log("[BLDG_AUDIT] collision err "+str(e))
 try:
  mats=m.get_editor_property("static_materials")
  unreal.log("[BLDG_AUDIT] materials="+str(mats))
 except Exception as e: unreal.log("[BLDG_AUDIT] materials err "+str(e))
