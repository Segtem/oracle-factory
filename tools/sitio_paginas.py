"""Las páginas del sitio salen de una sola tabla: el menú, el pie y los enlaces de lectura se generan desde ella, y este comprobador
verifica que lo escrito en cada HTML coincide, que ninguna página quedó fuera y que `documentacion.html` lista todas las guías de docs/.

Uso: python tools/sitio_paginas.py             (imprime los problemas; código 1 si hay)
     python tools/sitio_paginas.py --escribir  (rehace los bloques desde la tabla)"""
from __future__ import annotations

from pathlib import Path
import re
import sys

# El orden de lectura: cada página, su nombre en el menú y una frase.
PAGINAS = [
    ("desde-cero.html", "Desde cero", "Instalá Factory y llevá un pedido hasta el cierre, con tu agente."),
    ("modos.html", "Modos", "Cuánto decide una persona y cuánto un agente en cada cambio."),
    ("colaboracion.html", "En equipo", "Dos personas y sus agentes trabajando sobre el mismo producto sin pisarse."),
    ("concurrencia.html", "Simulación", "Mirá en pixel art qué pasa cuando varias personas y agentes trabajan a la vez."),
    ("documentacion.html", "Documentación", "Todas las guías del repositorio, ordenadas por tema."),
]
ANCLAS = [("formas", "Cuatro caminos"), ("recorrido", "El recorrido"), ("herramientas", "El kit"), ("jugar", "Jugá"), ("novedades", "Qué trae")]
DOCS = "https://github.com/Segtem/oracle-factory/blob/main/docs/"
TABLA = ["index.html"] + [f for f, _, _ in PAGINAS]


def _marcado(nombre: str, html: str) -> str:
    return f"<!-- {nombre} -->{html}<!-- /{nombre} -->"


def menu(actual: str) -> str:
    base = "" if actual == "index.html" else "./index.html"
    anclas = "".join(f'<a href="{base}#{a}">{t}</a>' for a, t in ANCLAS)
    paginas = "".join(f'<a href="./{f}"{" aria-current=" + chr(34) + "page" + chr(34) if f == actual else ""}>{t}</a>' for f, t, _ in PAGINAS)
    return f'<nav aria-label="Navegación principal">{anclas}{paginas}</nav>'


def pie(actual: str) -> str:
    inicio = "#inicio" if actual == "index.html" else "./index.html"
    paginas = "".join(f'<a href="./{f}">{t}</a>' for f, t, _ in PAGINAS)
    return (f'<footer class="wrap"><a class="footer-brand" href="{inicio}">ORACLE FACTORY <span>· Software con dirección humana.</span></a>'
            f'<div>{paginas}<a href="https://github.com/Segtem/oracle-factory">Factory ↗</a><a href="https://github.com/Segtem/oracle-clue">Clue ↗</a>'
            f'<span>Hecho para poder preguntar por qué.</span></div></footer>')


def leer(actual: str) -> str:
    i = [f for f, _, _ in PAGINAS].index(actual)
    antes = ("./index.html", "Portada") if i == 0 else (f"./{PAGINAS[i - 1][0]}", PAGINAS[i - 1][1])
    despues = ("./index.html", "Volver a la portada") if i == len(PAGINAS) - 1 else (f"./{PAGINAS[i + 1][0]}", PAGINAS[i + 1][1])
    return (f'<nav class="leer" aria-label="Seguí leyendo"><a rel="prev" href="{antes[0]}"><span>← Anterior</span> {antes[1]}</a>'
            f'<a rel="next" href="{despues[0]}"><span>Siguiente →</span> {despues[1]}</a></nav>')


def ruta() -> str:
    items = "".join(f'<li><a href="./{f}">{t}</a> — {frase}</li>' for f, t, frase in PAGINAS)
    return ('<nav class="ruta wrap" aria-labelledby="ruta-titulo"><p class="eyebrow">POR DÓNDE SEGUIR</p>'
            f'<h2 id="ruta-titulo">Cinco páginas, en este orden.</h2><ol>{items}</ol></nav>')


def bloques(actual: str) -> dict[str, str]:
    b = {"menu": menu(actual), "pie": pie(actual)}
    if actual == "index.html":
        b["ruta"] = ruta()
    else:
        b["leer"] = leer(actual)
    return b


_SIN_MARCAS = {"menu": r'<nav aria-label="Navegación principal">.*?</nav>', "pie": r'<footer class="wrap">.*?</footer>'}


def _actual(texto: str, bloque: str) -> str | None:
    m = re.search(rf"<!-- {bloque} -->(.*?)<!-- /{bloque} -->", texto, re.S)
    return m[1] if m else None


def _poner(texto: str, bloque: str, html: str) -> str:
    marcado = _marcado(bloque, html)
    if _actual(texto, bloque) is not None:
        return re.sub(rf"<!-- {bloque} -->.*?<!-- /{bloque} -->", lambda _: marcado, texto, count=1, flags=re.S)
    if bloque in _SIN_MARCAS and re.search(_SIN_MARCAS[bloque], texto, re.S):
        return re.sub(_SIN_MARCAS[bloque], lambda _: marcado, texto, count=1, flags=re.S)
    ancla = "</body>" if bloque == "pie" else "</main>"
    return texto.replace(ancla, marcado + ancla, 1)


