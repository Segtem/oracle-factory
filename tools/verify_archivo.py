"""Evidencia del contrato de archivar al cerrar: escenarios a1–a6 con nombre exacto."""
from collections import Counter
from importlib import metadata
import io
import argparse
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.verify_review_guided import Resultado, escribir, sha  # noqa: E402

CONTRACTS = {
    'la_spec_de_un_cambio_se_fusiona_al_cerrarlo': ['a1_primer_cambio_de_una_capacidad', 'a1_un_cambio_que_modifica_y_quita_requisitos'],
    'un_conflicto_impide_cerrar': ['a2_agregar_un_requisito_que_ya_existe', 'a2_modificar_un_requisito_que_no_existe',
                                   'a2_una_spec_consolidada_editada_a_mano_no_se_pisa',
                                   'a2_cerrar_con_la_spec_consolidada_editada_se_rechaza_antes_de_preguntar', 'a2_secciones_mayusculas_y_nombres_repetidos'],
    'lo_cerrado_no_se_mueve_ni_se_reescribe': ['a3_archivar_solo_agrega_la_marca', 'a3_un_corte_al_guardar_el_registro_no_lo_trunca',
                                               'a3_un_registro_de_solo_lectura_no_se_modifica'],
    'se_distingue_lo_vigente_de_lo_reemplazado': ['a4_requisito_reemplazado'],
    'una_capacidad_con_un_solo_nombre': ['a5_capacidad_con_alias', 'a5_un_alias_de_un_alias_se_rechaza'],
    'los_comandos_de_lectura_muestran_el_archivo': ['a6_lectura_de_un_cambio_archivado'],
    'este_repositorio_queda_archivado': ['a6_segunda_ejecucion_no_cambia_nada', 'a6_reintento_de_un_cierre_cortado_no_duplica',
                                         'a6_solo_se_archivan_los_cerrados_y_en_el_orden_de_cierre',
                                         'a6_un_cierre_anterior_sin_registro_de_cierre', 'a6_un_corte_entre_la_spec_y_el_indice_se_repara', 'a6_la_huella_ignora_solo_las_specs_que_genera_factory'],
}
REPO = 'este_repositorio_queda_archivado'  # además de sus pruebas, lo comprueba este verificador sobre el repositorio
PREFIX = 'test_archivo.Archivo.test_'
LIMITES = ('Escenarios a1–a6 en repositorios temporales, Linux; en algunos el cierre se simula marcando el registro, porque archivar '
           'sólo mira la fase y el orden de cierre. Más cuatro comprobaciones sobre este repositorio: cada cambio cerrado está archivado, '
           'cada spec consolidada coincide con su índice y cada requisito vigente existe, los registros sólo ganaron la marca de archivo '
           'respecto del commit anterior a archivar, y tareas/ no cambió. No mide que la spec consolidada sea legible.')


def fuentes():
    files = [ROOT / 'fabrica.py', ROOT / 'pyproject.toml', Path(__file__), ROOT / 'tools/terminal.py',
             *ROOT.glob('oracle_factory/*.py'), *ROOT.glob('tests/*.py'), *ROOT.glob('catalogos/factory_archivo.*.oracle')]
    head = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True, capture_output=True, check=True).stdout.strip()
    return {'head': head, 'sha256': {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(files))}}


def git_show(ref, ruta):
    p = subprocess.run(['git', '-C', str(ROOT), 'show', f'{ref}:{ruta}'], text=True, capture_output=True)
    return p.stdout if p.returncode == 0 else None


def este_repositorio(base, antes):
    """Problemas encontrados en este repositorio; vacío si está archivado y nada más cambió."""
    from oracle_factory import archivo
    problemas = []
    for registro in sorted(ROOT.glob('.factory/cambios/*/factory.json')):
        estado = json.loads(registro.read_text(encoding='utf-8'))
        if estado.get('fase') == 'cerrada' and not estado.get('archivo'):
            problemas.append(f'{estado["id"]}: cerrado sin archivar')
        previo = git_show(antes, registro.relative_to(ROOT).as_posix())
        if previo is not None and estado.get('archivo'):
            viejo = json.loads(previo)
            sin_marca = {k: v for k, v in estado.items() if k != 'archivo'}
            # cerrado antes de `antes` y archivado después: sólo puede haber ganado la marca y un evento. Un cambio que se cerró
            # después (con cerrar, que también archiva) cambió legítimamente su registro.
            if 'archivo' not in viejo and viejo.get('fase') == 'cerrada':
                sin_marca['eventos'] = sin_marca['eventos'][:-1]
                if sin_marca != viejo or estado['eventos'][-1]['accion'] != 'archivado':
                    problemas.append(f'{estado["id"]}: el registro cambió algo más que la marca de archivo')
    for indice_ruta in sorted(ROOT.glob('.factory/specs/*.json')):
        indice = json.loads(indice_ruta.read_text(encoding='utf-8'))
        spec = ROOT / 'openspec/specs' / indice['capacidad'] / 'spec.md'
        if not spec.is_file() or spec.read_text(encoding='utf-8') != archivo.texto_consolidado(indice):
            problemas.append(f'{spec.relative_to(ROOT)}: no coincide con su índice')
        for nombre, req in indice['requisitos'].items():
            if not (ROOT / 'requisitos' / f'{req["requisito"]}.requisito').is_file():
                problemas.append(f'{indice["capacidad"]}: «{nombre}» apunta a un requisito inexistente {req["requisito"]}')
    cambiados = subprocess.run(['git', '-C', str(ROOT), 'diff', '--name-status', base, '--', 'tareas'], text=True,
                               capture_output=True, check=True).stdout.splitlines()
    problemas += [f'tareas/ cambió: {l}' for l in cambiados if not l.startswith('A')]
    return problemas


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida', type=Path, required=True, help='carpeta nueva de evidencia')
    parser.add_argument('--base', default='main', help='referencia de Git contra la que tareas/ no debe cambiar')
    parser.add_argument('--antes', required=True, help='commit justo antes de archivar los cambios existentes; '
                                        'contra él se comprueba que los registros sólo ganaron la marca de archivo')
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
    problemas = este_repositorio(args.base, args.antes)
    repo_ok = not problemas
    ok = result.wasSuccessful() and complete and stable and repo_ok
    rows = [{'requisito': suffix, 'caso': name, 'codigo': result.observados.get(PREFIX + name, 1)}
            for suffix, names in CONTRACTS.items() for name in names]
    rows.append({'requisito': REPO, 'caso': 'repositorio_archivado', 'codigo': 0 if repo_ok else 1})
    (output / 'suite.txt').write_text(stream.getvalue(), encoding='utf-8')
    escribir(output / 'hechos.json', {'archivo_caso': rows, 'archivo_corrida': [{'completa': int(ok), 'casos': len(expected) + 1}]})
    escribir(output / 'resultado.json', {'exitoso': ok, 'tests': result.testsRun, 'casos_contrato': len(expected),
             'casos_exactos_sin_omisiones_duplicados_ni_fallas': complete, 'fuentes_estables': stable, 'problemas_en_el_repositorio': problemas, 'antes': args.antes, 'base': args.base, 'origen': origen,
             'versiones': {**versions, 'python': sys.version}, 'limites': LIMITES,
             'artefactos_sha256': {name: sha(output / name) for name in ('suite.txt', 'hechos.json')}})
    print(f'Evidencia: {output}; {result.testsRun} pruebas, {len(expected) + 1} casos de contrato; éxito: {ok}.')
    print(LIMITES)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
