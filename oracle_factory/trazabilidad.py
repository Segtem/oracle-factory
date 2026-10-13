"""Trazabilidad por candidato: qué líneas ejecuta cada caso del contrato y cuáles de las cambiadas no respalda ninguno.

`trazar` corre casos de unittest bajo `sys.settrace` (biblioteca estándar, Python 3.11+): la usa el sensor del proyecto
para dejar `trazabilidad.json` en la evidencia. `lineas_ejecutables`, `cambios_del_diff` y `cruzar` son puras.
"""
from __future__ import annotations

import inspect
from pathlib import Path
import re
import sys
import threading
import unittest

ESQUEMA_CASOS = 'oracle-factory.trazabilidad-casos/1'
ESQUEMA = 'oracle-factory.trazabilidad/1'
LIMITES = ('ejecutar una línea no prueba que sea correcta: sólo que algún caso del contrato pasó por ella',
           'el código que corre en otro proceso (por ejemplo, oracle o tasks llamados por la CLI) no se traza')


def trazar(raiz: Path, contratos: dict[str, list[str]]) -> dict:
    """Corre cada caso (id de unittest) con una traza de líneas; devuelve el objeto de `trazabilidad.json`.

    Sólo cuenta archivos dentro de `raiz` y fuera de su `.venv`. Un caso que falla queda con su resultado.
    """
    raiz = raiz.resolve()
    entorno = raiz / '.venv'
    rutas: dict[str, str | None] = {}

    def relativa(nombre: str) -> str | None:
        if nombre not in rutas:
            ruta = Path(nombre).resolve() if not nombre.startswith('<') else None
            rutas[nombre] = (ruta.relative_to(raiz).as_posix()
                             if ruta and ruta.is_relative_to(raiz) and not ruta.is_relative_to(entorno) else None)
        return rutas[nombre]

    casos = {}
    for caso in sorted({c for lista in contratos.values() for c in lista}):
        lineas: dict[str, set[int]] = {}

        def llamada(frame, evento, arg):
            archivo = relativa(frame.f_code.co_filename)
            if archivo is None:
                return None  # ni sus líneas ni las de lo que llame desde ahí sin pasar por el proyecto
            conjunto = lineas.setdefault(archivo, set())
            conjunto.add(frame.f_lineno)  # la línea del def: la función se llamó

            def linea(frame, evento, arg):
                if evento == 'line':
                    conjunto.add(frame.f_lineno)
                return linea
            return linea

        resultado = unittest.TestResult()
        suite = unittest.defaultTestLoader.loadTestsFromName(caso)
        previas = sys.gettrace(), threading.gettrace()  # quien traza a quien traza (el sensor de Factory) la recupera
        sys.settrace(llamada)
        threading.settrace(llamada)
        try:
            suite.run(resultado)
        finally:
            sys.settrace(previas[0])
            threading.settrace(previas[1])
        estado = ('omitido' if resultado.skipped else 'ok' if resultado.wasSuccessful() and resultado.testsRun == 1
                  else 'falla')
        casos[caso] = {'resultado': estado, 'lineas': {a: sorted(ls) for a, ls in sorted(lineas.items())}}
    return {'esquema': ESQUEMA_CASOS, 'requisitos': {r: sorted(c) for r, c in sorted(contratos.items())}, 'casos': casos}


def lineas_ejecutables(texto: str) -> set[int] | None:
    """Las líneas de un archivo Python que una traza puede ver dentro de una función; None si no compila.

    El código de módulo y de cuerpos de clase corre al importar, antes de cualquier caso: no se cuenta.
    """
    try:
        codigo = compile(texto, '<archivo>', 'exec')
    except (SyntaxError, ValueError):
        return None
    lineas, pila = set(), [codigo]
    while pila:
        c = pila.pop()
        if c.co_flags & inspect.CO_OPTIMIZED:  # funciones (y comprensiones), no el módulo ni los cuerpos de clase
            lineas.update(l for _, _, l in c.co_lines() if l is not None)
        pila.extend(k for k in c.co_consts if isinstance(k, type(codigo)))
    return lineas


