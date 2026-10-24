"""Evidencia de pq1–pq6, mutaciones y evaluación documental/generativa real; exige modelo explícito."""
from collections import Counter
from importlib import metadata
import argparse
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.verify_review_guided import Resultado, escribir, sha
from tools.mutar_preguntar import MUTACIONES, fuentes as fuentes_mutaciones
from oracle_factory import cli, rag, generacion, trazabilidad

CAMBIO = '20261024-020022-0b3-preguntar'
CONTRACTS = {
    'preguntar_elabora_respuestas_a_preguntas_abiertas_del_proyecto': ['Preguntar.test_pq1_respuesta_abierta_con_fuentes_y_herramientas'],
    'la_elaboracion_usa_herramientas_acotadas_y_un_modelo_explicito': ['Preguntar.test_pq2_herramientas_configuracion_fallos_y_limites'],
    'preguntar_cuenta_y_lista_cambios_desde_el_registro_vigente': ['Preguntar.test_pq3_cuenta_lista_cero_y_actualiza_registro'],
    'la_recuperacion_documental_expone_si_hay_respaldo_suficiente': ['Preguntar.test_pq4_sin_respaldo_ambiguedad_y_filtros'],
    'la_respuesta_conserva_su_significado_en_cli_mcp_y_vs_code': ['Preguntar.test_pq5_cli_mcp_y_editor_conservan_respuesta'],
    'la_evaluacion_distingue_exactitud_relevancia_y_abstencion': ['Preguntar.test_pq6_evaluacion_por_grupos_detecta_errores'],
}
PREFIX = 'test_preguntar.'
LIMITES = ('Contratos pq1–pq6 en proyectos aislados y transporte HTTP simulado; esos casos no acreditan calidad generativa. '
           'La evaluación real conserva las 22 preguntas documentales y agrega seis consultas de registro, cuatro abiertas '
           'y tres negativas. Las citas se verifican por pertenencia textual y la respuesta por conceptos mínimos; esto no '
           'certifica toda inferencia semántica ni comprensión universal. La revisión independiente debe inspeccionar el detalle.')


