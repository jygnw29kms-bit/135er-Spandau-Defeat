
$fn=64;
module raw_wing(){
    union(){
        linear_extrude(height=10,center=true) polygon(points=[[0.0,0.0],[220.0,0.0],[241.75,145.0],[79.75,145.0]]);
        
    }
}
module spar_channel(){
    hull(){
        translate([143.9,-5,0]) sphere(d=6.4,$fn=36);
        translate([178.0,150,0]) sphere(d=6.4,$fn=36);
    }
}
module wing(){
    difference(){
        raw_wing();
        spar_channel();
        
        translate([42.0,24.0,-8]) cylinder(h=16,d=10.2,$fn=64);
        translate([78,38,-8]) cylinder(h=16,d=3.2,$fn=36);
    
    }
}
wing();
