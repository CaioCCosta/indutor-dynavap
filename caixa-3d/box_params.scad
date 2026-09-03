// box_params.scad — Indutor Dynavap v3.2
// Espelha maquetes/dimensions.json (corpo 92×58×65 + tampa 8).
// Coordenadas OpenSCAD (impressão): X=largura, Y=profundidade (frente=+Y), Z=altura.

BOX_W = 92;
BOX_D = 58;
BOX_H = 65;
WALL  = 2.5;
FLOOR = 2.5;
LID_H = 8;

// Câmara (tubo) — offset à direita do centro
TUBE_X      = 28;
TUBE_HOLE_R = 8.5;   // Ø17 clearance para OD16 + folga
COLLAR_OD   = 22;
COLLAR_ID   = 17;
COLLAR_H    = 5;

// Ímã de descanso — centro da área livre da tampa (sem o bocal/collarinho)
// Área livre X: (-BOX_W/2+2) … (TUBE_X-COLLAR_OD/2-1.5) → centro ≈ -14
MAGNET_X    = -14;
MAGNET_Y    = 0;
MAGNET_D    = 12;    // disco alvo Ø12
MAGNET_H    = 3;     // espessura 3 mm (use 6 p/ boss extra)
MAGNET_CLR_D = 0.6;  // folga diametral total → pocket Ø12.6
MAGNET_CLR_H = 0.2;  // folga profundidade → 3.2 mm
POCKET_D    = MAGNET_D + MAGNET_CLR_D;
POCKET_H    = MAGNET_H + MAGNET_CLR_H;
// Se MAGNET_H > LID_H - 4, gera boss local
MAGNET_BOSS = (MAGNET_H > 3) ? (MAGNET_H - 3) : 0;

// Ventilação traseira (−Y)
VENT_N = 4;
VENT_W = 10;
VENT_H = 4;
VENT_Z = 12;         // altura do centro do slot a partir do piso interno

// Painel frontal (+Y) — Y absolutos do JSON → Z na peça
// A7 KCD1-106N redonda Ø20; A5 WH148 bushing Ø7.6; A6 Ø19.2; A9 Ø5.2
ROCK_X = -32; ROCK_Z = 18; ROCK_R = 10.1;  // Ø20.2
POT_X  = -12; POT_Z  = 42; POT_R  = 3.8;   // Ø7.6
BTN_X  =  12; BTN_Z  = 35; BTN_R  = 9.6;   // Ø19.2
LED1_X =  28; LED1_Z = 48; LED_R  = 2.6;   // Ø5.2
LED2_X =  38; LED2_Z = 48;

// Jack DC-022 Ø8.2 + porta-fusível 5×20 painel Ø13.2 (traseira −Y)
JACK_X = 0;  JACK_Z = 22; JACK_R = 4.1;
FUSE_X = 22; FUSE_Z = 22; FUSE_R = 6.6;

// Parafusos tampa M3 (furos 3.4 mm)
SCREW_R = 1.7;
SCREW_INSET = 6;     // margem da borda até centro do furo
LIP_H = 2;           // ressalto interno da tampa (encaixe)
LIP_CLR = 0.3;       // folga do lip vs interno

// ── Alto relevo tribal (decals/*.stl) ──
EMBOSS_H      = 0.8;   // altura do relevo (mm) — camada extra p/ filament claro
EMBOSS_MARGIN = 2.0;   // margem mínima das arestas (preencher área livre)
BOTTOM_PAD_H  = 1.0;   // pads nos cantos (assento estável)
KEEPOUT_CLR   = 1.5;   // folga ao redor de furos

// Larguras alvo dos STL gerados (ver vectorize_decals.py)
DECAL1_W = 70;   // laterais — escala por face
DECAL2_W = 36;   // tampa — área livre (sem bocal); ímã no centro
DECAL3_W = 42;   // base — cabe em 92×58 com margem

$fn = 48;

function screw_xy() = [
  [ BOX_W/2 - SCREW_INSET,  BOX_D/2 - SCREW_INSET],
  [-BOX_W/2 + SCREW_INSET,  BOX_D/2 - SCREW_INSET],
  [ BOX_W/2 - SCREW_INSET, -BOX_D/2 + SCREW_INSET],
  [-BOX_W/2 + SCREW_INSET, -BOX_D/2 + SCREW_INSET]
];
