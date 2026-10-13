"""Evidencia del contrato de abandonar un cambio: escenarios ab1–ab4 con nombre exacto."""
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
    'abandonar_es_una_decision_de_persona_con_motivo': ['ab1_la_persona_abandona_con_el_motivo_propuesto', 'ab1_un_agente_no_abandona',
                                                        'ab1_la_persona_cancela', 'ab1_sin_terminal_no_se_abandona',
                                                        'ab1_un_cambio_cerrado'],
    'lo_abandonado_no_queda_abierto_ni_medido': ['ab2_abandonar_un_cambio_con_requisitos_importados',
                                                 'ab2_un_comando_sobre_un_cambio_abandonado',
                                                 'ab2_si_el_tracker_no_cierra_no_cambia_nada',
                                                 'ab2_un_corte_despues_del_registro_se_completa'],
    'el_resumen_muestra_lo_abandonado_aparte': ['ab3_un_cambio_abandonado_en_el_resumen'],
    'una_carpeta_sin_registro_tambien_se_abandona': ['ab4_una_carpeta_anterior_al_flujo'],
}
PREFIX = 'test_abandonar.Abandonar.test_'
LIMITES = ('Escenarios ab1–ab4 en repositorios temporales, Linux, con la terminal y las respuestas del menú simuladas. No prueba '
           'el abandono de los cambios viejos de este repositorio: eso lo decide una persona después de integrar.')


def fuentes():
    files = [ROOT / 'fabrica.py', ROOT / 'pyproject.toml', Path(__file__), *ROOT.glob('oracle_factory/*.py'),
             *ROOT.glob('tests/*.py'), *ROOT.glob('catalogos/factory_abandonar.*.oracle')]
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
    escribir(output / 'hechos.json', {'abandonar_caso': rows, 'abandonar_corrida': [{'completa': int(ok), 'casos': len(expected)}]})
    escribir(output / 'resultado.json', {'exitoso': ok, 'tests': result.testsRun, 'casos_contrato': len(expected),
             'casos_exactos_sin_omisiones_duplicados_ni_fallas': complete, 'fuentes_estables': stable, 'origen': origen,
             'versiones': {**versions, 'python': sys.version}, 'limites': LIMITES,
             'artefactos_sha256': {name: sha(output / name) for name in ('suite.txt', 'hechos.json')}})
    print(f'Evidencia: {output}; {result.testsRun} pruebas, {len(expected)} casos de contrato; éxito: {ok}.')
    print(LIMITES)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
