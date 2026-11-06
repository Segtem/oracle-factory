"""Comprueba la página de la simulación de concurrencia: cada regla cita un texto que existe en docs/colaboracion.md, los comandos que
nombra existen en la CLI, está rotulada como simulación y se enlaza desde la guía de colaboración y la portada.

Uso: python tools/sitio_concurrencia.py   (imprime los problemas; código 1 si hay)"""
from __future__ import annotations

from pathlib import Path
import re
import sys

REGLA = re.compile(r"\{id: '(\w+)', texto: '((?:[^'\\]|\\.)*)',\s*cita: '((?:[^'\\]|\\.)*)'\}")
COMANDO = re.compile(r"oracle-factory\s+([a-z][\w-]*)")


def _subcomandos() -> set[str]:
    import argparse
    from oracle_factory import cli
    parser = cli.construir_parser()
    sub = next(a for a in parser._actions if isinstance(a, argparse._SubParsersAction))
    return set(sub.choices)


def problemas(raiz: Path, subcomandos: set[str] | None = None) -> list[str]:
    sitio, salida = raiz / "site", []
    js = (sitio / "concurrencia.js").read_text(encoding="utf-8") if (sitio / "concurrencia.js").is_file() else ""
    pagina = (sitio / "concurrencia.html").read_text(encoding="utf-8") if (sitio / "concurrencia.html").is_file() else ""
    if not js or not pagina:
        return ["falta site/concurrencia.js o site/concurrencia.html"]
    guia = (raiz / "docs" / "colaboracion.md").read_text(encoding="utf-8")
    reglas = REGLA.findall(js)
    if len(reglas) < 6:
        salida.append(f"concurrencia.js declara {len(reglas)} reglas con su cita; esperaba al menos 6")
    for ident, _texto, cita in reglas:
        if cita.replace("\\'", "'") not in guia:
            salida.append(f"la regla «{ident}» cita un texto que no está en docs/colaboracion.md")
    conocidos = subcomandos if subcomandos is not None else _subcomandos()
    for nombre, fuente in (("concurrencia.js", js), ("concurrencia.html", pagina)):
        for sub in sorted(set(COMANDO.findall(fuente))):
            if sub not in conocidos:
                salida.append(f"{nombre} nombra «oracle-factory {sub}», que no existe en la CLI")
    texto = re.sub(r"<[^>]+>", " ", pagina).lower()
    if "es una simulación" not in texto or "no ejecuta factory" not in texto:
        salida.append("concurrencia.html no dice que es una simulación que no ejecuta Factory")
    for origen in ("index.html", "colaboracion.html"):
        if 'href="./concurrencia.html' not in (sitio / origen).read_text(encoding="utf-8"):
            salida.append(f"{origen} no enlaza a concurrencia.html")
    if 'href="./colaboracion.html' not in pagina:
        salida.append("concurrencia.html no enlaza a la guía en equipo (colaboracion.html)")
    return salida


if __name__ == "__main__":
    ps = problemas(Path(__file__).resolve().parents[1])
    print("\n".join(ps) if ps else "sin problemas")
    sys.exit(1 if ps else 0)