def fuentes():
    archivos = [ROOT / 'pyproject.toml', Path(__file__), ROOT / 'tools/mutar_preguntar.py',
                *ROOT.glob('oracle_factory/*.py'), *ROOT.glob('tests/*.py'), *ROOT.glob('tests/datos/preguntar-*.json'),
                ROOT / 'tests/tablero_en_node.cjs', ROOT / 'README.md', *ROOT.glob('docs/**/*.md'),
                *ROOT.glob('editores/vscode/*.js'), *ROOT.glob('catalogos/factory_preguntar.*.oracle'),
                *ROOT.glob('kb/**/*.md'), ROOT / 'kb/preguntas-de-oro.json', ROOT / '.factory/config.json',
                *ROOT.glob('.factory/cambios/*/factory.json'), *ROOT.glob('openspec/**/*.md')]
    return {'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'sha256': {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(set(archivos))}}


def casos_registro():
    """Oráculo de referencia independiente: contar las filas de listar, no llamar al resolvedor de preguntas."""
    filas = []
    for filtro, opciones in [('cerrados', ['--cerrados']), ('abiertos', ['--abiertos']),
                             ('abandonados', ['--fase', 'abandonada']), ('todos', [])]:
        p = subprocess.run([sys.executable, '-c', 'from oracle_factory.cli import main; raise SystemExit(main())',
                            '--agente', 'codex', 'listar', *opciones],
                           cwd=ROOT, text=True, capture_output=True, check=True, stdin=subprocess.DEVNULL)
        ids = [linea.split()[0] for linea in p.stdout.splitlines() if linea.split() and cli.ID_RE.fullmatch(linea.split()[0])]
        n = len(ids)
        pregunta = '¿Cuántas tareas cerradas hay?' if filtro == 'cerrados' else (
            '¿Cuántos cambios hay en total?' if filtro == 'todos' else f'¿Cuántos cambios {filtro} hay?')
        filas.append({'id': 'pq-registro-' + filtro, 'grupo': 'registro', 'pregunta': pregunta, 'valor': n, 'ids': ids,
                      'referencia': {'comando': ['listar', *opciones], 'salida': p.stdout}})
    filas.extend([{**filas[0], 'id': 'pq-registro-variante', 'pregunta': 'Cuantas tareas cerradas hay?'},
                  {**filas[0], 'id': 'pq-registro-lista', 'pregunta': 'Listá tareas cerradas', 'requiere_listado': True}])
    return filas


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida', type=Path, required=True)
    parser.add_argument('--mutaciones', type=Path, required=True)
    parser.add_argument('--modelo', required=True, help='modelo generativo elegido para esta medición')
    parser.add_argument('--proveedor', choices=('ollama', 'openai'), default='ollama')
    parser.add_argument('--url', help='URL explícita; obligatoria para proveedor openai')
    parser.add_argument('--clave-env', help='nombre de la variable, nunca la clave')
    args = parser.parse_args(argv)
    conf = {'proveedor': args.proveedor, 'modelo': args.modelo}
    if args.url:
        conf['url'] = args.url
    if args.clave_env:
        conf['clave_env'] = args.clave_env
    class Proyecto:
        """Configuración explícita de la corrida: consulta los datos reales y no sustituye herramientas o respuestas."""
        def __getattr__(self, nombre):
            return getattr(cli, nombre)
        def config_proyecto(self):
            config = cli.config_proyecto()
            return {**config, 'rag': {**config['rag'], 'generacion': conf}}
    proyecto = Proyecto()
    cli.ROOT, cli.CHANGES = ROOT, ROOT / 'openspec/changes'
    config = generacion.configuracion(proyecto)
    mutaciones = json.loads(args.mutaciones.read_text())
    esperadas = {m[0] for m in MUTACIONES}
    filas_mutacion = mutaciones.get('mutaciones', [])
    validas = (mutaciones.get('fuentes') == fuentes_mutaciones() and len(filas_mutacion) == len(esperadas)
               and {m['id'] for m in filas_mutacion} == esperadas and all(m['detectada'] for m in filas_mutacion))
    if not validas:
        parser.error('Faltan mutaciones detectadas o no corresponden a las fuentes actuales; volvé a correr mutar_preguntar.py.')
    salida = args.salida.expanduser().resolve()
    cli.ruta_segura(salida)
    salida.mkdir(parents=True, exist_ok=False)
    origen = fuentes()
    escribir(salida / 'mutaciones.json', mutaciones)
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'))
    resultado = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=Resultado).run(suite)
    esperados = [PREFIX + n for nombres in CONTRACTS.values() for n in nombres]
    observados = {n: c for n, c in resultado.cantidad.items() if n in esperados}
    completos = observados == Counter(esperados) and all(resultado.observados.get(n, 1) == 0 for n in esperados)
    (salida / 'suite.txt').write_text(stream.getvalue())
    ids = {r.rsplit('.', 1)[-1]: r for r in json.loads((ROOT / '.factory/cambios' / CAMBIO / 'factory.json').read_text())['requisitos']}
    escribir(salida / 'trazabilidad.json', trazabilidad.trazar(ROOT, {ids[s]: [PREFIX + n for n in nombres]
                                                                    for s, nombres in CONTRACTS.items()}))
    casos = json.loads((ROOT / 'tests/datos/preguntar-abiertas.json').read_text()) + casos_registro()
    escribir(salida / 'casos.json', casos)
    rag.evaluar(proyecto, salida / 'oro', casos=salida / 'casos.json')
    oro = json.loads((salida / 'oro/hechos.json').read_text())
    grupos = {g['grupo']: g for g in oro['preguntar_grupo']}
    calidad = (oro['rag_corrida'][0]['preguntas'] == 22 and oro['rag_corrida'][0]['modo'] == 'hibrido'
               and oro['rag_corrida'][0]['modelo'] == 'qwen3-embedding:0.6b'
               and oro['rag_corrida'][0]['aciertos'] >= 18
               and grupos.get('documental', {}).get('aciertos', 0) >= 18
               and set(grupos) == {'documental', 'registro', 'generativa', 'abstencion'}
               and all(grupos[g]['errores'] == 0 for g in ('registro', 'generativa', 'abstencion'))
               and all(p['modelo_generativo'] == config['modelo'] and not p['simulado']
                       for p in oro['preguntar_pregunta'] if p['grupo'] == 'generativa'))
    estables = fuentes() == origen
    ok = resultado.wasSuccessful() and completos and estables and calidad and validas
    filas = [{'requisito': s, 'caso': n, 'codigo': resultado.observados.get(PREFIX + n, 1)}
             for s, nombres in CONTRACTS.items() for n in nombres]
    escribir(salida / 'hechos.json', {'preguntar_caso': filas, 'preguntar_suite': [{'completa': int(ok), 'casos': len(esperados)}],
                                     'preguntar_mutacion': [{'id': m['id'], 'detectada': int(m['detectada'])} for m in filas_mutacion], **oro})
    artefactos = ('suite.txt', 'mutaciones.json', 'trazabilidad.json', 'casos.json', 'hechos.json', 'oro/hechos.json', 'oro/detalle.json')
    escribir(salida / 'resultado.json', {'exitoso': ok, 'tests': resultado.testsRun, 'casos_contrato': len(esperados),
             'casos_exactos_sin_omisiones_duplicados_ni_fallas': completos, 'fuentes_estables': estables, 'origen': origen,
             'generacion': config, 'calidad': oro['rag_corrida'][0], 'grupos': oro['preguntar_grupo'], 'limites': LIMITES,
             'versiones': {**{p: metadata.version(p) for p in ('oracle-metalenguaje', 'oracle-task', 'oracle-clue')}, 'python': sys.version},
             'artefactos_sha256': {n: sha(salida / n) for n in artefactos}})
    print(f'Evidencia: {salida}; {resultado.testsRun} pruebas; éxito: {ok}; calidad: {calidad}; fuentes estables: {estables}.')
    print(LIMITES)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
