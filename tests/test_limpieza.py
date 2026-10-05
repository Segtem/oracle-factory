"""Limpieza de rutas privadas: escenarios l1–l4 de la spec, sobre proyectos temporales."""
import contextlib
import hashlib
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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import limpiar_rutas as lim  # noqa: E402

GIT = ['git', '-c', 'user.name=Persona fixture', '-c', 'user.email=fixture@example.invalid', '-c', 'core.hooksPath=/dev/null']
OTRA = '/home/otra-persona/Dev/proyecto'


class Limpieza(unittest.TestCase):
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
        self.ident = self.cambio_antiguo()

    # --- ayudantes -----------------------------------------------------------------
    def escribe(self, frase):
        return patch('builtins.input', return_value=frase)

    def git(self, *args):
        return subprocess.run([*GIT, *args], cwd=self.root, check=True, capture_output=True, text=True).stdout.strip()

    def cambio_antiguo(self):
        """Un cambio juzgado como los de antes de la portabilidad: fuente y hechos con la ruta de la máquina del autor."""
        ident = f.nuevo('Nota', con_ejemplo='notas')
        with self.escribe(f'APROBAR ESPECIFICACION {ident}'):
            f.aprobar_spec(ident)
        f.importar(ident)
        carpeta, estado = f.leer(ident)
        rid = estado['requisitos'][0]
        f.medir(ident, requisito_id=rid, medidas=['notas.casos_ejecutados', 'notas.resultados'], quitar_sin_medir=True)
        subprocess.run(['git', 'init', '-q', '-b', 'main'], cwd=self.root, check=True)
        hechos = self.root / 'tareas' / ident / 'hechos.json'
        hechos.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([sys.executable, 'examples/notas/sensor.py', '--salida', hechos], cwd=self.root, check=True, capture_output=True)
        self.git('add', '.')
        self.git('commit', '-qm', 'producto fixture')
        f.juzgar(ident, hechos)
        # el informe de tareas/ guarda la ruta histórica: evidencia que no se reescribe
        (self.root / 'tareas' / ident / 'informe-viejo.txt').write_text(f'corrida en {OTRA}/tareas/{ident}\n')
        archivo = self.root / 'requisitos' / f'{rid}.requisito'
        texto = archivo.read_text(encoding='utf-8')
        archivo.write_text(re.sub(r'fuente "([^"]*)"', lambda m: f'fuente "{OTRA}/{m.group(1)}"', texto), encoding='utf-8')
        carpeta, estado = f.leer(ident)
        estado['medidas'][rid]['sha256'] = hashlib.sha256(archivo.read_bytes()).hexdigest()
        estado['oracle']['hechos'] = f'{OTRA}/{estado["oracle"]["hechos"]}'
        f.guardar(carpeta, estado)
        previos = carpeta / 'requisitos-previos'
        previos.mkdir(exist_ok=True)
        (self.root / 'tareas' / ident / 'requisito-historico.txt').write_text(
            f'requisito h.h:\n    texto "t"\n    fuente "{OTRA}/openspec/changes/{ident}/specs/notas/spec.md#a"\n    sin_medir\n')
        (previos / 'viejo.requisito.txt').write_text(f'requisito x.y:\n    texto "t"\n    fuente "{OTRA}/openspec/changes/{ident}/specs/notas/spec.md#a"\n    sin_medir\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'registros con ruta absoluta')
        return ident

    def limpiar(self, *args):
        salida, errores = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(errores):
            codigo = lim.main(['--proyecto', str(self.root), '--agente', 'claude-code', *args])
        return codigo

    def requisito(self):
        return next((self.root / 'requisitos').glob('*.requisito'))

    def estado(self):
        return f.leer(self.ident)[1]

    def lineas_de_estado(self):
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            f.mostrar(self.ident)
        return salida.getvalue().replace(str(self.root), '<raiz>')

    def tareas(self):
        return {str(p.relative_to(self.root)): p.read_bytes() for p in sorted((self.root / 'tareas').rglob('*')) if p.is_file()}

    # --- l1: los registros no llevan la ruta ----------------------------------------
    def test_l1_requisito_con_fuente_absoluta(self):
        self.assertIn(OTRA, self.requisito().read_text())
        self.assertEqual(self.limpiar(), 0)
        fuente = re.search(r'fuente "([^"]*)"', self.requisito().read_text()).group(1)
        self.assertEqual(fuente, f'openspec/changes/{self.ident}/specs/notas/spec.md#' + fuente.split('#')[1])
        self.assertTrue((self.root / fuente.split('#')[0]).is_file(), 'la fuente relativa apunta al mismo documento')

    def test_l1_requisitos_previos(self):
        self.limpiar()
        previo = self.root / 'openspec/changes' / self.ident / 'requisitos-previos' / 'viejo.requisito.txt'
        self.assertNotIn(OTRA, previo.read_text())
        self.assertIn(f'fuente "openspec/changes/{self.ident}/specs/notas/spec.md#a"', previo.read_text())

    def test_l1_hechos_absolutos_en_el_registro(self):
        self.assertTrue(self.estado()['oracle']['hechos'].startswith(OTRA))
        self.limpiar()
        hechos = self.estado()['oracle']['hechos']
        self.assertEqual(hechos, f'tareas/{self.ident}/hechos.json')
        self.assertEqual(hashlib.sha256((self.root / hechos).read_bytes()).hexdigest(), self.estado()['oracle']['hechos_sha256'])

    def test_l1_directorios_ambiguos_y_formas_que_no_se_pueden_reescribir(self):
        rel = 'openspec/changes/20260101-000000-x/specs/a/spec.md#b'
        for absoluta in (f'/home/tareas/Dev/p/{rel}', f'/srv/openspec/proy/{rel}', f'/tmp/oracle/{rel}'):
            self.assertEqual(lim.relativa(absoluta), rel, absoluta)
        archivo = self.requisito()
        texto = archivo.read_text(encoding='utf-8')
        for fuente in ('/sin/identificador/spec.md#a', f'{OTRA}/openspec/changes/{self.ident}/specs/no-existe.md#a'):
            archivo.write_text(re.sub(r'fuente "[^"]*"', lambda m: f'fuente "{fuente}"', texto), encoding='utf-8')
            self.assertEqual(self.limpiar(), 1, fuente)  # se avisa, no se calla
            self.assertIn(fuente, archivo.read_text(encoding='utf-8'))  # y no se inventa una ruta
            self.assertEqual(self.limpiar('--verificar'), 1)
            self.assertIn(archivo.name, [Path(x).name for x in lim.restos(self.root)])  # el verificador la ve

    def test_l1_fin_de_linea_windows_y_comillas_escapadas(self):
        archivo = self.requisito()
        crlf = archivo.read_text(encoding='utf-8').replace('\n', '\r\n')
        archivo.write_bytes(crlf.encode('utf-8'))
        self.assertIn(archivo.name, [Path(x).name for x in lim.restos(self.root)])  # el verificador la ve con \r
        self.limpiar()
        limpio = archivo.read_bytes().decode('utf-8')
        self.assertNotIn(OTRA, limpio)
        self.assertIn('\r\n', limpio)  # se conserva el fin de línea del archivo
        escapada = re.sub(r'fuente "[^"]*"', lambda m: f'fuente "{OTRA}/a\\"b/openspec/changes/{self.ident}/x.md"', archivo.read_text(encoding='utf-8'))
        archivo.write_text(escapada, encoding='utf-8')
        self.assertEqual(self.limpiar(), 1)  # se avisa
        self.assertIn(archivo.name, [Path(x).name for x in lim.restos(self.root)])

    def test_l1_el_verificador_ve_cada_clase_de_registro(self):
        restos = [Path(x).name for x in lim.restos(self.root)]
        self.assertIn('viejo.requisito.txt', restos)  # requisito previo
        self.assertIn('factory.json', restos)  # hechos del registro
        self.assertTrue([x for x in restos if x.endswith('.requisito')])

    # --- l2: las decisiones conservan su integridad ------------------------------------
    def test_l2_la_decision_sigue_vigente_y_deja_evento(self):
        rid = self.estado()['requisitos'][0]
        antes = self.estado()['medidas'][rid]['sha256']
        self.limpiar()
        estado = self.estado()
        nuevo = hashlib.sha256(self.requisito().read_bytes()).hexdigest()
        self.assertEqual(estado['medidas'][rid]['sha256'], nuevo)
        evento = [e for e in estado['eventos'] if e['accion'] == 'rutas_limpiadas'][-1]
        self.assertEqual(evento['requisitos'][rid], {'anterior': antes, 'nuevo': nuevo})
        self.assertEqual(evento['actor'], 'claude-code')
        self.assertEqual(evento['forma'], 'migracion')  # no es una decisión de nadie
        self.assertEqual(f.medidas_sin_decision(estado), [])

    def test_l2_estado_igual_antes_y_despues(self):
        antes = self.lineas_de_estado()
        # con la ruta de otra máquina los hechos «faltaban»; limpiar lo resuelve, y es la única diferencia admitida
        self.assertIn('hechos ausentes', antes)
        antes = re.sub(r'; hechos ausentes \(.*?RUTA_DE_LOS_HECHOS', '', antes)
        self.limpiar()
        self.assertEqual(self.lineas_de_estado(), antes)

    def test_l2_decision_sin_hash_o_con_otro_hash_no_se_toca(self):
        rid = self.estado()['requisitos'][0]
        carpeta, estado = f.leer(self.ident)
        estado['medidas'][rid]['sha256'] = 'a' * 64
        f.guardar(carpeta, estado)
        self.limpiar()
        estado = self.estado()
        self.assertEqual(estado['medidas'][rid]['sha256'], 'a' * 64)
        self.assertFalse([e for e in estado['eventos'] if e['accion'] == 'rutas_limpiadas'])

    # --- l3: la evidencia no se reescribe ----------------------------------------------
    def test_l3_tareas_byte_a_byte(self):
        antes = self.tareas()
        self.assertIn(OTRA.encode(), antes[f'tareas/{self.ident}/informe-viejo.txt'])
        self.limpiar()
        self.assertEqual(self.tareas(), antes)

    # --- l4: repetible y verificable -----------------------------------------------------
    def test_l4_segunda_ejecucion_no_cambia_nada(self):
        self.limpiar()
        self.git('add', '.')
        self.git('commit', '-qm', 'limpio')
        self.assertEqual(self.limpiar(), 0)
        self.assertEqual(self.git('status', '--short'), '')

    def test_l4_verificar_no_escribe_y_falla_si_queda_algo(self):
        self.assertEqual(self.limpiar('--verificar'), 1)
        self.assertEqual(self.git('status', '--short'), '')
        self.limpiar()
        self.assertEqual(self.limpiar('--verificar'), 0)
        self.assertEqual(lim.restos(self.root), [])

    def test_l4_registro_que_no_se_reserializa_igual_se_avisa_y_no_se_toca(self):
        ruta = self.root / 'openspec/changes' / self.ident / 'factory.json'
        ruta.write_text(ruta.read_text().replace('\n', '\n\n', 1))  # JSON válido, formato distinto
        antes = ruta.read_bytes()
        requisito = self.requisito().read_bytes()
        self.assertEqual(self.limpiar(), 1)
        self.assertEqual(ruta.read_bytes(), antes)
        self.assertEqual(self.requisito().read_bytes(), requisito)  # el requisito no se limpia sin su decisión
        self.assertEqual(f.medidas_sin_decision(self.estado()), [])

    def test_l4_si_falla_el_reemplazo_el_archivo_original_queda_entero(self):
        archivo = self.requisito()
        antes = archivo.read_bytes()
        with patch.object(lim.os, 'replace', side_effect=OSError('disco lleno')), self.assertRaises(OSError):
            self.limpiar()
        self.assertEqual(archivo.read_bytes(), antes)  # nunca a medias
        self.assertEqual(self.limpiar(), 0)  # y la corrida siguiente termina el trabajo
        self.assertNotIn(OTRA, archivo.read_text())

    def test_l2_la_propuesta_pendiente_tambien_sigue_vigente(self):
        rid = self.estado()['requisitos'][0]
        carpeta, estado = f.leer(self.ident)
        estado['medidas_pendientes'] = {rid: {**estado['medidas'].pop(rid), 'actor': 'claude-code'}}
        f.guardar(carpeta, estado)
        self.limpiar()
        nuevo = hashlib.sha256(self.requisito().read_bytes()).hexdigest()
        self.assertEqual(self.estado()['medidas_pendientes'][rid]['sha256'], nuevo)

    def test_l4_una_interrupcion_a_mitad_se_repara_en_la_corrida_siguiente(self):
        rid = self.estado()['requisitos'][0]
        escritos = []
        real = lim.escribir_atomico

        def corta_despues_de_los_registros(archivo, texto):
            if archivo.name != 'factory.json':
                raise KeyboardInterrupt  # se corta antes de tocar los requisitos
            escritos.append(archivo)
            real(archivo, texto)

        with patch.object(lim, 'escribir_atomico', corta_despues_de_los_registros), self.assertRaises(KeyboardInterrupt):
            self.limpiar()
        self.assertTrue(escritos)
        self.assertEqual(self.limpiar(), 0)
        self.assertNotIn(OTRA, self.requisito().read_text())
        self.assertEqual(f.medidas_sin_decision(self.estado()), [])
        self.assertEqual(len([e for e in self.estado()['eventos'] if e['accion'] == 'rutas_limpiadas']), 1)


if __name__ == '__main__':
    unittest.main()
