"""La documentación contra la CLI: cada subcomando está documentado, ningún texto nombra uno que no existe y la versión
de Factory que se nombra es la de pyproject.toml.

    python tools/docs_al_dia.py [--raiz CARPETA]

Sale con 1 y la lista de problemas si algo no cuadra. Lo que mira: el README, docs/ (con las plantillas) y las páginas
de la web; las secciones de notas de versión y el historial de versiones del README pueden nombrar otras.
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

VALOR = r'''(?:"[^"\n]*"|'[^'\n]*'|[^\s`<>]+)'''
COMANDO = re.compile(r'oracle-factory(?![\w-])\s+(?:--(?:proyecto|agente)(?:=' + VALOR
                     + r'|\s+' + VALOR + r')\s+)*([\w][\w-]*)')
NUMERO = r'\d+\.\d+\.\d+(?:(?:a|b|rc)\d+)?(?:\.post\d+)?(?:\.dev\d+)?(?:\+[a-zA-Z0-9.]+)?'
VERSION = re.compile(r'(?<![\w.])v?(' + NUMERO + r')(?!\w|\.\d)')
ENLACE = re.compile(r"\]\(([^)\s]+)\)")
OTRO_PRODUCTO = re.compile(
    r'(?:oracle-metalenguaje|oracle-task|oracle-clue|Oracle(?: Task| Clue)?(?!\s+Factory)|Clue|Python|editores/vscode/)'
    r'[\s`(),:=*–—-]*v?' + NUMERO, re.IGNORECASE)


def sin_notas_de_version(texto: str, nombre: str) -> str:
    """Excepciones explícitas por archivo o sección, nunca por el verbo de una frase."""
    if re.search(r'(?:^|/)(?:notas-de-version|versiones|changelog|releases?)(?:/|\.md$)', nombre, re.I):
        return ''
    salida, nivel = [], None
    for linea in texto.splitlines(keepends=True):
        titulo = re.match(r'^(#{1,6})\s+(.+)', linea)
        if titulo:
            actual = len(titulo[1])
            if nivel is not None and actual <= nivel:
                nivel = None
            if re.search(r'notas de versi[oó]n', titulo[2], re.I) or (
                    nombre == 'README.md' and re.search(r'historial de versiones', titulo[2], re.I)):
                nivel = actual
        if nivel is None:
            salida.append(linea)
    return ''.join(salida)


def versiones_factory(texto: str, nombre: str) -> set[str]:
    texto = sin_notas_de_version(texto, nombre)
    # El destino de un enlace no se lee como una afirmación de versión del producto.
    texto = re.sub(r'\]\(https?://[^)]+\)', ']', texto)
    texto = re.sub(r'editores/vscode/[^\s`]*\.vsix', '', texto)
    texto = re.sub(r'\b(?!oracle-factory\b)[a-zA-Z][\w-]*@' + NUMERO, '', texto)
    texto = OTRO_PRODUCTO.sub('', texto)
    return {m[1] for m in VERSION.finditer(texto)}


def comandos_documentados(texto: str) -> set[str]:
    # Aceptamos invocaciones completas y nombres/ejemplos de subcomandos en código Markdown,
    # pero una palabra casual de la prosa («por ejemplo») no documenta un comando.
    nombres = {m[1] for m in COMANDO.finditer(texto)}
    for codigo in re.findall(r'(?<!`)`([^`\n]+)`(?!`)', texto):
        nombres.add(codigo.split()[0] if codigo.split() else '')
    return nombres


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
        de_factory = versiones_factory(texto, nombre)
        for v in sorted(de_factory - {version}):
            salida.append(f"{nombre}: nombra la versión {v}; la de pyproject.toml es {version}")
    documentado = " ".join(t for n, t in todo.items() if n == "README.md" or n.startswith("docs/"))
    for c in sorted(comandos - comandos_documentados(documentado)):
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
