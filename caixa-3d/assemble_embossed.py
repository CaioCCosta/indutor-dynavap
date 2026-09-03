"""assemble_embossed.py — v1 fechada: une relevos AMS (print/v1) e gera cavas + inserts (print/v1-cavas)."""
from __future__ import annotations

from pathlib import Path
import numpy as np
import trimesh
from trimesh.transformations import rotation_matrix

ROOT = Path(__file__).resolve().parent
DEC = ROOT / "decals"
STL = ROOT / "stl"

BOX_W, BOX_D, BOX_H = 92.0, 58.0, 65.0
LID_H = 8.0
EMBOSS_MARGIN = 2.0
BOTTOM_PAD_H = 1.0
KEEPOUT = 1.5
SINK = 0.3  # mm para dentro da parede — evita boolean coplanar (malha aranha)
CAVITY_D = 0.6  # profundidade da cava (pack v1-cavas)
INSERT_H = 0.5  # espessura do insert para colar
GLUE_CLR = 0.15  # folga XY do insert vs cava
MAGNET_X, MAGNET_Y, TUBE_X = -14.0, 0.0, 28.0
POCKET_R = 12.6 / 2
COLLAR_R = 22.0 / 2
SCREW_INSET = 6.0
SCREW_R = 1.7

DECAL1_NATIVE = (70.0, 28.5)
DECAL2_NATIVE = (45.0, 41.3)
DECAL3_NATIVE = (50.0, 80.6)


def translation(xyz):
    T = np.eye(4)
    T[:3, 3] = xyz
    return T


def Rx(deg):
    return rotation_matrix(np.radians(deg), [1, 0, 0])


def Ry(deg):
    return rotation_matrix(np.radians(deg), [0, 1, 0])


def Rz(deg):
    return rotation_matrix(np.radians(deg), [0, 0, 1])


def mul(*mats):
    out = np.eye(4)
    for m in mats:
        out = out @ m
    return out


def load_decal(name: str) -> trimesh.Trimesh:
    m = trimesh.load(DEC / f"{name}_emboss.stl", force="mesh")
    if not isinstance(m, trimesh.Trimesh):
        m = trimesh.util.concatenate(tuple(m.geometry.values()))
    return ensure_volume(m)


def ensure_volume(m: trimesh.Trimesh) -> trimesh.Trimesh:
    m = m.copy()
    m.remove_unreferenced_vertices()
    try:
        m.update_faces(m.unique_faces())
        m.update_faces(m.nondegenerate_faces())
    except Exception:
        pass
    if not m.is_watertight:
        try:
            m.fill_holes()
        except Exception:
            pass
    try:
        m.fix()
    except Exception:
        pass
    # Se ainda nao for volume, extrude um pouco via voxel merge nao — aceita concatenacao
    return m


def scale_to_fit(mesh: trimesh.Trimesh, native_wh, max_w, max_h) -> trimesh.Trimesh:
    nw, nh = native_wh
    s = min(max_w / nw, max_h / nh)
    m = mesh.copy()
    m.apply_scale([s, s, 1.0])
    m.apply_translation([0, 0, -m.bounds[0, 2]])
    return m


def place(mesh: trimesh.Trimesh, T) -> trimesh.Trimesh:
    m = mesh.copy()
    m.apply_transform(T)
    return m


def safe_union(a: trimesh.Trimesh, b: trimesh.Trimesh) -> trimesh.Trimesh:
    try:
        a2, b2 = ensure_volume(a), ensure_volume(b)
        if a2.is_volume and b2.is_volume:
            return a2.union(b2, engine="manifold")
    except Exception as e:
        print(f"  aviso union: {e}")
    return trimesh.util.concatenate([a, b])


def safe_difference(a: trimesh.Trimesh, b: trimesh.Trimesh) -> trimesh.Trimesh:
    try:
        a2, b2 = ensure_volume(a), ensure_volume(b)
        if a2.is_volume and b2.is_volume:
            return a2.difference(b2, engine="manifold")
    except Exception as e:
        print(f"  aviso difference: {e}")
    return a


def to_insert_flat(fitted: trimesh.Trimesh) -> trimesh.Trimesh:
    """Silhueta deitada na cama, um pouco menor que a cava, 0,5 mm de espessura."""
    m = fitted.copy()
    span = max(float(m.extents[0]), float(m.extents[1]), 1.0)
    s = max(0.90, 1.0 - (2.0 * GLUE_CLR) / span)
    c = m.centroid.copy()
    m.apply_translation(-c)
    hz = float(m.extents[2]) or 0.8
    m.apply_scale([s, s, INSERT_H / hz])
    m.apply_translation([0.0, 0.0, -m.bounds[0, 2]])
    return ensure_volume(m)


