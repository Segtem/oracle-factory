"""Alarmas para quien revisa: los tests que ya existían y un cambio modificó o borró, el bucle de revisión y el cambio demasiado grande.

La guarda de `docs/tests.md` (un test que ya existía no se edita para que pase sin dejarlo dicho) era sólo una regla escrita;
acá Git la hace visible. Es un aviso: no bloquea nada ni juzga si la edición fue legítima. La base es la del candidato, la misma que
usan la trazabilidad y `pedir-revision`; los archivos y las líneas salen de `git diff`, no del árbol de trabajo."""
from __future__ import annotations

import re
from typing import Callable

from . import trazabilidad

# Una carpeta tests o test en cualquier nivel, o un nombre test_*, *_test.* o *.test.*; no «contest.py», «docs/tests.md» ni «test.py».
RUTA_DE_PRUEBAS = re.compile(r"(?:^|/)(?:tests?/|test_[^/]*$|[^/]*_test\.[^/]+$|[^/]*\.test\.[^/]+$)")
# El nombre de un test quitado: def test_x (Python), func TestX (Go), it("…") / test("…") (JS, con la misma comilla de apertura y de cierre).
NOMBRES_DE_TEST = (re.compile(r"^-\s*(?:async\s+)?def\s+(test\w*)"), re.compile(r"^-\s*func\s+(Test\w+)"),
                   re.compile(r"^-\s*(?:it|test)\(\s*([\"'`])(.+?)\1"))
# Una comprobación según el lenguaje: assert* / ASSERT_* (Python, JS, C++), expect( / EXPECT_*( (JS, C++), self.fail / pytest.raises (Python), t.Error* / t.Fatal* /
# t.Fail* (Go: *_test.go no tiene «assert»).
ASERCION = re.compile(r"\bassert\w*\b|\bexpect(?:_\w+)?\(|\.fail\(|\bpytest\.raises\b|\bt\.(?:Error|Errorf|Fatal|Fatalf|Fail|FailNow)\b",
                      re.IGNORECASE)
ESTADOS = {"D": "borrado", "R": "renombrado", "M": "modificado"}


def es_de_pruebas(ruta: str) -> bool:
    return bool(RUTA_DE_PRUEBAS.search(ruta))


def _quitado(diff: str) -> tuple[int, list[str], int]:
    """(líneas quitadas, nombres de tests quitados, aserciones quitadas) del texto de `git diff -U0`.

    Sólo cuenta lo que está dentro de un hunk: las cabeceras («--- a/x», «+++ b/x») van antes del primer «@@», así que una línea
    quitada que empiece con «--» (un separador, un comentario SQL) no se confunde con una cabecera."""
    lineas, en_hunk = [], False
    for l in diff.splitlines():
        if l.startswith("diff --git"):
            en_hunk = False
        elif l.startswith("@@"):
            en_hunk = True
        elif en_hunk and l.startswith("-"):
            lineas.append(l)
    nombres = [m.groups()[-1] for l in lineas for patron in NOMBRES_DE_TEST if (m := patron.match(l))]
    return len(lineas), nombres, sum(bool(ASERCION.search(l)) for l in lineas)


def _git(ejecutar: Callable, argv: list[str]):
    """El resultado de `ejecutar`, o None si no se pudo leer: un nombre de archivo que no es UTF-8 hace fallar la decodificación de la
    salida de Git (-z entrega los bytes originales), y una alarma nunca puede romper el estado."""
    try:
        return ejecutar(argv)
    except (UnicodeDecodeError, OSError):
        return None


def base_del_candidato(ejecutar: Callable, candidato: str) -> str | None:
    """El merge-base del candidato con la rama principal (main o master, como en el resto de Factory); None si no se encuentra."""
    for rama in ("main", "master"):
        p = _git(ejecutar, ["git", "merge-base", candidato, rama])
        if p is not None and not p.returncode and p.stdout.strip():
            return p.stdout.strip()
    return None


def tests_editados(ejecutar: Callable, base: str, candidato: str, es_producto: Callable[[str], bool] | None = None) -> list[dict] | None:
    """Los archivos de pruebas de `base` que `candidato` borró, renombró o a los que les quitó líneas; None si Git no pudo.

    Un archivo es «de pruebas» por su ruta en la base (lo que ya existía), y se miran sólo los archivos del producto (`es_producto`,
    si se da): los registros generados no cuentan. Un renombre avisa siempre: mover un test a un archivo que nadie ejecuta lo desactiva."""
    lista = _git(ejecutar, ["git", "diff", "--name-status", "-z", "-M", base, candidato])
    if lista is None or lista.returncode:
        return None
    editados = []
    for archivo in trazabilidad.archivos_cambiados(lista.stdout):
        origen = archivo["origen"] or archivo["ruta"]  # la ruta en la base
        if archivo["estado"] not in ESTADOS or not es_de_pruebas(origen):
            continue  # agregados (A) y copias (C) son tests nuevos: libres; y lo que no era de pruebas en la base, no es un test existente
        if es_producto is not None and not (es_producto(origen) or es_producto(archivo["ruta"])):
            continue
        rutas = [archivo["origen"], archivo["ruta"]] if archivo["origen"] else [archivo["ruta"]]
        diff = _git(ejecutar, ["git", "--literal-pathspecs", "diff", "-U0", "-M", "--no-color", base, candidato, "--", *rutas])
        if diff is None or diff.returncode:
            return None
        quitadas, nombres, aserciones = _quitado(diff.stdout)
        if archivo["estado"] == "M" and not quitadas:
            continue  # sólo se agregó: no es una edición que afloje nada
        editados.append({"archivo": archivo["ruta"], "estado": ESTADOS[archivo["estado"]], "origen": archivo["origen"],
                         "lineas_quitadas": quitadas, "tests_quitados": nombres, "asserts_quitados": aserciones})
    return sorted(editados, key=lambda e: e["archivo"])


