#!/usr/bin/env python3
"""validate_layout.py — AABB + âncoras box_params vs maquetes/dimensions.json v1.1"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIMS = ROOT / "maquetes" / "dimensions.json"
PARAMS = ROOT / "caixa-3d" / "box_params.scad"

INNER = {"X": (-43.5, 43.5), "Y": (2.5, 62.5), "Z": (-26.5, 26.5)}


def aabb_box(pos, size):
    x, y, z = pos
    sx, sy, sz = size
    return (x - sx / 2, x + sx / 2, y - sy / 2, y + sy / 2, z - sz / 2, z + sz / 2)


def overlap(a, b, eps=0.05):
    return not (
        a[1] <= b[0] + eps
        or b[1] <= a[0] + eps
        or a[3] <= b[2] + eps
        or b[3] <= a[2] + eps
        or a[5] <= b[4] + eps
        or b[5] <= a[4] + eps
    )


def parse_scad(text: str) -> dict:
    out = {}
    for name in (
        "ROCK_X", "ROCK_Z", "POT_X", "POT_Z", "BTN_X", "BTN_Z",
        "LED1_X", "LED1_Z", "LED2_X", "LED2_Z",
        "JACK_X", "JACK_Z", "FUSE_X", "FUSE_Z",
        "TUBE_X", "MAGNET_X", "BOX_W", "BOX_D", "BOX_H", "LID_H",
    ):
        m = re.search(rf"{name}\s*=\s*([-\d.]+)", text)
        if m:
            out[name] = float(m.group(1))
    return out


def main() -> int:
    data = json.loads(DIMS.read_text(encoding="utf-8"))
    scad = parse_scad(PARAMS.read_text(encoding="utf-8"))
    fails = []

    # Anchors
    ph = data["box"]["panelHoles"]
    front = {h["id"]: h for h in ph["front"]}
    rear = {h["id"]: h for h in ph["rear"]}
    checks = [
        ("rocker.x", front["rocker"]["x"], scad["ROCK_X"]),
        ("rocker.y", front["rocker"]["y"], scad["ROCK_Z"]),
        ("pot.x", front["pot"]["x"], scad["POT_X"]),
        ("pot.y", front["pot"]["y"], scad["POT_Z"]),
        ("button.x", front["button"]["x"], scad["BTN_X"]),
        ("button.y", front["button"]["y"], scad["BTN_Z"]),
        ("led1.x", front["led1"]["x"], scad["LED1_X"]),
        ("led2.x", front["led2"]["x"], scad["LED2_X"]),
        ("jack.x", rear["jack"]["x"], scad["JACK_X"]),
        ("fuse.x", rear["fuse"]["x"], scad["FUSE_X"]),
        ("tube.x", ph["top_tube"]["x"], scad["TUBE_X"]),
        ("magnet.x", data["box"]["lid"]["magnetPocket"]["x"], scad["MAGNET_X"]),
        ("box.w", data["box"]["body"]["w"], scad["BOX_W"]),
        ("box.d", data["box"]["body"]["d"], scad["BOX_D"]),
        ("box.h", data["box"]["body"]["h"], scad["BOX_H"]),
        ("lid.h", data["box"]["lid"]["h"], scad["LID_H"]),
    ]
    for name, a, b in checks:
        if abs(a - b) > 0.05:
            fails.append(f"anchor {name}: json={a} scad={b}")

    comps = {c["id"]: c for c in data["components"]}
    if "fuse_holder" in comps:
        fails.append("fuse_holder still present (should be panel-only)")

    # Hard AABB among electronics boxes
    boxes = []
    for cid in ("zvs", "mosfet", "nano", "tmp36"):
        c = comps[cid]
        boxes.append((cid, aabb_box(c["pos"], c["size"])))

    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            if overlap(boxes[i][1], boxes[j][1]):
                fails.append(f"AABB overlap {boxes[i][0]} x {boxes[j][0]}")

    # Coil ID vs tube OD
    coil = comps["coil"]
    id_mm = 2 * (coil["radius"] - coil["tube"])
    if id_mm + 1e-6 < 16.0:
        fails.append(f"coil ID {id_mm:.2f} < tube OD 16")

    # Bed height
    bed = comps["stopper"]
    if abs(bed["height"] - 8.0) > 0.05:
        fails.append(f"bed height {bed['height']} != 8")

    # Nano catalog height
    nano = comps["nano"]
    if abs(nano["size"][1] - 11.0) > 0.05:
        fails.append(f"nano H {nano['size'][1]} != 11")

    # ZVS inside / gaps
    z = comps["zvs"]
    za = aabb_box(z["pos"], z["size"])
    if za[0] < INNER["X"][0] - 0.05 or za[1] > INNER["X"][1] + 0.05:
        fails.append("ZVS outside inner X")
    left_gap = za[0] - INNER["X"][0]
    if left_gap < 3.0 - 0.05:
        fails.append(f"ZVS left wall gap {left_gap:.2f} < 3")
    tube_left = 28.0 - 8.0
    zvs_tube = tube_left - za[1]
    if zvs_tube < 2.0 - 0.05:
        fails.append(f"ZVS–tube gap {zvs_tube:.2f} < 2")

    mos = comps["mosfet"]
    ma = aabb_box(mos["pos"], mos["size"])
    standoff = ma[2] - za[3]
    if standoff < 2.0 - 0.05:
        fails.append(f"MOSFET–ZVS Y standoff {standoff:.2f} < 2")

    # Documented clearance_checks ok flags
    for c in data.get("clearance_checks", []):
        if c.get("ok") is False:
            fails.append(f"clearance_checks marked fail: {c['name']}")

    print(f"components: {len(comps)}")
    print(f"anchors checked: {len(checks)}")
    if fails:
        print("FAIL:")
        for f in fails:
            print(" -", f)
        return 1
    print("OK - anchors match box_params; no hard AABB among zvs/mosfet/nano/tmp36; coil ID>=16; bed h=8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
