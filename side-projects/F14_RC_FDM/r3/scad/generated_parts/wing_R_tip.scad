
$fn=64;
module raw_wing(){
    union(){
        linear_extrude(height=10,center=true) polygon(points=[[148.5,270.0],[260.5,270.0],[279.25,395.0],[217.25,395.0]]);
        
    }
}
module spar_channel(){
    hull(){
        translate([203.3,265,0]) sphere(d=6.4,$fn=36);
        translate([233.0,400,0]) sphere(d=6.4,$fn=36);
    }
}
module wing(){
    difference(){
        raw_wing();
        spar_channel();
        
    }
}
mirror([0,1,0]) wing();
