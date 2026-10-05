"""Constant twin-axis disk clearance at E/F in a candidate shared side frame."""
import json
from pathlib import Path
from aft_edf_section_packaging import disk_radius

ROOT=Path(__file__).resolve().parents[1]


def run():
    folder=ROOT/'analysis'
    original=json.loads((folder/'upc_source_section_candidates_v07.json').read_text())
    de=json.loads((folder/'upc_DE_registration_v12.json').read_text())
    f_shape=json.loads((folder/'upc_F_connected_section_v11.json').read_text())
    f_fit=json.loads((folder/'upc_F_registration_v12.json').read_text())
    scale=868.496683861459/(1048*2113/1344)
    datum_pixel=2800.0  # Arbitrary common display-frame translation, not aircraft WL.
    sections=[]
    for name in ['E','F']:
        source=next(p for p in original['profiles'] if p['name']==('F_R' if name=='F' else name))
        polygon=f_shape['pixel_outline'] if name=='F' else source['pixel_outline']
        if name=='E':
            fit=next(p for p in de['sections'] if p['name']=='E')
            factor=fit['isotropic_multiplier']; vertical=fit['candidate_section_axis_side_pixel_y']
        else:
            factor=f_fit['isotropic_section_width_multiplier']
            vertical=f_fit['registered_candidate_section_axis_side_pixel_y']
        cx,cy=source['source_section_axis_pixel']
        transformed=[((y-cx)*factor*scale,
                      (datum_pixel-vertical-(z-cy)*factor)*scale) for y,z in polygon]
        sections.append(dict(name=name,polygon_yz_mm=transformed,
                             candidate_x_mm=source['station_fraction_candidate']*868.496683861459))
    best=(0,None,None)
    for index_y in range(140,341):  # 35 to 85 mm, 0.25 mm spacing.
        y=index_y/4
        for index_z in range(-140,81):  # -35 to +20 mm.
            z=index_z/4
            radius=min([disk_radius((sign*y,z),s['polygon_yz_mm'])
                        for s in sections for sign in (-1,1)]+[y])
            if radius>best[0]: best=(radius,y,z)
    radius,y,z=best
    checks=[]
    for section in sections:
        checks.append(dict(section=section['name'],
                           left_radius_mm=disk_radius((-y,z),section['polygon_yz_mm']),
                           right_radius_mm=disk_radius((y,z),section['polygon_yz_mm'])))
    output=dict(status='CANDIDATE_SHARED_FRAME_HORIZONTAL_EDF_AXIS_SCREEN',
                arbitrary_vertical_frame_side_pixel_y=datum_pixel,
                metric_scale_assumed_mm_per_plan_pixel=scale,
                symmetric_constant_centers_yz_mm=[[-y,z],[y,z]],
                sampled_common_radius_mm=radius,sampled_common_diameter_mm=2*radius,
                maximum_radial_service_for_52mm_housing_and_0p8_skin_mm=radius-26-0.8,
                grid_step_mm=0.25,search_y_offset_mm=[35,85],search_z_mm=[-35,20],
                per_section_clearance=checks,sections=sections,
                aircraft_WL_datum_verified=False,metric_source_registration_verified=False,
                continuous_cylinder_clearance_verified=False,actual_hardware_verified=False,
                native_cad_created=False,installation_release=False,
                limitations=['Common frame derives from provisional source-image registrations',
                             'Only endpoint planes E/F are checked, not intermediate skin',
                             'Constant horizontal axes only; no tilted/splayed cylinder evaluated',
                             'Sampled grid is not a global-optimum proof'])
    (folder/'edf_common_axis_sections_v17.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({'common_diameter_mm':2*radius,'centers':output['symmetric_constant_centers_yz_mm'],
                      'maximum_radial_allowance_mm':radius-26-0.8,'continuous_fit_verified':False}))


if __name__=='__main__': run()
