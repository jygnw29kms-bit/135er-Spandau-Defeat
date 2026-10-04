"""Reproducible preliminary beam FE screening; not an aircraft release analysis.

Run with Python + numpy. Uses the existing project's conservative loads.
No strength credit for printed skin. No assumed material data are certified.
"""
import csv
import json
import math
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent
G = 9.80665
MASS = 1.05
SPAN = 0.319
ARM = 0.250
E = 70e9  # sensitivity assumption, NOT verified carbon-tube property
ALLOWABLE = 350e6  # provisional screening value, supplier/coupon data required
DENSITY = 1600.0


def tube(od_mm, id_mm):
    od, inner = od_mm / 1000, id_mm / 1000
    return math.pi * (od**4 - inner**4) / 64, math.pi * (od**2 - inner**2) / 4, od / 2


def beam_fe(force, inertia, count):
    """Clamped beam, point load exactly at ARM; free remainder to SPAN.

    Two DOF/node: deflection, rotation. Piecewise cubic Euler-Bernoulli.
    Adding the force location as a node avoids interpolation ambiguity.
    """
    positions = np.unique(np.append(np.linspace(0, SPAN, count + 1), ARM))
    ndof = 2 * len(positions)
    k = np.zeros((ndof, ndof))
    f = np.zeros(ndof)
    for j, h in enumerate(np.diff(positions)):
        ke = E * inertia / h**3 * np.array([
            [12, 6*h, -12, 6*h],
            [6*h, 4*h*h, -6*h, 2*h*h],
            [-12, -6*h, 12, -6*h],
            [6*h, 2*h*h, -6*h, 4*h*h],
        ])
        dofs = np.arange(2*j, 2*j + 4)
        k[np.ix_(dofs, dofs)] += ke
    f[2 * int(np.where(positions == ARM)[0][0])] = force
    u = np.zeros(ndof)
    u[2:] = np.linalg.solve(k[2:, 2:], f[2:])
    reaction = k @ u - f
    analytical = force * ARM**2 * (3 * SPAN - ARM) / (6 * E * inertia)
    assert math.isclose(u[-2], analytical, rel_tol=1e-6, abs_tol=1e-10)
    assert math.isclose(reaction[0], -force, rel_tol=1e-6)
    assert math.isclose(reaction[1], -force*ARM, rel_tol=1e-6)
    return float(u[-2]), float(reaction[0]), float(reaction[1])


def sweep_span(angle_deg):
    # Rotate the ACTUAL existing right-wing planform about (456.5, 131).
    delta = math.radians(angle_deg - 20)
    le = 456.5 - 20.4
    tip_le = le + math.tan(math.radians(20)) * 319
    points = [(le, 131), (le+150.15, 131), (tip_le, 450), (tip_le+55.03, 450)]
    ys = [131 + (y-131)*math.cos(delta) - (x-456.5)*math.sin(delta) for x,y in points]
    return 2 * max(ys)


def capped_spar(force, count, width_mm=16, thickness_mm=1):
    """Candidate tapered carbon caps with a continuous shear web.

    Assumes nominal airfoil thickness and full cap/web composite action.
    Constant-width caps, separation tapered to stay inside nominal OML.
    The cap bond and web are NOT validated by this one-dimensional model.
    """
    nodes=np.unique(np.append(np.linspace(0,SPAN,count+1),ARM))
    k=np.zeros((2*len(nodes),2*len(nodes)))
    f=np.zeros(2*len(nodes))
    w,t=width_mm/1000,thickness_mm/1000
    def section(s):
        r=s/SPAN
        chord=(150.15+(55.03-150.15)*r)/1000
        tc=0.0965+(0.0891-0.0965)*r
        h=chord*tc-2*0.0008-t  # cap centroid separation
        assert h>t
        return 2*(w*t**3/12+w*t*(h/2)**2),h/2+t/2
    stress=0.0
    for j,h in enumerate(np.diff(nodes)):
        mid=(nodes[j]+nodes[j+1])/2
        inertia,c=section(mid)
        ke=E*inertia/h**3*np.array([[12,6*h,-12,6*h],[6*h,4*h*h,-6*h,2*h*h],[-12,-6*h,12,-6*h],[6*h,2*h*h,-6*h,4*h*h]])
        ix=np.arange(2*j,2*j+4)
        k[np.ix_(ix,ix)]+=ke
        stress=max(stress,force*max(0,ARM-mid)*c/inertia)
    f[2*int(np.where(nodes==ARM)[0][0])]=force
    u=np.zeros(len(f)); u[2:]=np.linalg.solve(k[2:,2:],f[2:])
    reaction=k@u-f
    assert math.isclose(reaction[0],-force,rel_tol=1e-6)
    assert math.isclose(reaction[1],-force*ARM,rel_tol=1e-6)
    # Independent virtual-work integral; fine composite midpoint integration.
    s=(np.arange(20000)+0.5)*ARM/20000
    integrand=np.array([force*(ARM-v)*(SPAN-v)/(E*section(v)[0]) for v in s])
    independent=float(np.sum(integrand)*ARM/20000)
    assert abs(u[-2]-independent)/independent < 0.005
    return float(u[-2]),stress,independent


