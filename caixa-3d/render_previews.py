"""render_previews.py — previews shaded + ortograficas por face (sem teia falsa)."""
from __future__ import annotations

from pathlib import Path
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "stl" / "previews"
OUT.mkdir(parents=True, exist_ok=True)


def matplotlib_iso(mesh: trimesh.Trimesh, path: Path, elev: float, azim: float) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    # Prefer faces with reasonable aspect (skip giant base slivers in preview)
    faces = mesh.faces
    tris = mesh.vertices[faces]
    edge = np.linalg.norm(tris[:, 1] - tris[:, 0], axis=1)
    edge = np.maximum(edge, np.linalg.norm(tris[:, 2] - tris[:, 1], axis=1))
    edge = np.maximum(edge, np.linalg.norm(tris[:, 0] - tris[:, 2], axis=1))
    keep = edge < 12.0
    if keep.sum() < 500:
        keep = np.ones(len(faces), dtype=bool)
    tris = tris[keep]
    if len(tris) > 14000:
        idx = np.linspace(0, len(tris) - 1, 14000, dtype=int)
        tris = tris[idx]

    normals = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    nlen = np.linalg.norm(normals, axis=1) + 1e-9
    normals = normals / nlen[:, None]
    light = np.array([0.35, 0.45, 0.8])
    light /= np.linalg.norm(light)
    intensity = np.clip(normals @ light, 0.2, 1.0)
    colors = np.clip(np.array([0.5, 0.58, 0.68]) * intensity[:, None], 0, 1)

    fig = plt.figure(figsize=(10, 8), facecolor="#1a202c")
    ax = fig.add_subplot(111, projection="3d")
    ax.set_facecolor("#1a202c")
    coll = Poly3DCollection(tris, linewidths=0, edgecolors="none")
    coll.set_facecolor(colors)
    ax.add_collection3d(coll)
    c = mesh.bounding_box.centroid
    span = mesh.extents.max() / 2 * 1.05
    ax.set_xlim(c[0] - span, c[0] + span)
    ax.set_ylim(c[1] - span, c[1] + span)
    ax.set_zlim(c[2] - span, c[2] + span)
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    ax.set_box_aspect([1, 1, 1])
    fig.tight_layout(pad=0)
    fig.savefig(path, dpi=140, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {path.name}")


def face_ortho(mesh: trimesh.Trimesh, path: Path, axis: str, sign: float, band: float = 2.0) -> None:
    """Projecao ortografica da casca perto de uma face — mostra relevo tribal."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    bounds = mesh.bounds
    center = mesh.bounding_box.centroid
    if axis == "x":
        plane = bounds[1, 0] if sign > 0 else bounds[0, 0]
        mask = np.abs(mesh.triangles_center[:, 0] - plane) < band
        u, v = 1, 2  # YZ
        title = f"{'right' if sign>0 else 'left'} (+X)" if sign > 0 else "left (-X)"
    elif axis == "y":
        plane = bounds[1, 1] if sign > 0 else bounds[0, 1]
        mask = np.abs(mesh.triangles_center[:, 1] - plane) < band
        u, v = 0, 2  # XZ
        title = "front (+Y)" if sign > 0 else "rear (-Y)"
    else:
        plane = bounds[0, 2] if sign < 0 else bounds[1, 2]
        mask = np.abs(mesh.triangles_center[:, 2] - plane) < band
        u, v = 0, 1  # XY
        title = "bottom (-Z)" if sign < 0 else "top (+Z)"

    cents = mesh.triangles_center[mask]
    if len(cents) < 20:
        print(f"  skip {path.name}: poucos tris")
        return

    fig, ax = plt.subplots(figsize=(9, 7), facecolor="#1a202c")
    ax.set_facecolor("#1a202c")
    # depth cue: distance from outer plane
    if axis == "x":
        depth = np.abs(cents[:, 0] - plane)
    elif axis == "y":
        depth = np.abs(cents[:, 1] - plane)
    else:
        depth = np.abs(cents[:, 2] - plane)
    sc = ax.scatter(cents[:, u], cents[:, v], c=depth, s=1.2, cmap="viridis", alpha=0.9)
    ax.set_aspect("equal")
    ax.set_title(title, color="white")
    ax.tick_params(colors="white")
    for spine in ax.spines.values():
        spine.set_color("#4a5568")
    fig.colorbar(sc, ax=ax, fraction=0.03, pad=0.02)
    fig.savefig(path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {path.name} (n={len(cents)})")


def main() -> None:
    body = trimesh.load(ROOT / "stl" / "box_body.stl", force="mesh")
    lid = trimesh.load(ROOT / "stl" / "box_lid.stl", force="mesh")
    if not isinstance(body, trimesh.Trimesh):
        body = trimesh.util.concatenate(tuple(body.geometry.values()))
    if not isinstance(lid, trimesh.Trimesh):
        lid = trimesh.util.concatenate(tuple(lid.geometry.values()))

    print("ISO previews...")
    matplotlib_iso(body, OUT / "body_iso.png", 25, 45)
    matplotlib_iso(body, OUT / "body_front.png", 8, 90)
    matplotlib_iso(body, OUT / "body_side.png", 12, 0)
    matplotlib_iso(body, OUT / "body_bottom.png", -65, 40)
    matplotlib_iso(lid, OUT / "lid_top.png", 78, 40)
    matplotlib_iso(lid, OUT / "lid_iso.png", 35, 40)

    print("Face orthos (relevo)...")
    face_ortho(body, OUT / "ortho_front.png", "y", +1)
    face_ortho(body, OUT / "ortho_rear.png", "y", -1)
    face_ortho(body, OUT / "ortho_left.png", "x", -1)
    face_ortho(body, OUT / "ortho_right.png", "x", +1)
    face_ortho(body, OUT / "ortho_bottom.png", "z", -1)
    face_ortho(lid, OUT / "ortho_lid.png", "z", +1)

    # Stats for accept
    e = body.edges_unique_length
    print(
        f"body faces={len(body.faces)} watertight={body.is_watertight} "
        f"edge p95={np.percentile(e,95):.2f} max={e.max():.2f}"
    )
    print("OK", sorted(p.name for p in OUT.glob("*.png")))


if __name__ == "__main__":
    main()
