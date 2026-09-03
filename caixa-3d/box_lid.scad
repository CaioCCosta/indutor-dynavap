// box_lid.scad — Tampa + ímã (relevo tribal 2 via assemble_embossed.py)
include <box_params.scad>

module lid_plate() {
  cube([BOX_W, BOX_D, LID_H], center = true);
}

module lid_lip() {
  iw = BOX_W - 2*WALL - LIP_CLR;
  id = BOX_D - 2*WALL - LIP_CLR;
  translate([0, 0, -LID_H/2 - LIP_H/2 + 0.01])
    difference() {
      cube([iw, id, LIP_H], center = true);
      cube([iw - 2.4, id - 2.4, LIP_H + 1], center = true);
    }
}

module tube_hole() {
  translate([TUBE_X, 0, 0])
    cylinder(h = LID_H + LIP_H + 4, r = TUBE_HOLE_R, center = true);
}

module collar() {
  translate([TUBE_X, 0, LID_H/2 + COLLAR_H/2])
    difference() {
      cylinder(h = COLLAR_H, r = COLLAR_OD/2, center = true);
      cylinder(h = COLLAR_H + 1, r = COLLAR_ID/2, center = true);
    }
}

module magnet_boss() {
  if (MAGNET_BOSS > 0) {
    translate([MAGNET_X, MAGNET_Y, LID_H/2 + MAGNET_BOSS/2])
      cylinder(h = MAGNET_BOSS, r = POCKET_D/2 + 2, center = true);
  }
}

module magnet_pocket() {
  top_z = LID_H/2 + MAGNET_BOSS;
  translate([MAGNET_X, MAGNET_Y, top_z - POCKET_H/2 + 0.01])
    cylinder(h = POCKET_H + 0.02, r = POCKET_D/2, center = true);
}

module screw_holes() {
  for (p = screw_xy()) {
    translate([p[0], p[1], 0])
      cylinder(h = LID_H + 4, r = SCREW_R, center = true);
  }
}

module box_lid() {
  difference() {
    union() {
      lid_plate();
      lid_lip();
      collar();
      magnet_boss();
    }
    tube_hole();
    magnet_pocket();
    screw_holes();
  }
}

box_lid();
