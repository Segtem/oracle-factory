"""Evidencia del contrato de revision-simultanea: escenarios rs1–rs2 con nombre exacto, y la trazabilidad de esos mismos casos."""
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

CAMBIO = '20261014-100834-revision-simultanea'
CONTRACTS = {
    'pedidos_de_revision_simultaneos_sobre_el_mismo_candidato': ['rs1_dos_revisores_distintos_a_la_vez',
                                                                 'rs1_el_mismo_revisor_dos_veces_a_la_vez'],
    'un_pedido_interrumpido_no_traba_los_siguientes': ['rs2_un_bloqueo_de_un_pedido_que_murio'],
}
PREFIX = 'test_revision_simultanea.RevisionSimultanea.test_'
LIMITES = ('Escenarios rs1–rs2 en repositorios temporales, Linux, con revisores de prueba y oracle-clue 0.1.0a2 real; '
           'los pedidos simultáneos son hilos de un mismo proceso que arrancan juntos, y el pedido muerto es un proceso '
           'terminado con SIGKILL. Una carrera puede no darse en una corrida: las pruebas la provocan, no la garantizan.')


def fuentes():
    files = [ROOT / 'fabrica.py', ROOT / 'pyproject.toml', Path(__file__), *ROOT.glob('oracle_factory/*.py'),
             *ROOT.glob('tests/*.py'), *ROOT.glob('catalogos/factory_simultanea.*.oracle')]
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
    observed = {name: count for name, count in result.cantidad.items() if name.startswith(PREFIX)}
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
    escribir(output / 'hechos.json', {'simultanea_caso': rows, 'simultanea_corrida': [{'completa': int(ok), 'casos': len(expected)}]})
    escribir(output / 'resultado.json', {'exitoso': ok, 'tests': result.testsRun, 'casos_contrato': len(expected),
             'casos_exactos_sin_omisiones_duplicados_ni_fallas': complete, 'fuentes_estables': stable, 'origen': origen,
             'versiones': {**versions, 'python': sys.version}, 'limites': LIMITES,
             'artefactos_sha256': {name: sha(output / name) for name in ('suite.txt', 'hechos.json', 'trazabilidad.json')}})
    print(f'Evidencia: {output}; {result.testsRun} pruebas, {len(expected)} casos de contrato; éxito: {ok}.')
    print(LIMITES)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