def del_candidato(ejecutar: Callable, candidato: str, base: str | None = None,
                  es_producto: Callable[[str], bool] | None = None) -> list[dict] | None:
    """Lo mismo contra la base del candidato (merge-base con la rama principal); None si no hay candidato o no se encuentra la base."""
    if not candidato:
        return None
    if base is None:
        base = base_del_candidato(ejecutar, candidato)
        if base is None:
            return None
    return tests_editados(ejecutar, base, candidato, es_producto)


def _detalle(e: dict) -> str:
    partes = [f"{e['lineas_quitadas']} línea(s) quitada(s)"] if e["lineas_quitadas"] else []
    if e["tests_quitados"]:
        partes.append("tests quitados: " + ", ".join(e["tests_quitados"]))
    if e["asserts_quitados"]:
        partes.append(f"{e['asserts_quitados']} aserción(es) quitada(s)")
    origen = f" (antes {e['origen']})" if e["origen"] else ""
    return f"{e['archivo']}{origen}, {e['estado']}" + (": " + "; ".join(partes) if partes else "")


def avisos(editados: list[dict] | None) -> list[str]:
    """Una línea por archivo, para el estado; vacío si no hay nada o no se pudo calcular."""
    return [f"test existente editado: {_detalle(e)} (la guarda de docs/tests.md: decilo en la revisión)" for e in editados or []]


def texto_para_el_revisor(editados: list[dict] | None) -> str:
    """La sección que se agrega al pedido del revisor; vacía si no hay nada."""
    if not editados:
        return ""
    filas = "\n".join(f"- {_detalle(e)}" for e in editados)
    return ("Tests existentes que este candidato modificó o borró (la guarda del proyecto: un test que ya existía no se edita para que "
            "pase sin dejarlo dicho). Mirá si cada edición está justificada por el cambio y mencionalo en tu informe, aunque la encuentres "
            f"legítima:\n{filas}\n")


# --- Alarmas del flujo: el bucle de revisión y el cambio demasiado grande ---------------------------------------------------
# Referencias sacadas de 20 cambios cerrados (tools/medir_rondas.py): hasta ~450 líneas la mediana fue de 2 rondas, y por encima, de 3;
# los cambios de 5 o 6 rondas fueron bucles que parchaban una clase de problema caso por caso. Son avisos, no una ley.
UMBRAL_RONDAS = 4
UMBRAL_LINEAS = 450


def rondas(estado: dict) -> int | None:
    """Las rondas de revisión del cambio: los candidatos distintos a los que se pidió o lanzó una revisión (varios revisores de un
    mismo candidato son una ronda). Un registro ilegible no se cuenta: None."""
    eventos = estado.get("eventos") if isinstance(estado, dict) else None
    if not isinstance(eventos, list) or not all(isinstance(e, dict) for e in eventos):
        return None  # un registro con algo que no es un evento no se puede contar
    # Con 7 caracteres y en minúsculas, como los guarda Factory: el mismo commit con otro largo de SHA sigue siendo una ronda.
    return len({e["candidato"][:7].lower() for e in eventos if e.get("accion") in ("revision_pedida", "revision_lanzada")
                and isinstance(e.get("candidato"), str) and e["candidato"]})


def lineas_de_producto(ejecutar: Callable, base: str, candidato: str, es_producto: Callable[[str], bool] | None = None) -> int | None:
    """Las líneas que el candidato agrega a archivos de producto (no de pruebas) respecto de la base; None si Git no puede decirlo."""
    if not base or not candidato:
        return None
    p = _git(ejecutar, ["git", "diff", "--numstat", "-z", "-M", "--no-color", base, candidato])
    if p is None or p.returncode:
        return None
    partes, total, i = p.stdout.split("\0"), 0, 0
    while i < len(partes) and partes[i]:
        campos = partes[i].split("\t", 2)
        if len(campos) != 3 or (not campos[2] and (i + 2 >= len(partes) or not partes[i + 2])):
            return None  # una salida que no es numstat (o cortada en un renombre): no se puede decir
        agregadas, _, ruta = campos
        if not ruta:  # un renombre: «a\td\t\0origen\0destino\0»
            ruta, i = partes[i + 2], i + 3
        else:
            i += 1
        if (es_producto is None or es_producto(ruta)) and not es_de_pruebas(ruta) and agregadas.isdigit():  # «-» es un binario
            total += int(agregadas)
    return total


