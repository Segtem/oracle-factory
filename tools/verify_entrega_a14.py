"""Evidencia de la preparación y comprobación de la distribución 0.1.0a14.

Verifica:
- ea1: la versión de entrega es coherente y declara su estado (metadatos, CLI, docs, web y distinción de publicación).
- ea2: la distribución instalada ofrece las consultas del proyecto (instalación aislada, origen site-packages, conteos, elaboración fixture con rechazo de escrituras).
- ea3: la entrega registra sus pruebas y sus límites (arneses, suite, hashes, trazabilidad y estabilidad de fuentes).
"""
from __future__ import annotations

import argparse
from collections import Counter
from importlib import metadata
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.verify_review_guided import Resultado, escribir, sha  # noqa: E402
from oracle_factory import trazabilidad, cli  # noqa: E402

CAMBIO = "20261025-122552-ho0-entrega-a14"
CONTRACTS = {
    "la_version_de_entrega_es_coherente_y_declara_su_estado": [
        "EntregaA14.test_ea1_version_coherente_y_estado_declarado",
    ],
    "la_distribucion_instalada_ofrece_las_consultas_del_proyecto": [
        "EntregaA14.test_ea2_distribucion_instalada_consultas_registro_y_elaboracion",
    ],
    "la_entrega_registra_sus_pruebas_y_sus_limites": [
        "EntregaA14.test_ea3_entrega_registra_pruebas_y_limites",
    ],
}
PREFIX = "test_entrega_a14."
LIMITES = (
    "Comprobación de la distribución 0.1.0a14 fuera del checkout en Linux con Python 3.13; "
    "wheel instalado en entorno aislado sin resolver módulos del repositorio. "
    "Conteos desde el registro con fuentes; elaboración simulada con servidor HTTP local fixture "
    "que rechaza escrituras; las pruebas simuladas no certifican calidad de un modelo real. "
    "No equivale a una publicación en PyPI ni reemplaza las decisiones humanas de Brian."
)


def fuentes():
    # Incluye recursos empaquetados, JS, guías y verificadores; excluye registros generados.
    nombres = subprocess.run(
        ['git', 'ls-files', '--cached', '--others', '--exclude-standard'], cwd=ROOT,
        text=True, capture_output=True, check=True).stdout.splitlines()
    elegidos = [ROOT / n for n in nombres if not n.startswith(
        ('.factory/', 'kb/', 'tareas/', 'openspec/')) and (ROOT / n).is_file()]
    head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                          text=True, capture_output=True, check=True).stdout.strip()
    return {'head': head, 'sha256': {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(elegidos)}}


def linea_base_valida(filas):
    from tools.mutar_entrega_a14 import MUTACIONES, CASOS
    esperados = Counter({CASOS[m[4]]: 1 for m in MUTACIONES})
    return (isinstance(filas, list) and Counter(b.get('caso') for b in filas) == esperados
            and all(type(b.get('codigo')) is int and b['codigo'] == 0 for b in filas))


def mutaciones_validas(datos, origen):
    from tools.mutar_entrega_a14 import MUTACIONES
    if not isinstance(datos, dict) or datos.get('fuentes') != origen:
        return False
    if not linea_base_valida(datos.get('linea_base')):
        return False
    filas = datos.get('mutaciones', [])
    esperadas = Counter(m[0] for m in MUTACIONES)
    if Counter(m.get('id') for m in filas) != esperadas:
        return False
    return datos.get('todas_detectadas') is True and all(
        m.get('detectada') is True and type(m.get('codigo')) is int and m['codigo'] == 1 for m in filas)


def suite_completa(resultado, esperado):
    return (bool(esperado) and resultado.cantidad == esperado
            and all(n == 1 for n in esperado.values())
            and all(resultado.observados.get(n, 1) == 0 for n in esperado)
            and not resultado.skipped and not resultado.expectedFailures
            and not resultado.unexpectedSuccesses and resultado.wasSuccessful())


def corrida_valida(completa, mutaciones_ok, origen, actual, arneses):
    return (completa and mutaciones_ok and origen == actual
            and all(arneses.get(n, {}).get('returncode') == 0
                    for n in ('verify_installed', 'verify_guide')))


def casos_de(suite):
    for caso in suite:
        if isinstance(caso, unittest.TestSuite):
            yield from casos_de(caso)
        else:
            yield caso.id()


def main(argv=None):
    from tools import probar_entrega_a14
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida', type=Path, required=True)
    parser.add_argument('--mutaciones', type=Path, required=True)
    args = parser.parse_args(argv)
    origen = fuentes()
    mut_datos = json.loads(args.mutaciones.read_text(encoding='utf-8'))
    if not mutaciones_validas(mut_datos, origen):
        parser.error('mutaciones incompletas, no detectadas o ajenas a las fuentes actuales')
    output = args.salida.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=False)
    escribir(output / 'mutaciones.json', mut_datos)
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'))
    esperado = Counter(casos_de(suite))
    result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=Resultado).run(suite)
    (output / 'suite.txt').write_text(stream.getvalue(), encoding='utf-8')
    completa = suite_completa(result, esperado)
    esperado_contrato = [PREFIX + n for names in CONTRACTS.values() for n in names]
    contratos_ok = all(result.cantidad.get(n) == 1 and result.observados.get(n) == 0
                       for n in esperado_contrato)
    prueba = {}
    error = None
    try:
        prueba = probar_entrega_a14.ejecutar_comprobacion_completa(output / 'dist')
    except Exception as exc:
        error = f'{type(exc).__name__}: {exc}'
    escribir(output / 'instalacion.json', {'comprobacion': prueba, 'error': error})
    actual = fuentes()
    ok = corrida_valida(completa and contratos_ok, True, origen, actual, prueba.get('arneses', {}))
    factory = json.loads((ROOT / '.factory/cambios' / CAMBIO / 'factory.json').read_text())
    ids = {r.rsplit('.', 1)[-1]: r for r in factory.get('requisitos', [])}
    if set(ids) != set(CONTRACTS):
        ok = False
    mapa = {ids[s]: [PREFIX + n for n in names] for s, names in CONTRACTS.items() if s in ids}
    escribir(output / 'trazabilidad.json', trazabilidad.trazar(ROOT, mapa))
    hechos = {
        'entrega_caso': [{'requisito': s, 'caso': n, 'codigo': result.observados.get(PREFIX + n, 1)}
                         for s, names in CONTRACTS.items() for n in names],
        'entrega_suite': [{'completa': int(ok), 'casos': len(esperado_contrato)}],
        'entrega_mutacion': [{'id': m['id'], 'detectada': int(m['detectada'])}
                             for m in mut_datos['mutaciones']],
    }
    escribir(output / 'hechos.json', hechos)
    archivos = [p for p in output.rglob('*') if p.is_file()]
    escribir(output / 'resultado.json', {
        'exitoso': bool(ok), 'tests': result.testsRun, 'tests_esperados': sum(esperado.values()),
        'casos_exactos_sin_omisiones_duplicados_ni_fallas': completa and contratos_ok,
        'omitidos': [(c.id(), motivo) for c, motivo in result.skipped],
        'fuentes_estables': actual == origen, 'origen': origen,
        'versiones': {**{p: metadata.version(p) for p in
                        ('oracle-metalenguaje', 'oracle-task', 'oracle-clue')}, 'python': sys.version},
        'limites': LIMITES,
        'artefactos_sha256': {p.relative_to(output).as_posix(): sha(p) for p in sorted(archivos)},
    })
    print(f'Evidencia: {output}; tests {result.testsRun}/{sum(esperado.values())}; éxito: {bool(ok)}')
    if error:
        print(error)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
