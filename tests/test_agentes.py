"""La guía para agentes: escenarios ag1 (se genera y no se desactualiza) y ag2 (dice lo que hace la CLI), en proyectos
temporales con la CLI de verdad; las órdenes de un agente, en una terminal (el peor caso: no basta con no tenerla)."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE))
from oracle_factory import agentes, modos  # noqa: E402
from tools.terminal import en_terminal  # noqa: E402

CLI = [sys.executable, '-c', 'import sys; from oracle_factory.cli import main; sys.exit(main())']
DECISIONES = {'spec_aprobada', 'medidas_confirmadas', 'medidas_elegidas', 'revision_registrada', 'cierre', 'abandono',
              'modo_cambiado', 'soltado', 'union_decidida'}


class Agentes(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'producto'
        self.root.mkdir()
        self.env = {**os.environ, 'PYTHONPATH': str(SOURCE), 'GIT_CEILING_DIRECTORIES': self.tmp.name}
        self.git('init', '-q', '-b', 'main')
        self.git('config', 'user.name', 'Ana')
        self.git('config', 'user.email', 'ana@x.invalid')

    def git(self, *args):
        return subprocess.run(['git', *args], cwd=self.root, env=self.env, check=True, capture_output=True, text=True).stdout

    def correr(self, *args, agente=None, entrada='1\n1\n1\n'):
        return en_terminal([*CLI, *(['--agente', agente] if agente else []), *args], cwd=self.root, env=self.env, entrada=entrada)

    # --- ag1: la guía se genera y no se desactualiza ---------------------------------------------------------------
    def test_ag1_marcas_rotas(self):
        self.correr('init')
        for roto in (f'# Propio\n{agentes.INICIO}\nsin cerrar\n', f'{agentes.INICIO}\na\n{agentes.FIN}\n{agentes.INICIO}\nb\n{agentes.FIN}\n',
                     f'{agentes.FIN}\nal revés\n{agentes.INICIO}\n'):
            (self.root / 'AGENTS.md').write_text(roto)
            for args in (('agentes',), ('agentes', '--verificar')):
                r = self.correr(*args)
                self.assertNotEqual(r.returncode, 0)
                self.assertIn('dejá un solo par', r.stdout + r.stderr)
            self.assertEqual((self.root / 'AGENTS.md').read_text(), roto)  # no se tocó nada

    def test_ag1_un_proyecto_con_su_propio_agents_md(self):
        # init ya la deja.
        self.correr('init')
        self.assertEqual(self.correr('agentes', '--verificar').returncode, 0)
        propio = '# Mi proyecto\n\nNo toquen la carpeta vendor/.\n'
        (self.root / 'AGENTS.md').write_text(propio)
        (self.root / 'CLAUDE.md').write_text('# Para Claude\n\nRespondé en español.\n')
        self.assertNotEqual(self.correr('agentes', '--verificar').returncode, 0)
        self.assertEqual(self.correr('agentes').returncode, 0)
        texto = (self.root / 'AGENTS.md').read_text()
        self.assertTrue(texto.startswith(propio))
        self.assertIn('| **confirmacion** (el de este proyecto) | propone | propone | propone | no puede |', texto)
        for comando, _ in agentes.PERSONA + agentes.AGENTE:
            self.assertIn(comando, texto)
        self.assertIn('mcp', texto)
        claude = (self.root / 'CLAUDE.md').read_text()
        self.assertTrue(claude.startswith('# Para Claude\n\nRespondé en español.\n') and '@AGENTS.md' in claude.splitlines())
        # Otra vez: no cambia nada ni repite el bloque o la línea.
        self.assertEqual(self.correr('agentes').returncode, 0)
        self.assertEqual(((self.root / 'AGENTS.md').read_text(), (self.root / 'CLAUDE.md').read_text()), (texto, claude))
        # Cambia el modo por defecto: la guía quedó vieja hasta que se vuelve a generar, y lo de afuera sigue igual.
        config = self.root / '.factory/config.json'
        config.write_text(json.dumps({**json.loads(config.read_text()), 'modo_por_defecto': 'autonomo'}))
        r = self.correr('agentes', '--verificar')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('no está al día en AGENTS.md', r.stdout + r.stderr)
        self.assertEqual((self.root / 'AGENTS.md').read_text(), texto)  # verificar no escribe
        self.correr('agentes')
        nuevo = (self.root / 'AGENTS.md').read_text()
        self.assertIn('| **autonomo** (el de este proyecto) |', nuevo)
        self.assertEqual(nuevo.count(agentes.INICIO), 1)
        self.assertTrue(nuevo.startswith(propio))
        # La tabla es la de modos.via_agente.
        for modo in modos.MODOS:
            self.assertEqual(modos.via_agente(modo, 'cierre', ['funcional']) == 'decide', f'| **{modo}** (el de este proyecto) | decide | decide | decide | decide |' in nuevo
                             or f'| {modo} | decide | decide | decide | decide |' in nuevo)

    # --- ag2: la guía dice lo que hace la CLI ----------------------------------------------------------------------
    def cambio(self, modo):
        """Un cambio del ejemplo de notas en el modo dado (la persona lo baja si hace falta)."""
        ejemplo = not (self.root / 'examples/notas').exists()  # el ejemplo se trae una vez; los demás, con su spec
        r = self.correr('nuevo', *(['--con-ejemplo', 'notas'] if ejemplo else ['--capacidad', 'notas', '--sufijo', modo]),
                        f'Una nota {modo}', agente='agente-x')
        self.assertEqual(r.returncode, 0, r.stderr)
        ident = max((p for p in (self.root / 'openspec/changes').iterdir() if p.is_dir()), key=lambda p: p.stat().st_mtime).name
        carpeta = self.root / 'openspec/changes' / ident
        if not ejemplo:
            (carpeta / 'proposal.md').write_text(f'# Una nota {modo}\n\n## Why\n\nPara la prueba.\n')
            (carpeta / 'specs/notas/spec.md').write_text(
                f'# Capability: notas\n\n## ADDED Requirements\n\n### Requirement: titulo en {modo}\nTipo: funcional\n'
                'The system SHALL reject empty titles.\n\n#### Scenario: vacío\n- WHEN el título está vacío\n- THEN no se guarda\n')
        if modo != 'confirmacion':
            self.assertEqual(self.correr('modo', ident, modo).returncode, 0)
        return ident, self.root / '.factory/cambios' / ident / 'factory.json'

    def eventos(self, ruta):
        return json.loads(ruta.read_text())['eventos']

    def esperado(self, r, ruta, antes, via, decidida, propuesta):
        """Lo que pasó al correr una decisión como agente, contra lo que dice la tabla de la guía."""
        nuevos = [e['accion'] for e in self.eventos(ruta)[antes:] if e.get('actor') == 'agente-x']
        if via == 'decide':
            self.assertIn(decidida, nuevos, (r.stdout + r.stderr)[-300:])
        elif via == 'propone':
            self.assertIn(propuesta, nuevos, (r.stdout + r.stderr)[-300:])
            self.assertNotIn(decidida, nuevos)
        else:
            self.assertNotEqual(r.returncode, 0)
            self.assertIn('sin --agente', r.stdout + r.stderr)
            self.assertNotIn(decidida, nuevos)

    def test_ag2_las_decisiones_segun_el_modo(self):
        self.correr('init')
        self.assertEqual([d for d, _, _ in agentes.DECISIONES], list(modos.DECISIONES))  # la guía nombra las cuatro
        for modo in modos.MODOS:
            ident, ruta = self.cambio(modo)
            # La spec.
            antes = len(self.eventos(ruta))
            r = self.correr('aprobar-spec', ident, agente='agente-x')
            self.esperado(r, ruta, antes, modos.via_agente(modo, 'spec', ['funcional']), 'spec_aprobada', 'spec_propuesta')
            if not json.loads(ruta.read_text()).get('spec_aprobada'):
                self.assertEqual(self.correr('aprobar-spec', ident).returncode, 0)
            self.assertEqual(self.correr('importar', ident, agente='agente-x').returncode, 0)
            [rid] = json.loads(ruta.read_text())['requisitos']
            # Las medidas.
            antes = len(self.eventos(ruta))
            r = self.correr('medir', ident, '--requisito', rid, '--medida', 'notas.casos_ejecutados', '--medida',
                            'notas.resultados', '--quitar-sin-medir', agente='agente-x')
            self.esperado(r, ruta, antes, modos.via_agente(modo, 'medidas', ['funcional']), 'medidas_elegidas', 'medidas_propuestas')
            if not (json.loads(ruta.read_text()).get('medidas') or {}).get(rid):
                self.assertEqual(self.correr('medir', ident, '--requisito', rid, '--medida', 'notas.casos_ejecutados',
                                             '--medida', 'notas.resultados', '--quitar-sin-medir').returncode, 0)
            # La revisión, sobre el candidato commiteado.
            self.git('add', '-A')
            self.git('commit', '-qm', f'producto {modo}')
            informe = self.root / 'tareas' / ident / 'revision.md'
            informe.write_text('Revisión de la prueba: sin hallazgos.\n')
            antes = len(self.eventos(ruta))
            r = self.correr('revision', ident, '--informe', str(informe), '--revisor', 'agente-x', '--decision', 'aprobar',
                            '--hallazgos-abiertos', '0', agente='agente-x')
            self.esperado(r, ruta, antes, modos.via_agente(modo, 'revision', ['funcional']), 'revision_registrada',
                          'revision_propuesta')
            # El cierre: donde un agente no puede, se niega por ser agente, antes de mirar lo que falta.
            if modos.via_agente(modo, 'cierre', []) == 'rechaza':
                antes = len(self.eventos(ruta))
                self.esperado(self.correr('cerrar', ident, agente='agente-x'), ruta, antes, 'rechaza', 'cierre', None)

    def test_ag2_un_agente_intenta_lo_que_es_solo_de_una_persona(self):
        self.correr('init')
        (self.root / 'kb/notas').mkdir(parents=True)
        (self.root / 'kb/notas/guia.md').write_text('---\nfuentes: [README.md]\n---\n# Guía\n\nAlgo.\n')
        (self.root / 'README.md').write_text('x\n')
        for modo in ('confirmacion', 'autonomo'):
            ident, ruta = self.cambio(modo)
            self.assertEqual(self.correr('aprobar-spec', ident).returncode, 0)
            self.assertEqual(self.correr('importar', ident, agente='agente-x').returncode, 0)
            self.assertEqual(self.correr('tomar', ident).returncode, 0)
            [rid] = json.loads(ruta.read_text())['requisitos']
            self.correr('medir', ident, '--requisito', rid, '--medida', 'notas.casos_ejecutados', '--quitar-sin-medir',
                        agente='agente-x')  # en confirmación queda propuesta, para que haya algo que confirmar
            registro = json.loads(ruta.read_text())
            registro['pendientes_de_union'] = [{'campo': 'fase', 'camino': ['fase'], 'nuestro': registro['fase'], 'suyo': 'otra'}]
            ruta.write_text(json.dumps(registro))
            antes = len(self.eventos(ruta))
            ordenes = {'medir ID --confirmar': ['medir', ident, '--confirmar'], 'revisar ID': ['revisar', ident],
                       'abandonar ID': ['abandonar', ident], 'modo ID MODO': ['modo', ident, 'autonomo'],
                       'soltar ID': ['soltar', ident], 'decidir-union ID CAMPO nuestro|suyo': ['decidir-union', ident, 'fase', 'suyo'],
                       'kb revisada NOTA': ['kb', 'revisada', 'kb/notas/guia.md']}
            self.assertEqual(set(ordenes), {c for c, _ in agentes.PERSONA})  # la prueba recorre toda la lista de la guía
            for comando, args in ordenes.items():
                if modo == 'autonomo' and comando == 'modo ID MODO':
                    continue  # en autónomo no hay intervención que bajar
                r = self.correr(*args, agente='agente-x')
                salida = r.stdout + r.stderr
                self.assertTrue(r.returncode != 0 or 'Propuesta' in salida or 'propuesta' in salida, (modo, comando, salida[-300:]))
            nuevos = self.eventos(ruta)[antes:]
            self.assertEqual([e for e in nuevos if e.get('actor') == 'agente-x' and e['accion'] in DECISIONES], [], modo)
            self.assertEqual(json.loads(ruta.read_text())['responsable']['persona'], 'Ana')
            self.assertTrue(json.loads(ruta.read_text()).get('pendientes_de_union'))

    def test_ag2_los_comandos_de_un_agente_aceptan_agente(self):
        self.correr('init')
        ident, ruta = self.cambio('confirmacion')
        self.assertEqual(self.correr('aprobar-spec', ident).returncode, 0)
        self.git('add', '-A')
        self.git('commit', '-qm', 'base')
        ordenes = {'nuevo --capacidad C --sufijo S "TÍTULO"': ['nuevo', '--capacidad', 'otra', '--sufijo', 'otro', 'Otro'],
                   'importar ID': ['importar', ident], 'pedir-revision ID --a REVISOR': ['pedir-revision', ident, '--a', 'nadie'],
                   'revision-preparar ID': ['revision-preparar', ident],
                   'revisar ID --decision aprobar|cambios --motivo M': ['revisar', ident, '--decision', 'aprobar', '--motivo', 'm'],
                   'juzgar ID': ['juzgar', ident], 'mensaje ID "TEXTO"': ['mensaje', ident, 'hola'], 'tomar ID': ['tomar', ident],
                   'abandonar ID --motivo M': ['abandonar', ident, '--motivo', 'ya no hace falta']}
        self.assertEqual(set(ordenes), {c for c, _ in agentes.AGENTE})
        for comando, args in ordenes.items():
            r = self.correr(*args, agente='agente-x')
            # Puede faltarle algo del flujo (un revisor configurado, evidencia), pero nunca negarse por ser un agente.
            self.assertNotIn('sin --agente', r.stdout + r.stderr, comando)
            self.assertNotIn('unrecognized arguments', r.stdout + r.stderr, comando)
        acciones = {e['accion'] for e in self.eventos(ruta) if e.get('actor') == 'agente-x'}
        self.assertTrue({'requisitos_importados', 'mensaje', 'agente_sumado', 'abandono_propuesto'} <= acciones, acciones)

if __name__ == '__main__':
    unittest.main()
