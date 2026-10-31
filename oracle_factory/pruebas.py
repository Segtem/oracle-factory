"""Las pruebas como práctica de desarrollo: qué requisitos de un cambio no tienen casos de prueba, y las excepciones declaradas.

Todo es un aviso: nada de acá bloquea una decisión. Los casos salen de la trazabilidad que deja el sensor del candidato
(`trazabilidad.json`); la excepción es una línea del requisito en su spec, que una persona acepta al aprobarla."""
from __future__ import annotations

import json
from pathlib import Path
import re

from . import estructura, modos
from . import procedencia as proc

ESQUEMA_CASOS = "oracle-factory.trazabilidad-casos/1"
EXCEPCION = re.compile(r"^\s*(?:[-*]\s*)?Pruebas:\s*(.*?)\s*$", re.IGNORECASE)
ENCABEZADO = re.compile(r"^(?:#{1,3}\s|####\s+Scenario:)")  # como el importador de OpenSpec de Oracle
CANDIDATO = re.compile(r"[0-9a-f]{4,40}")
NO_APLICA = re.compile(r"no\s+aplica\s*(?:[—–-]+\s*(.*))?$", re.IGNORECASE)


class PruebasInvalidas(Exception):
    pass


def leer(texto: str) -> tuple[dict[str, str], list[str]]:
    """({slug del requisito: motivo}, errores) de las líneas «Pruebas: no aplica — motivo» de la cabecera de cada requisito.

    Sólo cuenta antes del primer escenario y fuera de los bloques de código (como el importador de Oracle). Cada línea mala
    suma un error y no descarta las buenas de los otros requisitos."""
    salida: dict[str, str] = {}
    errores: list[str] = []
    declaradas: set[str] = set()  # los requisitos con una línea «Pruebas:» (buena o mala): una segunda los deja sin excepción
    actual, retirados, cercado = None, False, False
    for linea in texto.splitlines():
        if linea.lstrip().startswith("```"):
            cercado = not cercado
            continue
        if cercado:
            continue
        delta = re.match(r"^##\s+(ADDED|MODIFIED|REMOVED|RENAMED)\s+Requirements\s*$", linea, re.IGNORECASE)
        if delta:
            retirados, actual = delta[1].upper() == "REMOVED", None
            continue
        cabecera = re.match(r"^###\s+Requirement:\s*(.+?)\s*$", linea)
        if cabecera:
            actual = None if retirados else modos.slug(cabecera[1])
            continue
        if ENCABEZADO.match(linea):
            actual = None  # lo mismo que cierra un requisito para el importador de Oracle; «#42» o «#### Nota» no lo cierran
            continue
        declarada = EXCEPCION.match(linea)
        if not declarada or actual is None:
            continue
        if actual in declaradas:
            if actual in salida:
                errores.append(f"requisito {actual}: «Pruebas:» declarada dos veces")
                del salida[actual]  # lo contradictorio no exceptúa a nadie
            continue
        declaradas.add(actual)
        valor = NO_APLICA.fullmatch(declarada[1])
        if not valor:
            errores.append(f"requisito {actual}: «Pruebas:» sólo admite «no aplica — motivo»; encontré «{declarada[1]}»")
            continue
        motivo = (valor[1] or "").strip()
        if not re.search(r"[^\s—–-]", motivo):  # vacío, o hecho sólo de guiones: no es un motivo
            errores.append(f"requisito {actual}: la excepción «Pruebas: no aplica» necesita un motivo («Pruebas: no aplica — por qué»)")
        else:
            salida[actual] = motivo
    return salida, errores


def excepciones(texto: str) -> dict[str, str]:
    """Las excepciones de la spec; falla con el primer error si alguna línea es mala (aprobar-spec e importar se niegan)."""
    salida, errores = leer(texto)
    if errores:
        raise PruebasInvalidas(errores[0])
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


def datos(raiz: Path, identificador: str, estado: dict, candidato: str | None, documentos: dict | None = None) -> dict | None:
    """Lo que `estado` muestra de las pruebas; None si no hay nada que mostrar.

    `documentos` son las huellas actuales de la propuesta y la spec (cli.documentos): las excepciones sólo cuentan si coinciden con
    las que una persona aprobó, la misma regla que exigir_spec. No se sigue ninguna ruta fuera del proyecto ni por enlaces.
    Sin candidato no hay trazabilidad que mirar, pero las excepciones (y las mal escritas) se muestran igual."""
    requisitos = estado.get("requisitos", [])
    if (not isinstance(requisitos, list) or not all(isinstance(r, str) for r in requisitos)
            or estado.get("fase") in ("cerrada", "abandonada") or not isinstance(identificador, str)
            or not estructura.ID_RE.fullmatch(identificador)):
        return None
    invalidas: list[str] = []
    por_slug: dict[str, str] = {}
    try:
        relativa = Path(estado["spec"])
        if relativa.is_absolute() or ".." in relativa.parts:
            raise proc.ProcedenciaError(f"la spec tiene que estar dentro del proyecto, sin «..»: {estado['spec']}")
        spec = raiz / relativa
        proc.sin_enlaces(raiz, spec)
        por_slug, invalidas = leer(spec.read_bytes().decode("utf-8"))
        aprobacion = estado.get("spec_aprobada")
        if not (documentos and isinstance(aprobacion, dict) and aprobacion.get("documentos") == documentos):
            if por_slug or invalidas:  # lo escrito sin una aprobación vigente de esta spec no lo aceptó nadie
                invalidas = invalidas + ["la spec no tiene una aprobación vigente (todavía no se aprobó, cambió o se invalidó): "
                                         "sus excepciones «Pruebas:» no cuentan hasta aprobarla"]
            por_slug = {}
    except (proc.ProcedenciaError, OSError, KeyError, TypeError, ValueError) as e:
        por_slug = {}
        invalidas.append(f"no pude leer la spec para las excepciones de pruebas ({type(e).__name__}: {e})")
    exceptuados = ({r: por_slug[r.split(".", 1)[-1]] for r in requisitos if r.split(".", 1)[-1] in por_slug}
                   if requisitos else dict(por_slug))  # antes de importar, por el nombre del requisito
    if not requisitos or not candidato or not CANDIDATO.fullmatch(candidato):
        if not invalidas and not exceptuados:
            return None
        return {"sin_trazabilidad": False, "sin_casos": [], "excepciones": exceptuados, "invalidas": invalidas}
    ruta = estructura.ruta_canonica(raiz, identificador, "evidencia", candidato) / "trazabilidad.json"
    try:
        proc.sin_enlaces(raiz, ruta)
        trazas = json.loads(ruta.read_text(encoding="utf-8")) if ruta.is_file() else None
    except (proc.ProcedenciaError, OSError, ValueError):
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
