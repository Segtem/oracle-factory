"""Evidencia del contrato del bloqueo de aprobar-spec que nombra la causa: escenarios bc1–bc3 con nombre exacto, y la trazabilidad de esos mismos casos."""
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

CAMBIO = '20261028-100820-5n7-causa'
CONTRACTS = {
    'el_bloqueo_de_aprobar_spec_nombra_la_linea': [
        'BloqueoCausa.test_bc1_una_plantilla_recien_creada_nombra_cada_archivo_pendiente_con_su_linea',
        'BloqueoCausa.test_bc1_un_solo_archivo_pendiente_nombra_solo_ese_y_no_dice_que_quedan_mas',
        'BloqueoCausa.test_bc1_una_linea_larga_se_corta_a_ochenta_caracteres',
        'BloqueoCausa.test_bc1_una_linea_de_exactamente_ochenta_caracteres_no_se_corta',
        'BloqueoCausa.test_bc1_cuenta_las_marcas_que_quedan_y_nombra_la_primera',
        'BloqueoCausa.test_bc1_el_texto_de_la_linea_va_sin_sangria',
        'BloqueoCausa.test_bc1_en_ingles_tambien',
        'BloqueoCausa.test_bc1_un_bloqueo_no_registra_ninguna_aprobacion',
        'BloqueoCausa.test_bc1_una_plantilla_recien_creada_sin_tocar_nombra_los_archivos_que_la_tienen',
        'BloqueoCausa.test_bc1_con_exactamente_dos_marcas_dice_queda_uno',
        'BloqueoCausa.test_bc1_un_enlace_simbolico_fuera_del_proyecto_se_rechaza_sin_leerlo',
        'BloqueoCausa.test_bc1_un_enlace_simbolico_roto_tambien_se_rechaza',
        'BloqueoCausa.test_bc1_un_archivo_que_no_es_utf8_da_un_error_claro_y_no_un_traceback',
        'BloqueoCausa.test_bc1_una_ruta_fuera_del_proyecto_es_un_error_de_factory_y_no_un_valueerror'],
    'el_bloqueo_de_aprobar_spec_dice_si_falta_un_archivo': [
        'BloqueoCausa.test_bc2_si_falta_un_archivo_el_mensaje_dice_que_falta',
        'BloqueoCausa.test_bc2_si_faltan_varios_archivos_los_nombra_a_todos_en_plural',
        'BloqueoCausa.test_bc2_con_pendientes_y_un_archivo_que_falta_dice_las_dos_cosas'],
    'aprobar_spec_no_cambia_cuando_todo_esta_completo': [
        'BloqueoCausa.test_bc3_con_los_tres_archivos_completos_se_aprueba_como_siempre'],
}
PREFIX = 'test_bloqueo_causa.'
LIMITES = ('Escenarios bc1–bc3 en proyectos temporales con git, Linux. Sólo cubre el bloqueo de aprobar-spec por la marca de pendiente de la '
           'plantilla o por un archivo que falta; los demás mensajes de bloqueo de Factory no cambian.')


def fuentes():
    files = [ROOT / 'fabrica.py', ROOT / 'pyproject.toml', Path(__file__), *ROOT.glob('oracle_factory/*.py'),
             *ROOT.glob('tests/*.py'),
             *ROOT.glob('catalogos/factory_bloqueo_causa.*.oracle')]
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
    escribir(output / 'hechos.json', {'bloqueo_causa_caso': rows, 'bloqueo_causa_corrida': [{'completa': int(ok), 'casos': len(expected)}]})
    escribir(output / 'resultado.json', {'exitoso': ok, 'tests': result.testsRun, 'casos_contrato': len(expected),
             'casos_exactos_sin_omisiones_duplicados_ni_fallas': complete, 'fuentes_estables': stable, 'origen': origen,
             'versiones': {**versions, 'python': sys.version}, 'limites': LIMITES,
             'artefactos_sha256': {name: sha(output / name) for name in ('suite.txt', 'hechos.json', 'trazabilidad.json')}})
    print(f'Evidencia: {output}; {result.testsRun} pruebas, {len(expected)} casos de contrato; éxito: {ok}.')
    print(LIMITES)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
