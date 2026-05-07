"""
fix_images.py — Extrae las fotos base64 del menú HTML, detecta verticales,
las rota+recorta al aspect ratio del slot CSS, y reemplaza in-place.

Uso:
    python fix_images.py
"""
from __future__ import annotations
import base64
import io
import re
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).parent
HTML_PATH = ROOT / "index.html"
SOURCE_HTML = ROOT / "original.html"  # always start from pristine original
EXTRACTED = ROOT / "extracted"
FIXED = ROOT / "fixed"

# Manual rotation map (by slot index, 0-based).
# Positive = counter-clockwise, negative = clockwise (PIL convention).
# Determined by visual inspection of extracted/ folder.
MANUAL_ROTATIONS = {
    2: -90,  # 03_food_og_a — cerveza
    3: -90,  # 04_food_og_b — burger en canasta verde
    4: -90,  # 05_food_dirty — burger + cerveza
    6: -90,  # 07_food_katsu_detail — katsu en caja kraft
    7: -90,  # 08_footer — fachada El Tap
}

DATA_URI_RE = re.compile(
    rb'data:image/(?P<fmt>png|jpeg|jpg|webp);base64,(?P<data>[A-Za-z0-9+/=]+)'
)

@dataclass
class Slot:
    name: str
    aspect_w: int
    aspect_h: int

SLOTS = [
    Slot("01_hero",              16, 10),
    Slot("02_special_alitas",     4,  3),
    Slot("03_food_og_a",         16, 10),
    Slot("04_food_og_b",          4,  3),
    Slot("05_food_dirty",         4,  3),
    Slot("06_food_katsu_main",    4,  3),
    Slot("07_food_katsu_detail",  4,  3),
    Slot("08_footer",            16, 10),
]

def crop_to_aspect(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    w, h = img.size
    target_ratio = target_w / target_h
    current_ratio = w / h
    if abs(current_ratio - target_ratio) < 0.01:
        return img
    if current_ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    new_h = int(w / target_ratio)
    top = (h - new_h) // 2
    return img.crop((0, top, w, top + new_h))

def encode_jpeg(img: Image.Image, quality: int = 85, max_width: int = 1600) -> bytes:
    if img.mode != "RGB":
        img = img.convert("RGB")
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True, progressive=True)
    return buf.getvalue()

def main():
    EXTRACTED.mkdir(exist_ok=True)
    FIXED.mkdir(exist_ok=True)
    # Always work from the pristine original to allow re-runs without quality loss
    source = SOURCE_HTML if SOURCE_HTML.exists() else HTML_PATH
    html = source.read_bytes()

    matches = list(DATA_URI_RE.finditer(html))
    print(f"Found {len(matches)} base64 images in HTML")
    if len(matches) != len(SLOTS):
        print(f"WARNING: expected {len(SLOTS)} images, got {len(matches)}")

    print(f"\n{'#':<3} {'Slot':<24} {'Original':<22} {'Final':<22} {'KB':>8}")
    print("-" * 85)

    new_html = bytearray()
    last_end = 0
    for i, m in enumerate(matches):
        slot = SLOTS[i] if i < len(SLOTS) else Slot(f"img_{i:02d}", 4, 3)
        raw = base64.b64decode(m.group("data"))
        img = Image.open(io.BytesIO(raw))
        img = ImageOps.exif_transpose(img)
        ow, oh = img.size
        was_vertical = oh > ow

        ext = "jpg"
        (EXTRACTED / f"{slot.name}.{ext}").write_bytes(encode_jpeg(img, quality=92))

        rotation = MANUAL_ROTATIONS.get(i, 0)
        if rotation:
            img = img.rotate(rotation, expand=True)
        elif was_vertical:
            img = img.rotate(-90, expand=True)

        img = crop_to_aspect(img, slot.aspect_w, slot.aspect_h)
        fw, fh = img.size

        jpeg_bytes = encode_jpeg(img, quality=85)
        (FIXED / f"{slot.name}.jpg").write_bytes(jpeg_bytes)

        flag = f" [rot {rotation:+d}]" if rotation else (" [V->H]" if was_vertical else "")
        print(f"{i+1:<3} {slot.name:<24} {f'{ow}x{oh}':<22} "
              f"{f'{fw}x{fh}{flag}':<22} {len(jpeg_bytes)/1024:>7.1f}")

        new_html.extend(html[last_end:m.start()])
        new_uri = b"data:image/jpeg;base64," + base64.b64encode(jpeg_bytes)
        new_html.extend(new_uri)
        last_end = m.end()

    new_html.extend(html[last_end:])
    HTML_PATH.write_bytes(bytes(new_html))

    orig_kb = len(html) / 1024
    new_kb = len(new_html) / 1024
    print("-" * 85)
    print(f"HTML: {orig_kb:.0f} KB -> {new_kb:.0f} KB "
          f"({(1 - new_kb/orig_kb)*100:+.1f}%)")
    print(f"\nDone. Originals in extracted/, fixed copies in fixed/.")
    print(f"Open {HTML_PATH} to preview.")

if __name__ == "__main__":
    main()
