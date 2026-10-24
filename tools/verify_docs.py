"""Evidencia del contrato de la documentación al día: escenarios dc1 (cuenta lo que Factory hace hoy) y dc2 (se comprueba
contra la CLI), y la comprobación corrida sobre el repositorio con nombre exacto, y la trazabilidad de esos mismos casos."""
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

CAMBIO = '20261023-005051-ufj-docs'
CONTRACTS = {
    'la_documentacion_cuenta_lo_que_factory_hace_hoy': ['Docs.test_dc1_alguien_llega_al_proyecto'],
    'la_documentacion_se_comprueba_contra_la_cli': ['Docs.test_dc2_un_comando_sin_documentar_otro_que_no_existe_y_otra_version'],
}
PREFIX = 'test_docs.'
LIMITES = ('Escenarios dc1–dc2 sobre los archivos del repositorio y sobre copias con un problema puesto a propósito; la '
           'comprobación mira que los comandos y las versiones existan, no que lo explicado esté bien explicado.')


def fuentes():
    files = [ROOT / 'fabrica.py', ROOT / 'pyproject.toml', Path(__file__), ROOT / 'tools/docs_al_dia.py', *ROOT.glob('oracle_factory/*.py'),
             *ROOT.glob('tests/*.py'), ROOT / 'tests/tablero_en_node.cjs', ROOT / 'README.md', *ROOT.glob('docs/**/*.md'), *ROOT.glob('site/*.html'), *ROOT.glob('editores/vscode/*.js'),
             *ROOT.glob('catalogos/factory_docs.*.oracle')]
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
    # La comprobación de la documentación corrida de verdad sobre el repositorio: cuántos problemas tiene hoy.
    sys.path.insert(0, str(ROOT / 'tools'))
    import docs_al_dia
    pendientes = docs_al_dia.problemas(ROOT)
    escribir(output / 'problemas.json', pendientes)
    escribir(output / 'hechos.json', {'docs_caso': rows, 'docs_corrida': [{'completa': int(ok), 'casos': len(expected)}],
                                      'docs_estado': [{'problemas': len(pendientes)}]})
    escribir(output / 'resultado.json', {'exitoso': ok, 'tests': result.testsRun, 'casos_contrato': len(expected),
             'casos_exactos_sin_omisiones_duplicados_ni_fallas': complete, 'fuentes_estables': stable, 'origen': origen,
             'versiones': {**versions, 'python': sys.version}, 'limites': LIMITES,
             'artefactos_sha256': {name: sha(output / name) for name in ('suite.txt', 'hechos.json', 'trazabilidad.json', 'problemas.json')}})
    print(f'Evidencia: {output}; {result.testsRun} pruebas, {len(expected)} casos de contrato; éxito: {ok}.')
    print(LIMITES)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
