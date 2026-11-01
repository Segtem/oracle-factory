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


def tests_editados(ejecutar: Callable, base: str, candidato: str, es_producto: Callable[[str], bool] | None = None) -> list[dict] | None:
    """Los archivos de pruebas de `base` que `candidato` borró, renombró o a los que les quitó líneas; None si Git no pudo.

    Un archivo es «de pruebas» por su ruta en la base (lo que ya existía), y se miran sólo los archivos del producto (`es_producto`,
    si se da): los registros generados no cuentan. Un renombre avisa siempre: mover un test a un archivo que nadie ejecuta lo desactiva."""
    lista = ejecutar(["git", "diff", "--name-status", "-z", "-M", base, candidato])
    if lista.returncode:
        return None
    editados = []
    for archivo in trazabilidad.archivos_cambiados(lista.stdout):
        origen = archivo["origen"] or archivo["ruta"]  # la ruta en la base
        if archivo["estado"] not in ESTADOS or not es_de_pruebas(origen):
            continue  # agregados (A) y copias (C) son tests nuevos: libres; y lo que no era de pruebas en la base, no es un test existente
        if es_producto is not None and not (es_producto(origen) or es_producto(archivo["ruta"])):
            continue
        rutas = [archivo["origen"], archivo["ruta"]] if archivo["origen"] else [archivo["ruta"]]
        diff = ejecutar(["git", "--literal-pathspecs", "diff", "-U0", "-M", "--no-color", base, candidato, "--", *rutas])
        if diff.returncode:
            return None
        quitadas, nombres, aserciones = _quitado(diff.stdout)
        if archivo["estado"] == "M" and not quitadas:
            continue  # sólo se agregó: no es una edición que afloje nada
        editados.append({"archivo": archivo["ruta"], "estado": ESTADOS[archivo["estado"]], "origen": archivo["origen"],
                         "lineas_quitadas": quitadas, "tests_quitados": nombres, "asserts_quitados": aserciones})
    return sorted(editados, key=lambda e: e["archivo"])


def del_candidato(ejecutar: Callable, candidato: str, base: str | None = None,
                  es_producto: Callable[[str], bool] | None = None) -> list[dict] | None:
    """Lo mismo contra la base del candidato (merge-base con main); None si no hay candidato o no se encuentra la base."""
    if not candidato:
        return None
    if base is None:
        p = ejecutar(["git", "merge-base", candidato, "main"])
        if p.returncode:
            return None
        base = p.stdout.strip()
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
