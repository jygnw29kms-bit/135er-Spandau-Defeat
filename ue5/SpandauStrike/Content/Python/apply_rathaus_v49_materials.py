import unreal, os
SRC='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v48/SM_RathausSpandau_BUILDING_v48'
DST='/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v49/SM_RathausSpandau_BUILDING_v49'
OUT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_v49_materials.txt')
src=unreal.load_asset(SRC); dst=unreal.load_asset(DST)
if not src or not dst: raise RuntimeError('source/destination mesh missing')
src_slots=src.get_editor_property('static_materials'); dst_slots=dst.get_editor_property('static_materials')
if len(src_slots)!=len(dst_slots): raise RuntimeError(f'slot mismatch {len(src_slots)} vs {len(dst_slots)}')
lines=[]
for i,(s,d) in enumerate(zip(src_slots,dst_slots)):
    mat=s.get_editor_property('material_interface')
    if not mat: raise RuntimeError('missing v48 material at slot '+str(i))
    try: dst.set_material(i,mat)
    except Exception:
        d.set_editor_property('material_interface',mat); dst_slots[i]=d
    lines.append(f'{i}|{d.material_slot_name}|{mat.get_path_name()}')
try: dst.set_editor_property('static_materials',dst_slots)
except Exception: pass
unreal.EditorAssetLibrary.save_loaded_asset(dst)
os.makedirs(os.path.dirname(OUT),exist_ok=True); open(OUT,'w',encoding='utf-8').write('\n'.join(lines))
