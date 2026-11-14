"""El pedido le dice al revisor con qué Python correr las pruebas y que una prueba omitida no la hace incompleta (rp1).

Con el entorno de tests/test_vueltas.py: `pedir-revision` lanza de verdad un revisor de prueba y se lee el pedido que guardó."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_vueltas as _vueltas  # noqa: E402

f = _vueltas.f


class Python(_vueltas.Vueltas):
    def test_rp1_el_pedido_nombra_el_interprete_de_factory_y_que_una_omision_no_lo_hace_incompleto(self):
        self.preparar()
        self.pedir('codex')
        pedido = (self.carpeta() / 'revision' / 'codex-1.pedido.md').read_text()
        self.assertIn(sys.executable, pedido)  # el intérprete con que corrió Factory, que tiene sus dependencias
        self.assertIn('PYTHONPATH', pedido)
        self.assertRegex(pedido, r'(?i)se omite[^.]*no\s+hace\s+incompleta\s+la\s+revisión')
        self.assertIn('limitations', pedido)


for _nombre in dir(_vueltas.Vueltas):  # su entorno, no sus pruebas
    if _nombre.startswith('test_') and _nombre not in vars(Python):
        setattr(Python, _nombre, None)
del _nombre


if __name__ == '__main__':
    unittest.main()
