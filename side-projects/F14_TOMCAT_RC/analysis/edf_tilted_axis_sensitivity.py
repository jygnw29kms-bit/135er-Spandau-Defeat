"""Endpoint cylinder clearance accounting for oblique plane intersections."""
import json
import math
from pathlib import Path
import numpy as np
from aft_edf_section_packaging import disk_radius

ROOT=Path(__file__).resolve().parents[1]


def projection_metric(direction):
    u=np.asarray(direction,dtype=float)
    u=u/np.linalg.norm(u)
    if abs(u[0])<1e-6: raise ValueError('Axis nearly parallel to section plane')
    metric=np.eye(2)-np.outer(u[1:],u[1:])
    # A.T A = metric; distances after A are perpendicular-to-axis distances.
    return np.linalg.cholesky(metric).T, u


def oblique_radius(polygon, center, direction):
    transform,u=projection_metric(direction)
    projected=[tuple(transform@np.asarray(p)) for p in polygon]
    return disk_radius(tuple(transform@np.asarray(center)),projected)


def run():
    horizontal,u=projection_metric([1,0,0])
    assert np.allclose(horizontal,np.eye(2))
    tilt,u=projection_metric([math.cos(math.pi/6),0,math.sin(math.pi/6)])
    assert abs(np.linalg.norm(tilt@np.array([0.,10.]))-10*math.cos(math.pi/6))<1e-12
    folder=ROOT/'analysis'
    frame=json.loads((folder/'edf_common_axis_sections_v17.json').read_text())
    sampled=json.loads((folder/'aft_edf_registered_sections_v16.json').read_text())
    base=json.loads((folder/'upc_source_section_candidates_v07.json').read_text())
    de=json.loads((folder/'upc_DE_registration_v12.json').read_text())
    f=json.loads((folder/'upc_F_registration_v12.json').read_text())
    scale=frame['metric_scale_assumed_mm_per_plan_pixel']; preferred=[]
    for name in ['E','F']:
        source=next(p for p in base['profiles'] if p['name']==('F_R' if name=='F' else name))
        sample=next(p for p in sampled['sections'] if p['section']==name)
        factor=sample['isotropic_source_width_factor']
        vertical=(next(p for p in de['sections'] if p['name']=='E')['candidate_section_axis_side_pixel_y']
                  if name=='E' else f['registered_candidate_section_axis_side_pixel_y'])
        y,z=sample['sampled_symmetric_centers_pixels'][1]
        cx,cz=source['source_section_axis_pixel']
        preferred.append(((y-cx)*factor*scale,(frame['arbitrary_vertical_frame_side_pixel_y']-vertical-(z-cz)*factor)*scale))
    sections=frame['sections']; dx=sections[1]['candidate_x_mm']-sections[0]['candidate_x_mm']
    baseline=tuple(frame['symmetric_constant_centers_yz_mm'][1])
    configurations=[('horizontal',[baseline,baseline]),
                    ('pitch_only',[(baseline[0],preferred[0][1]),(baseline[0],preferred[1][1])]),
                    ('pitch_and_splay',preferred)]
    results=[]
    for name,centers in configurations:
        dy=centers[1][0]-centers[0][0]; dz=centers[1][1]-centers[0][1]
        checks=[]
        for sign in [-1,1]:
            direction=[dx,sign*dy,dz]
            _,unit=projection_metric(direction)
            for st,center in zip(sections,centers):
                radius=oblique_radius(st['polygon_yz_mm'],(sign*center[0],center[1]),direction)
                checks.append(dict(section=st['name'],side=sign,perpendicular_radius_mm=radius,
                                   section_ellipse_major_to_minor_ratio=1/abs(unit[0])))
        minimum=min(c['perpendicular_radius_mm'] for c in checks)
        if name=='horizontal': assert abs(minimum-frame['sampled_common_radius_mm'])<1e-9
        results.append(dict(configuration=name,right_axis_endpoint_yz_mm=centers,
                            pitch_deg=math.degrees(math.atan2(dz,math.hypot(dx,dy))),
                            splay_deg=math.degrees(math.atan2(dy,dx)),
                            minimum_endpoint_cylinder_diameter_mm=2*minimum,
                            provisional_radial_allowance_for_52mm_housing_and_0p8_skin_mm=minimum-26-0.8,
                            per_endpoint=checks))
    output=dict(status='OBLIQUE_CYLINDER_ENDPOINT_SENSITIVITY_ONLY',
                checks='PASS: horizontal metric, 30-degree perpendicular distance, horizontal baseline reproduction',
                method='Projected section metric I - u_yz u_yz^T; oblique cylinder ellipse accounted for',
                configurations=results,
                actual_aircraft_engine_axis_verified=False,intermediate_clearance_verified=False,
                actual_mount_wall_normal_clearance_verified=False,actual_hardware_verified=False,
                native_cad_created=False,installation_release=False,
                limitations=['Axis directions are packaging sensitivities, not original engine alignment',
                             'Only E/F planes checked, using provisional cross-source registrations',
                             'Skin deduction is assumed; true 3D wall-normal clearance remains unverified',
                             'No airflow, thrust-vector, mount, wiring or 81mm housing proof'])
    (folder/'edf_tilted_axis_sensitivity_v18.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps([dict(configuration=r['configuration'],diameter_mm=r['minimum_endpoint_cylinder_diameter_mm'],pitch_deg=r['pitch_deg'],splay_deg=r['splay_deg']) for r in results]))


if __name__=='__main__': run()
