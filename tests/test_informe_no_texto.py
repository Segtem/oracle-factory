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
CAMPOS = [('revision', 'informe', 'sha256', 'informe de revisión'),
          ('revision', 'decisiones', 'decisiones_sha256', 'decisiones de revisión'),
          ('oracle', 'informe', 'informe_sha256', 'informe Oracle'), ('oracle', 'hechos', 'hechos_sha256', 'hechos')]
# Lo que no es una ruta de texto, también lo que Python toma por falso (null es un campo ausente, como en una revisión libre).
VALORES = (5, ['x'], {'a': 1}, 0, False, '', [], {}, 'a\x00b')


class InformeNoTexto(unittest.TestCase):
    # Los ayudantes de test_estructura sin heredar sus pruebas.
    setUp = _estructura.Estructura.setUp
    escribe, git, estado = _estructura.Estructura.escribe, _estructura.Estructura.git, _estructura.Estructura.estado
    cambio_medido, cambio_juzgado = _estructura.Estructura.cambio_medido, _estructura.Estructura.cambio_juzgado
    sha7 = _estructura.Estructura.sha7

    def poner(self, ident, gate, campo, valor, sin_huella=None):
        registro = self.root / '.factory/cambios' / ident / 'factory.json'
        datos = json.loads(registro.read_text())
        datos[gate][campo] = valor
        if sin_huella:
            datos[gate].pop(sin_huella, None)
        registro.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + '\n')

    def comprobar(self, ident, gate, etiqueta):
        pendientes = f.datos_estado(ident)['pendientes']
        self.assertIn(f'{etiqueta} no válido en el registro (no es una ruta de texto)', pendientes)
        self.assertIn(f'{etiqueta} no válido en el registro', f.texto_resumen(None))
        self.assertIn('no_valido', {a['situacion'] for a in f.datos_donde(ident, None)['artefactos']})
        paso = f.pasos(ident)[0]
        if gate == 'revision':
            self.assertRegex(paso, rf'^oracle-factory (pedir-revision|revisar) {ident}\b')
        else:
            # Los hechos del candidato siguen ahí: se juzgan sin pedir una ruta por completar.
            self.assertEqual(paso, f'oracle-factory juzgar {ident}')

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
        for gate, campo, huella, etiqueta in CAMPOS:
            for valor in VALORES:
                for sin_huella in (None, huella):
                    with self.subTest(campo=f'{gate}.{campo}', valor=valor, sin_huella=bool(sin_huella)):
                        registro.write_text(original)
                        self.poner(ident, gate, campo, valor, sin_huella)
                        self.comprobar(ident, gate, etiqueta)


if __name__ == '__main__':
    unittest.main()
