"""Sondas de R2 sobre la corrección 19b8d76. Cada prueba afirma el defecto observado."""
import sys
from unittest.mock import patch
sys.path.insert(0, 'tests')
from test_modos import Modos as Base, f, modos


class SondasC(Base):
    def test_r2c_01_renovar_aceptacion_borra_propuesta_y_juzga_con_medidas_del_agente(self):
        # confirmacion: el agente propone medidas; se edita tasks.md (misma spec, mismos ids);
        # la persona renueva la aceptación e importa: la propuesta desaparece y el juicio la cuenta.
        ident = self.crear()
        self.aceptar(ident); f.importar(ident)
        with self.agente():
            rid = self.medir(ident)
        ruta = self.root / 'requisitos' / f'{rid}.requisito'
        tasks = self.root / 'openspec/changes' / ident / 'tasks.md'
        tasks.write_text(tasks.read_text() + '\n- [ ] nota de seguimiento\n')
        self.aceptar(ident); f.importar(ident)
        estado = self.estado(ident)
        print('\nR2C-01 requisitos:', estado['requisitos'], 'pendientes:', estado['medidas_pendientes'],
              'medidas:', estado['medidas'], file=sys.stderr)
        print('R2C-01 archivo:', ruta.read_text().splitlines()[-1], file=sys.stderr)
        self.assertIn(rid, estado['requisitos'])
        self.assertEqual(estado['medidas_pendientes'], {})
        self.assertIn('notas.casos_ejecutados', ruta.read_text())
        hechos, informe = self.producto_y_hechos(ident)
        with self.escribe(f'REGISTRAR REVISION {ident}'):
            f.revisar(ident, informe, 'Persona fixture', 'aprobar', 0)
        f.juzgar(ident, hechos)
        with self.escribe(f'CERRAR {ident}'):
            f.cerrar(ident)
        estado = self.estado(ident)
        print('R2C-01 fase:', estado['fase'], 'oracle:', estado['oracle']['codigo'], 'registro medidas:', estado['medidas'], file=sys.stderr)
        self.assertEqual(estado['fase'], 'cerrada')
        self.assertEqual(estado['medidas'], {})

    def test_r2c_02_bajar_a_funcional_conserva_propuesta_y_la_persona_confirma(self):
        ident = self.crear()
        with self.agente():
            f.aprobar_spec(ident)   # propuesta en confirmacion
        with self.escribe(f'CAMBIAR MODO {ident} funcional'):
            f.cambiar_modo(ident, 'funcional')
        self.assertIn('spec', self.estado(ident)['propuestas'])
        with patch('builtins.input', side_effect=[f'APROBAR ESPECIFICACION {ident}', 'motivo de la persona']):
            f.aprobar_spec(ident)
        sa = self.estado(ident)['spec_aprobada']
        print('\nR2C-02 spec_aprobada:', sa['tipo_actor'], sa['forma'], sa['modo'], sa.get('motivo'), file=sys.stderr)
        self.assertEqual((sa['forma'], sa['modo']), ('confirmo', 'funcional'))

    def test_r2c_03_motivo_no_se_muestra(self):
        ident = self.crear('funcional')
        notas = []
        with patch.object(f, 'nota_tarea', lambda i, t: notas.append(t)), \
                patch('builtins.input', side_effect=[f'APROBAR ESPECIFICACION {ident}', 'MOTIVO-VISIBLE']):
            f.aprobar_spec(ident)
        self.stdout.truncate(0); self.stdout.seek(0)
        f.mostrar(ident)
        print('\nR2C-03 nota:', notas[-1], file=sys.stderr)
        self.assertEqual(self.estado(ident)['spec_aprobada']['motivo'], 'MOTIVO-VISIBLE')
        self.assertNotIn('MOTIVO-VISIBLE', self.stdout.getvalue())
        self.assertNotIn('MOTIVO-VISIBLE', notas[-1])

    def test_r2c_04_subir_a_funcional_descarta_spec_del_agente(self):
        # Lo que el nombre de test_m5_bajar_a_funcional... no comprueba: la spec.
        ident = self.crear('autonomo')
        with self.agente(), self.sin_terminal():
            f.aprobar_spec(ident); f.importar(ident)
            f.cambiar_modo(ident, 'funcional')
        estado = self.estado(ident)
        print('\nR2C-04 spec_aprobada:', estado['spec_aprobada'], 'propuestas:', estado['propuestas'], file=sys.stderr)
        self.assertIsNone(estado['spec_aprobada'])
        self.assertNotIn('spec', estado['propuestas'])
