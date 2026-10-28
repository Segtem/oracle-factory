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


def publicacion_prematura(raiz: Path, version: str, todo: dict[str, str]) -> list[str]:
    """Mientras las notas dicen que la versión está en preparación, ningún texto puede decir que ya está publicada."""
    notas = raiz / "NOTAS-DE-RELEASE.md"
    if not notas.is_file() or f"# Oracle Factory {version} (en preparación)" not in notas.read_text(encoding="utf-8"):
        return []
    v = re.escape(version)
    publicada = r"(?:ya (?:está|esta) publicad[ao]|publicad[ao] en (?:PyPI|GitHub)|ya (?:está|esta) en PyPI|disponible en PyPI)"
    afirma = re.compile(rf"{v}[^\n]{{0,80}}{publicada}|{publicada}[^\n]{{0,80}}{v}", re.I)
    return [f"{nombre}: afirma que la versión {version} está publicada, pero NOTAS-DE-RELEASE.md la declara en preparación"
            for nombre, texto in todo.items() if afirma.search(texto)]


def patron_preparacion(version: str) -> re.Pattern:
    """Las formas de llamar a una versión candidata o en preparación. Toda forma lleva la versión en la misma frase, para no
    confundir el «candidato» de una revisión (un hash) ni un «estado de preparación» de otra cosa con la versión publicada."""
    v = re.escape(version)
    cerca = r"[^\n.]{0,40}"  # en la misma frase
    formas = [
        rf"{v}\s*\(?en preparaci[oó]n",                                          # 0.1.0a15 (en preparación)
        rf"preparaci[oó]n\s+{v}",                                                # PREPARACIÓN 0.1.0a15
        rf"candidat[oa]\s+(?:en preparaci[oó]n\s+)?(?:de\s+)?(?:factory\s+)?[`']?(?:oracle-factory\s*(?:==)?\s*)?{v}",  # candidato Factory 0.1.0a15
        rf"{v}{cerca}\s(?:es|sigue siendo|queda como|como)\s+(?:la\s+|el\s+|una?\s+)?(?:versi[oó]n\s+)?candidat[oa]",  # la 0.1.0a15 es la candidata
        rf"{v}{cerca}\b(?:est[aá]|queda|sigue)\s+en preparaci[oó]n",             # la 0.1.0a15 está en preparación
        rf"{v}{cerca}estado de preparaci[oó]n|estado de preparaci[oó]n{cerca}{v}", # Versión 0.1.0a15 y estado de preparación
        rf"en preparaci[oó]n\s*[:\-–]?\s*{v}",                                   # en preparación: 0.1.0a15
        rf"cuando se publique\s+(?:la\s+|el\s+)?(?:versi[oó]n\s+)?{v}|{v}{cerca}\bse publicar[aá]\b",  # cuando se publique la 0.1.0a15
        r"cuando se publique esta versi[oó]n",                                     # frase de instalación a futuro, sin versión
    ]
    return re.compile("|".join(formas), re.I)


def preparacion_olvidada(raiz: Path, version: str, todo: dict[str, str]) -> list[str]:
    """Cuando las notas ya no marcan la versión como «en preparación», ningún texto puede seguir llamándola candidata."""
    notas = raiz / "NOTAS-DE-RELEASE.md"
    if not notas.is_file() or f"\n# Oracle Factory {version}\n" not in "\n" + notas.read_text(encoding="utf-8"):
        return []
    afirma = patron_preparacion(version)
    return [f"{nombre}: describe la versión {version} como candidata o en preparación, pero NOTAS-DE-RELEASE.md la declara publicada"
            for nombre, texto in todo.items() if afirma.search(texto)]


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
    salida += publicacion_prematura(raiz, version, todo)
    salida += preparacion_olvidada(raiz, version, todo)
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
