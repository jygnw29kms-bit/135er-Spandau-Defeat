"""Defining-station rectangle properties, not bonded-spar qualification."""
import json,math,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def section(height,width,cap=1.0,web=.8):
    h=height-2*cap
    if h<=0: raise ValueError('No positive web height')
    separation=height-cap
    caps=2*(width*cap**3/12+width*cap*(separation/2)**2)
    web_i=web*h**3/12
    return dict(total_height_mm=height,web_height_mm=h,cap_centroid_separation_mm=separation,cap_area_mm2=2*width*cap,web_area_mm2=web*h,I_caps_only_mm4=caps,I_web_geometric_mm4=web_i,I_if_equal_modulus_mm4=caps+web_i,cap_only_section_modulus_mm3=caps/(height/2))

def run():
    test=section(10,.8)
    assert math.isclose(test['I_if_equal_modulus_mm4'],.8*10**3/12,rel_tol=1e-12)
    assert section(9.94,16)['I_caps_only_mm4']<section(10,16)['I_caps_only_mm4']
    path=ROOT/'cad/fusion/F14TomcatRC/F14_source_spar_fit_v10.json'
    data=json.loads(path.read_text()); rows=[]
    for st in data['sections'][:-1]:
        height=st['cap_top_outer_relative_wl_mm']-st['cap_bottom_outer_relative_wl_mm']
        old=section(height,st['cap_width_mm']); new=section(height-.06,st['cap_width_mm'])
        rows.append(dict(wbl_in=st['wbl_in'],model_y_mm=st['model_y_mm'],width_mm=st['cap_width_mm'],centroid_relative_wl_mm=(st['cap_top_outer_relative_wl_mm']+st['cap_bottom_outer_relative_wl_mm'])/2,original=old,shifted_and_trimmed=new,cap_I_ratio=new['I_caps_only_mm4']/old['I_caps_only_mm4']))
    root=rows[0]['shifted_and_trimmed']; loads=[]
    for mass in [1.05,1.2]:
        for n,fraction in [(6,.5),(8,.7)]:
            force=mass*9.80665*n*fraction; moment=force*250
            loads.append(dict(mass_kg=mass,load_factor=n,assigned_side_fraction=fraction,assumed_resultant_arm_mm=250,force_N=force,moment_Nmm=moment,root_cap_only_bending_stress_MPa=moment/root['cap_only_section_modulus_mm3']))
    result=dict(status='SOURCE_STATION_SECTION_PROPERTY_AND_ROOT_LOAD_SCREEN',fit_dataset_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),checks='PASS: full-rectangle inertia identity and inward-shift monotonicity',cap_inward_shift_mm=.03,stations=rows,root_load_sensitivities=loads,continuous_native_section_properties_verified=False,web_modulus_assumed_equal_for_geometric_I_only=True,web_stiffness_credit_used_in_stress=False,bond_load_transfer_verified=False,compression_buckling_verified=False,structural_capacity_verified=False,print_release=False)
    (ROOT/'analysis/source_spar_section_properties_v63.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(root=root,load_sensitivities=loads,minimum_retained_web_height_mm=min(r['shifted_and_trimmed']['web_height_mm'] for r in rows))))

if __name__=='__main__': run()
