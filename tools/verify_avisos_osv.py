"""Evidencia de la consulta de avisos a OSV: escenarios ao1–ao3 con nombre exacto contra un servidor local, y la trazabilidad de esos casos."""
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

CAMBIO = '20261029-164101-xux-avisososv'
CONTRACTS = {
    'sin_autorizacion_de_red_no_se_consulta_osv': [
        'SinAutorizacion.test_ao1_sin_la_bandera_de_red_no_se_abre_ninguna_conexion_ni_se_crea_archivo',
        'SinAutorizacion.test_ao1_sin_la_bandera_tampoco_se_conecta_a_un_servidor_que_no_existe',
        'SinAutorizacion.test_ao1_la_bandera_de_red_sola_no_consulta_nada',
        'SinAutorizacion.test_ao1_salida_sin_consultar_es_un_error',
        'SinAutorizacion.test_ao1_no_se_combina_con_auditar_buscar_avisos_ni_un_cambio'],
    'la_consulta_a_osv_guarda_avisos_validos_y_audita': [
        'ConsultaGuardaYAudita.test_ao2_una_dependencia_afectada_se_guarda_como_aviso_valido_y_nombra_al_candidato',
        'ConsultaGuardaYAudita.test_ao2_sale_solo_nombre_version_y_ecosistema_de_cada_dependencia_distinta_una_vez',
        'ConsultaGuardaYAudita.test_ao2_sin_avisos_dice_cuantas_consulto_y_no_guarda_archivo',
        'ConsultaGuardaYAudita.test_ao2_sin_avisos_en_json_es_una_auditoria_vacia',
        'ConsultaGuardaYAudita.test_ao2_un_aviso_de_otra_version_se_guarda_y_no_expone_a_nadie',
        'ConsultaGuardaYAudita.test_ao2_la_version_corregida_se_consulta_sin_su_sufijo',
        'ConsultaGuardaYAudita.test_ao2_un_aviso_que_alcanza_a_dos_dependencias_se_baja_una_vez',
        'ConsultaGuardaYAudita.test_ao2_el_identificador_del_aviso_se_escapa_en_la_ruta',
        'ConsultaGuardaYAudita.test_ao2_muchas_dependencias_se_consultan_en_lotes',
        'ConsultaGuardaYAudita.test_ao2_la_salida_indicada_se_respeta_y_la_de_por_omision_no_se_crea',
        'ConsultaGuardaYAudita.test_ao2_con_avisos_el_json_tambien_dice_cuantas_dependencias_se_consultaron',
        'ConsultaGuardaYAudita.test_ao2_el_archivo_guardado_se_audita_despues_con_auditar'],
    'un_fallo_de_consulta_no_se_lee_como_sin_afectados': [
        'UnFalloNoEsLimpio.test_ao3_un_error_http_en_querybatch',
        'UnFalloNoEsLimpio.test_ao3_un_error_http_al_bajar_un_aviso_no_deja_archivo',
        'UnFalloNoEsLimpio.test_ao3_una_conexion_cortada',
        'UnFalloNoEsLimpio.test_ao3_una_respuesta_que_no_es_json',
        'UnFalloNoEsLimpio.test_ao3_una_respuesta_demasiado_grande',
        'UnFalloNoEsLimpio.test_ao3_una_respuesta_que_no_es_utf8',
        'UnFalloNoEsLimpio.test_ao3_querybatch_con_otra_cantidad_de_resultados',
        'UnFalloNoEsLimpio.test_ao3_querybatch_con_avisos_sin_identificador',
        'UnFalloNoEsLimpio.test_ao3_un_aviso_que_no_es_osv_valido',
        'UnFalloNoEsLimpio.test_ao3_el_servicio_no_esta',
        'UnFalloNoEsLimpio.test_ao3_una_url_que_no_es_http_se_rechaza_sin_leer_archivos',
        'UnFalloNoEsLimpio.test_ao3_inventarios_sin_dependencias_no_se_dan_por_limpios_ni_se_conecta',
        'UnFalloNoEsLimpio.test_ao3_una_redireccion_no_se_sigue_hacia_otro_servidor',
        'UnFalloNoEsLimpio.test_ao3_un_identificador_de_aviso_vacio_se_rechaza_sin_pedir_la_raiz',
        'UnFalloNoEsLimpio.test_ao3_un_archivo_de_avisos_de_solo_lectura_no_se_reemplaza',
        'UnFalloNoEsLimpio.test_ao3_una_salida_fuera_del_proyecto_se_rechaza_antes_de_conectar',
        'UnFalloNoEsLimpio.test_ao3_una_salida_dentro_del_proyecto_con_un_ancestro_enlazado_se_rechaza',
        'UnFalloNoEsLimpio.test_ao3_la_url_invalida_se_rechaza_antes_de_leer_los_inventarios',
        'UnFalloNoEsLimpio.test_ao3_si_no_se_puede_escribir_es_un_error_claro_y_no_queda_nada',
        'UnFalloNoEsLimpio.test_ao3_el_guardado_es_atomico_un_fallo_al_reemplazar_deja_lo_anterior_y_ningun_temporal',
        'UnFalloNoEsLimpio.test_ao3_sin_inventarios_guardados_no_hay_nada_que_consultar_ni_conexion',
        'UnFalloNoEsLimpio.test_ao3_un_fallo_no_toca_un_archivo_de_avisos_anterior',
        'UnFalloNoEsLimpio.test_ao3_no_se_escribe_a_traves_de_un_enlace_simbolico',
        'UnFalloNoEsLimpio.test_ao3_una_salida_que_es_una_carpeta_se_rechaza_antes_de_conectar'],
}
PREFIX = 'test_avisos_osv.'
LIMITES = ('Escenarios ao1–ao3 contra un servidor OSV de mentira en 127.0.0.1: ninguna prueba toca la red. No se comprueba el '
           'comportamiento de api.osv.dev real (formato de sus respuestas, límites, caídas); el formato sigue la documentación de querybatch y vulns.')


def fuentes():
    files = [ROOT / 'fabrica.py', ROOT / 'pyproject.toml', Path(__file__), *ROOT.glob('oracle_factory/*.py'),
             *ROOT.glob('tests/*.py'), ROOT / 'oracle_factory/osv.py', ROOT / 'docs/procedencia.md',
             *ROOT.glob('catalogos/factory_avisos_osv.*.oracle')]
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
    escribir(output / 'hechos.json', {'avisos_osv_caso': rows, 'avisos_osv_corrida': [{'completa': int(ok), 'casos': len(expected)}]})
    escribir(output / 'resultado.json', {'exitoso': ok, 'tests': result.testsRun, 'casos_contrato': len(expected),
             'casos_exactos_sin_omisiones_duplicados_ni_fallas': complete, 'fuentes_estables': stable, 'origen': origen,
             'versiones': {**versions, 'python': sys.version}, 'limites': LIMITES,
             'artefactos_sha256': {name: sha(output / name) for name in ('suite.txt', 'hechos.json', 'trazabilidad.json')}})
    print(f'Evidencia: {output}; {result.testsRun} pruebas, {len(expected)} casos de contrato; éxito: {ok}.')
    print(LIMITES)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