def run():
    rows = []
    cases = [('3g', MASS*G*3/2), ('6g', MASS*G*6/2),
             ('8g', MASS*G*8/2), ('8g_70percent', MASS*G*8*0.7)]
    for od, inner in [(6,4), (8,6), (10,8), (12,10)]:
        inertia, area, extreme = tube(od, inner)
        for case, force in cases:
            results = [beam_fe(force, inertia, n) for n in [16,32,64]]
            tip_mm = results[-1][0]*1000
            stress = force*ARM*extreme/inertia
            rows.append(dict(tube=f'{od}/{inner}',case=case,force_N=round(force,6),
                moment_Nm=round(force*ARM,6),stress_MPa=round(stress/1e6,3),
                provisional_factor=round(ALLOWABLE/stress,3),tip_deflection_mm=round(tip_mm,4),
                mass_two_full_length_tubes_g=round(2*area*SPAN*DENSITY*1000,3),
                geometrically_possible_at_tip=False,
                linear_small_deflection_valid=tip_mm < SPAN*1000*0.05,
                mesh_relative_change=abs(results[-1][0]-results[-2][0])/abs(results[-1][0])))
    with (ROOT/'structural_screen_results.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.DictWriter(stream,fieldnames=rows[0].keys())
        writer.writeheader(); writer.writerows(rows)
    sweep=[dict(sweep_deg=a,span_mm=round(sweep_span(a),3)) for a in [20,30,40,50,60,68]]
    data = dict(status='PRELIMINARY_SCREENING_NOT_RELEASED', mass_kg=MASS,
        carbon_assumptions=dict(E_GPa=70,allowable_MPa=350,density_kg_m3=1600),
        span_m=SPAN,load_arm_m=ARM,model='clamped Euler-Bernoulli beam; concentrated wing resultant',
        verification='16/32/64 elements; closed-form deflection and force/moment equilibrium passed',
        excluded=['pivot compliance','bearing/contact','bond failure','carbon compression/buckling',
            'skin stiffness','torsion','dynamic loads','aerodynamics','flight stability'],
        sweep_planform_only=sweep,
        reference_swept_span_mm=round(38.2*304.8*900/19532.6,3),
        inherited_swept_span_mm=round(14681.2*900/19532.6,3),
        nominal_tip_thickness_mm=55.03*0.0891,
        skin_mm=0.8,nominal_tip_internal_height_mm=55.03*0.0891-1.6,
        root_8g_required_section_modulus_mm3=(MASS*G*8*0.7*ARM)/ALLOWABLE*1e9,
        battery_20g_forward_N=0.22*20*G,
        note='Span discrepancy is an OML gate; no reference body changed or printable aircraft released.')
    cap_rows=[]
    for case,force in cases:
        meshes=[capped_spar(force,n) for n in [32,64,128]]
        delta=abs(meshes[-1][0]-meshes[-2][0])/abs(meshes[-1][0])
        assert delta<0.005
        cap_rows.append(dict(case=case,force_N=force,tip_deflection_mm=meshes[-1][0]*1000,
            stress_MPa=meshes[-1][1]/1e6,provisional_factor=ALLOWABLE/meshes[-1][1],
            mesh_relative_change=delta,independent_tip_deflection_mm=meshes[-1][2]*1000))
    data['candidate_tapered_cap_spar']=dict(width_mm=16,cap_thickness_mm=1,
        cap_mass_two_wings_g=4*0.016*0.001*SPAN*DENSITY*1000,
        assumed_cap_centroid_separation_root_mm=150.15*0.0965-1.6-1,
        assumed_cap_centroid_separation_tip_mm=55.03*0.0891-1.6-1,
        status='CANDIDATE_ONLY_NOT_CAD_VALIDATED',results=cap_rows,
        limitations=['cap location must use actual airfoil ordinate, not nominal maximum thickness',
            'full shear transfer assumed; web, bonded joints and buckling need separate analysis',
            'pivot fitting, print joints and sweep envelope unresolved'])
    (ROOT/'structural_screen_summary.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(data,indent=2))
    print('FE cases:',len(rows),'All analytical and equilibrium checks passed.')


if __name__ == '__main__':
    run()
