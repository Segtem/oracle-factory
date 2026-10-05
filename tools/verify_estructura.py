"""Evidencia del contrato de la estructura de carpetas: escenarios e1–e10 con nombre exacto."""
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
    'estructura_documentada': ['e1_la_guia_describe_cada_artefacto'],
    'carpeta_propia_de_factory': ['e2_init_crea_factory_y_ignora_local', 'e2_init_en_proyecto_existente_conserva_el_gitignore'],
    'descubrir_la_raiz_del_proyecto': ['e3_comando_desde_una_subcarpeta', 'e3_proyecto_explicito_manda',
                                       'e3_sin_factory_se_comporta_como_antes'],
    'lo_versionado_y_lo_local': ['e4_rutas_relativas_en_otra_ruta_absoluta'],
    'la_huella_del_producto_excluye_lo_que_factory_produce': ['e5_nueva_evidencia_no_invalida_la_revision',
                                                              'e5_el_acuerdo_sigue_siendo_producto'],
    'donde_esta_cada_artefacto': ['e6_cambio_con_revision_registrada', 'e6_artefacto_ausente',
                                  'e6_cambio_anterior_a_la_estructura', 'e6_candidato_limita_el_listado',
                                  'e6_ruta_absoluta_de_un_registro_anterior'],
    'ruta_canonica_para_producir_artefactos': ['e7_evidencia_en_la_carpeta_del_candidato', 'e7_checkout_de_revision',
                                               'e7_tipo_desconocido'],
    'buscar_en_todo_el_proyecto': ['e8_texto_en_varios_cambios'],
    'listar_con_filtros': ['e9_filtro_de_abiertos'],
    'respetar_lo_existente': ['e10_los_comandos_de_lectura_no_cambian_nada'],
}
PREFIX = 'test_estructura.Estructura.test_'
LIMITES = ('Escenarios e1–e10 en repositorios temporales, Linux. La «otra máquina» de e4 es un clon al que se le quita el original. '
           'No mide que la guía sea clara para quien la lee, ni la fase 2 (mover el estado a .factory/).')


def fuentes():
    files = [ROOT / 'fabrica.py', ROOT / 'pyproject.toml', Path(__file__), ROOT / 'tools/terminal.py',
             *ROOT.glob('oracle_factory/*.py'), *ROOT.glob('tests/*.py'), *ROOT.glob('catalogos/factory_estructura.*.oracle')]
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
    escribir(output / 'hechos.json', {'estructura_caso': rows, 'estructura_corrida': [{'completa': int(ok), 'casos': len(expected)}]})
    escribir(output / 'resultado.json', {'exitoso': ok, 'tests': result.testsRun, 'casos_contrato': len(expected),
             'casos_exactos_sin_omisiones_duplicados_ni_fallas': complete, 'fuentes_estables': stable, 'origen': origen,
             'versiones': {**versions, 'python': sys.version}, 'limites': LIMITES,
             'artefactos_sha256': {name: sha(output / name) for name in ('suite.txt', 'hechos.json')}})
    print(f'Evidencia: {output}; {result.testsRun} pruebas, {len(expected)} casos de contrato; éxito: {ok}.')
    print(LIMITES)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
