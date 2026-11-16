"""«exigir» vale para cerrar un cambio, no para los que ya se cerraron: escenarios ec1, con la CLI en proceso y el ejemplo de notas."""
import contextlib
import io
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_archivo as _archivo  # noqa: E402
import test_sensor_de_factory as _sf  # noqa: E402
from oracle_factory import verificar  # noqa: E402

f = _sf.f


class Exigir(_sf.Base):
    cambio_cerrado = _archivo.Archivo.cambio_cerrado

    # --- ec1: exigir no reabre los cambios cerrados -----------------------------------------------------------------------
    def test_ec1_un_cambio_cerrado_antes_de_declarar_exigir(self):
        ident = self.cambio_cerrado()  # con hechos que dejó el sensor de notas a mano, no Factory
        self.declarar(hechos='exigir')
        self.assertEqual([p for p in f.pendientes_actuales(*f.leer(ident)) if 'Factory' in p], [])
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            codigo = verificar.comando(f, False)
        self.assertEqual(codigo, 0, salida.getvalue())
        self.assertNotIn('no los produjo Factory', salida.getvalue())

    def test_ec1_un_cambio_abierto_sigue_necesitandolos(self):
        ident = self.medido()
        self.declarar(hechos='exigir')
        self.git('add', '.')
        self.git('commit', '-qm', 'sensor')
        self.revisado(ident)
        f.juzgar(ident, self.a_mano(ident))
        with self.escribe('1'), self.assertRaisesRegex(f.FactoryError, f'oracle-factory evidencia {ident}'):
            f.cerrar(ident)


if __name__ == '__main__':
    unittest.main()
