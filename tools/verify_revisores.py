"""Evidencia del contrato de pedir una revisión independiente desde Factory: escenarios v1–v6 con nombre exacto."""
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
    'pedir_una_revision_del_candidato_actual': ['v1_revision_exitosa'],
    'revisores_configurables': ['v2_revisor_no_declarado', 'v2_configuracion_invalida'],
    'el_pedido_se_genera_desde_el_cambio': ['v3_plantilla_del_proyecto_e_indicaciones', 'v3_la_plantilla_de_factory_lleva_lo_necesario'],
    'lo_que_sale_mal_no_se_guarda_como_informe': ['v4_informe_que_clue_rechaza', 'v4_sin_informe', 'v4_tope_superado', 'v4_tope_detiene_a_los_hijos',
                                                  'v4_cambios_sin_commit'],
    'el_revisor_no_decide': ['v5_despues_de_una_revision_exitosa'],
    'las_vueltas_anteriores_se_muestran_sin_decidirse_otra_vez': ['v6_tres_vueltas', 'v6_vuelta_de_otro_candidato', 'v6_vuelta_que_clue_no_valida'],
    'este_cambio_se_revisa_con_pedir_revision': [],
}
REPO = 'este_cambio_se_revisa_con_pedir_revision'  # lo comprueba este verificador sobre el propio cambio
PREFIX = 'test_revisores.Revisores.test_'
CAMBIO = '20261007-192608-revisores'
LIMITES = ('Escenarios v1–v6 en repositorios temporales, Linux, con un revisor de prueba y oracle-clue real (sin Clue las pruebas se '
           'omiten y la corrida no es completa). Más la comprobación de que este cambio tiene en la carpeta de su candidato vigente '
           'un informe de revisor y el pedido con que se obtuvo. No mide la calidad de las revisiones.')


def fuentes():
    files = [ROOT / 'fabrica.py', ROOT / 'pyproject.toml', Path(__file__), ROOT / 'tools/terminal.py',
             *ROOT.glob('oracle_factory/*.py'), ROOT / 'oracle_factory/data/pedido_revision.md', *ROOT.glob('tests/*.py'),
             *ROOT.glob('catalogos/factory_revisores.*.oracle')]
    head = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True, capture_output=True, check=True).stdout.strip()
    return {'head': head, 'sha256': {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(files))}}


def este_repositorio():
    """Problemas: el candidato vigente de este cambio tiene que tener un informe de revisor y su pedido."""
    from unittest.mock import patch
    from oracle_factory import cli
    with patch.object(cli, 'ROOT', ROOT), patch.object(cli, 'CHANGES', ROOT / 'openspec/changes'):
        sha = cli.candidato_vigente(CAMBIO)
        if sha is None:
            return ['este cambio no tiene una carpeta de candidato vigente']
        eventos = cli.leer(CAMBIO)[1].get('eventos') or []
        pedidas = {(e.get('candidato'), e.get('resultado')) for e in eventos if e.get('accion') == 'revision_pedida'}
        # Los mismos informes que usa revision-preparar: de este candidato y validados con Clue contra su paquete.
        validos = [r for r in cli.material_del_candidato(CAMBIO, sha)[0] if r['validacion'] == 'validado con oracle-clue']
        informes = [r for r in validos if (ROOT / r['ruta']).with_suffix('.pedido.md').is_file()]
    if (sha, 'ok') not in pedidas:
        return [f'no hay un pedir-revision exitoso registrado para el candidato {sha}']
    return [] if informes else [f'el candidato {sha} no tiene un informe validado con Clue y su pedido']


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
    problemas = este_repositorio()
    repo_ok = not problemas
    ok = result.wasSuccessful() and complete and stable and repo_ok
    rows = [{'requisito': suffix, 'caso': name, 'codigo': result.observados.get(PREFIX + name, 1)}
            for suffix, names in CONTRACTS.items() for name in names]
    rows.append({'requisito': REPO, 'caso': 'revisado_con_pedir_revision', 'codigo': 0 if repo_ok else 1})
    (output / 'suite.txt').write_text(stream.getvalue(), encoding='utf-8')
    escribir(output / 'hechos.json', {'revisores_caso': rows, 'revisores_corrida': [{'completa': int(ok), 'casos': len(expected) + 1}]})
    escribir(output / 'resultado.json', {'exitoso': ok, 'tests': result.testsRun, 'casos_contrato': len(expected),
             'casos_exactos_sin_omisiones_duplicados_ni_fallas': complete, 'fuentes_estables': stable, 'problemas_en_el_repositorio': problemas, 'origen': origen,
             'versiones': {**versions, 'python': sys.version}, 'limites': LIMITES,
             'artefactos_sha256': {name: sha(output / name) for name in ('suite.txt', 'hechos.json')}})
    print(f'Evidencia: {output}; {result.testsRun} pruebas, {len(expected) + 1} casos de contrato; éxito: {ok}.')
    print(LIMITES)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
