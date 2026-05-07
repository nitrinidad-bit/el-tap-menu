# El Tap Beer Co. — Menú digital con QR

Menú self-contained (HTML + JS + CSS + fotos en base64) para Calle Loíza 1969, Santurce.

## Setup
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Workflow
1. **Editar fotos**: actualizar `original.html` (o reemplazar fotos en él) y correr:
   ```powershell
   python fix_images.py
   ```
   Detecta verticales (heurística + map manual `MANUAL_ROTATIONS`), rota a landscape, recorta al aspect ratio del slot, re-encodea como JPEG-85, reemplaza in-place. Guarda originales en `extracted/` y resultados en `fixed/`.

2. **Preview local**: doble-click `preview.bat` o `start index.html`.

3. **Editar detalles**: editar directamente `index.html` (textos, precios). El script no toca nada fuera de los slots `data:image`.

4. **Publicar a GitHub Pages**:
   ```powershell
   git init && git add . && git commit -m "init"
   gh repo create el-tap-menu --public --source=. --push
   gh api repos/<usuario>/el-tap-menu/pages -X POST -f source[branch]=main -f source[path]=/
   ```

5. **Generar QR**:
   ```powershell
   python generate_qr.py https://<usuario>.github.io/el-tap-menu/
   ```
   Output: `qr-el-tap.png` listo para imprimir.

## Mapa de fotos
| # | Slot                   | Aspect |
|---|------------------------|--------|
| 1 | hero (bar interior)    | 16:10  |
| 2 | special (alitas)       | 4:3    |
| 3 | food-og (cerveza)      | 16:10  |
| 4 | food-og (burger)       | 4:3    |
| 5 | food-dirty (burger)    | 4:3    |
| 6 | katsu main             | 4:3    |
| 7 | katsu detail           | 4:3    |
| 8 | footer (fachada)       | 16:10  |
