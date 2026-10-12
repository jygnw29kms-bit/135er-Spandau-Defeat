import unreal, traceback, time
import berlin_spandau_lyra_import as gis

MAP="/ShooterMaps/Maps/SpandauStrikeGIS/falkenhagener_feld"
LAT=52.5524034
LON=13.1668941
HALF=900.0
FOLDER="Berlin_LoD2_Autonomous_Import/falkenhagener_feld/Buildings"

def log(s): unreal.log("[SS_BUILDINGS] "+str(s))

def main():
    started=time.perf_counter()
    ce,cn=gis.wgs84_to_utm33(LAT,LON)
    bbox=(ce-HALF,cn-HALF,ce+HALF,cn+HALF)
    ft=gis.discover_feature_type()
    root=gis.download_features(ft,bbox)
    records=[]
    for feature in gis.feature_members(root):
        rec=gis.build_record(feature)
        if rec: records.append(rec)
    if not records: raise RuntimeError("no building records")
    valid=[r["base_z"] for r in records if abs(r["base_z"])>0.001]
    oz=sorted(valid)[len(valid)//2] if valid else 0.0
    origin=(ce,cn,oz)
    mesh=unreal.EditorAssetLibrary.load_asset(gis.CUBE_MESH)
    mat=unreal.EditorAssetLibrary.load_asset("/Game/SpandauStrike/GIS/Materials/M_SS_Building")
    if not mat: mat=unreal.EditorAssetLibrary.load_asset(gis.GRID_MATERIAL)
    if not mesh: raise RuntimeError("cube mesh missing")
    sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not sub.load_level(MAP): raise RuntimeError("map load failed")
    count=0
    with unreal.ScopedSlowTask(len(records),"Rebuilding Falkenhagener Feld buildings") as task:
        for rec in records:
            task.enter_progress_frame(1)
            a=gis.spawn_building(rec,origin,FOLDER,mesh,mat)
            if a:
                try: a.static_mesh_component.set_collision_profile_name("BlockAll")
                except: pass
                count+=1
    if not sub.save_current_level(): raise RuntimeError("map save failed")
    log(f"BUILDINGS_READY count={count} seconds={time.perf_counter()-started:.1f}")

if __name__=="__main__":
    try: main()
    except Exception as exc:
        unreal.log_error("[SS_BUILDINGS] FAILED "+str(exc))
        unreal.log_error(traceback.format_exc())
        raise
