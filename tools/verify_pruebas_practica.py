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
        'Pruebas.test_pp2_una_carpeta_de_evidencia_enlazada_no_se_sigue',
        'Pruebas.test_pp2_un_cambio_abandonado_no_avisa',
        'Pruebas.test_pp2_un_candidato_con_forma_rara_no_arma_rutas',
        'Pruebas.test_pp2_una_trazabilidad_que_no_se_puede_leer_cuenta_como_sin_trazabilidad',
        'Pruebas.test_pp2_un_identificador_con_forma_rara_no_arma_rutas',
        'Pruebas.test_pp2_un_candidato_demasiado_corto_o_largo_no_arma_rutas',
        'Analisis.test_el_analisis_de_requisitos_con_y_sin_casos',
        'Analisis.test_un_caso_de_solo_espacios_no_cuenta_como_caso',
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
        'Pruebas.test_pp3_sin_excepciones_la_spec_se_lee_como_siempre',
        'Pruebas.test_pp3_una_excepcion_mal_escrita_se_avisa_aunque_todavia_no_haya_candidato',
        'Pruebas.test_pp3_una_linea_mala_no_borra_las_excepciones_buenas_de_los_otros_requisitos',
        'Pruebas.test_pp3_lo_escrito_en_la_spec_despues_de_aprobarla_no_cuenta_como_aceptado',
        'Pruebas.test_pp3_una_spec_sin_excepciones_cambiada_despues_de_aprobarla_no_avisa_de_excepciones',
        'Pruebas.test_pp3_la_spec_que_es_un_enlace_simbolico_no_se_sigue',
        'Pruebas.test_pp3_una_spec_que_falta_se_avisa_y_no_rompe_el_estado',
        'Pruebas.test_pp3_valores_raros_en_el_registro_no_rompen_el_estado',
        'Pruebas.test_pp3_un_motivo_hecho_de_guiones_no_es_un_motivo',
        'Pruebas.test_pp3_declarar_dos_veces_pruebas_en_un_requisito_se_rechaza',
        'Pruebas.test_pp3_el_ejemplo_dentro_de_un_bloque_de_codigo_no_cuenta',
        'Pruebas.test_pp3_un_bloque_de_codigo_con_sangria_tambien_se_ignora',
        'Pruebas.test_pp3_la_viñeta_con_asterisco_y_con_guion_se_leen_igual',
        'Pruebas.test_pp3_una_seccion_modified_tambien_puede_declarar_la_excepcion',
        'Pruebas.test_pp3_el_motivo_conserva_su_texto_con_guiones_y_espacios_internos',
        'Pruebas.test_pp3_la_ruta_de_la_spec_no_puede_salir_del_proyecto',
        'Pruebas.test_pp3_una_aprobacion_invalidada_no_deja_vigentes_las_excepciones',
        'Pruebas.test_pp3_una_excepcion_valida_se_muestra_aunque_todavia_no_haya_candidato',
        'Pruebas.test_pp3_una_excepcion_mal_escrita_se_avisa_antes_de_importar',
        'Pruebas.test_pp3_un_requisito_con_varias_lineas_pruebas_queda_sin_excepcion',
        'Pruebas.test_pp3_un_numeral_en_la_descripcion_no_cierra_la_cabecera_del_requisito',
        'Pruebas.test_pp3_el_reconocimiento_ignora_mayusculas_sangria_y_raya_mediana',
        'Pruebas.test_pp3_las_excepciones_se_muestran_ordenadas',
        'Pruebas.test_pp3_un_registro_sin_la_clave_spec_se_avisa_y_no_rompe',
        'Pruebas.test_pp3_un_registro_con_spec_aprobada_rara_no_rompe_el_estado',
        'Pruebas.test_pp3_cambiar_la_propuesta_despues_de_aprobar_deja_sin_vigencia_las_excepciones',
        'Pruebas.test_pp3_sin_documentos_para_comparar_las_excepciones_no_cuentan',
        'Pruebas.test_pp3_la_ausencia_de_documentos_en_los_dos_lados_no_cuenta_como_aprobacion',
        'Pruebas.test_pp3_una_spec_que_todavia_no_se_aprobo_lo_dice_sin_decir_que_cambio',
        'Pruebas.test_pp3_las_excepciones_aprobadas_se_ven_antes_de_importar_por_el_nombre_del_requisito',
        'Pruebas.test_pp3_un_motivo_que_empieza_con_guiones_conserva_su_texto',
        'Pruebas.test_pp3_las_secciones_delta_se_leen_en_cualquier_mayuscula_y_renamed_no_retira',
        'Pruebas.test_pp3_el_primer_error_es_el_que_se_informa'],
}
PREFIX = 'test_pruebas_practica.'
LIMITES = ('Escenarios pp1–pp3 sobre proyectos temporales, con la trazabilidad que dejaría el sensor escrita a mano y el candidato vigente '
           'simulado. No se comprueba un sensor real que genere trazabilidad.json, ni qué tan buenas son las pruebas de un cambio: sólo que '
           'el estado avisa de las que faltan.')


def fuentes(salida=None):
    # Todo lo versionado o nuevo del producto (código, pruebas, datos de referencia, catálogos, docs); sin los registros generados.
    nombres = subprocess.run(['git', '-C', str(ROOT), 'ls-files', '-z', '--cached', '--others', '--exclude-standard'],
                             text=True, capture_output=True, check=True).stdout.split('\0')  # -z: nombres no ASCII sin comillas
    elegidos = [ROOT / n for n in nombres if n and not n.startswith(('.factory/', 'kb/', 'tareas/', 'openspec/changes/'))
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
