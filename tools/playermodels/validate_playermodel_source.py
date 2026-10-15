from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = Path(__file__).with_name('playermodel_contract.json')
REPORT = ROOT / 'ue5' / 'SpandauStrike' / 'Saved' / 'Reports' / 'playermodel_source_validation.json'

data = json.loads(CONTRACT.read_text(encoding='utf-8-sig'))
source_dir = ROOT / data['source_dir']
master = source_dir / data['source_master']
rows = []
for model in data['models']:
    fbx = source_dir / model['fbx']
    rows.append({
        'name': model['name'],
        'team': model['team'],
        'variant': model['variant'],
        'fbx': fbx.relative_to(ROOT).as_posix(),
        'exists': fbx.is_file(),
        'size_bytes': fbx.stat().st_size if fbx.is_file() else 0,
    })
result = {
    'contract_version': data['version'],
    'source_dir': data['source_dir'],
    'master': master.relative_to(ROOT).as_posix(),
    'master_exists': master.is_file(),
    'required_bones': data['required_bones'],
    'models': rows,
}
result['ready_for_blender_rig_audit'] = result['master_exists'] and all(r['exists'] for r in rows)
REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result, separators=(',', ':')))
raise SystemExit(0 if result['ready_for_blender_rig_audit'] else 2)
