$fn=64;
module raw(){linear_extrude(height=10,center=true) polygon(points=[[62.70889,225.00000],[168.26146,225.00000],[165.00000,346.00000],[110.00000,346.00000]]);}
module spar(){hull(){translate([126.2960,233.0000,0]) sphere(d=6.4,$fn=36); translate([146.9280,338.0000,0]) sphere(d=6.4,$fn=36);}}
module wing(){difference(){raw(); spar(); }}
mirror([0,1,0]) wing();
