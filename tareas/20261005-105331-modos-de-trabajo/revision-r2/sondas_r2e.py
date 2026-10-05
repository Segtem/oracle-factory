"""Sondas de R2 sobre 653de8f."""
import sys, json
from unittest.mock import patch
sys.path.insert(0, 'tests')
from test_modos import Modos as Base, f, modos


class SondasE(Base):
    def test_r2e_a_misma_spec_conserva_decision_con_hash(self):
        ident = self.crear()
        self.aceptar(ident); f.importar(ident)
        rid = self.medir(ident)
        tasks = self.root / 'openspec/changes' / ident / 'tasks.md'
        tasks.write_text(tasks.read_text() + '\n- [ ] seguimiento\n')
        self.aceptar(ident); f.importar(ident)
        e = self.estado(ident)
        print('\nR2E-A sin decisión tras reimportar:', f.medidas_sin_decision(e), 'registro:', rid in e['medidas'], file=sys.stderr)
        self.assertEqual(f.medidas_sin_decision(e), [])

    def test_r2e_b_agente_en_autonomo_cubre_edicion_a_mano_de_persona(self):
        # confirmacion: persona decide; archivo editado a mano; agente (tras bajar a autonomo) registra decidio sobre lo editado.
        ident = self.crear()
        self.aceptar(ident); f.importar(ident)
        rid = self.medir(ident)
        ruta = self.root / 'requisitos' / f'{rid}.requisito'
        ruta.write_text(ruta.read_text().replace('medido_por notas.casos_ejecutados, notas.resultados', 'medido_por notas.casos_ejecutados'))
        with self.escribe(f'CAMBIAR MODO {ident} autonomo'):
            f.cambiar_modo(ident, 'autonomo')
        with self.agente(), self.sin_terminal():
            f.medir(ident, requisito_id=rid, medidas=['notas.casos_ejecutados'], quitar_sin_medir=True)
        e = self.estado(ident)
        print('\nR2E-B registro:', e['medidas'][rid]['tipo_actor'], e['medidas'][rid]['forma'], file=sys.stderr)
        self.assertEqual(e['medidas'][rid]['tipo_actor'], 'agente')

    def test_r2e_c_propuesta_descartada_y_agente_en_confirmacion(self):
        ident = self.crear('autonomo')
        with self.agente(), self.sin_terminal():
            f.aprobar_spec(ident); f.importar(ident); rid = self.medir(ident)
            f.cambiar_modo(ident, 'funcional')    # sube; la medida pasa a descartada
        e = self.estado(ident)
        print('\nR2E-C pendiente:', e['medidas_pendientes'][rid].get('descartada'), file=sys.stderr)
        with self.agente():
            with self.assertRaises(f.FactoryError) as cm:
                f.medir(ident, requisito_id=rid, medidas=['notas.casos_ejecutados', 'notas.resultados'], quitar_sin_medir=True)
        print('R2E-C agente en funcional:', cm.exception, file=sys.stderr)
        e = self.estado(ident)
        self.assertNotIn(rid, e.get('medidas', {}))

    def test_r2e_d_persona_confirma_con_pendiente_obsoleta(self):
        # agente propone; archivo editado a mano; persona repite medir: ¿queda 'confirmo' de algo que no propuso el agente?
        ident = self.crear()
        self.aceptar(ident); f.importar(ident)
        with self.agente():
            rid = self.medir(ident)
        ruta = self.root / 'requisitos' / f'{rid}.requisito'
        ruta.write_text(ruta.read_text().replace('medido_por notas.casos_ejecutados, notas.resultados', 'medido_por notas.resultados'))
        f.medir(ident, requisito_id=rid, medidas=['notas.resultados'], quitar_sin_medir=True)
        r = self.estado(ident)['medidas'][rid]
        print('\nR2E-D forma:', r['forma'], file=sys.stderr)
        self.assertEqual(r['forma'], 'decidio')

    def test_r2e_e_agente_no_registra_en_funcional_tras_descarte(self):
        ident = self.crear('autonomo')
        with self.agente(), self.sin_terminal():
            f.aprobar_spec(ident); f.importar(ident); rid = self.medir(ident)
            f.cambiar_modo(ident, 'funcional')
        with patch('builtins.input', side_effect=[f'APROBAR ESPECIFICACION {ident}', 'motivo']):
            f.aprobar_spec(ident)
        f.importar(ident)
        e = self.estado(ident)
        print('\nR2E-E pendiente tras reimportar:', e['medidas_pendientes'].get(rid, {}).get('descartada'), 'medidas:', list(e['medidas']), file=sys.stderr)
        with self.agente(), self.assertRaises(f.FactoryError) as cm:
            f.medir(ident, requisito_id=rid, medidas=['notas.casos_ejecutados', 'notas.resultados'], quitar_sin_medir=True)
        print('R2E-E agente:', cm.exception, file=sys.stderr)
        self.assertNotIn(rid, self.estado(ident)['medidas'])
        # y la persona decide con motivo (y la propuesta descartada se va)
        with patch('builtins.input', side_effect=['Las dos cubren los tres escenarios']):
            f.medir(ident, requisito_id=rid, medidas=['notas.casos_ejecutados', 'notas.resultados'], quitar_sin_medir=True)
        r = self.estado(ident)['medidas'][rid]
        print('R2E-E persona:', r['tipo_actor'], r['forma'], r.get('motivo'), file=sys.stderr)
        self.assertEqual((r['forma'], r['motivo']), ('decidio', 'Las dos cubren los tres escenarios'))
