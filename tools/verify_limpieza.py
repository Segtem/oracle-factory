"""Evidencia del contrato de limpieza de rutas privadas: escenarios l1–l4 con nombre exacto."""
from collections import Counter
from importlib import metadata
import io
import argparse
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.verify_review_guided import Resultado, escribir, sha  # noqa: E402

CONTRACTS = {
    'los_registros_no_llevan_la_ruta_privada': ['l1_requisito_con_fuente_absoluta', 'l1_requisitos_previos',
                                                'l1_hechos_absolutos_en_el_registro',
                                                'l1_directorios_ambiguos_y_formas_que_no_se_pueden_reescribir',
                                                'l1_fin_de_linea_windows_y_comillas_escapadas', 'l1_el_verificador_ve_cada_clase_de_registro'],
    'las_decisiones_conservan_su_integridad': ['l2_la_decision_sigue_vigente_y_deja_evento', 'l2_estado_igual_antes_y_despues',
                                               'l2_decision_sin_hash_o_con_otro_hash_no_se_toca', 'l2_la_propuesta_pendiente_tambien_sigue_vigente'],
    'la_evidencia_no_se_reescribe': ['l3_tareas_byte_a_byte'],
    'limpieza_repetible_y_verificable': ['l4_segunda_ejecucion_no_cambia_nada', 'l4_verificar_no_escribe_y_falla_si_queda_algo',
                                         'l4_registro_que_no_se_reserializa_igual_se_avisa_y_no_se_toca',
                                         'l4_una_interrupcion_a_mitad_se_repara_en_la_corrida_siguiente',
                                         'l4_si_falla_el_reemplazo_el_archivo_original_queda_entero'],
}
PREFIX = 'test_limpieza.Limpieza.test_'
LIMITES = ('Escenarios l1–l4 en repositorios temporales, Linux, con la ruta de «otra persona» inventada; más tres comprobaciones sobre este '
           'repositorio: ningún registro conserva una ruta absoluta, ningún archivo de tareas/ que ya existía en la base cambió y el `estado` de cada cambio de la base es el mismo (salvo que ya no faltan hechos). '
           'No toca el historial de Git: la ruta sigue en los commits anteriores.')


def fuentes():
    files = [ROOT / 'fabrica.py', ROOT / 'pyproject.toml', Path(__file__), ROOT / 'tools/limpiar_rutas.py', ROOT / 'tools/terminal.py',
             *ROOT.glob('oracle_factory/*.py'), *ROOT.glob('tests/*.py'), *ROOT.glob('catalogos/factory_limpieza.*.oracle')]
    head = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True, capture_output=True, check=True).stdout.strip()
    return {'head': head, 'sha256': {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(files))}}


def estados(raiz, cambios):
    """La salida de `estado` de cada cambio, con las rutas de la máquina quitadas para poder compararlas."""
    salida = {}
    for ident in cambios:
        p = subprocess.run([sys.executable, '-W', 'ignore', '-m', 'oracle_factory.cli', '--proyecto', str(raiz), 'estado', ident],
                           cwd=ROOT, text=True, capture_output=True)
        texto = p.stdout.replace(str(raiz), '<raiz>')
        # La única diferencia admitida: sin la ruta de otra máquina, los hechos dejan de «faltar».
        salida[ident] = re.sub(r'; hechos ausentes \(.*?RUTA_DE_LOS_HECHOS', '', texto, flags=re.S)
        salida[ident] = re.sub(r'/(?:[^/\s]+/)*?(?=(?:openspec|tareas)/)', '', salida[ident])
    return salida


def estados_distintos(base, excluir=()):
    """Cambios cuyo `estado` no es el mismo en la base de Git y en este repositorio (los que ya existían en la base)."""
    with tempfile.TemporaryDirectory() as tmp:
        antes = Path(tmp) / 'base'
        subprocess.run(['git', '-C', str(ROOT), 'worktree', 'add', '--detach', '-q', str(antes), base], check=True, capture_output=True)
        try:
            cambios = sorted(p.parent.name for p in (antes / 'openspec/changes').glob('*/factory.json') if p.parent.name not in excluir)
            viejo, nuevo = estados(antes, cambios), estados(ROOT, cambios)
        finally:
            subprocess.run(['git', '-C', str(ROOT), 'worktree', 'remove', '--force', str(antes)], capture_output=True)
    return [ident for ident in cambios if viejo[ident] != nuevo[ident] or not viejo[ident]]


def este_repositorio(base):
    """(registros sin ruta absoluta, archivos de tareas/ ya existentes en la base que cambiaron)."""
    from tools import limpiar_rutas
    cambiados = subprocess.run(['git', '-C', str(ROOT), 'diff', '--name-status', base, '--', 'tareas'], text=True,
                               capture_output=True, check=True).stdout.splitlines()
    tocados = [l for l in cambiados if not l.startswith('A')]
    return limpiar_rutas.restos(ROOT), tocados


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida', type=Path, required=True, help='carpeta nueva de evidencia')
    parser.add_argument('--base', default='main', help='referencia de Git contra la que tareas/ no debe cambiar')
    parser.add_argument('--excluir', action='append', default=[], help='cambio que sigue avanzando (el de la propia limpieza)')
    parser.add_argument('--antes', help='commit justo antes de aplicar la limpieza, para comparar `estado`; por defecto, --base. '
                                        'Contra una base que difiere en otros archivos del producto, `estado` cambia por vigencia y no por la limpieza.')
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
    restos, tocados = este_repositorio(args.base)
    distintos = estados_distintos(args.antes or args.base, args.excluir)
    ok = result.wasSuccessful() and complete and stable and not restos and not tocados and not distintos
    rows = [{'requisito': suffix, 'caso': name, 'codigo': result.observados.get(PREFIX + name, 1)}
            for suffix, names in CONTRACTS.items() for name in names]
    (output / 'suite.txt').write_text(stream.getvalue(), encoding='utf-8')
    escribir(output / 'hechos.json', {'limpieza_caso': rows, 'limpieza_corrida': [{'completa': int(ok), 'casos': len(expected)}]})
    escribir(output / 'resultado.json', {'exitoso': ok, 'tests': result.testsRun, 'casos_contrato': len(expected),
             'casos_exactos_sin_omisiones_duplicados_ni_fallas': complete, 'fuentes_estables': stable, 'registros_con_ruta': restos, 'tareas_tocadas': tocados, 'estados_distintos': distintos, 'estados_comparados_con': args.antes or args.base, 'estados_excluidos': args.excluir, 'origen': origen,
             'versiones': {**versions, 'python': sys.version}, 'limites': LIMITES,
             'artefactos_sha256': {name: sha(output / name) for name in ('suite.txt', 'hechos.json')}})
    print(f'Evidencia: {output}; {result.testsRun} pruebas, {len(expected)} casos de contrato; éxito: {ok}.')
    print(LIMITES)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
