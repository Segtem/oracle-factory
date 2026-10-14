"""El paquete de revisión deja fuera lo que no es producto: escenarios pp1–pp2, con un revisor de prueba y Clue 0.1.0a2 real."""
import contextlib
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_revisores as _revisores  # noqa: E402

f = _revisores.f


class Base(unittest.TestCase):
    pass


for _nombre in (*_revisores.AYUDANTES, 'preparar', 'configurar', 'pedir', 'carpeta'):
    setattr(Base, _nombre, getattr(_revisores.Revisores, _nombre))


class PaqueteProducto(Base):
    def registros(self, gestionada=False):
        """Agrega al último commit del candidato registros de Factory (y, si se pide, una spec que gestiona Factory)."""
        evidencia = self.root / '.factory/cambios' / self.ident / 'candidatos' / 'viejo' / 'evidencia'
        evidencia.mkdir(parents=True)
        (evidencia / 'suite.txt').write_text('una vuelta anterior\n')
        tarea = self.root / 'tareas' / self.ident / 'TAREA.md'
        tarea.write_text(tarea.read_text() + '\nnota de una vuelta\n')
        if gestionada:  # una spec consolidada con su índice: Factory la genera, no es producto
            (self.root / '.factory/specs').mkdir(exist_ok=True)
            (self.root / '.factory/specs/demo.json').write_text('{}\n')
            spec = self.root / 'openspec/specs/demo/spec.md'
            spec.parent.mkdir(parents=True)
            spec.write_text('# Capability: demo\n')
        self.git('add', '.')
        self.git('commit', '-q', '--amend', '--no-edit')

    def paquete(self):
        return json.loads(next((self.carpeta() / 'clue').glob('paquete-prueba-*.json')).read_text())

    def preparar_revision(self):
        errores = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(errores):
            informe, _ = f.preparar_revision(self.ident)
        return json.loads(informe.read_text()), errores.getvalue()

    # --- pp1: el paquete de revisión excluye lo que no es producto --------------------------------------------------------------
    def test_pp1_un_candidato_con_registros_de_vueltas_anteriores(self):
        self.preparar('hallazgo')
        self.registros()
        self.pedir()
        paquete = self.paquete()
        self.assertEqual([a['file'] for a in paquete['files']], ['examples/notas/notas.py'])
        self.assertEqual(paquete['exclusions'], ['.factory', 'tareas'])
        self.assertIn(f'.factory/cambios/{self.ident}/candidatos/viejo/evidencia/suite.txt', paquete['excluded_files'])
        self.assertIn(f'tareas/{self.ident}/TAREA.md', paquete['excluded_files'])
        pedido = (self.carpeta() / 'revision' / 'prueba-1.pedido.md').read_text()
        self.assertIn('Fuera del paquete, porque no son producto (.factory, tareas)', pedido)
        informe, errores = self.preparar_revision()  # y el informe del paquete con exclusiones se usa
        self.assertEqual(len(informe['hallazgos']), 1, errores)

    def test_pp1_un_registro_fuera_de_esas_carpetas(self):
        self.preparar()
        self.registros(gestionada=True)
        self.pedir()
        paquete = self.paquete()
        self.assertEqual(paquete['exclusions'], ['.factory', 'openspec/specs/demo/spec.md', 'tareas'])
        self.assertEqual([a['file'] for a in paquete['files']], ['examples/notas/notas.py'])
        # Un candidato que sólo trae registros (cerrar con evidencia un cambio viejo): sin exclusiones, como antes.
        self.assertEqual(f.exclusiones_del_paquete(self.git('rev-parse', 'HEAD~1'), self.git('rev-parse', 'HEAD~1')), [])
        self.git('checkout', '-q', '-b', 'solo-registros', self.base)
        (self.root / 'tareas' / self.ident / 'otra.md').write_text('sólo un registro\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'sólo registros')
        self.assertEqual(f.exclusiones_del_paquete(self.base, self.git('rev-parse', 'HEAD')), [])

    # --- pp2: Factory comprueba las exclusiones del paquete ------------------------------------------------------------------
    def test_pp2_un_paquete_que_excluye_producto(self):
        self.preparar('hallazgo')
        self.registros()
        # Al pedir: si las exclusiones dejaran afuera producto, no se lanza al revisor ni se guarda nada.
        with patch.object(f, 'exclusiones_del_paquete', return_value=['examples/notas/sensor.py', 'tareas']):
            notas = self.root / 'examples/notas/sensor.py'
            notas.write_text(notas.read_text() + '\n# cambio de producto\n')
            self.git('add', '.')
            self.git('commit', '-q', '--amend', '--no-edit')
            with self.assertRaisesRegex(f.FactoryError, 'deja afuera archivos del producto: examples/notas/sensor.py'):
                self.pedir()
        self.assertFalse((self.carpeta() / 'revision').exists())
        # Al preparar: un informe guardado cuyo paquete excluye producto no se usa, y el aviso nombra el archivo.
        self.pedir()
        clue = next((self.carpeta() / 'clue').glob('paquete-prueba-*.json'))
        paquete = json.loads(clue.read_text())
        paquete['excluded_files'] = sorted(paquete['excluded_files'] + ['examples/notas/notas.py'])
        clue.write_text(json.dumps(paquete))
        informe, errores = self.preparar_revision()
        self.assertEqual(informe['hallazgos'], [])
        self.assertIn('deja afuera archivos del producto (examples/notas/notas.py); no lo uso', errores)

    def test_pp2_un_paquete_anterior_sin_exclusiones(self):
        self.preparar('hallazgo')
        self.registros()
        with patch.object(f, 'exclusiones_del_paquete', return_value=[]):  # como lo preparaba Factory con Clue 0.1.0a1
            self.pedir()
        paquete = self.paquete()
        self.assertNotIn('exclusions', paquete)
        self.assertIn(f'tareas/{self.ident}/TAREA.md', [a['file'] for a in paquete['files']])
        informe, errores = self.preparar_revision()
        self.assertEqual(len(informe['hallazgos']), 1, errores)


if __name__ == '__main__':
    unittest.main()
