"""Trazabilidad por candidato: qué líneas ejecuta cada caso del contrato y cuáles de las cambiadas no respalda ninguno.

`trazar` corre casos de unittest bajo `sys.settrace` (biblioteca estándar, Python 3.11+): la usa el sensor del proyecto
para dejar `trazabilidad.json` en la evidencia. `lineas_ejecutables`, `archivos_cambiados`, `lineas_agregadas` y `cruzar`
son puras.
"""
from __future__ import annotations

import ast
import inspect
from pathlib import Path
import re
import sys
import threading
import unittest

ESQUEMA_CASOS = 'oracle-factory.trazabilidad-casos/1'
ESQUEMA = 'oracle-factory.trazabilidad/1'
LIMITES = ('ejecutar una línea no prueba que sea correcta: sólo que algún caso del contrato pasó por ella',
           'el código que corre en otro proceso (por ejemplo, oracle o tasks llamados por la CLI) no se traza',
           'lo que corre al importar un módulo (constantes, imports, cuerpos de clase) pasa antes que los casos: '
           'se lista aparte, sin decir si tiene respaldo')


def _encadenada(previa, propia):
    """Una función de traza local que entrega cada evento a la previa (si la hay) y a la propia (si la hay)."""
    def ambas(frame, evento, arg):
        nonlocal previa
        if previa is not None:
            previa = previa(frame, evento, arg)
        if propia is not None:
            propia(frame, evento)
        return ambas if previa is not None or propia is not None else None
    return ambas


