
$fn=72;
H=26;
module diagbeam(x2,y2,w=12){
    hull(){
        translate([0,0,-H/2]) cylinder(h=H,d=w);
        translate([x2,y2,-H/2]) cylinder(h=H,d=w);
    }
}
difference(){
    union(){
        // 15 mm perimeter frame
        translate([-85,-114,-H/2]) cube([170,15,H]);
        translate([-85,99,-H/2]) cube([170,15,H]);
        translate([-85,-99,-H/2]) cube([15,198,H]);
        translate([70,-99,-H/2]) cube([15,198,H]);

        // central cross beams
        translate([-12,-114,-H/2]) cube([24,228,H]);
        translate([-85,-12,-H/2]) cube([170,24,H]);

        // diagonal truss members
        diagbeam(72,96);
        diagbeam(-72,96);
        diagbeam(72,-96);
        diagbeam(-72,-96);

        // pivot bosses
        translate([0,-87,-H/2]) cylinder(h=H,d=76);
        translate([0,87,-H/2]) cylinder(h=H,d=76);
    }
    // M5 pivot bores with printing clearance
    translate([0,-87,-20]) cylinder(h=40,d=5.2);
    translate([0,87,-20]) cylinder(h=40,d=5.2);
}
