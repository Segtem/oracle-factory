"""Alarmas para quien revisa: hoy, los tests que ya existían y un cambio modificó o borró.

La guarda de `docs/tests.md` (un test que ya existía no se edita para que pase sin dejarlo dicho) era sólo una regla escrita;
acá Git la hace visible. Es un aviso: no bloquea nada ni juzga si la edición fue legítima. La base es la del candidato, la misma que
usan la trazabilidad y `pedir-revision`; los archivos y las líneas salen de `git diff`, no del árbol de trabajo."""
from __future__ import annotations

import re
from typing import Callable

from . import trazabilidad

# Una carpeta tests o test en cualquier nivel, o un nombre test_*, *_test.* o *.test.*; no «contest.py», «docs/tests.md» ni «test.py».
RUTA_DE_PRUEBAS = re.compile(r"(?:^|/)(?:tests?/|test_[^/]*$|[^/]*_test\.[^/]+$|[^/]*\.test\.[^/]+$)")
NOMBRE_DE_TEST = re.compile(r"^-\s*(?:async\s+)?def\s+(test\w*)|^-\s*func\s+(Test\w+)|^-\s*(?:it|test)\(\s*[\"'`]([^\"'`]+)")
# Una comprobación según el lenguaje: assert* / ASSERT_* (Python, JS, C++), expect( / EXPECT_*( (JS, C++), self.fail / pytest.raises (Python), t.Error* / t.Fatal* /
# t.Fail* (Go: *_test.go no tiene «assert»).
ASERCION = re.compile(r"\bassert\w*\b|\bexpect(?:_\w+)?\(|\.fail\(|\bpytest\.raises\b|\bt\.(?:Error|Errorf|Fatal|Fatalf|Fail|FailNow)\b",
                      re.IGNORECASE)
ESTADOS = {"D": "borrado", "R": "renombrado", "M": "modificado"}


def es_de_pruebas(ruta: str) -> bool:
    return bool(RUTA_DE_PRUEBAS.search(ruta))


def _quitado(diff: str) -> tuple[int, list[str], int]:
    """(líneas quitadas, nombres de tests quitados, aserciones quitadas) del texto de `git diff -U0`."""
    lineas = [l for l in diff.splitlines() if l.startswith("-") and not l.startswith("---")]
    nombres = [next(g for g in m.groups() if g) for l in lineas if (m := NOMBRE_DE_TEST.match(l))]
    return len(lineas), nombres, sum(bool(ASERCION.search(l)) for l in lineas)


def tests_editados(ejecutar: Callable, base: str, candidato: str) -> list[dict] | None:
    """Los archivos de pruebas de `base` que `candidato` borró, renombró o a los que les quitó líneas; None si Git no pudo."""
    lista = ejecutar(["git", "diff", "--name-status", "-z", "-M", base, candidato])
    if lista.returncode:
        return None
    editados = []
    for archivo in trazabilidad.archivos_cambiados(lista.stdout):
        origen = archivo["origen"] or archivo["ruta"]
        if archivo["estado"] not in ESTADOS or not (es_de_pruebas(origen) or es_de_pruebas(archivo["ruta"])):
            continue  # agregados (A) y copias (C) son tests nuevos: libres
        rutas = [archivo["origen"], archivo["ruta"]] if archivo["origen"] else [archivo["ruta"]]
        diff = ejecutar(["git", "diff", "-U0", "-M", "--no-color", base, candidato, "--", *rutas])
        if diff.returncode:
            return None
        quitadas, nombres, aserciones = _quitado(diff.stdout)
        if archivo["estado"] != "D" and not quitadas:
            continue  # sólo se agregó: no es una edición que afloje nada
        editados.append({"archivo": archivo["ruta"], "estado": ESTADOS[archivo["estado"]], "origen": archivo["origen"],
                         "lineas_quitadas": quitadas, "tests_quitados": nombres, "asserts_quitados": aserciones})
    return sorted(editados, key=lambda e: e["archivo"])


def del_candidato(ejecutar: Callable, candidato: str, base: str | None = None) -> list[dict] | None:
    """Lo mismo contra la base del candidato (merge-base con main); None si no hay candidato o no se encuentra la base."""
    if not candidato:
        return None
    if base is None:
        p = ejecutar(["git", "merge-base", candidato, "main"])
        if p.returncode:
            return None
        base = p.stdout.strip()
    return tests_editados(ejecutar, base, candidato)


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
