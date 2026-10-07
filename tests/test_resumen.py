"""Resumen del estado actual: escenarios r1–r6 de la spec, sobre proyectos temporales."""
import contextlib
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_archivo as _archivo  # noqa: E402

MODIFICA, f = _archivo.MODIFICA, _archivo.f

AYUDANTES = ('setUp', 'escribe', 'git', 'salida', 'cambio_cerrado', 'cambio_importado', 'marcar_cerrado', 'consolidada', 'archivos')


class Base(unittest.TestCase):
    pass


for _nombre in AYUDANTES:  # los ayudantes del fixture de archivo, sin heredar sus pruebas
    setattr(Base, _nombre, getattr(_archivo.Archivo, _nombre))


class Resumen(Base):
    def seccion(self, titulo, sub=None):
        """El texto de una sección «## titulo» (y, si se pide, de su subsección «### sub»), o '' si no está."""
        partes = self.texto().split(f'## {titulo}\n', 1)
        if len(partes) < 2:
            return ''
        texto = partes[1].split('\n## ', 1)[0]
        if sub is None:
            return texto
        partes = texto.split(f'### {sub}\n', 1)
        return partes[1].split('\n### ', 1)[0] if len(partes) == 2 else ''

    def texto(self):
        return (self.root / '.factory/resumen.md').read_text(encoding='utf-8')

    def verificar(self, *args):
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                f.comando_resumen(True, *args)
            return 0
        except SystemExit as e:
            return e.code

    def con_riesgo(self, ident, hallazgo='H-01'):
        """Le da al cambio cerrado una revisión guiada con un riesgo aceptado y un límite declarado."""
        base = self.root / 'tareas' / ident / 'revisiones' / 'registro-fixture'
        base.mkdir(parents=True)
        (base / 'informe.json').write_text(json.dumps({'hallazgos': [{'id': hallazgo, 'descripcion': 'Un riesgo de prueba.'}],
                                                       'limites': ['Un límite de prueba.']}))
        (base / 'decisiones.json').write_text(json.dumps({'decisiones': [
            {'hallazgo_id': hallazgo, 'estado': 'riesgo_aceptado', 'motivo': 'Lo acepto por ahora.', 'actor': 'Persona fixture'},
            {'hallazgo_id': 'H-99', 'estado': 'corregido', 'motivo': 'Ya está.', 'actor': 'Persona fixture'}]}))
        carpeta, estado = f.leer(ident)
        estado['revision'] = {**(estado.get('revision') or {}), 'formato': 'guiado',
                              'informe': f'tareas/{ident}/revisiones/registro-fixture/informe.json',
                              'decisiones': f'tareas/{ident}/revisiones/registro-fixture/decisiones.json'}
        f.guardar(carpeta, estado)

    # --- r1: lo vigente y lo pendiente ------------------------------------------------------------------------------
    def test_r1_capacidad_archivada_y_cambio_abierto(self):
        cerrado = self.cambio_cerrado()
        abierto = self.cambio_importado('Títulos largos', 'notas', MODIFICA)
        with contextlib.redirect_stdout(io.StringIO()):
            f.comando_resumen(False, None)
        texto = self.texto()
        rid = f.leer(cerrado)[1]['requisitos'][0]
        self.assertIn(f'| titulo valido | funcional | `{rid}` | notas.casos_ejecutados, notas.resultados |', texto)
        self.assertIn(cerrado, texto)
        self.assertIn(f'### {abierto} — Títulos largos', texto)
        self.assertIn('revisión humana aprobada', texto)  # lo que le falta
        self.assertNotIn('#### Scenario', texto)  # sin escenarios: enlaza la spec
        self.assertIn('openspec/specs/notas/spec.md', texto)
        self.assertTrue(rid)

    def test_r1_requisito_reemplazado(self):
        cerrado = self.cambio_cerrado()
        modifica = self.cambio_importado('Títulos largos', 'notas', MODIFICA)
        self.marcar_cerrado(modifica, '2099-01-01T00:00:00+00:00')
        with contextlib.redirect_stdout(io.StringIO()):
            f.archivar()
        vigente = self.texto().split('## Lo vigente')[1].split('## Cambios abiertos')[0]
        self.assertEqual(vigente.count('| titulo valido |'), 1)
        self.assertIn(modifica, vigente)
        self.assertNotIn(cerrado, vigente)

    # --- r2: riesgos aceptados y límites declarados -------------------------------------------------------------------
    def test_r2_riesgo_vigente_e_historico(self):
        cerrado = self.cambio_cerrado()
        self.con_riesgo(cerrado)
        with contextlib.redirect_stdout(io.StringIO()):
            f.comando_resumen(False, None)
        vigentes = self.seccion('Riesgos aceptados', 'De cambios con requisitos vigentes')
        self.assertIn('**H-01**', vigentes)
        self.assertIn('Aceptado por Persona fixture: Lo acepto por ahora.', vigentes)
        self.assertNotIn('H-99', self.seccion('Riesgos aceptados'))  # un hallazgo corregido no es un riesgo aceptado
        self.assertEqual(self.seccion('Riesgos aceptados', 'Históricos'), '')  # una subsección vacía no se muestra
        modifica = self.cambio_importado('Títulos largos', 'notas', MODIFICA)  # reemplaza el único requisito del cerrado
        self.marcar_cerrado(modifica, '2099-01-01T00:00:00+00:00')
        with contextlib.redirect_stdout(io.StringIO()):
            f.archivar()
        self.assertNotIn('**H-01**', self.seccion('Riesgos aceptados', 'De cambios con requisitos vigentes'))
        self.assertIn('**H-01**', self.seccion('Riesgos aceptados', 'Históricos'))
        self.assertIn(f'({cerrado}) Un límite de prueba.', self.seccion('Límites declarados', 'Históricos'))

    def test_r2_una_revision_ilegible_se_avisa_y_no_se_omite(self):
        cerrado = self.cambio_cerrado()
        self.con_riesgo(cerrado)
        informe = self.root / 'tareas' / cerrado / 'revisiones' / 'registro-fixture' / 'informe.json'
        informe.write_text('{ esto no es JSON')
        with contextlib.redirect_stdout(io.StringIO()):
            f.comando_resumen(False, None)
        self.assertIn(f'⚠ ({cerrado}) no se pudo leer el informe de la revisión', self.seccion('Límites declarados'))
        carpeta, estado = f.leer(cerrado)
        sin_ruta = {**estado, 'revision': {k: v for k, v in estado['revision'].items() if k != 'decisiones'}}
        f.guardar(carpeta, sin_ruta)  # la revisión guiada perdió la ruta de sus decisiones
        with contextlib.redirect_stdout(io.StringIO()):
            f.comando_resumen(False, None)
        self.assertIn(f'⚠ ({cerrado}) la revisión guiada no registra su documento de decisiones', self.seccion('Riesgos aceptados'))
        f.guardar(carpeta, estado)
        informe.write_text(json.dumps({'hallazgos': 1, 'limites': 'no es una lista'}))  # JSON válido, forma rara
        with contextlib.redirect_stdout(io.StringIO()):
            f.comando_resumen(False, None)  # no se rompe

    def test_r1_carpetas_sin_registro_y_medidas_agrupadas(self):
        self.cambio_cerrado()
        (self.root / 'openspec/changes/20250101-000000-viejo').mkdir()
        abierto = self.cambio_importado('Títulos largos', 'notas', MODIFICA)
        carpeta, estado = f.leer(abierto)
        estado['medidas_pendientes'] = {f'r{i}': {'actor': 'agente-x', 'tipo_actor': 'agente'} for i in range(3)}
        f.guardar(carpeta, estado)
        with contextlib.redirect_stdout(io.StringIO()):
            f.comando_resumen(False, None)
        abiertos = self.seccion('Cambios abiertos')
        self.assertIn('`20250101-000000-viejo`', abiertos)
        self.assertIn('medidas de 3 requisitos: propuestas por agente-x, sin confirmar por una persona', abiertos)

    # --- r3: el veredicto es el del cierre y lo dice --------------------------------------------------------------------
    def test_r3_veredicto_del_cierre(self):
        cerrado = self.cambio_cerrado()
        fecha = f.leer(cerrado)[1]['cierre']['cuando'][:10]
        sin_veredicto = self.cambio_importado('Títulos largos', 'notas', MODIFICA)
        self.marcar_cerrado(sin_veredicto, '2099-01-01T00:00:00+00:00')
        texto_antes = None
        with contextlib.redirect_stdout(io.StringIO()):
            f.comando_resumen(False, None)
            texto_antes = self.texto()
            f.archivar()
        self.assertIn(f'verde al cerrar el {fecha}', texto_antes)
        self.assertIn('no una corrida nueva', texto_antes)
        self.assertIn('sin veredicto registrado (cierre 2099-01-01)', self.texto())

    # --- r4: determinista y sin otros cambios ----------------------------------------------------------------------------
    def test_r4_dos_ejecuciones_seguidas(self):
        self.cambio_cerrado()
        self.git('add', '.')
        self.git('commit', '-qm', 'cerrado')
        huella = f.contexto_producto()['archivos_sha256']
        with contextlib.redirect_stdout(io.StringIO()):
            f.comando_resumen(False, None)
        antes = self.archivos()
        with contextlib.redirect_stdout(io.StringIO()):
            f.comando_resumen(False, None)
        self.assertEqual(self.archivos(), antes)  # mismos bytes, ningún otro archivo
        self.assertEqual(f.contexto_producto()['archivos_sha256'], huella)  # no vence ninguna revisión
        self.assertNotRegex(self.texto(), r'\d{4}-\d{2}-\d{2}T')  # sin fecha de generación

    # --- r5: se sabe cuándo quedó viejo --------------------------------------------------------------------------------
    def test_r5_un_cambio_avanza_despues_de_generar(self):
        self.cambio_cerrado()
        self.assertEqual(self.verificar(None), 0)  # cerrar ya lo dejó al día
        abierto = self.cambio_importado('Títulos largos', 'notas', MODIFICA)
        antes = self.texto()
        self.assertEqual(self.verificar(None), 1)
        self.assertEqual(self.texto(), antes)  # verificar no escribe
        self.assertEqual(self.verificar(Path('no-existe.md')), 1)
        self.assertTrue(abierto)

    def test_r5_editado_a_mano(self):
        self.cambio_cerrado()
        ruta = self.root / '.factory/resumen.md'
        ruta.write_text(ruta.read_text() + 'agregado a mano\n')
        self.assertEqual(self.verificar(None), 1)

    # --- r6: se actualiza al cerrar y al archivar --------------------------------------------------------------------------
    def test_r6_cerrar_y_archivar_lo_regeneran(self):
        cerrado = self.cambio_cerrado()
        self.assertIn(cerrado, self.texto())
        self.assertEqual(self.verificar(None), 0)
        modifica = self.cambio_importado('Títulos largos', 'notas', MODIFICA)
        self.marcar_cerrado(modifica, '2099-01-01T00:00:00+00:00')
        with contextlib.redirect_stdout(io.StringIO()):
            f.archivar()
        self.assertIn(modifica, self.texto().split('## Cambios abiertos')[0])
        self.assertEqual(self.verificar(None), 0)

    def test_r6_un_fallo_del_resumen_no_rompe_el_cierre(self):
        with patch.object(f, 'texto_resumen', side_effect=TypeError('forma rara')):
            cerrado = self.cambio_cerrado()  # no lanza
        self.assertEqual(f.leer(cerrado)[1]['fase'], 'cerrada')
        self.assertEqual(self.verificar(None), 1)  # quedó sin resumen, y se nota
        with contextlib.redirect_stdout(io.StringIO()):
            f.comando_resumen(False, None)
        self.assertEqual(self.verificar(None), 0)

    def test_r6_salida_en_otra_ruta(self):
        self.cambio_cerrado()
        with contextlib.redirect_stdout(io.StringIO()):
            f.comando_resumen(False, Path('RESUMEN.md'))
        raiz = (self.root / 'RESUMEN.md').read_text()
        self.assertIn('](openspec/specs/notas/spec.md)', raiz)  # los enlaces se calculan desde donde se escribe
        self.assertIn('](../openspec/specs/notas/spec.md)', self.texto())
        self.assertEqual(raiz.split('\n', 1)[1].replace('](openspec/', '](../openspec/'), self.texto().split('\n', 1)[1])
        with self.assertRaises(f.FactoryError):
            f.comando_resumen(False, Path('../afuera.md'))


if __name__ == '__main__':
    unittest.main()
