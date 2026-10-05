"""Twin circular EDF housing sensitivity at source F, not a 3D installation."""
import json
import math
from pathlib import Path
from validate_source_contours import strictly_inside, edges
from source_wing_internal_fit import distance

ROOT=Path(__file__).resolve().parents[1]


def disk_radius(center, polygon):
    if not strictly_inside(center,polygon): return 0.0
    return min(distance(center,a,b) for a,b in edges(polygon))


def run():
    box=[[0,0],[10,0],[10,10],[0,10]]
    assert abs(disk_radius((5,5),box)-5)<1e-12
    assert disk_radius((11,5),box)==0
    section=json.loads((ROOT/'analysis/upc_F_connected_section_v11.json').read_text())
    envelope=json.loads((ROOT/'hardware/component_envelopes.json').read_text())['edf_50mm']
    polygon=section['pixel_outline']; axis=section['source_section_axis_pixel'][0]
    best=(0,None,None)
    for offset in range(110,156):
        for z in range(2550,2631):
            left,right=(axis-offset,z),(axis+offset,z)
            radius=min(disk_radius(left,polygon),disk_radius(right,polygon),offset)
            if radius>best[0]: best=(radius,left,right)
    # Metric conversion is explicitly a sensitivity assumption.
    source_length_pixels=1048*2113/1344
    scale=868.496683861459/source_length_pixels
    skin=0.8
    clearance=envelope['service_clearance_mm']  # assume radial, document convention
    required=envelope['diameter_mm']+2*(skin+clearance)
    available=2*best[0]*scale
    output=dict(status='UNVERIFIED_METRIC_F_SECTION_EDF_PACKAGING',
                source_image_sha256=section['source_image_sha256'],
                sampled_symmetric_centers_native_pixels=[best[1],best[2]],
                sampled_max_common_disk_radius_pixels=best[0],
                search_grid=dict(offset_pixels=[110,155],vertical_pixels=[2550,2630],step_pixels=1),
                assumed_scale_mm_per_native_pixel=scale,
                assumed_scale_basis='NASA 868.4967 mm length / UPC candidate nose-tail pixel distance; cross-source pairing unverified',
                housing_diameter_mm=envelope['diameter_mm'],skin_normal_mm=skin,
                service_clearance_assumed_radial_mm=clearance,
                required_outer_disk_diameter_mm=required,
                available_sampled_disk_diameter_mm=available,
                provisional_diameter_margin_mm=available-required,
                provisional_local_fit=available>=required,
                required_service_length_mm=envelope['length_mm']+2*clearance,
                rotor_nominal_full_disk_area_mm2=math.pi*50**2/4,
                source_station_metric_registration_verified=False,
                actual_edf_dimensions_verified=False,axial_75mm_housing_fit_verified=False,
                duct_path_verified=False,native_cad_created=False,installation_release=False,
                limitations=['Grid search is not a global optimum proof',
                             'Manual source contour accuracy and cross-source scale remain unverified',
                             'No hub subtraction, intake/outlet area ratio, airflow or thrust calculation',
                             'A single source section cannot prove clearance over the EDF housing length'],
                checks='PASS: square disk radius and outside-point rejection; symmetric disk separation included')
    (ROOT/'analysis/aft_edf_section_packaging_v15.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({'available_sampled_diameter_mm':available,'required_mm':required,
                      'provisional_margin_mm':available-required,'provisional_local_fit':available>=required}))


if __name__=='__main__': run()
