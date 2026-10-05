"""Common A/B battery axis and axial coverage limits; no continuous fit proof."""
import json
from pathlib import Path
from battery_section_fit import rectangle_gap

ROOT=Path(__file__).resolve().parents[1]


def center_interval_covering_planes(x0,x1,length):
    return [x1-length/2,x0+length/2]


def run():
    assert center_interval_covering_planes(0,100,120)==[40,60]
    data=json.loads((ROOT/'analysis/section_registration_audit_v09.json').read_text())
    hw=json.loads((ROOT/'hardware/component_envelopes.json').read_text())['battery_4s']
    sections=data['profiles'][:2]
    polygons=[[[p[1],p[2]] for p in s['diagnostic_candidate']['points_xyz_mm']] for s in sections]
    # Candidate same raster reference frame, not a verified aircraft waterline.
    ymin=max(min(p[0] for p in poly) for poly in polygons)+hw['width_mm']/2
    ymax=min(max(p[0] for p in poly) for poly in polygons)-hw['width_mm']/2
    zmin=max(min(p[1] for p in poly) for poly in polygons)+hw['height_mm']/2
    zmax=min(max(p[1] for p in poly) for poly in polygons)-hw['height_mm']/2
    best=(-1,None,None)
    for iy in range(int(ymin*2)-1,int(ymax*2)+2):
        for iz in range(int(zmin*2)-1,int(zmax*2)+2):
            center=[iy/2,iz/2]
            gaps=[rectangle_gap(center,hw['width_mm'],hw['height_mm'],p) for p in polygons]
            if all(g is not None for g in gaps) and min(gaps)>best[0]: best=(min(gaps),center,gaps)
    x0,x1=[s['nasa_view_candidate_x_mm'] for s in sections]
    interval=center_interval_covering_planes(x0,x1,hw['length_mm'])
    out=dict(status='COMMON_FRONT_SECTION_BATTERY_AXIS_SENSITIVITY',
             checks='PASS: independent axial coverage interval',grid_step_mm=.5,
             sampled_common_center_yz_mm=best[1],sampled_min_boundary_gap_mm=best[0],
             per_section_gap_mm=best[2],candidate_station_x_mm=[x0,x1],
             stationary_center_interval_covering_both_planes_mm=interval,
             interval_width_mm=max(0,interval[1]-interval[0]),
             target_adjustment_travel_mm=hw['longitudinal_adjustment_mm'],
             both_planes_remain_under_battery_for_full_travel=(interval[1]-interval[0]>=hw['longitudinal_adjustment_mm']),
             minimum_axial_body_region_for_length_plus_travel_mm=hw['length_mm']+hw['longitudinal_adjustment_mm'],
             metric_frame_verified=False,continuous_body_fit_verified=False,
             tray_strap_hatch_cg_verified=False,installation_release=False,
             limitations=['Only two candidate section planes constrain this screen',
                          'Coverage of a plane is not clearance of the intervening or outboard body',
                          'Failure to cover both planes during travel does not itself prove a collision',
                          'No metric registration, continuous loft or hatch access verified'])
    (ROOT/'analysis/battery_common_axis_v26.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out))


if __name__=='__main__': run()
