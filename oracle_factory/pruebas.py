"""Las pruebas como práctica de desarrollo: qué requisitos de un cambio no tienen casos de prueba, y las excepciones declaradas.

Todo es un aviso: nada de acá bloquea una decisión. Los casos salen de la trazabilidad que deja el sensor del candidato
(`trazabilidad.json`); la excepción es una línea del requisito en su spec, que una persona acepta al aprobarla."""
from __future__ import annotations

import json
from pathlib import Path
import re

from . import estructura, modos

ESQUEMA_CASOS = "oracle-factory.trazabilidad-casos/1"
EXCEPCION = re.compile(r"^\s*(?:-\s*)?Pruebas:\s*(.*?)\s*$", re.IGNORECASE)
NO_APLICA = re.compile(r"no\s+aplica\s*(?:[—–-]+\s*(.*))?$", re.IGNORECASE)


class PruebasInvalidas(Exception):
    pass


def excepciones(texto: str) -> dict[str, str]:
    """{slug del requisito: motivo} de las líneas «Pruebas: no aplica — motivo» de la cabecera de cada requisito.

    Sólo cuenta antes del primer escenario. Una excepción sin motivo, o un valor que no es «no aplica», falla diciendo cuál."""
    salida: dict[str, str] = {}
    actual, retirados = None, False
    for linea in texto.splitlines():
        delta = re.match(r"^##\s+(ADDED|MODIFIED|REMOVED|RENAMED)\s+Requirements\s*$", linea, re.IGNORECASE)
        if delta:
            retirados, actual = delta[1].upper() == "REMOVED", None
            continue
        cabecera = re.match(r"^###\s+Requirement:\s*(.+?)\s*$", linea)
        if cabecera:
            actual = None if retirados else modos.slug(cabecera[1])
            continue
        if linea.startswith("#"):
            actual = None  # un escenario (####) u otra sección cierra la cabecera del requisito
            continue
        declarada = EXCEPCION.match(linea)
        if not declarada or actual is None:
            continue
        valor = NO_APLICA.fullmatch(declarada[1])
        if not valor:
            raise PruebasInvalidas(f"requisito {actual}: «Pruebas:» sólo admite «no aplica — motivo»; encontré «{declarada[1]}»")
        motivo = (valor[1] or "").strip()
        if not motivo:
            raise PruebasInvalidas(f"requisito {actual}: la excepción «Pruebas: no aplica» necesita un motivo "
                                   "(«Pruebas: no aplica — por qué»)")
        salida[actual] = motivo
    return salida


def analizar(requisitos: list[str], trazas: dict | None, exceptuados: dict[str, str]) -> dict:
    """Qué requisitos no tienen casos en la trazabilidad. Un caso es un texto no vacío."""
    por_requisito = trazas.get("requisitos") if isinstance(trazas, dict) and trazas.get("esquema") == ESQUEMA_CASOS else None
    if not isinstance(por_requisito, dict):
        return {"sin_trazabilidad": True, "sin_casos": [], "excepciones": dict(exceptuados), "invalidas": []}

    def con_casos(rid: str) -> bool:
        casos = por_requisito.get(rid)
        return isinstance(casos, list) and any(isinstance(c, str) and c.strip() for c in casos)

    return {"sin_trazabilidad": False, "sin_casos": [r for r in requisitos if r not in exceptuados and not con_casos(r)],
            "excepciones": dict(exceptuados), "invalidas": []}


def datos(raiz: Path, identificador: str, estado: dict, candidato: str | None) -> dict | None:
    """Lo que `estado` muestra de las pruebas; None si no hay nada que mostrar (sin requisitos, cerrado o sin candidato)."""
    requisitos = estado.get("requisitos") or []
    if not requisitos or not candidato or estado.get("fase") in ("cerrada", "abandonada"):
        return None
    invalidas: list[str] = []
    try:
        por_slug = excepciones((raiz / estado["spec"]).read_text(encoding="utf-8"))
    except (PruebasInvalidas, OSError, KeyError, UnicodeDecodeError) as e:
        por_slug = {}
        invalidas.append(str(e))
    exceptuados = {r: por_slug[r.split(".", 1)[-1]] for r in requisitos if r.split(".", 1)[-1] in por_slug}
    ruta = estructura.ruta_canonica(raiz, identificador, "evidencia", candidato) / "trazabilidad.json"
    try:
        trazas = json.loads(ruta.read_text(encoding="utf-8")) if ruta.is_file() and not ruta.is_symlink() else None
    except (OSError, ValueError):
        trazas = None
    return {**analizar(requisitos, trazas, exceptuados), "invalidas": invalidas}


def avisos(pruebas: dict | None) -> list[str]:
    if not pruebas:
        return []
    salida = list(pruebas["invalidas"])
    if pruebas["sin_trazabilidad"]:
        salida.append("el candidato no tiene trazabilidad de pruebas: el sensor no dejó trazabilidad.json "
                      "(ver docs/trazabilidad.md); sin ella no se sabe qué requisitos tienen casos de prueba")
    if pruebas["sin_casos"]:
        salida.append("sin casos de prueba en la trazabilidad: " + ", ".join(pruebas["sin_casos"])
                      + " (escribí sus pruebas, o declará en la spec «Pruebas: no aplica — motivo»)")
    return salida


def lineas(pruebas: dict | None) -> list[str]:
    """Las excepciones aceptadas, una línea cada una, para mostrarlas junto al estado."""
    return [f"Pruebas: {rid} no aplica — {motivo}" for rid, motivo in sorted((pruebas or {}).get("excepciones", {}).items())]
