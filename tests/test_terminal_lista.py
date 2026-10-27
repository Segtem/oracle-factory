"""La terminal de Factory espera a estar lista antes de recibir un comando: escenarios tl1–tl4, en node con un `vscode` falso."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import unittest

SOURCE = Path(__file__).resolve().parents[1]
NODE = shutil.which('node')
EXTENSION = SOURCE / 'editores/vscode'
CMD = 'oracle-factory estado 20261027-000000-x'
OTRO = 'oracle-factory mensaje 20261027-000000-x hola'


def correr(**escenario):
    if not NODE:
        raise unittest.SkipTest('hace falta node')
    r = subprocess.run([NODE, str(SOURCE / 'tests/terminal_en_node.cjs'), str(EXTENSION), str(SOURCE), json.dumps(escenario)],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


def textos(foto):
    return [x['texto'] for x in foto]


class TerminalLista(unittest.TestCase):
    # --- tl1: una terminal nueva espera a estar lista ---------------------------------------------------------------
    def test_tl1_no_escribe_hasta_que_la_terminal_avisa(self):
        r = correr(espera=5000, pasos=[{'escribir': CMD}, {'esperar': 150}, {'foto': 'antes'}, {'avisar': True}, {'foto': 'despues'}])
        self.assertEqual(r['fotos']['antes'], [])
        self.assertEqual(r['fotos']['despues'], [{'terminal': 0, 'texto': CMD, 'enter': False}])

    def test_tl1_el_aviso_de_otra_terminal_no_cuenta(self):
        r = correr(espera=5000, pasos=[{'escribir': CMD}, {'avisar_otra': True}, {'esperar': 100}, {'foto': 'otra'},
                                        {'avisar': True}, {'foto': 'propia'}])
        self.assertEqual(r['fotos']['otra'], [])
        self.assertEqual(textos(r['fotos']['propia']), [CMD])

    def test_tl1_la_espera_se_libera_una_sola_vez_y_el_reloj_no_queda_andando(self):
        r = correr(espera=300, pasos=[{'escribir': CMD}, {'avisar': True}, {'esperar': 700}])
        self.assertEqual((r['suscripciones'], r['liberadas']), (1, 1))
        r = correr(espera=200, pasos=[{'escribir': CMD}, {'esperar': 600}])
        self.assertEqual((r['suscripciones'], r['liberadas']), (1, 1))

    def test_tl1_si_nunca_avisa_escribe_al_cumplirse_el_plazo_y_no_antes(self):
        r = correr(espera=400, pasos=[{'escribir': CMD}, {'esperar': 100}, {'foto': 'antes'}, {'esperar': 600}, {'foto': 'despues'}])
        self.assertEqual(r['fotos']['antes'], [])
        self.assertEqual(textos(r['fotos']['despues']), [CMD])
        self.assertIn('plazo', r['salida'][0])

    def test_tl1_un_plazo_de_cero_escribe_de_inmediato(self):
        r = correr(espera=0, pasos=[{'escribir': CMD}, {'foto': 'ya'}])
        self.assertEqual(textos(r['fotos']['ya']), [CMD])

    def test_tl1_una_version_sin_el_evento_cae_al_plazo(self):
        r = correr(espera=300, evento=False, pasos=[{'escribir': CMD}, {'esperar': 100}, {'foto': 'antes'},
                                                    {'esperar': 500}, {'foto': 'despues'}])
        self.assertEqual(r['fotos']['antes'], [])
        self.assertEqual(textos(r['fotos']['despues']), [CMD])

    def test_tl1_sin_plazo_configurado_no_escribe_enseguida(self):
        r = correr(pasos=[{'escribir': CMD}, {'esperar': 300}, {'foto': 'antes'}])
        self.assertEqual(r['fotos']['antes'], [])  # el plazo por defecto es de segundos, no de milisegundos

    def test_tl1_un_plazo_invalido_cae_al_de_por_defecto(self):
        for valor in (-5, 'abc', None):
            r = correr(espera=valor, pasos=[{'escribir': CMD}, {'esperar': 300}, {'foto': 'antes'}])
            self.assertEqual(r['fotos']['antes'], [], valor)

    # --- tl2: una terminal lista recibe el comando enseguida ---------------------------------------------------------
    def test_tl2_una_terminal_que_ya_existia_no_espera_ni_se_duplica(self):
        r = correr(espera=5000, existente=True, pasos=[{'escribir': CMD}, {'foto': 'ya'}])
        self.assertEqual(textos(r['fotos']['ya']), [CMD])
        self.assertEqual(r['terminales'], 1)

    def test_tl2_una_terminal_nueva_que_ya_informa_su_integracion_no_espera(self):
        r = correr(espera=5000, integracion=True, pasos=[{'escribir': CMD}, {'foto': 'ya'}])
        self.assertEqual(textos(r['fotos']['ya']), [CMD])
        self.assertEqual(r['terminales'], 1)

    # --- tl3: varios comandos seguidos --------------------------------------------------------------------------------
    def test_tl3_dos_comandos_mientras_arranca_se_escriben_en_orden_y_una_vez(self):
        r = correr(espera=5000, pasos=[{'escribir': CMD}, {'escribir': OTRO}, {'esperar': 100}, {'foto': 'antes'}, {'avisar': True},
                                        {'esperar': 50}, {'foto': 'despues'}, {'escribir': CMD}, {'foto': 'tercero'}])
        self.assertEqual(r['fotos']['antes'], [])
        self.assertEqual(r['fotos']['despues'], [{'terminal': 0, 'texto': CMD, 'enter': False},
                                                 {'terminal': 0, 'texto': OTRO, 'enter': False}])
        self.assertEqual(textos(r['fotos']['tercero']), [CMD, OTRO, CMD])  # ya lista: la tercera es inmediata
        self.assertEqual(r['terminales'], 1)

    def test_tl3_si_nunca_avisa_los_dos_salen_igual_en_orden(self):
        r = correr(espera=200, pasos=[{'escribir': CMD}, {'escribir': OTRO}, {'esperar': 700}, {'foto': 'despues'}])
        self.assertEqual(textos(r['fotos']['despues']), [CMD, OTRO])

    def test_tl3_un_error_al_crear_la_terminal_no_traba_los_pedidos_siguientes(self):
        r = correr(espera=0, falla_crear=True, pasos=[{'escribir': CMD}, {'esperar': 50}, {'escribir': OTRO}, {'esperar': 50}, {'foto': 'despues'}])
        self.assertEqual(r['errores'], ['no se pudo crear la terminal'])
        self.assertEqual(textos(r['fotos']['despues']), [OTRO])

    # --- tl4: constancia en la salida -----------------------------------------------------------------------------
    def test_tl4_la_salida_dice_por_que_y_cuanto_sin_el_comando(self):
        casos = {
            'lista': dict(espera=5000, pasos=[{'escribir': CMD}, {'esperar': 120}, {'avisar': True}, {'esperar': 50}]),
            'plazo': dict(espera=150, pasos=[{'escribir': CMD}, {'esperar': 500}]),
            'ya existía': dict(espera=5000, existente=True, pasos=[{'escribir': CMD}, {'esperar': 50}]),
            'integración ya informada': dict(espera=5000, integracion=True, pasos=[{'escribir': CMD}, {'esperar': 50}]),
        }
        for motivo, escenario in casos.items():
            [linea] = correr(**escenario)['salida']
            m = re.search(r'Terminal Factory: comando escrito \((.+); esperó (\d+) ms\)$', linea)
            self.assertIsNotNone(m, linea)
            self.assertEqual(m[1], motivo)
            self.assertNotIn('oracle-factory', linea)
            self.assertNotIn('estado', linea)
            if motivo in ('lista', 'plazo'):
                self.assertGreaterEqual(int(m[2]), 100, motivo)
            else:
                self.assertEqual(int(m[2]), 0, motivo)

    def test_tl4_el_plazo_se_puede_configurar_en_la_extension(self):
        propiedad = json.loads((EXTENSION / 'package.json').read_text())['contributes']['configuration']['properties']['factory.esperaTerminalMs']
        self.assertEqual((propiedad['type'], propiedad['default'], propiedad['minimum']), ('number', 3000, 0))


if __name__ == '__main__':
    unittest.main()
