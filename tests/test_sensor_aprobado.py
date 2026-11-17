"""El sensor que produce los hechos lo aprueba una persona: `aprobar-sensor` (sa1), `evidencia` sólo corre un sensor aprobado (sa2) y
los hechos de un sensor no aprobado no cuentan (sa3). Con la CLI en proceso y el ejemplo de notas."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_sensor_de_factory as _sf  # noqa: E402
from oracle_factory import sensor  # noqa: E402

f = _sf.f
OTRO = ['sh', '-c', 'mkdir -p {salida} && echo otro > {salida}/hechos.json']
TERCERO = ['sh', '-c', 'mkdir -p {salida} && echo señal > {salida}/hechos.json']
SOURCE = Path(__file__).resolve().parents[1]


class Base(_sf.Base):
    def aprobados(self):
        ruta = self.root / '.factory/sensor-aprobado.json'
        return json.loads(ruta.read_text(encoding='utf-8')) if ruta.exists() else None

    def huella(self):
        return sensor.huella(f.config_proyecto()['sensor'])

    def commitear(self, mensaje='sensor'):
        self.git('add', '.')
        self.git('commit', '-qm', mensaje)


class AprobarSa1(Base):
    def test_sa1_una_persona_aprueba_el_sensor(self):
        self.declarar(aprobar=False)
        self.assertIsNone(self.aprobados())
        self.salida()
        with self.escribe('1'):
            self.assertEqual(sensor.aprobar(), 0)
        mostrado = self.salida()
        self.assertIn(json.dumps(f.config_proyecto()['sensor'], ensure_ascii=False, indent=2), mostrado)  # ve lo que aprueba, entero
        [primera] = self.aprobados()
        self.assertEqual((primera['sha256'], primera['tipo_actor']), (self.huella(), 'persona'))
        self.assertTrue(primera['actor'] and primera['cuando'])
        self.assertEqual(primera['declaracion']['comando'], _sf.NOTAS)
        self.assertEqual(sensor.aprobar(), 0)  # ya aprobado: no pregunta nada ni lo registra dos veces
        self.assertIn('ya está aprobado', self.salida())
        self.assertEqual(len(self.aprobados()), 1)
        # Otra declaración: se ve la aprobada antes, y la lista conserva la primera.
        self.declarar(OTRO, aprobar=False)
        with self.escribe('1'):
            sensor.aprobar()
        mostrado = self.salida()
        self.assertIn('echo otro', mostrado)
        self.assertIn('examples/notas/sensor.py', mostrado)
        self.assertEqual([a['sha256'] for a in self.aprobados()], [primera['sha256'], self.huella()])
        # Cancelar no registra nada; y lo que se muestra como «último aprobado» es el último, no el primero.
        self.declarar(TERCERO, aprobar=False)
        self.salida()
        with self.escribe('2'), self.assertRaisesRegex(f.FactoryError, 'cancelad'):
            sensor.aprobar()
        mostrado = self.salida()
        self.assertIn('echo señal', mostrado)  # sin escapar: se lee como se escribió
        self.assertIn('echo otro', mostrado)
        self.assertNotIn('examples/notas/sensor.py', mostrado)
        self.assertEqual(len(self.aprobados()), 2)

    def test_sa1_la_huella_es_de_la_declaracion_entera_y_no_depende_del_orden(self):
        config = {'comando': ['echo', 'señal'], 'tope_minutos': 60, 'hechos': 'exigir'}
        esperada = hashlib.sha256('{"comando":["echo","señal"],"hechos":"exigir","tope_minutos":60}'.encode('utf-8')).hexdigest()
        self.assertEqual(sensor.huella(config), esperada)
        self.assertEqual(sensor.huella(dict(reversed(list(config.items())))), esperada)
        self.assertNotEqual(sensor.huella({**config, 'hechos': 'avisar'}), esperada)  # la política también se aprueba

    def test_sa1_por_la_cli_un_agente_se_niega(self):
        self.declarar(aprobar=False)
        r = subprocess.run([sys.executable, '-c', 'import sys; from oracle_factory.cli import main; sys.exit(main())', '--proyecto', str(self.root),
                            '--agente', 'claude-code', 'aprobar-sensor'], capture_output=True, text=True, stdin=subprocess.DEVNULL,
                           env={**os.environ, 'PYTHONPATH': str(SOURCE)})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('Aprobar este sensor', r.stderr)  # llegó al comando, y se negó por ser un agente
        self.assertIn('persona', r.stderr)
        self.assertIsNone(self.aprobados())

    def test_sa1_si_la_declaracion_cambia_mientras_se_aprueba_no_se_registra(self):
        self.declarar(aprobar=False)

        def responde(*_):  # entre que se muestra el sensor y se confirma, alguien cambia el comando
            self.declarar(OTRO, aprobar=False)
            return '1'
        with patch('builtins.input', side_effect=responde), self.assertRaisesRegex(f.FactoryError, 'cambiaron'):
            sensor.aprobar()
        self.assertIsNone(self.aprobados())

    def test_sa1_un_agente_no_puede(self):
        self.declarar(aprobar=False)
        with patch.object(f, 'AGENTE', 'claude-code'), self.escribe('1'), self.assertRaisesRegex(f.FactoryError, 'persona'):
            sensor.aprobar()
        self.assertIsNone(self.aprobados())

    def test_sa1_sin_sensor_declarado(self):
        with self.escribe('1'), self.assertRaisesRegex(f.FactoryError, r'"sensor"'):
            sensor.aprobar()
        self.assertIsNone(self.aprobados())


class EvidenciaSa2(Base):
    def test_sa2_cambiar_el_comando_del_sensor(self):
        # Lo que reprodujo la reauditoría de Fable (R1): cambiar el comando por uno que escribe hechos fijos «todo verde».
        ident = self.medido()
        self.declarar(hechos='exigir')
        self.commitear()
        self.revisado(ident)
        corrio = self.root.parent / 'corrio'
        verde = json.dumps({'comprobacion': [{'caso': c, 'codigo': 0} for c in ('vacío', 'espacios', 'válido')]})
        self.declarar(['sh', '-c', f"touch {corrio}; mkdir -p {{salida}} && printf '%s' '{verde}' > {{salida}}/hechos.json"],
                      hechos='exigir', aprobar=False)
        self.commitear('otro comando')
        with self.assertRaisesRegex(f.FactoryError, 'oracle-factory aprobar-sensor'):
            sensor.producir(ident, [])
        self.assertFalse(corrio.exists(), 'el comando sin aprobar llegó a correr')
        self.assertEqual(self.producciones(ident), [])
        self.assertFalse(self.evidencia(ident).exists())
        f.juzgar(ident, self.a_mano(ident))  # y con los hechos a mano, «exigir» sigue negando el cierre
        with self.escribe('1'), self.assertRaisesRegex(f.FactoryError, f'oracle-factory evidencia {ident}'):
            f.cerrar(ident)

    def test_sa2_un_sensor_nunca_aprobado(self):
        ident = self.medido()
        self.declarar(aprobar=False)
        self.commitear()
        with self.assertRaisesRegex(f.FactoryError, 'oracle-factory aprobar-sensor'):
            sensor.producir(ident, [])
        self.assertFalse(self.evidencia(ident).exists())
        self.assertEqual(self.producciones(ident), [])

    def test_sa2_un_archivo_de_aprobaciones_roto(self):
        ident = self.medido()
        self.declarar()
        self.commitear()
        ruta = self.root / '.factory/sensor-aprobado.json'
        bueno = ruta.read_text()
        for roto in ('{', '{}', '[1]', '[{"sha256": 1}]'):
            ruta.write_text(roto)
            with self.subTest(roto=roto), self.assertRaisesRegex(f.FactoryError, 'sensor-aprobado.json'):
                sensor.producir(ident, [])
            self.assertFalse(self.evidencia(ident).exists())
        f.mostrar(ident)  # las consultas siguen: con las aprobaciones rotas, ninguna cuenta
        ruta.write_text(bueno)
        sensor.producir(ident, [])

    def test_sa2_unos_hechos_que_son_un_enlace_no_valen(self):
        ident = self.medido()
        self.declarar(['sh', '-c', 'mkdir -p {salida} && echo x > {salida}/real && ln -s real {salida}/hechos.json'])
        self.commitear()
        with self.assertRaisesRegex(f.FactoryError, 'no dejó'):
            sensor.producir(ident, [])
        [p] = self.producciones(ident)
        self.assertIsNone(p['hechos_sha256'])

    def test_sa2_aprobado(self):
        ident = self.medido()
        self.declarar()
        self.commitear()
        sensor.producir(ident, [])
        [p] = self.producciones(ident)
        self.assertEqual(p['sensor_sha256'], self.huella())
        # Volver a una declaración que una persona ya aprobó no pide otra aprobación.
        self.declarar(OTRO)
        self.declarar(aprobar=False)
        self.assertTrue(sensor.aprobado(f.config_proyecto()['sensor']))


class HechosSa3(Base):
    def con_produccion(self):
        ident = self.medido()
        self.declarar(hechos='exigir')
        self.commitear()
        self.revisado(ident)
        sensor.producir(ident, [])
        return ident

    def cambiar_produccion(self, ident, cambio):
        carpeta, estado = f.leer(ident)
        [p] = [e for e in estado['eventos'] if e['accion'] == 'evidencia_producida']
        cambio(p)
        f.guardar(carpeta, estado)

    def test_sa3_una_produccion_sin_huella_de_sensor(self):
        ident = self.con_produccion()
        self.cambiar_produccion(ident, lambda p: p.pop('sensor_sha256'))  # como las registradas antes de este cambio
        self.salida()
        f.juzgar(ident, f.hechos_del_candidato(ident))
        self.assertIn('Hechos: declarados: no los produjo Factory', self.salida())
        f.mostrar(ident)
        self.assertIn('declarados: no los produjo Factory', self.salida())
        with self.escribe('1'), self.assertRaisesRegex(f.FactoryError, f'oracle-factory evidencia {ident}'):
            f.cerrar(ident)

    def test_sa3_una_produccion_de_un_sensor_que_nadie_aprobo(self):
        ident = self.con_produccion()
        self.cambiar_produccion(ident, lambda p: p.update(sensor_sha256='f' * 64))
        self.salida()
        f.juzgar(ident, f.hechos_del_candidato(ident))
        self.assertIn('Hechos: declarados: no los produjo Factory', self.salida())

    def test_sa3_con_el_sensor_aprobado_si_cuentan(self):
        ident = self.con_produccion()
        self.salida()
        f.juzgar(ident, f.hechos_del_candidato(ident))
        self.assertIn('Hechos: producidos por Factory', self.salida())
        with self.escribe('1'):
            f.cerrar(ident)
        self.assertEqual(f.leer(ident)[1]['fase'], 'cerrada')


if __name__ == '__main__':
    unittest.main()
