"""estado ofrece revisar cuando quedan hallazgos medios: escenarios er1, con revisores de prueba y Clue real."""
import contextlib
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_vueltas as _vueltas  # noqa: E402
from test_cli_humana import Terminal  # noqa: E402

f = _vueltas.f


class EstadoAlternativas(_vueltas.Base):
    preparar = _vueltas.Vueltas.preparar
    candidato_nuevo = _vueltas.Vueltas.candidato_nuevo
    pedir = _vueltas.Vueltas.pedir

    def estado(self):
        """estado en texto y en JSON, como lo pide la persona."""
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(io.StringIO()):
            f.mostrar(self.ident)
            datos = f.datos_estado(self.ident)
        return salida.getvalue(), datos

    # --- er1: estado ofrece revisar cuando quedan hallazgos medios ------------------------------------------------------------
    def test_er1_quedan_hallazgos_medios_sin_aceptar(self):
        self.preparar()
        self.pedir('codex', ['media', 'Falta validar el título'], ['baja', 'Un nombre poco claro'])
        texto, datos = self.estado()
        self.assertIn('Próximo paso: corregí los 1 hallazgos medios o más del candidato', texto)
        self.assertIn(f'También: oracle-factory revisar {self.ident} — para aceptarlos como riesgo o descartarlos, con motivo',
                      texto)
        self.assertTrue(datos['proximo_paso'].startswith('corregí los 1 hallazgos medios o más'))
        self.assertEqual(datos['alternativas'], [f'oracle-factory revisar {self.ident}'])
        self.assertEqual(f.proximo_paso(self.ident), datos['proximo_paso'])  # el paso de siempre no cambia

    def test_er1_el_menu_de_estado_ofrece_revisar(self):
        self.preparar()
        self.pedir('codex', ['media', 'Falta validar el título'])
        opciones = []
        elegir = f.elegir

        def mirar(pregunta, lista):
            opciones.extend(o for o, _ in lista)
            return elegir(pregunta, lista)

        with self.escribe('1'), patch.object(f, 'elegir', mirar), patch.object(f, 'revisar_paso_a_paso') as revisar, \
                contextlib.redirect_stdout(Terminal()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(f.ofrecer_siguiente(self.ident), 0)
        self.assertEqual(opciones, [f'Ejecutar «oracle-factory revisar {self.ident}»', 'Salir'])
        revisar.assert_called_once_with(self.ident)
        with self.escribe('2'), patch.object(f, 'revisar_paso_a_paso') as revisar, \
                contextlib.redirect_stdout(Terminal()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(f.ofrecer_siguiente(self.ident), 0)  # «Salir» no ejecuta nada
        revisar.assert_not_called()

    def test_er1_pedir_revision_lo_dice(self):
        self.preparar()
        salida = self.pedir('codex', ['alta', 'Falta validar el título'])
        self.assertIn(f'pedir otra vuelta con oracle-factory pedir-revision {self.ident}', salida)
        self.assertIn(f'También: aceptarlos como riesgo o descartarlos, con motivo, en oracle-factory revisar {self.ident}',
                      salida)

    def test_er1_sin_hallazgos_medios_no_hay_alternativa(self):
        self.preparar()
        salida = self.pedir('codex', ['baja', 'Un nombre poco claro'])
        self.assertNotIn('También:', salida)
        texto, datos = self.estado()
        self.assertIn(f'Próximo paso: oracle-factory revisar {self.ident}\n', texto)
        self.assertNotIn('También:', texto)
        self.assertEqual((datos['proximo_paso'], datos['alternativas']), (f'oracle-factory revisar {self.ident}', []))
        self.assertEqual(f.pasos(self.ident), [f'oracle-factory revisar {self.ident}'])


if __name__ == '__main__':
    unittest.main()
