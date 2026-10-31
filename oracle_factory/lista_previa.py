"""La lista previa a la revisión: una pregunta por cada clase de problema que más rondas de revisión cuesta.

Sale de medir los hallazgos altos y medios de los cambios cerrados (ver docs/lista-previa.md). Es un recordatorio para quien
escribe el cambio, antes de pedir una revisión: no bloquea nada y no viaja en el pedido al revisor. El documento
`docs/lista-previa.md` repite cada pregunta tal cual y `comprobar_documento` falla si alguna falta."""
from __future__ import annotations

DOCUMENTO = "docs/lista-previa.md"

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


def comprobar_documento(documento: str, items: tuple[tuple[str, str], ...] | None = None) -> None:
    """Falla nombrando cada pregunta de la lista que el documento no trae con el mismo texto."""
    faltan = [(clave, pregunta) for clave, pregunta in (ITEMS if items is None else items) if pregunta not in documento]
    if faltan:
        raise ListaPreviaInvalida(f"{DOCUMENTO} no trae estas preguntas de la lista previa: "
                                  + "; ".join(f"{clave} («{pregunta}»)" for clave, pregunta in faltan))