def punch_keepouts_xy_plane(emboss: trimesh.Trimesh, centers_r, axis: str) -> trimesh.Trimesh:
    """Remove material do relevo sob cilindros (furos). axis: 'y' front/rear, 'z' lid."""
    m = emboss
    for item in centers_r:
        if axis == "y":
            x, y, z, r = item
            c = trimesh.creation.cylinder(radius=r, height=12, sections=32)
            c.apply_transform(mul(translation([x, y, z]), Rx(90)))
        else:
            x, y, z, r = item
            c = trimesh.creation.cylinder(radius=r, height=8, sections=32)
            c.apply_translation([x, y, z])
        try:
            if m.is_volume and ensure_volume(c).is_volume:
                m = m.difference(c, engine="manifold")
        except Exception:
            pass
    return m


def build_body_emboss() -> list:
    d1 = load_decal("tribal_1")
    parts = []

    mw, mh = BOX_W - 2 * EMBOSS_MARGIN, BOX_H - 2 * EMBOSS_MARGIN
    z0 = -BOX_H / 2

    # Front (+Y): sink into wall (Y -= SINK)
    front = scale_to_fit(d1, DECAL1_NATIVE, mw, mh)
    front = place(front, mul(translation([0, BOX_D / 2 - SINK, 0]), Rx(-90)))
    # Keepouts = box_params (A5/A6/A7/A9)
    front_cuts = [
        (-32, BOX_D / 2, z0 + 18, 10.1 + KEEPOUT),  # ROCK Ø20.2
        (12, BOX_D / 2, z0 + 35, 9.6 + KEEPOUT),    # BTN Ø19.2
        (-12, BOX_D / 2, z0 + 42, 3.8 + KEEPOUT),   # POT Ø7.6
        (28, BOX_D / 2, z0 + 48, 2.6 + KEEPOUT),    # LED1
        (38, BOX_D / 2, z0 + 48, 2.6 + KEEPOUT),    # LED2
    ]
    front = punch_keepouts_xy_plane(front, front_cuts, "y")
    parts.append(front)

    # Rear (-Y): sink Y += SINK
    rear = scale_to_fit(d1, DECAL1_NATIVE, mw, mh)
    rear = place(rear, mul(translation([0, -BOX_D / 2 + SINK, 0]), Rx(90)))
    rear_cuts = [
        (0, -BOX_D / 2, z0 + 22, 4.1 + KEEPOUT),   # JACK Ø8.2
        (22, -BOX_D / 2, z0 + 22, 6.6 + KEEPOUT),  # FUSE Ø13.2
    ]
    rear = punch_keepouts_xy_plane(rear, rear_cuts, "y")
    parts.append(rear)

    # Left / Right
    mw2, mh2 = BOX_D - 2 * EMBOSS_MARGIN, BOX_H - 2 * EMBOSS_MARGIN
    left = scale_to_fit(d1, DECAL1_NATIVE, mw2, mh2)
    # -X face: sink X += SINK
    parts.append(
        place(left, mul(translation([-BOX_W / 2 + SINK, 0, 0]), Ry(-90), Rz(90)))
    )
    right = scale_to_fit(d1, DECAL1_NATIVE, mw2, mh2)
    # +X face: sink X -= SINK
    parts.append(
        place(right, mul(translation([BOX_W / 2 - SINK, 0, 0]), Ry(90), Rz(-90)))
    )

    # Bottom (-Z): sink Z += SINK; Rz(90) → eixo longo // BOX_W (vertical na placa)
    d3 = load_decal("tribal_3")
    bottom = scale_to_fit(d3, DECAL3_NATIVE, BOX_D - 8, BOX_W - 8)
    parts.append(
        place(bottom, mul(translation([0, 0, -BOX_H / 2 + SINK]), Rx(180), Rz(90)))
    )

    tribals = parts[:]
    pads = []
    for sx in (1, -1):
        for sy in (1, -1):
            pad = trimesh.creation.cylinder(radius=4, height=BOTTOM_PAD_H, sections=24)
            pad.apply_translation(
                [
                    sx * (BOX_W / 2 - SCREW_INSET),
                    sy * (BOX_D / 2 - SCREW_INSET),
                    -BOX_H / 2 - BOTTOM_PAD_H / 2,
                ]
            )
            pads.append(pad)
    return tribals, pads


