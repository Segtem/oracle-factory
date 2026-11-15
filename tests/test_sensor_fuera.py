"""El checkout del sensor va fuera del producto y del almacén: escenarios sx1, con la CLI en proceso y el ejemplo de notas."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_sensor_de_factory as _sf  # noqa: E402
from oracle_factory import sensor  # noqa: E402

f = _sf.f
DONDE = ['sh', '-c', 'mkdir -p {salida} && pwd -P > {salida}/hechos.json']


class Fuera(_sf.Base):
    def corrida(self, comando):
        ident = self.medido()
        self.declarar(comando)
        self.git('add', '.')
        self.git('commit', '-qm', 'sensor')
        return ident

    def fuera(self, carpeta: Path):
        for raiz in (f.ROOT, f.PRODUCTO or f.ROOT):
            self.assertFalse(carpeta.is_relative_to(Path(raiz).resolve()), f'{carpeta} está dentro de {raiz}')
        self.assertFalse(carpeta.exists(), f'{carpeta} quedó')

    # --- sx1: el checkout queda fuera del producto y del almacén ----------------------------------------------------------
    def test_sx1_donde_corre_el_sensor(self):
        ident = self.corrida(DONDE)
        sensor.producir(ident, [])
        self.fuera(Path((self.evidencia(ident) / 'hechos.json').read_text().strip()))

    def test_sx1_un_sensor_que_falla(self):
        ident = self.corrida(['sh', '-c', DONDE[2] + ' && exit 3'])
        with self.assertRaisesRegex(f.FactoryError, 'código 3'):
            sensor.producir(ident, [])
        self.fuera(Path((self.evidencia(ident) / 'hechos.json').read_text().strip()))


if __name__ == '__main__':
    unittest.main()
