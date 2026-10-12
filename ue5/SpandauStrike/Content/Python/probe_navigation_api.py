import unreal, json, os
names=[n for n in dir(unreal.NavigationSystemV1) if any(k in n.lower() for k in ['project','random','path','nav','build','lock'])]
out={'methods':names}
path=os.path.join(unreal.Paths.project_saved_dir(),'Reports','navigation_system_v1_methods.json')
os.makedirs(os.path.dirname(path),exist_ok=True)
with open(path,'w',encoding='utf-8') as f: json.dump(out,f,indent=2)
unreal.log('[NAV_API_PROBE] '+json.dumps(out))
