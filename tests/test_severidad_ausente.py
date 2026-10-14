"""Un informe sin severidad no se guarda ni se usa: escenarios sa1, con revisores de prueba y Clue real."""
import contextlib
import io
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_vueltas as _vueltas  # noqa: E402

f = _vueltas.f
# El revisor de test_vueltas, que además puede dejar un hallazgo sin la clave severity.
REVISOR = _vueltas.REVISOR.replace('"severity": s, ', '**({} if s == "SIN" else {"severity": s}), ')
assert REVISOR != _vueltas.REVISOR


class SeveridadAusente(_vueltas.Base):
    preparar = _vueltas.Vueltas.preparar
    candidato_nuevo = _vueltas.Vueltas.candidato_nuevo
    pedir = _vueltas.Vueltas.pedir

    # --- sa1: el corte de vueltas sigue la severidad (escenarios nuevos del MODIFIED) ----------------------------------------
    def test_sa1_un_informe_sin_severidad_no_se_guarda(self):
        self.preparar()
        self.script.write_text(REVISOR)
        for i, severidad in enumerate(('SIN', None, 'rara'), 1):  # sin la clave, nula o una que no existe
            with self.assertRaisesRegex(f.FactoryError, r'(?s)Clue rechazó el informe.*severity'):
                self.pedir('codex', [severidad, 'Un hallazgo'])
            self.assertFalse((self.carpeta() / 'revision').exists())
            eventos = [e for e in f.leer(self.ident)[1]['eventos'] if e['accion'] == 'revision_pedida']
            self.assertEqual([e['resultado'] for e in eventos], ['rechazado'] * i)

    def test_sa1_un_informe_guardado_que_pierde_la_severidad(self):
        self.preparar()
        self.pedir('codex', ['media', 'Falta validar el título'])
        self.pedir('agy', ['baja', 'Un nombre poco claro'])
        informe = self.carpeta() / 'revision' / 'codex-1.json'
        datos = json.loads(informe.read_text())
        del datos['findings'][0]['severity']
        informe.write_text(json.dumps(datos))
        salida, errores = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(errores):
            self.assertEqual(f.main(['--proyecto', str(self.root), 'estado', self.ident]), 0)
        self.assertIn('codex-1.json no pasa la validación de Clue', errores.getvalue())
        self.assertIn("'severity' is a required property", errores.getvalue())
        # La vuelta se decide con el informe que queda (el de agy, sólo bajos): revisar, no corregir el medio de codex.
        self.assertNotIn('corregí', salida.getvalue())
        self.assertIn(f'Próximo paso: oracle-factory revisar {self.ident}\n', salida.getvalue())

if __name__ == '__main__':
    unittest.main()
