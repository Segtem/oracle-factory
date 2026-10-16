"""Un valor del registro que no es una ruta se informa sin caerse: escenarios in1–in2."""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_estructura as _estructura  # noqa: E402

f = _estructura.f
CAMPOS = [('revision', 'informe', 'informe de revisión'), ('revision', 'decisiones', 'decisiones de revisión'),
          ('oracle', 'informe', 'informe Oracle'), ('oracle', 'hechos', 'hechos')]


class InformeNoTexto(unittest.TestCase):
    # Los ayudantes de test_estructura sin heredar sus pruebas.
    setUp = _estructura.Estructura.setUp
    escribe, git, estado = _estructura.Estructura.escribe, _estructura.Estructura.git, _estructura.Estructura.estado
    cambio_medido, cambio_juzgado = _estructura.Estructura.cambio_medido, _estructura.Estructura.cambio_juzgado
    sha7 = _estructura.Estructura.sha7

    def poner(self, ident, gate, campo, valor):
        registro = self.root / '.factory/cambios' / ident / 'factory.json'
        datos = json.loads(registro.read_text())
        datos[gate][campo] = valor
        registro.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + '\n')

    def comprobar(self, ident, gate, etiqueta):
        pendientes = f.datos_estado(ident)['pendientes']
        self.assertIn(f'{etiqueta} no válido en el registro (no es una ruta de texto)', pendientes)
        self.assertIn(ident, f.texto_resumen(None))
        self.assertIn('no_valido', {a['situacion'] for a in f.datos_donde(ident, None)['artefactos']})
        paso = f.pasos(ident)[0]
        if gate == 'revision':
            self.assertRegex(paso, rf'^oracle-factory (pedir-revision|revisar) {ident}\b')
        else:
            self.assertRegex(paso, rf'^oracle-factory juzgar {ident}\b')

    def test_in1_un_informe_de_revision_que_es_un_numero(self):
        ident = self.cambio_juzgado()
        self.poner(ident, 'revision', 'informe', 5)
        self.comprobar(ident, 'revision', 'informe de revisión')
        # Y por la CLI de verdad: estado --json termina bien y dice lo mismo.
        r = subprocess.run([sys.executable, '-c', 'import sys; from oracle_factory.cli import main; sys.exit(main())',
                            'estado', ident, '--json'], cwd=self.root, capture_output=True, text=True,
                           env={**os.environ, 'PYTHONPATH': str(_estructura.SOURCE)})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('informe de revisión no válido en el registro (no es una ruta de texto)',
                      json.loads(r.stdout)['pendientes'])

    def test_in2_los_cuatro_campos_con_valores_que_no_son_texto(self):
        ident = self.cambio_juzgado()
        registro = self.root / '.factory/cambios' / ident / 'factory.json'
        original = registro.read_text()
        for gate, campo, etiqueta in CAMPOS:
            for valor in (5, ['x'], {'a': 1}):
                with self.subTest(campo=f'{gate}.{campo}', valor=valor):
                    registro.write_text(original)
                    self.poner(ident, gate, campo, valor)
                    self.comprobar(ident, gate, etiqueta)


if __name__ == '__main__':
    unittest.main()
