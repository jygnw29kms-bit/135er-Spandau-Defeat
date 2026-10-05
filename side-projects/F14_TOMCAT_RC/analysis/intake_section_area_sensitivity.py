"""Source C duct-section area versus hypothetical EDF annular areas."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def area(points):
    return abs(sum(a[0]*b[1]-b[0]*a[1]
                   for a,b in zip(points, points[1:]+points[:1]))) / 2


def run():
    rectangle = [[0,0],[4,0],[4,3],[0,3]]
    assert area(rectangle) == area(rectangle[::-1]) == 12
    assert area([[x+100,y-50] for x,y in rectangle]) == 12
    source = json.loads((ROOT/'upc_C_intake_topology_v13.json').read_text())
    polygons = source['inner_opening_pixel_loops']
    areas = [area(p) for p in polygons]
    assert len(areas) == 2 and min(areas) > 0
    rows = []
    for hub in [15,20,25]:
        fan_area = math.pi/4*(50**2-hub**2)
        for ratio in [.8,1,1.2]:
            rows.append({
                'assumed_rotor_diameter_mm': 50,
                'assumed_hub_diameter_mm': hub,
                'comparison_area_ratio': ratio,
                'one_fan_annular_area_mm2': fan_area,
                'required_section_area_mm2_per_duct': fan_area*ratio,
                'minimum_isotropic_section_scale_mm_per_source_pixel': [
                    math.sqrt(fan_area*ratio/a) for a in areas]
            })
    result = {
        'status': 'UNREGISTERED_SOURCE_C_SECTION_AREA_SENSITIVITY',
        'source_image_sha256': source['source_image_sha256'],
        'source_opening_areas_pixel2': areas,
        'source_section_area_asymmetry_percent': 100*abs(areas[0]-areas[1])/max(areas),
        'checks': 'PASS: rectangle, winding reversal, translation invariance, positive two-opening areas',
        'metric_section_scale_selected': False,
        'actual_rotor_hub_dimensions_verified': False,
        'flow_capacity_verified': False,
        'installation_release': False,
        'sensitivities': rows,
        'limitations': ['C inner loops are manual source duct-section candidates, not verified intake mouths',
                        'Area ratios and hub sizes are comparisons, not design recommendations',
                        'Station pairing and isotropic metric scale remain unverified',
                        'No boundary layer, grille, duct losses or minimum area along full duct evaluated',
                        'Area agreement cannot prove airflow, thrust or EDF fit']
    }
    (ROOT/'intake_section_area_sensitivity_v22.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'source_areas_pixel2':areas,'comparisons':rows}))


if __name__ == '__main__':
    run()
