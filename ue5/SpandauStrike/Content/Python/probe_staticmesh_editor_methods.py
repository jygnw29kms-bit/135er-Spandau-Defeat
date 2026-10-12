import unreal,json,os
s=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
out={'methods':[x for x in dir(s) if any(k in x.lower() for k in ['collision','mesh','lod','build'])]}
report=os.path.join(unreal.Paths.project_saved_dir(),'Reports','staticmesh_editor_methods.json');open(report,'w').write(json.dumps(out,indent=2));unreal.log('[SM_METHODS] '+json.dumps(out))
