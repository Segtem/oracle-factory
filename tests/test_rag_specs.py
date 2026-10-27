"""Contratos rs1–rs4: preguntar cuenta y lista las specs desde sus carpetas, en proyectos aislados."""
import contextlib
import io
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_archivo as base
from oracle_factory import consultas, rag

f = base.f


class RagSpecs(unittest.TestCase):
    setUp, escribe, git = base.Archivo.setUp, base.Archivo.escribe, base.Archivo.git

    def preparar(self, vigentes=2):
        """Specs vigentes (capacidades «vieja», «vieja2»), un cambio abierto con su spec, uno cerrado y uno abandonado con la suya."""
        ruta = self.root / '.factory/config.json'
        datos = json.loads(ruta.read_text())
        datos['rag'] = {'embeddings': {'proveedor': 'ninguno'}}
        ruta.write_text(json.dumps(datos))
        for nombre in ('vieja', 'vieja2')[:vigentes]:
            vigente = self.root / f'openspec/specs/{nombre}/spec.md'
            vigente.parent.mkdir(parents=True)
            vigente.write_text(f'# Capability: {nombre}\n')
        f.AGENTE = 'codex'
        try:
            self.abierto = f.nuevo('Abierto', capacidad='nueva', sufijo='abierto')
            self.cerrado = f.nuevo('Cerrado', capacidad='otra', sufijo='cerrado')
            self.abandonado = f.nuevo('Abandonado', capacidad='tercera', sufijo='abandonado')
        finally:
            f.AGENTE = None
        for ident, fase in ((self.cerrado, 'cerrada'), (self.abandonado, 'abandonada')):
            carpeta, estado = f.leer(ident)
            estado['fase'] = fase
            f.ruta_registro(carpeta).write_text(json.dumps(estado))

    def preguntar(self, pregunta):
        return rag.preguntar(f, pregunta)

    # --- rs1: contar y listar -----------------------------------------------------------------------------------------------
    def test_rs1_cuantas_specs_hay_da_dos_numeros_y_cita_los_archivos(self):
        self.preparar()
        r = self.preguntar('¿Cuántas specs hay?')
        self.assertEqual(r['tipo'], 'registro')
        self.assertEqual(r['valor'], {'vigentes': 2, 'en_cambios_abiertos': 1})  # ni el cerrado ni el abandonado cuentan como abiertos
        self.assertEqual(r['respuesta'], 'Hay 2 specs vigentes (una por capacidad) y 1 en cambios abiertos.')
        self.assertEqual(sorted(r['fuentes'][0]['archivos']), sorted([
            'openspec/specs/vieja/spec.md', 'openspec/specs/vieja2/spec.md', f'openspec/changes/{self.abierto}/specs/nueva/spec.md']))
        self.assertEqual(r['resultados'], [])  # no son pasajes sueltos

    def test_rs1_cuales_son_lista_capacidad_estado_y_ruta(self):
        self.preparar()
        r = self.preguntar('Mostrame las specs')
        self.assertIn('- vieja · vigente · openspec/specs/vieja/spec.md', r['respuesta'])
        self.assertIn(f'- nueva · en cambio abierto ({self.abierto}) · openspec/changes/{self.abierto}/specs/nueva/spec.md',
                      r['respuesta'])
        self.assertNotIn(self.cerrado, r['respuesta'])
        self.assertNotIn(self.abandonado, r['respuesta'])
        self.assertIn('- vieja2 · vigente · openspec/specs/vieja2/spec.md', r['respuesta'])

    def test_rs1_con_una_sola_spec_vigente_va_en_singular(self):
        self.preparar(vigentes=1)
        self.assertEqual(self.preguntar('¿Cuántas specs hay?')['respuesta'],
                         'Hay 1 spec vigente (una por capacidad) y 1 en cambios abiertos.')

    def test_rs1_sin_ninguna_spec_dice_cero(self):
        ruta = self.root / '.factory/config.json'
        datos = json.loads(ruta.read_text())
        datos['rag'] = {'embeddings': {'proveedor': 'ninguno'}}
        ruta.write_text(json.dumps(datos))
        r = self.preguntar('cuantas spec hay?')
        self.assertEqual(r['valor'], {'vigentes': 0, 'en_cambios_abiertos': 0})

    def test_rs1_funciona_por_la_cli(self):
        self.preparar()
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(f.main(['--proyecto', str(self.root), 'preguntar', 'Cuantas spec hay?']), 0)
        self.assertIn('Hay 2 specs vigentes (una por capacidad) y 1 en cambios abiertos.', salida.getvalue())
        self.assertNotIn('No encontré respaldo', salida.getvalue())

    # --- rs2: filtros no admitidos ------------------------------------------------------------------------------------------
    def test_rs2_un_filtro_no_admitido_se_rechaza_sin_pasajes(self):
        self.preparar()
        for palabra in ('no', 'excepto', 'sin', 'desde', 'hasta', 'ayer', 'hoy', 'semana', 'mes', 'año', 'fecha', 'periodo'):
            self.assertEqual(consultas.interpretar_specs(f'cuantas specs hay {palabra}')['tipo'], 'consulta_no_admitida', palabra)
        for pregunta in ('¿Cuántas specs hay desde ayer?', 'cuantas specs no estan aprobadas'):
            r = self.preguntar(pregunta)
            self.assertEqual(r['tipo'], 'consulta_no_admitida', pregunta)
            self.assertIn('no está admitido', r['respuesta'])
            self.assertEqual(r['resultados'], [])

    def test_rs2_una_compuesta_o_de_otro_tema_no_es_de_este_camino(self):
        self.assertEqual(consultas.interpretar_specs('cuantas specs hay en total')['operacion'], 'contar')  # lo normal sí entra
        for pregunta in ('cuantas specs hay en el repositorio de oracle', '¿Cuántas specs hay y cómo se aprueban?', '¿Cómo se escribe una spec?', 'qué es una capacidad en factory y para qué sirve'):
            self.assertIsNone(consultas.interpretar_specs(pregunta), pregunta)

    # --- rs3: lo demás no cambia -----------------------------------------------------------------------------------------
    def test_rs3_cambios_abiertos_sigue_igual(self):
        self.preparar()
        r = self.preguntar('¿Cuántos cambios abiertos hay?')
        self.assertEqual(r['tipo'], 'registro')
        self.assertEqual(r['respuesta'], 'Hay 1 cambios abiertos.')
        self.assertEqual(r['valor'], 1)

    def test_rs3_una_pregunta_que_nombra_cambios_y_specs_no_cambia_de_camino(self):
        self.assertIsNone(consultas.interpretar_specs('cuantos cambios tienen spec'))
        self.assertIsNone(consultas.interpretar('cuantas specs hay'))

    # --- rs4: salvaguardas de la vuelta 1 --------------------------------------------------------------------------------
    def test_rs4_una_pregunta_que_explica_no_es_de_contar_ni_listar(self):
        for pregunta in ('¿Qué son las specs?', '¿Qué son las capacidades?', '¿Qué dice la spec sobre no modificar archivos?',
                         '¿Qué especificaciones no admiten cambios?', '¿Qué spec define el periodo de prueba?',
                         '¿Qué dice la spec sin entrar en detalles?', 'cómo se escribe una spec sin errores'):
            self.assertIsNone(consultas.interpretar_specs(pregunta), pregunta)
        self.preparar()
        self.assertNotIn(self.preguntar('¿Qué son las specs?')['tipo'], ('registro', 'consulta_no_admitida'))

    def test_rs4_lo_compuesto_o_con_cambios_va_al_modelo_aunque_traiga_un_filtro(self):
        for pregunta in ('¿Cuántos cambios y cuántas specs hay hoy?', '¿Cuántas specs hay y cuántos cambios sin spec?',
                         'cuantos cambios tienen spec hoy', 'cuantas specs hay y cuales no estan aprobadas'):
            self.assertIsNone(consultas.interpretar_specs(pregunta), pregunta)
        self.preparar()
        self.assertNotIn(self.preguntar('¿Cuántos cambios y cuántas specs hay hoy?')['tipo'], ('registro', 'consulta_no_admitida'))

    def test_rs4_otros_filtros_de_estado_se_rechazan(self):
        self.preparar()
        for pregunta in ('cuantas specs estan aprobadas', 'cuantas specs hay en revision', 'cuales specs estan pendientes',
                         'cuantas specs cerradas hay', 'cuantas specs nuevas hay', 'cuantas specs archivadas hay'):
            r = self.preguntar(pregunta)
            self.assertEqual(r['tipo'], 'consulta_no_admitida', pregunta)
            self.assertEqual(r['resultados'], [])

    def test_rs4_vigentes_y_abiertas_se_responden_con_las_dos_cantidades_rotuladas(self):
        self.preparar()
        for pregunta in ('¿Cuántas specs vigentes hay?', 'cuantas specs abiertas hay', 'Mostrame las specs vigentes'):
            r = self.preguntar(pregunta)
            self.assertEqual(r['valor'], {'vigentes': 2, 'en_cambios_abiertos': 1}, pregunta)
            self.assertIn('2 specs vigentes', r['respuesta'])

    def test_rs4_cuales_especificaciones_y_capacidades_tambien_entran(self):
        self.preparar()
        for pregunta in ('cuales son las capacidades', 'cuantas especificaciones hay', 'que specs hay', 'lista las especificaciones'):
            self.assertEqual(self.preguntar(pregunta)['tipo'], 'registro', pregunta)

    def test_rs4_un_enlace_simbolico_no_cuenta_ni_se_cita(self):
        self.preparar()
        afuera = Path(self.tmp.name if hasattr(self, 'tmp') else self.root.parent) / 'afuera'
        (afuera / 'spec.md').parent.mkdir(parents=True, exist_ok=True)
        (afuera / 'spec.md').write_text('# fuera\n')
        (self.root / 'openspec/specs/externo').symlink_to(afuera, target_is_directory=True)  # carpeta enlazada
        (self.root / 'openspec/specs/archivo').mkdir()
        (self.root / 'openspec/specs/archivo/spec.md').symlink_to(afuera / 'spec.md')  # spec.md enlazado
        carpeta = self.root / f'openspec/changes/{self.abierto}/specs/enlazada'
        carpeta.symlink_to(afuera, target_is_directory=True)  # enlace dentro de un cambio abierto
        r = self.preguntar('¿Cuántas specs hay?')
        self.assertEqual(r['valor'], {'vigentes': 2, 'en_cambios_abiertos': 1})
        self.assertFalse([a for a in r['fuentes'][0]['archivos'] if 'externo' in a or 'archivo' in a or 'enlazada' in a])

    def test_rs4_una_pregunta_de_contenido_con_cuales_o_cuantas_no_se_intercepta(self):
        for pregunta in ('¿Cuáles capacidades no tienen tests?', '¿Cuáles specs definen el periodo de prueba?',
                         'mostrame la spec sin entrar en detalles', 'cuales specs no requieren confirmacion',
                         '¿Cuántos requisitos no tienen tests en la spec?'):
            self.assertIsNone(consultas.interpretar_specs(pregunta), pregunta)
        self.preparar()
        self.assertNotIn(self.preguntar('¿Cuáles capacidades no tienen tests?')['tipo'], ('registro', 'consulta_no_admitida'))

    def test_rs4_abandonadas_y_fechas_con_operando_se_rechazan(self):
        self.preparar()
        for pregunta in ('cuantas specs abandonadas hay', 'cuales specs estan abandonadas', 'lista las specs abandonadas',
                         'cuantas specs hay desde el 1 de octubre', 'cuantas specs hay en los ultimos 7 dias',
                         'cuantas specs hay del 1 de octubre', 'cuantas specs hay del 2026', 'cuantas specs hay de la semana pasada',
                         'cuantas specs hay en los ultimos 3 meses', 'cuantas specs hay esta semana', 'cuantas specs hay del ano pasado',
                         'cuantas specs hay al 1 de octubre', 'cuantas specs hay en las ultimas 2 semanas',
                         'cuantas specs hay en estos meses', 'cuantas specs hay en estas semanas', 'cuantas specs hay a la fecha',
                         'cuantas specs hay de ayer a hoy', 'cuantas specs hay en estos ultimos 7 dias',
                         'cuantas specs hay en unas semanas', 'cuantas specs hay en unos dias', 'cuantas specs hay en una semana', 'cuantas specs hay en un mes',
                         'cuantas specs hay en ese mes', 'cuantas specs hay en esa semana', 'cuantas specs hay en esos meses',
                         'cuantas specs hay en esas semanas', 'cuantas specs hay por semana', 'cuantas specs hay para esta semana'):
            r = self.preguntar(pregunta)
            self.assertEqual(r['tipo'], 'consulta_no_admitida', pregunta)
            self.assertEqual(r['resultados'], [])

    def test_rs4_la_fuente_trae_criterio_cita_y_huella_del_inventario(self):
        self.preparar()
        fuente = self.preguntar('¿Cuántas specs hay?')['fuentes'][0]
        self.assertEqual(fuente['ruta'], 'specs')
        self.assertEqual(fuente['criterio'], {'tema': 'specs', 'operacion': 'contar'})
        self.assertEqual(fuente['cita'], 'specs:{"operacion": "contar", "tema": "specs"}')
        self.assertEqual((fuente['directorio'], fuente['directorio_existe']), ('openspec', True))
        self.assertRegex(fuente['inventario_sha256'], r'^[0-9a-f]{64}$')
        nueva = self.root / 'openspec/specs/vieja3/spec.md'
        nueva.parent.mkdir()
        nueva.write_text('# Capability: vieja3\n')
        self.assertNotEqual(self.preguntar('¿Cuántas specs hay?')['fuentes'][0]['inventario_sha256'], fuente['inventario_sha256'])


if __name__ == '__main__':
    unittest.main()
