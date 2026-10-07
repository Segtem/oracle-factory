"""Evidencia del contrato de producir en la carpeta del candidato y preparar la revisión desde los revisores: escenarios p1–p4 con nombre exacto."""
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
    'juzgar_encuentra_la_evidencia_del_candidato': ['p1_evidencia_en_la_carpeta_del_candidato', 'p1_sin_evidencia_falla_sin_registrar',
                                                    'p1_un_cambio_de_producto_deja_viejo_al_candidato',
                                                    'p1_un_cambio_local_sin_commit_deja_viejo_al_candidato',
                                                    'p1_muchos_commits_que_no_tocan_el_producto'],
    'revision_preparar_arma_el_informe_desde_los_revisores': ['p2_dos_informes_de_revisores'],
    'el_borrador_de_decisiones_no_decide': ['p3_registrar_sin_decidir_se_rechaza'],
    'los_informes_se_validan_o_se_marcan': ['p4_informe_de_otro_candidato_no_se_usa', 'p4_sin_clue_se_usa_marcado',
                                            'p4_un_informe_que_no_pasa_clue_no_se_usa', 'p4_con_clue_y_sin_checkout_no_se_usa'],
    'este_repositorio_produce_en_la_carpeta_del_candidato': ['p5_init_avisa_de_paquetes_de_clue_versionados'],
}
REPO = 'este_repositorio_produce_en_la_carpeta_del_candidato'  # lo comprueba este verificador sobre el propio cambio
PREFIX = 'test_autoproduccion.Autoproduccion.test_'
CAMBIO = '20261007-150043-autoproduccion'
LIMITES = ('Escenarios p1–p4 en repositorios temporales, Linux; los informes de revisores son fixtures con el formato de Clue y la '
           'validación de Clue se simula. Más la comprobación de que este cambio tiene su paquete de Clue y los informes de sus '
           'revisores en la carpeta de su candidato.')


def fuentes():
    files = [ROOT / 'fabrica.py', ROOT / 'pyproject.toml', Path(__file__), ROOT / 'tools/terminal.py',
             *ROOT.glob('oracle_factory/*.py'), *ROOT.glob('tests/*.py'), *ROOT.glob('catalogos/factory_autoproduccion.*.oracle')]
    head = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True, capture_output=True, check=True).stdout.strip()
    return {'head': head, 'sha256': {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(files))}}


def este_repositorio():
    """Problemas: el candidato vigente de este cambio tiene que tener los informes de sus revisores (versionados) y, en la
    máquina donde se revisó, su paquete de Clue (los paquetes son locales: en otra máquina se informa, no se exige)."""
    import json
    from unittest.mock import patch
    from oracle_factory import cli, estructura
    with patch.object(cli, 'ROOT', ROOT), patch.object(cli, 'CHANGES', ROOT / 'openspec/changes'):
        sha = cli.candidato_vigente(CAMBIO)
        if sha is None:
            return ['este cambio no tiene una carpeta de candidato vigente'], 'sin candidato'
        carpeta = estructura.ruta_canonica(ROOT, CAMBIO, 'revision', sha)
        informes, problemas = [], []
        for p in sorted(carpeta.glob('*.json')):
            try:
                datos = json.loads(p.read_text(encoding='utf-8'))
            except (OSError, ValueError) as e:  # un informe ilegible es un problema que se informa, no una caída
                problemas.append(f'{p.relative_to(ROOT)} no se puede leer ({type(e).__name__})')
                continue
            if isinstance(datos, dict) and datos.get('schema_version') == 'oracle-clue.review/v1':
                informes.append(p)
        problemas += [] if informes else [f'el candidato {sha} no tiene informes de revisores en revision/']
        if not any((carpeta.parent / 'clue').glob('*.json')):
            return problemas, 'paquetes de Clue ausentes en esta máquina (son locales): informes sin validar aquí'
        revisores, _, _, avisos = cli.material_del_candidato(CAMBIO, sha)
        problemas += [a for a in avisos if 'no lo uso' in a]
        return problemas, f'{len(revisores)} informe(s) validados o marcados en esta máquina'


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
    problemas, nota_repositorio = este_repositorio()
    repo_ok = not problemas
    ok = result.wasSuccessful() and complete and stable and repo_ok
    rows = [{'requisito': suffix, 'caso': name, 'codigo': result.observados.get(PREFIX + name, 1)}
            for suffix, names in CONTRACTS.items() for name in names]
    rows.append({'requisito': REPO, 'caso': 'candidato_propio', 'codigo': 0 if repo_ok else 1})
    (output / 'suite.txt').write_text(stream.getvalue(), encoding='utf-8')
    escribir(output / 'hechos.json', {'autoproduccion_caso': rows, 'autoproduccion_corrida': [{'completa': int(ok), 'casos': len(expected) + 1}]})
    escribir(output / 'resultado.json', {'exitoso': ok, 'tests': result.testsRun, 'casos_contrato': len(expected),
             'casos_exactos_sin_omisiones_duplicados_ni_fallas': complete, 'fuentes_estables': stable, 'problemas_en_el_repositorio': problemas, 'repositorio': nota_repositorio, 'origen': origen,
             'versiones': {**versions, 'python': sys.version}, 'limites': LIMITES,
             'artefactos_sha256': {name: sha(output / name) for name in ('suite.txt', 'hechos.json')}})
    print(f'Evidencia: {output}; {result.testsRun} pruebas, {len(expected) + 1} casos de contrato; éxito: {ok}.')
    print(LIMITES)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
