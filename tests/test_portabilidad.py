"""Portabilidad entre máquinas: escenarios p1–p7 de la spec, con un clon en otra ruta como segunda máquina."""
import contextlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from oracle_factory import cli as f

GIT = ['git', '-c', 'user.name=Persona fixture', '-c', 'user.email=fixture@example.invalid', '-c', 'core.hooksPath=/dev/null']


class Portabilidad(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'producto'
        self.root.mkdir()
        for name, value in [('ROOT', self.root), ('CHANGES', self.root / 'openspec/changes'), ('AGENTE', None)]:
            p = patch.object(f, name, value); p.start(); self.addCleanup(p.stop)
        p = patch.object(f, 'terminal_interactiva', return_value=True); p.start(); self.addCleanup(p.stop)
        self.stdout = io.StringIO()
        p = contextlib.redirect_stdout(self.stdout); p.__enter__(); self.addCleanup(p.__exit__, None, None, None)
        f.inicializar()

    # --- ayudantes -----------------------------------------------------------------
    def escribe(self, frase):
        return patch('builtins.input', return_value=frase)

    def git(self, *args, cwd=None):
        return subprocess.run([*GIT, *args], cwd=cwd or self.root, check=True, capture_output=True, text=True).stdout.strip()

    def estado(self, ident):
        return f.leer(ident)[1]

    def cambio_medido(self):
        ident = f.nuevo('Nota', con_ejemplo='notas')
        with self.escribe(f'APROBAR ESPECIFICACION {ident}'):
            f.aprobar_spec(ident)
        f.importar(ident)
        rid = self.estado(ident)['requisitos'][0]
        f.medir(ident, requisito_id=rid, medidas=['notas.casos_ejecutados', 'notas.resultados'], quitar_sin_medir=True)
        subprocess.run(['git', 'init', '-q', '-b', 'main'], cwd=self.root, check=True)
        self.git('add', '.')
        self.git('commit', '-qm', 'producto fixture')
        informe = self.root / 'tareas' / ident / 'revision.md'
        informe.write_text('Fixture de revisión; no es una revisión real.\n')
        with self.escribe(f'REGISTRAR REVISION {ident}'):
            f.revisar(ident, informe, 'Persona fixture', 'aprobar', 0)
        return ident

    def sensor(self, destino):
        destino.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([sys.executable, 'examples/notas/sensor.py', '--salida', destino], cwd=self.root, check=True,
                       capture_output=True)
        return destino

    def cambio_juzgado(self):
        ident = self.cambio_medido()
        f.juzgar(ident, self.sensor(self.root / 'tareas' / ident / 'hechos.json'))
        self.git('add', '.')
        self.git('commit', '-qm', 'registros')
        return ident

    def clon(self, nombre='clon-otra-ruta'):
        destino = Path(self.tmp.name) / 'otra' / 'maquina' / nombre
        destino.parent.mkdir(parents=True)
        subprocess.run(['git', 'clone', '-q', self.root, destino], check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Otra persona'], cwd=destino, check=True)
        subprocess.run(['git', 'config', 'user.email', 'otra@example.invalid'], cwd=destino, check=True)
        # En otra máquina la ruta de la primera no existe: sin esto, una ruta absoluta del original seguiría resolviendo.
        self.root.rename(self.root.with_name('producto-que-la-otra-maquina-no-tiene'))
        return destino

    @contextlib.contextmanager
    def en(self, raiz):
        with patch.object(f, 'ROOT', raiz), patch.object(f, 'CHANGES', raiz / 'openspec/changes'):
            yield

    def juzgar_avisando(self, ident, hechos):
        avisos = io.StringIO()
        with contextlib.redirect_stderr(avisos):
            f.juzgar(ident, hechos)
        return avisos.getvalue()

    # --- p1: hechos con ruta relativa -----------------------------------------------------
    def test_p1_hechos_dentro_del_proyecto(self):
        ident = self.cambio_juzgado()
        self.assertEqual(self.estado(ident)['oracle']['hechos'], f'tareas/{ident}/hechos.json')

    def test_p1_clon_en_otra_ruta(self):
        ident = self.cambio_juzgado()
        clon = self.clon()
        with self.en(clon):
            carpeta, estado = f.leer(ident)
            self.assertEqual(f.pendientes_actuales(carpeta, estado), [])  # antes: «hechos ausente»

    # --- p2: advertir cuando los hechos no viajan ------------------------------------------
    def test_p2_hechos_ignorados_por_git(self):
        ident = self.cambio_medido()
        hechos = self.sensor(self.root / '.factory-demo' / 'hechos.json')  # carpeta que inicializar() ignora
        avisos = self.juzgar_avisando(ident, hechos)
        self.assertIn('ignorados por Git', avisos)
        self.assertEqual(self.estado(ident)['fase'], 'oracle_verde')  # se advierte y se sigue

    def test_p2_hechos_fuera_del_proyecto(self):
        ident = self.cambio_medido()
        hechos = self.sensor(Path(self.tmp.name) / 'fuera' / 'hechos.json')
        avisos = self.juzgar_avisando(ident, hechos)
        self.assertIn('fuera del proyecto', avisos)
        registrado = self.estado(ident)['oracle']['hechos']
        self.assertTrue(registrado.startswith('/') and registrado.endswith('hechos.json'))

    # --- p3: fuente relativa --------------------------------------------------------------
    def test_p3_fuente_relativa(self):
        ident = self.cambio_medido()
        rid = self.estado(ident)['requisitos'][0]
        texto = (self.root / 'requisitos' / f'{rid}.requisito').read_text(encoding='utf-8')
        self.assertNotIn(str(self.root), texto)
        self.assertIn(f'fuente "openspec/changes/{ident}/', texto)

    def test_p3_fuente_con_comillas_en_la_ruta_se_reescribe_o_avisa(self):
        raiz = Path('/tmp/pro"ducto')  # Oracle escapa la comilla: fuente "/tmp/pro\"ducto/openspec/x#y"
        ruta = Path(self.tmp.name) / 'r.requisito'
        ruta.write_text('requisito x.y:\n    fuente "/tmp/pro\\"ducto/openspec/x.md#t"\n', encoding='utf-8')
        with patch.object(f, 'ROOT', raiz):
            f.fuente_relativa(ruta)
        self.assertEqual(ruta.read_text(encoding='utf-8'), 'requisito x.y:\n    fuente "openspec/x.md#t"\n')
        ajena = Path(self.tmp.name) / 's.requisito'  # una ruta que no es la de este proyecto: se avisa
        ajena.write_text('requisito x.y:\n    fuente "/otra/ruta/x.md#t"\n', encoding='utf-8')
        avisos = io.StringIO()
        with patch.object(f, 'ROOT', raiz), contextlib.redirect_stderr(avisos):
            f.fuente_relativa(ajena)
        self.assertIn('no pude hacer relativa', avisos.getvalue())

    # --- p4: el pendiente explica cómo recuperarse ----------------------------------------
    def test_p4_pendiente_explica_como_recuperarse(self):
        ident = self.cambio_juzgado()
        (self.root / 'tareas' / ident / 'hechos.json').unlink()
        carpeta, estado = f.leer(ident)
        pendiente = ' '.join(f.pendientes_actuales(carpeta, estado))
        self.assertIn(f'tareas/{ident}/hechos.json', pendiente)
        self.assertIn('juzgando de nuevo', pendiente)

    # --- p5: se cierra desde otra máquina -----------------------------------------------------
    def test_p5_cierre_desde_un_clon_en_otra_ruta(self):
        ident = self.cambio_juzgado()
        clon = self.clon()
        with self.en(clon):
            with self.escribe(f'CERRAR {ident}'):
                f.cerrar(ident)
            cierre = f.leer(ident)[1]
        self.assertEqual(cierre['fase'], 'cerrada')
        self.assertEqual((cierre['cierre']['actor'], cierre['cierre']['tipo_actor']), ('Otra persona', 'persona'))

    # --- p6: sin rutas privadas en lo versionado ---------------------------------------------------
    def test_p6_sin_rutas_privadas_en_lo_versionado(self):
        self.cambio_juzgado()
        archivos = self.git('ls-files', '--cached', '--others', '--exclude-standard').splitlines()
        con_ruta = []
        for nombre in archivos:
            try:
                if str(self.root) in (self.root / nombre).read_text(encoding='utf-8'):
                    con_ruta.append(nombre)
            except (UnicodeDecodeError, OSError):
                continue
        self.assertEqual(con_ruta, [])

    def test_p6_los_requisitos_de_este_repositorio_no_llevan_rutas_privadas(self):
        propios = sorted((Path(__file__).resolve().parents[1] / 'requisitos').glob('portabilidad_*.requisito'))
        self.assertTrue(propios)
        self.assertEqual([p.name for p in propios if re.search(r'(?m)^\s*fuente "/', p.read_text(encoding='utf-8'))], [])

    # --- p7: registros existentes -------------------------------------------------------------------
    def test_p7_registro_anterior_con_ruta_absoluta(self):
        ident = self.cambio_juzgado()
        ruta = self.root / 'openspec/changes' / ident / 'factory.json'
        estado = json.loads(ruta.read_text())
        estado['oracle']['hechos'] = str(self.root / 'tareas' / ident / 'hechos.json')  # como lo escribía la versión anterior
        ruta.write_text(json.dumps(estado, ensure_ascii=False, indent=2) + '\n')
        antes = ruta.read_bytes()
        carpeta, estado = f.leer(ident)
        self.assertEqual(f.pendientes_actuales(carpeta, estado), [])  # se sigue verificando
        f.mostrar(ident)
        self.assertEqual(ruta.read_bytes(), antes)  # y no se reescribe


if __name__ == '__main__':
    unittest.main()
