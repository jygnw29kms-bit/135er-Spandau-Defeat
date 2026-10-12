import unreal,json,os,traceback
ASSETS={
'v32':'/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v32/SM_RathausSpandau_BUILDING_v32.SM_RathausSpandau_BUILDING_v32',
'v70':'/Game/SpandauStrike/Maps/Rathaus/Architecture/REAL_v70/SM_RathausSpandau_BERLIN3D_REAL_v70.SM_RathausSpandau_BERLIN3D_REAL_v70'}
REPORT=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_v32_v70_perf_compare.json')
os.makedirs(os.path.dirname(REPORT),exist_ok=True)
out={'ok':True,'assets':{},'errors':[]}
for key,path in ASSETS.items():
    try:
        m=unreal.load_asset(path)
        if not m: raise RuntimeError('load failed '+path)
        bb=m.get_bounding_box(); d={'path':path,'bounds_cm':[bb.max.x-bb.min.x,bb.max.y-bb.min.y,bb.max.z-bb.min.z]}
        try:d['lod_count']=m.get_num_lods()
        except Exception as e:d['lod_error']=str(e)
        try:
            ns=m.get_editor_property('nanite_settings'); d['nanite_enabled']=bool(ns.get_editor_property('enabled'))
        except Exception as e:d['nanite_error']=str(e)
        try:
            bs=m.get_editor_property('body_setup'); ag=bs.get_editor_property('agg_geom') if bs else None
            d['collision']={'trace_flag':str(bs.get_editor_property('collision_trace_flag')) if bs else None,'boxes':len(ag.get_editor_property('box_elems')) if ag else None,'spheres':len(ag.get_editor_property('sphere_elems')) if ag else None,'capsules':len(ag.get_editor_property('sphyl_elems')) if ag else None,'convex':len(ag.get_editor_property('convex_elems')) if ag else None}
        except Exception as e:d['collision_error']=str(e)
        try:
            d['materials']=len(m.get_editor_property('static_materials'))
        except Exception as e:d['materials_error']=str(e)
        try:
            subs=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
            d['lod0_vertices']=subs.get_number_verts(m,0)
        except Exception as e:d['verts_error']=str(e)
        try:
            subs=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
            d['lod0_triangles']=subs.get_number_triangles(m,0)
        except Exception as e:d['triangles_error']=str(e)
        out['assets'][key]=d
    except Exception as e:
        out['ok']=False;out['errors'].append(key+': '+str(e));out['errors'].append(traceback.format_exc())
with open(REPORT,'w',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2)
unreal.log('[RATHAUS_PERF_COMPARE] '+json.dumps(out))
if not out['ok']: raise RuntimeError('perf compare failed')
