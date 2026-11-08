"""Frenos de construcción: escenarios fr1–fr2 (los avisos de estado que mandan parar), con Git de verdad para el estado."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import test_tests_editados as _te  # noqa: E402
from oracle_factory import estructura, frenos  # noqa: E402

f = _te.f
SIN = {'bucle_de_revision': None, 'cambio_grande': None}
GRANDE = {'bucle_de_revision': {'rondas': 5, 'umbral': 4, 'avisa': True}, 'cambio_grande': {'lineas': 900, 'umbral': 450, 'avisa': True}}


def juicio(codigo):
    return {'accion': 'oracle_ejecutado', 'codigo': codigo, 'cuando': '2026-11-01T10:00:00'}


def calcular(eventos=(), informes=(), aprobada=False, editados=None, flujo=SIN, candidato='abc1234'):
    return frenos.calcular({'eventos': list(eventos)}, list(informes), candidato, aprobada, editados, flujo)


def ids(lista):
    return [x['id'] for x in lista]


def informe(severidad, candidato='abc1234'):
    return {'revisor': 'codex', 'candidato': candidato, 'hallazgos': [{'severity': severidad, 'title': 't'}]}


class Calculo(unittest.TestCase):
    # --- fr1: los frenos salen de los datos del cambio ---------------------------------------------------------------------
    def test_fr1_dos_juicios_rojos_seguidos_frenan_y_un_verde_o_un_solo_rojo_no(self):
        [freno] = calcular([juicio(1), juicio(1)])
        self.assertEqual(freno['id'], 'juicios_rojos')
        self.assertTrue(freno['motivo'])
        self.assertEqual(calcular([juicio(1), juicio(0), juicio(1)]), [])
        self.assertEqual(calcular([juicio(1)]), [])
        self.assertEqual(calcular([juicio(1), juicio(1), juicio(0)]), [])
        self.assertEqual(ids(calcular([juicio(0), juicio(1), juicio(2)])), ['juicios_rojos'])
        self.assertEqual(calcular([{'accion': 'mensaje'}, juicio(1), {'accion': 'mensaje'}]), [])  # lo que no es un juicio no corta ni suma

    def test_fr1_un_hallazgo_alto_del_candidato_frena_salvo_con_revision_aprobada_vigente(self):
        self.assertEqual(ids(calcular(informes=[informe('alta')])), ['hallazgo_alto_abierto'])
        self.assertEqual(calcular(informes=[informe('alta')], aprobada=True), [])
        self.assertEqual(calcular(informes=[informe('media'), informe('baja')]), [])
        self.assertEqual(calcular(informes=[informe('alta', candidato='fffffff')]), [])  # de otra ronda
        self.assertEqual(ids(calcular(informes=[informe('alta', candidato='ABC1234567')])), ['hallazgo_alto_abierto'])
        self.assertEqual(calcular(informes=[informe('alta')], candidato=None), [])  # sin candidato vigente no hay a qué atar el hallazgo

    def test_fr1_prueba_editada_cambio_grande_y_bucle_frenan_con_lo_que_ya_calcula_estado(self):
        editados = [{'archivo': 'tests/test_a.py', 'estado': 'modificado', 'origen': None, 'lineas_quitadas': 2, 'tests_quitados': [], 'asserts_quitados': 1}]
        self.assertEqual(ids(calcular(editados=editados)), ['prueba_existente_editada'])
        self.assertEqual(ids(calcular(flujo=GRANDE)), ['cambio_grande', 'bucle_de_revision'])
        self.assertEqual(calcular(editados=[]), [])
        todo = calcular([juicio(1), juicio(1)], [informe('alta')], editados=editados, flujo=GRANDE)
        self.assertEqual(ids(todo), ['juicios_rojos', 'hallazgo_alto_abierto', 'prueba_existente_editada', 'cambio_grande', 'bucle_de_revision'])
        self.assertTrue(all(isinstance(x['motivo'], str) and x['motivo'] for x in todo))

    def test_fr1_un_dato_ilegible_no_inventa_un_freno_ni_rompe(self):
        for estado in ({}, {'eventos': None}, {'eventos': 'x'}, {'eventos': [None, 3, 'x']}, None):
            with self.subTest(estado=estado):
                self.assertEqual(frenos.calcular(estado, [], 'abc1234', False, None, SIN), [])
        self.assertEqual(calcular([juicio(None), juicio('x'), juicio(True)]), [])  # un código que no es un entero no cuenta
        raros = [None, 3, {'hallazgos': None}, {'candidato': 'abc1234', 'hallazgos': 'x'}, {'candidato': 'abc1234', 'hallazgos': [None, 3, {'severity': None}]},
                 {'candidato': None, 'hallazgos': [{'severity': 'alta'}]}]
        self.assertEqual(calcular(informes=raros), [])
        self.assertEqual(frenos.calcular({'eventos': []}, None, 'abc1234', False, None, None), [])
        self.assertEqual(frenos.calcular({'eventos': []}, [], 'abc1234', False, None, {'bucle_de_revision': 'x', 'cambio_grande': 3}), [])


class EstadoReal(_te.Base):
    # --- fr2: estado los muestra, sin cambiar nada más ----------------------------------------------------------------------
    def informe_alto(self, sha):
        carpeta = estructura.ruta_canonica(self.root, self.ident, 'revision', sha)
        carpeta.mkdir(parents=True, exist_ok=True)
        (carpeta / 'codex-1.json').write_text(json.dumps({'findings': [{'severity': 'alta', 'title': 'grave'}]}))

    def agregar_juicios_rojos(self):
        carpeta, estado = f.leer(self.ident)
        estado.setdefault('eventos', []).extend([juicio(1), juicio(1)])
        f.guardar(carpeta, estado)

    def test_fr2_con_frenos_estado_los_lista_en_el_json_y_en_el_texto_sin_cambiar_lo_demas(self):
        self.preparar()
        sha = self.candidato(lambda: (self.root / 'src/chico.py').write_text('x = 1\n'))
        antes = f.datos_estado(self.ident)
        self.assertEqual(antes['frenos'], [])
        self.assertFalse(any(a.startswith('FRENO:') for a in antes['avisos']))
        self.informe_alto(sha)
        self.agregar_juicios_rojos()
        texto, datos = self.estado()
        self.assertEqual(ids(datos['frenos']), ['juicios_rojos', 'hallazgo_alto_abierto'])
        for freno in datos['frenos']:
            self.assertIn(f"FRENO: {freno['motivo']}", datos['avisos'])
            self.assertIn(f"FRENO: {freno['motivo']}", texto)
        self.assertEqual((datos['pendientes'], datos['proximo_paso'], datos['alternativas']),
                         (antes['pendientes'], antes['proximo_paso'], antes['alternativas']))  # un freno no decide nada

    def test_fr2_sin_frenos_la_lista_esta_vacia_y_no_hay_avisos(self):
        self.preparar()
        self.candidato(lambda: (self.root / 'src/chico.py').write_text('x = 1\n'))
        texto, datos = self.estado()
        self.assertEqual(datos['frenos'], [])
        self.assertNotIn('FRENO:', texto)

    def test_fr2_un_cambio_abandonado_no_lleva_frenos_y_un_registro_roto_no_rompe_estado(self):
        self.preparar()
        carpeta, estado = f.leer(self.ident)
        estado['eventos'] = [{'accion': 'oracle_ejecutado'}, {'codigo': 1}, {'accion': 'oracle_ejecutado', 'codigo': 'x'}] + (estado.get('eventos') or [])
        f.guardar(carpeta, estado)
        self.assertEqual(f.datos_estado(self.ident)['frenos'], [])
        estado['fase'] = 'abandonada'
        estado['eventos'] = (estado.get('eventos') or []) + [juicio(1), juicio(1)]
        f.guardar(carpeta, estado)
        self.assertEqual(f.datos_estado(self.ident)['frenos'], [])


if __name__ == '__main__':
    unittest.main()
