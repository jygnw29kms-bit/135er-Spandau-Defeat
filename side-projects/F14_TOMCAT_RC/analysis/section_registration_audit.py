"""Audit projected envelopes before registering UPC section candidates.

These are assembly silhouette intersections, never production skin sections.
Run from any directory; inputs and output resolve relative to this file.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def intersections(polygon, x):
    """Half-open edge convention avoids double counting vertices."""
    result = []
    for a, b in zip(polygon, polygon[1:] + polygon[:1]):
        if min(a[0], b[0]) <= x < max(a[0], b[0]):
            t = (x - a[0]) / (b[0] - a[0])
            result.append(a[1] + t * (b[1] - a[1]))
    result.sort()
    if len(result) % 2:
        raise ValueError('Odd intersection count at X=' + str(x))
    return result


def run():
    # Independent geometry checks include an exact vertex and disconnected spans.
    rectangle = [[0, -2], [4, -2], [4, 3], [0, 3]]
    assert intersections(rectangle, 0) == [-2, 3]
    assert intersections(rectangle, 2) == [-2, 3]
    assert intersections(rectangle, 4) == []
    concave = [[0, 0], [3, 0], [3, 1], [1, 1], [1, 2], [3, 2], [3, 3], [0, 3]]
    assert intersections(concave, 2) == [0, 1, 2, 3]
    folder = ROOT / 'cad/fusion/F14TomcatRC'
    reference = json.loads((folder / 'NASA_F14_reference_trace_v06.json').read_text())
    sections = json.loads((ROOT / 'analysis/upc_source_section_candidates_v07.json').read_text())
    c = reference['calibration']
    ax, ay = c['plan_longitudinal_pixel_vector']
    bx, by = c['plan_span_pixel_vector']
    nx, ny = c['plan_nose_pixel']
    det = ax * by - ay * bx
    length = c['airframe_length_model_mm']
    plan = []
    for x, y in reference['traces']['plan_airframe_without_wings']:
        dx, dy = x - nx, y - ny
        plan.append([(dx * by - dy * bx) / det * length,
                     -(ax * dy - ay * dx) / det * c['span_model_mm']])
    side_name = next(n for n in reference['traces'] if n.startswith('side_') and n != 'side_vertical_tail')
    x0, x1 = c['side_length_dimension_pixels']
    zscale = c['vertical_tail_above_waterline_mm'] / (c['side_waterline_pixel_y'] - c['side_tail_top_pixel_y'])
    side = [[(x - x0) * length / (x1 - x0), (c['side_waterline_pixel_y'] - y) * zscale]
            for x, y in reference['traces'][side_name]]
    rows = []
    for section in sections['profiles']:
        # Fraction registration preserves this NASA view's independent length.
        # Do not mix production inch scale with the wind-tunnel raster length.
        x = section['station_fraction_candidate'] * length
        yp, zs = intersections(plan, x), intersections(side, x)
        if not yp or not zs:
            raise ValueError('Missing projected envelope for ' + section['name'])
        outline = section['common_axis_width_normalized_outline']
        ys = [p[0] for p in outline]
        heights = [p[1] for p in outline]
        ratio = (max(heights) - min(heights)) / (max(ys) - min(ys))
        width, height = yp[-1] - yp[0], zs[-1] - zs[0]
        candidate = None
        if section['name'] in ('A', 'B'):
            # Diagnostic isotropic fit: preserve section shape, measure mismatch.
            # Never stretch height independently to force a false agreement.
            factor = width / (max(ys) - min(ys))
            yc = (yp[0] + yp[-1]) / 2 - factor * (min(ys) + max(ys)) / 2
            zc = (zs[0] + zs[-1]) / 2 - factor * (min(heights) + max(heights)) / 2
            candidate = dict(status='FRONT_SECTION_ISOTROPIC_FIT_CANDIDATE',
                             points_xyz_mm=[[x, yc + factor * y, zc + factor * z]
                                            for y, z in outline],
                             height_mismatch_mm=ratio * width - height,
                             source_section_axis_in_nasa_frame_mm=[yc, zc],
                             independent_vertical_stretch_applied=False,
                             production_registration_verified=False)
        rows.append(dict(section=section['name'], nasa_view_candidate_x_mm=x,
                         projected_y_intersections_mm=yp, projected_z_intersections_mm=zs,
                         assembly_projected_width_mm=width, assembly_projected_height_mm=height,
                         section_contour_height_to_width=ratio,
                         assembly_height_to_width=height / width,
                         diagnostic_candidate=candidate, fitting_permitted=False,
                         blocking_reasons=['Unverified station pairing between source views',
                                           'Plan assembly can include glove/stabilator projections',
                                           'Side assembly can include canopy/ventral-fin projections',
                                           'Source section axis is not a verified aircraft waterline'] +
                                           (['Individual nacelle cannot be scaled to full assembly width']
                                            if section['name'].startswith('F_') else [])))
    output = dict(status='PROJECTED_ENVELOPE_DIAGNOSTIC_ONLY',
                  coordinate_frame='NASA v06 nose X=0, raster waterline Z=0; not aircraft WL',
                  geometry_checks='PASS: rectangle, vertex convention, disconnected intervals',
                  source_length_mm=length, digitization_uncertainty_pixels=reference['uncertainty_pixels'],
                  uncertainty_note='No certified envelope tolerance; horizontal station uncertainty and contour slopes must also be propagated.',
                  production_loft_allowed=False, profiles=rows)
    target = ROOT / 'analysis/section_registration_audit_v09.json'
    target.write_text(json.dumps(output, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': output['status'], 'profiles': len(rows),
                      'checks': output['geometry_checks'], 'output': str(target)}))


if __name__ == '__main__':
    run()
