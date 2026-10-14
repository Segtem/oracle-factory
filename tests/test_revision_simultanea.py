"""Pedidos de revisión simultáneos sobre el mismo candidato: escenarios rs1–rs2, con revisores de prueba y Clue real."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_revisores as _revisores  # noqa: E402

f = _revisores.f


class Base(unittest.TestCase):
    pass


for _nombre in (*_revisores.AYUDANTES, 'preparar', 'configurar', 'carpeta', 'eventos'):
    setattr(Base, _nombre, getattr(_revisores.Revisores, _nombre))


class RevisionSimultanea(Base):
    def a_la_vez(self, *nombres):
        """Lanza un pedido por nombre en hilos que arrancan juntos; devuelve los errores de cada uno."""
        juntos, original = threading.Barrier(len(nombres)), f.candidato_vigente
        errores = {}

        def candidato(ident):  # todos llegan juntos al checkout y al número del paquete
            juntos.wait(timeout=30)
            return original(ident)

        def pedir(i, nombre):
            try:
                f.pedir_revision(self.ident, nombre, base=self.base)
            except Exception as e:  # noqa: BLE001 — se informa en la aserción
                errores[i] = repr(e)

        hilos = [threading.Thread(target=pedir, args=(i, n)) for i, n in enumerate(nombres)]
        with patch.object(f, 'candidato_vigente', candidato), contextlib.redirect_stdout(io.StringIO()):
            for h in hilos:
                h.start()
            for h in hilos:
                h.join(timeout=120)
        self.assertFalse(any(h.is_alive() for h in hilos), 'un pedido quedó colgado')
        return errores

    # --- rs1: pedidos de revisión simultáneos sobre el mismo candidato ---------------------------------------------------
    def test_rs1_dos_revisores_distintos_a_la_vez(self):
        self.preparar('ok')
        config = json.loads((self.root / '.factory/config.json').read_text())
        otro = dict(config['revisores']['prueba'], comando=[*config['revisores']['prueba']['comando']])
        otro['comando'][2] = 'hallazgo'
        config['revisores']['otro'] = otro
        (self.root / '.factory/config.json').write_text(json.dumps(config))
        self.assertEqual(self.a_la_vez('prueba', 'otro'), {})
        revision = self.carpeta() / 'revision'
        self.assertEqual(sorted(p.name for p in revision.glob('*.json')), ['otro-1.json', 'prueba-1.json'])
        self.assertEqual(len(json.loads((revision / 'otro-1.json').read_text())['findings']), 1)
        self.assertEqual(sorted(e['revisor'] for e in self.eventos()), ['otro', 'prueba'])
        self.assertEqual([e['resultado'] for e in self.eventos()], ['ok', 'ok'])

    def test_rs1_el_mismo_revisor_dos_veces_a_la_vez(self):
        self.preparar('ok')
        self.assertEqual(self.a_la_vez('prueba', 'prueba', 'prueba'), {})
        self.assertEqual(sorted(p.name for p in (self.carpeta() / 'clue').glob('*.json')),
                         ['paquete-prueba-1.json', 'paquete-prueba-2.json', 'paquete-prueba-3.json'])
        self.assertEqual(sorted(p.name for p in (self.carpeta() / 'revision').glob('*.json')),
                         ['prueba-1.json', 'prueba-2.json', 'prueba-3.json'])
        self.assertEqual(len(self.eventos()), 3)

    # --- rs2: un pedido interrumpido no traba los siguientes ---------------------------------------------------------------
    def test_rs2_un_bloqueo_de_un_pedido_que_murio(self):
        self.preparar('ok')
        bloqueo = self.root / '.factory/local/locks' / f'{self.ident}.pedir.lock'
        bloqueo.parent.mkdir(parents=True, exist_ok=True)
        # Un proceso toma el turno: mientras vive, un pedido espera.
        dueño = subprocess.Popen([sys.executable, '-c', 'import fcntl, sys, time; a = open(sys.argv[1], "a"); '
                                  'fcntl.flock(a, fcntl.LOCK_EX); print("listo", flush=True); time.sleep(120)', str(bloqueo)],
                                 stdout=subprocess.PIPE, text=True)
        self.addCleanup(dueño.stdout.close)
        self.addCleanup(dueño.kill)
        self.assertEqual(dueño.stdout.readline().strip(), 'listo')
        terminado = threading.Event()

        def pedir():
            with contextlib.redirect_stdout(io.StringIO()):
                f.pedir_revision(self.ident, 'prueba', base=self.base)
            terminado.set()

        hilo = threading.Thread(target=pedir)
        hilo.start()
        self.assertFalse(terminado.wait(3), 'el pedido no esperó su turno')
        dueño.kill()  # muere sin soltar nada a mano; el archivo de bloqueo queda en el disco
        dueño.wait()
        self.assertTrue(terminado.wait(60), 'el pedido quedó trabado por el bloqueo de un proceso muerto')
        hilo.join()
        self.assertTrue(bloqueo.is_file())
        self.assertTrue((self.carpeta() / 'revision' / 'prueba-1.json').is_file())
        with contextlib.redirect_stdout(io.StringIO()):  # y con el archivo ahí, el siguiente pedido no espera
            f.pedir_revision(self.ident, 'prueba', base=self.base)
        self.assertEqual(len(self.eventos()), 2)


if __name__ == '__main__':
    unittest.main()