def build_lid_emboss() -> list:
    d2 = load_decal("tribal_2")
    # Área livre da tampa: esquerda até o collarinho do bocal; ímã no centro
    free_l = -BOX_W / 2 + EMBOSS_MARGIN
    free_r = TUBE_X - COLLAR_R - KEEPOUT
    mw = free_r - free_l
    md = BOX_D - 2 * EMBOSS_MARGIN
    top = scale_to_fit(d2, DECAL2_NATIVE, mw, md)
    top = place(top, translation([MAGNET_X, MAGNET_Y, LID_H / 2]))
    cuts = [
        (MAGNET_X, 0, LID_H / 2 + 0.4, POCKET_R + KEEPOUT),
        (TUBE_X, 0, LID_H / 2 + 0.4, COLLAR_R + KEEPOUT),
    ]
    for sx in (1, -1):
        for sy in (1, -1):
            cuts.append(
                (
                    sx * (BOX_W / 2 - SCREW_INSET),
                    sy * (BOX_D / 2 - SCREW_INSET),
                    LID_H / 2 + 0.4,
                    SCREW_R + 2,
                )
            )
    top = punch_keepouts_xy_plane(top, cuts, "z")
    return [top]


def assemble(base_path: Path, extra_parts: list, out_path: Path) -> None:
    print(f"Montando {out_path.name}...")
    base = trimesh.load(base_path, force="mesh")
    if not isinstance(base, trimesh.Trimesh):
        base = trimesh.util.concatenate(tuple(base.geometry.values()))
    result = ensure_volume(base)
    for i, p in enumerate(extra_parts):
        if p is None or len(getattr(p, "faces", [])) == 0:
            print(f"  skip part {i}")
            continue
        print(f"  union part {i}: faces={len(p.faces)} extents={np.round(p.extents, 1)}")
        result = safe_union(result, p)
    result.export(out_path)
    print(
        f"  OK {out_path.name}: faces={len(result.faces)} "
        f"extents={np.round(result.extents, 1).tolist()} "
        f"watertight={result.is_watertight}"
    )


def export_decal(parts: list, out_path: Path) -> None:
    meshes = [p for p in parts if p is not None and len(getattr(p, "faces", [])) > 0]
    if not meshes:
        return
    m = trimesh.util.concatenate(meshes)
    m.export(out_path)
    print(f"  decal {out_path.name}: faces={len(m.faces)} extents={np.round(m.extents, 1)}")


def export_dual_3mf(dark: trimesh.Trimesh, light: trimesh.Trimesh, out_path: Path) -> None:
    try:
        scene = trimesh.Scene()
        scene.add_geometry(dark, node_name="caixa_escura")
        scene.add_geometry(light, node_name="decal_claro")
        scene.export(out_path)
        print(f"  3MF dual {out_path.name}")
    except Exception as e:
        print(f"  aviso 3MF: {e}")


def export_print_v1(body_dark, body_light, lid_dark, lid_light) -> None:
    out = ROOT / "print" / "v1"
    out.mkdir(parents=True, exist_ok=True)
    mapping = [
        (body_dark, out / "corpo_cor1.stl"),
        (body_light, out / "corpo_cor2.stl"),
        (lid_dark, out / "tampa_cor1.stl"),
        (lid_light, out / "tampa_cor2.stl"),
    ]
    for mesh, path in mapping:
        mesh.export(path)
        print(f"  print/v1 {path.name}: faces={len(mesh.faces)} extents={np.round(mesh.extents, 1)}")


def export_print_lisa(body_dark, lid_dark) -> None:
    """Casca lisa (sem tribal): corpo + pads, tampa base."""
    out = ROOT / "print" / "v1-lisa"
    out.mkdir(parents=True, exist_ok=True)
    for mesh, path in [
        (body_dark, out / "corpo_liso.stl"),
        (lid_dark, out / "tampa_lisa.stl"),
    ]:
        mesh.export(path)
        print(f"  print/v1-lisa {path.name}: faces={len(mesh.faces)} extents={np.round(mesh.extents, 1)}")