def cambios_del_diff(diff: str) -> dict[str, set[int]]:
    """Líneas agregadas o modificadas por archivo (numeración del candidato) en la salida de `git diff -U0`."""
    cambios: dict[str, set[int]] = {}
    archivo = None
    for linea in diff.splitlines():
        if linea.startswith('+++ '):
            archivo = linea[6:] if linea.startswith('+++ b/') else None  # /dev/null: el archivo se borró
        elif linea.startswith('@@') and archivo is not None:
            m = re.match(r'@@ -\S+ \+(\d+)(?:,(\d+))? @@', linea)
            if m:
                inicio, cantidad = int(m[1]), int(m[2] if m[2] is not None else 1)
                if cantidad:
                    cambios.setdefault(archivo, set()).update(range(inicio, inicio + cantidad))
    return cambios


def cruzar(trazas: dict, cambios: dict[str, set[int]], ejecutables: dict[str, set[int] | None]) -> dict:
    """Por requisito, las líneas cambiadas que ejecutan sus casos; las ejecutables que no ejecuta ninguno; lo no rastreable."""
    casos = trazas.get('casos') or {}

    def ejecutadas(lista) -> dict[str, set[int]]:
        union: dict[str, set[int]] = {}
        for caso in lista:
            for archivo, ls in ((casos.get(caso) or {}).get('lineas') or {}).items():
                union.setdefault(archivo, set()).update(ls)
        return union

    def interseccion(ejec: dict[str, set[int]]) -> dict[str, list[int]]:
        return {a: sorted(cambios[a] & ejec[a]) for a in sorted(cambios) if a in ejec and cambios[a] & ejec[a]}

    todas = ejecutadas(casos)
    requisitos = {r: {'casos': [{'caso': c, 'resultado': (casos.get(c) or {}).get('resultado', 'sin traza')} for c in lista],
                      'lineas': interseccion(ejecutadas(lista))}
                  for r, lista in sorted((trazas.get('requisitos') or {}).items())}
    sin_respaldo = {}
    for archivo in sorted(cambios):
        visibles = ejecutables.get(archivo)
        if visibles is not None:
            faltan = sorted((cambios[archivo] & visibles) - todas.get(archivo, set()))
            if faltan:
                sin_respaldo[archivo] = faltan
    return {'requisitos': requisitos, 'sin_respaldo': sin_respaldo,
            'no_rastreables': [a for a in sorted(cambios) if ejecutables.get(a) is None], 'limites': list(LIMITES)}


if __name__ == '__main__':
    fuente = 'X = 1\n\ndef f(a):\n    # nota\n    return a + 1\n\nclass C:\n    y = 2\n\n    def g(self):\n        return 3\n'
    assert lineas_ejecutables(fuente) == {3, 5, 10, 11} and lineas_ejecutables('def (') is None
    diff = '+++ b/x.py\n@@ -1,0 +2,2 @@\n+a\n+b\n@@ -9 +11 @@\n-c\n+d\n+++ /dev/null\n@@ -1 +0,0 @@\n+++ b/y.md\n@@ -3,1 +3,0 @@\n'
    assert cambios_del_diff(diff) == {'x.py': {2, 3, 11}}
    t = {'requisitos': {'r': ['c1']}, 'casos': {'c1': {'resultado': 'ok', 'lineas': {'x.py': [2]}}}}
    c = cruzar(t, {'x.py': {2, 3, 4}, 'y.md': {1}}, {'x.py': {2, 3}, 'y.md': None})
    assert c['requisitos']['r']['lineas'] == {'x.py': [2]} and c['sin_respaldo'] == {'x.py': [3]} and c['no_rastreables'] == ['y.md']
    print('ok')
