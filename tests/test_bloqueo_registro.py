"""Dos procesos que escriben el mismo registro no se pisan: escenarios bl1–bl3; bl1 y bl2 con un segundo proceso de verdad."""
import json
import os
from pathlib import Path
import subprocess
import sys
import textwrap
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_estructura as _estructura  # noqa: E402

f = _estructura.f


class BloqueoRegistro(unittest.TestCase):
    setUp = _estructura.Estructura.setUp

    def otro_proceso(self, codigo):
        """Otro proceso de Factory en el mismo proyecto, que corre `codigo` con f (la CLI) e ident ya definidos."""
        programa = (f'import sys, json, time, fcntl, os\nfrom oracle_factory import cli as f\nident = {self.ident!r}\n'
                    + textwrap.dedent(codigo))
        return subprocess.Popen([sys.executable, '-c', programa], cwd=self.root, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, env={**os.environ, 'PYTHONPATH': str(_estructura.SOURCE)})

    def registro(self):
        return json.loads(f.ruta_registro(f.leer(self.ident)[0]).read_text())

    def test_bl1_otro_proceso_escribe_entre_la_lectura_y_la_escritura(self):
        self.ident = f.nuevo('Nota', con_ejemplo='notas')
        f.LEIDOS.clear()  # como un proceso nuevo: la base sale de leer, no de lo que nuevo escribió
        carpeta, estado = f.leer(self.ident)
        otro = self.otro_proceso('''
            c, e = f.leer(ident)
            e['del_otro'] = 1
            f.guardar(c, e)
        ''')
        _, errores = otro.communicate(timeout=60)
        self.assertEqual(otro.returncode, 0, errores)
        estado['de_este'] = 1
        with self.assertRaisesRegex(f.FactoryError, 'el archivo cambió durante la operación'):
            f.guardar(carpeta, estado)
        registro = self.registro()
        self.assertEqual((registro.get('del_otro'), registro.get('de_este')), (1, None))

    def test_bl2_otro_proceso_escribe_entre_la_comparacion_y_el_reemplazo(self):
        self.ident = f.nuevo('Nota', con_ejemplo='notas')
        f.LEIDOS.clear()  # como un proceso nuevo: la base sale de leer, no de lo que nuevo escribió
        carpeta, estado = f.leer(self.ident)
        # El otro guarda con Factory, y se demora justo entre su comparación y su reemplazo.
        otro = self.otro_proceso('''
            reemplazar = os.replace
            def lento(origen, destino):
                print('comparado', flush=True)
                time.sleep(0.8)
                reemplazar(origen, destino)
            os.replace = lento
            c, e = f.leer(ident)
            e['del_otro'] = 1
            f.guardar(c, e)
        ''')
        self.assertEqual(otro.stdout.readline().strip(), 'comparado')
        estado['de_este'] = 1
        inicio = time.monotonic()
        with self.assertRaisesRegex(f.FactoryError, 'el archivo cambió durante la operación'):
            f.guardar(carpeta, estado)
        self.assertGreater(time.monotonic() - inicio, 0.3)  # esperó a que el otro terminara de reemplazar
        _, errores = otro.communicate(timeout=60)
        self.assertEqual(otro.returncode, 0, errores)
        registro = self.registro()
        self.assertEqual((registro.get('del_otro'), registro.get('de_este')), (1, None))

    def test_bl1_una_escritura_sin_leer_antes_tambien_cuenta(self):
        # Lo que el proceso escribió sin haber leído es su base para la próxima escritura.
        self.ident = f.nuevo('Nota', con_ejemplo='notas')
        carpeta, estado = f.leer(self.ident)
        f.LEIDOS.clear()
        f.guardar(carpeta, estado)  # escribe sin haber leído en este proceso
        otro = self.otro_proceso('''
            c, e = f.leer(ident)
            e['del_otro'] = 1
            f.guardar(c, e)
        ''')
        _, errores = otro.communicate(timeout=60)
        self.assertEqual(otro.returncode, 0, errores)
        estado['de_este'] = 1
        with self.assertRaisesRegex(f.FactoryError, 'el archivo cambió durante la operación'):
            f.guardar(carpeta, estado)
        self.assertEqual(self.registro().get('del_otro'), 1)
        # Y si otro lo borró, también es un archivo que cambió, no un error del sistema.
        f.ruta_registro(carpeta).unlink()
        with self.assertRaisesRegex(f.FactoryError, 'el archivo cambió durante la operación'):
            f.guardar(carpeta, estado)

    def test_bl3_un_proceso_que_lee_y_escribe_varias_veces(self):
        self.ident = f.nuevo('Nota', con_ejemplo='notas')
        carpeta, estado = f.leer(self.ident)
        estado['primera'] = 1
        f.guardar(carpeta, estado)
        estado['segunda'] = 2
        f.guardar(carpeta, estado)  # sobre lo que este mismo proceso escribió
        carpeta, estado = f.leer(self.ident)
        estado['tercera'] = 3
        f.guardar(carpeta, estado)
        registro = self.registro()
        self.assertEqual([registro.get(k) for k in ('primera', 'segunda', 'tercera')], [1, 2, 3])
        # Y los comandos de siempre, que leen y guardan varias veces, siguen andando.
        with _estructura.Estructura.escribe(self, '1'):
            f.aprobar_spec(self.ident)
        f.importar(self.ident)
        self.assertEqual(f.leer(self.ident)[1]['fase'], 'requisitos_importados')


if __name__ == '__main__':
    unittest.main()