def avisos_de_flujo(rondas: int | None, lineas: int | None) -> list[str]:
    """Los avisos del flujo para el estado; vacío si no hay nada o no se pudo calcular."""
    avisos = []
    if rondas is not None and rondas >= UMBRAL_RONDAS:
        avisos.append(f"{rondas} rondas de revisión: parate a arreglar la clase del problema entera y mirá la lista previa "
                      "(docs/lista-previa.md) antes de pedir otra")
    if lineas is not None and lineas > UMBRAL_LINEAS:
        avisos.append(f"el candidato agrega {lineas} líneas de producto (referencia: {UMBRAL_LINEAS}): considerá partir el cambio")
    return avisos


def del_flujo(ejecutar: Callable, estado: dict, candidato: str | None, es_producto: Callable[[str], bool] | None = None) -> dict:
    """Los dos datos del flujo para el estado y su JSON: {clave: {valor, umbral, avisa} | None}; None si no se pudo calcular."""
    n, lineas = rondas(estado), None
    if candidato and (base := base_del_candidato(ejecutar, candidato)):
        lineas = lineas_de_producto(ejecutar, base, candidato, es_producto)
    return {"bucle_de_revision": None if n is None else {"rondas": n, "umbral": UMBRAL_RONDAS, "avisa": n >= UMBRAL_RONDAS},
            "cambio_grande": None if lineas is None else {"lineas": lineas, "umbral": UMBRAL_LINEAS, "avisa": lineas > UMBRAL_LINEAS}}


def avisos_del_flujo(flujo: dict) -> list[str]:
    """Los avisos de `del_flujo`."""
    return avisos_de_flujo((flujo["bucle_de_revision"] or {}).get("rondas"), (flujo["cambio_grande"] or {}).get("lineas"))


# --- El camino ligero: cuánta revisión independiente conviene pedir ----------------------------------------------------------
# Una orientación, no un gate: no cambia ningún paso pendiente ni lo que decide una persona. Un cambio chico y que no toca las reglas de
# decisión alcanza con un revisor y una ronda. `cli.py` entero cuenta por prudencia: un cambio chico en él pasa por el camino completo.
UMBRAL_LIGERO = 150
REGLAS_DE_DECISION = ("oracle_factory/cli.py", "oracle_factory/modos.py", "oracle_factory/flujo_revision.py", "oracle_factory/flujo_medidas.py",
                      "oracle_factory/revision.py", "oracle_factory/preparacion.py", "oracle_factory/puerta.py", "oracle_factory/unir.py",
                      "oracle_factory/alarmas.py")  # esta lista y el umbral viven acá: tocarlos no puede ser «ligero»


def archivos_tocados(ejecutar: Callable, base: str, candidato: str) -> set[str] | None:
    """Las rutas que el candidato cambió respecto de la base, con el origen de los renombres; None si Git no pudo."""
    p = _git(ejecutar, ["git", "diff", "--name-status", "-z", "-M", base, candidato])
    if p is None or p.returncode:
        return None
    return {n for a in trazabilidad.archivos_cambiados(p.stdout) for n in (a["ruta"], a["origen"]) if n}


def camino_del_candidato(ejecutar: Callable, candidato: str | None, es_producto: Callable[[str], bool] | None = None) -> dict | None:
    """{tipo: ligero|completo, lineas, umbral, reglas_tocadas}; None si no hay candidato o Git no puede decirlo (no se afirma nada)."""
    if not candidato or not (base := base_del_candidato(ejecutar, candidato)):
        return None
    lineas = lineas_de_producto(ejecutar, base, candidato, es_producto)
    tocados = archivos_tocados(ejecutar, base, candidato)
    if lineas is None or tocados is None:
        return None
    reglas = sorted(tocados & set(REGLAS_DE_DECISION))
    return {"tipo": "ligero" if lineas <= UMBRAL_LIGERO and not reglas else "completo", "lineas": lineas, "umbral": UMBRAL_LIGERO,
            "reglas_tocadas": reglas}


def linea_camino(camino: dict | None) -> str | None:
    """La línea del estado; None si no se pudo calcular."""
    if not camino:
        return None
    if camino["tipo"] == "ligero":
        return (f"Camino de revisión: ligero ({camino['lineas']} líneas de producto, {camino['umbral']} o menos, sin reglas de decisión): "
                "alcanza un revisor y una ronda (ver la guía para agentes)")
    motivos = ([f"{camino['lineas']} líneas de producto, más de {camino['umbral']}"] if camino["lineas"] > camino["umbral"] else [])
    if camino["reglas_tocadas"]:
        motivos.append("toca reglas de decisión: " + ", ".join(camino["reglas_tocadas"]))
    return f"Camino de revisión: completo ({'; '.join(motivos)})"
