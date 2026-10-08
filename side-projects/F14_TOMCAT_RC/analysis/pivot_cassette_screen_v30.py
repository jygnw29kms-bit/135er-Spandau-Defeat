import json, math, pathlib
G=9.80665
mass=1.40
n=8.0
high=0.70
arm=0.25
F_total=mass*G*n
F_side=F_total*high
M_root=F_side*arm
lug_chord=0.040
couple=M_root/lug_chord
shaft_d=0.006
shaft_A=math.pi*shaft_d**2/4
servo_stall=2.0
horn_r=0.015
link_force=servo_stall/horn_r
shaft_resultant=(F_side**2+link_force**2)**0.5
shaft_double_shear=shaft_resultant/(2*shaft_A)/1e6
washer_od=0.016
washer_id=0.006
washer_area=math.pi*(washer_od**2-washer_id**2)/4
thrust_pressure=F_side/washer_area/1e6
pad_x=0.012; pad_z=0.016
pad_pressure=couple/(pad_x*pad_z)/1e6
unsupported_span=0.018
M_center=shaft_resultant*unsupported_span/4
shaft_bend=32*M_center/(math.pi*shaft_d**3)/1e6
out={
 'status':'PRELIMINARY_PIVOT_CASSETTE_SCREEN_NOT_RELEASED',
 'review_mass_kg':mass,'load_factor_g':n,'asymmetric_high_side_fraction':high,
 'per_high_side_vertical_N':F_side,'root_bending_moment_Nm':M_root,
 'mechanical_concept':{
   'pivot_shaft_d_mm':6.0,'bearing_class':'generic 6x13x5 radial bearing pair per pivot',
   'pivot_boss_od_mm':24.0,'moving_lug_chord_mm':40.0,'moving_lug_height_mm':16.0,
   'thrust_washer_od_mm':16.0,'thrust_washer_id_mm':6.0,
   'hardpoint_plate_thickness_mm':2.0,'hardpoint_material_class':'G10/CF or metal; final coupon/datasheet required',
   'sweep_servo_envelope_mm':[42,21,40],'servo_stall_screen_Nm':servo_stall,'servo_horn_radius_mm':15.0},
 'screen':{
   'root_moment_fore_aft_contact_couple_N':couple,
   'assumed_hardpad_area_mm2':pad_x*pad_z*1e6,
   'hardpad_bearing_pressure_MPa':pad_pressure,
   'servo_stall_link_force_N':link_force,
   'shaft_resultant_transverse_screen_N':shaft_resultant,
   'M6_double_shear_stress_MPa':shaft_double_shear,
   'thrust_washer_axial_pressure_MPa':thrust_pressure,
   'shaft_simple_span_bending_stress_MPa':shaft_bend},
 'load_path_policy':[
   'Wing root bending moment is reacted by fore/aft hardpoint contact across the 40 mm lug chord, not by printed skin.',
   '6 mm metal shaft locates the sweep pivot and carries transverse/linkage loads; it is not the sole bending-moment path.',
   'Upper/lower hard plates and thrust faces carry vertical/axial pivot reactions into the central wing box.',
   'Bearing dynamic/static ratings and actual shaft alloy must be checked against selected purchased hardware before release.'
 ],
 'release':{'mechanical_detail_release':False,'print_release':False,'flight_release':False}}
path=pathlib.Path(r'C:\Users\dezen\Desktop\RC-F14-Tomcat\Engineering\F14_pivot_cassette_screen_v30.json')
path.write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
