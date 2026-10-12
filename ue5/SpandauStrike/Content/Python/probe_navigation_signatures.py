import unreal, json, os
names=['project_point_to_navigation','get_random_point_in_navigable_radius','get_random_reachable_point_in_radius','navigation_raycast','get_path_length']
out={}
for n in names:
    fn=getattr(unreal.NavigationSystemV1,n,None)
    out[n]=getattr(fn,'__doc__',None)
p=os.path.join(unreal.Paths.project_saved_dir(),'Reports','navigation_signatures.json')
os.makedirs(os.path.dirname(p),exist_ok=True)
with open(p,'w',encoding='utf-8') as f: json.dump(out,f,indent=2,ensure_ascii=False)
unreal.log('[NAV_SIG] '+json.dumps(out))
