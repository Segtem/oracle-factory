"""Evidencia del contrato del idioma de las plantillas: escenarios id1–id3 con nombre exacto, y la trazabilidad de esos mismos casos."""
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

CAMBIO = '20261027-220102-yjy-idioma'
CONTRACTS = {
    'idioma_de_la_plantilla': [
        'Idioma.test_id1_sin_idioma_declarado_sale_en_espanol',
        'Idioma.test_id1_el_proyecto_declara_ingles',
        'Idioma.test_id1_el_cambio_elige_otro_idioma_y_el_proyecto_no_cambia',
        'Idioma.test_id1_lo_que_exige_el_formato_no_se_traduce',
        'Idioma.test_id1_el_ejemplo_notas_no_depende_del_idioma'],
    'idioma_no_admitido': [
        'Idioma.test_id2_un_idioma_desconocido_en_la_configuracion',
        'Idioma.test_id2_un_idioma_desconocido_en_la_linea_de_comandos_no_crea_nada',
        'Idioma.test_id2_por_la_cli_de_verdad'],
    'la_plantilla_en_cualquier_idioma_se_aprueba_e_importa': [
        'Idioma.test_id3_una_spec_completa_se_aprueba_y_se_importa_en_cada_idioma',
        'Idioma.test_id3_una_plantilla_sin_completar_no_se_aprueba'],
}
PREFIX = 'test_idioma.'
LIMITES = ('Escenarios id1–id3 en proyectos temporales con git, Linux, con Oracle real para importar. Sólo hay dos idiomas; no se traducen la CLI, '
           'la documentación ni el tablero, y no hay una configuración global del usuario.')


def fuentes():
    files = [ROOT / 'fabrica.py', ROOT / 'pyproject.toml', Path(__file__), *ROOT.glob('oracle_factory/*.py'),
             *ROOT.glob('tests/*.py'), ROOT / 'tests/tablero_en_node.cjs', *ROOT.glob('editores/vscode/*.js'),
             *ROOT.glob('catalogos/factory_idioma.*.oracle')]
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
    escribir(output / 'hechos.json', {'idioma_caso': rows, 'idioma_corrida': [{'completa': int(ok), 'casos': len(expected)}]})
    escribir(output / 'resultado.json', {'exitoso': ok, 'tests': result.testsRun, 'casos_contrato': len(expected),
             'casos_exactos_sin_omisiones_duplicados_ni_fallas': complete, 'fuentes_estables': stable, 'origen': origen,
             'versiones': {**versions, 'python': sys.version}, 'limites': LIMITES,
             'artefactos_sha256': {name: sha(output / name) for name in ('suite.txt', 'hechos.json', 'trazabilidad.json')}})
    print(f'Evidencia: {output}; {result.testsRun} pruebas, {len(expected)} casos de contrato; éxito: {ok}.')
    print(LIMITES)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
