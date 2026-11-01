"""Evidencia de la puerta local de salida: escenarios pu1–pu4 con nombre exacto, y la trazabilidad de esos casos."""
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

CAMBIO = '20261101-121356-ih8-puertalocal'
CONTRACTS = {
    'la_puerta_detecta_secretos_en_todos_los_commits_que_se_publican': [
        'Detectar.test_pu1_cada_tipo_de_credencial_se_nombra_con_archivo_linea_y_commit',
        'Detectar.test_pu1_el_valor_sale_tapado_y_nunca_entero',
        'Detectar.test_pu1_un_token_de_otro_tipo_de_anthropic_tambien',
        'Detectar.test_pu1_las_palabras_no_son_secretos',
        'Detectar.test_pu1_la_marca_de_exencion_salva_solo_esa_linea',
        'Detectar.test_pu1_solo_cuentan_las_lineas_agregadas_y_los_numeros_siguen_los_hunks',
        'Detectar.test_pu1_cada_commit_se_atribuye_al_suyo_y_cada_archivo_al_suyo',
        'Detectar.test_pu1_dos_archivos_en_el_mismo_commit_se_atribuyen_cada_uno_al_suyo',
        'Detectar.test_pu1_una_cabecera_con_guiones_no_se_lee_como_linea_agregada',
        'Detectar.test_pu1_un_archivo_borrado_o_binario_no_rompe',
        'Detectar.test_pu1_una_linea_enorme_se_mira_pero_no_cuelga',
        'Detectar.test_pu1_el_documento_nombra_cada_tipo_de_credencial_el_codigo_de_salida_y_la_marca',
        'Detectar.test_pu1_el_contrato_del_verificador_nombra_exactamente_los_casos_que_existen',
        'Detectar.test_pu1_el_texto_nombra_cada_hallazgo'],
    'la_puerta_corre_las_verificaciones_del_proyecto': [
        'Verificaciones.test_pu2_las_tres_verificaciones_pasan',
        'Verificaciones.test_pu2_una_que_falla_se_nombra_y_las_demas_se_corren_igual',
        'Verificaciones.test_pu2_un_kb_o_un_resumen_vencidos_avisan_y_no_bloquean',
        'Verificaciones.test_pu2_la_guia_vieja_bloquea_y_las_otras_se_informan_como_aviso',
        'Verificaciones.test_pu2_la_verificacion_pide_siempre_verificar_y_no_escribe',
        'Verificaciones.test_pu2_una_verificacion_cuyo_archivo_no_existe_se_omite_y_no_bloquea',
        'Verificaciones.test_pu2_la_puerta_con_un_kb_vencido_pasa_y_lo_dice_sin_decir_que_esta_al_dia',
        'Verificaciones.test_pu2_con_todas_omitidas_la_puerta_dice_que_ninguna_aplica_y_pasa',
        'Verificaciones.test_pu2_la_puerta_junta_secretos_y_verificaciones_en_un_resultado',
        'Verificaciones.test_pu2_si_git_falla_al_leer_los_commits_la_puerta_no_dice_que_esta_limpio'],
    'el_hook_pre_push_llama_a_la_puerta_con_lo_que_se_empuja': [
        'Rangos.test_pu3_una_rama_nueva_mira_lo_que_ningun_remoto_tiene',
        'Rangos.test_pu3_una_rama_existente_mira_desde_el_sha_remoto',
        'Rangos.test_pu3_borrar_una_rama_remota_no_se_mira',
        'Rangos.test_pu3_un_sha_remoto_que_no_tenemos_cae_al_modo_de_rama_nueva',
        'Rangos.test_pu3_varias_ramas_en_un_push_dan_un_rango_cada_una_y_las_lineas_raras_se_ignoran',
        'HookReal.test_pu3_hooks_instala_el_pre_push_y_lo_dice',
        'HookReal.test_pu3_un_push_limpio_pasa',
        'HookReal.test_pu3_un_push_con_un_secreto_se_bloquea_y_lo_nombra_sin_mostrarlo',
        'HookReal.test_pu3_un_secreto_quitado_en_el_commit_siguiente_igual_bloquea',
        'HookReal.test_pu3_solo_se_miran_los_commits_que_el_remoto_todavia_no_tiene',
        'HookReal.test_pu3_una_rama_nueva_se_mira_desde_lo_que_el_remoto_no_tiene',
        'HookReal.test_pu3_borrar_una_rama_remota_pasa_aunque_tuviera_un_secreto',
        'HookReal.test_pu3_una_puerta_que_no_puede_mirar_sale_con_el_codigo_2_y_nunca_con_el_de_bloqueo',
        'HookReal.test_pu3_la_puerta_a_mano_sin_argumentos_mira_lo_que_el_remoto_no_tiene',
        'HookReal.test_pu3_no_verify_saltea_la_puerta',
        'HookReal.test_pu3_la_exencion_de_una_linea_deja_pasar',
        'HookReal.test_pu3_un_hook_ajeno_no_se_pisa',
        'HookReal.test_pu3_instalar_dos_veces_no_duplica_ni_rompe',
        'HookReal.test_pu3_con_el_interprete_borrado_el_push_pasa_con_un_aviso',
        'HookReal.test_pu3_si_la_puerta_se_rompe_por_dentro_el_push_pasa_con_un_aviso',
        'HookReal.test_pu3_un_kb_vencido_no_frena_el_push_pero_se_avisa_y_no_se_toca',
        'HookReal.test_pu3_un_proyecto_que_todavia_no_genero_su_kb_ni_su_resumen_puede_empujar',
        'HookReal.test_pu3_las_verificaciones_viejas_bloquean_el_push'],
    'la_puerta_no_modifica_el_arbol_de_trabajo': [
        'HookReal.test_pu4_correr_la_puerta_con_el_kb_vencido_no_cambia_nada',
        'HookReal.test_pu4_verificar_la_guia_tampoco_regenera_el_kb',
        'HookReal.test_pu4_un_push_con_el_kb_vencido_deja_el_arbol_como_estaba',
        'HookReal.test_pu4_agentes_sin_verificar_sigue_escribiendo_la_guia_pero_no_el_kb'],
}
PREFIX = 'test_puerta.'
LIMITES = ('Escenarios pu1–pu4 con Git de verdad (un remoto local temporal y el hook instalado), un ejecutor falso para los casos de error y secretos armados '
           'al vuelo, en Linux. Comprueban lo que la puerta detecta, bloquea y deja pasar, y que no modifica el árbol; no son un escáner completo '
           '(no miden entropía ni formatos que la lista no incluye) y no corren analizadores estáticos.')


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
    escribir(output / 'hechos.json', {'puerta_local_caso': rows, 'puerta_local_corrida': [{'completa': int(ok), 'casos': len(expected)}]})
    escribir(output / 'resultado.json', {'exitoso': ok, 'tests': result.testsRun, 'casos_contrato': len(expected),
             'casos_exactos_sin_omisiones_duplicados_ni_fallas': complete, 'fuentes_estables': stable, 'origen': origen,
             'versiones': {**versions, 'python': sys.version}, 'limites': LIMITES,
             'artefactos_sha256': {name: sha(output / name) for name in ('suite.txt', 'hechos.json', 'trazabilidad.json')}})
    print(f'Evidencia: {output}; {result.testsRun} pruebas, {len(expected)} casos de contrato; éxito: {ok}.')
    print(LIMITES)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
