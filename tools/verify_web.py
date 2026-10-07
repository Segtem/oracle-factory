"""Evidencia del contrato de la web y las guías al día: escenarios w1–w6 y el arnés de la guía con el paquete instalado con nombre exacto."""
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
    'la_web_explica_como_trabajar_entre_varias_personas_con_sus_agentes': ['w1_pagina_de_colaboracion_enlazada_y_completa'],
    'el_sitio_cuenta_lo_que_trae_la_version_publicada': ['w2_el_sitio_cuenta_la_version_publicada'],
    'lo_que_la_web_nombra_existe': ['w3_los_comandos_nombrados_existen', 'w3_la_comprobacion_detecta_un_comando_inexistente',
                                    'w3_los_enlaces_internos_resuelven'],
    'guia_de_colaboracion_sin_las_fricciones_del_piloto': ['w4_la_guia_resuelve_las_fricciones'],
    'el_id_de_un_cambio_termina_en_un_sufijo_legible': ['w5_sufijo_por_defecto_y_elegido', 'w5_sufijo_invalido_no_crea_nada'],
    'la_guia_desde_cero_sigue_funcionando': ['w6_pagina_nueva_accesible_sin_javascript'],
}
REPO = 'la_guia_desde_cero_sigue_funcionando'  # además, el arnés de la guía con el paquete instalado
PREFIX = 'test_web.Web.test_'
LIMITES = ('Escenarios w1–w6 sobre el HTML y las guías del repositorio, sin navegador (Playwright no está instalado); más el arnés '
           'de la guía desde cero con el paquete construido e instalado. No mide que la página sea clara para quien la lee.')


def fuentes():
    files = [ROOT / 'fabrica.py', ROOT / 'pyproject.toml', Path(__file__), ROOT / 'tools/terminal.py', ROOT / 'tools/verify_guide.py',
             *ROOT.glob('oracle_factory/*.py'), *ROOT.glob('tests/*.py'), *ROOT.glob('catalogos/factory_web.*.oracle'),
             *ROOT.glob('site/*'), *ROOT.glob('docs/*.md')]
    head = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True, capture_output=True, check=True).stdout.strip()
    return {'head': head, 'sha256': {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(files))}}


def este_repositorio(factory):
    p = subprocess.run([sys.executable, str(ROOT / 'tools/verify_guide.py'), '--factory', str(factory)],
                       cwd=ROOT, text=True, capture_output=True, stdin=subprocess.DEVNULL)
    return [] if p.returncode == 0 else [(p.stdout + p.stderr).strip()[-2000:]]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida', type=Path, required=True, help='carpeta nueva de evidencia')
    parser.add_argument('--factory', type=Path, required=True, help='oracle-factory del paquete construido e instalado, para el arnés de la guía')
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
    problemas = este_repositorio(args.factory)
    repo_ok = not problemas
    ok = result.wasSuccessful() and complete and stable and repo_ok
    rows = [{'requisito': suffix, 'caso': name, 'codigo': result.observados.get(PREFIX + name, 1)}
            for suffix, names in CONTRACTS.items() for name in names]
    rows.append({'requisito': REPO, 'caso': 'guia_con_el_paquete_instalado', 'codigo': 0 if repo_ok else 1})
    (output / 'suite.txt').write_text(stream.getvalue(), encoding='utf-8')
    escribir(output / 'hechos.json', {'web_caso': rows, 'web_corrida': [{'completa': int(ok), 'casos': len(expected) + 1}]})
    escribir(output / 'resultado.json', {'exitoso': ok, 'tests': result.testsRun, 'casos_contrato': len(expected),
             'casos_exactos_sin_omisiones_duplicados_ni_fallas': complete, 'fuentes_estables': stable, 'problemas_en_el_repositorio': problemas, 'origen': origen,
             'versiones': {**versions, 'python': sys.version}, 'limites': LIMITES,
             'artefactos_sha256': {name: sha(output / name) for name in ('suite.txt', 'hechos.json')}})
    print(f'Evidencia: {output}; {result.testsRun} pruebas, {len(expected) + 1} casos de contrato; éxito: {ok}.')
    print(LIMITES)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
