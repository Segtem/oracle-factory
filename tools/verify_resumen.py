"""Evidencia del contrato de el resumen del estado actual: escenarios r1–r6 con nombre exacto."""
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
    'el_resumen_muestra_lo_vigente_y_lo_pendiente': ['r1_capacidad_archivada_y_cambio_abierto', 'r1_requisito_reemplazado'],
    'riesgos_aceptados_y_limites_declarados': ['r2_riesgo_vigente_e_historico'],
    'el_veredicto_es_el_del_cierre_y_lo_dice': ['r3_veredicto_del_cierre'],
    'el_resumen_es_determinista_y_no_cambia_nada_mas': ['r4_dos_ejecuciones_seguidas'],
    'se_sabe_cuando_quedo_viejo': ['r5_un_cambio_avanza_despues_de_generar', 'r5_editado_a_mano'],
    'se_actualiza_al_cerrar_y_al_archivar': ['r6_cerrar_y_archivar_lo_regeneran', 'r6_salida_en_otra_ruta'],
    'este_repositorio_tiene_su_resumen_al_dia': [],
}
REPO = 'este_repositorio_tiene_su_resumen_al_dia'  # lo comprueba este verificador: resumen --verificar sobre el repositorio
PREFIX = 'test_resumen.Resumen.test_'
LIMITES = ('Escenarios r1–r6 en repositorios temporales, Linux; los riesgos se arman a mano en el registro. Más la comprobación de que el '
           'resumen de este repositorio está al día. No mide que el resumen sea útil para quien lo lee.')


def fuentes():
    files = [ROOT / 'fabrica.py', ROOT / 'pyproject.toml', Path(__file__), ROOT / 'tools/terminal.py',
             *ROOT.glob('oracle_factory/*.py'), *ROOT.glob('tests/*.py'), *ROOT.glob('catalogos/factory_resumen.*.oracle')]
    head = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True, capture_output=True, check=True).stdout.strip()
    return {'head': head, 'sha256': {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(files))}}


def este_repositorio():
    p = subprocess.run([sys.executable, '-W', 'ignore', '-m', 'oracle_factory.cli', '--proyecto', str(ROOT), 'resumen', '--verificar'],
                       cwd=ROOT, text=True, capture_output=True)
    return [] if p.returncode == 0 else [p.stdout.strip() or p.stderr.strip()]


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
    rows.append({'requisito': REPO, 'caso': 'repositorio_al_dia', 'codigo': 0 if repo_ok else 1})
    (output / 'suite.txt').write_text(stream.getvalue(), encoding='utf-8')
    escribir(output / 'hechos.json', {'resumen_caso': rows, 'resumen_corrida': [{'completa': int(ok), 'casos': len(expected) + 1}]})
    escribir(output / 'resultado.json', {'exitoso': ok, 'tests': result.testsRun, 'casos_contrato': len(expected),
             'casos_exactos_sin_omisiones_duplicados_ni_fallas': complete, 'fuentes_estables': stable, 'problemas_en_el_repositorio': problemas, 'origen': origen,
             'versiones': {**versions, 'python': sys.version}, 'limites': LIMITES,
             'artefactos_sha256': {name: sha(output / name) for name in ('suite.txt', 'hechos.json')}})
    print(f'Evidencia: {output}; {result.testsRun} pruebas, {len(expected) + 1} casos de contrato; éxito: {ok}.')
    print(LIMITES)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
