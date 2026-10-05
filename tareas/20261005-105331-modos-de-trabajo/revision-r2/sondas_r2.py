"""Sondas de R2 sobre el checkout 1a12a1a. Correr desde el checkout:
PYTHONPATH=.:tests <env>/python -m unittest -v sondas_r2 </dev/null
Cada prueba AFIRMA el comportamiento observado (defecto); si pasa, el hallazgo se reproduce."""
import json, sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, 'tests')
from test_modos import Modos as Base, f, modos


class Sondas(Base):
    def _flujo_hasta_juicio(self, ident, agente_rev=False):
        hechos, informe = self.producto_y_hechos(ident)
        return hechos, informe

    def test_r2_01_propuesta_vieja_bloquea_autonomo(self):
        # confirmacion: el agente propone la spec; la persona baja a autonomo; el agente decide.
        ident = self.crear()
        with self.agente():
            f.aprobar_spec(ident)
        self.assertIn('spec', self.estado(ident)['propuestas'])
        with self.escribe(f'CAMBIAR MODO {ident} autonomo'):
            f.cambiar_modo(ident, 'autonomo')
        with self.agente(), self.sin_terminal():
            f.aprobar_spec(ident)          # decide en autonomo
        estado = self.estado(ident)
        self.assertEqual(estado['spec_aprobada']['tipo_actor'], 'agente')
        self.assertIn('spec', estado['propuestas'])  # sigue colgada
        p = [x for x in f.pendientes(estado) if 'propuesta por' in x]
        print('\nR2-01 pendientes:', p, file=sys.stderr)
        self.assertTrue(p)

    def test_r2_02_medidas_pendientes_huerfanas_tras_cambiar_spec(self):
        ident = self.crear()
        self.aceptar(ident); f.importar(ident)
        with self.agente():
            rid_viejo = self.medir(ident)
        spec = self.root / self.estado(ident)['spec']
        spec.write_text(spec.read_text() + '\n')  # cambia la huella de la spec
        self.aceptar(ident); f.importar(ident)
        estado = self.estado(ident)
        self.assertNotIn(rid_viejo, estado['requisitos'])
        self.assertIn(rid_viejo, estado['medidas_pendientes'])
        print('\nR2-02 pendientes:', [x for x in f.pendientes(estado) if 'medidas de' in x], file=sys.stderr)
        with self.assertRaisesRegex(f.FactoryError, 'id completo'):
            f.medir(ident, requisito_id=rid_viejo, medidas=['notas.casos_ejecutados', 'notas.resultados'], quitar_sin_medir=True)

    def test_r2_03_juicio_verde_con_medidas_sin_confirmar(self):
        ident = self.crear()
        self.aceptar(ident); f.importar(ident)
        with self.agente():
            rid = self.medir(ident)
        hechos, informe = self.producto_y_hechos(ident)
        with self.escribe(f'REGISTRAR REVISION {ident}'):
            f.revisar(ident, informe, 'Persona fixture', 'aprobar', 0)
        f.juzgar(ident, hechos)
        estado = self.estado(ident)
        print('\nR2-03 fase/oracle:', estado['fase'], estado['oracle']['codigo'], 'pendiente:', list(estado['medidas_pendientes']), file=sys.stderr)
        self.assertEqual((estado['fase'], estado['oracle']['codigo']), ('oracle_verde', 0))
        self.assertIn(rid, estado['medidas_pendientes'])

    def test_r2_04_agente_crea_autonomo_si_el_proyecto_lo_define(self):
        (self.root / 'factory.json').write_text(json.dumps({'modo_por_defecto': 'autonomo'}))
        with self.agente(), self.sin_terminal():
            ident = f.nuevo('Otra', 'otra', modo='autonomo')
        estado = self.estado(ident)
        print('\nR2-04 modo/actor:', estado['modo'], estado['eventos'][0]['tipo_actor'], file=sys.stderr)
        self.assertEqual(estado['modo'], 'autonomo')

    def test_r2_05_nota_de_revision_sin_actor(self):
        notas = []
        with patch.object(f, 'nota_tarea', lambda i, t: notas.append(t)):
            ident = self.crear('autonomo')
            with self.agente(), self.sin_terminal():
                f.aprobar_spec(ident); f.importar(ident); self.medir(ident)
                hechos, informe = self.producto_y_hechos(ident)
                f.revisar(ident, informe, 'Brian Hollweg', 'aprobar', 0)
        nota = [n for n in notas if n.startswith('Revisión')][0]
        medida = [n for n in notas if n.startswith('Medidas de')][0]
        print('\nR2-05 nota revisión:', nota, '\nR2-05 nota medidas:', medida, file=sys.stderr)
        self.assertNotIn('agente', nota); self.assertNotIn('autonomo', nota)
        self.assertNotIn('agente', medida)
        self.stdout.truncate(0); self.stdout.seek(0)
        f.mostrar(ident)
        print('R2-05 estado:', [l for l in self.stdout.getvalue().splitlines() if l.startswith('Revisión')], file=sys.stderr)

    def test_r2_06_funcional_convierte_decision_de_agente_en_propuesta_confirmable(self):
        ident = self.crear('autonomo')
        with self.agente():
            f.aprobar_spec(ident)
        with self.escribe(f'CAMBIAR MODO {ident} funcional'):
            f.cambiar_modo(ident, 'funcional')
        estado = self.estado(ident)
        self.assertIn('spec', estado['propuestas'])
        self.aceptar(ident)
        sa = self.estado(ident)['spec_aprobada']
        print('\nR2-06 spec_aprobada:', sa['tipo_actor'], sa['forma'], sa['modo'], 'motivo' in sa, file=sys.stderr)
        self.assertEqual((sa['forma'], sa['modo']), ('confirmo', 'funcional'))

    def test_r2_07_cierre_dice_sin_decision_humana_aunque_la_hubo(self):
        notas = []
        with patch.object(f, 'nota_tarea', lambda i, t: notas.append(t)):
            ident = self.crear('autonomo')
            self.aceptar(ident)   # persona acepta la spec
            with self.agente(), self.sin_terminal():
                f.importar(ident); self.medir(ident)
                hechos, informe = self.producto_y_hechos(ident)
                f.revisar(ident, informe, 'agente-x', 'aprobar', 0)
                f.juzgar(ident, hechos); f.cerrar(ident)
        estado = self.estado(ident)
        cierre = [n for n in notas if n.startswith('Cierre')][0]
        print('\nR2-07 spec:', estado['spec_aprobada']['tipo_actor'], '| nota:', cierre, file=sys.stderr)
        self.assertEqual(estado['spec_aprobada']['tipo_actor'], 'persona')
        self.assertIn('no hubo decisión humana', cierre)

    def test_r2_08_agente_no_puede_retirar_su_propuesta_de_medidas_al_repetir(self):
        # confirmacion: agente propone medidas; la persona baja a funcional; requisito no funcional.
        ident = self.crear(tipo='no funcional')
        self.aceptar(ident); f.importar(ident)
        with self.agente():
            rid = self.medir(ident)
        with self.escribe(f'CAMBIAR MODO {ident} funcional'):
            f.cambiar_modo(ident, 'funcional')
        with self.agente():
            self.medir(ident)   # en funcional el agente decide lo no funcional
        estado = self.estado(ident)
        print('\nR2-08 pendientes:', list(estado.get('medidas_pendientes', {})), 'medidas:', list(estado.get('medidas', {})), file=sys.stderr)
        self.assertIn(rid, estado['medidas_pendientes'])
        self.assertNotIn(rid, estado.get('medidas', {}))
