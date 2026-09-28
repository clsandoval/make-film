#!/usr/bin/env python3
"""Key magenta out of raw cut-out sheets and slice them into single pieces.

raw/<name>.png (cutout kind)  -> cut/<name>_<k>.png  (RGBA, trimmed, reading order)
raw/<name>.png (plate kind)   -> cut/<name>.jpg      (1920x1080 cover crop)
Also writes cut/<name>_index.png: the pieces laid out with their k labels.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

ASSETS = {}

HERE = Path(__file__).parent
RAW, CUT = HERE / "raw", HERE / "cut"
CUT.mkdir(exist_ok=True)


def key(img: Image.Image) -> Image.Image:
    a = np.asarray(img.convert("RGB")).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    # how much of the pixel is magenta: strong R and B, weak G
    m = np.clip((np.minimum(r, b) - g - 40) / 150, 0, 1)
    # pure background
    m[(r > 200) & (b > 200) & (g < 80)] = 1
    alpha = 1 - m
    # un-mix the magenta from the edge pixels
    mag = np.array([255, 0, 255], np.float32)
    rgb = (a - m[..., None] * mag) / np.maximum(alpha[..., None], 1e-3)
    rgb = np.clip(rgb, 0, 255)
    out = np.dstack([rgb, alpha * 255]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def slice_sheet(name: str, min_area: int = 2500) -> list[Path]:
    im = key(Image.open(RAW / f"{name}.png"))
    al = np.asarray(im)[..., 3] > 40
    closed = ndimage.binary_closing(al, iterations=3)
    lab, n = ndimage.label(closed)
    boxes = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        area = int((lab[sl] == i).sum())
        if area < min_area:
            continue
        boxes.append((sl, i))
    # reading order: rows by centre y (tolerance 12% of height), then x
    H = al.shape[0]
    boxes.sort(key=lambda b: (round(((b[0][0].start + b[0][0].stop) / 2) / (H * 0.12)), b[0][1].start))
    arr = np.asarray(im).copy()
    out = []
    for k, (sl, i) in enumerate(boxes):
        piece = arr[sl].copy()
        piece[..., 3] = np.where(lab[sl] == i, piece[..., 3], 0)
        pad = 6
        p = np.zeros((piece.shape[0] + 2 * pad, piece.shape[1] + 2 * pad, 4), np.uint8)
        p[pad:-pad, pad:-pad] = piece
        path = CUT / f"{name}_{k}.png"
        Image.fromarray(p, "RGBA").save(path)
        out.append(path)
    # labelled index for review
    idx = im.copy().convert("RGBA")
    bg = Image.new("RGBA", idx.size, (90, 90, 90, 255))
    bg.alpha_composite(idx)
    d = ImageDraw.Draw(bg)
    for k, (sl, i) in enumerate(boxes):
        d.rectangle([sl[1].start, sl[0].start, sl[1].stop, sl[0].stop], outline=(255, 255, 0), width=3)
        d.text((sl[1].start + 8, sl[0].start + 6), str(k), fill=(255, 255, 0))
    bg.convert("RGB").save(CUT / f"{name}_index.jpg", quality=80)
    return out


def plate(name: str) -> Path:
    im = Image.open(RAW / f"{name}.png").convert("RGB")
    W, H = 1920, 1080
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - W) // 2, (im.height - H) // 2
    path = CUT / f"{name}.jpg"
    im.crop((x, y, x + W, y + H)).save(path, quality=92)
    return path


if __name__ == "__main__":
    names = sys.argv[1:] or [p.stem for p in RAW.glob("*.png")]
    for n in names:
        kind = ASSETS.get(n, ("cutout",))[0]
        if kind == "plate":
            print(n, "->", plate(n).name)
        else:
            print(n, "->", len(slice_sheet(n)), "pieces")
