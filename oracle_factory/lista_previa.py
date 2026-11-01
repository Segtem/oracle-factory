"""La lista previa a la revisión: una pregunta por cada clase de problema que más rondas de revisión cuesta.

Sale de medir los hallazgos altos y medios de los cambios cerrados (ver docs/lista-previa.md). Es un recordatorio para quien
escribe el cambio, antes de pedir una revisión: no bloquea nada y no viaja en el pedido al revisor. El documento
`docs/lista-previa.md` repite cada pregunta tal cual y `comprobar_documento` falla si alguna falta."""
from __future__ import annotations

import re

DOCUMENTO = "docs/lista-previa.md"
SECCION = "## Las preguntas"

ITEMS: tuple[tuple[str, str], ...] = (
    ("reusar", "¿Buscaste en el código el ayudante que ya existe (por ejemplo para rutas, nombres o lectura de la spec) antes de escribir otro?"),
    ("rutas", "¿Rechazás «..», las rutas absolutas y los enlaces simbólicos de todo el camino antes de leer o escribir un archivo?"),
    ("valores", "¿Qué hace el código con None, un número, una lista, un byte nulo o un archivo que falta, y puede terminar en un traceback?"),
    ("paridad", "¿Leés el formato igual que la herramienta que ya lo lee (Oracle, exigir_spec, modos): mismos espacios, mayúsculas y encabezados?"),
    ("avisos", "¿Puede haber un falso aviso o un falso silencio: qué muestra sin candidato, sin requisitos, o con la spec cambiada?"),
    ("pruebas", "¿Cada prueba falla si rompés la línea que vigila? Corré las mutaciones: ¿sobrevive alguna?"),
    ("textos", "¿Lo que dicen los documentos, los mensajes y los docstrings es lo que el código hace hoy?"),
    ("evidencia", "¿El verificador mide la estabilidad después de su última corrida, cuenta cualquier caso nuevo y no cuenta su propia carpeta?"),
    ("clase", "Si un hallazgo anterior fue de una clase de problema, ¿arreglaste la clase entera o sólo el caso que te señalaron?"),
)


class ListaPreviaInvalida(Exception):
    pass


def texto() -> str:
    """La lista numerada, tal como se muestra antes de pedir una revisión."""
    filas = [f"{i}. {pregunta}" for i, (_, pregunta) in enumerate(ITEMS, 1)]
    return ("Antes de pedir la revisión, mirá la lista previa (no bloquea; está en " + DOCUMENTO + "):\n"
            + "\n".join(filas) + "\n")


def preguntas_del_documento(documento: str) -> list[tuple[int, str]]:
    """[(número, pregunta)] de la lista numerada de la sección «Las preguntas» del documento, en el orden en que están."""
    en_seccion, salida = False, []
    for linea in documento.splitlines():
        if linea.startswith("## "):
            en_seccion = linea.strip() == SECCION
            continue
        numerada = re.match(r"^(\d+)\. (.+?)\s*$", linea) if en_seccion else None
        if numerada:
            salida.append((int(numerada[1]), numerada[2]))
    return salida


def comprobar_documento(documento: str, items: tuple[tuple[str, str], ...] | None = None) -> None:
    """Falla si la lista numerada del documento no es exactamente la del código: faltan, sobran, otro orden u otra numeración."""
    items = ITEMS if items is None else items
    en_documento = preguntas_del_documento(documento)
    textos = [pregunta for _, pregunta in en_documento]
    problemas = []
    faltan = [(clave, pregunta) for clave, pregunta in items if pregunta not in textos]
    if faltan:
        problemas.append("faltan " + "; ".join(f"{clave} («{pregunta}»)" for clave, pregunta in faltan))
    sobran = [pregunta for pregunta in textos if pregunta not in [p for _, p in items]]
    if sobran:
        problemas.append("sobran " + "; ".join(f"«{pregunta}»" for pregunta in sobran))
    if not faltan and not sobran:
        if textos != [pregunta for _, pregunta in items]:
            problemas.append("están en otro orden que en el código")
        elif [n for n, _ in en_documento] != list(range(1, len(items) + 1)):
            problemas.append("la numeración no es 1, 2, 3… seguida")
    if problemas:
        raise ListaPreviaInvalida(f"{DOCUMENTO}, sección «Las preguntas», no coincide con la lista previa del código: " + " | ".join(problemas))
