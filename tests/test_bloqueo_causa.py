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

    def test_bc1_una_plantilla_recien_creada_sin_tocar_nombra_los_archivos_que_la_tienen(self):
        # La plantilla real trae la marca en la propuesta y en la spec; las tareas no la traen y no se nombran.
        for idioma in ('es', 'en'):
            ident, a = self.cambio(idioma=idioma, sufijo=f'real{idioma}')
            m = self.mensaje(ident)
            self.assertIn('proposal.md (línea', m, idioma)
            self.assertIn('spec.md (línea', m, idioma)
            self.assertNotIn('tasks.md', m, idioma)

    def test_bc1_con_exactamente_dos_marcas_dice_queda_uno(self):
        ident, a = self.cambio()
        self.completar(a['proposal'], a['spec'])
        a['tasks'].write_text(f'# Tareas\n\n- [ ] {MARCA} una\n- [ ] {MARCA} dos\n', encoding='utf-8')
        m = self.mensaje(ident)
        self.assertIn('; queda 1 más)', m)
        self.assertNotIn('quedan 1', m)

    def test_bc1_un_enlace_simbolico_fuera_del_proyecto_se_rechaza_sin_leerlo(self):
        ident, a = self.cambio()
        self.completar(a['proposal'], a['spec'])
        afuera = Path(self.tmp.name) / 'secreto.txt'
        afuera.write_text(f'{MARCA} contenido que no debe aparecer\n')
        a['tasks'].unlink()
        a['tasks'].symlink_to(afuera)
        m = self.mensaje(ident)
        self.assertIn('no se siguen enlaces simbólicos', m)
        self.assertNotIn('contenido que no debe aparecer', m)

    def test_bc1_un_enlace_simbolico_roto_tambien_se_rechaza(self):
        ident, a = self.cambio()
        self.completar(a['proposal'], a['spec'])
        a['tasks'].unlink()
        a['tasks'].symlink_to(Path(self.tmp.name) / 'no-existe.txt')
        self.assertIn('no se siguen enlaces simbólicos', self.mensaje(ident))

    def test_bc1_un_archivo_que_no_es_utf8_da_un_error_claro_y_no_un_traceback(self):
        for clave in ('proposal', 'spec', 'tasks'):
            ident, a = self.cambio(sufijo=f'bin{clave}')
            self.completar(a['proposal'], a['spec'], a['tasks'])
            a[clave].write_bytes(b'# Algo\n\xff\xfe\x00 bytes invalidos\n')
            m = self.mensaje(ident)
            self.assertIn('no está en UTF-8', m, clave)
            self.assertIn(a[clave].name, m, clave)

    # --- bc2: un archivo que falta ------------------------------------------------------------------------------------
    def test_bc2_si_falta_un_archivo_el_mensaje_dice_que_falta(self):
        ident, a = self.cambio()
        self.completar(a['proposal'], a['spec'])
        a['tasks'].unlink()
        m = self.mensaje(ident)
        self.assertEqual(m, f'falta el archivo openspec/changes/{ident}/tasks.md')

    def test_bc2_si_faltan_varios_archivos_los_nombra_a_todos_en_plural(self):
        ident, a = self.cambio()
        self.completar(a['spec'])
        a['proposal'].unlink()
        a['tasks'].unlink()
        m = self.mensaje(ident)
        self.assertEqual(m, f'faltan los archivos openspec/changes/{ident}/proposal.md, openspec/changes/{ident}/tasks.md')

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
