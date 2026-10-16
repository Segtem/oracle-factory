"""Dos procesos que escriben el mismo registro no se pisan: escenarios bl1–bl3, con un segundo proceso de verdad."""
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
        carpeta, estado = f.leer(self.ident)
        destino = f.ruta_registro(carpeta)
        # El otro tiene tomada la carpeta del registro y lo escribe justo antes de soltarla.
        otro = self.otro_proceso(f'''
            fd = os.open({str(destino.parent)!r}, os.O_RDONLY)
            fcntl.flock(fd, fcntl.LOCK_EX)
            print('tomada', flush=True)
            time.sleep(0.8)
            ruta = {str(destino)!r}
            datos = json.load(open(ruta))
            datos['del_otro'] = 1
            open(ruta, 'w').write(json.dumps(datos))
            os.close(fd)
        ''')
        self.assertEqual(otro.stdout.readline().strip(), 'tomada')
        estado['de_este'] = 1
        inicio = time.monotonic()
        with self.assertRaisesRegex(f.FactoryError, 'el archivo cambió durante la operación'):
            f.guardar(carpeta, estado)
        self.assertGreater(time.monotonic() - inicio, 0.3)  # esperó a que el otro soltara la carpeta
        _, errores = otro.communicate(timeout=60)
        self.assertEqual(otro.returncode, 0, errores)
        registro = self.registro()
        self.assertEqual((registro.get('del_otro'), registro.get('de_este')), (1, None))

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
