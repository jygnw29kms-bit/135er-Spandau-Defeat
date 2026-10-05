"""D/E/F EDF clearance sensitivity using individual isotropic width fits."""
import json
import math
from pathlib import Path
from aft_edf_section_packaging import disk_radius

ROOT=Path(__file__).resolve().parents[1]


def run():
    folder=ROOT/'analysis'
    base=json.loads((folder/'upc_source_section_candidates_v07.json').read_text())
    corrected_f=json.loads((folder/'upc_F_connected_section_v11.json').read_text())
    de=json.loads((folder/'upc_DE_registration_v12.json').read_text())
    f_fit=json.loads((folder/'upc_F_registration_v12.json').read_text())
    common_scale=868.496683861459/(1048*2113/1344)
    results=[]
    for name in ['D','E','F']:
        source=next(s for s in base['profiles'] if s['name']==('F_R' if name=='F' else name))
        polygon=corrected_f['pixel_outline'] if name=='F' else source['pixel_outline']
        axis=source['source_section_axis_pixel'][0]
        fit=(f_fit['isotropic_section_width_multiplier'] if name=='F' else
             next(s for s in de['sections'] if s['name']==name)['isotropic_multiplier'])
        half=(max(p[0] for p in polygon)-min(p[0] for p in polygon))/2
        lo,hi=int(min(p[1] for p in polygon)),math.ceil(max(p[1] for p in polygon))
        best=(0,None,None)
        for offset in range(math.floor(half*0.35),math.ceil(half*0.85)+1):
            for z in range(lo,hi+1):
                left,right=(axis-offset,z),(axis+offset,z)
                radius=min(disk_radius(left,polygon),disk_radius(right,polygon),offset)
                if radius>best[0]: best=(radius,left,right)
        diameter=2*best[0]*common_scale*fit
        alternatives=[]
        for radial in [0.5,1.0,1.5,3.0]:
            required=52+2*(0.8+radial)
            alternatives.append(dict(assumed_radial_service_mm=radial,
                                     required_outer_diameter_mm=required,
                                     diameter_margin_mm=diameter-required,
                                     provisional_local_fit=diameter>=required))
        results.append(dict(section=name,candidate_model_x_mm=source['station_fraction_candidate']*868.496683861459,
                            isotropic_source_width_factor=fit,
                            sampled_symmetric_centers_pixels=[best[1],best[2]],
                            sampled_disk_radius_pixels=best[0],
                            available_disk_diameter_mm=diameter,
                            maximum_radial_service_for_52mm_housing_and_0p8_skin_mm=(diameter-52)/2-0.8,
                            clearance_sensitivity=alternatives))
    output=dict(status='ISOTROPIC_REGISTERED_SECTION_PACKAGING_SENSITIVITY',
                common_scale_assumed_mm_per_plan_pixel=common_scale,
                grid_step_source_pixels=1,offset_search_fraction_of_half_width=[0.35,0.85],
                housing_assumed_diameter_mm=52,housing_assumed_length_mm=75,
                assumed_axial_service_each_end_mm=3,required_axial_envelope_mm=81,
                individual_section_scale_fits_used=True,
                common_vertical_axes_verified=False,metric_station_registration_verified=False,
                continuous_81mm_clearance_verified=False,actual_edf_dimensions_verified=False,
                native_installation_created=False,installation_release=False,
                source_station_gaps_mm=[results[i+1]['candidate_model_x_mm']-results[i]['candidate_model_x_mm'] for i in range(2)],
                limitations=['Independent optimal section centers cannot define a straight installed EDF axis',
                             'One-pixel sampled search is not a global maximum proof',
                             'Manual source outlines and cross-source length pairing remain unverified',
                             'Radial clearance alternatives are sensitivities, not selected mount tolerances',
                             'V15 used direct raw-pixel scale; these results include separately drawn section width factors'],
                sections=results)
    (folder/'aft_edf_registered_sections_v16.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({'sections':[{k:r[k] for k in ['section','available_disk_diameter_mm','maximum_radial_service_for_52mm_housing_and_0p8_skin_mm']} for r in results],
                      'continuous_axial_fit_verified':False}))


if __name__=='__main__': run()
