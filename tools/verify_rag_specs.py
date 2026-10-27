"""Evidencia del contrato de rag-specs: escenarios rs1–rs4 con nombre exacto, y la trazabilidad de esos mismos casos."""
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

CAMBIO = '20261026-225825-rn5-rag-specs'
CONTRACTS = {
    'contar_y_listar_specs': ['rs1_cuantas_specs_hay_da_dos_numeros_y_cita_los_archivos', 'rs1_cuales_son_lista_capacidad_estado_y_ruta', 'rs1_con_una_sola_spec_vigente_va_en_singular', 'rs1_sin_ninguna_spec_dice_cero', 'rs1_funciona_por_la_cli', 'rs4_cuales_especificaciones_y_capacidades_tambien_entran', 'rs4_un_enlace_simbolico_no_cuenta_ni_se_cita', 'rs4_vigentes_y_abiertas_se_responden_con_las_dos_cantidades_rotuladas', 'rs4_la_fuente_trae_criterio_cita_y_huella_del_inventario'],
    'filtro_de_specs_no_admitido': ['rs2_un_filtro_no_admitido_se_rechaza_sin_pasajes', 'rs2_una_compuesta_o_de_otro_tema_no_es_de_este_camino', 'rs4_otros_filtros_de_estado_se_rechazan', 'rs4_abandonadas_y_fechas_con_operando_se_rechazan'],
    'las_demas_preguntas_no_cambian': ['rs3_cambios_abiertos_sigue_igual', 'rs3_una_pregunta_que_nombra_cambios_y_specs_no_cambia_de_camino', 'rs4_una_pregunta_que_explica_no_es_de_contar_ni_listar', 'rs4_lo_compuesto_o_con_cambios_va_al_modelo_aunque_traiga_un_filtro', 'rs4_una_pregunta_de_contenido_con_cuales_o_cuantas_no_se_intercepta'],
}
PREFIX = 'test_rag_specs.RagSpecs.test_'
LIMITES = ('Escenarios rs1–rs4 en repositorios temporales, Linux, con Oracle 0.38.2 real y sin modelo generativo ni embeddings: el '
           'conteo y la lista de specs vigentes y de cambios abiertos, los filtros no admitidos y la no regresión de cambios. No cubre '
           'preguntas compuestas con un modelo generativo configurado.')


def fuentes():
    files = [ROOT / 'fabrica.py', ROOT / 'pyproject.toml', Path(__file__), *ROOT.glob('oracle_factory/*.py'),
             *ROOT.glob('tests/*.py'), *ROOT.glob('catalogos/factory_rag_specs.*.oracle')]
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
    escribir(output / 'hechos.json', {'specs_caso': rows, 'specs_corrida': [{'completa': int(ok), 'casos': len(expected)}]})
    escribir(output / 'resultado.json', {'exitoso': ok, 'tests': result.testsRun, 'casos_contrato': len(expected),
             'casos_exactos_sin_omisiones_duplicados_ni_fallas': complete, 'fuentes_estables': stable, 'origen': origen,
             'versiones': {**versions, 'python': sys.version}, 'limites': LIMITES,
             'artefactos_sha256': {name: sha(output / name) for name in ('suite.txt', 'hechos.json', 'trazabilidad.json')}})
    print(f'Evidencia: {output}; {result.testsRun} pruebas, {len(expected)} casos de contrato; éxito: {ok}.')
    print(LIMITES)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
