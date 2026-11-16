"""Una interrupción también detiene a todo el grupo de procesos del paso (ig1): con SIGINT de verdad a un proceso que corre Factory."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest

SOURCE = Path(__file__).resolve().parents[1]
ENTORNO = {**os.environ, 'PYTHONPATH': str(SOURCE)}


def vivo(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


class Interrupcion(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.raiz = Path(self.tmp.name)

    def lanzar(self, codigo: str):
        """Un proceso aparte que corre `codigo` con Factory importable; su salida de errores queda en errores.txt."""
        guion = self.raiz / 'trabajador.py'
        guion.write_text(codigo, encoding='utf-8')
        self.errores = (self.raiz / 'errores.txt').open('w')
        self.addCleanup(self.errores.close)
        return subprocess.Popen([sys.executable, str(guion), str(self.raiz)], env=ENTORNO, stdin=subprocess.DEVNULL,
                                stdout=subprocess.DEVNULL, stderr=self.errores)

    def esperar(self, archivo: Path, segundos: float = 10):
        limite = time.monotonic() + segundos
        while not archivo.exists() and time.monotonic() < limite:
            time.sleep(0.01)
        self.assertTrue(archivo.exists(), f'nunca apareció {archivo.name}')

    def no_vuelve(self, pid: int):
        for _ in range(60):
            if not vivo(pid):
                return
            time.sleep(0.1)
        os.kill(pid, signal.SIGKILL)
        self.fail('el proceso del comando siguió vivo después de la interrupción')

    # --- ig1: una interrupción detiene a todo el grupo --------------------------------------------------------------------
    def test_ig1_un_ctrl_c_real_durante_un_despliegue(self):
        p = self.lanzar('''import sys
from pathlib import Path
from oracle_factory import despliegue
r = Path(sys.argv[1])
app = {'tipo': 'fixture', 'depende_de': [], 'secretos': [], 'tope_segundos': 30,
       'desplegar': f'touch {r}/listo; sleep 1; echo cambiado > {r}/efecto-tardio', 'version': 'printf abc', 'probar': 'true', 'volver': 'true'}
decl = {'destinos': {'app': app}, 'politica': 'cortar', 'conjunto': {'probar': 'true'}}
despliegue.ejecutar(r, decl, {'commit': 'abc', 'rama': 'main', 'orden': ['app']}, 'Persona fixture', 'claude-code')
''')
        self.esperar(self.raiz / 'listo')
        p.send_signal(signal.SIGINT)
        p.wait(timeout=30)
        sys.path.insert(0, str(SOURCE))
        from oracle_factory import despliegue
        [registro] = despliegue.registros(self.raiz)
        self.assertEqual(registro['resultado'], 'interrumpido')
        time.sleep(2)  # el comando habría escrito al segundo
        self.assertFalse((self.raiz / 'efecto-tardio').exists(), 'el comando siguió aplicando cambios después de la interrupción')

    def test_ig1_un_hijo_que_ignora_sigterm(self):
        p = self.lanzar('''import sys
from pathlib import Path
from oracle_factory import procesos
r = Path(sys.argv[1])
hijo = f"import signal, time; signal.signal(signal.SIGTERM, signal.SIG_IGN); open({str(r)!r} + '/hijo.pid', 'w').write(str(__import__('os').getpid())); time.sleep(3); open({str(r)!r} + '/escrito', 'w').write('vivo')"
procesos.correr_en_grupo([sys.executable, '-c', f'import subprocess, sys, time; subprocess.Popen([sys.executable, "-c", {hijo!r}]); time.sleep(60)'],
                         r, 60, gracia=0.5)
''')
        self.esperar(self.raiz / 'hijo.pid')
        p.send_signal(signal.SIGINT)
        p.wait(timeout=30)
        self.no_vuelve(int((self.raiz / 'hijo.pid').read_text()))
        time.sleep(3.5)
        self.assertFalse((self.raiz / 'escrito').exists())
        self.assertIn('KeyboardInterrupt', (self.raiz / 'errores.txt').read_text())  # la interrupción llegó a quien llamó

    def test_ig1_otra_interrupcion_durante_la_gracia(self):
        p = self.lanzar('''import sys
from pathlib import Path
from oracle_factory import procesos
r = Path(sys.argv[1])
procesos.correr_en_grupo(['sh', '-c', f"trap '' TERM; echo $$ > {r}/sh.pid; while true; do sleep 0.1; done"], r, 60, gracia=3)
''')
        self.esperar(self.raiz / 'sh.pid')
        time.sleep(0.2)
        p.send_signal(signal.SIGINT)
        time.sleep(0.5)  # en medio de la gracia de 3 s
        p.send_signal(signal.SIGINT)
        p.wait(timeout=30)
        self.no_vuelve(int((self.raiz / 'sh.pid').read_text()))
        self.assertIn('KeyboardInterrupt', (self.raiz / 'errores.txt').read_text())


if __name__ == '__main__':
    unittest.main()
