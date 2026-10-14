"""Sampled native cap geometry with an explicit uniform span-load sensitivity."""
import json, math, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def cap_pair(profiles):
    area=sum(p['area_mm2'] for p in profiles)
    z=sum(p['area_mm2']*p['centroid_mm'][2] for p in profiles)/area
    # Parallel-axis contribution alone: no unsupported local profile inertia credit.
    inertia=sum(p['area_mm2']*(p['centroid_mm'][2]-z)**2 for p in profiles)
    distance=max(abs(p['centroid_mm'][2]-z) for p in profiles)+.5
    if inertia<=0: raise ValueError('Nonpositive cap separation')
    return dict(neutral_z_mm=z,I_parallel_axis_only_mm4=inertia,assumed_cap_thickness_mm=1,outer_fiber_distance_mm=distance,W_screen_mm3=inertia/distance)

def run():
    source=ROOT/'cad/fusion/source_review/span_sections_20261014/F14_v65_section_audit.json'
    data=json.loads(source.read_text()); records=data['sections']; ys=sorted(set(r['y_mm'] for r in records)); assert len(ys)==17
    # Independent symmetric two-point identity, with translated coordinates.
    toy=[dict(area_mm2=10,centroid_mm=[0,0,z]) for z in (98,102)]
    assert math.isclose(cap_pair(toy)['I_parallel_axis_only_mm4'],80)
    stations=[]
    for y in ys:
        caps=[r['profiles'][0] for r in records if r['y_mm']==y and '_CAP_' in r['body']]
        assert len(caps)==2 and all(p['loop_count']==1 for p in caps)
        assert abs(caps[0]['centroid_mm'][0]-caps[1]['centroid_mm'][0])<1e-5
        stations.append(dict(y_mm=y,**cap_pair(caps)))
    root_y=148.8263775; tip_y=450.; span=tip_y-root_y
    cases=[]
    for mass,n,fraction in [(1.05,6,.5),(1.05,8,.7),(1.2,6,.5),(1.2,8,.7)]:
        force=mass*9.80665*n*fraction; q=force/span
        values=[dict(y_mm=s['y_mm'],moment_Nmm=q*(tip_y-s['y_mm'])**2/2,stress_screen_MPa=q*(tip_y-s['y_mm'])**2/(2*s['W_screen_mm3'])) for s in stations]
        peak=max(values,key=lambda x:x['stress_screen_MPa'])
        assert math.isclose(q*span**2/2,force*span/2)
        cases.append(dict(mass_kg=mass,load_factor=n,assigned_side_fraction=fraction,uniform_load_N_per_mm=q,stations=values,peak_sample=peak))
    result=dict(status='SAMPLED_NATIVE_GEOMETRY_UNIFORM_LOAD_SENSITIVITY',source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),stations=stations,cases=cases,checks='PASS: parallel-axis identity, cap X alignment, uniform-load moment identity',load_distribution_measured=False,local_profile_inertia_credited=False,web_or_skin_stiffness_credited=False,cap_material_modulus_uniform_assumed=True,cap_thickness_source_assumption_mm=1,sweep_torsion_shear_coupling_included=False,continuous_capacity_verified=False,tip_load_transfer_verified=False,bond_buckling_material_allowables_verified=False,structural_capacity_verified=False,print_release=False)
    out=ROOT/'analysis/native_span_load_screen_v66.json'; out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps([c['peak_sample'] for c in cases]))
if __name__=='__main__': run()
