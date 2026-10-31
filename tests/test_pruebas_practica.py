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
        estado['spec_aprobada']['documentos'] = f.documentos(carpeta, estado)
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
        [pruebas_] = [i for i, l in enumerate(lineas) if 'escribir primero' in l.lower() and 'tests de cada escenario' in l.lower()]
        [implementar] = [i for i, l in enumerate(lineas) if 'implementar y correr las pruebas' in l.lower()]
        self.assertLess(pruebas_, implementar)

    def test_pp1_un_cambio_nuevo_en_ingles_pide_las_pruebas_antes_de_implementar(self):
        tareas = (self.root / 'openspec/changes' / f.nuevo('Uno', 'algo', idioma='en') / 'tasks.md').read_text(encoding='utf-8')
        lineas = [l for l in tareas.splitlines() if l.startswith('- [ ]')]
        [pruebas_] = [i for i, l in enumerate(lineas) if 'write' in l.lower() and 'tests for each spec scenario' in l.lower()]
        [implementar] = [i for i, l in enumerate(lineas) if 'implement and run the product tests' in l.lower()]
        self.assertLess(pruebas_, implementar)
        self.assertNotIn('tests de cada escenario', tareas)

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
        self.assertIn('no tiene una aprobación vigente', ' '.join(datos['invalidas']))

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

    def test_pp3_valores_raros_en_el_registro_no_hacen_caer_a_pruebas_datos(self):
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

    def test_pp3_un_bloque_de_codigo_con_sangria_tambien_se_ignora(self):
        texto = spec(('hacer uno', ['   ```markdown', '   Pruebas: no aplica', '   ```', 'Pruebas: no aplica — el de verdad']))
        self.assertEqual(pruebas.excepciones(texto), {'hacer_uno': 'el de verdad'})

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

    # --- segunda ronda -----------------------------------------------------------------------------------------------------
    def test_pp3_la_ruta_de_la_spec_no_puede_salir_del_proyecto(self):
        ident = self.cambio(('hacer uno', []))
        (self.root.parent / 'secreto.md').write_text(spec(('hacer uno', ['Pruebas: no aplica — afuera'])), encoding='utf-8')
        base = f.leer(ident)[1]
        for ruta in ('../secreto.md', 'openspec/../../secreto.md', str(self.root.parent / 'secreto.md')):
            with self.subTest(ruta=ruta):
                estado = json.loads(json.dumps(base))
                estado['spec'] = ruta
                datos = pruebas.datos(self.root, ident, estado, SHA)
                self.assertEqual(datos['excepciones'], {})
                self.assertIn('dentro del proyecto', ' '.join(datos['invalidas']))

    def test_pp2_un_candidato_con_forma_rara_no_arma_rutas(self):
        ident = self.cambio(('hacer uno', []))
        estado = f.leer(ident)[1]
        for candidato in ('../x', 'abc/def', 'ABC1234', 'g' * 7):
            with self.subTest(candidato=candidato):
                self.assertIsNone(pruebas.datos(self.root, ident, estado, candidato))

    def test_pp3_una_aprobacion_invalidada_no_deja_vigentes_las_excepciones(self):
        ident = self.cambio(('hacer uno', []))
        self.reescribir_spec_aprobada(ident, spec(('hacer uno', ['Pruebas: no aplica — motivo'])))
        carpeta, estado = f.leer(ident)
        self.assertEqual(self.estado(ident)[1]['pruebas']['excepciones'], {f.leer(ident)[1]['requisitos'][0]: 'motivo'})
        for aprobada in (None, {}, {'documentos': None}, {'documentos': {}}):
            with self.subTest(spec_aprobada=aprobada):
                estado['spec_aprobada'] = aprobada
                f.guardar(carpeta, estado)
                datos = self.estado(ident)[1]['pruebas']
                self.assertEqual(datos['excepciones'], {})
                self.assertIn('no tiene una aprobación vigente', ' '.join(datos['invalidas']))

    def test_pp3_una_excepcion_valida_se_muestra_aunque_todavia_no_haya_candidato(self):
        ident = self.cambio(('hacer uno', []))
        uno = f.leer(ident)[1]['requisitos'][0]
        self.reescribir_spec_aprobada(ident, spec(('hacer uno', ['Pruebas: no aplica — motivo'])))
        texto, datos = self.estado(ident, candidato=None)
        self.assertEqual(datos['pruebas']['excepciones'], {uno: 'motivo'})
        self.assertIn(f'Pruebas: {uno} no aplica — motivo', texto)

    def test_pp3_una_excepcion_mal_escrita_se_avisa_antes_de_importar(self):
        ident = f.nuevo('Sin importar', 'demo')
        carpeta, estado = f.leer(ident)
        (self.root / estado['spec']).write_text(spec(('hacer uno', ['Pruebas: no aplica'])), encoding='utf-8')
        estado['spec_sha256'] = hashlib.sha256((self.root / estado['spec']).read_bytes()).hexdigest()
        estado['spec_aprobada'] = {'documentos': f.documentos(carpeta, estado)}
        f.guardar(carpeta, estado)
        datos = pruebas.datos(self.root, ident, f.leer(ident)[1], None)
        self.assertIn('necesita un motivo', ' '.join(datos['invalidas']))

    def test_pp3_un_requisito_con_varias_lineas_pruebas_queda_sin_excepcion(self):
        casos = {'dos con motivo': ['Pruebas: no aplica — uno', 'Pruebas: no aplica — dos'],
                 'buena y luego sin motivo': ['Pruebas: no aplica — uno', 'Pruebas: no aplica'],
                 'buena y luego un valor raro': ['Pruebas: no aplica — uno', 'Pruebas: sí'],
                 'sin motivo y luego buena': ['Pruebas: no aplica', 'Pruebas: no aplica — dos']}
        for nombre, lineas in casos.items():
            with self.subTest(nombre):
                salida, errores = pruebas.leer(spec(('hacer uno', lineas), ('hacer dos', ['Pruebas: no aplica — otro'])))
                self.assertEqual(salida, {'hacer_dos': 'otro'})
                self.assertTrue(errores)

    def test_pp3_un_numeral_en_la_descripcion_no_cierra_la_cabecera_del_requisito(self):
        texto = spec(('hacer uno', ['#42 sin errores.', 'Pruebas: no aplica']))
        with self.assertRaisesRegex(pruebas.PruebasInvalidas, 'necesita un motivo'):
            pruebas.excepciones(texto)
        for encabezado in ('# Otro título', '## Otra sección', '### Otro', '#### Scenario: x'):  # lo que cierra un requisito en Oracle
            with self.subTest(cierra=encabezado):
                self.assertEqual(pruebas.excepciones(spec(('hacer uno', [encabezado, 'Pruebas: no aplica']))), {})
        for no_encabezado in ('#### Nota', '##### Detalle', '###### Ref', '###', '#42', '#sin espacio'):  # lo que Oracle no toma por encabezado
            with self.subTest(no_cierra=no_encabezado), self.assertRaisesRegex(pruebas.PruebasInvalidas, 'necesita un motivo'):
                pruebas.excepciones(spec(('hacer uno', [no_encabezado, 'Pruebas: no aplica'])))

    def test_pp3_el_reconocimiento_ignora_mayusculas_sangria_y_raya_mediana(self):
        for linea in ('pruebas: NO APLICA — motivo', '   Pruebas: no aplica — motivo', 'Pruebas: no aplica – motivo',
                      'PRUEBAS:  No   Aplica  —  motivo'):
            with self.subTest(linea=linea):
                self.assertEqual(pruebas.excepciones(spec(('hacer uno', [linea]))), {'hacer_uno': 'motivo'})

    def test_pp3_las_excepciones_se_muestran_ordenadas(self):
        datos = {'excepciones': {'d.b': 'dos', 'd.a': 'uno', 'd.c': 'tres'}}
        self.assertEqual(pruebas.lineas(datos), ['Pruebas: d.a no aplica — uno', 'Pruebas: d.b no aplica — dos', 'Pruebas: d.c no aplica — tres'])
        self.assertEqual(pruebas.lineas(None), [])

    def test_pp3_un_registro_sin_la_clave_spec_se_avisa_y_pruebas_datos_no_cae(self):
        ident = self.cambio(('hacer uno', []))
        estado = json.loads(json.dumps(f.leer(ident)[1]))
        del estado['spec']
        self.assertIn('no pude leer la spec', ' '.join(pruebas.datos(self.root, ident, estado, SHA)['invalidas']))

    def test_pp2_una_trazabilidad_que_no_se_puede_leer_cuenta_como_sin_trazabilidad(self):
        ident = self.cambio(('hacer uno', []))
        destino = estructura.ruta_canonica(self.root, ident, 'evidencia', SHA)
        destino.mkdir(parents=True)
        (destino / 'trazabilidad.json').write_text('{}')
        original = Path.read_text

        def falla(ruta, *a, **kw):
            if ruta.name == 'trazabilidad.json':
                raise OSError('sin permiso')
            return original(ruta, *a, **kw)
        with patch.object(Path, 'read_text', falla):
            self.assertTrue(pruebas.datos(self.root, ident, f.leer(ident)[1], SHA)['sin_trazabilidad'])

    # --- tercera ronda -------------------------------------------------------------------------------------------------------
    def test_pp3_una_spec_aprobada_rara_no_hace_caer_a_pruebas_datos(self):
        ident = self.cambio(('hacer uno', []))
        base = f.leer(ident)[1]
        for valor in (5, 'si', ['x'], True, {'documentos': 'no'}, {'documentos': 7}, {'documentos': None}):
            with self.subTest(spec_aprobada=valor):
                estado = json.loads(json.dumps(base))
                estado['spec_aprobada'] = valor
                datos = pruebas.datos(self.root, ident, estado, SHA, {'a': 'b'})
                self.assertEqual(datos['excepciones'], {})

    def test_pp3_cambiar_la_propuesta_despues_de_aprobar_deja_sin_vigencia_las_excepciones(self):
        ident = self.cambio(('hacer uno', []))
        self.reescribir_spec_aprobada(ident, spec(('hacer uno', ['Pruebas: no aplica — motivo'])))
        uno = f.leer(ident)[1]['requisitos'][0]
        self.assertEqual(self.estado(ident)[1]['pruebas']['excepciones'], {uno: 'motivo'})
        propuesta = self.root / 'openspec/changes' / ident / 'proposal.md'
        propuesta.write_text(propuesta.read_text() + '\nUn cambio posterior.\n')
        datos = self.estado(ident)[1]['pruebas']
        self.assertEqual(datos['excepciones'], {})
        self.assertIn('no tiene una aprobación vigente', ' '.join(datos['invalidas']))

    def test_pp3_sin_documentos_para_comparar_las_excepciones_no_cuentan(self):
        ident = self.cambio(('hacer uno', []))
        self.reescribir_spec_aprobada(ident, spec(('hacer uno', ['Pruebas: no aplica — motivo'])))
        estado = f.leer(ident)[1]
        self.assertEqual(pruebas.datos(self.root, ident, estado, SHA, None)['excepciones'], {})
        self.assertEqual(pruebas.datos(self.root, ident, estado, SHA, {})['excepciones'], {})
        self.assertNotEqual(pruebas.datos(self.root, ident, estado, SHA, f.documentos(*f.leer(ident)))['excepciones'], {})

    def test_pp3_la_ausencia_de_documentos_en_los_dos_lados_no_cuenta_como_aprobacion(self):
        ident = self.cambio(('hacer uno', []))
        self.reescribir_spec_aprobada(ident, spec(('hacer uno', ['Pruebas: no aplica — motivo'])))
        base = f.leer(ident)[1]
        for aprobacion, documentos in (({'documentos': None}, None), ({'documentos': {}}, {}), ({}, None), ({'documentos': {}}, None)):
            with self.subTest(aprobacion=aprobacion, documentos=documentos):
                estado = json.loads(json.dumps(base))
                estado['spec_aprobada'] = aprobacion
                self.assertEqual(pruebas.datos(self.root, ident, estado, SHA, documentos)['excepciones'], {})

    def test_pp3_una_spec_que_todavia_no_se_aprobo_lo_dice_sin_decir_que_cambio(self):
        ident = f.nuevo('Nueva', 'demo')
        carpeta, estado = f.leer(ident)
        (self.root / estado['spec']).write_text(spec(('hacer uno', ['Pruebas: no aplica — motivo'])), encoding='utf-8')
        datos = pruebas.datos(self.root, ident, f.leer(ident)[1], None, f.documentos(carpeta, estado))
        self.assertEqual(datos['excepciones'], {})
        self.assertIn('todavía no se aprobó', ' '.join(datos['invalidas']))

    def test_pp3_las_excepciones_aprobadas_se_ven_antes_de_importar_por_el_nombre_del_requisito(self):
        ident = f.nuevo('Antes de importar', 'demo')
        carpeta, estado = f.leer(ident)
        (self.root / estado['spec']).write_text(spec(('hacer uno', ['Pruebas: no aplica — motivo'])), encoding='utf-8')
        (carpeta / 'proposal.md').write_text('# Antes de importar\n\nFixture.\n', encoding='utf-8')
        with self.escribe('1'):
            f.aprobar_spec(ident)
        self.assertEqual(f.leer(ident)[1]['requisitos'], [])
        texto, datos = self.estado(ident)
        self.assertEqual(datos['pruebas']['excepciones'], {'hacer_uno': 'motivo'})
        self.assertIn('Pruebas: hacer_uno no aplica — motivo', texto)

    def test_pp2_un_identificador_con_forma_rara_no_arma_rutas(self):
        ident = self.cambio(('hacer uno', []))
        estado = f.leer(ident)[1]
        for raro in ('../../..', '../x', 'sin-forma', '', None, 7):
            with self.subTest(identificador=raro):
                self.assertIsNone(pruebas.datos(self.root, raro, estado, SHA))

    def test_pp2_un_candidato_demasiado_corto_o_largo_no_arma_rutas(self):
        ident = self.cambio(('hacer uno', []))
        estado = f.leer(ident)[1]
        for candidato in ('abc', 'a' * 41, '', 'ab c'):
            with self.subTest(candidato=candidato):
                self.assertIsNone(pruebas.datos(self.root, ident, estado, candidato))
        self.assertIsNotNone(pruebas.datos(self.root, ident, estado, 'abcd'))
        self.assertIsNotNone(pruebas.datos(self.root, ident, estado, 'a' * 40))

    def test_pp3_un_motivo_que_empieza_con_guiones_conserva_su_texto(self):
        self.assertEqual(pruebas.excepciones(spec(('hacer uno', ['Pruebas: no aplica — --help es texto fijo']))),
                         {'hacer_uno': '--help es texto fijo'})
        self.assertEqual(pruebas.excepciones(spec(('hacer uno', ['Pruebas: no aplica — -n y -v']))), {'hacer_uno': '-n y -v'})

    def test_pp3_las_secciones_delta_se_leen_en_cualquier_mayuscula_y_renamed_no_retira(self):
        base = spec(('hacer uno', ['Pruebas: no aplica — motivo']))
        for seccion in ('added', 'Modified', 'RENAMED'):
            with self.subTest(seccion=seccion):
                self.assertEqual(pruebas.excepciones(base.replace('ADDED', seccion)), {'hacer_uno': 'motivo'})
        self.assertEqual(pruebas.excepciones(base.replace('ADDED', 'removed')), {})

    def test_pp3_el_primer_error_es_el_que_se_informa(self):
        texto = spec(('hacer uno', ['Pruebas: no aplica']), ('hacer dos', ['Pruebas: sí']))
        with self.assertRaisesRegex(pruebas.PruebasInvalidas, 'hacer_uno'):
            pruebas.excepciones(texto)

    # --- cuarta ronda ------------------------------------------------------------------------------------------------------
    def test_pp3_las_huellas_no_se_leen_si_las_rutas_salen_del_proyecto_o_son_enlaces(self):
        ident = self.cambio(('hacer uno', []))
        carpeta, base = f.leer(ident)
        (self.root.parent / 'secreto.md').write_text('secreto', encoding='utf-8')
        with patch.object(f, 'documentos', side_effect=AssertionError('no debía leer')):
            for ruta in ('../secreto.md', 'openspec/../../secreto.md', str(self.root.parent / 'secreto.md')):
                with self.subTest(spec=ruta):
                    estado = json.loads(json.dumps(base))
                    estado['spec'] = ruta
                    self.assertIsNone(f.documentos_o_nada(carpeta, estado))
            enlace = self.root / 'enlace.md'
            enlace.symlink_to(self.root.parent / 'secreto.md')
            estado = json.loads(json.dumps(base))
            estado['spec'] = 'enlace.md'
            self.assertIsNone(f.documentos_o_nada(carpeta, estado))
            propuesta = carpeta / 'proposal.md'
            original = propuesta.read_text()
            propuesta.unlink()
            propuesta.symlink_to(self.root.parent / 'secreto.md')
            self.assertIsNone(f.documentos_o_nada(carpeta, json.loads(json.dumps(base))))
            propuesta.unlink()
            propuesta.write_text(original)
            for fase in ('cerrada', 'abandonada'):
                estado = json.loads(json.dumps(base))
                estado['fase'] = fase
                self.assertIsNone(f.documentos_o_nada(carpeta, estado))

    def test_pp3_las_huellas_con_una_spec_que_no_es_ruta_devuelven_nada_y_no_caen(self):
        ident = self.cambio(('hacer uno', []))
        carpeta, base = f.leer(ident)
        for valor in (None, 7, ['x'], 'a\x00b'):
            with self.subTest(spec=valor):
                estado = json.loads(json.dumps(base))
                estado['spec'] = valor
                self.assertIsNone(f.documentos_o_nada(carpeta, estado))
        estado = json.loads(json.dumps(base))
        del estado['spec']
        self.assertIsNone(f.documentos_o_nada(carpeta, estado))

    def test_pp3_las_huellas_de_un_cambio_normal_se_leen(self):
        ident = self.cambio(('hacer uno', []))
        carpeta, estado = f.leer(ident)
        self.assertEqual(f.documentos_o_nada(carpeta, estado), f.documentos(carpeta, estado))

    def test_pp3_los_encabezados_se_leen_con_los_espacios_exactos_del_importador_de_oracle(self):
        # Oracle no toma por encabezado «####  Scenario:», «#<tab>x» ni «###  Requirement:»: la cabecera sigue abierta
        for linea in ('####  Scenario: x', '#\tnota', '##\tnota', '#### scenario: x', '####Scenario: x'):
            with self.subTest(sigue_abierta=linea), self.assertRaisesRegex(pruebas.PruebasInvalidas, 'necesita un motivo'):
                pruebas.excepciones(spec(('hacer uno', [linea, 'Pruebas: no aplica'])))
        # y sí cierra exactamente lo que Oracle cierra
        for linea in ('# x', '## x', '### x', '#### Scenario: x', '#### Scenario:'):
            with self.subTest(cierra=linea):
                self.assertEqual(pruebas.excepciones(spec(('hacer uno', [linea, 'Pruebas: no aplica']))), {})
        # «###  Requirement:» (dos espacios) no abre un requisito: su línea Pruebas no es de nadie
        texto = '# Capability: x\n\n## ADDED Requirements\n\n###  Requirement: hacer uno\nPruebas: no aplica\n'
        self.assertEqual(pruebas.excepciones(texto), {})

    def test_pp3_la_vineta_necesita_un_espacio_como_en_oracle(self):
        self.assertEqual(pruebas.excepciones(spec(('hacer uno', ['-Pruebas: no aplica']))), {})
        self.assertEqual(pruebas.excepciones(spec(('hacer uno', ['*Pruebas: no aplica']))), {})

    def test_pp3_una_spec_sin_aprobacion_con_solo_una_linea_mala_tambien_lo_dice(self):
        ident = f.nuevo('Mala', 'demo')
        carpeta, estado = f.leer(ident)
        (self.root / estado['spec']).write_text(spec(('hacer uno', ['Pruebas: no aplica'])), encoding='utf-8')
        datos = pruebas.datos(self.root, ident, f.leer(ident)[1], None, f.documentos(carpeta, estado))
        texto = ' '.join(datos['invalidas'])
        self.assertIn('necesita un motivo', texto)
        self.assertIn('no tiene una aprobación vigente', texto)

    def test_pp2_un_candidato_que_no_es_texto_no_arma_rutas(self):
        ident = self.cambio(('hacer uno', []))
        estado = f.leer(ident)[1]
        for candidato in (7, True, ['abcd'], b'abcd'):
            with self.subTest(candidato=candidato):
                self.assertIsNone(pruebas.datos(self.root, ident, estado, candidato))

    def test_pp2_el_analisis_no_comparte_el_diccionario_de_excepciones_con_quien_lo_llama(self):
        exceptuados = {'d.a': 'motivo'}
        trazas = {'esquema': 'oracle-factory.trazabilidad-casos/1', 'requisitos': {}, 'casos': {}}
        for t in (trazas, None):
            r = pruebas.analizar(['d.a'], t, exceptuados)
            r['excepciones']['d.z'] = 'otro'
            self.assertEqual(exceptuados, {'d.a': 'motivo'})


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
