
$fn=64;
module raw_wing(){
    union(){
        linear_extrude(height=10,center=true) polygon(points=[[77.0,140.0],[241.0,140.0],[261.25,275.0],[151.25,275.0]]);
        
    }
}
module spar_channel(){
    hull(){
        translate([174.7,135,0]) sphere(d=6.4,$fn=36);
        translate([206.6,280,0]) sphere(d=6.4,$fn=36);
    }
}
module wing(){
    difference(){
        raw_wing();
        spar_channel();
        
    }
}
wing();