def escribir(raiz: Path) -> None:
    for nombre in TABLA:
        archivo = raiz / "site" / nombre
        texto = archivo.read_text(encoding="utf-8")
        for bloque, html in bloques(nombre).items():
            texto = _poner(texto, bloque, html)
        archivo.write_text(texto, encoding="utf-8")


def problemas_de_documentacion(raiz: Path) -> list[str]:
    salida_href: list[str] = []
    pagina = raiz / "site" / "documentacion.html"
    if not pagina.is_file():
        return ["falta site/documentacion.html"]
    texto = pagina.read_text(encoding="utf-8")
    listadas = re.findall(r'<a [^>]*data-doc="([^"]+)"[^>]*>([^<]*)</a>', texto)
    for entrada in re.findall(r'<li>(<a [^>]*data-doc="[^"]+"[^>]*>[^<]*</a>.*?)</li>', texto, re.S):
        nombre = re.search(r'data-doc="([^"]+)"', entrada)[1]
        href = re.search(r'href="([^"]*)"', entrada)
        if not href or href[1] != f"{DOCS}{nombre}.md":
            salida_href.append(f"documentacion.html: el enlace de docs/{nombre}.md debe ser {DOCS}{nombre}.md, no {href[1] if href else 'ninguno'}")
        frase = re.sub(r"<[^>]+>", "", entrada.split("</a>", 1)[1]).strip()
        if len(frase) < 30:
            salida_href.append(f"documentacion.html: falta la frase de docs/{nombre}.md (al menos 30 caracteres)")
    nombres = [n for n, _ in listadas]
    salida = salida_href
    guias = {p.stem: p for p in (raiz / "docs").glob("*.md")}
    for g in sorted(set(guias) - set(nombres)):
        salida.append(f"documentacion.html no lista la guía docs/{g}.md")
    for n in sorted(set(nombres) - set(guias)):
        salida.append(f"documentacion.html lista docs/{n}.md, que no existe")
    for n in sorted({x for x in nombres if nombres.count(x) > 1}):
        salida.append(f"documentacion.html lista dos veces docs/{n}.md")
    for n, titulo in listadas:
        if n in guias:
            real = guias[n].read_text(encoding="utf-8").splitlines()[0].removeprefix("# ").strip()
            if titulo.strip() != real:
                salida.append(f"documentacion.html: el título de docs/{n}.md es «{real}», no «{titulo.strip()}»")
    if len(re.findall(r'<section class="docs-grupo"', texto)) != 4:
        salida.append("documentacion.html no tiene cuatro grupos")
    return salida


def problemas_de_enlaces(raiz: Path) -> list[str]:
    """Los enlaces internos de cada página (a otra página, o a un ancla) llevan a algo que existe."""
    sitio, salida, ids = raiz / "site", [], {}
    paginas = sorted(sitio.glob("*.html"))
    for p in paginas:
        ids[p.name] = set(re.findall(r'\bid="([^"]+)"', p.read_text(encoding="utf-8")))
    for p in paginas:
        for href in re.findall(r'<a [^>]*href="([^"]*)"', p.read_text(encoding="utf-8")):
            if re.match(r"^(https?:|mailto:)", href) or href == "":
                continue
            destino, _, ancla = href.partition("#")
            destino = destino.removeprefix("./") or p.name
            if destino not in ids:
                if not (sitio / destino).is_file():  # una imagen o cualquier otro archivo del sitio también vale
                    salida.append(f"{p.name}: el enlace «{href}» no lleva a ninguna página ni archivo")
            elif ancla and ancla not in ids[destino]:
                salida.append(f"{p.name}: el enlace «{href}» apunta a un ancla que no existe en {destino}")
    return salida


def problemas(raiz: Path) -> list[str]:
    salida = []
    sitio = raiz / "site"
    for p in sorted(sitio.glob("*.html")):
        if p.name not in TABLA:
            salida.append(f"{p.name} no está en la tabla de páginas (tools/sitio_paginas.py)")
    for nombre in TABLA:
        if not (sitio / nombre).is_file():
            salida.append(f"{nombre} está en la tabla pero no existe")
            continue
        texto = (sitio / nombre).read_text(encoding="utf-8")
        for bloque, html in bloques(nombre).items():
            actual = _actual(texto, bloque)
            if actual is None:
                salida.append(f"{nombre}: falta el bloque «{bloque}» con sus marcadores")
            elif actual != html:
                salida.append(f"{nombre}: el bloque «{bloque}» no coincide con la tabla (python tools/sitio_paginas.py --escribir)")
        sobra = "leer" if nombre == "index.html" else "ruta"
        if _actual(texto, sobra) is not None:
            salida.append(f"{nombre}: no debería tener el bloque «{sobra}»")
    return salida + problemas_de_documentacion(raiz) + problemas_de_enlaces(raiz)


if __name__ == "__main__":
    raiz = Path(__file__).resolve().parents[1]
    if "--escribir" in sys.argv:
        escribir(raiz)
        print("bloques rehechos")
    ps = problemas(raiz)
    print("\n".join(ps) if ps else "sin problemas")
    sys.exit(1 if ps else 0)
