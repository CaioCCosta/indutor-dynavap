// box_body.scad — Corpo oco (relevo tribal aplicado depois em assemble_embossed.py)
include <box_params.scad>

module body_shell() {
  difference() {
    cube([BOX_W, BOX_D, BOX_H], center = true);
    translate([0, 0, FLOOR/2 + 0.01])
      cube([BOX_W - 2*WALL, BOX_D - 2*WALL, BOX_H - FLOOR + 0.2], center = true);
  }
}

module front_holes() {
  z0 = -BOX_H/2;
  translate([ROCK_X, BOX_D/2, z0 + ROCK_Z])
    rotate([90, 0, 0]) cylinder(h = WALL + 4, r = ROCK_R, center = true);
  translate([BTN_X, BOX_D/2, z0 + BTN_Z])
    rotate([90, 0, 0]) cylinder(h = WALL + 4, r = BTN_R, center = true);
  translate([POT_X, BOX_D/2, z0 + POT_Z])
    rotate([90, 0, 0]) cylinder(h = WALL + 4, r = POT_R, center = true);
  translate([LED1_X, BOX_D/2, z0 + LED1_Z])
    rotate([90, 0, 0]) cylinder(h = WALL + 4, r = LED_R, center = true);
  translate([LED2_X, BOX_D/2, z0 + LED2_Z])
    rotate([90, 0, 0]) cylinder(h = WALL + 4, r = LED_R, center = true);
}

module rear_features() {
  z0 = -BOX_H/2;
  translate([JACK_X, -BOX_D/2, z0 + JACK_Z])
    rotate([90, 0, 0]) cylinder(h = WALL + 4, r = JACK_R, center = true);
  translate([FUSE_X, -BOX_D/2, z0 + FUSE_Z])
    rotate([90, 0, 0]) cylinder(h = WALL + 4, r = FUSE_R, center = true);
  span = (VENT_N - 1) * (VENT_W + 2);
  for (i = [0 : VENT_N - 1]) {
    x = -span/2 + i * (VENT_W + 2);
    translate([x, -BOX_D/2, z0 + VENT_Z])
      cube([VENT_W, WALL + 4, VENT_H], center = true);
  }
}

module top_tube_clearance() {
  translate([TUBE_X, 0, BOX_H/2])
    cylinder(h = WALL + 6, r = TUBE_HOLE_R, center = true);
}

module screw_posts() {
  post_r = 4;
  post_h = 8;
  for (p = screw_xy()) {
    translate([p[0], p[1], -BOX_H/2 + FLOOR])
      difference() {
        cylinder(h = post_h, r = post_r);
        translate([0, 0, -0.1])
          cylinder(h = post_h + 0.2, r = 1.2);
      }
  }
}

module box_body() {
  difference() {
    union() {
      body_shell();
      screw_posts();
    }
    front_holes();
    rear_features();
    top_tube_clearance();
  }
}

box_body();
