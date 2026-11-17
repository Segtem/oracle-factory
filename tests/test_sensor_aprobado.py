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
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import test_sensor_de_factory as _sf  # noqa: E402
from oracle_factory import sensor  # noqa: E402
from tools import verificar_cambio  # noqa: E402

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
        self.declarar()  # ya aprobado por una persona: con --agente se niega igual, no «termina bien»
        with patch.object(f, 'AGENTE', 'claude-code'), self.assertRaisesRegex(f.FactoryError, 'persona'):
            sensor.aprobar()
        self.assertEqual(len(self.aprobados()), 1)

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
        [entera] = json.loads(bueno)
        incompletas = [{k: v for k, v in entera.items() if k != campo} for campo in ('declaracion', 'actor', 'tipo_actor', 'cuando')]
        rotos = ['{', '{}', '[1]', '[{"sha256": 1}]', json.dumps([{'sha256': entera['sha256']}]),  # sólo el hash: no es una aprobación
                 *(json.dumps([i]) for i in incompletas),
                 json.dumps([{**entera, 'tipo_actor': 'agente'}]),  # no la aprobó una persona
                 json.dumps([{**entera, 'declaracion': {**entera['declaracion'], 'hechos': 'exigir'}}])]  # la huella no es la de su declaración
        for roto in rotos:
            ruta.write_text(roto)
            with self.subTest(roto=roto[:60]), self.assertRaisesRegex(f.FactoryError, 'sensor-aprobado.json'):
                sensor.producir(ident, [])
            self.assertFalse(self.evidencia(ident).exists())
        ruta.write_text(bueno)
        sensor.producir(ident, [])
        f.juzgar(ident, f.hechos_del_candidato(ident))
        ruta.write_text('{')  # con veredicto y las aprobaciones rotas, las consultas siguen y ninguna producción cuenta
        self.salida()
        f.mostrar(ident)
        self.assertIn('declarados: no los produjo Factory', self.salida())

    def test_sa2_no_se_aceptan_argumentos_extra(self):
        # Lo que encontraron codex y agy: con «evidencia ID -- …» se le agregaban al sensor argumentos que nadie aprobó.
        ident = self.medido()
        corrio = self.root.parent / 'corrio'
        self.declarar(['sh', '-c', f'touch {corrio}; mkdir -p {{salida}} && echo "$@" > {{salida}}/hechos.json', 'sensor'])
        self.commitear()
        with self.assertRaisesRegex(f.FactoryError, 'argumentos'):
            sensor.producir(ident, ['--otro', 'valor'])
        self.assertFalse(corrio.exists())
        self.assertEqual(self.producciones(ident), [])
        sensor.producir(ident, [])
        [p] = self.producciones(ident)
        self.assertEqual(p['comando'], f.config_proyecto()['sensor']['comando'])  # lo que corrió es lo aprobado, tal cual

    def test_sa2_el_entorno_de_quien_lo_corre_no_altera_los_hechos(self):
        # Lo que reprodujo codex: un PYTHONPATH con un sitecustomize.py que reescribe los hechos al salir.
        ident = self.medido()
        notas = self.root / 'examples/notas/notas.py'
        notas.write_text(notas.read_text().replace('return bool(', 'return True or bool(', 1))  # roto: el sensor real da fallas
        self.declarar()
        self.commitear('roto')
        trampa = self.root.parent / 'trampa'
        trampa.mkdir()
        (trampa / 'sitecustomize.py').write_text(
            'import atexit, json, sys\n'
            'def _verde():\n'
            '    if "--salida" in sys.argv:\n'
            '        open(sys.argv[sys.argv.index("--salida") + 1], "w").write(json.dumps({"comprobacion": '
            '[{"caso": c, "codigo": 0} for c in ("vacío", "espacios", "válido")]}))\n'
            'atexit.register(_verde)\n')
        falso = self.root.parent / 'binfalso'
        falso.mkdir()
        (falso / 'sh').write_text('#!/bin/sh\nexit 0\n')
        (falso / 'sh').chmod(0o755)
        sucio = {'PYTHONPATH': str(trampa), 'PYTHONSTARTUP': str(trampa / 'sitecustomize.py'), 'LD_PRELOAD': '/no/existe.so',
                 'BASH_ENV': str(trampa / 'x'), 'PATH': f"{falso}:{os.environ['PATH']}", 'HOME': str(trampa), 'CANARIO': 'si'}
        with patch.dict(os.environ, sucio):
            sensor.producir(ident, [])
        hechos = json.loads((self.evidencia(ident) / 'hechos.json').read_text())
        self.assertTrue([c for c in hechos['comprobacion'] if c['codigo'] != 0], 'los hechos los reescribió el entorno')

    def test_sa2_el_sensor_corre_con_un_entorno_minimo(self):
        ident = self.medido()
        self.declarar(['sh', '-c', 'mkdir -p {salida} && env > {salida}/hechos.json'])
        self.commitear()
        with patch.dict(os.environ, {'PYTHONPATH': '/trampa', 'CANARIO': 'si', 'PATH': f"/trampa/bin:{os.environ['PATH']}", 'HOME': '/trampa'}):
            sensor.producir(ident, [])
        visto = dict(l.split('=', 1) for l in (self.evidencia(ident) / 'hechos.json').read_text().splitlines() if '=' in l)
        self.assertNotIn('PYTHONPATH', visto)
        self.assertNotIn('CANARIO', visto)
        self.assertNotIn('/trampa', visto['PATH'])
        self.assertEqual(visto['PYTHONNOUSERSITE'], '1')
        self.assertIn('ORACLE_FACTORY_CHECKOUT', visto)
        import pwd
        self.assertEqual(visto['HOME'], pwd.getpwuid(os.getuid()).pw_dir)

    def test_sa2_las_carpetas_del_sistema_van_primero_en_el_path(self):
        # Lo que encontró codex: ~/.local/bin antes que /usr/bin dejaba que un «sh» puesto ahí suplantara al del comando aprobado.
        visto = sensor.entorno_minimo()['PATH'].split(os.pathsep)
        sistema = [visto.index(c) for c in ('/usr/local/bin', '/usr/bin', '/bin')]
        de_usuario = [visto.index(c) for c in (str(Path(sys.executable).parent), str(Path.home() / '.local' / 'bin')) if c in visto]
        self.assertLess(max(sistema), min(de_usuario))

    def test_sa2_el_git_que_arma_el_checkout_no_es_el_del_path_de_quien_lo_corre(self):
        # Lo que encontró codex: un «git» falso en el PATH heredado podía cambiar el código del checkout antes de correr el sensor.
        ident = self.medido()
        self.declarar()
        self.commitear()
        falso = self.root.parent / 'gitfalso'
        falso.mkdir()
        marca = self.root.parent / 'usaron-el-git-falso'
        (falso / 'git').write_text(f'#!/bin/sh\necho "$@" >> {marca}\nexec /usr/bin/git "$@"\n')
        (falso / 'git').chmod(0o755)
        with patch.dict(os.environ, {'PATH': f"{falso}:{os.environ['PATH']}", 'GIT_CONFIG_GLOBAL': str(self.root.parent / 'no-existe')}):
            sensor.producir(ident, [])
        # Factory mismo puede usar el git del PATH para lo suyo (por ejemplo, el nombre de quien registra el evento); lo que no
        # puede es que ese git elija el commit o arme el checkout que corre el sensor.
        usos = marca.read_text().splitlines() if marca.exists() else []
        self.assertFalse([u for u in usos if {'clone', 'checkout', 'rev-parse', 'diff', 'ls-files', 'remote'} & set(u.split())],
                         'el commit o el checkout los resolvió un git del PATH de quien corre evidencia')
        self.assertEqual(len(self.producciones(ident)), 1)

    def test_sa2_el_verificador_deduce_el_modulo_de_las_medidas_confirmadas(self):
        # Sin argumentos extra, tools/verificar_cambio.py saca el módulo de pruebas de las medidas que confirmó una persona.
        registro = self.root / '.factory/cambios/20990101-000000-abc-demo/factory.json'
        registro.parent.mkdir(parents=True)

        def con(medidas):
            registro.write_text(json.dumps({'medidas': medidas}))
            return verificar_cambio.modulo_del_cambio(self.root, '20990101-000000-abc-demo')
        uno = {'catalogos': {'factory_demo.el_primero': 'a' * 64, 'factory_demo.corrida_completa': 'b' * 64}}
        self.assertEqual(con({'flujo_x.el_primero': uno, 'flujo_x.el_segundo': {'catalogos': {'factory_demo.el_segundo': 'c' * 64}}}), 'test_demo')
        for medidas in ({}, {'r': {'catalogos': {}}}, {'r': uno, 's': {'catalogos': {'factory_otro.x': 'd' * 64}}}, {'r': {'catalogos': {'notas.resultados': 'e' * 64}}}):
            with self.subTest(medidas=medidas), self.assertRaisesRegex(verificar_cambio.ContratoInvalido, '--pruebas'):
                con(medidas)

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
