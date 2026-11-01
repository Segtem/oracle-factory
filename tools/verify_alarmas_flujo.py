"""Evidencia de las alarmas del flujo (bucle de revisión y cambio grande): escenarios af1–af3 con nombre exacto, y la trazabilidad de esos casos."""
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

CAMBIO = '20261101-205730-dm3-alarmasflujo'
CONTRACTS = {
    'el_estado_avisa_cuando_la_revision_lleva_cuatro_rondas': [
        'Rondas.test_af1_cuatro_candidatos_revisados_son_cuatro_rondas_y_avisan',
        'Rondas.test_af1_dos_revisores_del_mismo_candidato_son_una_sola_ronda',
        'Rondas.test_af1_un_registro_ilegible_no_se_cuenta_ni_rompe',
        'Rondas.test_af1_el_umbral_es_cuatro_y_el_aviso_sugiere_parar_a_arreglar_la_clase',
        'Rondas.test_af1_el_mismo_commit_con_otro_largo_de_sha_es_una_sola_ronda',
        'Rondas.test_af1_una_revision_lanzada_cuenta_como_ronda_igual_que_una_pedida',
        'Rondas.test_af1_el_dato_del_json_dice_si_avisa_justo_en_el_umbral',
        'EstadoReal.test_af1_cuatro_rondas_avisan_en_el_texto_y_en_el_json',
        'EstadoReal.test_af1_con_tres_rondas_no_avisa',
        'EstadoReal.test_af1_un_registro_con_eventos_rotos_no_hace_fallar_el_estado',
        'Abandonado.test_af1_un_cambio_abandonado_no_lleva_alarmas_del_flujo_ni_en_el_json'],
    'el_estado_avisa_cuando_el_candidato_agrega_mas_de_450_lineas_de_producto': [
        'Tamano.test_af2_cuentan_las_lineas_agregadas_de_producto_y_no_las_de_pruebas',
        'Tamano.test_af2_lo_que_no_es_producto_no_cuenta',
        'Tamano.test_af2_un_renombre_con_numstat_z_se_lee_con_su_destino',
        'Tamano.test_af2_si_git_falla_no_se_calcula',
        'Tamano.test_af2_el_umbral_es_450_y_justo_en_el_umbral_no_avisa',
        'Tamano.test_af2_el_dato_del_json_dice_si_avisa_justo_en_el_umbral',
        'Tamano.test_af2_si_no_se_encuentra_la_base_no_se_calcula_nada',
        'Tamano.test_af2_la_rama_principal_puede_llamarse_master',
        'Tamano.test_af2_una_salida_rota_o_no_utf8_no_rompe_y_no_se_calcula',
        'Tamano.test_af2_un_avisos_de_cada_uno_cuando_hay_los_dos',
        'EstadoReal.test_af2_un_candidato_grande_avisa_en_el_texto_y_en_el_json_sin_cambiar_los_pendientes',
        'EstadoReal.test_af2_las_pruebas_no_cuentan_en_un_candidato_real',
        'EstadoReal.test_af2_sin_candidato_vigente_no_se_calcula'],
    'el_documento_nombra_los_umbrales_y_dice_que_el_conteo_de_aserciones_es_aproximado': [
        'Documento.test_af3_el_documento_nombra_los_dos_umbrales_y_el_conteo_aproximado',
        'Documento.test_af3_el_contrato_del_verificador_nombra_exactamente_los_casos_que_existen'],
}
PREFIX = 'test_alarmas_flujo.'
LIMITES = ('Escenarios af1–af3 con repositorios Git temporales y un ejecutor falso de Git, en Linux. Comprueban que el estado avisa de las rondas y del '
           'tamaño, que no cambia los pendientes y que el documento coincide con los umbrales del código; no validan que 4 rondas y 450 líneas sean los '
           'umbrales correctos (son referencias de 20 cambios).')


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
    escribir(output / 'hechos.json', {'alarmas_flujo_caso': rows, 'alarmas_flujo_corrida': [{'completa': int(ok), 'casos': len(expected)}]})
    escribir(output / 'resultado.json', {'exitoso': ok, 'tests': result.testsRun, 'casos_contrato': len(expected),
             'casos_exactos_sin_omisiones_duplicados_ni_fallas': complete, 'fuentes_estables': stable, 'origen': origen,
             'versiones': {**versions, 'python': sys.version}, 'limites': LIMITES,
             'artefactos_sha256': {name: sha(output / name) for name in ('suite.txt', 'hechos.json', 'trazabilidad.json')}})
    print(f'Evidencia: {output}; {result.testsRun} pruebas, {len(expected)} casos de contrato; éxito: {ok}.')
    print(LIMITES)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
