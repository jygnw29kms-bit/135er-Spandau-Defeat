$fn=64;
module raw(){linear_extrude(height=10,center=true) polygon(points=[[15.80863,105.00000],[171.49596,105.00000],[168.12668,230.00000],[64.66307,230.00000]]);}
module spar(){hull(){translate([102.7164,113.0000,0]) sphere(d=6.4,$fn=36); translate([124.1345,222.0000,0]) sphere(d=6.4,$fn=36);}}
module wing(){difference(){raw(); spar(); }}
mirror([0,1,0]) wing();
