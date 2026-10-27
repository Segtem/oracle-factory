"""Evidencia del contrato del tablero para el equipo: escenarios tbe1–tbe2 con nombre exacto, y la trazabilidad de esos mismos casos."""
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

CAMBIO = '20261027-160716-arb-equipo'
CONTRACTS = {
    'el_tablero_dice_a_quien_necesita': [
        'TableroEquipo.test_tbe1_el_json_dice_quien_sos_sin_tocar_la_configuracion_de_git',
        'TableroEquipo.test_tbe1_sin_nombre_de_git_yo_es_nulo',
        'TableroEquipo.test_tbe1_un_cambio_de_otra_persona_se_rotula_con_su_nombre',
        'TableroEquipo.test_tbe1_el_cambio_mio_o_sin_responsable_sigue_te_necesita',
        'TableroEquipo.test_tbe1_lo_que_no_es_una_decision_no_cambia_de_rotulo',
        'TableroEquipo.test_tbe1_el_nombre_del_responsable_se_escapa'],
    'actividad_reciente_del_proyecto': [
        'TableroEquipo.test_tbe2_la_actividad_trae_los_diez_eventos_mas_nuevos_primero',
        'TableroEquipo.test_tbe2_un_cambio_cerrado_no_entra',
        'TableroEquipo.test_tbe2_sin_cambios_la_actividad_es_una_lista_vacia',
        'TableroEquipo.test_tbe2_la_pagina_muestra_la_actividad_y_escapa_el_registro',
        'TableroEquipo.test_tbe2_sin_actividad_la_pagina_lo_dice'],
}
PREFIX = 'test_tablero_equipo.'
LIMITES = ('Escenarios tbe1–tbe2: el JSON con la CLI de verdad en proyectos temporales con git, y la página del tablero armada en node '
           '(tablero.js puro) con datos de un cambio; el panel de VS Code no se abre en un editor real y no se mide la apariencia. '
           'El invitado de Live Share ve el tablero de quien comparte, con el nombre de Git de esa persona: no se prueba con dos máquinas.')


def fuentes():
    files = [ROOT / 'fabrica.py', ROOT / 'pyproject.toml', Path(__file__), *ROOT.glob('oracle_factory/*.py'),
             *ROOT.glob('tests/*.py'), ROOT / 'tests/tablero_en_node.cjs', *ROOT.glob('editores/vscode/*.js'),
             *ROOT.glob('catalogos/factory_tablero_equipo.*.oracle')]
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
    escribir(output / 'hechos.json', {'tablero_equipo_caso': rows, 'tablero_equipo_corrida': [{'completa': int(ok), 'casos': len(expected)}]})
    escribir(output / 'resultado.json', {'exitoso': ok, 'tests': result.testsRun, 'casos_contrato': len(expected),
             'casos_exactos_sin_omisiones_duplicados_ni_fallas': complete, 'fuentes_estables': stable, 'origen': origen,
             'versiones': {**versions, 'python': sys.version}, 'limites': LIMITES,
             'artefactos_sha256': {name: sha(output / name) for name in ('suite.txt', 'hechos.json', 'trazabilidad.json')}})
    print(f'Evidencia: {output}; {result.testsRun} pruebas, {len(expected)} casos de contrato; éxito: {ok}.')
    print(LIMITES)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
