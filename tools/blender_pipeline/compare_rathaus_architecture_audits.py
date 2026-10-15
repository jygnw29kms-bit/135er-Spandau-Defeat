import argparse
import json
import re
from pathlib import Path

PREFIXES = (
    'sm_', 'p_', 'zb_', 'raw_real_', 'real_', 'master_', 'ucx_col_', 'ucx_',
)

def norm(name: str) -> str:
    s = name.lower()
    changed = True
    while changed:
        changed = False
        for p in PREFIXES:
            if s.startswith(p):
                s = s[len(p):]
                changed = True
    s = s.replace('.', '_').replace('-', '_')
    s = re.sub(r'__+', '_', s)
    s = re.sub(r'(_copy|_dup|_mesh)$', '', s)
    return s.strip('_')


def group_name(name: str) -> str:
    n = name.lower()
    if any(k in n for k in ('window', 'fenster', 'sill')): return 'window'
    if any(k in n for k in ('tower', 'turm', 'clock')): return 'tower'
    if any(k in n for k in ('roof', 'dach', 'dormer')): return 'roof'
    if 'wing' in n: return 'wing'
    if any(k in n for k in ('portal', 'door', 'tor')): return 'portal_door'
    if any(k in n for k in ('risalit', 'gable', 'cornice', 'facade', 'fassade')): return 'facade_detail'
    if any(k in n for k in ('collision', 'ucx_')): return 'collision'
    return 'other'


def load(path: Path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('v4', type=Path)
    ap.add_argument('v15', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()

    a = load(args.v4)
    b = load(args.v15)
    anames = {o['name'] for o in a['objects']}
    bnames = {o['name'] for o in b['objects']}
    exact = sorted(anames & bnames)

    amap = {}
    bmap = {}
    for name in anames: amap.setdefault(norm(name), []).append(name)
    for name in bnames: bmap.setdefault(norm(name), []).append(name)
    normalized_common = sorted(set(amap) & set(bmap))

    exact_or_norm_v4 = set(exact)
    for key in normalized_common:
        exact_or_norm_v4.update(amap[key])
    unique_v4 = sorted(anames - exact_or_norm_v4)

    unique_by_group = {}
    for name in unique_v4:
        unique_by_group.setdefault(group_name(name), []).append(name)

    payload = {
        'schema': 'SpandauStrike.RathausArchitectureCompare.v1',
        'v4_file': a['file'],
        'v15_file': b['file'],
        'v4_candidates': a['rathaus_candidates'],
        'v15_candidates': b['rathaus_candidates'],
        'v4_polygons': a['candidate_polygons'],
        'v15_polygons': b['candidate_polygons'],
        'exact_name_overlap_count': len(exact),
        'exact_name_overlap_sample': exact[:100],
        'normalized_overlap_count': len(normalized_common),
        'normalized_overlap_sample': [
            {'key': k, 'v4': sorted(amap[k])[:6], 'v15': sorted(bmap[k])[:6]}
            for k in normalized_common[:100]
        ],
        'v4_unique_after_normalization_count': len(unique_v4),
        'v4_unique_by_group': {
            g: {'count': len(names), 'names': names[:120]}
            for g, names in sorted(unique_by_group.items())
        },
        'recommendation': (
            'Do not wholesale-merge v4. Review only v4_unique_after_normalization objects; '
            'v15 already contains a much richer Rathaus production/detail set.'
        ),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({
        'exact_overlap': len(exact),
        'normalized_overlap': len(normalized_common),
        'v4_unique': len(unique_v4),
        'v4_unique_groups': {g: len(v) for g, v in sorted(unique_by_group.items())},
    }, ensure_ascii=False))
    print(args.out)

if __name__ == '__main__':
    main()
