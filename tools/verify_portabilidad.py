"""Evidencia del contrato de portabilidad: escenarios p1–p7 con nombre exacto."""
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

CONTRACTS = {
    'hechos_con_ruta_relativa_al_proyecto': ['p1_hechos_dentro_del_proyecto', 'p1_clon_en_otra_ruta'],
    'advertir_cuando_los_hechos_no_viajan': ['p2_hechos_ignorados_por_git', 'p2_hechos_fuera_del_proyecto'],
    'fuente_de_los_requisitos_relativa': ['p3_fuente_relativa', 'p3_fuente_con_comillas_en_la_ruta_se_reescribe_o_avisa'],
    'pendiente_que_explica_como_recuperarse': ['p4_pendiente_explica_como_recuperarse'],
    'un_cambio_juzgado_en_una_maquina_se_cierra_desde_otra': ['p5_cierre_desde_un_clon_en_otra_ruta'],
    'sin_rutas_privadas_en_lo_versionado': ['p6_sin_rutas_privadas_en_lo_versionado',
                                            'p6_los_requisitos_de_este_repositorio_no_llevan_rutas_privadas'],
    'respetar_los_registros_existentes': ['p7_registro_anterior_con_ruta_absoluta'],
}
PREFIX = 'test_portabilidad.Portabilidad.test_'
LIMITES = ('Escenarios p1–p7 en repositorios temporales, Linux; la otra máquina es un clon en otra ruta, al que se le quita el '
           'original. La evidencia entre máquinas reales aisladas, con contenedores, la da tools/verify_maquinas.py, que se corre a pedido.')


def fuentes():
    files = [ROOT / 'fabrica.py', ROOT / 'pyproject.toml', Path(__file__), ROOT / 'tools/terminal.py',
             *ROOT.glob('oracle_factory/*.py'), *ROOT.glob('tests/*.py'), *ROOT.glob('catalogos/factory_portabilidad.*.oracle')]
    head = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True, capture_output=True, check=True).stdout.strip()
    return {'head': head, 'sha256': {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(files))}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida', type=Path, required=True, help='carpeta nueva de evidencia')
    args = parser.parse_args(argv)
    versions = {p: metadata.version(p) for p in ('oracle-metalenguaje', 'oracle-task')}
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
    escribir(output / 'hechos.json', {'portabilidad_caso': rows, 'portabilidad_corrida': [{'completa': int(ok), 'casos': len(expected)}]})
    escribir(output / 'resultado.json', {'exitoso': ok, 'tests': result.testsRun, 'casos_contrato': len(expected),
             'casos_exactos_sin_omisiones_duplicados_ni_fallas': complete, 'fuentes_estables': stable, 'origen': origen,
             'versiones': {**versions, 'python': sys.version}, 'limites': LIMITES,
             'artefactos_sha256': {name: sha(output / name) for name in ('suite.txt', 'hechos.json')}})
    print(f'Evidencia: {output}; {result.testsRun} pruebas, {len(expected)} casos de contrato; éxito: {ok}.')
    print(LIMITES)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
