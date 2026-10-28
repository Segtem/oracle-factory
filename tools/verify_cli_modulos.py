"""Evidencia del contrato de partir cli.py en módulos: escenarios cm1–cm3 con nombre exacto, y la trazabilidad de esos mismos casos."""
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

CAMBIO = '20261028-222656-b2m-clidividido'
CONTRACTS = {
    'la_cli_se_comporta_igual_tras_partirse': [
        'CliModulos.test_cm1_todos_los_nombres_y_firmas_de_antes_siguen_en_cli',
        'CliModulos.test_cm1_la_ayuda_de_oracle_factory_y_de_cada_subcomando_es_identica',
        'CliModulos.test_cm1_lo_movido_es_el_mismo_objeto_en_cli_y_en_su_modulo',
        'CliModulos.test_cm1_lo_movido_ya_no_se_define_en_cli',
        'CliModulos.test_cm1_dos_modulos_nuevos_no_definen_el_mismo_nombre',
        'CliModulos.test_cm1_cli_sigue_siendo_la_entrada_del_comando'],
    'lo_movido_lee_a_cli_en_el_momento_de_usarlo': [
        'CliModulos.test_cm2_un_valor_de_cli_cambiado_vale_para_lo_movido',
        'CliModulos.test_cm2_una_funcion_cambiada_en_cli_la_usa_lo_movido',
        'CliModulos.test_cm2_exclusiones_del_paquete_usa_ejecutar_y_es_producto_de_cli',
        'CliModulos.test_cm2_ninguna_funcion_movida_usa_un_nombre_de_cli_como_propio',
        'CliModulos.test_cm2_ninguna_funcion_movida_usa_un_nombre_que_no_existe',
        'CliModulos.test_cm2_los_modulos_nuevos_importan_a_cli_entero_y_no_sus_nombres',
        'CliModulos.test_cm2_se_puede_importar_primero_cualquiera_de_los_modulos',
        'CliModulos.test_cm2_el_import_de_cli_va_al_final_de_cada_modulo_que_lo_usa',
        'CliModulos.test_cm2_ningun_modulo_nuevo_se_pasa_al_kb_en_lugar_de_cli'],
    'ningun_archivo_fuente_pasa_del_tope': [
        'CliModulos.test_cm3_cli_py_y_los_demas_archivos_estan_bajo_sus_topes',
        'CliModulos.test_cm3_un_archivo_que_crece_de_mas_se_nombra_con_su_tamano_y_el_limite_de_clue',
        'CliModulos.test_cm3_justo_bajo_el_tope_no_es_un_problema'],
}
PREFIX = 'test_cli_modulos.'
LIMITES = ('Escenarios cm1–cm3 sobre el código partido, en Linux. Los nombres, las firmas y la ayuda se comparan con lo tomado de cli.py antes de '
           'moverlo (tests/datos/nombres-cli.json y ayuda-cli.json); que lo movido lea a cli al usarlo se comprueba con parches y con un análisis '
           'del árbol sintáctico, no con una prueba de cada función. No se prueba el tope real de Oracle Clue, sólo los topes propios de 160000 y 200000.')


def fuentes():
    files = [ROOT / 'fabrica.py', ROOT / 'pyproject.toml', Path(__file__), *ROOT.glob('oracle_factory/*.py'),
             *ROOT.glob('tests/*.py'), ROOT / 'tests/datos/nombres-cli.json', ROOT / 'tests/datos/ayuda-cli.json', ROOT / 'tools/tamanos.py',
             *ROOT.glob('catalogos/factory_cli_modulos.*.oracle')]
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
    escribir(output / 'hechos.json', {'cli_modulos_caso': rows, 'cli_modulos_corrida': [{'completa': int(ok), 'casos': len(expected)}]})
    escribir(output / 'resultado.json', {'exitoso': ok, 'tests': result.testsRun, 'casos_contrato': len(expected),
             'casos_exactos_sin_omisiones_duplicados_ni_fallas': complete, 'fuentes_estables': stable, 'origen': origen,
             'versiones': {**versions, 'python': sys.version}, 'limites': LIMITES,
             'artefactos_sha256': {name: sha(output / name) for name in ('suite.txt', 'hechos.json', 'trazabilidad.json')}})
    print(f'Evidencia: {output}; {result.testsRun} pruebas, {len(expected)} casos de contrato; éxito: {ok}.')
    print(LIMITES)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
