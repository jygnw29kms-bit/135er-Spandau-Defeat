// F-14 RC FDM R2 - parametric OpenSCAD master
// Units: mm. Coordinate system: +X nose->tail, +Y aircraft left, +Z up.
// This is an RC-optimized interpretation, not a manufacturing replica of the real aircraft.

$fn = 40;
part = is_undef(part) ? "assembly" : part;
sweep = is_undef(sweep) ? 20 : sweep;
wall = 2.2;
clearance = 0.35;

L = 950;
W_EXT = 900;
PIVOT_X = 430;
PIVOT_Y = 82;
PIVOT_D = 5.2;
CFK_D = 5.4;

module ellipsoid(pos=[0,0,0], r=[10,10,10]) { translate(pos) scale(r) sphere(1); }
module rounded_box(size=[10,10,10], r=2, center=true) {
    sx=size[0]; sy=size[1]; sz=size[2];
    translate(center?[-sx/2,-sy/2,-sz/2]:[0,0,0])
    minkowski(){ cube([sx-2*r,sy-2*r,sz-2*r]); sphere(r); }
}
module slab_x(x0,x1, pad=300) { translate([x0,-pad,-pad]) cube([x1-x0,2*pad,2*pad]); }
module slab_y(y0,y1, padx=300, padz=100) { translate([-padx,y0,-padz]) cube([2*padx,y1-y0,2*padz]); }

outer_st = [
 [0,3,3,0],[45,22,24,0],[110,35,34,2],[180,43,42,4],[260,54,48,5],[350,65,52,3],
 [450,72,50,0],[560,70,44,-2],[670,64,38,-3],[780,54,32,-2],[875,38,26,0],[950,18,18,2]
];

module loft_from_st(st, shrink=0) {
    union(){ for(i=[0:len(st)-2]) hull(){
        ellipsoid([st[i][0],0,st[i][3]],[10,max(1,st[i][1]-shrink),max(1,st[i][2]-shrink)]);
        ellipsoid([st[i+1][0],0,st[i+1][3]],[10,max(1,st[i+1][1]-shrink),max(1,st[i+1][2]-shrink)]);
    }}
}
module center_fuselage_shell(){
    difference(){
        loft_from_st(outer_st,0);
        intersection(){ loft_from_st(outer_st,wall); slab_x(18,944,160); }
        translate([215,-34,18]) rounded_box([215,68,45],r=5,center=false);
        translate([470,-42,-48]) rounded_box([170,84,26],r=4,center=false);
    }
}
module fuselage_cfk_holes(){ for(y=[-40,40]) translate([470,y,-16]) rotate([0,90,0]) cylinder(h=620,d=4.4,center=true,$fn=28); }
module fuselage_segment(x0,x1){ difference(){ intersection(){ center_fuselage_shell(); slab_x(x0,x1,160); } fuselage_cfk_holes(); } }

module canopy_outer(){ hull(){ ellipsoid([238,0,42],[28,42,18]); ellipsoid([320,0,45],[42,45,20]); ellipsoid([375,0,32],[18,37,12]); } }
module canopy(){ difference(){ canopy_outer(); translate([0,0,-2]) scale([0.965,0.93,0.84]) canopy_outer(); translate([200,-80,-40]) cube([220,160,44]); } translate([300,-22,20]) cube([42,44,3]); }

module wing_solid_local(){
    hull(){ translate([18,30,0]) rounded_box([205,36,14],r=5); translate([72,330,0]) rounded_box([92,26,8],r=4); }
    cylinder(h=14,d=46,center=true,$fn=48);
}
module wing_holes_local(){
    cylinder(h=30,d=PIVOT_D,center=true,$fn=32);
    for(x=[38,88]) translate([x,165,0]) rotate([90,0,0]) cylinder(h=360,d=CFK_D,center=true,$fn=28);
}
module wing_local(){ difference(){ wing_solid_local(); wing_holes_local(); } }
module wing_segment_local(y0,y1){ intersection(){ wing_local(); slab_y(y0,y1,180,40); } }
module wing_root(side=1){ difference(){ wing_segment_local(-25,125); if(side<0) translate([-10,-7,-20]) cube([20,14,40]); } }
module wing_mid(side=1){ wing_segment_local(120,245); }
module wing_tip(side=1){ wing_segment_local(240,360); }
module pivot_doubler(side=1){ difference(){ cylinder(h=10,d=58,center=true,$fn=48); cylinder(h=12,d=PIVOT_D,center=true,$fn=32); translate([20,-4,-6]) cube([22,8,12]); } }

