"""vectorize_decals.py — tribal JPG → STL de relevo limpo (0.8 mm)."""
from __future__ import annotations

from pathlib import Path
import numpy as np
from PIL import Image, ImageOps, ImageFilter
import trimesh
from skimage import measure, morphology

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
OUT = ROOT
EMBOSS_H = 0.8
MAX_EDGE_MM = 1.2
MAX_EDGE_ACCEPT = 8.0

SPECS = [
    ("tribal_1", 70.0, 900),
    ("tribal_2", 45.0, 900),
    ("tribal_3", 50.0, 900),
]


def load_mask(src: Path, max_px: int) -> np.ndarray:
    im = Image.open(src).convert("L")
    w, h = im.size
    scale = max_px / max(w, h)
    if scale != 1.0:
        im = im.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.Resampling.LANCZOS)
    im = ImageOps.autocontrast(im)
    im = im.filter(ImageFilter.MedianFilter(3))
    arr = np.asarray(im, dtype=np.uint8)
    mask = arr < 160
    if mask.mean() > 0.55:
        mask = ~mask
    # fecha furos/ruido tipico de JPG tribal
    mask = morphology.binary_closing(mask, morphology.disk(2))
    mask = morphology.remove_small_objects(mask, min_size=40)
    mask = morphology.remove_small_holes(mask, area_threshold=40)
    mask[:2, :] = False
    mask[-2:, :] = False
    mask[:, :2] = False
    mask[:, -2:] = False
    return mask


def remesh_short_edges(mesh: trimesh.Trimesh, max_edge: float) -> trimesh.Trimesh:
    m = mesh.copy()
    try:
        # subdividir arestas longas
        v, f = trimesh.remesh.subdivide_to_size(
            m.vertices, m.faces, max_edge=max_edge, max_iter=8
        )
        m = trimesh.Trimesh(vertices=v, faces=f, process=True)
    except Exception as e:
        print(f"  aviso remesh: {e}")
    m.remove_unreferenced_vertices()
    try:
        m.update_faces(m.nondegenerate_faces())
        m.update_faces(m.unique_faces())
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
    return m


def mask_to_mesh(mask: np.ndarray, target_w_mm: float, height_mm: float) -> trimesh.Trimesh:
    h, w = mask.shape
    px_to_mm = target_w_mm / w
    contours = measure.find_contours(mask.astype(float), 0.5)
    if not contours:
        raise RuntimeError("Nenhum contorno encontrado")

    meshes = []
    for contour in contours:
        if len(contour) < 10:
            continue
        # simplificar (Douglas-Peucker em px)
        tol_px = max(1.0, max(h, w) * 0.0015)
        c = measure.approximate_polygon(contour, tolerance=tol_px)
        if len(c) < 4:
            continue
        # subsample se ainda grande
        if len(c) > 500:
            step = max(1, len(c) // 400)
            c = c[::step]
        ys = c[:, 0] * px_to_mm
        xs = c[:, 1] * px_to_mm
        ys = -(ys - mask.shape[0] * px_to_mm / 2)
        xs = xs - mask.shape[1] * px_to_mm / 2
        verts_2d = np.column_stack([xs, ys])
        if np.linalg.norm(verts_2d[0] - verts_2d[-1]) > 1e-6:
            verts_2d = np.vstack([verts_2d, verts_2d[0]])
        try:
            polys = trimesh.path.polygons.paths_to_polygons([verts_2d])
            if not polys:
                continue
            for p in polys:
                if p is None or p.area < 0.8:
                    continue
                m = trimesh.creation.extrude_polygon(p, height=height_mm)
                meshes.append(m)
        except Exception:
            continue

    if not meshes:
        raise RuntimeError("Falha ao extrudir contornos")

    combined = meshes[0]
    for m in meshes[1:]:
        try:
            if combined.is_volume and m.is_volume:
                combined = combined.union(m, engine="manifold")
            else:
                combined = trimesh.util.concatenate([combined, m])
        except Exception:
            combined = trimesh.util.concatenate([combined, m])

    combined.apply_translation(
        [-combined.centroid[0], -combined.centroid[1], -combined.bounds[0, 2]]
    )
    cur_w = combined.extents[0]
    if cur_w > 1e-6:
        s = target_w_mm / cur_w
        combined.apply_scale([s, s, 1.0])
        combined.apply_translation(
            [-combined.centroid[0], -combined.centroid[1], -combined.bounds[0, 2]]
        )
    combined.apply_translation([0, 0, -combined.bounds[0, 2]])
    combined = remesh_short_edges(combined, MAX_EDGE_MM)

    emax = float(combined.edges_unique_length.max()) if len(combined.edges_unique_length) else 0
    print(f"  aresta max={emax:.2f} mm (alvo < {MAX_EDGE_ACCEPT})")
    if emax > MAX_EDGE_ACCEPT:
        print("  AVISO: arestas ainda longas; remesh parcial")
    return combined


def save_preview_png(mask: np.ndarray, path: Path) -> None:
    img = Image.fromarray((~mask * 255).astype(np.uint8), mode="L")
    img.save(path)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, target_w, max_px in SPECS:
        src = SRC / f"{name}.jpg"
        if not src.exists():
            raise SystemExit(f"Falta {src}")
        print(f"Processando {name}...")
        mask = load_mask(src, max_px)
        save_preview_png(mask, OUT / f"{name}_mask.png")
        mesh = mask_to_mesh(mask, target_w, EMBOSS_H)
        stl = OUT / f"{name}_emboss.stl"
        mesh.export(stl)
        print(
            f"  {stl.name}: faces={len(mesh.faces)} "
            f"extents={mesh.bounding_box.extents.round(2).tolist()} mm "
            f"watertight={mesh.is_watertight}"
        )


if __name__ == "__main__":
    main()
