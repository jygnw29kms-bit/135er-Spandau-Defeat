"""Conditional endpoint clearance budget, not a measured source-error model."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def clearance_budget(radius, boundary_error, axis_error, housing_radius, skin, service):
    # Distance to a boundary is 1-Lipschitz under positional perturbations.
    return radius - boundary_error - axis_error - housing_radius - skin - service


def run():
    assert abs(clearance_budget(30, 1, 2, 26, .8, .2)) < 1e-12
    assert abs(clearance_budget(30, 0, 0, 26, .8, 1) - 2.2) < 1e-12
    source = json.loads((ROOT / 'edf_tilted_axis_sensitivity_v18.json').read_text())
    results = []
    for config in source['configurations']:
        radius = config['minimum_endpoint_cylinder_diameter_mm'] / 2
        results.append({
            'configuration': config['configuration'],
            'combined_boundary_and_axis_error_budget_mm_by_radial_service': [
                {'radial_service_mm': service,
                 'maximum_combined_error_mm': clearance_budget(radius, 0, 0, 26, .8, service),
                 'nominal_endpoint_fit': clearance_budget(radius, 0, 0, 26, .8, service) >= 0}
                for service in [0, .5, 1, 1.5, 3]
            ],
            'margin_for_1mm_service_by_combined_error': [
                {'combined_error_mm': error,
                 'remaining_margin_mm': clearance_budget(radius, error, 0, 26, .8, 1)}
                for error in [0, .25, .5, 1, 2]
            ]
        })
    output = {
        'status': 'CONDITIONAL_ENDPOINT_ERROR_BUDGET_ONLY',
        'method': 'Subtract bounded boundary and axis positional errors from minimum perpendicular radius',
        'checks': 'PASS: additive error budget and zero-error case',
        'source_error_measured': False,
        'axis_error_measured': False,
        'metric_scale_error_included': False,
        'skin_thickness_error_included': False,
        'intermediate_clearance_verified': False,
        'installation_release': False,
        'configurations': results,
        'limitations': ['Error values are sensitivities, not measured tolerances',
                        'Only existing provisional E/F endpoint contours are assessed',
                        'A positive budget is conditional on bounded errors and unchanged topology',
                        'Native loft, full axial envelope and actual hardware remain unverified']
    }
    (ROOT / 'edf_clearance_uncertainty_v20.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(results))


if __name__ == '__main__':
    run()