module wing_box(){
    difference(){
      union(){ rounded_box([150,210,24],r=8); for(y=[-PIVOT_Y,PIVOT_Y]) translate([0,y,0]) cylinder(h=30,d=64,center=true,$fn=48); }
      for(y=[-PIVOT_Y,PIVOT_Y]) translate([0,y,0]) cylinder(h=40,d=PIVOT_D,center=true,$fn=32);
      translate([15,0,0]) rounded_box([62,44,28],r=3);
      rotate([90,0,0]) cylinder(h=230,d=8.4,center=true,$fn=28);
    }
}
module sweep_crank(){
    difference(){
      union(){ cylinder(h=8,d=34,center=true,$fn=48); for(a=[0,180]) rotate([0,0,a]) translate([31,0,0]) rounded_box([58,12,8],r=3); }
      cylinder(h=12,d=6.2,center=true,$fn=28);
      for(x=[-55,55]) translate([x,0,0]) cylinder(h=12,d=3.2,center=true,$fn=20);
    }
}
module pivot_spacer(){ difference(){ cylinder(h=4,d=34,center=true,$fn=48); cylinder(h=6,d=PIVOT_D+0.25,center=true,$fn=32);} }

module nacelle_outer(len=180){ rotate([0,90,0]) scale([1,1.25,0.95]) cylinder(h=len,d=66,center=true,$fn=40); }
module nacelle_shell(len=180){ difference(){ nacelle_outer(len); rotate([0,90,0]) scale([1,1.0,0.78]) cylinder(h=len+2,d=58,center=true,$fn=40); } }
module nacelle_front(){
  difference(){ nacelle_shell(180); translate([-92,0,0]) rotate([0,90,0]) cylinder(h=12,d=51.5,center=true,$fn=48); }
  translate([70,0,0]) rotate([0,90,0]) difference(){ cylinder(h=6,d=62,center=true,$fn=48); cylinder(h=8,d=50.8,center=true,$fn=48); }
}
module nacelle_rear(){ difference(){ nacelle_shell(180); translate([92,0,0]) rotate([0,90,0]) cylinder(h=20,d1=44,d2=54,center=true,$fn=48); } }
module edf_ring(){ rotate([0,90,0]) difference(){ cylinder(h=8,d=62,center=true,$fn=48); cylinder(h=10,d=50.8,center=true,$fn=48); } }

module wing_glove(side=1){
  mirror([0,side<0?1:0,0]) difference(){
    hull(){ translate([0,0,0]) rounded_box([180,70,18],r=7); translate([55,105,0]) rounded_box([130,42,12],r=6); }
    translate([0,45,0]) cylinder(h=30,d=54,center=true,$fn=48);
  }
}

module taileron(side=1){
    linear_extrude(height=7,center=true) polygon(points=[[0,0],[170,28],[155,95],[35,78]]);
    translate([34,44,0]) rotate([90,0,0]) difference(){ cylinder(h=20,d=14,center=true,$fn=32); cylinder(h=22,d=4.2,center=true,$fn=24); }
}
module vertical_tail(side=1){
  linear_extrude(height=7,center=true) polygon(points=[[0,0],[145,22],[118,155],[70,175],[38,58]]);
  translate([45,36,0]) rounded_box([38,24,10],r=3);
}
module battery_tray(){
 difference(){ rounded_box([210,62,8],r=4); for(x=[-60,0,60]) translate([x,0,0]) rounded_box([22,48,10],r=3); }
 for(x=[-92,92]) translate([x,0,8]) rounded_box([10,58,18],r=2);
}
module electronics_hatch(){ rounded_box([162,80,3.2],r=1.4); }

