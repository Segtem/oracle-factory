"""Evidencia de los tests editados: escenarios te1–te3 con nombre exacto, y la trazabilidad de esos casos."""
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

CAMBIO = '20261101-012816-1qf-testseditados'
CONTRACTS = {
    'el_estado_avisa_de_los_tests_existentes_que_el_cambio_modifico_o_borro': [
        'EstadoAvisa.test_te1_un_archivo_borrado_y_un_test_con_su_asercion_quitados',
        'A.test_te1_un_archivo_de_pruebas_renombrado_con_tests_quitados',
        'A.test_te1_solo_agregar_tests_y_archivos_nuevos_no_avisa',
        'A.test_te1_sin_candidato_vigente_no_se_calcula',
        'A.test_te1_un_cambio_de_linea_en_un_test_cuenta_como_quitada',
        'A.test_te1_el_texto_del_estado_nombra_cada_archivo_y_no_es_un_pendiente',
        'GitFalso.test_te1_si_git_falla_al_listar_o_al_leer_un_archivo_no_se_calcula_nada',
        'GitFalso.test_te1_sin_candidato_o_sin_base_no_se_calcula_y_no_se_llama_a_git_de_mas',
        'GitFalso.test_te1_con_la_base_dada_no_se_busca_el_merge_base',
        'GitFalso.test_te1_la_lista_sale_ordenada_por_archivo_y_nombra_el_origen_de_un_renombre'],
    'el_pedido_al_revisor_lleva_los_tests_editados': [
        'PedidoAlRevisor.test_te2_el_pedido_nombra_los_tests_quitados_y_pide_mencionarlos',
        'PedidoAlRevisor.test_te2_sin_tests_editados_el_pedido_es_el_mismo',
        'PedidoAlRevisor.test_te2_la_revision_se_pide_igual_aunque_haya_tests_editados',
        'GitFalso.test_te2_el_texto_para_el_revisor_nombra_cada_archivo_y_sin_nada_es_vacio'],
    'solo_cuentan_los_archivos_de_pruebas': [
        'QueEsUnTest.test_te3_los_nombres_de_archivos_de_pruebas',
        'QueEsUnTest.test_te3_los_que_no_son_de_pruebas',
        'ProductoNoAvisa.test_te3_un_archivo_de_producto_que_pierde_lineas_no_avisa',
        'ProductoNoAvisa.test_te3_un_archivo_de_documentacion_sobre_tests_tampoco'],
}
PREFIX = 'test_tests_editados.'
LIMITES = ('Escenarios te1–te3 sobre repositorios Git temporales y un ejecutor de Git falso, en Linux. Comprueban que el aviso sale en el '
           'estado, en su JSON y en el pedido al revisor, y qué archivos cuentan como de pruebas; no juzgan si una edición fue legítima, y las '
           'convenciones fuera de tests/test, test_*, *_test.* y *.test.* (por ejemplo __tests__ o *.spec.*) no se miran todavía.')


def fuentes(salida=None):
    # Todo lo versionado o nuevo del producto (código, pruebas, datos de referencia, catálogos, docs); sin los registros generados.
    nombres = subprocess.run(['git', '-C', str(ROOT), 'ls-files', '-z', '--cached', '--others', '--exclude-standard'],
                             text=True, capture_output=True, check=True).stdout.split('\0')  # -z: nombres no ASCII sin comillas
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
    escribir(output / 'hechos.json', {'tests_editados_caso': rows, 'tests_editados_corrida': [{'completa': int(ok), 'casos': len(expected)}]})
    escribir(output / 'resultado.json', {'exitoso': ok, 'tests': result.testsRun, 'casos_contrato': len(expected),
             'casos_exactos_sin_omisiones_duplicados_ni_fallas': complete, 'fuentes_estables': stable, 'origen': origen,
             'versiones': {**versions, 'python': sys.version}, 'limites': LIMITES,
             'artefactos_sha256': {name: sha(output / name) for name in ('suite.txt', 'hechos.json', 'trazabilidad.json')}})
    print(f'Evidencia: {output}; {result.testsRun} pruebas, {len(expected)} casos de contrato; éxito: {ok}.')
    print(LIMITES)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
