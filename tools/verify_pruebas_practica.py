"""Evidencia de las pruebas como práctica de desarrollo: escenarios pp1–pp3 con nombre exacto, y la trazabilidad de esos casos."""
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

CAMBIO = '20261031-011717-c2q-pruebaspractica'
CONTRACTS = {
    'la_plantilla_de_tareas_pide_escribir_primero_las_pruebas': [
        'Pruebas.test_pp1_un_cambio_nuevo_en_espanol_pide_las_pruebas_antes_de_implementar',
        'Pruebas.test_pp1_un_cambio_nuevo_en_ingles_pide_las_pruebas_antes_de_implementar',
        'Pruebas.test_pp1_el_paso_nuevo_no_cambia_los_demas_pasos'],
    'el_estado_avisa_de_los_requisitos_sin_pruebas_sin_bloquear': [
        'Pruebas.test_pp2_un_requisito_sin_casos_se_nombra_y_el_otro_no',
        'Pruebas.test_pp2_un_requisito_ausente_de_la_trazabilidad_tambien_cuenta_como_sin_casos',
        'Pruebas.test_pp2_un_candidato_sin_trazabilidad_lo_dice',
        'Pruebas.test_pp2_una_trazabilidad_ilegible_cuenta_como_sin_trazabilidad_y_no_rompe_el_estado',
        'Pruebas.test_pp2_una_trazabilidad_de_otro_esquema_no_se_toma_por_valida',
        'Pruebas.test_pp2_una_trazabilidad_que_es_un_enlace_simbolico_no_se_sigue',
        'Pruebas.test_pp2_con_casos_en_todos_no_hay_aviso_de_pruebas',
        'Pruebas.test_pp2_sin_candidato_todavia_no_hay_nada_que_avisar',
        'Pruebas.test_pp2_un_cambio_sin_requisitos_importados_o_cerrado_no_avisa',
        'Analisis.test_el_analisis_de_requisitos_con_y_sin_casos',
        'Analisis.test_un_caso_vacio_o_no_texto_no_cuenta_como_caso'],
    'una_excepcion_declarada_en_la_spec_explica_por_que_no_hay_pruebas': [
        'Pruebas.test_pp3_una_excepcion_con_motivo_se_muestra_y_ese_requisito_no_avisa',
        'Pruebas.test_pp3_la_excepcion_tambien_vale_sin_trazabilidad',
        'Pruebas.test_pp3_una_excepcion_sin_motivo_se_rechaza_al_aprobar_la_spec_y_no_se_modifica_el_registro',
        'Pruebas.test_pp3_una_excepcion_sin_motivo_tambien_se_rechaza_al_importar',
        'Pruebas.test_pp3_una_excepcion_sin_motivo_que_llego_al_estado_no_exceptua_y_se_avisa',
        'Pruebas.test_pp3_un_valor_desconocido_de_pruebas_se_rechaza_en_vez_de_ignorarse',
        'Pruebas.test_pp3_la_linea_pruebas_solo_cuenta_en_la_cabecera_del_requisito_no_en_los_escenarios',
        'Pruebas.test_pp3_la_excepcion_se_asocia_al_requisito_por_su_nombre_y_no_a_otro',
        'Pruebas.test_pp3_lo_que_la_spec_retira_no_lleva_excepcion',
        'Pruebas.test_pp3_sin_excepciones_la_spec_se_lee_como_siempre'],
}
PREFIX = 'test_pruebas_practica.'
LIMITES = ('Escenarios pp1–pp3 sobre proyectos temporales, con la trazabilidad que dejaría el sensor escrita a mano y el candidato vigente '
           'simulado. No se comprueba un sensor real que genere trazabilidad.json, ni qué tan buenas son las pruebas de un cambio: sólo que '
           'el estado avisa de las que faltan.')


def fuentes():
    files = [ROOT / 'fabrica.py', ROOT / 'pyproject.toml', Path(__file__), *ROOT.glob('oracle_factory/*.py'),
             *ROOT.glob('tests/*.py'), ROOT / 'oracle_factory/pruebas.py', ROOT / 'docs/trazabilidad.md',
             *ROOT.glob('catalogos/factory_pruebas_practica.*.oracle')]
    head = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True, capture_output=True, check=True).stdout.strip()
    return {'head': head, 'sha256': {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(files))}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida', type=Path, required=True, help='carpeta nueva de evidencia')
    args = parser.parse_args(argv)
    versions = {p: metadata.version(p) for p in ('oracle-metalenguaje', 'oracle-task', 'oracle-clue')}
    output = args.salida.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=False)
    origen = fuentes()
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'))
    result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=Resultado).run(suite)
    expected = [PREFIX + name for names in CONTRACTS.values() for name in names]
    observed = {name: count for name, count in result.cantidad.items() if name in expected}
    complete = observed == Counter(expected) and all(result.observados.get(name, 1) == 0 for name in expected)
    stable = fuentes() == origen
    ok = result.wasSuccessful() and complete and stable
    rows = [{'requisito': suffix, 'caso': name, 'codigo': result.observados.get(PREFIX + name, 1)}
            for suffix, names in CONTRACTS.items() for name in names]
    (output / 'suite.txt').write_text(stream.getvalue(), encoding='utf-8')
    # Los mismos casos, otra vez y trazados: requisito → casos → líneas ejecutadas (oracle-factory trazabilidad lo cruza).
    ids = {r.rsplit('.', 1)[-1]: r for r in json.loads((ROOT / '.factory/cambios' / CAMBIO / 'factory.json').read_text())['requisitos']}
    escribir(output / 'trazabilidad.json', trazabilidad.trazar(ROOT, {ids[s]: [PREFIX + n for n in names]
                                                                     for s, names in CONTRACTS.items()}))
    escribir(output / 'hechos.json', {'pruebas_practica_caso': rows, 'pruebas_practica_corrida': [{'completa': int(ok), 'casos': len(expected)}]})
    escribir(output / 'resultado.json', {'exitoso': ok, 'tests': result.testsRun, 'casos_contrato': len(expected),
             'casos_exactos_sin_omisiones_duplicados_ni_fallas': complete, 'fuentes_estables': stable, 'origen': origen,
             'versiones': {**versions, 'python': sys.version}, 'limites': LIMITES,
             'artefactos_sha256': {name: sha(output / name) for name in ('suite.txt', 'hechos.json', 'trazabilidad.json')}})
    print(f'Evidencia: {output}; {result.testsRun} pruebas, {len(expected)} casos de contrato; éxito: {ok}.')
    print(LIMITES)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