module joiner_ring_dims(ry=45,rz=40){
    rotate([0,90,0]) difference(){
      scale([1,rz/ry,1]) cylinder(h=8,d=2*ry,center=true,$fn=56);
      scale([1,(rz-4)/(ry-4),1]) cylinder(h=10,d=2*(ry-4),center=true,$fn=56);
    }
}

module aircraft_assembly(sweep_deg=20){
  color("lightgray") center_fuselage_shell();
  color([0.2,0.35,0.5,0.65]) canopy();
  color("orange") translate([PIVOT_X,0,0]) wing_box();
  color("lightgray") translate([PIVOT_X,PIVOT_Y,0]) rotate([0,0,-sweep_deg]) wing_local();
  color("lightgray") mirror([0,1,0]) translate([PIVOT_X,PIVOT_Y,0]) rotate([0,0,-sweep_deg]) wing_local();
  color("gainsboro") translate([445,82,6]) wing_glove(1);
  color("gainsboro") mirror([0,1,0]) translate([445,82,6]) wing_glove(1);
  for(y=[-66,66]){ color("silver") translate([650,y,-18]) nacelle_front(); color("silver") translate([830,y,-18]) nacelle_rear(); }
  color("lightgray") translate([760,72,0]) rotate([0,0,-8]) taileron(1);
  color("lightgray") mirror([0,1,0]) translate([760,72,0]) rotate([0,0,-8]) taileron(1);
  color("lightgray") translate([780,54,10]) rotate([90,0,0]) vertical_tail(1);
  color("lightgray") mirror([0,1,0]) translate([780,54,10]) rotate([90,0,0]) vertical_tail(1);
}

if(part=="assembly") aircraft_assembly(sweep);
else if(part=="fuselage_01_nose") fuselage_segment(0,175);
else if(part=="fuselage_02_cockpit") fuselage_segment(175,355);
else if(part=="fuselage_03_center") fuselage_segment(355,535);
else if(part=="fuselage_04_rear") fuselage_segment(535,715);
else if(part=="fuselage_05_tail") fuselage_segment(715,950);
else if(part=="canopy") canopy();
else if(part=="joiner_175") joiner_ring_dims(43,42);
else if(part=="joiner_355") joiner_ring_dims(65,51);
else if(part=="joiner_535") joiner_ring_dims(71,46);
else if(part=="joiner_715") joiner_ring_dims(60,35);
else if(part=="wing_box") wing_box();
else if(part=="sweep_crank") sweep_crank();
else if(part=="pivot_spacer") pivot_spacer();
else if(part=="wing_L_root") wing_root(1);
else if(part=="wing_L_mid") wing_mid(1);
else if(part=="wing_L_tip") wing_tip(1);
else if(part=="wing_R_root") wing_root(-1);
else if(part=="wing_R_mid") wing_mid(-1);
else if(part=="wing_R_tip") wing_tip(-1);
else if(part=="pivot_doubler_L") pivot_doubler(1);
else if(part=="pivot_doubler_R") pivot_doubler(-1);
else if(part=="wing_glove_L") wing_glove(1);
else if(part=="wing_glove_R") mirror([0,1,0]) wing_glove(1);
else if(part=="nacelle_L_front") nacelle_front();
else if(part=="nacelle_L_rear") nacelle_rear();
else if(part=="nacelle_R_front") mirror([0,1,0]) nacelle_front();
else if(part=="nacelle_R_rear") mirror([0,1,0]) nacelle_rear();
else if(part=="edf_ring_L") edf_ring();
else if(part=="edf_ring_R") edf_ring();
else if(part=="taileron_L") taileron(1);
else if(part=="taileron_R") taileron(-1);
else if(part=="vertical_tail_L") vertical_tail(1);
else if(part=="vertical_tail_R") vertical_tail(-1);
else if(part=="battery_tray") battery_tray();
else if(part=="electronics_hatch") electronics_hatch();
