$fn=64;
module raw(){linear_extrude(height=10,center=true) polygon(points=[[-35.00000,-25.00000],[175.00000,-25.00000],[171.36119,110.00000],[17.76280,110.00000]]);}
module spar(){hull(){translate([77.1720,-17.0000,0]) sphere(d=6.4,$fn=36); translate([100.5550,102.0000,0]) sphere(d=6.4,$fn=36);}}
module wing(){difference(){raw(); spar(); translate([0,0,-8]) cylinder(h=16,d=10.2,$fn=64); translate([34,28,-8]) cylinder(h=16,d=3.2,$fn=40);}}
mirror([0,1,0]) wing();
