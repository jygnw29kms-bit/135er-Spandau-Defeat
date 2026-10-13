"""Refit corrected E without stretching or changing previous audit records."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def run():
    contour_path=ROOT/'upc_E_source_contour_v43.json'
    contour=json.loads(contour_path.read_text())
    old=json.loads((ROOT/'upc_DE_registration_v12.json').read_text())
    fit=next(s for s in old['sections'] if s['name']=='E')
    points=contour['pixel_outline']
    width=max(p[0] for p in points)-min(p[0] for p in points)
    top=min(p[1] for p in points)
    bottom=max(p[1] for p in points)
    factor=fit['plan_body_width_pixels']/width
    height=(bottom-top)*factor
    side_center=(fit['side_body_top_pixel_y']+fit['side_body_bottom_pixel_y'])/2
    axis=side_center+(contour['source_section_axis_pixel'][1]-(top+bottom)/2)*factor
    assert abs(width*factor-fit['plan_body_width_pixels'])<1e-9
    assert abs(((top+bottom)/2+(axis-side_center)/factor)-contour['source_section_axis_pixel'][1])<1e-9
    out=dict(status='CORRECTED_E_ISOTROPIC_REGISTRATION_CANDIDATE',
        contour_sha256=hashlib.sha256(contour_path.read_bytes()).hexdigest(),
        source_image_sha256=contour['source_image_sha256'],
        source_width_pixels=width,source_height_pixels=bottom-top,
        isotropic_multiplier=factor,predicted_height_pixels=height,
        side_height_pixels=fit['side_body_height_pixels'],
        height_residual_pixels=height-fit['side_body_height_pixels'],
        candidate_axis_side_pixel_y=axis,
        checks='PASS: width reproduction and axis transform round-trip',
        independent_vertical_stretch_applied=False,
        metric_registration_verified=False,production_loft_allowed=False,
        legacy_E_dependent_reports_require_regeneration=['v12 E fit','v16 EDF section packing','v17 common axis','v18 tilted axes','v20 error budgets'])
    (ROOT/'upc_E_registration_v44.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out))

if __name__=='__main__': run()
