"""ri1–ri2: un valor interno roto de un registro se nombra sin traceback (ri1) y las consultas que recorren todos los cambios siguen
con él (ri2). A4-03 de la cuarta auditoría: `medidas[ID] = 7` tiraba `estado` y `verificar` con un AttributeError."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_registros_robustos as _robustos  # noqa: E402

f = _robustos.f


class Base(_robustos.Robustos):
    """Los ayudantes de test_registros_robustos sin heredar sus pruebas."""
    def importado(self):
        """Un cambio sano y otro con la spec de notas aprobada, su requisito importado y sus medidas elegidas (como el ciclo de la
        auditoría). Devuelve (sano, roto, ruta del registro del roto, requisito)."""
        sano = f.nuevo('Sano', 'notas')
        roto = f.nuevo('Nota', con_ejemplo='notas')
        with self.escribe('1'):
            f.aprobar_spec(roto)
        f.importar(roto)
        rid = f.leer(roto)[1]['requisitos'][0]
        f.medir(roto, requisito_id=rid, medidas=['notas.casos_ejecutados', 'notas.resultados'], quitar_sin_medir=True)
        self.salida()
        return sano, roto, f.ruta_registro(f.ruta_cambio(roto)), rid

    def romper(self, ruta, campo, clave, valor):
        datos = json.loads(ruta.read_text())
        datos.setdefault(campo, {})[clave] = valor
        ruta.write_text(json.dumps(datos))
        f.LEIDOS.clear()


for _nombre in [n for n in dir(_robustos.Robustos) if n.startswith('test_')]:
    setattr(Base, _nombre, None)
del _nombre


class ValorInternoRi1(Base):
    def roto(self, campo, valor, clave=None, preparado=None):
        _, roto, ruta, rid = preparado or self.importado()
        clave = clave or rid
        self.romper(ruta, campo, clave, valor)
        codigo, salida, errores = self.correr('estado', roto, '--json')
        self.assertEqual(codigo, 1, errores)
        self.assertEqual(salida, '')
        self.assertNotIn('Traceback', errores)
        for nombre in ('factory.json', campo, clave):
            self.assertIn(nombre, errores)

    def test_ri1_una_medida_que_es_un_numero(self):
        self.roto('medidas', 7)

    def test_ri1_los_vecinos(self):
        preparado = self.importado()
        original = preparado[2].read_bytes()
        for campo, valor in (('medidas', 'sí'), ('medidas', None), ('medidas', [1]), ('medidas_pendientes', 7),
                             ('propuestas', 'spec'), ('tipos', 7), ('tipos', 'rápido')):
            with self.subTest(campo=campo, valor=valor):
                preparado[2].write_bytes(original)
                self.roto(campo, valor, 'spec' if campo == 'propuestas' else None, preparado)

    def test_ri1_un_registro_sano_se_sigue_leyendo(self):
        _, roto, _, _ = self.importado()
        codigo, _, errores = self.correr('estado', roto, '--json')
        self.assertEqual(codigo, 0, errores)


class ConsultasRi2(Base):
    def test_ri2_verificar_y_listar_con_un_registro_roto(self):
        sano, roto, ruta, rid = self.importado()
        self.romper(ruta, 'medidas', rid, 7)
        codigo, salida, errores = self.correr('verificar', '--json')
        self.assertEqual(codigo, 1, errores)
        self.assertNotIn('Traceback', errores)
        problemas = json.loads(salida)['problemas']
        self.assertEqual([p['cambio'] for p in problemas], [roto])
        self.assertIn('ilegible', problemas[0]['problema'])
        self.assertIn('medidas', problemas[0]['problema'])
        codigo, salida, errores = self.correr('listar')
        self.assertEqual(codigo, 0, errores)
        self.assertIn(f'{sano}  ', salida)
        self.assertIn('ilegible', next(l for l in salida.splitlines() if l.startswith(roto)))


if __name__ == '__main__':
    unittest.main()
