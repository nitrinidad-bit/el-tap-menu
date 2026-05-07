"""
generate_qr.py — Genera el QR imprimible que apunta al menú online.

Uso:
    python generate_qr.py https://USUARIO.github.io/el-tap-menu/
"""
from __future__ import annotations
import sys
from pathlib import Path

import qrcode
from qrcode.constants import ERROR_CORRECT_H

ROOT = Path(__file__).parent
OUTPUT = ROOT / "qr-el-tap.png"

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_qr.py <url>")
        print("Example: python generate_qr.py https://usuario.github.io/el-tap-menu/")
        sys.exit(1)

    url = sys.argv[1]
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=20,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0a0806", back_color="#f5ede0")
    img.save(OUTPUT)
    print(f"QR -> {OUTPUT} ({OUTPUT.stat().st_size // 1024} KB)")
    print(f"URL: {url}")
    print(f"Size: {img.size[0]}x{img.size[1]} px")

if __name__ == "__main__":
    main()
