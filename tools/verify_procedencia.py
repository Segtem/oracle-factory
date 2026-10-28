"""Evidencia del contrato de la procedencia de las dependencias: escenarios pr1–pr5 con nombre exacto, y la trazabilidad de esos mismos casos."""
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

CAMBIO = '20261028-150627-lva-procedencia'
CONTRACTS = {
    'el_inventario_dice_que_hay_y_de_donde_viene': [
        'Procedencia.test_pr1_un_proyecto_con_lock_lista_cada_componente_con_su_origen_y_sus_hashes',
        'Procedencia.test_pr1_una_dependencia_que_no_es_directa_lo_dice',
        'Procedencia.test_pr1_un_proyecto_sin_lock_usa_lo_instalado_y_lo_dice',
        'Procedencia.test_pr1_sin_lock_ni_entorno_no_hay_componentes_y_se_dice',
        'Procedencia.test_pr1_una_version_corregida_por_lightwell_se_reconoce',
        'Procedencia.test_pr1_el_nombre_se_normaliza_en_el_enlace',
        'Procedencia.test_pr1_dos_corridas_iguales_dan_el_mismo_inventario_sin_marcas_de_tiempo',
        'Procedencia.test_pr1_el_entorno_no_consultado_se_declara',
        'Procedencia.test_pr1_un_lock_ilegible_es_un_error_claro',
        'Procedencia.test_pr1_un_lock_enlazado_no_se_lee',
        'Procedencia.test_pr1_la_raiz_virtual_de_un_lock_no_es_un_componente',
        'Procedencia.test_pr1_los_hashes_salen_ordenados_aunque_el_lock_los_traiga_desordenados',
        'Procedencia.test_pr1_un_paquete_en_dos_versiones_del_lock_aparece_dos_veces',
        'Procedencia.test_pr1_si_la_instalada_no_es_ninguna_de_las_del_lock_se_dice',
        'Procedencia.test_pr1_un_entorno_que_falla_no_se_toma_por_vacio',
        'Procedencia.test_pr1_un_entorno_que_responde_cualquier_cosa_no_se_toma_por_valido',
        'Procedencia.test_pr1_un_python_que_no_existe_no_rompe',
        'Procedencia.test_pr1_sin_indicar_python_se_usa_el_venv_del_proyecto'],
    'un_lock_desactualizado_se_declara_no_confiable': [
        'Procedencia.test_pr2_todo_coincide_es_confiable_y_sin_diferencias',
        'Procedencia.test_pr2_el_lock_difiere_de_lo_que_exige_el_proyecto',
        'Procedencia.test_pr2_el_lock_difiere_de_lo_instalado',
        'Procedencia.test_pr2_algo_del_lock_que_no_esta_instalado',
        'Procedencia.test_pr2_una_dependencia_directa_que_falta_en_el_lock',
        'Procedencia.test_pr2_un_lock_de_otra_version_del_proyecto',
        'Procedencia.test_pr2_una_especificacion_no_fijada_no_es_una_diferencia',
        'Procedencia.test_pr2_los_extras_y_marcadores_de_una_dependencia_no_confunden',
        'Procedencia.test_pr2_el_nombre_se_compara_normalizado'],
    'el_inventario_queda_en_el_candidato': [
        'Procedencia.test_pr3_con_un_cambio_el_inventario_queda_en_su_candidato_y_en_el_registro',
        'Procedencia.test_pr3_un_candidato_nuevo_no_pisa_el_inventario_del_anterior',
        'Procedencia.test_pr3_el_mismo_candidato_se_regraba_con_el_mismo_contenido',
        'Procedencia.test_pr3_con_json_imprime_exactamente_lo_que_guarda',
        'Procedencia.test_pr3_sin_un_cambio_no_se_guarda_nada',
        'Procedencia.test_pr3_un_cambio_inexistente_o_cerrado_se_rechaza_sin_escribir',
        'Procedencia.test_pr3_un_commit_que_no_cambia_el_producto_no_abre_otro_candidato',
        'Procedencia.test_pr3_un_cambio_cerrado_se_rechaza_sin_escribir',
        'Procedencia.test_pr3_una_carpeta_enlazada_no_deja_escribir_afuera',
        'Procedencia.test_pr3_una_carpeta_enlazada_a_ninguna_parte_da_un_error_claro'],
    'se_busca_quien_uso_una_dependencia': [
        'Procedencia.test_pr4_un_paquete_y_una_version_lista_solo_a_quien_la_uso',
        'Procedencia.test_pr4_sin_version_lista_a_todos_los_que_lo_usaron',
        'Procedencia.test_pr4_un_paquete_que_nadie_uso_lo_dice',
        'Procedencia.test_pr4_una_version_es_exacta_y_no_un_prefijo',
        'Procedencia.test_pr4_el_nombre_se_busca_normalizado',
        'Procedencia.test_pr4_la_busqueda_en_json_y_sin_inventarios',
        'Procedencia.test_pr4_sin_inventarios_guardados_no_inventa_nada',
        'Procedencia.test_pr4_un_pedido_vacio_y_las_combinaciones_invalidas_se_rechazan',
        'Procedencia.test_pr4_un_inventario_ilegible_se_avisa_y_no_traba_la_busqueda',
        'Procedencia.test_pr4_un_inventario_enlazado_no_se_lee'],
    'se_audita_contra_avisos_sin_red': [
        'Procedencia.test_pr5_un_aviso_por_version_exacta_afecta_al_candidato_que_la_uso',
        'Procedencia.test_pr5_un_rango_afecta_antes_de_la_correccion_y_no_desde_ella',
        'Procedencia.test_pr5_los_rangos_semver_valen_y_los_git_se_ignoran',
        'Procedencia.test_pr5_last_affected_y_varios_tramos',
        'Procedencia.test_pr5_un_evento_introduced_cero_cubre_desde_el_principio',
        'Procedencia.test_pr5_una_prerrelease_de_la_version_corregida_sigue_afectada',
        'Procedencia.test_pr5_un_aviso_que_ningun_candidato_uso_no_afecta',
        'Procedencia.test_pr5_otro_ecosistema_no_cuenta_y_el_nombre_se_compara_normalizado',
        'Procedencia.test_pr5_los_tres_formatos_de_archivo_se_aceptan',
        'Procedencia.test_pr5_una_version_corregida_por_lightwell_se_lista_aparte',
        'Procedencia.test_pr5_una_version_que_no_se_puede_comparar_se_dice_y_no_se_da_por_limpia',
        'Procedencia.test_pr5_la_salida_en_json_y_el_orden_son_estables',
        'Procedencia.test_pr5_un_archivo_de_avisos_invalido_falla_diciendo_que_esta_mal',
        'Procedencia.test_pr5_un_archivo_que_no_existe_o_enlazado_se_rechaza',
        'Procedencia.test_pr5_la_auditoria_no_usa_la_red',
        'Procedencia.test_las_versiones_se_ordenan_al_estilo_pep_440'],
}
PREFIX = 'test_procedencia.'
LIMITES = ('Escenarios pr1–pr5 en proyectos temporales con git, Linux, con un «python» de mentira que informa lo instalado y sin red (una '
           'prueba corta la apertura de sockets). El formato de los avisos OSV y de los inventarios CycloneDX se comprueba contra los '
           'campos que Factory usa, no contra el esquema completo; no hay firmas ni consulta a servicios de avisos.')


def fuentes():
    files = [ROOT / 'fabrica.py', ROOT / 'pyproject.toml', Path(__file__), *ROOT.glob('oracle_factory/*.py'),
             *ROOT.glob('tests/*.py'), ROOT / 'README.md', ROOT / 'docs/procedencia.md',
             *ROOT.glob('catalogos/factory_procedencia.*.oracle')]
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
    escribir(output / 'hechos.json', {'procedencia_caso': rows, 'procedencia_corrida': [{'completa': int(ok), 'casos': len(expected)}]})
    escribir(output / 'resultado.json', {'exitoso': ok, 'tests': result.testsRun, 'casos_contrato': len(expected),
             'casos_exactos_sin_omisiones_duplicados_ni_fallas': complete, 'fuentes_estables': stable, 'origen': origen,
             'versiones': {**versions, 'python': sys.version}, 'limites': LIMITES,
             'artefactos_sha256': {name: sha(output / name) for name in ('suite.txt', 'hechos.json', 'trazabilidad.json')}})
    print(f'Evidencia: {output}; {result.testsRun} pruebas, {len(expected)} casos de contrato; éxito: {ok}.')
    print(LIMITES)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
