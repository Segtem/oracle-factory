"""Las pruebas como práctica de desarrollo, sin bloquear: escenarios pp1–pp3, en proyectos temporales."""
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_archivo as _archivo  # noqa: E402
from oracle_factory import estructura, pruebas  # noqa: E402

f = _archivo.f
SHA = 'abc1234'


def spec(*requisitos):
    """Una spec con un requisito por cada (nombre, líneas extra) dado."""
    cuerpo = ['# Capability: demo', '', '## ADDED Requirements', '']
    for nombre, extra in requisitos:
        cuerpo += [f'### Requirement: {nombre}', 'Tipo: funcional', *extra, f'El sistema DEBE {nombre}.', '',
                   '#### Scenario: uno', '- DADO a', '- CUANDO b', '- ENTONCES c', '']
    return '\n'.join(cuerpo)


class Pruebas(unittest.TestCase):
    setUp, escribe, git, salida, cambio_importado = (_archivo.Archivo.setUp, _archivo.Archivo.escribe, _archivo.Archivo.git,
                                                     _archivo.Archivo.salida, _archivo.Archivo.cambio_importado)

    def cambio(self, *requisitos):
        ident = self.cambio_importado('Demo', 'demo', spec(*requisitos))
        self.salida()
        return ident

    def ids(self, ident, *slugs):
        """Los ids de los requisitos con esos nombres (f.leer los da ordenados por id, no por orden de la spec)."""
        por_slug = {r.split('.', 1)[1]: r for r in f.leer(ident)[1]['requisitos']}
        return [por_slug[x] for x in slugs]

    def reescribir_spec_aprobada(self, ident, texto):
        """Cambia la spec y deja su huella como la aprobada, como si así se hubiera aprobado."""
        carpeta, estado = f.leer(ident)
        (self.root / estado['spec']).write_text(texto, encoding='utf-8')
        estado['spec_sha256'] = hashlib.sha256(texto.encode('utf-8')).hexdigest()
        f.guardar(carpeta, estado)

    def trazabilidad(self, ident, por_requisito):
        """El trazabilidad.json que dejaría el sensor del candidato SHA: {rid: [casos]}."""
        destino = estructura.ruta_canonica(self.root, ident, 'evidencia', SHA)
        destino.mkdir(parents=True, exist_ok=True)
        (destino / 'trazabilidad.json').write_text(json.dumps({
            'esquema': 'oracle-factory.trazabilidad-casos/1', 'requisitos': por_requisito, 'casos': {}}))

    def estado(self, ident, candidato=SHA):
        """(texto de `estado`, datos de `estado --json`) con el candidato vigente dado."""
        with patch.object(f, 'candidato_vigente', return_value=candidato):
            self.salida()
            f.mostrar(ident)
            texto = self.salida()
            return texto, f.datos_estado(ident)

    def avisos_de_pruebas(self, texto):
        return [l for l in texto.splitlines() if l.startswith('Aviso:') and 'prueba' in l.lower()]

    # --- pp1: la plantilla de tareas pide escribir primero las pruebas --------------------------------------------------
    def test_pp1_un_cambio_nuevo_en_espanol_pide_las_pruebas_antes_de_implementar(self):
        tareas = (self.root / 'openspec/changes' / f.nuevo('Uno', 'algo') / 'tasks.md').read_text(encoding='utf-8')
        lineas = [l for l in tareas.splitlines() if l.startswith('- [ ]')]
        [pruebas_] = [i for i, l in enumerate(lineas) if 'escribir' in l.lower() and 'pruebas de cada escenario' in l.lower()]
        [implementar] = [i for i, l in enumerate(lineas) if 'implementar y correr las pruebas' in l.lower()]
        self.assertLess(pruebas_, implementar)

    def test_pp1_un_cambio_nuevo_en_ingles_pide_las_pruebas_antes_de_implementar(self):
        tareas = (self.root / 'openspec/changes' / f.nuevo('Uno', 'algo', idioma='en') / 'tasks.md').read_text(encoding='utf-8')
        lineas = [l for l in tareas.splitlines() if l.startswith('- [ ]')]
        [pruebas_] = [i for i, l in enumerate(lineas) if 'write' in l.lower() and 'tests for each scenario' in l.lower()]
        [implementar] = [i for i, l in enumerate(lineas) if 'implement and run the product tests' in l.lower()]
        self.assertLess(pruebas_, implementar)
        self.assertNotIn('pruebas de cada escenario', tareas)

    def test_pp1_el_paso_nuevo_no_cambia_los_demas_pasos(self):
        tareas = (self.root / 'openspec/changes' / f.nuevo('Uno', 'algo') / 'tasks.md').read_text(encoding='utf-8')
        for paso in ('revisar y aceptar proposal.md', 'importar requisitos Oracle', 'acordar medidas y evidencia',
                     'implementar y correr las pruebas del producto', 'revisar el diff', 'correr Oracle', 'decidir si se cierra'):
            self.assertIn(paso, tareas)

    # --- pp2: el estado avisa de los requisitos sin pruebas, sin bloquear -----------------------------------------------
    def test_pp2_un_requisito_sin_casos_se_nombra_y_el_otro_no(self):
        ident = self.cambio(('hacer uno', []), ('hacer dos', []))
        uno, dos = self.ids(ident, 'hacer_uno', 'hacer_dos')
        self.trazabilidad(ident, {uno: ['test_x.A.test_uno'], dos: []})
        antes = f.datos_estado(ident)
        texto, datos = self.estado(ident)
        aviso = ' '.join(self.avisos_de_pruebas(texto))
        self.assertIn(dos, aviso)
        self.assertNotIn(uno, aviso)
        self.assertEqual(datos['pruebas']['sin_casos'], [dos])
        self.assertFalse(datos['pruebas']['sin_trazabilidad'])
        self.assertTrue(any(dos in a for a in datos['avisos']))
        # no bloquea: pendientes y próximo paso son los mismos que sin el aviso
        self.assertEqual((datos['pendientes'], datos['proximo_paso']), (antes['pendientes'], antes['proximo_paso']))
        self.assertFalse(any('prueba' in p.lower() for p in datos['pendientes']))

    def test_pp2_un_requisito_ausente_de_la_trazabilidad_tambien_cuenta_como_sin_casos(self):
        ident = self.cambio(('hacer uno', []), ('hacer dos', []))
        uno, dos = self.ids(ident, 'hacer_uno', 'hacer_dos')
        self.trazabilidad(ident, {uno: ['test_x.A.test_uno']})
        self.assertEqual(self.estado(ident)[1]['pruebas']['sin_casos'], [dos])

    def test_pp2_un_candidato_sin_trazabilidad_lo_dice(self):
        ident = self.cambio(('hacer uno', []))
        texto, datos = self.estado(ident)
        [aviso] = self.avisos_de_pruebas(texto)
        self.assertIn('no tiene trazabilidad de pruebas', aviso)
        self.assertTrue(datos['pruebas']['sin_trazabilidad'])
        self.assertEqual(datos['pruebas']['sin_casos'], [])
        self.assertEqual(datos['pendientes'], f.datos_estado(ident)['pendientes'])

    def test_pp2_una_trazabilidad_ilegible_cuenta_como_sin_trazabilidad_y_no_rompe_el_estado(self):
        ident = self.cambio(('hacer uno', []))
        destino = estructura.ruta_canonica(self.root, ident, 'evidencia', SHA)
        destino.mkdir(parents=True)
        for contenido in ('{no es json', '[]', '{"requisitos": 3}'):
            (destino / 'trazabilidad.json').write_text(contenido)
            with self.subTest(contenido=contenido):
                texto, datos = self.estado(ident)
                self.assertTrue(datos['pruebas']['sin_trazabilidad'])
                self.assertTrue(self.avisos_de_pruebas(texto))

    def test_pp2_una_trazabilidad_de_otro_esquema_no_se_toma_por_valida(self):
        ident = self.cambio(('hacer uno', []))
        uno = f.leer(ident)[1]['requisitos'][0]
        destino = estructura.ruta_canonica(self.root, ident, 'evidencia', SHA)
        destino.mkdir(parents=True)
        (destino / 'trazabilidad.json').write_text(json.dumps({'esquema': 'otro/1', 'requisitos': {uno: ['test_x.A.test_uno']}}))
        self.assertTrue(self.estado(ident)[1]['pruebas']['sin_trazabilidad'])

    def test_pp2_una_trazabilidad_que_es_un_enlace_simbolico_no_se_sigue(self):
        ident = self.cambio(('hacer uno', []))
        uno = f.leer(ident)[1]['requisitos'][0]
        fuera = self.root / 'fuera.json'
        fuera.write_text(json.dumps({'esquema': 'oracle-factory.trazabilidad-casos/1', 'requisitos': {uno: ['test_x.A.test_uno']}, 'casos': {}}))
        destino = estructura.ruta_canonica(self.root, ident, 'evidencia', SHA)
        destino.mkdir(parents=True)
        (destino / 'trazabilidad.json').symlink_to(fuera)
        self.assertTrue(self.estado(ident)[1]['pruebas']['sin_trazabilidad'])

    def test_pp2_con_casos_en_todos_no_hay_aviso_de_pruebas(self):
        ident = self.cambio(('hacer uno', []), ('hacer dos', []))
        uno, dos = self.ids(ident, 'hacer_uno', 'hacer_dos')
        self.trazabilidad(ident, {uno: ['test_x.A.test_uno'], dos: ['test_x.A.test_dos']})
        texto, datos = self.estado(ident)
        self.assertEqual(self.avisos_de_pruebas(texto), [])
        self.assertEqual(datos['pruebas'], {'sin_trazabilidad': False, 'sin_casos': [], 'excepciones': {}, 'invalidas': []})
        self.assertFalse(any('prueba' in a.lower() for a in datos['avisos']))

    def test_pp2_sin_candidato_todavia_no_hay_nada_que_avisar(self):
        ident = self.cambio(('hacer uno', []))
        texto, datos = self.estado(ident, candidato=None)
        self.assertEqual(self.avisos_de_pruebas(texto), [])
        self.assertIsNone(datos['pruebas'])

    def test_pp2_un_cambio_sin_requisitos_importados_o_cerrado_no_avisa(self):
        ident = f.nuevo('Sin importar', 'algo')
        self.assertIsNone(self.estado(ident)[1]['pruebas'])
        cerrado = self.cambio(('hacer uno', []))
        carpeta, estado = f.leer(cerrado)
        estado['fase'] = 'cerrada'
        f.guardar(carpeta, estado)
        self.assertIsNone(self.estado(cerrado)[1]['pruebas'])

    # --- pp3: una excepción declarada en la spec explica por qué no hay pruebas -------------------------------------------
    def test_pp3_una_excepcion_con_motivo_se_muestra_y_ese_requisito_no_avisa(self):
        ident = self.cambio(('hacer uno', ['Pruebas: no aplica — es sólo un texto de ayuda']), ('hacer dos', []))
        uno, dos = self.ids(ident, 'hacer_uno', 'hacer_dos')
        self.trazabilidad(ident, {uno: [], dos: []})
        texto, datos = self.estado(ident)
        self.assertEqual(datos['pruebas']['sin_casos'], [dos])
        self.assertEqual(datos['pruebas']['excepciones'], {uno: 'es sólo un texto de ayuda'})
        self.assertIn(f'Pruebas: {uno} no aplica — es sólo un texto de ayuda', texto)
        aviso = ' '.join(self.avisos_de_pruebas(texto))
        self.assertIn(dos, aviso)
        self.assertNotIn(uno, aviso)

    def test_pp3_la_excepcion_tambien_vale_sin_trazabilidad(self):
        ident = self.cambio(('hacer uno', ['Pruebas: no aplica - es documentación']))
        uno = f.leer(ident)[1]['requisitos'][0]
        texto, datos = self.estado(ident)
        self.assertEqual(datos['pruebas']['excepciones'], {uno: 'es documentación'})  # con guion simple
        self.assertTrue(datos['pruebas']['sin_trazabilidad'])  # y lo demás se sigue avisando

    def test_pp3_una_excepcion_sin_motivo_se_rechaza_al_aprobar_la_spec_y_no_se_modifica_el_registro(self):
        ident = f.nuevo('Sin motivo', 'demo')
        carpeta, estado = f.leer(ident)
        (carpeta / 'proposal.md').write_text('# Sin motivo\n\nFixture.\n', encoding='utf-8')
        registro = (self.root / '.factory/cambios' / ident / 'factory.json').read_text()
        for linea in ('Pruebas: no aplica', 'Pruebas: no aplica —', 'Pruebas: no aplica -   '):
            with self.subTest(linea=linea):
                (self.root / estado['spec']).write_text(spec(('hacer uno', [linea])), encoding='utf-8')
                with self.escribe('1'), self.assertRaisesRegex(f.FactoryError, 'necesita un motivo'):
                    f.aprobar_spec(ident)
                self.assertEqual((self.root / '.factory/cambios' / ident / 'factory.json').read_text(), registro)

    def test_pp3_una_excepcion_sin_motivo_tambien_se_rechaza_al_importar(self):
        ident = self.cambio(('hacer uno', []))
        carpeta, estado = f.leer(ident)
        (self.root / estado['spec']).write_text(spec(('hacer uno', ['Pruebas: no aplica'])), encoding='utf-8')
        estado['spec_aprobada']['documentos'] = f.documentos(carpeta, estado)  # como si se hubiera aprobado así
        f.guardar(carpeta, estado)
        with self.assertRaisesRegex(f.FactoryError, 'necesita un motivo'):
            f.importar(ident)

    def test_pp3_una_excepcion_sin_motivo_que_llego_al_estado_no_exceptua_y_se_avisa(self):
        ident = self.cambio(('hacer uno', []))
        uno = f.leer(ident)[1]['requisitos'][0]
        carpeta, estado = f.leer(ident)
        self.reescribir_spec_aprobada(ident, spec(('hacer uno', ['Pruebas: no aplica'])))
        self.trazabilidad(ident, {uno: []})
        texto, datos = self.estado(ident)
        self.assertEqual(datos['pruebas']['excepciones'], {})
        self.assertEqual(datos['pruebas']['sin_casos'], [uno])
        self.assertEqual(len(datos['pruebas']['invalidas']), 1)
        self.assertIn('necesita un motivo', ' '.join(datos['pruebas']['invalidas']))
        self.assertTrue(any('necesita un motivo' in l for l in texto.splitlines()))

    def test_pp3_un_valor_desconocido_de_pruebas_se_rechaza_en_vez_de_ignorarse(self):
        with self.assertRaisesRegex(pruebas.PruebasInvalidas, 'sólo admite'):
            pruebas.excepciones(spec(('hacer uno', ['Pruebas: sí'])))

    def test_pp3_la_linea_pruebas_solo_cuenta_en_la_cabecera_del_requisito_no_en_los_escenarios(self):
        texto = spec(('hacer uno', [])).replace('- ENTONCES c', '- ENTONCES c\nPruebas: no aplica — no vale aquí')
        self.assertEqual(pruebas.excepciones(texto), {})

    def test_pp3_la_excepcion_se_asocia_al_requisito_por_su_nombre_y_no_a_otro(self):
        texto = spec(('hacer uno', []), ('hacer dos', ['Pruebas: no aplica — motivo dos']))
        self.assertEqual(pruebas.excepciones(texto), {'hacer_dos': 'motivo dos'})

    def test_pp3_lo_que_la_spec_retira_no_lleva_excepcion(self):
        texto = ('# Capability: demo\n\n## REMOVED Requirements\n\n### Requirement: viejo\nPruebas: no aplica\nEl sistema DEBE x.\n\n'
                 '## ADDED Requirements\n\n### Requirement: nuevo\nPruebas: no aplica — motivo\nEl sistema DEBE y.\n')
        self.assertEqual(pruebas.excepciones(texto), {'nuevo': 'motivo'})

    def test_pp3_sin_excepciones_la_spec_se_lee_como_siempre(self):
        self.assertEqual(pruebas.excepciones(spec(('hacer uno', []))), {})
        self.assertEqual(pruebas.excepciones(''), {})

    # --- las revisiones: lo que el aviso no debía callar ni inventar ---------------------------------------------------------
    def test_pp3_una_excepcion_mal_escrita_se_avisa_aunque_todavia_no_haya_candidato(self):
        ident = self.cambio(('hacer uno', []))
        self.reescribir_spec_aprobada(ident, spec(('hacer uno', ['Pruebas: no aplica'])))
        texto, datos = self.estado(ident, candidato=None)
        self.assertEqual(datos['pruebas']['sin_casos'], [])
        self.assertFalse(datos['pruebas']['sin_trazabilidad'])
        self.assertIn('necesita un motivo', ' '.join(datos['pruebas']['invalidas']))
        self.assertTrue(any('necesita un motivo' in l for l in texto.splitlines()))

    def test_pp3_una_linea_mala_no_borra_las_excepciones_buenas_de_los_otros_requisitos(self):
        ident = self.cambio(('hacer uno', []), ('hacer dos', []))
        uno, dos = self.ids(ident, 'hacer_uno', 'hacer_dos')
        self.reescribir_spec_aprobada(ident, spec(('hacer uno', ['Pruebas: no aplica — es ayuda']), ('hacer dos', ['Pruebas: no aplica'])))
        self.trazabilidad(ident, {uno: [], dos: []})
        datos = self.estado(ident)[1]['pruebas']
        self.assertEqual(datos['excepciones'], {uno: 'es ayuda'})
        self.assertEqual(datos['sin_casos'], [dos])
        self.assertEqual(len(datos['invalidas']), 1)

    def test_pp3_lo_escrito_en_la_spec_despues_de_aprobarla_no_cuenta_como_aceptado(self):
        ident = self.cambio(('hacer uno', []))
        uno = f.leer(ident)[1]['requisitos'][0]
        carpeta, estado = f.leer(ident)
        (self.root / estado['spec']).write_text(spec(('hacer uno', ['Pruebas: no aplica — pretexto'])), encoding='utf-8')
        self.trazabilidad(ident, {uno: []})
        datos = self.estado(ident)[1]['pruebas']
        self.assertEqual(datos['excepciones'], {})
        self.assertEqual(datos['sin_casos'], [uno])
        self.assertIn('cambió desde su aprobación', ' '.join(datos['invalidas']))

    def test_pp3_una_spec_sin_excepciones_cambiada_despues_de_aprobarla_no_avisa_de_excepciones(self):
        ident = self.cambio(('hacer uno', []))
        carpeta, estado = f.leer(ident)
        (self.root / estado['spec']).write_text(spec(('hacer uno', []), ('otro', [])), encoding='utf-8')
        self.assertEqual(self.estado(ident)[1]['pruebas']['invalidas'], [])

    def test_pp3_la_spec_que_es_un_enlace_simbolico_no_se_sigue(self):
        ident = self.cambio(('hacer uno', []))
        carpeta, estado = f.leer(ident)
        ruta = self.root / estado['spec']
        fuera = self.root / 'fuera.md'
        fuera.write_text(spec(('hacer uno', ['Pruebas: no aplica — desde afuera'])), encoding='utf-8')
        ruta.unlink()
        ruta.symlink_to(fuera)
        datos = self.estado(ident)[1]['pruebas']
        self.assertEqual(datos['excepciones'], {})
        self.assertIn('enlaces simbólicos', ' '.join(datos['invalidas']))

    def test_pp3_una_spec_que_falta_se_avisa_y_no_rompe_el_estado(self):
        ident = self.cambio(('hacer uno', []))
        carpeta, estado = f.leer(ident)
        (self.root / estado['spec']).unlink()
        datos = self.estado(ident)[1]['pruebas']
        self.assertIn('no pude leer la spec', ' '.join(datos['invalidas']))

    def test_pp3_valores_raros_en_el_registro_no_rompen_el_estado(self):
        ident = self.cambio(('hacer uno', []))
        carpeta, base = f.leer(ident)
        for campo, valor in (('spec', None), ('spec', 7), ('spec', ['x']), ('spec', 'a\x00b'), ('requisitos', 'texto'),
                             ('requisitos', [1, 2]), ('requisitos', {'a': 1})):
            with self.subTest(campo=campo, valor=valor):
                estado = json.loads(json.dumps(base))
                estado[campo] = valor
                resultado = pruebas.datos(self.root, ident, estado, SHA)  # lo que importa: no cae
                if campo == 'requisitos':
                    self.assertIsNone(resultado)
                else:
                    self.assertIn('no pude leer la spec', ' '.join(resultado['invalidas']))

    def test_pp2_una_carpeta_de_evidencia_enlazada_no_se_sigue(self):
        ident = self.cambio(('hacer uno', []))
        uno = f.leer(ident)[1]['requisitos'][0]
        real = self.root / 'real'
        real.mkdir()
        (real / 'trazabilidad.json').write_text(json.dumps({'esquema': 'oracle-factory.trazabilidad-casos/1',
                                                            'requisitos': {uno: ['test_x.A.test_uno']}, 'casos': {}}))
        destino = estructura.ruta_canonica(self.root, ident, 'evidencia', SHA)
        destino.parent.mkdir(parents=True)
        destino.symlink_to(real)
        self.assertTrue(self.estado(ident)[1]['pruebas']['sin_trazabilidad'])

    def test_pp2_un_cambio_abandonado_no_avisa(self):
        ident = self.cambio(('hacer uno', []))
        carpeta, estado = f.leer(ident)
        estado['fase'] = 'abandonada'
        f.guardar(carpeta, estado)
        self.assertIsNone(pruebas.datos(self.root, ident, f.leer(ident)[1], SHA))

    def test_pp3_un_motivo_hecho_de_guiones_no_es_un_motivo(self):
        for linea in ('Pruebas: no aplica - -', 'Pruebas: no aplica — —', 'Pruebas: no aplica — - —'):
            with self.subTest(linea=linea), self.assertRaisesRegex(pruebas.PruebasInvalidas, 'necesita un motivo'):
                pruebas.excepciones(spec(('hacer uno', [linea])))

    def test_pp3_declarar_dos_veces_pruebas_en_un_requisito_se_rechaza(self):
        with self.assertRaisesRegex(pruebas.PruebasInvalidas, 'declarada dos veces'):
            pruebas.excepciones(spec(('hacer uno', ['Pruebas: no aplica — uno', 'Pruebas: no aplica — dos'])))

    def test_pp3_el_ejemplo_dentro_de_un_bloque_de_codigo_no_cuenta(self):
        texto = spec(('hacer uno', ['```markdown', 'Pruebas: no aplica — ejemplo', '```', 'Pruebas: no aplica — el de verdad']))
        self.assertEqual(pruebas.excepciones(texto), {'hacer_uno': 'el de verdad'})
        sin_motivo = spec(('hacer uno', ['```', 'Pruebas: no aplica', '```']))
        self.assertEqual(pruebas.excepciones(sin_motivo), {})  # un ejemplo mal escrito dentro del bloque tampoco rechaza

    def test_pp3_la_viñeta_con_asterisco_y_con_guion_se_leen_igual(self):
        for marca in ('-', '*'):
            with self.subTest(marca=marca):
                self.assertEqual(pruebas.excepciones(spec(('hacer uno', [f'{marca} Pruebas: no aplica — motivo']))), {'hacer_uno': 'motivo'})

    def test_pp3_una_seccion_modified_tambien_puede_declarar_la_excepcion(self):
        texto = spec(('hacer uno', ['Pruebas: no aplica — motivo'])).replace('ADDED', 'MODIFIED')
        self.assertEqual(pruebas.excepciones(texto), {'hacer_uno': 'motivo'})

    def test_pp3_el_motivo_conserva_su_texto_con_guiones_y_espacios_internos(self):
        self.assertEqual(pruebas.excepciones(spec(('hacer uno', ['Pruebas: no aplica —  es una prueba - a mano  ']))),
                         {'hacer_uno': 'es una prueba - a mano'})


