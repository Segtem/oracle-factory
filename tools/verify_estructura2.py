"""Evidencia del contrato de la fase 2 de la estructura: escenarios s1–s7 con nombre exacto."""
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
    'el_estado_de_un_cambio_nuevo_vive_en_factory': ['s1_cambio_nuevo_guarda_su_estado_en_factory'],
    'un_proyecto_no_migrado_sigue_funcionando': ['s2_cambio_anterior_a_la_fase_2'],
    'migrar_mueve_el_estado_sin_cambiar_su_contenido': ['s3_migrar_mueve_el_estado_y_solo_reescribe_las_rutas_citadas',
                                                        's3_vista_previa_no_escribe_y_falla_mientras_haya_algo'],
    'migrar_no_pierde_ni_pisa_nada': ['s4_segunda_ejecucion_no_cambia_nada', 's4_interrupcion_despues_de_escribir_y_antes_de_borrar',
                                      's4_corte_a_mitad_de_la_escritura_deja_el_viejo_entero',
                                      's4_estado_en_los_dos_lugares_con_contenido_distinto'],
    'la_migracion_conserva_el_significado': ['s5_estado_y_huella_iguales_antes_y_despues'],
    'la_configuracion_del_proyecto_vive_en_factory': ['s6_init_crea_la_configuracion_en_factory', 's6_configuracion_en_factory_manda',
                                                      's6_configuracion_en_la_raiz_se_respeta_y_se_avisa', 's6_migrar_pasa_la_configuracion'],
    'los_comandos_de_lectura_entienden_los_dos_lugares': ['s7_lectura_con_cambios_en_los_dos_lugares'],
}
REPO = 'este_repositorio_queda_migrado_y_verificado'  # sin prueba unitaria: lo comprueba este verificador sobre el repositorio
PREFIX = 'test_estructura2.Estructura2.test_'
LIMITES = ('Escenarios s1–s7 en repositorios temporales, Linux; el lugar anterior se simula moviendo los archivos de un cambio nuevo. '
           'Más tres comprobaciones sobre este repositorio: ningún estado queda en openspec/changes/, ningún archivo de tareas/ que ya '
           'existía en la base cambió y el `estado` de cada cambio es el mismo antes y después. No migra a otras máquinas ni toca el historial de Git.')


def fuentes():
    files = [ROOT / 'fabrica.py', ROOT / 'pyproject.toml', Path(__file__), ROOT / 'tools/terminal.py',
             *ROOT.glob('oracle_factory/*.py'), *ROOT.glob('tests/*.py'), *ROOT.glob('catalogos/factory_estructura2.*.oracle')]
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
        # las únicas diferencias admitidas son las rutas de los archivos movidos
        salida[ident] = salida[ident].replace('.factory/cambios/', 'openspec/changes/')
    return salida


def estados_distintos(base, excluir=()):
    """Cambios cuyo `estado` no es el mismo en la base de Git y en este repositorio (los que ya existían en la base)."""
    with tempfile.TemporaryDirectory() as tmp:
        antes = Path(tmp) / 'base'
        subprocess.run(['git', '-C', str(ROOT), 'worktree', 'add', '--detach', '-q', str(antes), base], check=True, capture_output=True)
        try:
            cambios = sorted({p.parent.name for p in [*antes.glob('openspec/changes/*/factory.json'), *antes.glob('.factory/cambios/*/factory.json')]
                              if p.parent.name not in excluir})
            viejo, nuevo = estados(antes, cambios), estados(ROOT, cambios)
        finally:
            subprocess.run(['git', '-C', str(ROOT), 'worktree', 'remove', '--force', str(antes)], capture_output=True)
    return [ident for ident in cambios if viejo[ident] != nuevo[ident] or not viejo[ident]]


def este_repositorio(base):
    """(estados que quedan en el lugar anterior, archivos de tareas/ ya existentes en la base que cambiaron)."""
    quedan = sorted(p.relative_to(ROOT).as_posix() for n in ('factory.json', 'review.md', 'oracle-veredicto.txt')
                    for p in ROOT.glob(f'openspec/changes/*/{n}'))
    if (ROOT / 'factory.json').exists():
        quedan.append('factory.json')
    cambiados = subprocess.run(['git', '-C', str(ROOT), 'diff', '--name-status', base, '--', 'tareas'], text=True,
                               capture_output=True, check=True).stdout.splitlines()
    return quedan, [l for l in cambiados if not l.startswith('A')]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida', type=Path, required=True, help='carpeta nueva de evidencia')
    parser.add_argument('--base', default='main', help='referencia de Git contra la que tareas/ no debe cambiar')
    parser.add_argument('--excluir', action='append', default=[], help='cambio que sigue avanzando (el de la propia fase 2)')
    parser.add_argument('--antes', help='commit justo antes de migrar, para comparar `estado`; por defecto, --base. '
                                        'Contra una base que difiere en otros archivos del producto, `estado` cambia por vigencia y no por la migración.')
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
    quedan, tocados = este_repositorio(args.base)
    distintos = estados_distintos(args.antes or args.base, args.excluir)
    repo_ok = not quedan and not tocados and not distintos
    ok = result.wasSuccessful() and complete and stable and repo_ok
    rows = [{'requisito': suffix, 'caso': name, 'codigo': result.observados.get(PREFIX + name, 1)}
            for suffix, names in CONTRACTS.items() for name in names]
    rows.append({'requisito': REPO, 'caso': 'repositorio_migrado', 'codigo': 0 if repo_ok else 1})
    (output / 'suite.txt').write_text(stream.getvalue(), encoding='utf-8')
    escribir(output / 'hechos.json', {'estructura2_caso': rows, 'estructura2_corrida': [{'completa': int(ok), 'casos': len(expected) + 1}]})
    escribir(output / 'resultado.json', {'exitoso': ok, 'tests': result.testsRun, 'casos_contrato': len(expected),
             'casos_exactos_sin_omisiones_duplicados_ni_fallas': complete, 'fuentes_estables': stable, 'estados_en_el_lugar_anterior': quedan, 'tareas_tocadas': tocados, 'estados_distintos': distintos, 'estados_comparados_con': args.antes or args.base, 'estados_excluidos': args.excluir, 'origen': origen,
             'versiones': {**versions, 'python': sys.version}, 'limites': LIMITES,
             'artefactos_sha256': {name: sha(output / name) for name in ('suite.txt', 'hechos.json')}})
    print(f'Evidencia: {output}; {result.testsRun} pruebas, {len(expected) + 1} casos de contrato; éxito: {ok}.')
    print(LIMITES)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
