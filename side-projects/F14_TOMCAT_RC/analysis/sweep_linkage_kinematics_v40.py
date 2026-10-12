import json, math
from pathlib import Path

PX=613.1323905812828
PY=125.20927023775282
OUT=Path(__file__).with_name('F14_sweep_linkage_kinematics_v40.json')

candidates=[]
for dx0 in range(-50,31,5):
    for dy0 in range(-60,21,5):
        radius=math.hypot(dx0,dy0)
        if radius < 20.0 or radius > 55.0:
            continue
        for slider_y in range(25,66,5):
            for slider_x_at_20 in range(470,581,10):
                ax0=PX+dx0; ay0=PY+dy0
                rod_length=math.hypot(ax0-slider_x_at_20,ay0-slider_y)
                if rod_length > 150.0:
                    continue
                samples=[]; slider_x=[]; moment_arms=[]; valid=True
                for sweep in range(20,69,2):
                    angle=-math.radians(sweep-20.0)
                    ca,sa=math.cos(angle),math.sin(angle)
                    dx=dx0*ca-dy0*sa; dy=dx0*sa+dy0*ca
                    ax=PX+dx; ay=PY+dy
                    q=rod_length**2-(ay-slider_y)**2
                    if q <= 0.0:
                        valid=False; break
                    sx=ax-math.sqrt(q)
                    vx,vy=sx-ax,slider_y-ay
                    ll=math.hypot(vx,vy)
                    ma=abs(dx*(vy/ll)-dy*(vx/ll))
                    slider_x.append(sx); moment_arms.append(ma)
                    samples.append({'sweep_deg':sweep,'slider_x_mm':sx,'crank_pin_mm':[ax,ay],'moment_arm_mm':ma})
                if not valid:
                    continue
                stroke=max(slider_x)-min(slider_x)
                min_ma=min(moment_arms); max_ma=max(moment_arms)
                # 17-mm servo horn can provide at most 34 mm peak-to-peak; reserve margin and target ~24 mm.
                if 14.0 <= stroke <= 30.0 and min_ma >= 15.0:
                    score=min_ma-0.12*abs(stroke-24.0)-0.06*rod_length
                    candidates.append({'score':score,'crank_vector_at_20deg_mm':[dx0,dy0],
                        'crank_radius_mm':radius,'slider_attach_y_mm':float(slider_y),
                        'slider_x_at_20_mm':float(slider_x_at_20),'rod_length_mm':rod_length,
                        'slider_x_min_mm':min(slider_x),'slider_x_max_mm':max(slider_x),'slider_travel_mm':stroke,
                        'min_linkage_moment_arm_mm':min_ma,'max_linkage_moment_arm_mm':max_ma,'samples':samples})

candidates.sort(key=lambda r:r['score'],reverse=True)
selected=candidates[0]
servo_stall_Nm=2.0; horn_mm=17.0
servo_force=servo_stall_Nm/(horn_mm/1000.0)
selected['theoretical_min_wing_torque_at_2Nm_servo_Nm']=servo_force*selected['min_linkage_moment_arm_mm']/1000.0
selected['estimated_servo_travel_deg']=2.0*math.degrees(math.asin(min(0.999,(selected['slider_travel_mm']/2.0)/horn_mm)))
result={'status':'V40_KINEMATIC_SEARCH_READY_FOR_FUSION_PACKAGING','candidate_count':len(candidates),
        'constraints':{'slider_y_mm':[25,65],'crank_radius_mm':[20,55],'slider_travel_mm':[14,30],'minimum_moment_arm_mm':15,'servo_horn_radius_mm':17},
        'selected_candidate':selected,'top_candidates':candidates[:50],
        'packaging_verified':False,'mechanical_detail_release':False,'print_release':False,'flight_release':False}
OUT.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({'status':result['status'],'candidate_count':len(candidates),'selected_candidate':selected},indent=2))
