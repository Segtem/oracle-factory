"""Un registro roto se nombra y no tumba la CLI (rr1), cortar la salida no es un error (rr2) y dos cierres a la vez conservan las
dos specs (rr3). Mismo entorno que tests/test_archivo.py: un proyecto temporal con la CLI en el mismo proceso."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_archivo as _archivo  # noqa: E402

f = _archivo.f
SOURCE = Path(__file__).resolve().parents[1]
CLI = [sys.executable, '-c', 'import sys; from oracle_factory.cli import main; sys.exit(main())']


def spec_con(requisito):
    return ('# Capability: conc\n\n## ADDED Requirements\n\n'
            f'### Requirement: {requisito}\nTipo: funcional\nEl sistema DEBE hacer {requisito}.\n\n'
            f'#### Scenario: {requisito} pasa\n- DADO algo\n- CUANDO pasa\n- ENTONCES sigue\n')


class Robustos(_archivo.Archivo):
    def correr(self, *args):
        salida, errores = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(errores):
            try:
                codigo = f.main(['--proyecto', str(self.root), *args])
            except Exception as e:  # noqa: BLE001 — una excepción que se escapa es justo lo que no tiene que pasar
                codigo, errores = 'excepción', io.StringIO(f'{type(e).__name__}: {e}')
        return codigo, salida.getvalue(), errores.getvalue()

    def dos_cambios(self):
        sano, roto = f.nuevo('Sano', 'notas'), f.nuevo('Roto', 'notas')
        return sano, roto, f.ruta_registro(f.ruta_cambio(roto))

    # --- rr1: un registro roto se nombra y no tumba ------------------------------------------------------------------------
    def test_rr1_estado_de_un_registro_roto_lo_nombra_sin_traceback(self):
        _, roto, ruta = self.dos_cambios()
        sano_json = ruta.read_text()
        for contenido in ('[]', sano_json[:40], json.dumps({**json.loads(sano_json), 'titulo': 5}),
                          json.dumps({k: v for k, v in json.loads(sano_json).items() if k != 'fase'})):
            with self.subTest(contenido=contenido[:30]):
                ruta.write_text(contenido)
                codigo, _, errores = self.correr('estado', roto)
                self.assertEqual(codigo, 1, errores)
                self.assertIn('factory.json', errores)
                self.assertNotIn('Traceback', errores)
                self.assertNotIn('excepción', str(codigo))

    def test_rr1_listar_sigue_con_los_demas_y_muestra_el_roto(self):
        sano, roto, ruta = self.dos_cambios()
        ruta.write_text('[]')
        codigo, salida, errores = self.correr('listar')
        self.assertEqual(codigo, 0, errores)
        self.assertIn(f'{sano}  ', salida)
        linea = next(l for l in salida.splitlines() if l.startswith(roto))
        self.assertIn('ilegible', linea)

    def test_rr1_un_cambio_viejo_sin_capacidad_y_eventos_raros_se_siguen_leyendo(self):
        sano, _, ruta = self.dos_cambios()
        datos = json.loads(ruta.read_text())
        datos.pop('capacidad')
        datos['eventos'] = 'no es una lista'  # tolerado con un aviso (test_eventos_raros)
        ruta.write_text(json.dumps(datos))
        codigo, salida, errores = self.correr('listar')
        self.assertEqual(codigo, 0, errores)
        self.assertNotIn('ilegible', salida)

    def test_rr1_los_registros_reales_se_leen_todos(self):
        registros = f.almacenes.registros_de(SOURCE)
        if not (registros / '.factory/cambios').is_dir():
            self.skipTest('los registros de este repositorio no están a mano (un clon limpio, el CI)')
        r = subprocess.run([*CLI, '--proyecto', str(SOURCE), '--agente', 'claude-code', 'listar'], capture_output=True, text=True,
                           stdin=subprocess.DEVNULL, timeout=300)
        self.assertEqual(r.returncode, 0, r.stderr[-2000:])
        self.assertNotIn('ilegible', r.stdout)

    # --- rr2: cortar la salida no es un error ------------------------------------------------------------------------------
    def test_rr2_una_salida_que_se_corta_sale_con_141_y_en_silencio(self):
        class Cortada(io.StringIO):
            def write(self, texto):
                raise BrokenPipeError(32, 'Broken pipe')
        errores = io.StringIO()
        with patch('sys.stdout', Cortada()), contextlib.redirect_stderr(errores):
            codigo = f.main(['--proyecto', str(self.root), 'listar'])
        self.assertEqual(codigo, 141)
        self.assertEqual(errores.getvalue(), '')

    def test_rr2_de_verdad_con_un_proceso_y_una_tuberia_cerrada(self):
        for i in range(3):
            f.nuevo(f'Cambio {i}', 'notas')
        p = subprocess.Popen([*CLI, '--proyecto', str(self.root), 'listar'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             stdin=subprocess.DEVNULL, env={**os.environ, 'PYTHONPATH': str(SOURCE)})
        p.stdout.close()  # nadie lee: la primera escritura encuentra la tubería rota
        _, errores = p.communicate(timeout=120)
        self.assertEqual(p.returncode, 141, errores.decode())
        self.assertEqual(errores.decode(), '')

    # --- rr3: dos cierres a la vez conservan las dos specs -----------------------------------------------------------------
    def test_rr3_dos_fusiones_intercaladas_dejan_los_dos_requisitos(self):
        uno = self.cambio_importado('Uno', 'conc', spec_con('primero'))
        dos = self.cambio_importado('Dos', 'conc', spec_con('segundo'))
        real, empezo, errores = f.plan_archivo, threading.Event(), []

        def lenta(estado):  # la primera fusión se queda a mitad: entre calcular el índice y escribirlo
            plan = real(estado)
            if estado['id'] == uno and not empezo.is_set():
                empezo.set()
                hilo.start()
                time.sleep(0.5)  # la segunda arranca mientras tanto
            return plan

        def segunda():
            try:
                f.fusionar_capacidad(f.leer(dos)[1])
            except Exception as e:  # noqa: BLE001
                errores.append(e)
        hilo = threading.Thread(target=segunda)
        with patch.object(f, 'plan_archivo', side_effect=lenta):
            f.fusionar_capacidad(f.leer(uno)[1])
            hilo.join(timeout=30)
        self.assertEqual(errores, [])
        consolidada = self.consolidada('conc')
        self.assertIn('### Requirement: primero', consolidada)
        self.assertIn('### Requirement: segundo', consolidada)

    def test_rr3_cerrar_y_archivar_fusionan_bajo_el_bloqueo(self):
        llamadas, real = [], f.fusionar_capacidad
        with patch.object(f, 'fusionar_capacidad', side_effect=lambda estado: llamadas.append(estado['id']) or real(estado)):
            cerrado = self.cambio_cerrado()  # cerrar fusiona
            otro = self.cambio_importado('Otro', 'conc', spec_con('tercero'))
            self.marcar_cerrado(otro, '2099-01-01T00:00:00+00:00')
            f.archivar()  # archivar fusiona el que quedó cerrado sin archivar
        self.assertEqual(llamadas, [cerrado, otro])
        self.assertIn('### Requirement: tercero', self.consolidada('conc'))


for _nombre in dir(_archivo.Archivo):  # su entorno, no sus pruebas
    if _nombre.startswith('test_') and _nombre not in vars(Robustos):
        setattr(Robustos, _nombre, None)
del _nombre


if __name__ == '__main__':
    unittest.main()
