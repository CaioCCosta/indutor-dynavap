// box_emboss.scad — Alto relevo tribal (import STL dos decals)
include <box_params.scad>

DECAL1_FILE = "decals/tribal_1_emboss.stl";
DECAL2_FILE = "decals/tribal_2_emboss.stl";
DECAL3_FILE = "decals/tribal_3_emboss.stl";

DECAL1_NATIVE_W = 70.0;
DECAL1_NATIVE_H = 28.5;
DECAL2_NATIVE_W = 45.0;
DECAL2_NATIVE_H = 41.3;
DECAL3_NATIVE_W = 50.0;
DECAL3_NATIVE_H = 80.6;

module emboss_scaled(file, native_w, native_h, max_w, max_h) {
  s = min(max_w / native_w, max_h / native_h);
  scale([s, s, 1])
    import(file, convexity = 12);
}

module front_keepouts() {
  z0 = -BOX_H/2;
  translate([ROCK_X, BOX_D/2, z0 + ROCK_Z])
    rotate([90, 0, 0]) cylinder(h = WALL + 8, r = ROCK_R + KEEPOUT_CLR, center = true);
  translate([BTN_X, BOX_D/2, z0 + BTN_Z])
    rotate([90, 0, 0]) cylinder(h = WALL + 8, r = BTN_R + KEEPOUT_CLR, center = true);
  translate([POT_X, BOX_D/2, z0 + POT_Z])
    rotate([90, 0, 0]) cylinder(h = WALL + 8, r = POT_R + KEEPOUT_CLR, center = true);
  translate([LED1_X, BOX_D/2, z0 + LED1_Z])
    rotate([90, 0, 0]) cylinder(h = WALL + 8, r = LED_R + KEEPOUT_CLR, center = true);
  translate([LED2_X, BOX_D/2, z0 + LED2_Z])
    rotate([90, 0, 0]) cylinder(h = WALL + 8, r = LED_R + KEEPOUT_CLR, center = true);
}

module rear_keepouts() {
  z0 = -BOX_H/2;
  translate([JACK_X, -BOX_D/2, z0 + JACK_Z])
    rotate([90, 0, 0]) cylinder(h = WALL + 8, r = JACK_R + KEEPOUT_CLR, center = true);
  translate([FUSE_X, -BOX_D/2, z0 + FUSE_Z])
    rotate([90, 0, 0]) cylinder(h = WALL + 8, r = FUSE_R + KEEPOUT_CLR, center = true);
  span = (VENT_N - 1) * (VENT_W + 2);
  for (i = [0 : VENT_N - 1]) {
    x = -span/2 + i * (VENT_W + 2);
    translate([x, -BOX_D/2, z0 + VENT_Z])
      cube([VENT_W + KEEPOUT_CLR, WALL + 8, VENT_H + KEEPOUT_CLR], center = true);
  }
}

// Frente (+Y): STL Z → +Y; STL X → X; STL Y → Z
module emboss_front() {
  mw = BOX_W - 2*EMBOSS_MARGIN;
  mh = BOX_H - 2*EMBOSS_MARGIN;
  difference() {
    translate([0, BOX_D/2, 0])
      rotate([-90, 0, 0])
        emboss_scaled(DECAL1_FILE, DECAL1_NATIVE_W, DECAL1_NATIVE_H, mw, mh);
    front_keepouts();
  }
}

// Trás (−Y): STL Z → −Y
module emboss_rear() {
  mw = BOX_W - 2*EMBOSS_MARGIN;
  mh = BOX_H - 2*EMBOSS_MARGIN;
  difference() {
    translate([0, -BOX_D/2, 0])
      rotate([90, 0, 0])
        emboss_scaled(DECAL1_FILE, DECAL1_NATIVE_W, DECAL1_NATIVE_H, mw, mh);
    rear_keepouts();
  }
}

// Esquerda (−X): STL Z → −X; largura do tribal ao longo de Y
module emboss_left() {
  mw = BOX_D - 2*EMBOSS_MARGIN;
  mh = BOX_H - 2*EMBOSS_MARGIN;
  translate([-BOX_W/2, 0, 0])
    rotate([0, -90, 0])
      rotate([0, 0, 90])
        emboss_scaled(DECAL1_FILE, DECAL1_NATIVE_W, DECAL1_NATIVE_H, mw, mh);
}

// Direita (+X): STL Z → +X
module emboss_right() {
  mw = BOX_D - 2*EMBOSS_MARGIN;
  mh = BOX_H - 2*EMBOSS_MARGIN;
  translate([BOX_W/2, 0, 0])
    rotate([0, 90, 0])
      rotate([0, 0, -90])
        emboss_scaled(DECAL1_FILE, DECAL1_NATIVE_W, DECAL1_NATIVE_H, mw, mh);
}

// Base (−Z): eixo longo // BOX_W (Rz 90); margem 4 mm
module emboss_bottom() {
  mw = BOX_D - 2*4;  // nativo W → profundidade após Rz90
  md = BOX_W - 2*4;  // nativo H → largura após Rz90
  translate([0, 0, -BOX_H/2])
    rotate([180, 0, 0])
      rotate([0, 0, 90])
        emboss_scaled(DECAL3_FILE, DECAL3_NATIVE_W, DECAL3_NATIVE_H, mw, md);

  for (p = screw_xy()) {
    translate([p[0], p[1], -BOX_H/2 - BOTTOM_PAD_H])
      cylinder(h = BOTTOM_PAD_H, r = 4);
  }
}

// Tampa (+Z): arte centrada no pocket do ímã (escala máx. sem recortar cantos)
module emboss_lid_top() {
  free_l = -BOX_W/2 + EMBOSS_MARGIN;
  free_r = TUBE_X - COLLAR_OD/2 - KEEPOUT_CLR;
  mw = free_r - free_l;
  md = BOX_D - 2*EMBOSS_MARGIN;
  difference() {
    translate([MAGNET_X, MAGNET_Y, LID_H/2])
      emboss_scaled(DECAL2_FILE, DECAL2_NATIVE_W, DECAL2_NATIVE_H, mw, md);
    translate([MAGNET_X, MAGNET_Y, LID_H/2])
      cylinder(h = EMBOSS_H * 6, r = POCKET_D/2 + KEEPOUT_CLR, center = true);
    translate([TUBE_X, 0, LID_H/2])
      cylinder(h = EMBOSS_H * 6, r = COLLAR_OD/2 + KEEPOUT_CLR, center = true);
    for (p = screw_xy()) {
      translate([p[0], p[1], LID_H/2])
        cylinder(h = EMBOSS_H * 6, r = SCREW_R + 2, center = true);
    }
  }
}

module body_emboss_all() {
  emboss_front();
  emboss_rear();
  emboss_left();
  emboss_right();
  emboss_bottom();
}
