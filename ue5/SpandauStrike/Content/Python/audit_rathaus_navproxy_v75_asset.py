import unreal, json, os
P='/Game/SpandauStrike/Maps/Rathaus/Navigation/REAL_v75/SM_RathausSpandau_NAV_PROXY_v75'
out={'ok':False}
m=unreal.load_asset(P)
if m:
    bs=m.get_editor_property('body_setup')
    ns=m.get_editor_property('nanite_settings')
    out={'ok':True,'mesh':m.get_path_name(),'has_navigation_data':str(m.get_editor_property('has_navigation_data')),'collision_trace_flag':str(bs.get_editor_property('collision_trace_flag')) if bs else None,'agg_geom':str(bs.get_editor_property('agg_geom')) if bs else None,'nanite_enabled':str(getattr(ns,'enabled',None))}
p=os.path.join(unreal.Paths.project_saved_dir(),'Reports','rathaus_navproxy_v75_asset.json')
with open(p,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,default=str)
print(json.dumps(out,indent=2,default=str))