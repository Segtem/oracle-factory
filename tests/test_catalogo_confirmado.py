"""Una decisión de medidas deja de valer si cambia el catálogo: escenarios cc1–cc2, en proyectos temporales."""
import contextlib
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_archivo as _archivo  # noqa: E402

f = _archivo.f
MEDIDAS = ['notas.casos_ejecutados', 'notas.resultados']


class Base(unittest.TestCase):
    pass


for _nombre in ('setUp', 'escribe', 'git', 'salida'):
    setattr(Base, _nombre, getattr(_archivo.Archivo, _nombre))


class CatalogoConfirmado(Base):
    def con_notas(self):
        ident = f.nuevo('Nota', con_ejemplo='notas')
        with self.escribe('1'):
            f.aprobar_spec(ident)
        f.importar(ident)
        self.salida()
        [rid] = f.leer(ident)[1]['requisitos']
        return ident, rid

    def medir(self, ident, rid, agente=None):
        with self.escribe('1'), patch.object(f, 'AGENTE', agente):
            f.medir(ident, requisito_id=rid, medidas=list(MEDIDAS))
        return self.salida()

    def catalogo(self, medida):
        """El archivo de la medida en el catálogo efectivo, como lo resuelve Oracle."""
        requisito = next((self.root / 'requisitos').glob('*.requisito')).read_bytes()
        return f.archivos_de_medidas(requisito)[medida]

    def cambiar_alcance(self, medida):
        ruta = self.catalogo(medida)
        texto = ruta.read_text()
        self.assertIn('    alcance "', texto)
        ruta.write_text(texto.replace('    alcance "', '    alcance "otro alcance: ', 1))
        return ruta.relative_to(self.root).as_posix()

    def estado(self, ident):
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(io.StringIO()):
            f.mostrar(ident)
        return salida.getvalue()

    # --- cc1: una decisión de medidas deja de valer si cambia el catálogo -------------------------------------------------
    def test_cc1_cambia_el_catalogo_de_una_medida_confirmada(self):
        ident, rid = self.con_notas()
        self.medir(ident, rid)
        estado = f.leer(ident)[1]
        self.assertEqual(sorted(estado['medidas'][rid]['catalogos']), MEDIDAS)
        self.assertEqual(f.medidas_sin_decision(estado), [])
        archivo = self.cambiar_alcance('notas.resultados')
        texto = self.estado(ident)
        self.assertIn(f'medidas de {rid}: el catálogo de notas.resultados ({archivo}) cambió después de la decisión registrada', texto)
        self.assertNotIn('notas.casos_ejecutados (', texto)  # sólo la que cambió
        with self.assertRaisesRegex(f.FactoryError, 'sin una decisión vigente.*notas.resultados'):
            f.juzgar(ident, self.root / 'hechos.json')

    def test_cc1_volver_a_decidir_con_las_mismas_medidas(self):
        ident, rid = self.con_notas()
        self.medir(ident, rid)
        self.cambiar_alcance('notas.resultados')
        self.assertTrue(f.medidas_sin_decision(f.leer(ident)[1]))
        salida = self.medir(ident, rid)  # las mismas medidas, otra vez
        self.assertNotIn('Sin cambios', salida)
        self.assertIn('registradas como decisión', salida)
        estado = f.leer(ident)[1]
        self.assertEqual(f.medidas_sin_decision(estado), [])
        self.assertNotIn(f'medidas de {rid}:', self.estado(ident))
        self.assertIn('Sin cambios', self.medir(ident, rid))  # y ahora sí no hay nada que registrar

    def test_cc1_una_decision_anterior_sin_huella_de_catalogos(self):
        ident, rid = self.con_notas()
        self.medir(ident, rid)
        carpeta, estado = f.leer(ident)
        del estado['medidas'][rid]['catalogos']  # como la registraba Factory antes de este cambio
        f.guardar(carpeta, estado)
        self.cambiar_alcance('notas.resultados')
        self.assertEqual(f.medidas_sin_decision(f.leer(ident)[1]), [])
        self.assertNotIn(f'medidas de {rid}:', self.estado(ident))

    # --- cc2: una propuesta de medidas no se confirma si cambió el catálogo -----------------------------------------------
    def test_cc2_el_catalogo_cambia_entre_la_propuesta_y_la_confirmacion(self):
        ident, rid = self.con_notas()
        self.medir(ident, rid, agente='claude-code')
        estado = f.leer(ident)[1]
        self.assertEqual(sorted(estado['medidas_pendientes'][rid]['catalogos']), MEDIDAS)
        self.assertEqual(f.propuestas_confirmables(estado), [rid])
        self.cambiar_alcance('notas.casos_ejecutados')
        self.assertEqual(f.propuestas_confirmables(f.leer(ident)[1]), [])
        with self.escribe('1'):
            f.confirmar_medidas(ident)
        salida = self.salida()
        self.assertIn(f'Aviso: {rid} o el catálogo de sus medidas cambió después de la propuesta; no se confirma', salida)
        self.assertIn('No hay medidas propuestas pendientes de confirmar', salida)
        self.assertNotIn(rid, f.leer(ident)[1].get('medidas') or {})
        # El agente la propone otra vez con el catálogo nuevo: ya no es «la misma propuesta», y se puede confirmar.
        self.assertNotIn('ya está registrada', self.medir(ident, rid, agente='claude-code'))
        self.assertEqual(f.propuestas_confirmables(f.leer(ident)[1]), [rid])


if __name__ == '__main__':
    unittest.main()
