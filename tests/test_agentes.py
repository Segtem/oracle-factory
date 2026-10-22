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
    def test_ag2_un_agente_intenta_las_decisiones_de_una_persona(self):
        self.correr('init')
        r = self.correr('nuevo', '--con-ejemplo', 'notas', 'Una nota', agente='agente-x')
        self.assertEqual(r.returncode, 0, r.stderr)
        [ident] = [p.name for p in (self.root / 'openspec/changes').iterdir() if p.is_dir()]
        # Lo que necesita cada decisión para llegar a decidirse: una persona aprueba e importa, toma el cambio, el agente
        # propone medidas, dos ramas dejaron algo sin unir y hay una nota de personas.
        self.assertEqual(self.correr('aprobar-spec', ident).returncode, 0)
        self.assertEqual(self.correr('importar', ident, agente='agente-x').returncode, 0)
        self.assertEqual(self.correr('tomar', ident).returncode, 0)
        registro = json.loads((self.root / '.factory/cambios' / ident / 'factory.json').read_text())
        [rid] = registro['requisitos']
        self.assertEqual(self.correr('medir', ident, '--requisito', rid, '--medida', 'notas.casos_ejecutados',
                                     '--quitar-sin-medir', agente='agente-x').returncode, 0)
        ruta = self.root / '.factory/cambios' / ident / 'factory.json'
        registro = json.loads(ruta.read_text())
        registro['pendientes_de_union'] = [{'campo': 'fase', 'camino': ['fase'], 'nuestro': registro['fase'], 'suyo': 'otra'}]
        ruta.write_text(json.dumps(registro))
        (self.root / 'kb/notas').mkdir(parents=True)
        (self.root / 'kb/notas/guia.md').write_text('---\nfuentes: [README.md]\n---\n# Guía\n\nAlgo.\n')
        (self.root / 'README.md').write_text('x\n')
        antes = json.loads(ruta.read_text())['eventos']
        ordenes = {'aprobar-spec ID': ['aprobar-spec', ident], 'medir ID --confirmar': ['medir', ident, '--confirmar'],
                   'revisar ID': ['revisar', ident], 'cerrar ID': ['cerrar', ident], 'abandonar ID': ['abandonar', ident],
                   'modo ID MODO': ['modo', ident, 'autonomo'], 'soltar ID': ['soltar', ident],
                   'decidir-union ID CAMPO nuestro|suyo': ['decidir-union', ident, 'fase', 'suyo'],
                   'kb revisada NOTA': ['kb', 'revisada', 'kb/notas/guia.md']}
        self.assertEqual(set(ordenes), {c for c, _ in agentes.PERSONA})  # la prueba recorre toda la lista de la guía
        for comando, args in ordenes.items():
            r = self.correr(*args, agente='agente-x')
            salida = r.stdout + r.stderr
            self.assertTrue(r.returncode != 0 or 'Propuesta' in salida or 'no cambié nada' in salida, (comando, salida[-300:]))
        nuevos = json.loads(ruta.read_text())['eventos'][len(antes):]
        self.assertEqual([e for e in nuevos if e.get('actor') == 'agente-x' and e['accion'] in DECISIONES], [])
        self.assertEqual(json.loads(ruta.read_text())['responsable']['persona'], 'Ana')
        # Y cada comando que la guía da a un agente acepta --agente.
        for comando, _ in agentes.AGENTE:
            r = self.correr(comando.split()[0], '--help', agente='agente-x')
            self.assertEqual(r.returncode, 0, comando)
        r = self.correr('mensaje', ident, 'hola', agente='agente-x')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(ruta.read_text())['eventos'][-1]['actor'], 'agente-x')


if __name__ == '__main__':
    unittest.main()
