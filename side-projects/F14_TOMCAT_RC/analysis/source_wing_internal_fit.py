"""Local spar packaging in original Grumman defining sections, not FEA.

Skin and clearance are normal offsets of the digitized section boundaries.
Local fit does not establish a straight tube path or fit between loft sections.
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def interp(rows, x, column):
    for a, b in zip(rows, rows[1:]):
        if a[0] <= x <= b[0]:
            return a[column] + (b[column] - a[column]) * (x - a[0]) / (b[0] - a[0])
    raise ValueError('Outside source chord')


def distance(p, a, b):
    dx, dz = b[0] - a[0], b[1] - a[1]
    den = dx * dx + dz * dz
    if den == 0:
        return math.dist(p, a)
    t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dz) / den))
    return math.dist(p, (a[0] + t * dx, a[1] + t * dz))


def clearance_diameter(rows, xc, offset):
    z = (interp(rows, xc, 1) + interp(rows, xc, 2)) / 2
    polygon = [(x, u) for x, u, l in rows] + [(x, l) for x, u, l in rows[::-1]]
    closest = min(distance((xc, z), a, b) for a, b in zip(polygon, polygon[1:] + polygon[:1]))
    return max(0, 2 * (closest - offset)), z


def cap_envelope(rows, x0, x1, offset):
    top, bottom = [], []
    for a, b in zip(rows, rows[1:]):
        lo, hi = max(x0, a[0]), min(x1, b[0])
        if lo > hi:
            continue
        for column, collection, sign in [(1, top, -1), (2, bottom, 1)]:
            slope = (b[column] - a[column]) / (b[0] - a[0])
            for x in (lo, hi):
                z = a[column] + slope * (x - a[0])
                collection.append(z + sign * offset * math.sqrt(1 + slope * slope))
    if not top or not bottom:
        raise ValueError('Cap outside source section')
    return min(top), max(bottom)


def run():
    assert abs(distance((1, 2), (0, 0), (2, 0)) - 2) < 1e-12
    assert abs(distance((3, 0), (0, 0), (2, 0)) - 1) < 1e-12
    box = [[0, 5, -5], [10, 5, -5]]
    assert cap_envelope(box, 3, 7, 1) == (4, -4)
    assert abs(clearance_diameter(box, 5, 1)[0] - 8) < 1e-12
    source = json.loads((ROOT / 'cad/fusion/F14TomcatRC/NASA_F14_basic_wing_v08.json').read_text())
    scale = 900 / (2 * source['sections'][-1]['wbl_in'])
    sections = source['sections']
    y0, y1 = sections[0]['wbl_in'], sections[-1]['wbl_in']
    result = []
    for st in sections:
        chord = (st['trailing_edge_fs_in'] - st['leading_edge_fs_in']) * scale
        rows = [[x * chord, u * chord, l * chord] for x, u, l in st['ordinates_xc_upper_lower']]
        fraction = (st['wbl_in'] - y0) / (y1 - y0)
        width = 16 + (8 - 16) * fraction
        x = 0.30 * chord
        top, bottom = cap_envelope(rows, x - width / 2, x + width / 2, 1.0)
        diameter, center_z = clearance_diameter(rows, x, 1.0)
        candidates = [(clearance_diameter(rows, chord * (0.15 + i * 0.005), 1.0)[0],
                       0.15 + i * 0.005) for i in range(91)]
        best, best_xc = max(candidates)
        web_gap = top - bottom - 2 * 1.0
        alternatives = []
        for tip_width in (8, 6, 4):
            local_width = 16 + (tip_width - 16) * fraction
            for cap_thickness in (1.0, 0.8):
                for chord_fraction in (0.30, 0.35, 0.40):
                    center = chord_fraction * chord
                    alt_top, alt_bottom = cap_envelope(rows, center - local_width / 2,
                                                      center + local_width / 2, 1.0)
                    gap = alt_top - alt_bottom - 2 * cap_thickness
                    alternatives.append(dict(tip_width_mm=tip_width, local_width_mm=local_width,
                                             cap_thickness_mm=cap_thickness,
                                             chord_fraction=chord_fraction, web_gap_mm=gap,
                                             local_packaging_pass=gap >= 0.8))
        result.append(dict(wbl_in=st['wbl_in'], model_y_mm=st['wbl_in'] * scale,
                           chord_mm=chord, spar_fraction_chord=0.30,
                           local_circle_center_fs_in=st['leading_edge_fs_in'] + 0.30 * chord / scale,
                           local_circle_center_wl_in=st['reference_vertical_wl_in'] + center_z / scale,
                           local_max_tube_od_at_30pct_mm=diameter,
                           stock_tube_local_fit={str(od): od <= diameter for od in (4, 6, 8, 10, 12)},
                           searched_max_tube_od_mm=best, searched_max_tube_xc=best_xc,
                           cap_width_mm=width, cap_top_outer_relative_wl_mm=top,
                           cap_bottom_outer_relative_wl_mm=bottom,
                           remaining_web_height_mm=web_gap,
                           web_height_at_least_0p8mm=web_gap >= 0.8,
                           alternative_cap_packaging=alternatives))
    continuous_candidates = []
    for candidate in result[0]['alternative_cap_packaging']:
        matches = [next(c for c in st['alternative_cap_packaging']
                        if all(c[k] == candidate[k] for k in ('tip_width_mm', 'cap_thickness_mm', 'chord_fraction')))
                   for st in result]
        continuous_candidates.append(dict(tip_width_mm=candidate['tip_width_mm'],
                                           cap_thickness_mm=candidate['cap_thickness_mm'],
                                           chord_fraction=candidate['chord_fraction'],
                                           minimum_defining_station_web_gap_mm=min(c['web_gap_mm'] for c in matches),
                                           all_defining_stations_fit=all(c['local_packaging_pass'] for c in matches)))
    output = dict(status='SOURCE_SECTION_PACKAGING_SCREEN_ONLY',
                  source_sha256=source['source_sha256'],
                  assumptions=dict(skin_normal_mm=0.8, assembly_clearance_normal_mm=0.2,
                                   cap_thickness_mm=1.0, cap_width_root_mm=16, cap_width_tip_mm=8),
                  checks='PASS: segment normal distance, endpoint distance, rectangular cap and disk fit',
                  continuous_span_clearance_verified=False,
                  straight_tube_alignment_verified=False, structural_capacity_verified=False,
                  native_internal_structure_created=False,
                  limitations=['Boundary is source polygon; Fusion interpolation requires separate validation',
                               'Mid-ordinate circle centers are not globally optimal disk centers',
                               'Local circles in Y-normal sections do not prove swept tube clearance',
                               'Caps require bend, joint, bond, torsion, buckling and load-path design'],
                  cap_option_summary=continuous_candidates, sections=result)
    output['baseline_terminated_spar_candidate'] = dict(
        last_defining_wbl_in=sections[-2]['wbl_in'],
        last_defining_model_y_mm=result[-2]['model_y_mm'],
        unsupported_tip_span_mm=result[-1]['model_y_mm'] - result[-2]['model_y_mm'],
        all_retained_defining_sections_fit=all(r['web_height_at_least_0p8mm'] for r in result[:-1]),
        minimum_retained_web_height_mm=min(r['remaining_web_height_mm'] for r in result[:-1]),
        load_transfer_and_printed_tip_strength_verified=False,
        decision='Candidate only: terminate before thin tip; design and verify outer-panel load transfer')
    (ROOT / 'analysis/source_wing_internal_fit_v09.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps({'checks': output['checks'], 'tip_tube_od_mm': result[-1]['local_max_tube_od_at_30pct_mm'],
                      'tip_web_gap_mm': result[-1]['remaining_web_height_mm'],
                      'cap_fit_at_all_defining_stations': all(r['web_height_at_least_0p8mm'] for r in result)}))


if __name__ == '__main__':
    run()
