"""Unir al integrar: escenarios un1–un3, con git de verdad, un repositorio central y dos clones; más la unión pura."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE))
from oracle_factory import unir as unir_mod  # noqa: E402
from tools.terminal import en_terminal  # noqa: E402

CLI = [sys.executable, '-c', 'import sys; from oracle_factory.cli import main; sys.exit(main())']


class Unir(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.env = {**os.environ, 'PYTHONPATH': str(SOURCE), 'GIT_CEILING_DIRECTORIES': str(base),
                    'GIT_AUTHOR_EMAIL': 'p@x.invalid', 'GIT_COMMITTER_EMAIL': 'p@x.invalid'}
        semilla = base / 'semilla'
        semilla.mkdir()
        self.git(semilla, 'init', '-q', '-b', 'main')
        self.git(semilla, 'config', 'user.name', 'Semilla')
        self.cli(semilla, 'init')
        self.git(semilla, 'add', '-A')
        self.git(semilla, 'commit', '-qm', 'init')
        self.cli(semilla, 'nuevo', '--capacidad', 'calc', '--sufijo', 'comun', 'Un cambio de los dos')
        self.cli(semilla, 'kb')
        self.git(semilla, 'add', '-A')
        self.git(semilla, 'commit', '-qm', 'el cambio')
        [self.ident] = [p.name for p in (semilla / 'openspec/changes').iterdir() if p.is_dir()]
        self.central = base / 'central.git'
        subprocess.run(['git', 'clone', '-q', '--bare', str(semilla), str(self.central)], check=True, capture_output=True)
        self.ana, self.beto = self.clon('Ana'), self.clon('Beto')

    def git(self, donde, *args):
        r = subprocess.run(['git', *args], cwd=donde, env=self.env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        return r.stdout.strip()

    def cli(self, donde, *args):
        r = subprocess.run([*CLI, '--agente', 'agente-prueba', *args], cwd=donde, env=self.env, capture_output=True,
                           text=True, stdin=subprocess.DEVNULL)
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        return r.stdout

    def persona(self, donde, *args):
        r = en_terminal([*CLI, *args], cwd=donde, env=self.env)
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        return r.stdout

    def clon(self, nombre):
        destino = Path(self.tmp.name) / nombre.lower()
        subprocess.run(['git', 'clone', '-q', str(self.central), str(destino)], check=True, capture_output=True)
        self.git(destino, 'config', 'user.name', nombre)
        self.cli(destino, 'hooks')
        return destino

    def registro(self, donde):
        return json.loads((donde / '.factory/cambios' / self.ident / 'factory.json').read_text())

    def en_rama(self, donde, rama, *orden, persona=False):
        """En una rama propia, hace la orden, commitea y sube."""
        self.git(donde, 'checkout', '-q', '-b', rama)
        (self.persona if persona else self.cli)(donde, *orden)
        self.git(donde, 'add', '-A')
        self.git(donde, 'commit', '-qm', rama)
        self.git(donde, 'push', '-q', 'origin', rama)

    def integrar_las_dos(self):
        """Ana integra su rama y la de Beto en main; ninguna de las dos chocan."""
        self.git(self.ana, 'checkout', '-q', 'main')
        self.git(self.ana, 'fetch', '-q', 'origin')
        for rama in ('origin/tarea/ana', 'origin/tarea/beto'):
            self.git(self.ana, 'merge', '-q', '--no-ff', '-m', f'Integrar {rama}', rama)
        self.assertEqual(self.git(self.ana, 'status', '--porcelain'), '')

    # --- un1: el registro editado en dos ramas se une --------------------------------------------------------------
    def test_un1_mensajes_en_dos_ramas(self):
        self.en_rama(self.ana, 'tarea/ana', 'mensaje', self.ident, 'de Ana')
        self.en_rama(self.beto, 'tarea/beto', 'mensaje', self.ident, 'de Beto')
        self.integrar_las_dos()
        eventos = self.registro(self.ana)['eventos']
        self.assertEqual(sorted(e['texto'] for e in eventos if e['accion'] == 'mensaje'), ['de Ana', 'de Beto'])
        self.assertEqual([e['cuando'] for e in eventos], sorted(e['cuando'] for e in eventos))
        self.assertNotIn('pendientes_de_union', self.registro(self.ana))

    # --- un2: lo que las dos ramas decidieron distinto lo decide una persona ---------------------------------------
    def test_un2_dos_personas_lo_toman(self):
        self.en_rama(self.ana, 'tarea/ana', 'tomar', self.ident, persona=True)
        self.en_rama(self.beto, 'tarea/beto', 'tomar', self.ident, persona=True)
        self.integrar_las_dos()
        registro = self.registro(self.ana)
        self.assertEqual(registro['responsable']['persona'], 'Ana')  # el de la rama que integra, sin elegir
        self.assertIn('responsable.persona', [p['campo'] for p in registro['pendientes_de_union']])
        self.assertIn('union_con_decisiones', [e['accion'] for e in registro['eventos']])
        estado = self.cli(self.ana, 'estado', self.ident)
        self.assertIn('Beto', estado)
        self.assertIn(f'tomar {self.ident} --relevo', estado)
        avisos = json.loads(self.cli(self.ana, 'estado', self.ident, '--json'))['avisos']
        self.assertTrue(any('responsable.persona' in x and 'Beto' in x for x in avisos), avisos)
        self.persona(self.ana, 'tomar', self.ident)
        self.assertNotIn('pendientes_de_union', self.registro(self.ana))
        self.assertNotIn('Factory no eligió', self.cli(self.ana, 'estado', self.ident))

    # --- un3: lo generado no choca y queda al día ------------------------------------------------------------------
    def test_un3_lo_generado_se_rehace(self):
        self.en_rama(self.ana, 'tarea/ana', 'nuevo', '--capacidad', 'calc', '--sufijo', 'ana', 'El de Ana')
        self.en_rama(self.beto, 'tarea/beto', 'nuevo', '--capacidad', 'calc', '--sufijo', 'beto', 'El de Beto')
        self.integrar_las_dos()
        resumen = (self.ana / '.factory/resumen.md').read_text()
        self.assertIn('El de Ana', resumen)
        self.assertIn('El de Beto', resumen)
        self.assertIn('Rehacer lo generado', self.git(self.ana, 'log', '-1', '--format=%s'))
        self.assertEqual(len(self.git(self.ana, 'log', '-1', '--format=%P').split()), 1)
        self.cli(self.ana, 'resumen', '--verificar')
        self.cli(self.ana, 'kb', '--verificar')
        self.assertEqual(len(list((self.ana / 'kb/cambios').glob('*.md'))), 3)


class UnirPuro(unittest.TestCase):
    def test_lo_de_una_sola_rama_se_toma(self):
        base = {'fase': 'spec', 'titulo': 'T', 'eventos': [{'accion': 'creado', 'cuando': '1'}]}
        nuestro = {**base, 'modo': 'pair', 'eventos': base['eventos'] + [{'accion': 'mensaje', 'cuando': '3'}], 'fase': 'impl'}
        suyo = {**base, 'titulo': 'Otro', 'eventos': base['eventos'] + [{'accion': 'mensaje', 'cuando': '2'}], 'fase': 'rev'}
        unido = unir_mod.unir(base, nuestro, suyo)
        self.assertEqual(unido['titulo'], 'Otro')
        self.assertEqual(unido['modo'], 'pair')
        self.assertEqual(unido['fase'], 'impl')
        self.assertEqual([e['cuando'] for e in unido['eventos']], ['1', '2', '3'])
        self.assertNotIn('pendientes_de_union', unido)

    def test_lo_que_las_dos_cambiaron_distinto_queda_pendiente(self):
        unido = unir_mod.unir({'cierre': None}, {'cierre': {'por': 'Ana'}}, {'cierre': {'por': 'Beto'}})
        self.assertEqual(unido['cierre'], {'por': 'Ana'})
        self.assertEqual(unido['pendientes_de_union'], [{'campo': 'cierre.por', 'nuestro': 'Ana', 'suyo': 'Beto'}])
        self.assertEqual(unir_mod.resueltos_por('cierre'), ('cierre',))
        self.assertIn('cerrar X', unir_mod.como_resolver('cierre.por', 'X'))


if __name__ == '__main__':
    unittest.main()
