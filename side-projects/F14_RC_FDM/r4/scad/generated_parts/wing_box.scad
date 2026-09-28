$fn=72;
H=26;
difference(){
  translate([-82,-98,-H/2]) cube([164,196,H]);

  // Four relief windows; edge rails and central cross remain continuous.
  translate([-64,-48,-20]) cube([48,30,40]);
  translate([16,-48,-20]) cube([48,30,40]);
  translate([-64,18,-20]) cube([48,30,40]);
  translate([16,18,-20]) cube([48,30,40]);

  // 5x10x4 bearing pockets around 5 mm steel pivot shafts.
  translate([0,-68.5,-20]) cylinder(h=40,d=10.2);
  translate([0,68.5,-20]) cylinder(h=40,d=10.2);
}
