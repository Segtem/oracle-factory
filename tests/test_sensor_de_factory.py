"""Factory produce los hechos: `oracle-factory evidencia` corre el sensor del proyecto sobre el commit (sf1), `juzgar` y `estado` dicen de
dónde salen los hechos (sf2), «exigir» pide hechos de Factory para cerrar (sf3) y el titular dice lo que garantiza (sf4). En proyectos
temporales con la CLI en proceso y el ejemplo de notas."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_archivo as _archivo  # noqa: E402
from oracle_factory import almacenes, sensor  # noqa: E402

f = _archivo.f
SOURCE = Path(__file__).resolve().parents[1]
NOTAS = ['sh', '-c', 'mkdir -p {salida} && {python} examples/notas/sensor.py --salida {salida}/hechos.json']


class Base(unittest.TestCase):
    setUp, escribe, git, salida = _archivo.Archivo.setUp, _archivo.Archivo.escribe, _archivo.Archivo.git, _archivo.Archivo.salida

    def declarar(self, comando=None, **mas):
        """El sensor en `.factory/config.json`, commiteado: la configuración no es un cambio de producto."""
        ruta = self.root / '.factory/config.json'
        datos = json.loads(ruta.read_text(encoding='utf-8'))
        datos['sensor'] = {'comando': comando or NOTAS, **mas}
        ruta.write_text(json.dumps(datos, indent=2), encoding='utf-8')

    def medido(self):
        """El ejemplo de notas con su spec aprobada, sus medidas decididas y el producto commiteado."""
        ident = f.nuevo('Nota', con_ejemplo='notas')
        with self.escribe('1'):
            f.aprobar_spec(ident)
        f.importar(ident)
        rid = f.leer(ident)[1]['requisitos'][0]
        f.medir(ident, requisito_id=rid, medidas=['notas.casos_ejecutados', 'notas.resultados'], quitar_sin_medir=True)
        self.git('add', '.')
        self.git('commit', '-qm', 'producto fixture')
        return ident

    def producciones(self, ident):
        return [e for e in f.leer(ident)[1].get('eventos', []) if e['accion'] == 'evidencia_producida']

    def evidencia(self, ident):
        sha = self.git('rev-parse', '--short=7', 'HEAD')
        return f.estructura.ruta_canonica(self.root, ident, 'evidencia', sha)

    def revisado(self, ident):
        informe = self.root / 'tareas' / ident / 'revision.md'
        informe.write_text('Fixture de revisión; no es una revisión real.\n')
        with self.escribe('1'):
            f.revisar(ident, informe, 'Persona fixture', 'aprobar', 0)

    def a_mano(self, ident):
        """Lo que reprodujo Fable (N1): un hechos.json «todo verde» escrito a mano en la carpeta de evidencia del candidato."""
        carpeta = self.evidencia(ident)
        carpeta.mkdir(parents=True, exist_ok=True)
        (carpeta / 'hechos.json').write_text(json.dumps({'comprobacion': [{'caso': c, 'codigo': 0} for c in ('vacío', 'espacios', 'válido')]}))
        return carpeta / 'hechos.json'


class EvidenciaSf1(Base):
    def test_sf1_los_hechos_salen_del_commit_no_del_arbol_de_trabajo(self):
        ident = self.medido()
        (self.root / 'dato.txt').write_text('del commit\n')
        (self.root / '.gitignore').write_text((self.root / '.gitignore').read_text() + 'local.txt\n' if (self.root / '.gitignore').exists() else 'local.txt\n')
        self.declarar(['sh', '-c', 'mkdir -p {salida} && { cat dato.txt; test -e local.txt && echo hay-local; true; } > {salida}/hechos.json'])
        self.git('add', '.')
        self.git('commit', '-qm', 'dato')
        (self.root / 'local.txt').write_text('sólo en el árbol de trabajo\n')  # ignorado: no es un cambio de producto, y el checkout no lo tiene
        sensor.producir(ident, [])
        hechos = self.evidencia(ident) / 'hechos.json'
        self.assertEqual(hechos.read_text(), 'del commit\n')
        [p] = self.producciones(ident)
        self.assertEqual(p['commit'], self.git('rev-parse', 'HEAD'))
        self.assertEqual(p['codigo'], 0)
        self.assertEqual(p['hechos_sha256'], f.sha256(hechos.read_bytes()))
        self.assertIn('{salida}', ' '.join(p['comando']))  # el comando declarado, sin las rutas de esta máquina
        self.assertEqual(p['tipo_actor'], 'persona')
        self.assertFalse(list((self.root / '.factory/local/sensores').glob('*')))  # el checkout no queda
        with self.assertRaisesRegex(f.FactoryError, 'ya hay evidencia'):  # sobre el mismo commit no se pisa la que hay
            sensor.producir(ident, [])
        self.assertEqual(len(self.producciones(ident)), 1)
        # El código roto y commiteado sale rojo, aunque haya hechos verdes escritos a mano en otro lado (Fable N1).
        notas = self.root / 'examples/notas/notas.py'
        notas.write_text(notas.read_text().replace('return bool(', 'return True or bool(', 1))
        self.declarar()
        self.git('add', '.')
        self.git('commit', '-qm', 'roto')
        sensor.producir(ident, [])
        observados = json.loads((self.evidencia(ident) / 'hechos.json').read_text())
        self.assertTrue([c for c in observados['comprobacion'] if c['codigo'] != 0], observados)

    def test_sf1_el_checkout_encuentra_los_registros(self):
        ident = self.medido()
        self.declarar(['sh', '-c', 'mkdir -p {salida} && {python} -c "import sys; sys.path.insert(0, sys.argv[1]); from pathlib import Path; '
                       'from oracle_factory import almacenes; print(almacenes.registros_de(Path(\'.\')))" ' + str(SOURCE) + ' > {salida}/hechos.json'])
        self.git('add', '.')
        self.git('commit', '-qm', 'sensor')
        sensor.producir(ident, [])
        self.assertEqual(Path((self.evidencia(ident) / 'hechos.json').read_text().strip()), self.root.resolve())
        # Fuera del checkout, la variable no vale: un producto temporal sigue siendo él mismo.
        otro = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: subprocess.run(['rm', '-rf', str(otro)]))
        subprocess.run(['git', 'init', '-q', str(otro)], check=True)
        antes = {k: os.environ.get(k) for k in ('ORACLE_FACTORY_CHECKOUT', 'ORACLE_FACTORY_REGISTROS')}
        os.environ.update(ORACLE_FACTORY_CHECKOUT=str(self.root / 'otro-checkout'), ORACLE_FACTORY_REGISTROS=str(self.root))
        try:
            self.assertEqual(almacenes.registros_de(otro), otro)
        finally:
            for k, v in antes.items():
                os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)

    def test_sf1_un_producto_con_cambios_sin_commitear(self):
        ident = self.medido()
        self.declarar()
        self.git('add', '.')
        self.git('commit', '-qm', 'sensor')
        notas = self.root / 'examples/notas/notas.py'
        notas.write_text(notas.read_text() + '\n# a medio hacer\n')
        with self.assertRaisesRegex(f.FactoryError, 'examples/notas/notas.py'):
            sensor.producir(ident, [])
        self.assertFalse(self.evidencia(ident).exists())
        self.assertEqual(self.producciones(ident), [])

    def test_sf1_sin_sensor_declarado(self):
        ident = self.medido()
        with self.assertRaisesRegex(f.FactoryError, r'"sensor"'):
            sensor.producir(ident, [])
        ruta = self.root / '.factory/config.json'  # una declaración que no sirve se rechaza al leer la configuración
        for malo in ({'comando': 'texto'}, {'comando': []}, {'comando': ['sh', 3]}, {'comando': NOTAS, 'hechos': 'quizás'}, {'comando': NOTAS, 'tope_minutos': 0},
                     {'comando': NOTAS, 'otro': 1}):
            datos = json.loads(ruta.read_text(encoding='utf-8'))
            datos['sensor'] = malo
            ruta.write_text(json.dumps(datos), encoding='utf-8')
            with self.subTest(malo=malo), self.assertRaisesRegex(f.FactoryError, 'sensor'):
                f.config_proyecto()

    def test_sf1_un_sensor_que_se_pasa_del_tope(self):
        ident = self.medido()
        pid = Path(self.root.parent) / 'hijo.pid'
        self.declarar(['sh', '-c', f'sleep 60 & echo $! > {pid}; wait'], tope_minutos=0.02)
        self.git('add', '.')
        self.git('commit', '-qm', 'sensor')
        inicio = time.monotonic()
        with self.assertRaisesRegex(f.FactoryError, '124'):
            sensor.producir(ident, [])
        self.assertLess(time.monotonic() - inicio, 30)
        [p] = self.producciones(ident)
        self.assertEqual(p['codigo'], 124)
        hijo = int(pid.read_text())
        for _ in range(40):
            try:
                os.kill(hijo, 0)
            except ProcessLookupError:
                break
            time.sleep(0.1)
        else:
            os.kill(hijo, 9)
            self.fail('el hijo del sensor siguió vivo tras el tope')


class OrigenSf2(Base):
    def test_sf2_hechos_producidos_por_factory(self):
        ident = self.medido()
        self.declarar()
        self.git('add', '.')
        self.git('commit', '-qm', 'sensor')
        sensor.producir(ident, [])
        self.salida()
        f.juzgar(ident, f.hechos_del_candidato(ident))
        corto = self.git('rev-parse', '--short=7', 'HEAD')
        self.assertIn(f'Hechos: producidos por Factory (oracle-factory evidencia, commit {corto})', self.salida())
        f.mostrar(ident)
        self.assertIn(f'producidos por Factory (oracle-factory evidencia, commit {corto})', self.salida())

    def test_sf2_hechos_escritos_a_mano(self):
        ident = self.medido()
        f.juzgar(ident, self.a_mano(ident))
        self.assertIn('Hechos: declarados: no los produjo Factory', self.salida())
        f.mostrar(ident)
        self.assertIn('declarados: no los produjo Factory', self.salida())

    def test_sf2_hechos_producidos_y_despues_editados(self):
        ident = self.medido()
        self.declarar()
        self.git('add', '.')
        self.git('commit', '-qm', 'sensor')
        sensor.producir(ident, [])
        hechos = f.hechos_del_candidato(ident)
        hechos.write_text(hechos.read_text().replace('"codigo": 1', '"codigo": 0'))
        hechos.write_text(hechos.read_text() + '\n')  # aunque no haya nada que «arreglar», otra huella ya no es la producida
        self.salida()
        f.juzgar(ident, hechos)
        self.assertIn('Hechos: declarados: no los produjo Factory', self.salida())

    def test_sf2_hechos_producidos_para_otro_candidato(self):
        ident = self.medido()
        self.declarar()
        self.git('add', '.')
        self.git('commit', '-qm', 'sensor')
        sensor.producir(ident, [])
        viejos = f.hechos_del_candidato(ident).read_bytes()
        notas = self.root / 'examples/notas/notas.py'
        notas.write_text(notas.read_text() + '\n# otro candidato\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'otro candidato')
        copia = self.evidencia(ident) / 'hechos.json'  # los mismos bytes, en la carpeta del candidato nuevo
        copia.parent.mkdir(parents=True)
        copia.write_bytes(viejos)
        self.salida()
        f.juzgar(ident, copia)
        self.assertIn('Hechos: declarados: no los produjo Factory', self.salida())

    def test_sf2_dos_sensores_uno_a_mano(self):
        ident = self.medido()
        self.declarar()
        self.git('add', '.')
        self.git('commit', '-qm', 'sensor')
        sensor.producir(ident, [])
        otro = self.root / 'tareas' / ident / 'otro.json'
        otro.parent.mkdir(parents=True, exist_ok=True)
        otro.write_text(json.dumps({'otra_relacion': [{'x': 1}]}))
        self.salida()
        try:
            f.juzgar(ident, [f.hechos_del_candidato(ident), otro])
        except f.FactoryError:
            pass  # el veredicto puede no salir verde; lo que importa es de dónde dice que salen
        self.salida()
        f.mostrar(ident)
        self.assertIn('Hechos: declarados: no los produjo Factory', self.salida())


class ExigirSf3(Base):
    def test_sf3_exigir_con_hechos_escritos_a_mano(self):
        ident = self.medido()
        self.declarar(hechos='exigir')
        self.git('add', '.')
        self.git('commit', '-qm', 'sensor')
        self.revisado(ident)
        f.juzgar(ident, self.a_mano(ident))
        self.assertTrue([p for p in f.pendientes_actuales(*f.leer(ident)) if 'no los produjo Factory' in p])
        with self.escribe('1'), self.assertRaisesRegex(f.FactoryError, f'oracle-factory evidencia {ident}'):
            f.cerrar(ident)
        self.assertNotEqual(f.leer(ident)[1]['fase'], 'cerrada')

    def test_sf3_exigir_con_hechos_de_factory(self):
        ident = self.medido()
        self.declarar(hechos='exigir')
        self.git('add', '.')
        self.git('commit', '-qm', 'sensor')
        self.revisado(ident)
        sensor.producir(ident, [])
        f.juzgar(ident, f.hechos_del_candidato(ident))
        self.assertEqual([p for p in f.pendientes_actuales(*f.leer(ident)) if 'Factory' in p], [])
        with self.escribe('1'):
            f.cerrar(ident)
        self.assertEqual(f.leer(ident)[1]['fase'], 'cerrada')

    def test_sf3_avisar(self):
        ident = self.medido()
        self.revisado(ident)
        f.juzgar(ident, self.a_mano(ident))
        self.salida()
        with self.escribe('1'):
            f.cerrar(ident)
        self.assertEqual(f.leer(ident)[1]['fase'], 'cerrada')
        self.assertIn('no los produjo Factory', self.salida())


class TitularSf4(unittest.TestCase):
    def test_sf4_el_readme_y_el_sitio(self):
        readme = (SOURCE / 'README.md').read_text(encoding='utf-8')
        primero = readme.split('\n\n')[1]
        sitio = (SOURCE / 'site/index.html').read_text(encoding='utf-8')
        for texto in (primero, sitio):
            self.assertIn('oracle-factory evidencia', texto)
            self.assertIn('código del proyecto', texto)
        guias = [readme, (SOURCE / 'site/factory.js').read_text(encoding='utf-8')]
        guias += [p.read_text(encoding='utf-8') for p in sorted((SOURCE / 'docs').rglob('*.md'))]
        guias += [p.read_text(encoding='utf-8') for p in sorted((SOURCE / 'site').glob('*.html'))]
        for texto in guias:
            self.assertNotRegex(texto.lower(), r'no ejecuta el sensor')


if __name__ == '__main__':
    unittest.main()
