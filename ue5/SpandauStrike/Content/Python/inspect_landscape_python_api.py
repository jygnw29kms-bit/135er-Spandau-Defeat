"""Read-only discovery of UE 5.8 Landscape editor Python APIs for P0."""
import json
import os
import unreal

out = {'engine': str(unreal.SystemLibrary.get_engine_version()), 'classes': {}}
for name in ('Landscape', 'LandscapeProxy', 'LandscapeEditorSubsystem',
             'LandscapeEditorUtils', 'LandscapeImportHelper', 'LandscapeComponent',
             'LandscapeHeightfieldCollisionComponent', 'EditorActorSubsystem'):
    cls = getattr(unreal, name, None)
    if cls is None:
        out['classes'][name] = {'available': False}
    else:
        out['classes'][name] = {'available': True, 'methods': [
            attr for attr in dir(cls)
            if any(term in attr.lower() for term in ('import', 'height', 'landscape', 'collision', 'create'))
            and not attr.startswith('_')]}
path = os.path.join(unreal.Paths.project_saved_dir(), 'Reports', 'landscape_python_api_probe.json')
os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, 'w', encoding='utf-8') as stream:
    json.dump(out, stream, indent=2)
print('LANDSCAPE_API_PROBE=' + path)