def trazar(raiz: Path, contratos: dict[str, list[str]]) -> dict:
    """Corre cada caso (id de unittest) con una traza de líneas; devuelve el objeto de `trazabilidad.json`.

    Sólo cuenta archivos dentro de `raiz` y fuera de su `.venv`. Un caso que falla queda con su resultado. Quien ya
    trazaba (otro sensor, un depurador) sigue recibiendo sus eventos: la traza se encadena, no se reemplaza.
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

        def con_previa(previa):
            def llamada(frame, evento, arg):
                otra = previa(frame, evento, arg) if previa is not None else None
                archivo = relativa(frame.f_code.co_filename)
                propia = None
                if archivo is not None:
                    conjunto = lineas.setdefault(archivo, set())
                    conjunto.add(frame.f_lineno)  # la primera línea del código llamado: se llamó

                    def propia(frame, evento):
                        if evento == 'line':
                            conjunto.add(frame.f_lineno)
                if otra is None and propia is None:
                    return None
                return otra if propia is None else _encadenada(otra, propia)
            return llamada

        resultado = unittest.TestResult()
        suite = unittest.defaultTestLoader.loadTestsFromName(caso)
        previas = sys.gettrace(), threading.gettrace()
        sys.settrace(con_previa(previas[0]))
        threading.settrace(con_previa(previas[1]))
        try:
            suite.run(resultado)
        finally:
            sys.settrace(previas[0])
            threading.settrace(previas[1])
        # Una falla gana a una omisión: un caso puede tener subpruebas omitidas y otras que fallan.
        estado = ('falla' if not resultado.wasSuccessful() or resultado.testsRun != 1
                  else 'omitido' if resultado.skipped else 'ok')
        casos[caso] = {'resultado': estado, 'lineas': {a: sorted(ls) for a, ls in sorted(lineas.items())}}
    return {'esquema': ESQUEMA_CASOS, 'requisitos': {r: sorted(c) for r, c in sorted(contratos.items())}, 'casos': casos}


def lineas_ejecutables(texto: str) -> tuple[set[int], set[int], dict[int, int]] | None:
    """(líneas que corren dentro de funciones, líneas que corren al importar, {decorador: def}); None si no compila.

    Las de funciones son las que una traza de los casos puede ver: también los cuerpos de clases definidas dentro de
    una función. Las de módulo y de clases del módulo corren al importar, antes de cualquier caso. En una función
    decorada, la traza ve la línea del primer decorador; el `def` cuenta como ejecutado cuando ese decorador lo está.
    Los comentarios y las líneas en blanco no están en ninguna.
    """
    try:
        codigo = compile(texto, '<archivo>', 'exec')
        arbol = ast.parse(texto)
    except (SyntaxError, ValueError):
        return None
    funciones, importar, pila = set(), set(), [(codigo, False)]
    while pila:
        c, en_funcion = pila.pop()
        en_funcion = en_funcion or bool(c.co_flags & inspect.CO_OPTIMIZED)  # funciones y comprensiones, o lo que corre dentro
        (funciones if en_funcion else importar).update(l for _, _, l in c.co_lines() if l)  # la 0 es el arranque, no una línea
        pila.extend((k, en_funcion) for k in c.co_consts if isinstance(k, type(codigo)))
    decorados = {min(d.lineno for d in n.decorator_list): n.lineno for n in ast.walk(arbol)
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.decorator_list}
    funciones |= set(decorados.values())
    # El cuerpo de `if __name__ == "__main__":` no corre al importar: es ejecutable, y sólo un caso lo podría respaldar.
    for n in arbol.body:
        if isinstance(n, ast.If) and _es_principal(n.test):
            principal = set(range(n.body[0].lineno, n.body[-1].end_lineno + 1)) & importar
            funciones |= principal
    return funciones, importar - funciones, decorados


def _es_principal(test) -> bool:
    """`__name__ == "__main__"` en cualquier orden; no `!=` (ese cuerpo sí corre al importar) ni comparaciones encadenadas."""
    if not (isinstance(test, ast.Compare) and len(test.ops) == 1 and isinstance(test.ops[0], ast.Eq)):
        return False
    lados = (test.left, test.comparators[0])
    return (any(isinstance(l, ast.Name) and l.id == '__name__' for l in lados)
            and any(isinstance(l, ast.Constant) and l.value == '__main__' for l in lados))


def archivos_cambiados(name_status: str) -> list[dict]:
    """La salida de `git diff --name-status -z -M`: [{estado, ruta, origen}], con los nombres exactos (sin comillas)."""
    partes = name_status.split('\0')
    archivos, i = [], 0
    while i < len(partes) and partes[i]:
        estado = partes[i][0]
        if estado in 'RC':  # renombre o copia: origen y destino
            archivos.append({'estado': estado, 'origen': partes[i + 1], 'ruta': partes[i + 2]})
            i += 3
        else:
            archivos.append({'estado': estado, 'origen': None, 'ruta': partes[i + 1]})
            i += 2
    return archivos


def lineas_agregadas(diff: str) -> set[int]:
    """Las líneas agregadas o modificadas (numeración del candidato) en el `git diff -U0` de un archivo."""
    lineas = set()
    for m in re.finditer(r'^@@ -\S+ \+(\d+)(?:,(\d+))? @@', diff, re.MULTILINE):
        inicio, cantidad = int(m[1]), int(m[2] if m[2] is not None else 1)
        lineas.update(range(inicio, inicio + cantidad))
    return lineas


def cruzar(trazas: dict, cambios: dict[str, set[int]], ejecutables: dict[str, tuple | None],
           borrados: list[str] = ()) -> dict:
    """Por requisito, las líneas cambiadas que ejecutan sus casos; las de funciones que no ejecuta ninguno; las que corren
    al importar; los archivos que la traza no puede ver; y los borrados."""
    casos = trazas.get('casos') or {}

    def ejecutadas(lista) -> dict[str, set[int]]:
        union: dict[str, set[int]] = {}
        for caso in lista:
            for archivo, ls in ((casos.get(caso) or {}).get('lineas') or {}).items():
                decorados = (ejecutables.get(archivo) or ((), (), {}))[2]
                union.setdefault(archivo, set()).update([*ls, *(decorados[l] for l in ls if l in decorados)])
        return union

    def interseccion(ejec: dict[str, set[int]]) -> dict[str, list[int]]:
        return {a: sorted(cambios[a] & ejec[a]) for a in sorted(cambios) if a in ejec and cambios[a] & ejec[a]}

    todas = ejecutadas(casos)
    requisitos = {r: {'casos': [{'caso': c, 'resultado': (casos.get(c) or {}).get('resultado', 'sin traza')} for c in lista],
                      'lineas': interseccion(ejecutadas(lista))}
                  for r, lista in sorted((trazas.get('requisitos') or {}).items())}
    sin_respaldo, al_importar = {}, {}
    for archivo in sorted(cambios):
        visibles = ejecutables.get(archivo)
        if visibles is None:
            continue
        faltan = sorted((cambios[archivo] & visibles[0]) - todas.get(archivo, set()))
        importa = sorted(cambios[archivo] & visibles[1])
        if faltan:
            sin_respaldo[archivo] = faltan
        if importa:
            al_importar[archivo] = importa
    return {'requisitos': requisitos, 'sin_respaldo': sin_respaldo, 'al_importar': al_importar,
            'no_rastreables': [a for a in sorted(cambios) if ejecutables.get(a) is None], 'borrados': sorted(borrados),
            'limites': list(LIMITES)}


if __name__ == '__main__':
    fuente = ('X = 1\n\ndef f(a):\n    # nota\n    return a + 1\n\nclass C:\n    y = 2\n\n    def g(self):\n        return 3\n'
              '\n@staticmethod\ndef h():\n    class L:\n        z = 4\n    return L\n')
    assert lineas_ejecutables(fuente) == ({3, 5, 10, 11, 13, 14, 15, 16, 17}, {1, 7, 8}, {13: 14})
    assert lineas_ejecutables('def (') is None
    assert lineas_ejecutables("A = 1\nif __name__ == '__main__':\n    print(A)\n")[:2] == ({3}, {1, 2})
    assert lineas_ejecutables("A = 1\nif '__main__' == __name__:\n    print(A)\n")[:2] == ({3}, {1, 2})
    assert lineas_ejecutables("A = 1\nif __name__ != '__main__':\n    print(A)\n")[:2] == (set(), {1, 2, 3})
    assert archivos_cambiados('M\0a b.py\0R087\0viejo.py\0nuevo.py\0D\0x.md\0') == [
        {'estado': 'M', 'origen': None, 'ruta': 'a b.py'}, {'estado': 'R', 'origen': 'viejo.py', 'ruta': 'nuevo.py'},
        {'estado': 'D', 'origen': None, 'ruta': 'x.md'}]
    assert lineas_agregadas('@@ -1,0 +2,2 @@\n+a\n+b\n@@ -9 +11 @@\n-c\n+d\n@@ -3,2 +12,0 @@\n') == {2, 3, 11}
    t = {'requisitos': {'r': ['c1']}, 'casos': {'c1': {'resultado': 'ok', 'lineas': {'x.py': [2]}}}}
    c = cruzar(t, {'x.py': {1, 2, 3, 4}, 'y.md': set()}, {'x.py': ({2, 3, 4}, {1}, {2: 4}), 'y.md': None}, ['z.py'])
    assert c['requisitos']['r']['lineas'] == {'x.py': [2, 4]} and c['sin_respaldo'] == {'x.py': [3]}  # 4: el def de 2
    assert c['al_importar'] == {'x.py': [1]} and c['no_rastreables'] == ['y.md'] and c['borrados'] == ['z.py']
    print('ok')
