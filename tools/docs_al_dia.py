"""La documentación contra la CLI: cada subcomando está documentado, ningún texto nombra uno que no existe y la versión
de Factory que se nombra es la de pyproject.toml.

    python tools/docs_al_dia.py [--raiz CARPETA]

Sale con 1 y la lista de problemas si algo no cuadra. Lo que mira: el README, docs/ (con las plantillas) y las páginas
de la web; las notas de versión y el historial de versiones del README («La 0.1.0aN trajo …») pueden nombrar otras.
"""
from __future__ import annotations

import argparse
import html
from pathlib import Path
import re
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from oracle_factory import cli  # noqa: E402

COMANDO = re.compile(r"oracle-factory(?:\s+--(?:proyecto|agente)(?:\s+[^\s`<>]+))*\s+([a-z][a-z-]+)")
VERSION = re.compile(r"\b0\.1\.0(?:a|b|rc)\d+\b")
ENLACE = re.compile(r"\]\(([^)\s]+)\)")
HISTORIAL = re.compile(r"\b[Ll]a 0\.1\.0(?:a|b|rc)\d+ (?:trajo|abrió|hizo)\b")


def subcomandos() -> set[str]:
    acciones = [a for a in cli.construir_parser()._actions if isinstance(a, argparse._SubParsersAction)]
    return set(acciones[0].choices)


def textos(raiz: Path) -> dict[str, str]:
    archivos = [raiz / "README.md", *sorted((raiz / "docs").rglob("*.md")), *sorted((raiz / "site").glob("*.html"))]
    salida = {}
    for f in archivos:
        if not f.is_file():
            continue
        texto = f.read_text(encoding="utf-8")
        if f.suffix == ".html":  # el texto que se lee, sin etiquetas
            texto = html.unescape(re.sub(r"<[^>]+>", " ", texto))
        salida[f.relative_to(raiz).as_posix()] = texto
    return salida


def problemas(raiz: Path = ROOT) -> list[str]:
    comandos = subcomandos()
    version = tomllib.loads((raiz / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    salida = []
    todo = textos(raiz)
    for nombre, texto in todo.items():
        for m in COMANDO.finditer(texto):
            if m[1] not in comandos:
                salida.append(f"{nombre}: nombra «oracle-factory {m[1]}», que no es un subcomando")
        sin_historial = HISTORIAL.sub("", texto)
        # Las versiones de Oracle Clue (0.1.0a1, 0.1.0a2…) tienen la misma forma: ésas no son de Factory.
        de_factory = {m[0] for m in VERSION.finditer(sin_historial) if "clue" not in sin_historial[max(0, m.start() - 14):m.start()].lower()}
        for v in sorted(de_factory - {version}):
            salida.append(f"{nombre}: nombra la versión {v}; la de pyproject.toml es {version}")
    documentado = " ".join(t for n, t in todo.items() if n == "README.md" or n.startswith("docs/"))
    for c in sorted(comandos):
        if not re.search(rf"(?<![\w-]){re.escape(c)}(?![\w-])", documentado):
            salida.append(f"el subcomando {c} no aparece en el README ni en docs/")
    return sorted(set(salida))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--raiz", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    lista = problemas(args.raiz.resolve())
    for p in lista:
        print(p)
    print("La documentación está al día con la CLI." if not lista else f"{len(lista)} problema(s).")
    return 1 if lista else 0


if __name__ == "__main__":
    raise SystemExit(main())
