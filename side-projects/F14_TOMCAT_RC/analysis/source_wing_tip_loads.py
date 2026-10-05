"""Sensitivity study for the 43 mm panel outside the candidate carbon spar.

Assigned wing-side force is conservative but its span distribution is assumed.
This is equilibrium integration, not aerodynamic simulation or print strength.
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def interpolate(stations, y):
    for a, b in zip(stations, stations[1:]):
        if a[0] <= y <= b[0]:
            return a[1] + (b[1] - a[1]) * (y - a[0]) / (b[0] - a[0])
    raise ValueError('Outside defining wing panel')


def integrate(stations, cut, mode, count):
    y0, y1 = stations[0][0], stations[-1][0]
    step = (y1 - y0) / count
    total = tail = moment = root_moment = 0.0
    # Split at the termination so partial integration has no grid-edge error.
    for lo, hi, outside in [(y0, cut, False), (cut, y1, True)]:
        n = max(1, math.ceil((hi - lo) / step))
        dy = (hi - lo) / n
        for i in range(n):
            y = lo + (i + 0.5) * dy
            weight = {'uniform': lambda: 1.0,
                      'area_proportional': lambda: interpolate(stations, y),
                      'elliptic_full_semispan': lambda: math.sqrt(max(0, 1 - (y / y1) ** 2))}[mode]()
            load = weight * dy
            total += load
            root_moment += load * (y - y0)
            if outside:
                tail += load
                moment += load * (y - cut)
    return tail / total, moment / total, root_moment / total


def run():
    fit = json.loads((ROOT / 'analysis/source_wing_internal_fit_v09.json').read_text())
    stations = [(s['model_y_mm'], s['chord_mm']) for s in fit['sections']]
    cut = stations[-2][0]
    span, outer = stations[-1][0] - stations[0][0], stations[-1][0] - cut
    f, m, root_arm = integrate(stations, cut, 'uniform', 4096)
    assert abs(f - outer / span) < 1e-10
    assert abs(m - outer ** 2 / (2 * span)) < 1e-9
    assert abs(root_arm - span / 2) < 1e-9
    total_panel_area = sum((b[0] - a[0]) * (a[1] + b[1]) / 2
                           for a, b in zip(stations, stations[1:]))
    cases = []
    for mode in ['uniform', 'area_proportional', 'elliptic_full_semispan']:
        coarse = integrate(stations, cut, mode, 4096)
        fine = integrate(stations, cut, mode, 8192)
        if abs(fine[1] - coarse[1]) > 0.01:
            raise RuntimeError('Moment-arm convergence failed')
        for label, load in [('symmetric_6g', 1.05 * 9.80665 * 6 / 2),
                            ('symmetric_8g', 1.05 * 9.80665 * 8 / 2),
                            ('asymmetric_8g_high_side', 1.05 * 9.80665 * 8 * 0.70)]:
            cases.append(dict(distribution=mode, case=label, assigned_panel_force_N=load,
                              outer_panel_shear_N=load * fine[0],
                              termination_bending_moment_Nm=load * fine[1] / 1000,
                              first_defining_section_moment_Nm=load * fine[2] / 1000,
                              outer_force_fraction=fine[0],
                              refinement_moment_arm_difference_mm=abs(fine[1] - coarse[1])))
    highest = 1.05 * 9.80665 * 8 * 0.70
    output = dict(status='ASSUMED_LOAD_DISTRIBUTION_SENSITIVITY',
                  checks='PASS: uniform force/moment closed forms; 4096/8192 interval refinement',
                  defined_panel_span_mm=span, outer_panel_span_mm=outer,
                  one_defined_panel_plan_area_mm2=total_panel_area,
                  absolute_nonnegative_load_bound=dict(
                      assumption='Entire high-side 8g force concentrated at outer tip',
                      outer_shear_N=highest, termination_moment_Nm=highest * outer / 1000),
                  cases=cases,
                  limitations=['No aerodynamic lift distribution established',
                               'Inboard glove/body lift omitted; whole wing-side force assigned to defining panel',
                               'Source-root moment excludes unknown pivot-to-first-section arm',
                               'Nonnegative-load bound excludes self-equilibrated loads and torsion',
                               'No carbon joint, skin, printed rib, bond or buckling capacity checked'],
                  print_tip_strength_verified=False, physical_proof_test_required=True)
    target = ROOT / 'analysis/source_wing_tip_loads_v10.json'
    target.write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps({'checks': output['checks'], 'outer_span_mm': outer,
                      'worst_nonnegative_tip_moment_Nm': highest * outer / 1000,
                      'area_proportional_high_side': cases[5]}))


if __name__ == '__main__':
    run()
