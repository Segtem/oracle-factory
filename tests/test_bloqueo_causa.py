"""Aprobar una spec dice qué línea de qué archivo falta completar: escenarios bc1–bc3, en proyectos temporales."""
import contextlib
import io
from pathlib import Path
import re
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_archivo as _archivo  # noqa: E402

f = _archivo.f
MARCA = 'TODO:'  # la marca de la plantilla


class BloqueoCausa(unittest.TestCase):
    setUp, escribe, git, salida = (_archivo.Archivo.setUp, _archivo.Archivo.escribe, _archivo.Archivo.git,
                                   _archivo.Archivo.salida)

    def cambio(self, **kw):
        ident = f.nuevo('Algo nuevo', 'algo', **kw)
        carpeta = self.root / 'openspec/changes' / ident
        return ident, {'proposal': carpeta / 'proposal.md', 'spec': carpeta / 'specs/algo/spec.md', 'tasks': carpeta / 'tasks.md'}

    def completar(self, *archivos):
        for a in archivos:
            a.write_text(a.read_text(encoding='utf-8').replace(MARCA + ' ', ''), encoding='utf-8')

    def mensaje(self, ident):
        with self.escribe('1'), self.assertRaises(f.FactoryError) as c:
            f.aprobar_spec(ident)
        return str(c.exception)

    def linea_de(self, archivo, n_marca=1):
        """(número de línea, texto) de la n-ésima línea con la marca."""
        con = [(n, l.strip()) for n, l in enumerate(archivo.read_text(encoding='utf-8').splitlines(), 1) if MARCA in l]
        return con[n_marca - 1]

    # --- bc1: el bloqueo nombra la línea ------------------------------------------------------------------------------
    def test_bc1_una_plantilla_recien_creada_nombra_cada_archivo_pendiente_con_su_linea(self):
        ident, a = self.cambio()
        a['tasks'].write_text(a['tasks'].read_text(encoding='utf-8') + f'\n- [ ] {MARCA} una tarea sin completar\n', encoding='utf-8')
        m = self.mensaje(ident)
        self.assertTrue(m.startswith(f'hay que completar y revisar primero: openspec/changes/{ident}/proposal.md'), m)
        for clave, ruta in (('proposal', 'proposal.md'), ('spec', 'specs/algo/spec.md'), ('tasks', 'tasks.md')):
            n, texto = self.linea_de(a[clave])
            self.assertIn(f'openspec/changes/{ident}/{ruta} (línea {n}: «{texto}»', m, clave)
        self.assertEqual(m.count('quedan 3 más'), 2)  # la propuesta y la spec traen cuatro marcas; las tareas, una
        self.assertLess(m.index('proposal.md'), m.index('spec.md'))
        self.assertLess(m.index('spec.md'), m.index('tasks.md'))
        self.assertNotIn('falta el archivo', m)

    def test_bc1_un_solo_archivo_pendiente_nombra_solo_ese_y_no_dice_que_quedan_mas(self):
        ident, a = self.cambio()
        self.completar(a['proposal'], a['spec'])
        a['spec'].write_text(a['spec'].read_text(encoding='utf-8') + f'\nUna promesa más. {MARCA} falta.\n', encoding='utf-8')
        m = self.mensaje(ident)
        n, texto = self.linea_de(a['spec'])
        self.assertEqual(m, f'hay que completar y revisar primero: openspec/changes/{ident}/specs/algo/spec.md (línea {n}: «{texto}»)')

    def test_bc1_una_linea_larga_se_corta_a_ochenta_caracteres(self):
        ident, a = self.cambio()
        self.completar(a['proposal'], a['spec'])
        larga = MARCA + ' ' + 'x' * 200
        a['tasks'].write_text(larga + '\n', encoding='utf-8')
        m = self.mensaje(ident)
        self.assertIn(f'«{larga[:80]}…»', m)
        self.assertNotIn(larga[:81], m)

    def test_bc1_una_linea_de_exactamente_ochenta_caracteres_no_se_corta(self):
        ident, a = self.cambio()
        self.completar(a['proposal'], a['spec'])
        justa = (MARCA + ' ' + 'y' * 80)[:80]
        a['tasks'].write_text(justa + '\n', encoding='utf-8')
        self.assertIn(f'«{justa}»', self.mensaje(ident))

    def test_bc1_cuenta_las_marcas_que_quedan_y_nombra_la_primera(self):
        ident, a = self.cambio()
        self.completar(a['proposal'], a['spec'])
        a['tasks'].write_text(f'# Tareas\n\n- [ ] {MARCA} primera\n- [ ] hecha\n- [ ] {MARCA} segunda\n- [ ] {MARCA} tercera\n', encoding='utf-8')
        m = self.mensaje(ident)
        self.assertIn(f'(línea 3: «- [ ] {MARCA} primera»; quedan 2 más)', m)
        self.assertNotIn('segunda', m)

    def test_bc1_el_texto_de_la_linea_va_sin_sangria(self):
        ident, a = self.cambio()
        self.completar(a['proposal'], a['spec'])
        a['tasks'].write_text(f'# Tareas\n\n      - [ ] {MARCA} sangrada\n', encoding='utf-8')
        self.assertIn(f'(línea 3: «- [ ] {MARCA} sangrada»)', self.mensaje(ident))

    def test_bc1_en_ingles_tambien(self):
        ident, a = self.cambio(idioma='en')
        m = self.mensaje(ident)
        n, texto = self.linea_de(a['proposal'])
        self.assertIn(f'proposal.md (línea {n}: «{texto}»; quedan 3 más)', m)

    def test_bc1_un_bloqueo_no_registra_ninguna_aprobacion(self):
        ident, _ = self.cambio()
        self.mensaje(ident)
        self.assertIsNone(f.leer(ident)[1]['spec_aprobada'])

    # --- bc2: un archivo que falta ------------------------------------------------------------------------------------
    def test_bc2_si_falta_un_archivo_el_mensaje_dice_que_falta(self):
        ident, a = self.cambio()
        self.completar(a['proposal'], a['spec'])
        a['tasks'].unlink()
        m = self.mensaje(ident)
        self.assertEqual(m, f'falta el archivo openspec/changes/{ident}/tasks.md')

    def test_bc2_con_pendientes_y_un_archivo_que_falta_dice_las_dos_cosas(self):
        ident, a = self.cambio()
        a['tasks'].unlink()
        m = self.mensaje(ident)
        self.assertTrue(m.startswith('hay que completar y revisar primero: '), m)
        self.assertTrue(m.endswith(f'; falta el archivo openspec/changes/{ident}/tasks.md'), m)

    # --- bc3: todo completo sigue igual ---------------------------------------------------------------------------------
    def test_bc3_con_los_tres_archivos_completos_se_aprueba_como_siempre(self):
        ident, a = self.cambio()
        self.completar(a['proposal'], a['spec'], a['tasks'])
        with self.escribe('1'), contextlib.redirect_stderr(io.StringIO()):
            f.aprobar_spec(ident)
        estado = f.leer(ident)[1]
        self.assertIsNotNone(estado['spec_aprobada'])
        self.assertEqual(estado['fase'], 'spec_aprobada')


if __name__ == '__main__':
    unittest.main()
