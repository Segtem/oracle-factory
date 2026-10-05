"""Evidencia del contrato de modos de trabajo: escenarios m1–m5 con nombre exacto."""
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
    'modo_explicito_por_cambio': ['m1_crear_cambio_con_modo', 'm1_elegir_autonomo_exige_persona',
                                  'm1_modo_del_proyecto_no_evita_a_la_persona'],
    'tipo_de_requisito': ['m2_requisito_no_funcional_declarado', 'm2_requisito_sin_tipo', 'm2_tipos_obligatorios'],
    'decisiones_segun_el_modo': ['m3_funcional_requisito_funcional', 'm3_funcional_requisito_no_funcional',
                                 'm3_confirmacion_propone', 'm3_autonomo', 'm3_cierre_en_modo_funcional',
                                 'm3_spec_nueva_descarta_lo_anterior', 'm3_juzgar_no_cuenta_medidas_propuestas',
                                 'm3_funcional_persona_decide_con_motivo',
                                 'm3_misma_spec_conserva_registros', 'm3_medidas_sin_decision_no_cuentan'],
    'actor_registrado_sin_aparentar_humanos': ['m4_confirmacion_por_pipe', 'm4_lectura_del_estado',
                                               'm4_sin_agente_ni_terminal_no_es_persona', 'm4_notas_dicen_quien_decidio',
                                               'm4_cierre_autonomo_no_niega_decisiones_humanas'],
    'cambio_de_modo_con_invalidacion': ['m5_subir_la_intervencion_humana', 'm5_bajar_de_modo_el_agente_reemplaza_su_propuesta',
                                        'm5_subir_a_funcional_descarta_decision_del_agente',
                                        'm5_bajar_a_funcional_descarta_propuestas'],
}
PREFIX = 'test_modos.Modos.test_'
LIMITES = ('Escenarios m1–m5 en repositorios temporales, Linux. Las personas son fixtures con una terminal simulada; '
           'Factory no autentica actores: un agente que simule una terminal pasa por persona.')


def fuentes():
    files = [ROOT / 'fabrica.py', ROOT / 'pyproject.toml', Path(__file__), ROOT / 'tools/terminal.py',
             *ROOT.glob('oracle_factory/*.py'), *ROOT.glob('tests/*.py'), *ROOT.glob('catalogos/factory_modos.*.oracle')]
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
    escribir(output / 'hechos.json', {'modos_caso': rows, 'modos_corrida': [{'completa': int(ok), 'casos': len(expected)}]})
    escribir(output / 'resultado.json', {'exitoso': ok, 'tests': result.testsRun, 'casos_contrato': len(expected),
             'casos_exactos_sin_omisiones_duplicados_ni_fallas': complete, 'fuentes_estables': stable, 'origen': origen,
             'versiones': {**versions, 'python': sys.version}, 'limites': LIMITES,
             'artefactos_sha256': {name: sha(output / name) for name in ('suite.txt', 'hechos.json')}})
    print(f'Evidencia: {output}; {result.testsRun} pruebas, {len(expected)} casos de contrato; éxito: {ok}.')
    print(LIMITES)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
