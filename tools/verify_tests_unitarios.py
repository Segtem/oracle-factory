"""Evidencia del contrato de los tests unitarios como práctica: escenarios tu1–tu3 con nombre exacto, y la trazabilidad de esos mismos casos."""
from collections import Counter
from importlib import metadata
import io
import argparse
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.verify_review_guided import Resultado, escribir, sha  # noqa: E402
from oracle_factory import trazabilidad  # noqa: E402
import json  # noqa: E402

CAMBIO = '20261030-185728-0w1-tests'
CONTRACTS = {
    'paso_de_tests_primero': [
        'PasoDeTests.test_tu1_un_cambio_nuevo_en_espanol',
        'PasoDeTests.test_tu1_un_cambio_nuevo_en_ingles',
        'PasoDeTests.test_tu1_la_plantilla_de_cada_idioma_lo_trae',
        'PasoDeTests.test_tu1_el_paso_no_bloquea',
        'PasoDeTests.test_tu1_la_aprobacion_solo_se_niega_por_la_marca_de_pendiente_no_por_el_paso'],
    'guia_de_tests_para_agentes': [
        'GuiaDeTests.test_tu2_la_guia_generada_lo_dice',
        'GuiaDeTests.test_tu2_una_guia_vieja_se_detecta'],
    'documento_de_la_practica': [
        'DocumentoDeTests.test_tu3_explica_las_tres_capas_y_cita_las_fuentes',
        'DocumentoDeTests.test_tu3_dice_lo_mismo_que_la_plantilla',
        'DocumentoDeTests.test_tu3_dice_que_hacer_cuando_no_se_puede_y_nombra_la_excepcion_de_la_spec',
        'DocumentoDeTests.test_tu3_no_dice_que_falta_lo_que_ya_existe'],
}
PREFIX = 'test_tests_unitarios.'
LIMITES = ('Escenarios tu1–tu3 en proyectos temporales (la plantilla y la guía se generan de verdad) y sobre docs/tests.md, en Linux. '
           'Comprueban que el paso y la guarda están dichos; no miden si un agente de verdad escribe los tests primero: eso es práctica, no gate.')


def fuentes(salida=None):
    # Todo lo versionado o nuevo del producto (código, pruebas, datos de referencia, catálogos, docs); sin los registros generados.
    nombres = subprocess.run(['git', '-C', str(ROOT), 'ls-files', '-z', '--cached', '--others', '--exclude-standard'],
                             text=True, capture_output=True, check=True).stdout.split('\0')
    elegidos = [ROOT / n for n in nombres if n and not n.startswith(('.factory/', 'kb/', 'tareas/'))
                and (ROOT / n).is_file() and not (salida and (ROOT / n).is_relative_to(salida))]  # la evidencia no es producto
    head = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True, capture_output=True, check=True).stdout.strip()
    return {'head': head, 'sha256': {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(elegidos)}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida', type=Path, required=True, help='carpeta nueva de evidencia')
    args = parser.parse_args(argv)
    versions = {p: metadata.version(p) for p in ('oracle-metalenguaje', 'oracle-task', 'oracle-clue')}
    output = args.salida.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=False)
    origen = fuentes(output)
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'))
    result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=Resultado).run(suite)
    expected = [PREFIX + name for names in CONTRACTS.values() for name in names]
    observed = {name: count for name, count in result.cantidad.items() if name.startswith(PREFIX)}
    complete = observed == Counter(expected) and all(result.observados.get(name, 1) == 0 for name in expected)
    rows = [{'requisito': suffix, 'caso': name, 'codigo': result.observados.get(PREFIX + name, 1)}
            for suffix, names in CONTRACTS.items() for name in names]
    (output / 'suite.txt').write_text(stream.getvalue(), encoding='utf-8')
    # Los mismos casos, otra vez y trazados: requisito → casos → líneas ejecutadas (oracle-factory trazabilidad lo cruza).
    ids = {r.rsplit('.', 1)[-1]: r for r in json.loads((ROOT / '.factory/cambios' / CAMBIO / 'factory.json').read_text())['requisitos']}
    traza = trazabilidad.trazar(ROOT, {ids[s]: [PREFIX + n for n in names] for s, names in CONTRACTS.items()})
    escribir(output / 'trazabilidad.json', traza)
    trazada = all(c.get('resultado') == 'ok' for c in traza['casos'].values()) and len(traza['casos']) == len(expected)
    stable = fuentes(output) == origen  # después de la segunda corrida, la trazada: ahí también tienen que seguir quietas
    ok = result.wasSuccessful() and complete and stable and trazada
    escribir(output / 'hechos.json', {'tests_unitarios_caso': rows, 'tests_unitarios_corrida': [{'completa': int(ok), 'casos': len(expected)}]})
    escribir(output / 'resultado.json', {'exitoso': ok, 'tests': result.testsRun, 'casos_contrato': len(expected),
             'casos_exactos_sin_omisiones_duplicados_ni_fallas': complete, 'fuentes_estables': stable, 'origen': origen,
             'versiones': {**versions, 'python': sys.version}, 'limites': LIMITES,
             'artefactos_sha256': {name: sha(output / name) for name in ('suite.txt', 'hechos.json', 'trazabilidad.json')}})
    print(f'Evidencia: {output}; {result.testsRun} pruebas, {len(expected)} casos de contrato; éxito: {ok}.')
    print(LIMITES)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
