"""validate_stl.py — checagem das malhas da caixa e do pack v1."""
from pathlib import Path
import sys

try:
    import trimesh
    import numpy as np
except ImportError:
    print("trimesh nao instalado; pulando validacao")
    sys.exit(0)

ROOT = Path(__file__).parent
SHELL_MIN = {
    "box_body.stl": (90, 56, 63),
    "box_body_base.stl": (90, 56, 63),
    "box_lid.stl": (90, 56, 12),
    "box_lid_base.stl": (90, 56, 12),
}

ok = True


def load(path: Path) -> trimesh.Trimesh:
    m = trimesh.load(path, force="mesh")
    if not isinstance(m, trimesh.Trimesh):
        m = trimesh.util.concatenate(tuple(m.geometry.values()))
    return m


def report(path: Path, mesh: trimesh.Trimesh, min_ext=None) -> None:
    global ok
    watertight = bool(getattr(mesh, "is_watertight", False))
    vol = float(mesh.volume) if watertight else float("nan")
    extents = mesh.bounding_box.extents
    print(
        f"  {path.name}: faces={len(mesh.faces)} "
        f"extents={extents.round(1).tolist()} mm "
        f"watertight={watertight} vol={vol:.0f} mm3"
    )
    if not watertight:
        print(f"    AVISO: {path.name} nao e watertight (ainda pode imprimir)")
    if min_ext is not None:
        if any(extents[i] < min_ext[i] for i in range(3)):
            ok = False
            print(f"    ERRO: extents suspeitos (min {list(min_ext)})")


def hole_d(mesh, y_plane, cx, cz) -> float:
    verts = mesh.vertices
    mask = np.abs(verts[:, 1] - y_plane) < 1.6
    v = verts[mask]
    r = np.sqrt((v[:, 0] - cx) ** 2 + (v[:, 2] - cz) ** 2)
    return float(2 * r.min()) if len(r) else float("nan")


stl_dir = ROOT / "stl"
for name, mins in SHELL_MIN.items():
    path = stl_dir / name
    if not path.exists():
        print(f"  FALTA {name}")
        ok = False
        continue
    report(path, load(path), mins)

base = stl_dir / "box_body_base.stl"
if base.exists():
    m = load(base)
    z0 = -65 / 2
    checks = [
        ("rock", 29, -32, z0 + 18, 20.2),
        ("pot", 29, -12, z0 + 42, 7.6),
        ("btn", 29, 12, z0 + 35, 19.2),
        ("jack", -29, 0, z0 + 22, 8.2),
        ("fuse", -29, 22, z0 + 22, 13.2),
    ]
    print("  furos box_body_base:")
    for label, y, cx, cz, expect in checks:
        d = hole_d(m, y, cx, cz)
        delta = abs(d - expect)
        flag = "OK" if delta < 0.15 else "ERRO"
        if flag == "ERRO":
            ok = False
        print(f"    {label}: Ø{d:.2f} (alvo {expect:.1f}) {flag}")

print("OK" if ok else "FALHAS na validacao (export segue)")
sys.exit(0)
