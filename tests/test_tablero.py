"""El tablero de comando: escenarios tb1–tb2, el JSON con la CLI de verdad y el panel en node con un `vscode` falso."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_archivo as _archivo  # noqa: E402
import test_vueltas as _vueltas  # noqa: E402

f = _archivo.f
SOURCE = Path(__file__).resolve().parents[1]
PYTHON_CLI = [sys.executable, '-c', 'import sys; from oracle_factory.cli import main; sys.exit(main())']
NODE = shutil.which('node')
EXTENSION = SOURCE / 'editores/vscode'


def cli_json(raiz, *args):
    r = subprocess.run([*PYTHON_CLI, *args], cwd=raiz, capture_output=True, text=True, stdin=subprocess.DEVNULL,
                       env={**os.environ, 'PYTHONPATH': str(SOURCE)})
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


class Tablero(unittest.TestCase):
    setUp, escribe, git, salida = (_archivo.Archivo.setUp, _archivo.Archivo.escribe, _archivo.Archivo.git,
                                   _archivo.Archivo.salida)
    cambio_cerrado = _archivo.Archivo.cambio_cerrado
    candidato_nuevo, pedir = _vueltas.Vueltas.candidato_nuevo, _vueltas.Vueltas.pedir

    def con_dos_revisores(self):
        """Un cambio cerrado y otro abierto cuyo candidato tiene informes de codex y agy con hallazgos."""
        self.cerrado = self.cambio_cerrado()
        shutil.rmtree(self.root / 'examples/notas')  # el ejemplo se trae una sola vez por proyecto
        for catalogo in (self.root / 'catalogos').glob('notas.*'):
            catalogo.unlink()
        self.ident = f.nuevo('Nota abierta', con_ejemplo='notas')
        with self.escribe('1'):
            f.aprobar_spec(self.ident)
        f.importar(self.ident)
        rid = f.leer(self.ident)[1]['requisitos'][0]
        with self.escribe('1'):
            f.medir(self.ident, requisito_id=rid, medidas=['notas.casos_ejecutados', 'notas.resultados'])
        self.git('add', '.')
        self.git('commit', '-qm', 'base')
        self.base = self.git('rev-parse', 'HEAD')
        self.script = Path(self.tmp.name) / 'revisor.py'
        self.script.write_text(_vueltas.REVISOR)
        self.candidato_nuevo()
        self.pedir('codex', ['media', 'Falta validar el título'], ['baja', 'Un nombre poco claro'])
        self.pedir('agy', ['alta', 'El título vacío pasa'], ['baja', '<img src=x onerror=alert(1)>'])
        self.salida()
        return rid

    # --- tb1: el tablero junta todo lo de cada cambio y sus métricas ------------------------------------------------
    def test_tb1_un_cambio_con_revision_y_hallazgos(self):
        rid = self.con_dos_revisores()
        datos = cli_json(self.root, 'tablero', '--json')
        self.assertEqual(datos['esquema'], 'oracle-factory.tablero/1')
        [cambio] = datos['cambios']
        self.assertEqual(cambio['id'], self.ident)
        # Con un medio abierto: corregir (no es un comando) o revisar, que es una decisión de la persona.
        paso, revisar = f.pasos(self.ident)
        self.assertEqual(cambio['proximo_paso'], {'texto': paso, 'comando': None, 'decision_de_la_persona': False})
        self.assertEqual(cambio['alternativas'], [{'texto': revisar, 'comando': revisar, 'decision_de_la_persona': True}])
        # La línea de tiempo, en orden, con quién y cómo.
        linea = cambio['linea_de_tiempo']
        self.assertEqual([e['cuando'] for e in linea], sorted(e['cuando'] for e in linea))
        self.assertEqual(linea[0]['accion'], 'cambio_creado')
        self.assertIn(('spec_aprobada', 'persona'), [(e['accion'], e['tipo_actor']) for e in linea])
        self.assertEqual([e['detalle']['revisor'] for e in linea if e['accion'] == 'revision_pedida'], ['codex', 'agy'])
        # Cada hallazgo con archivo, línea, severidad y revisor.
        hallazgos = {(h['revisor'], h['severidad'], h['titulo']): h for h in cambio['hallazgos']}
        self.assertEqual(set(hallazgos), {('codex', 'media', 'Falta validar el título'), ('codex', 'baja', 'Un nombre poco claro'),
                                          ('agy', 'alta', 'El título vacío pasa'), ('agy', 'baja', '<img src=x onerror=alert(1)>')})
        for h in hallazgos.values():
            self.assertEqual(h['archivo'], 'examples/notas/notas.py')
            self.assertIsInstance(h['linea'], int)
            self.assertEqual(h['estado'], 'abierto')
            self.assertTrue((self.root / h['informe']).is_file())
        # Un riesgo aceptado se ve como aceptado; los informes de un candidato anterior no se mezclan.
        registro = self.root / '.factory/cambios' / self.ident / 'factory.json'
        estado = json.loads(registro.read_text())
        estado['aceptados'] = [{'firma': f.preparacion.firma('examples/notas/notas.py', 'Un nombre poco claro'),
                                'titulo': 'Un nombre poco claro', 'archivo': 'examples/notas/notas.py',
                                'actor': 'Persona fixture', 'motivo': 'fixture', 'fecha': '2026-10-19T00:00:00+00:00',
                                'candidato': cambio['candidato']}]
        registro.write_text(json.dumps(estado, ensure_ascii=False, indent=2) + '\n')
        otro = cli_json(self.root, 'tablero', '--json')['cambios'][0]
        self.assertEqual({h['titulo']: h['estado'] for h in otro['hallazgos']}['Un nombre poco claro'], 'aceptado')
        self.candidato_nuevo()
        self.pedir('codex', ['baja', 'Otro detalle'])
        nuevo = cli_json(self.root, 'tablero', '--json')['cambios'][0]
        self.assertEqual([h['titulo'] for h in nuevo['hallazgos']], ['Otro detalle'])
        self.assertEqual(nuevo['metricas']['vueltas_de_revision'], 2)
        # Los requisitos con sus archivos.
        [req] = cambio['requisitos']
        self.assertEqual(req['id'], rid)
        self.assertEqual(req['archivo'], f'requisitos/{rid}.requisito')
        self.assertEqual([m['archivo'] for m in req['medidas']],
                         ['catalogos/notas.casos_ejecutados.oracle', 'catalogos/notas.resultados.oracle'])
        # Las métricas del cambio.
        m = cambio['metricas']
        self.assertEqual(m['vueltas_de_revision'], 1)
        self.assertEqual(m['hallazgos_por_severidad']['alta'], 1)
        self.assertEqual(m['hallazgos_por_revisor']['codex']['media'], 1)
        self.assertEqual([f_['fase'] for f_ in m['fases']], ['acuerdo', 'medidas'])
        self.assertEqual(m['requisitos'], {'total': 1, 'medidos': 1, 'cumplidos': None})
        self.assertGreater(m['decisiones_por_actor']['persona'], 0)
        # Las del proyecto cuentan los dos cambios: el cerrado también.
        p = datos['proyecto']
        self.assertEqual(p['cambios'], {'abiertos': 1, 'cerrados': 1, 'abandonados': 0})
        self.assertIsNotNone(p['mediana_horas_hasta_cierre'])
        self.assertEqual(p['hallazgos_por_revisor']['agy']['alta'], 1)
        cerrado = json.loads((self.root / '.factory/cambios' / self.cerrado / 'factory.json').read_text())
        decisiones = sum(1 for e in cerrado['eventos'] if e.get('tipo_actor') == 'persona'
                         and e.get('forma') in ('decidio', 'confirmo')) + m['decisiones_por_actor']['persona']
        self.assertEqual(p['decisiones_por_actor']['persona'], decisiones)

    def test_tb1_un_proyecto_sin_cambios(self):
        with tempfile.TemporaryDirectory() as d:
            subprocess.run(['git', 'init', '-q', '-b', 'main'], cwd=d, check=True)
            subprocess.run([*PYTHON_CLI, 'init'], cwd=d, capture_output=True, stdin=subprocess.DEVNULL, check=True,
                           env={**os.environ, 'PYTHONPATH': str(SOURCE)})
            datos = cli_json(d, 'tablero', '--json')
        self.assertEqual(datos['cambios'], [])
        self.assertEqual(datos['proyecto']['cambios'], {'abiertos': 0, 'cerrados': 0, 'abandonados': 0})
        self.assertIsNone(datos['proyecto']['mediana_horas_hasta_cierre'])
        self.assertEqual(datos['proyecto']['hallazgos_por_revisor'], {})

    # --- tb2: el tablero se ve y se usa en VS Code -------------------------------------------------------------------
    @unittest.skipUnless(NODE, 'hace falta node')
    def test_tb2_abrir_el_tablero_y_seguir_un_hallazgo(self):
        rid = self.con_dos_revisores()
        datos = cli_json(self.root, 'tablero', '--json')
        [cambio] = datos['cambios']
        hallazgo = next(h for h in cambio['hallazgos'] if h['revisor'] == 'agy')
        cli = Path(self.tmp.name) / 'oracle-factory'
        cli.write_text(f'#!/bin/sh\nPYTHONPATH={SOURCE} exec {sys.executable} -c "import sys; '
                       f'from oracle_factory.cli import main; sys.exit(main())" "$@"\n')
        cli.chmod(0o755)
        mensajes = [{'tipo': 'abrir', 'archivo': hallazgo['archivo'], 'linea': hallazgo['linea']},
                    {'tipo': 'abrir', 'archivo': f'requisitos/{rid}.requisito', 'linea': None},
                    {'tipo': 'abrir', 'archivo': 'catalogos/notas.resultados.oracle', 'linea': None},
                    {'tipo': 'abrir', 'archivo': '../../etc/passwd', 'linea': 1},  # fuera del proyecto: no se abre
                    {'tipo': 'abrir', 'archivo': '.factory/local/enlace-afuera', 'linea': 1},  # un symlink que apunta afuera, tampoco
                    {'tipo': 'abrir', 'archivo': '.', 'linea': 1},  # ni la carpeta del proyecto
                    {'tipo': 'abrir', 'archivo': 'catalogos', 'linea': 1},  # ni una carpeta de adentro
                    {'tipo': 'terminal', 'comando': 'oracle-factory estado X\ntouch pwned'},  # dos líneas: no se escribe
                    {'tipo': 'terminal', 'comando': cambio['alternativas'][0]['comando']}]
        afuera = Path(self.tmp.name) / 'secreto.txt'
        afuera.write_text('fuera del proyecto\n')
        (self.root / '.factory/local').mkdir(parents=True, exist_ok=True)  # ignorada por git: no cambia el estado
        (self.root / '.factory/local/enlace-afuera').symlink_to(afuera)
        r = subprocess.run([NODE, str(SOURCE / 'tests/tablero_en_node.cjs'), str(EXTENSION), str(self.root),
                            json.dumps(mensajes), str(cli)], capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr)
        salida = json.loads(r.stdout)
        html = salida['html']
        # Lo que te necesita, primero; los hallazgos, los requisitos, la línea de tiempo y las métricas, en la página.
        self.assertLess(html.index(cambio['proximo_paso']['texto']), html.index('<h3>Hallazgos</h3>'))
        for texto in ('El título vacío pasa', 'Falta validar el título', rid.split('.')[-1], 'Línea de tiempo', 'El proyecto',
                      f'data-abrir="{hallazgo["archivo"]}" data-linea="{hallazgo["linea"]}"'):
            self.assertIn(texto, html)
        self.assertIn("default-src 'none'", html)  # sin red
        self.assertIn('&lt;img src=x onerror=alert(1)&gt;', html)  # el título de un hallazgo se escapa
        self.assertNotIn('<img src=x', html)
        self.assertNotIn('<script src', html)
        self.assertEqual(salida['abiertos'], [{'archivo': hallazgo['archivo'], 'linea': hallazgo['linea']},
                                              {'archivo': f'requisitos/{rid}.requisito', 'linea': 1},
                                              {'archivo': 'catalogos/notas.resultados.oracle', 'linea': 1}])
        esperado = cambio['alternativas'][0]['comando'].replace('oracle-factory', str(cli), 1)
        self.assertEqual(salida['terminal'], [{'texto': esperado, 'enter': False, 'cwd': str(self.root)}])
        self.assertEqual(f.leer(self.ident)[1].get('revision'), None)  # el tablero no decidió nada

    @unittest.skipUnless(NODE, 'hace falta node')
    def test_tb2_un_registro_que_cambia(self):
        self.con_dos_revisores()
        registro = self.root / '.factory/cambios' / self.ident / 'factory.json'
        datos = json.loads(registro.read_text())
        datos['titulo'] = 'Un título que cambió'
        cli = Path(self.tmp.name) / 'oracle-factory'
        cli.write_text(f'#!/bin/sh\nPYTHONPATH={SOURCE} exec {sys.executable} -c "import sys; '
                       f'from oracle_factory.cli import main; sys.exit(main())" "$@"\n')
        cli.chmod(0o755)
        cambio = json.dumps({'ruta': str(registro), 'contenido': json.dumps(datos, ensure_ascii=False, indent=2) + '\n'})
        r = subprocess.run([NODE, str(SOURCE / 'tests/tablero_en_node.cjs'), str(EXTENSION), str(self.root), '[]', str(cli)],
                           capture_output=True, text=True, timeout=120, env={**os.environ, 'TABLERO_CAMBIO': cambio})
        self.assertEqual(r.returncode, 0, r.stderr)
        salida = json.loads(r.stdout)
        self.assertIn('Nota abierta', salida['html'])
        self.assertNotIn('Un título que cambió', salida['html'])
        self.assertIn('Un título que cambió', salida['htmlDespues'])
        self.assertEqual(salida['pintadas'], 2)


class Metricas(unittest.TestCase):
    def test_tb1_una_fase_que_vuelve_atras_no_cuenta(self):
        from oracle_factory import tablero
        eventos = [{'accion': 'cambio_creado', 'cuando': '2026-10-01T10:00:00+00:00', 'tipo_actor': 'agente', 'forma': 'decidio'},
                   {'accion': 'spec_aprobada', 'cuando': '2026-10-01T11:00:00+00:00', 'tipo_actor': 'persona', 'forma': 'decidio'},
                   # una propuesta y un registro de revisor no son decisiones
                   {'accion': 'medidas_propuestas', 'cuando': '2026-10-01T11:10:00+00:00', 'tipo_actor': 'agente', 'forma': 'propuso'},
                   {'accion': 'revision_pedida', 'cuando': '2026-10-01T11:20:00+00:00', 'tipo_actor': 'agente', 'forma': 'registro'},
                   {'accion': 'revision_registrada', 'decision': 'aprobar', 'cuando': '2026-10-01T12:00:00+00:00',
                    'tipo_actor': 'persona', 'forma': 'confirmo'},
                   # medidas vueltas a decidir después de la revisión
                   {'accion': 'medidas_confirmadas', 'cuando': '2026-10-01T13:00:00+00:00', 'tipo_actor': 'persona', 'forma': 'confirmo'}]
        m = tablero.metricas_del_cambio({'eventos': eventos, 'requisitos': []}, [], None)
        # Medidas vueltas a decidir después de aprobar la revisión: el tramo de después cuenta como juicio (ahí estaba)
        # y el cambio vuelve a construcción y revisión, que todavía no terminó.
        self.assertEqual([(f['fase'], f['horas']) for f in m['fases']], [('acuerdo', 1.0), ('medidas', 1.0), ('juicio', 1.0)])
        hora = lambda h: f'2026-10-01T{h:02d}:00:00+00:00'
        ida_y_vuelta = [{'accion': 'cambio_creado', 'cuando': hora(0)}, {'accion': 'spec_aprobada', 'cuando': hora(1)},
                        {'accion': 'medidas_confirmadas', 'cuando': hora(2)},
                        {'accion': 'revision_registrada', 'decision': 'aprobar', 'cuando': hora(3)},
                        {'accion': 'medidas_confirmadas', 'cuando': hora(4)},
                        {'accion': 'revision_registrada', 'decision': 'pedir_cambios', 'cuando': hora(5)},
                        {'accion': 'revision_registrada', 'decision': 'aprobar', 'cuando': hora(7)},
                        {'accion': 'oracle_ejecutado', 'codigo': 0, 'cuando': hora(8)}, {'accion': 'cierre', 'cuando': hora(10)}]
        m2 = tablero.metricas_del_cambio({'eventos': ida_y_vuelta, 'requisitos': []}, [], None)
        self.assertEqual([(f['fase'], f['horas']) for f in m2['fases']],
                         [('acuerdo', 1.0), ('medidas', 1.0), ('construcción y revisión', 4.0), ('juicio', 2.0), ('cierre', 2.0)])
        self.assertEqual(m2['horas_hasta_cierre'], 10.0)
        # Un reloj que va hacia atrás (un registro copiado de otra máquina) no resta tiempo, y un cambio_creado repetido
        # no corre el comienzo.
        raro = ida_y_vuelta[:1] + [{'accion': 'cambio_creado', 'cuando': hora(3)}, {'accion': 'spec_aprobada', 'cuando': hora(1)}] \
            + ida_y_vuelta[2:]
        m3 = tablero.metricas_del_cambio({'eventos': raro, 'requisitos': []}, [], None)
        self.assertEqual([(f['fase'], f['horas']) for f in m3['fases']][:2], [('acuerdo', 3.0), ('medidas', 1.0)])
        self.assertEqual(m3['horas_hasta_cierre'], 10.0)
        self.assertEqual(m['decisiones_por_actor'], {'persona': 3, 'agente': 1, 'sin_identificar': 0})
        self.assertEqual(m['vueltas_de_revision'], 1)  # revisada a mano, sin revisores pedidos: una vuelta
        # Un registro viejo con una fecha sin zona horaria: esa fase no tiene duración, y el tablero no se cae.
        viejo = [dict(eventos[0], cuando='2026-10-01T10:00:00')] + eventos[1:]
        m = tablero.metricas_del_cambio({'eventos': viejo, 'requisitos': []}, [], None)
        self.assertEqual([f['fase'] for f in m['fases']], ['medidas', 'juicio'])
        # Los requisitos cumplidos salen del juicio sólo si sigue vigente.
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / 'informe.txt').write_text('✓ dom.uno  ok\n✗ dom.dos  falla\n')
            self.assertEqual(tablero._cumplidos(Path(d), {'informe': 'informe.txt', 'vigente': True}, ['dom.uno', 'dom.dos']), 1)
            self.assertEqual(tablero._cumplidos(Path(d), {'informe': 'informe.txt'}, ['dom.uno', 'dom.dos']), 1)  # cerrado
            self.assertIsNone(tablero._cumplidos(Path(d), {'informe': 'informe.txt', 'vigente': False}, ['dom.uno']))
        # Un informe pedido otra vez en el mismo candidato reemplaza al anterior de ese revisor: no se cuenta dos veces.
        with tempfile.TemporaryDirectory() as d:
            raiz = Path(d)
            for candidato, nombre, n in (('c1', 'codex-1', 1), ('c2', 'codex-1', 2), ('c2', 'codex-2', 3), ('c2', 'agy-1', 1)):
                ruta = raiz / 'candidatos' / candidato / 'revision' / f'{nombre}.json'
                ruta.parent.mkdir(parents=True, exist_ok=True)
                ruta.write_text(json.dumps({'findings': [{'severity': 'media', 'title': f'h{i}'} for i in range(n)]}))
            vistos = [(i['candidato'], i['revisor'], len(i['hallazgos'])) for i in tablero.informes(raiz, raiz)]
            self.assertEqual(sorted(vistos), [('c1', 'codex', 1), ('c2', 'agy', 1), ('c2', 'codex', 3)])

    def test_tb1_que_es_una_decision_de_la_persona(self):
        from oracle_factory import tablero
        decide = {texto: tablero._paso(texto)['decision_de_la_persona'] for texto in (
            'oracle-factory medir X --listar', 'oracle-factory medir X --confirmar', 'oracle-factory revisar X',
            'oracle-factory juzgar X', 'corregí los hallazgos; después: oracle-factory pedir-revision X')}
        self.assertEqual(decide, {'oracle-factory medir X --listar': False, 'oracle-factory medir X --confirmar': True,
                                  'oracle-factory revisar X': True, 'oracle-factory juzgar X': False,
                                  'corregí los hallazgos; después: oracle-factory pedir-revision X': False})

if __name__ == '__main__':
    unittest.main()
