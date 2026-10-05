"""Modos de trabajo: quién decide cada gate y cómo queda registrado (escenarios m1–m5)."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from oracle_factory import cli as f
from oracle_factory import modos

GIT = ['git', '-c', 'user.name=Persona fixture', '-c', 'user.email=fixture@example.invalid', '-c', 'core.hooksPath=/dev/null']


class Modos(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'producto'
        self.root.mkdir()
        for name, value in [('ROOT', self.root), ('CHANGES', self.root / 'openspec/changes'), ('AGENTE', None)]:
            p = patch.object(f, name, value); p.start(); self.addCleanup(p.stop)
        self.terminal = patch.object(f, 'terminal_interactiva', return_value=True)
        self.terminal.start(); self.addCleanup(self.terminal.stop)
        self.stdout = io.StringIO()
        p = contextlib.redirect_stdout(self.stdout); p.__enter__(); self.addCleanup(p.__exit__, None, None, None)
        f.inicializar()

    # --- ayudantes -----------------------------------------------------------------
    def agente(self, nombre='agente-x'):
        return patch.object(f, 'AGENTE', nombre)

    def sin_terminal(self):
        return patch.object(f, 'terminal_interactiva', return_value=False)

    def escribe(self, frase):
        return patch('builtins.input', return_value=frase)

    def crear(self, modo=None, tipo=None):
        if modo and modos.baja_intervencion(modos.POR_DEFECTO, modo):
            with self.escribe(f'ELEGIR MODO {modo}'):
                ident = f.nuevo('Nota', con_ejemplo='notas', modo=modo)
        else:
            ident = f.nuevo('Nota', con_ejemplo='notas', modo=modo)
        if tipo:
            spec = self.root / f.leer(ident)[1]['spec']
            texto = spec.read_text()
            cabecera = texto.index('\n', texto.index('### Requirement:')) + 1
            spec.write_text(texto[:cabecera] + f'Tipo: {tipo}\n' + texto[cabecera:])
        return ident

    def estado(self, ident):
        return f.leer(ident)[1]

    def registro(self, ident):
        return (self.root / 'openspec/changes' / ident / 'factory.json').read_bytes()

    def aceptar(self, ident):
        with self.escribe(f'APROBAR ESPECIFICACION {ident}'):
            f.aprobar_spec(ident)

    def medir(self, ident):
        rid = self.estado(ident)['requisitos'][0]
        f.medir(ident, requisito_id=rid, medidas=['notas.casos_ejecutados', 'notas.resultados'], quitar_sin_medir=True)
        return rid

    def producto_y_hechos(self, ident):
        subprocess.run(['git', 'init', '-q', '-b', 'main'], cwd=self.root, check=True)
        subprocess.run(['git', 'add', '.'], cwd=self.root, check=True)
        subprocess.run([*GIT, 'commit', '-qm', 'producto fixture'], cwd=self.root, check=True)
        hechos = self.root / 'tareas' / ident / 'hechos.json'
        subprocess.run([sys.executable, 'examples/notas/sensor.py', '--salida', hechos], cwd=self.root, check=True,
                       capture_output=True)
        informe = self.root / 'tareas' / ident / 'revision.md'
        informe.write_text('Fixture de revisión; no es una revisión real.\n')
        return hechos, informe

    # --- m1: modo explícito por cambio -----------------------------------------------
    def test_m1_crear_cambio_con_modo(self):
        ident = self.crear('funcional')
        self.assertEqual(self.estado(ident)['modo'], 'funcional')
        f.mostrar(ident)
        self.assertIn('Modo de trabajo: funcional', self.stdout.getvalue())
        self.assertEqual(self.estado(f.nuevo('Otra', 'otra'))['modo'], 'confirmacion')

    def test_m1_elegir_autonomo_exige_persona(self):
        ident = self.crear()
        antes = self.registro(ident)
        with self.agente(), self.assertRaisesRegex(f.FactoryError, 'persona'):
            f.cambiar_modo(ident, 'autonomo')
        with self.sin_terminal(), self.assertRaisesRegex(f.FactoryError, 'terminal interactiva'):
            f.cambiar_modo(ident, 'autonomo')
        with self.agente(), self.assertRaisesRegex(f.FactoryError, 'persona'):
            f.nuevo('Otra', 'otra', modo='autonomo')
        self.assertEqual(self.registro(ident), antes)
        with self.escribe(f'CAMBIAR MODO {ident} autonomo'):
            f.cambiar_modo(ident, 'autonomo')
        estado = self.estado(ident)
        self.assertEqual(estado['modo'], 'autonomo')
        self.assertEqual(estado['eventos'][-1]['tipo_actor'], 'persona')

    # --- m2: tipo de requisito -------------------------------------------------------
    def test_m2_requisito_no_funcional_declarado(self):
        ident = self.crear(tipo='no funcional')
        self.aceptar(ident)
        f.importar(ident)
        self.assertEqual(list(self.estado(ident)['tipos'].values()), ['no funcional'])

    def test_m2_requisito_sin_tipo(self):
        ident = self.crear()
        self.aceptar(ident)
        f.importar(ident)
        self.assertEqual(list(self.estado(ident)['tipos'].values()), ['funcional'])

    def test_m2_tipos_obligatorios(self):
        (self.root / 'factory.json').write_text(json.dumps({'tipos_obligatorios': True}))
        ident = self.crear()
        self.aceptar(ident)
        antes = self.registro(ident)
        with self.assertRaisesRegex(f.FactoryError, 'titulo_valido'):
            f.importar(ident)
        self.assertEqual(self.registro(ident), antes)

    # --- m3: decisiones según el modo ------------------------------------------------
    def test_m3_funcional_requisito_funcional(self):
        ident = self.crear('funcional')
        antes = self.registro(ident)
        with self.agente(), self.assertRaisesRegex(f.FactoryError, 'persona'):
            f.aprobar_spec(ident)
        self.assertEqual(self.registro(ident), antes)

    def test_m3_funcional_requisito_no_funcional(self):
        ident = self.crear('funcional', tipo='no funcional')
        with self.agente():
            f.aprobar_spec(ident)
            f.importar(ident)
            rid = self.medir(ident)
        estado = self.estado(ident)
        self.assertEqual(estado['spec_aprobada']['tipo_actor'], 'agente')
        self.assertEqual(estado['medidas'][rid]['tipo_actor'], 'agente')
        self.assertNotIn(rid, estado.get('medidas_pendientes', {}))

    def test_m3_confirmacion_propone(self):
        ident = self.crear()
        self.aceptar(ident)
        f.importar(ident)
        with self.agente():
            rid = self.medir(ident)
        estado = self.estado(ident)
        self.assertIn(rid, estado['medidas_pendientes'])
        self.assertTrue(any('sin confirmar' in p for p in f.pendientes(estado)))
        self.medir(ident)  # la persona repite el mismo comando
        estado = self.estado(ident)
        self.assertNotIn(rid, estado['medidas_pendientes'])
        self.assertEqual((estado['medidas'][rid]['tipo_actor'], estado['medidas'][rid]['forma']), ('persona', 'confirmo'))

    def test_m3_autonomo(self):
        ident = self.crear('autonomo')
        with self.agente(), self.sin_terminal():
            f.aprobar_spec(ident)
            f.importar(ident)
            self.medir(ident)
            hechos, informe = self.producto_y_hechos(ident)
            f.revisar(ident, informe, 'agente-x', 'aprobar', 0)
            f.juzgar(ident, hechos)
            f.cerrar(ident)
        estado = self.estado(ident)
        self.assertEqual(estado['fase'], 'cerrada')
        decisiones = [e for e in estado['eventos'] if e['accion'] in ('spec_aprobada', 'medidas_elegidas', 'revision_registrada', 'cierre')]
        self.assertEqual(len(decisiones), 4)
        self.assertTrue(all(e['tipo_actor'] == 'agente' and e['modo'] == 'autonomo' for e in decisiones))
        self.assertIn('El cierre lo decidió el agente agente-x en modo autónomo', self.stdout.getvalue())

    def test_m3_cierre_en_modo_funcional(self):
        ident = self.crear('funcional')
        self.aceptar(ident)
        f.importar(ident)
        with self.escribe('Las dos medidas cubren los tres escenarios'):
            self.medir(ident)
        hechos, informe = self.producto_y_hechos(ident)
        with self.escribe(f'REGISTRAR REVISION {ident}'):
            f.revisar(ident, informe, 'Persona fixture', 'aprobar', 0)
        f.juzgar(ident, hechos)
        with self.agente(), self.assertRaisesRegex(f.FactoryError, 'el cierre la toma una persona'):
            f.cerrar(ident)
        self.assertNotEqual(self.estado(ident)['fase'], 'cerrada')

    # --- m4: actor registrado sin aparentar humanos ---------------------------------
    def test_m4_confirmacion_por_pipe(self):
        ident = self.crear()
        antes = self.registro(ident)
        with self.sin_terminal(), self.escribe(f'APROBAR ESPECIFICACION {ident}'), \
                self.assertRaisesRegex(f.FactoryError, 'terminal interactiva'):
            f.aprobar_spec(ident)
        self.assertEqual(self.registro(ident), antes)

    def test_m4_lectura_del_estado(self):
        self.test_m3_autonomo()
        ident = next(p.name for p in (self.root / 'openspec/changes').iterdir())
        self.stdout.truncate(0); self.stdout.seek(0)
        f.mostrar(ident)
        salida = self.stdout.getvalue()
        lineas = [l for l in salida.splitlines() if l.startswith(('Aprobación spec:', 'Revisión registrada por:', 'Medidas de', 'Cierre:'))]
        self.assertEqual(len(lineas), 4)
        self.assertTrue(all('(agente,' in l and 'persona' not in l for l in lineas), lineas)

    def test_m4_sin_agente_ni_terminal_no_es_persona(self):
        ident = self.crear()
        self.aceptar(ident)
        with self.sin_terminal():
            f.importar(ident)
        evento = self.estado(ident)['eventos'][-1]
        self.assertEqual((evento['accion'], evento['tipo_actor']), ('requisitos_importados', 'sin_identificar'))

    # --- m5: cambio de modo con invalidación ----------------------------------------
    def test_m5_subir_la_intervencion_humana(self):
        ident = self.crear('autonomo')
        with self.agente():
            f.aprobar_spec(ident)
            f.cambiar_modo(ident, 'confirmacion')  # subir no exige persona
        estado = self.estado(ident)
        self.assertIsNone(estado['spec_aprobada'])
        self.assertIn('spec', estado['propuestas'])
        self.aceptar(ident)
        estado = self.estado(ident)
        self.assertEqual((estado['spec_aprobada']['tipo_actor'], estado['spec_aprobada']['forma']), ('persona', 'confirmo'))
        self.assertNotIn('spec', estado['propuestas'])


    # --- correcciones de la revisión de R2 ----------------------------------------
    def test_m1_modo_del_proyecto_no_evita_a_la_persona(self):
        (self.root / 'factory.json').write_text(json.dumps({'modo_por_defecto': 'autonomo'}))
        with self.agente(), self.sin_terminal(), self.assertRaisesRegex(f.FactoryError, 'lo elige una persona'):
            f.nuevo('Nota', con_ejemplo='notas')
        with self.escribe('ELEGIR MODO autonomo'):
            ident = f.nuevo('Nota', con_ejemplo='notas')
        self.assertEqual(self.estado(ident)['modo'], 'autonomo')

    def test_m3_spec_nueva_descarta_lo_anterior(self):
        ident = self.crear()
        self.aceptar(ident)
        f.importar(ident)
        with self.agente():
            viejo = self.medir(ident)
        spec = self.root / self.estado(ident)['spec']
        spec.write_text(spec.read_text() + '\n### Requirement: conservar texto\nSHALL conservar el texto.\n#### Scenario: texto\n- THEN permanece\n')
        self.aceptar(ident)
        f.importar(ident)
        estado = self.estado(ident)
        self.assertNotIn(viejo, estado['requisitos'])
        self.assertEqual(estado['medidas_pendientes'], {})
        self.assertFalse([p for p in f.pendientes(estado) if viejo in p])

    def test_m3_juzgar_no_cuenta_medidas_propuestas(self):
        ident = self.crear()
        self.aceptar(ident)
        f.importar(ident)
        with self.agente():
            self.medir(ident)
        hechos, _ = self.producto_y_hechos(ident)
        with self.assertRaisesRegex(f.FactoryError, 'sin confirmar'):
            f.juzgar(ident, hechos)
        self.assertIsNone(self.estado(ident)['oracle'])

    def test_m3_funcional_persona_decide_con_motivo(self):
        ident = self.crear('funcional')
        antes = self.registro(ident)
        with patch('builtins.input', side_effect=[f'APROBAR ESPECIFICACION {ident}', '']), \
                self.assertRaisesRegex(f.FactoryError, 'motivo'):
            f.aprobar_spec(ident)
        self.assertEqual(self.registro(ident), antes)
        with patch('builtins.input', side_effect=[f'APROBAR ESPECIFICACION {ident}', 'Es lo que pidió el equipo']):
            f.aprobar_spec(ident)
        self.assertEqual(self.estado(ident)['spec_aprobada']['motivo'], 'Es lo que pidió el equipo')

    def test_m4_notas_dicen_quien_decidio(self):
        ident = self.crear('autonomo')
        with self.agente(), self.sin_terminal():
            f.aprobar_spec(ident)
            f.importar(ident)
            self.medir(ident)
            _, informe = self.producto_y_hechos(ident)
            f.revisar(ident, informe, 'Brian Hollweg', 'aprobar', 0)
        notas = (self.root / 'tareas' / ident / 'TAREA.md').read_text()
        self.assertIn('Revisión Brian Hollweg: aprobar; registrada por agente-x (agente', notas)
        self.assertIn('elegidas por agente-x (agente', notas)

    def test_m4_cierre_autonomo_no_niega_decisiones_humanas(self):
        ident = self.crear('autonomo')
        self.aceptar(ident)  # una persona acepta la spec
        with self.agente(), self.sin_terminal():
            f.importar(ident)
            self.medir(ident)
            hechos, informe = self.producto_y_hechos(ident)
            f.revisar(ident, informe, 'agente-x', 'aprobar', 0)
            f.juzgar(ident, hechos)
            f.cerrar(ident)
        self.assertNotIn('no hubo decisión humana', self.stdout.getvalue())
        self.assertNotIn('no hubo decisión humana', (self.root / 'tareas' / ident / 'TAREA.md').read_text())
        self.assertEqual(self.estado(ident)['spec_aprobada']['tipo_actor'], 'persona')

    def test_m5_bajar_de_modo_el_agente_reemplaza_su_propuesta(self):
        ident = self.crear()
        with self.agente():
            f.aprobar_spec(ident)
        with self.escribe(f'CAMBIAR MODO {ident} autonomo'):
            f.cambiar_modo(ident, 'autonomo')
        with self.agente(), self.sin_terminal():
            f.aprobar_spec(ident)
        self.assertNotIn('spec', self.estado(ident)['propuestas'])
        with self.escribe(f'CAMBIAR MODO {ident} confirmacion'):
            f.cambiar_modo(ident, 'confirmacion')  # la spec del agente pasa a propuesta
        self.aceptar(ident)
        f.importar(ident)
        with self.agente():
            rid = self.medir(ident)
        with self.escribe(f'CAMBIAR MODO {ident} autonomo'):
            f.cambiar_modo(ident, 'autonomo')
        with self.agente(), self.sin_terminal():
            self.medir(ident)  # mismas medidas: ahora decide y retira su propuesta
        estado = self.estado(ident)
        self.assertEqual(estado['medidas_pendientes'], {})
        self.assertEqual(estado['medidas'][rid]['tipo_actor'], 'agente')
        self.assertFalse([p for p in f.pendientes(estado) if 'propuesta' in p])

    def test_m5_bajar_a_funcional_descarta_decision_del_agente(self):
        ident = self.crear('autonomo')
        with self.agente(), self.sin_terminal():
            f.aprobar_spec(ident)
            f.importar(ident)
            rid = self.medir(ident)
            f.cambiar_modo(ident, 'funcional')  # sube la intervención: no exige persona
        estado = self.estado(ident)
        self.assertIsNone(estado['medidas'].get(rid))
        self.assertTrue(estado['medidas_pendientes'][rid]['descartada'])
        self.assertTrue(any('las decide una persona' in p for p in f.pendientes(estado)))
        self.assertNotIn(rid, estado['medidas'])


class Politica(unittest.TestCase):
    def test_tabla_de_la_propuesta(self):
        tabla = {
            ('autonomo', 'spec', ('funcional',)): 'decide', ('autonomo', 'cierre', ()): 'decide',
            ('funcional', 'spec', ('funcional', 'no funcional')): 'rechaza', ('funcional', 'spec', ('no funcional',)): 'decide',
            ('funcional', 'medidas', ('no funcional',)): 'decide', ('funcional', 'cierre', ()): 'rechaza',
            ('confirmacion', 'medidas', ('no funcional',)): 'propone', ('confirmacion', 'cierre', ()): 'rechaza',
        }
        for (modo, decision, tipos), esperado in tabla.items():
            with self.subTest(modo=modo, decision=decision, tipos=tipos):
                self.assertEqual(modos.via_agente(modo, decision, list(tipos)), esperado)

    def test_tipos_en_la_spec(self):
        texto = '### Requirement: Uno\nTipo: no funcional\n#### Scenario: a\n### Requirement: Dos\n#### Scenario: b\n'
        self.assertEqual(modos.tipos_spec(texto), {'uno': 'no funcional', 'dos': 'funcional'})
        with self.assertRaisesRegex(modos.TipoInvalido, 'dos'):
            modos.tipos_spec(texto, obligatorios=True)
        with self.assertRaisesRegex(modos.TipoInvalido, 'desconocido'):
            modos.tipos_spec('### Requirement: X\nTipo: rápido\n')


if __name__ == '__main__':
    unittest.main()