def flatten_world_decal(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    m = mesh.copy()
    ax = int(np.argmin(m.extents))
    if ax == 0:
        m.apply_transform(Ry(90))
    elif ax == 1:
        m.apply_transform(Rx(90))
    m.apply_translation(-m.centroid)
    return to_insert_flat(m)


def pack_flats(named: list, out_path: Path) -> None:
    x = 0.0
    packed = []
    for _name, m in named:
        p = m.copy()
        p.apply_translation([x - p.bounds[0, 0], -p.bounds[0, 1], -p.bounds[0, 2]])
        packed.append(p)
        x = p.bounds[1, 0] + 8.0
    trimesh.util.concatenate(packed).export(out_path)
    print(f"  {out_path.name}: {len(named)} inserts")


def assemble_cavities(base_path: Path, cutters: list, pads: list, out_path: Path) -> trimesh.Trimesh:
    print(f"Cavas {out_path.name}...")
    base = trimesh.load(base_path, force="mesh")
    if not isinstance(base, trimesh.Trimesh):
        base = trimesh.util.concatenate(tuple(base.geometry.values()))
    result = ensure_volume(base)
    for p in pads:
        result = safe_union(result, p)
    for i, c in enumerate(cutters):
        if c is None:
            continue
        print(f"  cava {i}: faces={len(c.faces)}")
        result = safe_difference(result, c)
    result.export(out_path)
    print(
        f"  OK {out_path.name}: faces={len(result.faces)} "
        f"watertight={result.is_watertight}"
    )
    return result


def export_print_cavas(tribals: list, lid_tribals: list, pads: list) -> None:
    """Pack paralelo a v1: casca com cava + inserts deitados (colar). Não sobrescreve print/v1."""
    out = ROOT / "print" / "v1-cavas"
    out.mkdir(parents=True, exist_ok=True)
    extra = CAVITY_D - SINK
    body_cut = [
        place(tribals[0], translation([0, -extra, 0])),
        place(tribals[1], translation([0, extra, 0])),
        place(tribals[2], translation([extra, 0, 0])),
        place(tribals[3], translation([-extra, 0, 0])),
        place(tribals[4], translation([0, 0, extra])),
    ]
    lid_cut = [place(lid_tribals[0], translation([0, 0, -CAVITY_D]))]
    assemble_cavities(STL / "box_body_base.stl", body_cut, pads, out / "corpo_cava.stl")
    assemble_cavities(STL / "box_lid_base.stl", lid_cut, [], out / "tampa_cava.stl")

    names = ["frente", "tras", "esq", "dir", "base", "tampa"]
    meshes_3d = tribals + lid_tribals
    flats = []
    for name, m in zip(names, meshes_3d):
        flat = flatten_world_decal(m)
        dest = out / f"decal_{name}.stl"
        flat.export(dest)
        print(f"  insert {dest.name}: extents={np.round(flat.extents, 2)}")
        flats.append((name, flat))
    pack_flats(flats, out / "decais.stl")


def main() -> None:
    body_base_path = STL / "box_body_base.stl"
    lid_base_path = STL / "box_lid_base.stl"
    if not body_base_path.exists() or not lid_base_path.exists():
        raise SystemExit("Rode export.ps1 (OpenSCAD) antes para gerar *_base.stl")

    tribals, pads = build_body_emboss()
    assemble(body_base_path, tribals + pads, STL / "box_body.stl")
    export_decal(tribals, STL / "box_body_decal.stl")

    lid_tribals = build_lid_emboss()
    assemble(lid_base_path, lid_tribals, STL / "box_lid.stl")
    export_decal(lid_tribals, STL / "box_lid_decal.stl")

    body_dark = trimesh.load(body_base_path, force="mesh")
    if not isinstance(body_dark, trimesh.Trimesh):
        body_dark = trimesh.util.concatenate(tuple(body_dark.geometry.values()))
    for p in pads:
        body_dark = safe_union(body_dark, p)
    lid_dark = trimesh.load(lid_base_path, force="mesh")
    if not isinstance(lid_dark, trimesh.Trimesh):
        lid_dark = trimesh.util.concatenate(tuple(lid_dark.geometry.values()))
    body_light = trimesh.load(STL / "box_body_decal.stl", force="mesh")
    lid_light = trimesh.load(STL / "box_lid_decal.stl", force="mesh")
    export_dual_3mf(body_dark, body_light, STL / "box_body_dual.3mf")
    export_dual_3mf(lid_dark, lid_light, STL / "box_lid_dual.3mf")
    export_print_v1(body_dark, body_light, lid_dark, lid_light)
    export_print_lisa(body_dark, lid_dark)
    export_print_cavas(tribals, lid_tribals, pads)


if __name__ == "__main__":
    main()
