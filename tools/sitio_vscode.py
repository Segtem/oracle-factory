"""Comprueba lo que la web muestra de VS Code y de los ejemplos: capturas que existen, salidas de comandos reales y nada personal.

Uso: python tools/sitio_vscode.py   (imprime los problemas; código 1 si hay)"""
from __future__ import annotations

import html
import json
from pathlib import Path
import re
import sys

MAX_IMAGEN = 300 * 1024
MAX_TOTAL = 1536 * 1024
MIN_CAPTURAS = 4
PERSONAL = re.compile(r"/home/\w|/Users/\w|C:\\Users|/tmp/claude|brianhollweg|@gmail\.|Brianholl", re.I)
CORREO = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
CORREO_DEL_EJEMPLO = "@ejemplo.org"
IMG = re.compile(r"<img\b[^>]*>", re.I)
EJEMPLO = re.compile(r'<pre\b[^>]*\bdata-ejemplo="([^"]+)"[^>]*>(.*?)</pre>', re.S)


def _attr(etiqueta: str, nombre: str) -> str | None:
    m = re.search(rf'\b{nombre}="([^"]*)"', etiqueta)
    return m[1] if m else None


def problemas(raiz: Path) -> list[str]:
    raiz = Path(raiz)
    sitio, salida = raiz / "site", []
    paginas = sorted(sitio.glob("*.html"))
    vistas: set[str] = set()
    for p in paginas:
        for etiqueta in IMG.findall(p.read_text(encoding="utf-8")):
            src = _attr(etiqueta, "src") or ""
            if "img/vscode-" not in src:
                continue
            ruta = sitio / src.removeprefix("./")
            vistas.add(src)
            if not ruta.is_file():
                salida.append(f"{p.name}: la imagen {src} no existe")
            if not (_attr(etiqueta, "alt") or "").strip():
                salida.append(f"{p.name}: la imagen {src} no tiene texto alternativo")
            if not (_attr(etiqueta, "width") and _attr(etiqueta, "height")):
                salida.append(f"{p.name}: la imagen {src} no declara ancho y alto")
    if len(vistas) < MIN_CAPTURAS:
        salida.append(f"las guías muestran {len(vistas)} capturas de VS Code distintas; la spec pide al menos {MIN_CAPTURAS}")
    pesos = {s: (sitio / s.removeprefix("./")).stat().st_size for s in vistas if (sitio / s.removeprefix("./")).is_file()}
    salida += [f"la imagen {s} pesa {n // 1024} KB: el tope es {MAX_IMAGEN // 1024} KB" for s, n in sorted(pesos.items()) if n > MAX_IMAGEN]
    if sum(pesos.values()) > MAX_TOTAL:
        salida.append(f"las capturas pesan {sum(pesos.values()) // 1024} KB: el tope del conjunto es {MAX_TOTAL // 1024} KB")

    registro_ruta = raiz / "tests" / "datos" / "ejemplos-demo.json"
    registro = json.loads(registro_ruta.read_text(encoding="utf-8")) if registro_ruta.is_file() else {}
    if not registro:
        salida.append("tests/datos/ejemplos-demo.json no existe o está vacío")
    for p in paginas:
        for ident, cuerpo in EJEMPLO.findall(p.read_text(encoding="utf-8")):
            texto = html.unescape(re.sub(r"</?code>", "", cuerpo)).strip("\n")
            if ident not in registro:
                salida.append(f"{p.name}: el ejemplo {ident} no está en el registro")
            elif texto != registro[ident].strip("\n"):
                salida.append(f"{p.name}: el ejemplo {ident} no coincide con lo que contestó la CLI")

    textos = [(p.name, p.read_text(encoding="utf-8")) for p in paginas]
    textos += [("tests/datos/ejemplos-demo.json", json.dumps(registro, ensure_ascii=False))] if registro else []
    script = raiz / "tools" / "capturas_vscode.py"
    if not script.is_file():
        salida.append("falta tools/capturas_vscode.py, la forma de regenerar capturas y ejemplos")
    else:
        textos.append(("tools/capturas_vscode.py", script.read_text(encoding="utf-8")))
    for nombre, t in textos:
        if m := PERSONAL.search(t):
            salida.append(f"{nombre}: contiene un dato personal ({m[0]})")
        for c in CORREO.findall(t):
            if not c.endswith(CORREO_DEL_EJEMPLO) and not c.endswith("@noreply.github.com") and nombre.endswith((".json", ".py")):
                salida.append(f"{nombre}: contiene un correo ajeno al ejemplo ({c})")
    return salida


if __name__ == "__main__":
    p = problemas(Path(__file__).resolve().parents[1])
    print("\n".join(p) if p else "sin problemas")
    sys.exit(1 if p else 0)
