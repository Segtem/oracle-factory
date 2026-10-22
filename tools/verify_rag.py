"""Evidencia del contrato de preguntar al conocimiento: escenarios rag1–rag5 y la evaluación del RAG de Factory con sus
preguntas de oro (necesita Ollama con qwen3-embedding:0.6b) con nombre exacto, y la trazabilidad de esos mismos casos."""
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
from oracle_factory import cli, trazabilidad  # noqa: E402
import contextlib  # noqa: E402
import json  # noqa: E402

CAMBIO = '20261021-235127-fjn-rag'
CONTRACTS = {
    'preguntar_devuelve_pasajes_vigentes_con_su_cita': ['Rag.test_rag1_una_pregunta_sobre_una_decision'],
    'la_busqueda_es_hibrida_y_dice_que_uso': ['Rag.test_rag2_una_pregunta_con_otras_palabras'],
    'los_embeddings_son_configurables_y_locales_por_defecto': ['Rag.test_rag3_sin_configuracion_y_con_un_proveedor_externo'],
    'el_indice_se_mantiene_solo': ['Rag.test_rag4_el_vault_cambia_entre_dos_preguntas'],
    'la_calidad_se_mide_con_preguntas_de_oro': ['Rag.test_rag5_evaluar'],
}
PREFIX = 'test_rag.'
LIMITES = ('Escenarios rag1–rag5 en proyectos temporales, Linux, con un proveedor de embeddings de prueba (HTTP local); la '
           'calidad del RAG de Factory se mide con sus 22 preguntas de oro, Ollama local y qwen3-embedding:0.6b.')


def fuentes():
    files = [ROOT / 'fabrica.py', ROOT / 'pyproject.toml', Path(__file__), *ROOT.glob('oracle_factory/*.py'),
             *ROOT.glob('tests/*.py'), ROOT / 'tests/tablero_en_node.cjs', ROOT / 'kb/preguntas-de-oro.json', *ROOT.glob('editores/vscode/*.js'),
             *ROOT.glob('catalogos/factory_rag.*.oracle')]
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
    # La calidad del RAG de Factory: sus preguntas de oro sobre su propio conocimiento.
    with contextlib.redirect_stdout(io.StringIO()):
        cli.main(['--proyecto', str(ROOT), 'preguntar', '--evaluar', '--salida', str(output / 'oro')])
    oro = json.loads((output / 'oro' / 'hechos.json').read_text(encoding='utf-8'))
    escribir(output / 'hechos.json', {'rag_caso': rows, 'rag_suite': [{'completa': int(ok), 'casos': len(expected)}], **oro})
    escribir(output / 'resultado.json', {'exitoso': ok, 'tests': result.testsRun, 'casos_contrato': len(expected),
             'casos_exactos_sin_omisiones_duplicados_ni_fallas': complete, 'fuentes_estables': stable, 'origen': origen,
             'versiones': {**versions, 'python': sys.version}, 'limites': LIMITES,
             'calidad': oro['rag_corrida'][0],
             'artefactos_sha256': {name: sha(output / name) for name in ('suite.txt', 'hechos.json', 'trazabilidad.json',
                                                                          'oro/hechos.json', 'oro/detalle.json')}})
    print(f'Evidencia: {output}; {result.testsRun} pruebas, {len(expected)} casos de contrato; éxito: {ok}.')
    print(LIMITES)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
