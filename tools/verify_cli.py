"""Evidencia del contrato de la CLI cómoda para la persona: escenarios c1–c5 con nombre exacto."""
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
    'los_errores_dicen_que_paso_y_como_seguir': ['c1_aprobar_con_una_comprobacion_que_falla', 'c1_preparar_sin_candidato_avisa',
                                                 'c1_falta_oracle'],
    'fabrica_py_usa_el_entorno_del_proyecto': ['c2_python_del_sistema'],
    'el_resumen_se_ve_con_formato': ['c3_sin_glow', 'c3_con_glow'],
    'estado_calcula_y_ofrece_el_proximo_paso': ['c4_listo_para_cerrar', 'c4_medidas_propuestas', 'c4_salir_no_ejecuta',
                                                'c4_candidato_sin_material',
                                                'c4_oracle_rojo_sin_cambios', 'c4_recorrido_completo'],
    'el_proximo_paso_no_se_ejecuta_solo': ['c5_agente_sin_terminal_o_salida_redirigida'],
}
PREFIX = 'test_cli_humana.CliHumana.test_'
LIMITES = ('Escenarios c1–c5 en repositorios temporales, Linux, con la entrada de la terminal simulada; la re-ejecución de '
           'fabrica.py se prueba con un intérprete sin site-packages y un .venv de prueba; glow no se ejecuta (se comprueba la '
           'llamada). No mide que los mensajes sean claros para quien los lee.')


def fuentes():
    files = [ROOT / 'fabrica.py', ROOT / 'pyproject.toml', Path(__file__), *ROOT.glob('oracle_factory/*.py'),
             *ROOT.glob('tests/*.py'), *ROOT.glob('catalogos/factory_cli.*.oracle')]
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
    escribir(output / 'hechos.json', {'cli_caso': rows, 'cli_corrida': [{'completa': int(ok), 'casos': len(expected)}]})
    escribir(output / 'resultado.json', {'exitoso': ok, 'tests': result.testsRun, 'casos_contrato': len(expected),
             'casos_exactos_sin_omisiones_duplicados_ni_fallas': complete, 'fuentes_estables': stable, 'origen': origen,
             'versiones': {**versions, 'python': sys.version}, 'limites': LIMITES,
             'artefactos_sha256': {name: sha(output / name) for name in ('suite.txt', 'hechos.json')}})
    print(f'Evidencia: {output}; {result.testsRun} pruebas, {len(expected)} casos de contrato; éxito: {ok}.')
    print(LIMITES)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
