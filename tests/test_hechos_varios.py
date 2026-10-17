"""Juzgar un candidato con hechos de varios sensores: escenarios hv1–hv2, en repositorios temporales con Oracle 0.39.0."""
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_estructura as _estructura  # noqa: E402

f, estructura = _estructura.f, _estructura.estructura


class HechosVarios(unittest.TestCase):
    # Los ayudantes de test_estructura sin heredar sus pruebas.
    setUp = _estructura.Estructura.setUp
    escribe, git, estado, salida = (_estructura.Estructura.escribe, _estructura.Estructura.git,
                                     _estructura.Estructura.estado, _estructura.Estructura.salida)
    cambio_medido, sha7 = _estructura.Estructura.cambio_medido, _estructura.Estructura.sha7

    def dos_sensores(self, ident, otra='otro_frente'):
        """Los hechos de dos frentes en la carpeta del candidato: el ejemplo de notas y otro sensor."""
        carpeta = estructura.ruta_canonica(self.root, ident, 'evidencia', self.sha7())
        carpeta.mkdir(parents=True, exist_ok=True)
        a, b = carpeta / 'hechos-notas.json', carpeta / 'hechos-otro.json'
        subprocess.run([sys.executable, 'examples/notas/sensor.py', '--salida', a], cwd=self.root, check=True,
                       capture_output=True)
        filas = json.loads(a.read_text())['comprobacion'] if otra == 'comprobacion' else [{'frente': 'b', 'ok': 1}]
        b.write_text(json.dumps({otra: filas}))
        return a, b

    def relativas(self, *rutas):
        return [p.relative_to(self.root).as_posix() for p in rutas]

    # --- hv1: juzgar acepta los hechos de varios sensores ---------------------------------------------------------
    def test_hv1_un_candidato_integrado_con_dos_sensores(self):
        ident = self.cambio_medido()
        a, b = self.dos_sensores(ident)
        self.salida()
        f.juzgar(ident, [a, b])
        oracle = self.estado(ident)['oracle']
        self.assertEqual(oracle['codigo'], 0)
        ra, rb = self.relativas(a, b)
        self.assertEqual((oracle['hechos'], oracle['hechos_sha256']), (ra, f.sha256(a.read_bytes())))
        self.assertEqual(oracle['hechos_mas'], [{'ruta': rb, 'sha256': f.sha256(b.read_bytes())}])
        self.assertEqual(f.hechos_registrados(oracle), [(ra, oracle['hechos_sha256']), (rb, f.sha256(b.read_bytes()))])
        # Oracle los recibió a los dos: el informe es el de un juicio con las dos relaciones.
        self.assertTrue(f.juicio_vigente(oracle, f.contexto_producto()))
        self.assertEqual(f.pendientes_actuales(*f.leer(ident)), [])
        juicio = [x['ruta'] for x in f.datos_donde(ident, None)['artefactos'] if x['gate'] == 'juicio']
        self.assertLessEqual({ra, rb}, set(juicio))
        self.assertEqual(f.datos_estado(ident)['oracle']['hechos_mas'], oracle['hechos_mas'])
        # Al revés también: la relación que miden las medidas viene en el segundo archivo, así que Oracle tuvo que recibirlo.
        f.juzgar(ident, [b, a])
        self.assertEqual(self.estado(ident)['oracle']['codigo'], 0)
        self.assertEqual(self.estado(ident)['oracle']['hechos'], rb)
        # Por la CLI de verdad, con --con repetido y rutas relativas, también.
        with self.escribe('1'), patch.object(sys, 'stdout', io.StringIO()):
            self.assertEqual(f.main(['--proyecto', str(self.root), 'juzgar', ident, '--con', ra, '--con', rb]), 0)
        self.assertEqual(self.estado(ident)['oracle']['hechos_mas'][0]['ruta'], rb)

    def test_hv1_uno_de_los_archivos_cambia_despues_del_juicio(self):
        ident = self.cambio_medido()
        a, b = self.dos_sensores(ident)
        f.juzgar(ident, [a, b])
        ra, rb = self.relativas(a, b)
        b.write_text(json.dumps({'otro_frente': [{'frente': 'b', 'ok': 0}]}))
        oracle = self.estado(ident)['oracle']
        self.assertFalse(f.juicio_vigente(oracle, f.contexto_producto()))
        self.assertIn(f'hechos {rb} cambiado o sin huella', f.pendientes_actuales(*f.leer(ident)))
        self.assertEqual(f.pasos(ident)[0], f'oracle-factory juzgar {ident} --con {ra} --con {rb}')
        # Si falta, también lo nombra; y uno que no es una ruta, igual.
        b.unlink()
        self.assertTrue(any(rb in p and 'ausentes' in p for p in f.pendientes_actuales(*f.leer(ident))))
        registro = self.root / '.factory/cambios' / ident / 'factory.json'
        datos = json.loads(registro.read_text())
        datos['oracle']['hechos_mas'] = [{'ruta': 5, 'sha256': 'x'}]
        registro.write_text(json.dumps(datos))
        self.assertIn('hechos no válido en el registro (no es una ruta de texto)', f.pendientes_actuales(*f.leer(ident)))

    def test_hv1_un_archivo_que_cambia_durante_el_juicio(self):
        ident = self.cambio_medido()
        a, b = self.dos_sensores(ident)
        ejecutar = f.ejecutar
        def y_otro_sensor_escribe(args, *resto, **claves):
            r = ejecutar(args, *resto, **claves)
            if 'cobertura' in args and '--con' in args:
                b.write_text(json.dumps({'otro_frente': [{'frente': 'b', 'ok': 2}]}))
            return r
        with patch.object(f, 'ejecutar', side_effect=y_otro_sensor_escribe), \
                self.assertRaisesRegex(f.FactoryError, 'cambiaron durante el juicio'):
            f.juzgar(ident, [a, b])
        self.assertIsNone(self.estado(ident).get('oracle'))

    def test_hv1_con_uno_solo_el_registro_es_el_de_siempre(self):
        ident = self.cambio_medido()
        a, _ = self.dos_sensores(ident)
        f.juzgar(ident, [a])
        self.assertNotIn('hechos_mas', self.estado(ident)['oracle'])
        f.juzgar(ident, a)  # una ruta sola, como antes
        self.assertNotIn('hechos_mas', self.estado(ident)['oracle'])

    # --- hv2: dos sensores no emiten la misma relación ------------------------------------------------------------
    def test_hv2_dos_frentes_que_emiten_la_misma_relacion(self):
        ident = self.cambio_medido()
        a, b = self.dos_sensores(ident, otra='comprobacion')
        self.salida()
        with self.assertRaises(f.FactoryError) as error:
            f.juzgar(ident, [a, b])
        texto = str(error.exception) + self.salida()
        self.assertIn(f'la relación «comprobacion» viene en «{a}» y en «{b}»', texto)
        self.assertIsNone(self.estado(ident).get('oracle'))  # no se registra un veredicto
        self.assertNotIn('oracle_ejecutado', [e['accion'] for e in self.estado(ident)['eventos']])


if __name__ == '__main__':
    unittest.main()
