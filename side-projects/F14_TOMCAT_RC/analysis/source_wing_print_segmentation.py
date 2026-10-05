"""P2S envelope planning from defining wing points, not sliced print geometry."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def run():
    source=json.loads((ROOT/'cad/fusion/F14TomcatRC/NASA_F14_basic_wing_v08.json').read_text())
    sections=source['sections']
    factor=900/(2*sections[-1]['wbl_in'])
    split=5  # Original defining WBL 311.15283, preserves audited section plane.
    parts=[]
    for name,subset in [('inner',sections[:split+1]),('outer',sections[split:])]:
        points=[]
        for st in subset:
            chord=st['trailing_edge_fs_in']-st['leading_edge_fs_in']
            for x,u,l in st['ordinates_xc_upper_lower']:
                for z in (u,l):
                    points.append(((st['leading_edge_fs_in']+x*chord)*factor,
                                   st['wbl_in']*factor,
                                   (st['reference_vertical_wl_in']+z*chord)*factor))
        low=[min(p[i] for p in points) for i in range(3)]
        high=[max(p[i] for p in points) for i in range(3)]
        size=[b-a for a,b in zip(low,high)]
        # Rotate +90 deg about model X: source Y is build Z; source Z is bed Y.
        footprint=[size[0]+16,size[2]+16]
        parts.append(dict(name=name,first_wbl_in=subset[0]['wbl_in'],last_wbl_in=subset[-1]['wbl_in'],
                          defining_point_bounds_mm=dict(min=low,max=high),
                          defining_point_size_xyz_mm=size,
                          assumed_print_rotation='90 degrees about X; source span Y maps to printer Z',
                          bed_footprint_with_8mm_brim_each_side_mm=footprint,
                          print_height_mm=size[1],
                          assumed_envelope_fit=all(v<=240 for v in footprint) and size[1]<=250))
    assert abs(sum(p['print_height_mm'] for p in parts)-(sections[-1]['wbl_in']-sections[0]['wbl_in'])*factor)<1e-9
    assert all(p['assumed_envelope_fit'] for p in parts)
    result=dict(status='DEFINING_POINT_SEGMENTATION_PLAN_ONLY',
                printer='Bambu Lab P2S',official_build_volume_mm=[256,256,256],
                primary_source_url='https://blog.bambulab.com/the-icon-redefined-meet-the-p2s-a-completely-reengineered-version-of-the-ultra-productive-p1-series/',
                design_assumed_usable_envelope_mm=[240,240,250],assumed_brim_per_side_mm=8,
                split_wbl_in=sections[split]['wbl_in'],split_model_y_mm=sections[split]['wbl_in']*factor,
                print_shell_joint='Keep candidate carbon cap load path continuous across FDM shell joint',
                native_brep_split_performed=False,native_loft_bounds_verified=False,
                slicer_collision_check_passed=False,print_release=False,
                limitations=['Bounds of defining points may omit native loft overshoot',
                             'Usable envelope and brim are design assumptions, not verified slicer settings',
                             'No shell, joining lip, rib, adhesive or support geometry yet constructed',
                             'Spanwise build orientation requires layer-strength and support assessment'],
                parts=parts,checks='PASS: two segment spans sum to defining panel span; assumed envelope fit')
    target=ROOT/'analysis/source_wing_print_segmentation_v14.json'
    target.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'split_y_mm':result['split_model_y_mm'],'parts':parts,'checks':result['checks']}))


if __name__=='__main__': run()
