"""Evidencia del contrato de los textos de la 0.1.0a15 publicada: escenarios pa1–pa2 con nombre exacto, y la trazabilidad de esos mismos casos."""
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

CAMBIO = '20261028-143519-qhd-publicadaa15'
CONTRACTS = {
    'los_textos_declaran_publicada_la_version_publicada': [
        'PublicadaA15.test_pa1_las_notas_declaran_la_version_publicada_con_su_tag_y_su_release',
        'PublicadaA15.test_pa1_ningun_texto_llama_candidata_a_la_version_publicada',
        'PublicadaA15.test_pa1_el_readme_y_la_guia_dicen_que_esta_publicada',
        'PublicadaA15.test_pa1_la_historia_anterior_se_conserva'],
    'un_texto_en_preparacion_de_una_version_publicada_se_detecta': [
        'PublicadaA15.test_pa2_un_texto_candidata_con_las_notas_publicadas_se_detecta',
        'PublicadaA15.test_pa2_una_version_en_preparacion_no_es_divergencia',
        'PublicadaA15.test_pa2_sin_notas_la_regla_no_inventa_divergencias',
        'PublicadaA15.test_pa2_otra_version_con_la_palabra_candidato_no_cuenta'],
}
PREFIX = 'test_publicada_a15.'
LIMITES = ('Escenarios pa1–pa2 sobre los textos del repositorio (notas, README, documentación y web) y sobre copias temporales para los casos '
           'negativos, en Linux. El estado «publicada» de la 0.1.0a15 se comprobó contra PyPI aparte (mismos SHA-256 del wheel y del sdist); estas '
           'pruebas no consultan la red.')


def fuentes():
    files = [ROOT / 'fabrica.py', ROOT / 'pyproject.toml', Path(__file__), *ROOT.glob('oracle_factory/*.py'),
             *ROOT.glob('tests/*.py'), ROOT / 'tests/datos/guias-texto.json', ROOT / 'NOTAS-DE-RELEASE.md', ROOT / 'README.md', ROOT / 'tools/docs_al_dia.py',
             *ROOT.glob('docs/*.md'), *ROOT.glob('site/*.html'),
             *ROOT.glob('catalogos/factory_publicada_a15.*.oracle')]
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
    escribir(output / 'hechos.json', {'publicada_a15_caso': rows, 'publicada_a15_corrida': [{'completa': int(ok), 'casos': len(expected)}]})
    escribir(output / 'resultado.json', {'exitoso': ok, 'tests': result.testsRun, 'casos_contrato': len(expected),
             'casos_exactos_sin_omisiones_duplicados_ni_fallas': complete, 'fuentes_estables': stable, 'origen': origen,
             'versiones': {**versions, 'python': sys.version}, 'limites': LIMITES,
             'artefactos_sha256': {name: sha(output / name) for name in ('suite.txt', 'hechos.json', 'trazabilidad.json')}})
    print(f'Evidencia: {output}; {result.testsRun} pruebas, {len(expected)} casos de contrato; éxito: {ok}.')
    print(LIMITES)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
