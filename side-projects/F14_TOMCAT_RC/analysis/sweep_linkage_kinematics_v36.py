import math,json,pathlib
PX=613.1323905812828; PY=125.20927023775282
VX=-20.0; VY=8.0; SLIDER_Y=60.0; X0=525.0; CRANK_R=17.0; SERVO_STALL=2.0

def rot(vx,vy,d):
    a=-math.radians(d); return vx*math.cos(a)-vy*math.sin(a), vx*math.sin(a)+vy*math.cos(a)
A0=(PX+VX,PY+VY); ROD=math.hypot(A0[0]-X0,A0[1]-SLIDER_Y)
rows=[]; xs=[]
for sweep in range(20,69,2):
    rx,ry=rot(VX,VY,sweep-20); ax,ay=PX+rx,PY+ry
    disc=ROD**2-(ay-SLIDER_Y)**2
    if disc<=0: raise RuntimeError('linkage singularity')
    sx=ax-math.sqrt(disc); xs.append(sx)
    dx=sx-ax; dy=SLIDER_Y-ay; ln=math.hypot(dx,dy); ux,uy=dx/ln,dy/ln
    arm=abs(rx*uy-ry*ux)
    rows.append(dict(sweep_deg=sweep,slider_x_mm=sx,wing_attach_right_mm=[ax,ay],rod_length_mm=ln,moment_arm_mm=arm))
xmin,xmax=min(xs),max(xs); mid=(xmin+xmax)/2; travel=xmax-xmin; half=travel/2
if half>=CRANK_R: raise RuntimeError('crank radius too small')
for r in rows:
    beta=math.acos((mid-r['slider_x_mm'])/CRANK_R)
    deriv_m_per_rad=(CRANK_R/1000.0)*math.sin(beta)
    slider_force=SERVO_STALL/deriv_m_per_rad
    per_rod=slider_force/2.0
    torque_side=per_rod*(r['moment_arm_mm']/1000.0)
    r.update(servo_angle_deg=math.degrees(beta),servo_total_slider_force_at_2Nm_N=slider_force,per_rod_force_equal_split_N=per_rod,theoretical_wing_torque_capacity_equal_split_Nm=torque_side)
result=dict(status='PRELIMINARY_SYNCHRONIZED_SWEEP_LINKAGE_KINEMATICS_NOT_RELEASED',
 geometry=dict(pivot_right_mm=[PX,PY],wing_attach_vector_at_20deg_mm=[VX,VY],slider_attach_y_mm=SLIDER_Y,rod_length_mm=ROD,slider_x_min_mm=xmin,slider_x_max_mm=xmax,slider_travel_mm=travel,servo_crank_radius_mm=CRANK_R,servo_angle_min_deg=min(r['servo_angle_deg'] for r in rows),servo_angle_max_deg=max(r['servo_angle_deg'] for r in rows),servo_angle_travel_deg=max(r['servo_angle_deg'] for r in rows)-min(r['servo_angle_deg'] for r in rows)),
 performance=dict(min_linkage_moment_arm_mm=min(r['moment_arm_mm'] for r in rows),max_linkage_moment_arm_mm=max(r['moment_arm_mm'] for r in rows),min_theoretical_wing_torque_capacity_Nm=min(r['theoretical_wing_torque_capacity_equal_split_Nm'] for r in rows),servo_stall_screen_Nm=SERVO_STALL),
 samples=rows,
 notes=['Left side is exact mirror of right side and uses the same central slider X; synchronization is mechanically constrained.','Servo crank mapping assumes a slotted-yoke/scotch-yoke style conversion from rotary servo motion to X slider travel.','Torque capacity is a static geometric screen only; aerodynamic sweep hinge moment, friction, backlash and purchased servo data remain release gates.'],
 release=dict(linkage_kinematics_geometry_pass=True,servo_model_selected=False,aerodynamic_sweep_torque_verified=False,mechanical_detail_release=False,print_release=False,flight_release=False))
out=pathlib.Path(r'C:\Users\dezen\Desktop\RC-F14-Tomcat\Engineering\F14_sweep_linkage_kinematics_v36.json'); out.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='samples'},indent=2))
