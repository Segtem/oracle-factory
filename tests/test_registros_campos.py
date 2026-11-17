"""Un campo de tipo equivocado no tira las consultas (rc1), tablero y resumen siguen con los demás (rc2) y un archivo que falta se
dice con su ruta (rc3). Mismo entorno que tests/test_registros_robustos.py: un proyecto temporal con la CLI en el mismo proceso."""
import contextlib
import io
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_archivo as _archivo  # noqa: E402
import test_registros_robustos as _robustos  # noqa: E402

from oracle_factory import robusto  # noqa: E402

f = _archivo.f
SOURCE = Path(__file__).resolve().parents[1]


class Campos(_archivo.Archivo):
    def correr(self, *args):
        try:
            return _robustos.Robustos.correr(self, *args)
        except SystemExit as e:  # resumen --verificar sale así cuando no está al día
            return e.code, '', ''

    def tres_cambios(self):
        uno, dos, roto = f.nuevo('Uno', 'notas'), f.nuevo('Dos', 'notas'), f.nuevo('Roto', 'notas')
        return uno, dos, roto, f.ruta_registro(f.ruta_cambio(roto))

    def con(self, ruta, **campos):
        datos = {**json.loads(ruta.read_text()), **campos}
        ruta.write_text(json.dumps(datos))
        return ruta.read_bytes()

    def sin_traceback(self, codigo, errores):
        self.assertNotIn('Traceback', errores)
        self.assertNotIn('excepción', str(codigo), errores)

    # --- rc1: un campo de tipo equivocado no tira las consultas ------------------------------------------------------------
    def test_rc1_requisitos_que_es_un_numero(self):
        _, _, roto, ruta = self.tres_cambios()
        antes = self.con(ruta, requisitos=7)
        codigo, _, errores = self.correr('estado', roto, '--json')
        self.sin_traceback(codigo, errores)
        self.assertEqual(codigo, 1, errores)
        self.assertIn('factory.json', errores)
        self.assertIn('«requisitos»', errores)
        self.assertIn('git restore', errores)
        self.assertEqual(ruta.read_bytes(), antes)

    def test_rc1_oracle_revision_o_spec_aprobada_que_no_son_un_objeto(self):
        uno, _, roto, ruta = self.tres_cambios()
        sano = ruta.read_text()
        for campo, valor in (('oracle', 'x'), ('revision', 'x'), ('spec_aprobada', [1])):
            with self.subTest(campo=campo):
                ruta.write_text(sano)
                self.con(ruta, **{campo: valor})
                codigo, _, errores = self.correr('estado', roto)
                self.sin_traceback(codigo, errores)
                self.assertEqual(codigo, 1, errores)
                self.assertIn(f'«{campo}»', errores)
                codigo, salida, errores = self.correr('listar')
                self.assertEqual(codigo, 0, errores)
                self.assertIn(f'{uno}  ', salida)
                linea = next(l for l in salida.splitlines() if l.startswith(roto))
                self.assertIn('ilegible', linea)
                self.assertIn(f'«{campo}»', linea)

    def test_rc1_cada_campo_que_consumen_las_consultas(self):
        _, _, roto, ruta = self.tres_cambios()
        sano = ruta.read_text()
        malos = [('requisitos', [1]), ('requisitos', None), ('cierre', 'x'), ('archivo', 3), ('medidas', []), ('medidas', None),
                 ('tipos', 'x'), ('propuestas', [])]
        for campo, valor in malos:
            with self.subTest(campo=campo, valor=valor):
                ruta.write_text(sano)
                antes = self.con(ruta, **{campo: valor})
                codigo, _, errores = self.correr('estado', roto, '--json')
                self.sin_traceback(codigo, errores)
                self.assertEqual(codigo, 1, errores)
                self.assertIn(f'«{campo}»', errores)
                self.assertEqual(ruta.read_bytes(), antes)

    def test_rc1_las_formas_legitimas_se_siguen_leyendo(self):
        _, _, roto, ruta = self.tres_cambios()
        sano = json.loads(ruta.read_text())
        for campos in ({'spec_aprobada': None, 'revision': None, 'oracle': None, 'cierre': None, 'archivo': None},
                       {'medidas': {}, 'tipos': {}, 'propuestas': {}, 'requisitos': ['a.b']}):
            with self.subTest(campos=campos):
                self.assertIsNone(robusto.forma_invalida({**sano, **campos}))
        for campo in ('requisitos', 'spec_aprobada', 'revision', 'oracle', 'cierre', 'archivo', 'medidas', 'tipos', 'propuestas',
                      'spec_sha256'):
            with self.subTest(ausente=campo):
                self.assertIsNone(robusto.forma_invalida({k: v for k, v in sano.items() if k != campo}))
        codigo, _, errores = self.correr('estado', roto, '--json')
        self.assertEqual(codigo, 0, errores)

    def test_rc1_una_spec_aprobada_sin_su_huella(self):
        _, _, roto, ruta = self.tres_cambios()
        for sin in ({'spec_sha256': None}, {}):
            with self.subTest(sin=sin):
                datos = {**json.loads(ruta.read_text()), 'spec_aprobada': {'actor': 'Persona', 'documentos': {}}, **sin}
                datos.pop('spec_sha256') if not sin else None
                ruta.write_text(json.dumps(datos))
                antes = ruta.read_bytes()
                codigo, _, errores = self.correr('importar', roto)
                self.sin_traceback(codigo, errores)
                self.assertEqual(codigo, 1, errores)
                self.assertIn('«spec_sha256»', errores)
                self.assertEqual(ruta.read_bytes(), antes)

    def test_rc1_los_registros_reales_son_validos(self):
        registros = f.almacenes.registros_de(SOURCE)
        if not (registros / '.factory/cambios').is_dir():
            self.skipTest('los registros de este repositorio no están a mano (un clon limpio, el CI)')
        rutas = sorted((registros / '.factory/cambios').glob('*/factory.json'))
        self.assertTrue(rutas)
        invalidos = {r.parent.name: p for r in rutas if (p := robusto.forma_invalida(json.loads(r.read_text(encoding='utf-8'))))}
        self.assertEqual(invalidos, {})

    # --- rc2: una consulta agregada sigue con los demás ----------------------------------------------------------------------
    def test_rc2_el_tablero_con_un_registro_roto(self):
        uno, dos, roto, ruta = self.tres_cambios()
        ruta.write_text(ruta.read_text()[:40])
        codigo, salida, errores = self.correr('tablero', '--json')
        self.sin_traceback(codigo, errores)
        self.assertEqual(codigo, 0, errores)
        datos = json.loads(salida)
        self.assertEqual(sorted(c['id'] for c in datos['cambios']), sorted([uno, dos]))
        [ilegible] = datos['ilegibles']
        self.assertEqual(ilegible['id'], roto)
        self.assertIn('no es JSON válido', ilegible['motivo'])

    def test_rc2_el_resumen_con_un_registro_roto(self):
        uno, dos, roto, ruta = self.tres_cambios()
        self.con(ruta, oracle='x')
        codigo, salida, errores = self.correr('resumen')
        self.sin_traceback(codigo, errores)
        self.assertEqual(codigo, 0, errores)
        self.assertIn(roto, errores)
        texto = (self.root / '.factory/resumen.md').read_text()
        self.assertIn(f'### {uno} — Uno', texto)
        self.assertIn(f'### {dos} — Dos', texto)
        self.assertNotIn(f'### {roto}', texto)
        linea = next(l for l in texto.splitlines() if roto in l)
        self.assertIn('«oracle»', linea)

    def test_rc2_el_resumen_en_json_y_su_verificacion(self):
        uno, dos, roto, ruta = self.tres_cambios()
        self.con(ruta, oracle='x')
        codigo, salida, errores = self.correr('resumen', '--json')
        self.assertEqual(codigo, 0, errores)
        datos = json.loads(salida)
        self.assertEqual(sorted(a['id'] for a in datos['abiertos']), sorted([uno, dos]))
        self.assertEqual([i['id'] for i in datos['ilegibles']], [roto])
        self.assertIn('«oracle»', datos['ilegibles'][0]['motivo'])
        self.correr('resumen')
        # El resumen recién escrito coincide, pero no está al día: un registro no se pudo leer.
        with contextlib.redirect_stdout(io.StringIO()) as salida, contextlib.redirect_stderr(io.StringIO()) as errores:
            with self.assertRaises(SystemExit) as salio:
                f.main(['--proyecto', str(self.root), 'resumen', '--verificar'])
        self.assertEqual(salio.exception.code, 1)
        self.assertIn('ilegibles', salida.getvalue())
        self.assertIn(roto, errores.getvalue())

    def test_rc2_sin_registros_rotos_el_resumen_no_cambia(self):
        self.tres_cambios()
        self.correr('resumen')
        texto = (self.root / '.factory/resumen.md').read_text()
        self.assertNotIn('ilegible', texto)
        codigo, salida, errores = self.correr('resumen', '--verificar')
        self.assertEqual(codigo, 0, salida + errores)
        codigo, salida, _ = self.correr('tablero', '--json')
        self.assertEqual(json.loads(salida)['ilegibles'], [])

    # --- rc3: un archivo que falta se dice con su ruta -----------------------------------------------------------------------
    def test_rc3_la_spec_ausente(self):
        _, _, roto, _ = self.tres_cambios()
        spec = json.loads(f.ruta_registro(f.ruta_cambio(roto)).read_text())['spec']
        (self.root / spec).unlink()
        for comando in (('estado', roto), ('aprobar-spec', roto)):
            with self.subTest(comando=comando[0]):
                codigo, salida, errores = self.correr(*comando)
                self.sin_traceback(codigo, errores)
                self.assertNotIn('Errno', salida + errores)
                self.assertIn(spec, salida + errores)
                self.assertIn('git restore', salida + errores)

    def test_rc3_un_archivo_que_falta_en_cualquier_comando(self):
        roto = f.nuevo('Ejemplo', con_ejemplo='notas')
        spec = json.loads(f.ruta_registro(f.ruta_cambio(roto)).read_text())['spec']
        with self.escribe('1'):
            self.assertEqual(self.correr('aprobar-spec', roto)[0], 0)
        (self.root / spec).unlink()
        codigo, salida, errores = self.correr('importar', roto)
        self.sin_traceback(codigo, errores)
        self.assertEqual(codigo, 1, errores)
        self.assertNotIn('Errno', errores)
        self.assertIn(spec, errores)
        self.assertIn('git restore', errores)


    def test_rc3_otros_errores_de_archivo_sin_errno(self):
        raiz = Path('/proyecto')
        self.assertEqual(robusto.sin_errno(PermissionError(13, 'Permission denied', '/proyecto/a/b.md'), raiz),
                         'Permission denied: a/b.md')
        self.assertEqual(robusto.sin_errno(FileNotFoundError(2, 'No such file', '/otro/c.md'), raiz),
                         'falta el archivo /otro/c.md: recuperalo desde Git (git restore /otro/c.md)')
        self.assertEqual(robusto.sin_errno(OSError('disco lleno'), raiz), 'disco lleno')


for _nombre in dir(_archivo.Archivo):  # su entorno, no sus pruebas
    if _nombre.startswith('test_') and _nombre not in vars(Campos):
        setattr(Campos, _nombre, None)
del _nombre


if __name__ == '__main__':
    unittest.main()
