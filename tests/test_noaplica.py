"""El verificador respeta «Pruebas: no aplica»: escenarios na1–na3, con proyectos temporales de verdad."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_verificador_generico import CAMBIO, ProyectoTemporal, vc  # noqa: E402


def spec(excepcion='Pruebas: no aplica — se prueba a mano', segundo='el_segundo'):
    """Tres requisitos; el segundo lleva `excepcion` en su cabecera (o nada si es None)."""
    def req(nombre, linea=None):
        return (f'### Requirement: {nombre}\nTipo: funcional\n' + (linea + '\n' if linea else '') + 'El sistema DEBE a.\n\n'
                '#### Scenario: uno\n- DADO a\n- CUANDO b\n- ENTONCES c\n\n')
    return '# Capability: demo\n\n## ADDED Requirements\n\n' + req('el_primero') + req(segundo, excepcion) + req('el_tercero')


def modulo(*numeros):
    """Un módulo con un caso `test_dm<n>_…` por número."""
    return 'import unittest\n\n\nclass Uno(unittest.TestCase):\n' + ''.join(
        f'    def test_dm{n}_caso(self):\n        self.assertTrue(True)\n\n' for n in numeros)


class Proyecto(ProyectoTemporal):
    def setUp(self):
        super().setUp()
        self.preparar(spec(), modulo(1, 3))

    def preparar(self, texto_spec, texto_modulo):
        self.escribir('tests/test_demo.py', texto_modulo)
        self.escribir(f'openspec/changes/{CAMBIO}/specs/demo/spec.md', texto_spec)
        self.escribir(f'.factory/cambios/{CAMBIO}/factory.json',
                      json.dumps({'requisitos': ['demo_h.el_primero', 'demo_h.el_segundo', 'demo_h.el_tercero']}))
        self.git('add', '-A')
        self.git('commit', '-qm', 'cambio')

    def contrato(self):
        return vc.leer_contrato(self.raiz, CAMBIO, 'test_demo')[0]

    def carpeta(self):
        return self.raiz / 'catalogos'

    def catalogos(self):
        return sorted(p.name for p in self.carpeta().glob('*.oracle'))


class Contrato(Proyecto):
    # --- na1: un requisito exceptuado no pide casos ------------------------------------------------------------------------
    def test_na1_un_requisito_exceptuado_sin_casos_queda_fuera_del_contrato_y_los_demas_conservan_su_numero(self):
        self.assertEqual(self.contrato(), {'el_primero': ['Uno.test_dm1_caso'], 'el_tercero': ['Uno.test_dm3_caso']})

    def test_na1_un_caso_para_el_requisito_exceptuado_falla_y_lo_nombra(self):
        self.preparar(spec(), modulo(1, 2, 3))
        with self.assertRaises(vc.ContratoInvalido) as e:
            self.contrato()
        self.assertIn('Uno.test_dm2_caso', str(e.exception))
        self.assertIn('el_segundo', str(e.exception))

    def test_na1_los_demas_requisitos_siguen_exigiendo_casos(self):
        self.preparar(spec(), modulo(1))
        with self.assertRaises(vc.ContratoInvalido) as e:
            self.contrato()
        self.assertIn('el_tercero', str(e.exception))
        self.assertNotIn('el_primero', str(e.exception))

    # --- na3: lo mal escrito no se ignora ---------------------------------------------------------------------------------
    def test_na3_una_excepcion_sin_motivo_falla_con_el_error_del_lector(self):
        self.preparar(spec('Pruebas: no aplica'), modulo(1, 3))
        with self.assertRaises(vc.ContratoInvalido) as e:
            self.contrato()
        self.assertIn('necesita un motivo', str(e.exception))
        self.assertIn('el_segundo', str(e.exception))

    def test_na3_una_linea_pruebas_con_otra_cosa_falla_con_el_error_del_lector(self):
        self.preparar(spec('Pruebas: manuales'), modulo(1, 3))
        with self.assertRaises(vc.ContratoInvalido) as e:
            self.contrato()
        self.assertIn('sólo admite', str(e.exception))

    def test_na3_una_excepcion_repetida_falla(self):
        self.preparar(spec('Pruebas: no aplica — a mano\nPruebas: no aplica — otra vez'), modulo(1, 3))
        with self.assertRaises(vc.ContratoInvalido) as e:
            self.contrato()
        self.assertIn('dos veces', str(e.exception))

    def test_na3_con_todos_los_requisitos_exceptuados_no_hay_nada_que_verificar(self):
        todos = spec().replace('Tipo: funcional\nEl sistema DEBE a.', 'Tipo: funcional\nPruebas: no aplica — a mano\nEl sistema DEBE a.')
        self.preparar(todos, 'import unittest\n\n\nclass Uno(unittest.TestCase):\n    def test_sin_numero(self):\n        pass\n')
        with self.assertRaises(vc.ContratoInvalido) as e:
            self.contrato()
        self.assertIn('ningún caso', str(e.exception))


class EvidenciaYCatalogos(Proyecto):
    # --- na2: la evidencia y los catálogos cuentan sólo los requisitos con casos --------------------------------------------
    def test_na2_la_evidencia_nombra_solo_a_los_requisitos_con_casos_y_la_corrida_cuenta_los_suyos(self):
        r = self.correr('--salida', str(self.evidencia()))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(self.resultado()['exitoso'])
        hechos = json.loads((self.evidencia() / 'hechos.json').read_text())
        self.assertEqual({h['requisito'] for h in hechos['demo_caso']}, {'el_primero', 'el_tercero'})
        self.assertEqual(hechos['demo_corrida'], [{'completa': 1, 'casos': 2}])
        traza = json.loads((self.evidencia() / 'trazabilidad.json').read_text())
        self.assertEqual(set(traza['requisitos']), {'demo_h.el_primero', 'demo_h.el_tercero'})

    def test_na2_los_catalogos_no_incluyen_al_exceptuado(self):
        r = self.correr('--catalogos')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.catalogos(), ['factory_demo.corrida_completa.oracle', 'factory_demo.el_primero.oracle',
                                            'factory_demo.el_tercero.oracle'])
        self.assertIn('c.casos == 2', (self.carpeta() / 'factory_demo.corrida_completa.oracle').read_text())

    def test_na2_un_requisito_que_pasa_a_estar_exceptuado_pierde_su_catalogo_y_los_demas_no_cambian(self):
        self.preparar(spec(None), modulo(1, 2, 3))  # sin excepción: los tres tienen catálogo
        self.correr('--catalogos')
        self.assertIn('factory_demo.el_segundo.oracle', self.catalogos())
        antes = (self.carpeta() / 'factory_demo.el_primero.oracle').read_bytes()
        self.preparar(spec(), modulo(1, 3))
        r = self.correr('--catalogos')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn('factory_demo.el_segundo.oracle', self.catalogos())
        self.assertIn('factory_demo.el_segundo.oracle (retirado)', r.stdout)
        self.assertEqual((self.carpeta() / 'factory_demo.el_primero.oracle').read_bytes(), antes)


if __name__ == '__main__':
    unittest.main()
