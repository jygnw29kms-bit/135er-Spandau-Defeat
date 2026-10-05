"""Local rectangular battery screen using provisional original A/B sections."""
import json
from pathlib import Path
from validate_source_contours import edges, strictly_inside, contact
from source_wing_internal_fit import distance

ROOT=Path(__file__).resolve().parents[1]


def rectangle_gap(center, width, height, polygon):
    y,z=center
    rect=[[y-width/2,z-height/2],[y+width/2,z-height/2],
          [y+width/2,z+height/2],[y-width/2,z+height/2]]
    if not all(strictly_inside(p,polygon) for p in rect): return None
    if any(contact(a,b,c,d) for a,b in edges(rect) for c,d in edges(polygon)): return None
    return min(min(distance(a,c,d),distance(b,c,d),distance(c,a,b),distance(d,a,b))
               for a,b in edges(rect) for c,d in edges(polygon))


def run():
    box=[[-10,-10],[10,-10],[10,10],[-10,10]]
    assert abs(rectangle_gap((0,0),12,8,box)-4)<1e-12
    assert rectangle_gap((5,0),12,8,box) is None
    notched=[[-10,-10],[10,-10],[10,10],[2,10],[2,-2],[-2,-2],[-2,10],[-10,10]]
    assert rectangle_gap((0,0),12,8,notched) is None
    data=json.loads((ROOT/'analysis/section_registration_audit_v09.json').read_text())
    battery=json.loads((ROOT/'hardware/component_envelopes.json').read_text())['battery_4s']
    results=[]
    for section in data['profiles'][:2]:
        poly=[[p[1],p[2]] for p in section['diagnostic_candidate']['points_xyz_mm']]
        best=(-1,None)
        for iy in range(int(min(p[0] for p in poly)*2),int(max(p[0] for p in poly)*2)+1):
            y=iy/2
            # Reject impossible lateral centers before the more expensive edge checks.
            if y-battery['width_mm']/2<min(p[0] for p in poly) or y+battery['width_mm']/2>max(p[0] for p in poly): continue
            for iz in range(int(min(p[1] for p in poly)*2),int(max(p[1] for p in poly)*2)+1):
                z=iz/2
                gap=rectangle_gap((y,z),battery['width_mm'],battery['height_mm'],poly)
                if gap is not None and gap>best[0]: best=(gap,[y,z])
        results.append(dict(section=section['section'],candidate_x_mm=section['nasa_view_candidate_x_mm'],
                            sampled_center_yz_mm=best[1],sampled_boundary_gap_mm=best[0],
                            passes_assumed_0p8_skin_plus_1mm_service=best[0]>=1.8))
    out=dict(status='LOCAL_CANDIDATE_BATTERY_SECTION_SCREEN',checks='PASS: rectangle gap, protrusion and concave edge-crossing rejection',
             battery_width_height_mm=[battery['width_mm'],battery['height_mm']],grid_step_mm=.5,
             sections=results,metric_source_registration_verified=False,
             full_155mm_length_fit_verified=False,adjustment_travel_verified=False,
             tray_strap_hatch_cg_verified=False,native_cad_created=False,installation_release=False)
    (ROOT/'analysis/battery_section_fit_v25.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(results))


if __name__=='__main__': run()
