"""Offline validation of the Rathaus UE5 Landscape height source; no editor/GPU."""
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'ue5/SpandauStrike/SourceData/Rathaus'
meta = json.loads((SOURCE / 'rathaus_dgm1_height_513.json').read_text(encoding='utf-8'))
raw = (SOURCE / 'rathaus_dgm1_height_513.r16').read_bytes()
w, h = meta['width'], meta['height']
assert (w, h) == (513, 513), (w, h)
assert len(raw) == w * h * 2 == meta['bytes'], len(raw)
assert meta['xy_scale_cm_per_vertex'] == 100000 / (w - 1)
assert meta['z_scale_unreal'] == 100
values = struct.unpack('<' + str(w * h) + 'H', raw)

def sample(row, col):
    encoded = values[row * w + col]
    return {'row': row, 'col': col,
            'world_x_cm': -50000 + col * meta['xy_scale_cm_per_vertex'],
            'world_y_cm': -50000 + row * meta['xy_scale_cm_per_vertex'],
            'height_cm': (encoded - 32768) / 128 * meta['z_scale_unreal']}

minimum = (min(values) - 32768) / 128
maximum = (max(values) - 32768) / 128
assert abs(minimum - meta['min_elevation_m']) < 0.02, minimum
assert abs(maximum - meta['max_elevation_m']) < 0.02, maximum
result = {'source': str(SOURCE), 'samples': [sample(r, c) for r, c in
          [(0, 0), (0, 512), (256, 256), (512, 0), (512, 512)]],
          'min_m': minimum, 'max_m': maximum,
          'source_pass': True, 'landscape_collision_pass': False}
print(json.dumps(result, indent=2))
