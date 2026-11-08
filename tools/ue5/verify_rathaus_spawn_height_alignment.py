"""Offline v84 spawn-to-R16 height alignment check (not a collision test)."""
import json
import struct
from pathlib import Path

repo = Path(__file__).resolve().parents[2]
source = repo / 'ue5/SpandauStrike/SourceData/Rathaus'
report = repo / 'ue5/SpandauStrike/Saved/Reports/rathaus_v84_ground_lock_qa.json'
meta = json.loads((source / 'rathaus_dgm1_height_513.json').read_text(encoding='utf-8'))
raw = (source / 'rathaus_dgm1_height_513.r16').read_bytes()
width, height = meta['width'], meta['height']
assert len(raw) == width * height * 2
samples = struct.unpack('<' + str(width * height) + 'H', raw)
spawns = json.loads(report.read_text(encoding='utf-8'))['spawns']
assert len(spawns) == 24, len(spawns)
spacing = meta['xy_scale_cm_per_vertex']

def sample_at(x, y):
    col = round((x + 50000) / spacing)
    row = round((y + 50000) / spacing)
    if not (0 <= row < height and 0 <= col < width):
        raise ValueError(f'spawn outside heightmap: {x}, {y}')
    return (samples[row * width + col] - 32768) / 128 * meta['z_scale_unreal']

results = []
for spawn in spawns:
    z = sample_at(spawn['x'], spawn['y'])
    delta = z - spawn['ground_z']
    results.append({'label': spawn['label'], 'r16_z_cm': z,
                    'v84_obj_z_cm': spawn['ground_z'], 'delta_cm': round(delta, 4)})
max_delta = max(abs(row['delta_cm']) for row in results)
# v84 uses nearest OBJ vertex, so the R16 equivalent should differ only by quantization.
passed = max_delta <= 1.0
print(json.dumps({'spawn_count': len(results), 'max_abs_delta_cm': max_delta,
                  'height_alignment_pass': passed, 'landscape_collision_pass': False,
                  'spawns': results}, indent=2))
if not passed:
    raise SystemExit('FAIL: R16 and v84 spawn ground heights disagree')