class Analisis(unittest.TestCase):
    """El núcleo puro: qué requisitos quedan sin casos."""

    def test_el_analisis_de_requisitos_con_y_sin_casos(self):
        trazas = {'esquema': 'oracle-factory.trazabilidad-casos/1', 'requisitos': {'d.a': ['x'], 'd.b': []}, 'casos': {}}
        r = pruebas.analizar(['d.a', 'd.b', 'd.c'], trazas, {})
        self.assertEqual((r['sin_trazabilidad'], r['sin_casos']), (False, ['d.b', 'd.c']))
        self.assertEqual(pruebas.analizar(['d.a'], None, {})['sin_trazabilidad'], True)
        self.assertEqual(pruebas.analizar(['d.a', 'd.b'], trazas, {'d.b': 'motivo'})['sin_casos'], [])
        self.assertEqual(pruebas.analizar(['d.b'], trazas, {'d.b': 'motivo'})['excepciones'], {'d.b': 'motivo'})

    def test_un_caso_de_solo_espacios_no_cuenta_como_caso(self):
        trazas = {'esquema': 'oracle-factory.trazabilidad-casos/1', 'requisitos': {'d.a': ['   ', '\t']}, 'casos': {}}
        self.assertEqual(pruebas.analizar(['d.a'], trazas, {})['sin_casos'], ['d.a'])

    def test_un_caso_vacio_o_no_texto_no_cuenta_como_caso(self):
        trazas = {'esquema': 'oracle-factory.trazabilidad-casos/1', 'requisitos': {'d.a': [''], 'd.b': [None], 'd.c': 'x'}, 'casos': {}}
        self.assertEqual(pruebas.analizar(['d.a', 'd.b', 'd.c'], trazas, {})['sin_casos'], ['d.a', 'd.b', 'd.c'])


if __name__ == '__main__':
    unittest.main()
