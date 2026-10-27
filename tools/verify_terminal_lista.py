"""Evidencia del contrato de la terminal de Factory que espera a estar lista: escenarios tl1–tl4 con nombre exacto, y la trazabilidad de esos mismos casos."""
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

CAMBIO = '20261027-225048-59a-terminallista'
CONTRACTS = {
    'la_terminal_nueva_espera_a_estar_lista': [
        'TerminalLista.test_tl1_no_escribe_hasta_que_la_terminal_avisa',
        'TerminalLista.test_tl1_el_aviso_de_otra_terminal_no_cuenta',
        'TerminalLista.test_tl1_la_espera_se_libera_una_sola_vez_y_el_reloj_no_queda_andando',
        'TerminalLista.test_tl1_si_la_terminal_se_cierra_mientras_arranca_se_abre_otra_y_el_comando_sale_una_vez',
        'TerminalLista.test_tl1_el_cierre_de_otra_terminal_no_corta_la_espera',
        'TerminalLista.test_tl1_si_se_cierra_dos_veces_seguidas_el_pedido_falla_y_no_escribe_nada',
        'TerminalLista.test_tl1_sin_plazo_configurado_o_con_uno_nulo_escribe_a_los_tres_segundos',
        'TerminalLista.test_tl1_si_nunca_avisa_escribe_al_cumplirse_el_plazo_y_no_antes',
        'TerminalLista.test_tl1_un_plazo_de_cero_escribe_de_inmediato',
        'TerminalLista.test_tl1_una_version_sin_el_evento_cae_al_plazo',
        'TerminalLista.test_tl1_sin_plazo_configurado_no_escribe_enseguida',
        'TerminalLista.test_tl1_un_plazo_invalido_cae_al_de_por_defecto',
        'TerminalLista.test_tl4_el_plazo_se_puede_configurar_en_la_extension'],
    'una_terminal_lista_recibe_el_comando_enseguida': [
        'TerminalLista.test_tl2_una_terminal_que_ya_existia_no_espera_ni_se_duplica',
        'TerminalLista.test_tl2_una_terminal_nueva_que_ya_informa_su_integracion_no_espera',
        'TerminalLista.test_tl2_una_terminal_ya_cerrada_no_se_reutiliza'],
    'los_comandos_seguidos_se_escriben_en_orden_y_una_vez': [
        'TerminalLista.test_tl3_dos_comandos_mientras_arranca_se_escriben_en_orden_y_una_vez',
        'TerminalLista.test_tl3_si_nunca_avisa_los_dos_salen_igual_en_orden',
        'TerminalLista.test_tl3_un_error_al_crear_la_terminal_no_traba_los_pedidos_siguientes',
        'TerminalLista.test_tl3_quien_pide_un_comando_ve_verdadero_si_se_escribio_y_falso_si_no',
        'TerminalLista.test_tl3_si_falla_la_terminal_quien_lo_pide_ve_falso_y_la_salida_lo_dice'],
    'queda_constancia_en_la_salida': [
        'TerminalLista.test_tl4_la_salida_dice_por_que_y_cuanto_sin_el_comando'],
}
PREFIX = 'test_terminal_lista.'
LIMITES = ('Escenarios tl1–tl4 en node con un vscode falso que decide cuándo avisa la terminal: prueban el orden y el momento de la escritura, '
           'no el comportamiento de un shell ni del entorno de Python de VS Code. Que el ^C desaparezca se confirma mirando el botón en un '
           'VS Code real.')


def fuentes():
    files = [ROOT / 'fabrica.py', ROOT / 'pyproject.toml', Path(__file__), *ROOT.glob('oracle_factory/*.py'),
             *ROOT.glob('tests/*.py'), ROOT / 'tests/terminal_en_node.cjs', *ROOT.glob('editores/vscode/*.js'), ROOT / 'editores/vscode/package.json',
             *ROOT.glob('catalogos/factory_terminal_lista.*.oracle')]
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
    escribir(output / 'hechos.json', {'terminal_lista_caso': rows, 'terminal_lista_corrida': [{'completa': int(ok), 'casos': len(expected)}]})
    escribir(output / 'resultado.json', {'exitoso': ok, 'tests': result.testsRun, 'casos_contrato': len(expected),
             'casos_exactos_sin_omisiones_duplicados_ni_fallas': complete, 'fuentes_estables': stable, 'origen': origen,
             'versiones': {**versions, 'python': sys.version}, 'limites': LIMITES,
             'artefactos_sha256': {name: sha(output / name) for name in ('suite.txt', 'hechos.json', 'trazabilidad.json')}})
    print(f'Evidencia: {output}; {result.testsRun} pruebas, {len(expected)} casos de contrato; éxito: {ok}.')
    print(LIMITES)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
