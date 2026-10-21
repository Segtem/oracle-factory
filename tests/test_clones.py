"""Dos clones sin tropiezos: escenarios cl1–cl3, con git de verdad, un repositorio central y procesos simultáneos."""
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_archivo as _archivo  # noqa: E402

f = _archivo.f

SOURCE = Path(__file__).resolve().parents[1]
CLI = [sys.executable, '-c', 'import sys; from oracle_factory.cli import main; sys.exit(main())']


class Clones(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.env = {**os.environ, 'PYTHONPATH': str(SOURCE), 'GIT_CEILING_DIRECTORIES': str(base),
                    'GIT_AUTHOR_NAME': 'P', 'GIT_AUTHOR_EMAIL': 'p@x.invalid', 'GIT_COMMITTER_NAME': 'P',
                    'GIT_COMMITTER_EMAIL': 'p@x.invalid'}
        semilla = base / 'semilla'
        semilla.mkdir()
        self.git(semilla, 'init', '-q', '-b', 'main')
        self.cli(semilla, 'init')
        self.git(semilla, 'add', '-A')
        self.git(semilla, 'commit', '-qm', 'init')
        self.central = base / 'central.git'
        subprocess.run(['git', 'clone', '-q', '--bare', str(semilla), str(self.central)], check=True, capture_output=True)

    def git(self, donde, *args):
        r = subprocess.run(['git', *args], cwd=donde, env=self.env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip()

    def cli(self, donde, *args, ok=True):
        r = subprocess.run([*CLI, '--agente', 'agente-prueba', *args], cwd=donde, env=self.env, capture_output=True,
                           text=True, stdin=subprocess.DEVNULL)
        if ok:
            self.assertEqual(r.returncode, 0, r.stderr)
        return r

    def clon(self, nombre):
        destino = Path(self.tmp.name) / nombre
        subprocess.run(['git', 'clone', '-q', str(self.central), str(destino)], check=True, capture_output=True)
        return destino

    def cambios(self, donde):
        return sorted(p.name for p in (donde / 'openspec/changes').iterdir() if p.is_dir())

    # --- cl1: un clon recién hecho puede trabajar ---------------------------------------------------------------------
    def test_cl1_la_segunda_persona_clona_el_proyecto(self):
        beto = self.clon('beto')
        for carpeta in ('tareas', 'catalogos', 'openspec/changes', '.factory/cambios'):
            self.assertTrue((beto / carpeta).is_dir(), carpeta)
        self.cli(beto, 'nuevo', '--capacidad', 'calc', '--sufijo', 'primero', 'El primer cambio de Beto')
        self.assertEqual(len(self.cambios(beto)), 1)
        # Un clon de un proyecto viejo, sin tareas/ ni openspec/changes/: nuevo las crea.
        viejo = self.clon('viejo')
        for carpeta in ('tareas', 'openspec/changes', '.factory/cambios'):
            shutil.rmtree(viejo / carpeta)
        self.cli(viejo, 'nuevo', '--capacidad', 'calc', '--sufijo', 'otro', 'Un cambio en un proyecto viejo')
        self.assertEqual(len(self.cambios(viejo)), 1)

    # --- cl2: dos clones no generan el mismo ID -----------------------------------------------------------------------
    def test_cl2_dos_cambios_en_el_mismo_segundo(self):
        ana, beto = self.clon('ana'), self.clon('beto')
        for donde, rama in ((ana, 'tarea/a'), (beto, 'tarea/b')):
            self.git(donde, 'checkout', '-q', '-b', rama)
        with ThreadPoolExecutor(2) as pool:
            for f in [pool.submit(self.cli, d, 'nuevo', '--capacidad', 'calc', '--sufijo', 'igual', 'El mismo nombre')
                      for d in (ana, beto)]:
                f.result()
        [id_a], [id_b] = self.cambios(ana), self.cambios(beto)
        self.assertNotEqual(id_a, id_b)
        self.assertTrue(id_a.endswith('-igual') and id_b.endswith('-igual'))
        for donde, rama in ((ana, 'tarea/a'), (beto, 'tarea/b')):
            self.git(donde, 'add', '-A')
            self.git(donde, 'commit', '-qm', rama)
            self.git(donde, 'push', '-q', 'origin', rama)
        self.git(ana, 'checkout', '-q', 'main')
        self.git(ana, 'fetch', '-q', 'origin')
        for rama in ('origin/tarea/a', 'origin/tarea/b'):
            self.git(ana, 'merge', '-q', '--no-ff', '-m', f'Integrar {rama}', rama)  # sin conflicto
        self.assertEqual(self.cambios(ana), sorted([id_a, id_b]))

    # --- cl3: escribir a la vez no obliga a repetir ------------------------------------------------------------------
    def test_cl3_doce_mensajes_a_la_vez(self):
        ana = self.clon('ana')
        self.cli(ana, 'nuevo', '--capacidad', 'calc', '--sufijo', 'charla', 'Un registro concurrido')
        [ident] = self.cambios(ana)
        with ThreadPoolExecutor(12) as pool:
            codigos = [f.result().returncode for f in [pool.submit(self.cli, ana, 'mensaje', ident, f'mensaje {i}', ok=False)
                                                       for i in range(12)]]
        self.assertEqual(codigos, [0] * 12)
        registro = json.loads((ana / '.factory/cambios' / ident / 'factory.json').read_text())
        textos = sorted(e['texto'] for e in registro['eventos'] if e['accion'] == 'mensaje')
        self.assertEqual(textos, sorted(f'mensaje {i}' for i in range(12)))

    # --- cl1: una regla del proyecto que ignora una carpeta de Factory se avisa -----------------------------------
    def test_cl1_una_carpeta_ignorada_se_avisa(self):
        otro = Path(self.tmp.name) / 'otro'
        otro.mkdir()
        self.git(otro, 'init', '-q', '-b', 'main')
        (otro / '.gitignore').write_text('tareas/\n')
        r = self.cli(otro, 'init')
        self.assertIn('Aviso: Git ignora tareas/ (.gitignore:1:tareas/)', r.stderr)
        self.assertNotIn('Git ignora catalogos', r.stderr)


class Reintento(unittest.TestCase):
    """cl3, determinista: otro proceso escribe el registro justo antes de que tomar, soltar o mensaje lo guarden."""
    setUp, git = _archivo.Archivo.setUp, _archivo.Archivo.git

    def como(self, persona):
        subprocess.run(['git', 'config', 'user.name', persona], cwd=self.root, check=True)

    def a_destiempo(self, ident, veces=1):
        """guardar, pero antes otro proceso agrega un mensaje al registro (las primeras `veces`)."""
        real, llamadas = f.guardar, []

        def guardar(carpeta, estado, *args, **kwargs):
            if len(llamadas) < veces:
                llamadas.append(1)
                ruta = self.root / '.factory/cambios' / ident / 'factory.json'
                otro = json.loads(ruta.read_text())
                otro['eventos'].append({'accion': 'mensaje', 'texto': f'de otro {len(llamadas)}', 'cuando': f.ahora()})
                ruta.write_text(json.dumps(otro, ensure_ascii=False, indent=2) + '\n')
            return real(carpeta, estado, *args, **kwargs)
        return patch.object(f, 'guardar', guardar)

    def test_cl3_tomar_y_soltar_reintentan(self):
        f.AGENTE = 'claude-code'
        try:
            ident = f.nuevo('Concurrido', capacidad='calc', sufijo='uno')
        finally:
            f.AGENTE = None
        self.como('Ana')
        with self.a_destiempo(ident), patch.object(f.time, 'sleep'):
            f.tomar(ident)
        with self.a_destiempo(ident), patch.object(f.time, 'sleep'):
            f.soltar(ident)
        eventos = f.leer(ident)[1]['eventos']
        self.assertEqual([e.get('texto') for e in eventos if e['accion'] == 'mensaje'], ['de otro 1', 'de otro 1'])
        self.assertEqual([e['accion'] for e in eventos][-1], 'soltado')
        self.assertIsNone(f.leer(ident)[1]['responsable'])
        # Vuelve a comprobar sus reglas: si mientras tanto lo tomó otra persona, Beto no lo pisa.
        self.como('Beto')
        real = f.guardar

        def lo_toma_ana(carpeta, estado, *args, **kwargs):
            ruta = self.root / '.factory/cambios' / ident / 'factory.json'
            otro = json.loads(ruta.read_text())
            otro['responsable'] = {'persona': 'Ana', 'desde': f.ahora(), 'con': []}
            ruta.write_text(json.dumps(otro, ensure_ascii=False, indent=2) + '\n')
            return real(carpeta, estado, *args, **kwargs)
        with patch.object(f, 'guardar', lo_toma_ana), patch.object(f.time, 'sleep'), \
                self.assertRaisesRegex(f.FactoryError, 'lo tiene Ana'):
            f.tomar(ident)
        # Si nunca logra escribir, falla claro y no guarda nada.
        with self.a_destiempo(ident, veces=99), patch.object(f.time, 'sleep'), \
                self.assertRaisesRegex(f.FactoryError, 'cambió 20 veces .*no guardé nada'):
            f.mensaje(ident, 'nunca')
        self.assertNotIn('nunca', [e.get('texto') for e in f.leer(ident)[1]['eventos']])


if __name__ == '__main__':
    unittest.main()
