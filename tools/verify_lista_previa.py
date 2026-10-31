"""Evidencia de la lista previa a la revisión: escenarios lp1–lp3 con nombre exacto, y la trazabilidad de esos casos."""
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

CAMBIO = '20261031-220741-vts-listaprevia'
CONTRACTS = {
    'pedir_revision_muestra_la_lista_previa_sin_bloquear': [
        'PedirRevision.test_lp1_la_lista_sale_antes_de_anunciar_al_revisor',
        'PedirRevision.test_lp1_el_revisor_se_lanza_igual_y_deja_su_informe',
        'PedirRevision.test_lp1_la_lista_se_muestra_aunque_el_revisor_falle',
        'PedirRevision.test_lp1_el_pedido_que_recibe_el_revisor_no_cambia'],
    'la_lista_previa_tiene_una_sola_fuente': [
        'FuenteUnica.test_lp2_la_lista_tiene_una_pregunta_por_clase_y_la_regla_de_la_clase',
        'FuenteUnica.test_lp2_cada_pregunta_esta_en_el_documento_con_el_mismo_texto',
        'FuenteUnica.test_lp2_una_pregunta_nueva_sin_documento_se_nombra',
        'FuenteUnica.test_lp2_varias_preguntas_faltantes_se_nombran_todas_y_un_documento_vacio_falla',
        'FuenteUnica.test_lp2_el_texto_para_mostrar_trae_cada_pregunta_numerada_y_es_estable',
        'FuenteUnica.test_lp2_el_documento_no_promete_que_bloquea'],
    'la_guia_para_agentes_nombra_la_lista_previa': [
        'GuiaDeLaLista.test_lp3_la_guia_generada_nombra_la_lista',
        'GuiaDeLaLista.test_lp3_una_guia_vieja_sin_la_mencion_se_detecta'],
}
PREFIX = 'test_lista_previa.'
LIMITES = ('Escenarios lp1–lp3 con un revisor de prueba, el repositorio temporal y la CLI de verdad. Comprueban que la lista se muestra, '
           'que no cambia el pedido y que el documento y la guía la nombran; no miden si la lista reduce las rondas de revisión: eso se mide '
           'después, sobre los cambios que vengan.')


def fuentes(salida=None):
    # Todo lo versionado o nuevo del producto (código, pruebas, datos de referencia, catálogos, docs); sin los registros generados.
    nombres = subprocess.run(['git', '-C', str(ROOT), 'ls-files', '-z', '--cached', '--others', '--exclude-standard'],
                             text=True, capture_output=True, check=True).stdout.split('\0')  # -z: nombres no ASCII sin comillas
    elegidos = [ROOT / n for n in nombres if n and not n.startswith(('.factory/', 'kb/', 'tareas/'))
                and (ROOT / n).is_file() and not (salida and (ROOT / n).is_relative_to(salida))]  # la evidencia no es producto
    head = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True, capture_output=True, check=True).stdout.strip()
    return {'head': head, 'sha256': {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(elegidos)}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida', type=Path, required=True, help='carpeta nueva de evidencia')
    args = parser.parse_args(argv)
    versions = {p: metadata.version(p) for p in ('oracle-metalenguaje', 'oracle-task', 'oracle-clue')}
    output = args.salida.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=False)
    origen = fuentes(output)
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'))
    result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=Resultado).run(suite)
    expected = [PREFIX + name for names in CONTRACTS.values() for name in names]
    observed = {name: count for name, count in result.cantidad.items() if name.startswith(PREFIX)}
    complete = observed == Counter(expected) and all(result.observados.get(name, 1) == 0 for name in expected)
    rows = [{'requisito': suffix, 'caso': name, 'codigo': result.observados.get(PREFIX + name, 1)}
            for suffix, names in CONTRACTS.items() for name in names]
    (output / 'suite.txt').write_text(stream.getvalue(), encoding='utf-8')
    # Los mismos casos, otra vez y trazados: requisito → casos → líneas ejecutadas (oracle-factory trazabilidad lo cruza).
    ids = {r.rsplit('.', 1)[-1]: r for r in json.loads((ROOT / '.factory/cambios' / CAMBIO / 'factory.json').read_text())['requisitos']}
    traza = trazabilidad.trazar(ROOT, {ids[s]: [PREFIX + n for n in names] for s, names in CONTRACTS.items()})
    escribir(output / 'trazabilidad.json', traza)
    trazada = all(c.get('resultado') == 'ok' for c in traza['casos'].values()) and len(traza['casos']) == len(expected)
    stable = fuentes(output) == origen  # después de la segunda corrida, la trazada: ahí también tienen que seguir quietas
    ok = result.wasSuccessful() and complete and stable and trazada
    escribir(output / 'hechos.json', {'lista_previa_caso': rows, 'lista_previa_corrida': [{'completa': int(ok), 'casos': len(expected)}]})
    escribir(output / 'resultado.json', {'exitoso': ok, 'tests': result.testsRun, 'casos_contrato': len(expected),
             'casos_exactos_sin_omisiones_duplicados_ni_fallas': complete, 'fuentes_estables': stable, 'origen': origen,
             'versiones': {**versions, 'python': sys.version}, 'limites': LIMITES,
             'artefactos_sha256': {name: sha(output / name) for name in ('suite.txt', 'hechos.json', 'trazabilidad.json')}})
    print(f'Evidencia: {output}; {result.testsRun} pruebas, {len(expected)} casos de contrato; éxito: {ok}.')
    print(LIMITES)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
