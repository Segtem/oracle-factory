"""Al vencer el plazo se detiene a todo el grupo de procesos (pg1): en autopilot, con un hijo que ignora SIGTERM y en despliegue."""
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from oracle_factory import conductor, despliegue, procesos  # noqa: E402


def padre_con_hijo(archivo: Path, espera_hijo: float, ignora_term: bool = False, hijo_sin_salida: bool = False) -> list[str]:
    """Un proceso que lanza a un hijo (en su mismo grupo) que escribe `archivo` después de `espera_hijo` segundos, y se queda dormido.
    Con `hijo_sin_salida`, el hijo no hereda la salida: no la mantiene abierta, así que no frena la lectura de su padre."""
    hijo = ('import signal, time; ' + ('signal.signal(signal.SIGTERM, signal.SIG_IGN); ' if ignora_term else '')
            + f'time.sleep({espera_hijo}); open({str(archivo)!r}, "w").write("vivo")')
    salida = ', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL' if hijo_sin_salida else ''
    return [sys.executable, '-c', f'import subprocess, sys, time; subprocess.Popen([sys.executable, "-c", {hijo!r}]{salida}); time.sleep(60)']


class Grupo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.archivo = Path(self.tmp.name) / 'escrito'

    # --- pg1: el plazo detiene a todo el grupo -----------------------------------------------------------------------------
    def test_pg1_un_paso_de_autopilot_que_lanzo_a_un_hijo(self):
        _, lanzar = conductor.ejecutor(Path(self.tmp.name), 'claude-code')
        inicio = time.monotonic()
        codigo, _ = lanzar(padre_con_hijo(self.archivo, 1.5), 0.5)
        self.assertEqual(codigo, 124)
        self.assertLess(time.monotonic() - inicio, 10)
        time.sleep(2.5)  # el hijo habría escrito al segundo y medio
        self.assertFalse(self.archivo.exists(), 'el hijo siguió vivo después del plazo')

    def test_pg1_un_hijo_que_ignora_sigterm_termina_igual(self):
        codigo, _, motivo = procesos.correr_en_grupo(padre_con_hijo(self.archivo, 1.5, ignora_term=True), self.tmp.name, 0.5,
                                                     gracia=0.3)
        self.assertEqual((codigo, motivo), (124, 'plazo'))
        time.sleep(2.5)
        self.assertFalse(self.archivo.exists(), 'el hijo que ignora SIGTERM siguió vivo')

    def test_pg1_un_hijo_que_ignora_sigterm_y_no_tiene_la_salida_abierta_termina_igual(self):
        codigo, _, _ = procesos.correr_en_grupo(padre_con_hijo(self.archivo, 1.5, ignora_term=True, hijo_sin_salida=True),
                                                self.tmp.name, 0.5, gracia=0.3)
        self.assertEqual(codigo, 124)
        time.sleep(2.5)
        self.assertFalse(self.archivo.exists(), 'el hijo que ignora SIGTERM y no tiene la salida abierta siguió vivo')

    def test_pg1_un_proceso_que_no_arranca_se_distingue(self):
        self.assertEqual(procesos.correr_en_grupo(['no-existe-este-comando-xyz'], self.tmp.name, 5)[::2], (127, 'no_arranca'))
        codigo, salida, _ = despliegue._correr('true', Path(self.tmp.name) / 'no-existe', {'PATH': '/usr/bin:/bin'}, 5)
        self.assertEqual(codigo, 127)
        self.assertIn('no se pudo ejecutar', salida)

    def test_pg1_autopilot_y_despliegue_pasan_por_la_funcion_comun(self):
        llamadas, real = [], procesos.correr_en_grupo
        with patch.object(procesos, 'correr_en_grupo', side_effect=lambda *a, **k: llamadas.append(a[0]) or real(*a, **k)):
            _, lanzar = conductor.ejecutor(Path(self.tmp.name), 'claude-code')
            self.assertEqual(lanzar([sys.executable, '-c', 'print("hola")'], 30), (0, 'hola'))
            codigo, salida, _ = despliegue._correr('echo chau; exit 3', Path(self.tmp.name), {'PATH': '/usr/bin:/bin'}, 30)
        self.assertEqual((codigo, salida.strip()), (3, 'chau'))
        self.assertEqual(len(llamadas), 2)

    def test_pg1_un_comando_que_sale_con_127_no_es_uno_que_no_arranco(self):
        codigo, salida, _ = despliegue._correr('no-existe-este-comando-xyz', Path(self.tmp.name), {'PATH': '/usr/bin:/bin'}, 30)
        self.assertEqual(codigo, 127)  # lo dice sh: «not found»
        self.assertNotIn('no se pudo ejecutar', salida)


if __name__ == '__main__':
    unittest.main()
