"""La procedencia de las dependencias: escenarios pr1–pr5, en proyectos temporales y sin red."""
import argparse
import json
from pathlib import Path
import stat
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_archivo as _archivo  # noqa: E402
from oracle_factory import procedencia  # noqa: E402

f = _archivo.f
H = {c: c * 64 for c in "abcdef"}


def lock(proyecto='1.0.0', paquetes=None, directas=None):
    paquetes = paquetes if paquetes is not None else [('alfa', '1.2.3', ('a', 'b')), ('beta', '2.0.1', ('c',))]
    directas = directas if directas is not None else [('alfa', '==1.2.3'), ('beta', '>=2')]
    t = ['version = 1', 'revision = 3', 'requires-python = ">=3.11"', '',
         '[[package]]', 'name = "demo"', f'version = "{proyecto}"', 'source = { editable = "." }', '', '[package.metadata]',
         'requires-dist = [' + ', '.join(f'{{ name = "{n}", specifier = "{e}" }}' for n, e in directas) + ']', '']
    for nombre, version, hashes in paquetes:
        t += ['[[package]]', f'name = "{nombre}"', f'version = "{version}"', 'source = { registry = "https://pypi.org/simple" }',
              f'sdist = {{ url = "https://files.example/{nombre}.tar.gz", hash = "sha256:{H[hashes[0]]}" }}',
              'wheels = [' + ', '.join(f'{{ url = "https://files.example/{nombre}-{h}.whl", hash = "sha256:{H[h]}" }}' for h in hashes[1:] or hashes[:1]) + ']', '']
    return '\n'.join(t)


class Procedencia(unittest.TestCase):
    python = None
    setUp, escribe, git, salida = (_archivo.Archivo.setUp, _archivo.Archivo.escribe, _archivo.Archivo.git, _archivo.Archivo.salida)

    def proyecto(self, *, con_lock=True, lock_texto=None, version='1.0.0', dependencias=('alfa==1.2.3', 'beta>=2'),
                 instalado=None):
        """pyproject.toml, uv.lock y un «python» de mentira que informa lo instalado (None: no hay entorno)."""
        (self.root / 'pyproject.toml').write_text('[project]\nname = "demo"\nversion = "%s"\ndependencies = [%s]\n' % (
            version, ', '.join(f'"{d}"' for d in dependencias)))
        if con_lock:
            (self.root / 'uv.lock').write_text(lock_texto if lock_texto is not None else lock())
        self.python = None
        if instalado is not None:
            (self.root / 'entorno').mkdir(exist_ok=True)
            self.python = self.root / 'entorno/python'
            self.python.write_text("#!/bin/sh\ncat <<'FIN'\n%s\nFIN\n" % json.dumps(instalado))
            self.python.chmod(self.python.stat().st_mode | stat.S_IXUSR)

    def correr(self, **kw):
        args = argparse.Namespace(id=None, python=str(self.python) if self.python else None, json=False, buscar=None, auditar=False, avisos=None)
        for k, v in kw.items():
            setattr(args, k, v)
        self.salida()
        f.comando_procedencia(args)
        return self.salida()

    def bom(self, **kw):
        return json.loads(self.correr(json=True, **kw))

    def componente(self, bom, nombre):
        return next(c for c in bom['components'] if c['name'] == nombre)

    def prop(self, c, nombre):
        return procedencia.propiedad(c, nombre)

    # --- pr1: el inventario dice qué hay y de dónde viene ----------------------------------------------------------------
    def test_pr1_un_proyecto_con_lock_lista_cada_componente_con_su_origen_y_sus_hashes(self):
        self.proyecto(instalado={'alfa': '1.2.3', 'beta': '2.0.1'})
        bom = self.bom()
        self.assertEqual((bom['bomFormat'], bom['specVersion']), ('CycloneDX', '1.5'))
        self.assertEqual([(c['name'], c['version']) for c in bom['components']], [('alfa', '1.2.3'), ('beta', '2.0.1')])
        alfa, beta = (self.componente(bom, n) for n in ('alfa', 'beta'))
        self.assertEqual((alfa['purl'], alfa['bom-ref']), ('pkg:pypi/alfa@1.2.3', 'pkg:pypi/alfa@1.2.3'))
        self.assertEqual([h['content'] for h in alfa['hashes']], [H['a'], H['b']])
        self.assertTrue(all(h['alg'] == 'SHA-256' for h in alfa['hashes']))
        self.assertEqual([h['content'] for h in beta['hashes']], [H['c']])
        for c in (alfa, beta):
            self.assertEqual(self.prop(c, 'factory:origen'), 'https://pypi.org/simple')
            self.assertEqual(self.prop(c, 'factory:fuente'), 'uv.lock')
        self.assertEqual((self.prop(alfa, 'factory:directa'), self.prop(alfa, 'factory:exigida'), self.prop(alfa, 'factory:fijada')), ('true', '==1.2.3', 'true'))
        self.assertEqual((self.prop(beta, 'factory:directa'), self.prop(beta, 'factory:exigida')), ('true', '>=2'))
        self.assertEqual(bom['metadata']['component'], {'type': 'application', 'name': 'demo', 'version': '1.0.0'})

    def test_pr1_una_dependencia_que_no_es_directa_lo_dice(self):
        self.proyecto(lock_texto=lock(paquetes=[('alfa', '1.2.3', ('a',)), ('gama', '9.9', ('d',))], directas=[('alfa', '==1.2.3')]),
                      dependencias=('alfa==1.2.3',), instalado={'alfa': '1.2.3', 'gama': '9.9'})
        gama = self.componente(self.bom(), 'gama')
        self.assertEqual((self.prop(gama, 'factory:directa'), self.prop(gama, 'factory:exigida')), ('false', ''))
        self.assertEqual(self.prop(gama, 'factory:fijada'), 'true')  # el lock la fija con sus hashes

    def test_pr1_un_proyecto_sin_lock_usa_lo_instalado_y_lo_dice(self):
        self.proyecto(con_lock=False, instalado={'Alfa_Dos': '1.0', 'beta': '2.0.1', 'demo': '1.0.0'})
        bom = self.bom()
        self.assertEqual([(c['name'], c['version']) for c in bom['components']], [('Alfa_Dos', '1.0'), ('beta', '2.0.1')])  # sin el propio proyecto
        for c in bom['components']:
            self.assertEqual(self.prop(c, 'factory:fuente'), 'instalado')
            self.assertEqual(self.prop(c, 'factory:origen'), 'desconocido')
            self.assertEqual((c['hashes'], self.prop(c, 'factory:fijada')), ([], 'false'))
        self.assertEqual(self.prop(self.componente(bom, 'beta'), 'factory:exigida'), '>=2')
        propiedades = {p['name']: p['value'] for p in bom['metadata']['properties'] if p['name'] != 'factory:diferencia'}
        self.assertEqual(propiedades['factory:confiable'], 'false')
        self.assertIn('no hay uv.lock', self.correr().split('\n')[2])

    def test_pr1_sin_lock_ni_entorno_no_hay_componentes_y_se_dice(self):
        self.proyecto(con_lock=False)
        bom = self.bom()
        self.assertEqual(bom['components'], [])
        diferencias = [p['value'] for p in bom['metadata']['properties'] if p['name'] == 'factory:diferencia']
        self.assertEqual(len(diferencias), 2)
        self.assertTrue(any('no se pudo leer el entorno' in d for d in diferencias))

    def test_pr1_una_version_corregida_por_lightwell_se_reconoce(self):
        self.proyecto(lock_texto=lock(paquetes=[('a1', '1.0.rhlw-00001', ('a',)), ('a2', '2.0+rhlw.00002', ('b',)), ('a3', '3.0-rhlw-1', ('c',)),
                                                ('a4', '4.0', ('d',)), ('a5', '5.0rc1', ('e',)), ('a6', '6.0+local', ('f',))],
                                      directas=[]), dependencias=())
        bom = self.bom()
        corregidas = {c['name']: self.prop(c, 'factory:corregida') for c in bom['components']}
        self.assertEqual(corregidas, {'a1': 'lightwell', 'a2': 'lightwell', 'a3': 'lightwell', 'a4': None, 'a5': None, 'a6': None})
        self.assertEqual(self.componente(bom, 'a1')['version'], '1.0.rhlw-00001')  # la versión queda tal cual
        self.assertIn('corregido por Lightwell: a1 1.0.rhlw-00001', self.correr())

    def test_pr1_el_nombre_se_normaliza_en_el_enlace(self):
        self.proyecto(lock_texto=lock(paquetes=[('Foo_Bar.Baz', '1.0+x y', ('a',))], directas=[]), dependencias=())
        c = self.bom()['components'][0]
        self.assertEqual((c['name'], c['purl']), ('Foo_Bar.Baz', 'pkg:pypi/foo-bar-baz@1.0%2Bx%20y'))

    def test_pr1_dos_corridas_iguales_dan_el_mismo_inventario_sin_marcas_de_tiempo(self):
        self.proyecto(instalado={'alfa': '1.2.3', 'beta': '2.0.1'})
        a, b = self.correr(json=True), self.correr(json=True)
        self.assertEqual(a, b)
        self.assertTrue(a.endswith('}\n'))
        for prohibido in ('timestamp', 'serialNumber', '"tools"'):
            self.assertNotIn(prohibido, a)
        self.assertEqual(list(json.loads(a)), sorted(json.loads(a)))  # claves ordenadas

    def test_pr1_el_entorno_no_consultado_se_declara(self):
        self.proyecto()
        propiedades = {p['name']: p['value'] for p in self.bom()['metadata']['properties']}
        self.assertEqual((propiedades['factory:entorno'], propiedades['factory:confiable']), ('no consultado', 'true'))

    def test_pr1_un_lock_ilegible_es_un_error_claro(self):
        self.proyecto(lock_texto='esto no es [toml')
        with self.assertRaisesRegex(f.FactoryError, 'uv.lock no se puede leer'):
            self.correr()

    def test_pr1_un_lock_enlazado_no_se_lee(self):
        self.proyecto(con_lock=False)
        fuera = Path(self.tmp.name) / 'afuera.lock'
        fuera.write_text(lock())
        (self.root / 'uv.lock').symlink_to(fuera)
        bom = self.bom()
        self.assertEqual(bom['components'], [])  # como si no hubiera lock
        self.assertTrue(any('no hay uv.lock' in p['value'] for p in bom['metadata']['properties']))

    def test_pr1_la_raiz_virtual_de_un_lock_no_es_un_componente(self):
        virtual = lock().replace('source = { editable = "." }', 'source = { virtual = "." }')
        self.proyecto(lock_texto=virtual)
        self.assertEqual([c['name'] for c in self.bom()['components']], ['alfa', 'beta'])

    def test_pr1_los_hashes_salen_ordenados_aunque_el_lock_los_traiga_desordenados(self):
        self.proyecto(lock_texto=lock(paquetes=[('alfa', '1.2.3', ('b', 'a', 'c'))], directas=[('alfa', '==1.2.3')]), dependencias=('alfa==1.2.3',))
        self.assertEqual([h['content'] for h in self.bom()['components'][0]['hashes']], [H['a'], H['b'], H['c']])

    def test_pr1_un_paquete_en_dos_versiones_del_lock_aparece_dos_veces(self):
        self.proyecto(lock_texto=lock(paquetes=[('alfa', '1.2.3', ('a',)), ('alfa', '1.0.0', ('b',)), ('beta', '2.0.1', ('c',))]),
                      instalado={'alfa': '1.2.3', 'beta': '2.0.1'})
        bom = self.bom()
        self.assertEqual([(c['name'], c['version']) for c in bom['components']], [('alfa', '1.0.0'), ('alfa', '1.2.3'), ('beta', '2.0.1')])
        self.assertEqual(self.diferencias(bom), [])  # la instalada es una de las dos fijadas

    def test_pr1_si_la_instalada_no_es_ninguna_de_las_del_lock_se_dice(self):
        self.proyecto(lock_texto=lock(paquetes=[('alfa', '1.2.3', ('a',)), ('alfa', '1.0.0', ('b',)), ('beta', '2.0.1', ('c',))]),
                      instalado={'alfa': '1.5.0', 'beta': '2.0.1'})
        self.assertEqual(self.diferencias(self.bom()), ['alfa: el lock fija 1.2.3, 1.0.0 y está instalada la 1.5.0'])

    def test_pr1_un_entorno_que_falla_no_se_toma_por_vacio(self):
        self.proyecto()
        (self.root / 'entorno').mkdir()
        self.python = self.root / 'entorno/python'
        self.python.write_text('#!/bin/sh\nexit 3\n')
        self.python.chmod(self.python.stat().st_mode | stat.S_IXUSR)
        bom = self.bom()
        propiedades = {p['name']: p['value'] for p in bom['metadata']['properties'] if p['name'] != 'factory:diferencia'}
        self.assertEqual((propiedades['factory:entorno'], propiedades['factory:confiable']), ('no consultado', 'true'))
        self.assertFalse(any('no está instalado' in d for d in self.diferencias(bom)))

    def test_pr1_un_entorno_que_responde_cualquier_cosa_no_se_toma_por_valido(self):
        self.proyecto()
        for salida in ('no es json', '[1, 2]', '"texto"'):
            (self.root / 'entorno').mkdir(exist_ok=True)
            self.python = self.root / 'entorno/python'
            self.python.write_text(f"#!/bin/sh\ncat <<'FIN'\n{salida}\nFIN\n")
            self.python.chmod(self.python.stat().st_mode | stat.S_IXUSR)
            propiedades = {p['name']: p['value'] for p in self.bom()['metadata']['properties'] if p['name'] != 'factory:diferencia'}
            self.assertEqual(propiedades['factory:entorno'], 'no consultado', salida)

    def test_pr1_un_python_que_no_existe_no_rompe(self):
        self.proyecto()
        self.python = self.root / 'no-existe/python'
        self.assertEqual(len(self.bom()['components']), 2)

    def test_pr1_sin_indicar_python_se_usa_el_venv_del_proyecto(self):
        self.proyecto(instalado={'alfa': '1.2.3', 'beta': '2.0.1'})
        (self.root / '.venv/bin').mkdir(parents=True)
        (self.root / '.venv/bin/python').write_text((self.root / 'entorno/python').read_text())
        (self.root / '.venv/bin/python').chmod(0o755)
        self.python = None  # sin --python
        propiedades = {p['name']: p['value'] for p in self.bom()['metadata']['properties'] if p['name'] != 'factory:diferencia'}
        self.assertEqual(propiedades['factory:entorno'], 'consultado')

    # --- pr2: un lock desactualizado se declara no confiable ----------------------------------------------------------
    def confiable(self, bom):
        return {p['name']: p['value'] for p in bom['metadata']['properties'] if p['name'] != 'factory:diferencia'}['factory:confiable']

    def diferencias(self, bom):
        return [p['value'] for p in bom['metadata']['properties'] if p['name'] == 'factory:diferencia']

    def test_pr2_todo_coincide_es_confiable_y_sin_diferencias(self):
        self.proyecto(instalado={'alfa': '1.2.3', 'beta': '2.0.1'})
        bom = self.bom()
        self.assertEqual((self.confiable(bom), self.diferencias(bom)), ('true', []))
        self.assertIn('Confiable: sí.', self.correr())

    def test_pr2_el_lock_difiere_de_lo_que_exige_el_proyecto(self):
        self.proyecto(dependencias=('alfa==1.2.9', 'beta>=2'), instalado={'alfa': '1.2.3', 'beta': '2.0.1'})
        bom = self.bom()
        self.assertEqual(self.confiable(bom), 'false')
        self.assertEqual(self.diferencias(bom), ['alfa: pyproject.toml exige ==1.2.9 y el lock fija 1.2.3'])
        self.assertIn('  - alfa: pyproject.toml exige ==1.2.9 y el lock fija 1.2.3', self.correr())

    def test_pr2_el_lock_difiere_de_lo_instalado(self):
        self.proyecto(instalado={'alfa': '1.2.4', 'beta': '2.0.1'})
        bom = self.bom()
        self.assertEqual((self.confiable(bom), self.diferencias(bom)), ('false', ['alfa: el lock fija 1.2.3 y está instalada la 1.2.4']))

    def test_pr2_algo_del_lock_que_el_entorno_no_instala_se_marca_y_no_es_una_diferencia(self):
        self.proyecto(instalado={'alfa': '1.2.3'})
        bom = self.bom()
        self.assertEqual((self.confiable(bom), self.diferencias(bom)), ('true', []))
        self.assertEqual((self.prop(self.componente(bom, 'alfa'), 'factory:instalado'), self.prop(self.componente(bom, 'beta'), 'factory:instalado')),
                         ('true', 'false'))

    def test_pr2_una_dependencia_directa_que_falta_en_el_lock(self):
        self.proyecto(dependencias=('alfa==1.2.3', 'beta>=2', 'gama==3.0'), instalado={'alfa': '1.2.3', 'beta': '2.0.1'})
        self.assertEqual(self.diferencias(self.bom()), ['gama: lo exige pyproject.toml (==3.0) y no está en el lock'])

    def test_pr2_un_lock_de_otra_version_del_proyecto(self):
        self.proyecto(lock_texto=lock(proyecto='0.1.0a3'), version='0.1.0a15', instalado={'alfa': '1.2.3', 'beta': '2.0.1'})
        self.assertEqual(self.diferencias(self.bom()), ['el lock es de la versión 0.1.0a3 del proyecto y pyproject.toml dice 0.1.0a15'])

    def test_pr2_una_especificacion_no_fijada_no_es_una_diferencia(self):
        self.proyecto(dependencias=('alfa>=1', 'beta'), instalado={'alfa': '1.2.3', 'beta': '2.0.1'})
        bom = self.bom()
        self.assertEqual((self.confiable(bom), self.diferencias(bom)), ('true', []))
        self.assertEqual(self.prop(self.componente(bom, 'alfa'), 'factory:exigida'), '>=1')

    def test_pr2_sin_pyproject_no_se_puede_declarar_confiable(self):
        self.proyecto(instalado={'alfa': '1.2.3', 'beta': '2.0.1'})
        (self.root / 'pyproject.toml').unlink()
        bom = self.bom()
        self.assertEqual(self.confiable(bom), 'false')
        self.assertEqual(self.diferencias(bom), ['no hay pyproject.toml: no se puede comprobar que el lock coincida con lo que pide el proyecto'])

    def test_pr2_un_pyproject_enlazado_no_se_sigue_y_se_dice(self):
        self.proyecto(instalado={'alfa': '1.2.3', 'beta': '2.0.1'})
        real = Path(self.tmp.name) / 'pyproject-de-afuera.toml'
        real.write_text('[project]\nname = "demo"\nversion = "1.0.0"\ndependencies = ["alfa==9.9"]\n')
        (self.root / 'pyproject.toml').unlink()
        (self.root / 'pyproject.toml').symlink_to(real)
        bom = self.bom()
        self.assertEqual(self.confiable(bom), 'false')
        self.assertEqual(self.diferencias(bom), ['pyproject.toml es un enlace simbólico y no se sigue: no se puede comprobar que el lock coincida con lo que pide el proyecto'])
        self.assertNotIn('9.9', texto := json.dumps(bom))  # lo que dice el archivo de afuera no se lee

    def test_pr2_un_pyproject_malformado_es_un_error_claro_y_no_un_traceback(self):
        self.proyecto(instalado={'alfa': '1.2.3', 'beta': '2.0.1'})
        casos = {'project es un texto': 'project = "demo"\n', 'project es una lista': 'project = [1]\n',
                 'dependencies es un texto': '[project]\nname = "demo"\nversion = "1.0.0"\ndependencies = "alfa"\n',
                 'dependencies es una tabla': '[project]\nname = "demo"\nversion = "1.0.0"\n[project.dependencies]\nalfa = "1"\n'}
        for nombre, contenido in casos.items():
            with self.subTest(nombre):
                (self.root / 'pyproject.toml').write_text(contenido)
                with self.assertRaisesRegex(f.FactoryError, 'pyproject.toml: «(project|dependencies)» tiene que ser una'):
                    self.correr()

    def test_pr2_un_pyproject_con_dependencias_raras_las_saltea_sin_romper(self):
        self.proyecto(instalado={'alfa': '1.2.3', 'beta': '2.0.1'})
        (self.root / 'pyproject.toml').write_text('[project]\nname = 3\nversion = ["x"]\ndependencies = [1, "alfa==1.2.3", "beta>=2", "???"]\n')
        bom = self.bom()
        self.assertEqual(bom['metadata']['component'], {'type': 'application', 'name': '', 'version': ''})
        self.assertEqual([self.prop(c, 'factory:directa') for c in bom['components']], ['true', 'true'])
        self.assertEqual(self.diferencias(bom), [])  # el 1 y el ??? no se tomaron por dependencias

    def test_pr1_un_lock_con_entradas_malformadas_las_saltea_sin_romper(self):
        malo = lock() + """
[[package]]
name = "gama"
version = "1.0"
source = "pypi"
metadata = "no es una tabla"

[[package]]
name = 3
version = "1"

[[package]]
version = "9"
"""
        self.proyecto(lock_texto=malo)
        bom = self.bom()
        gama = self.componente(bom, 'gama')
        self.assertEqual((gama['version'], self.prop(gama, 'factory:origen')), ('1.0', 'desconocido'))
        self.assertEqual([c['name'] for c in bom['components']], ['alfa', 'beta', 'gama'])

    def test_pr1_un_lock_donde_package_no_es_una_lista_o_trae_cosas_raras_no_rompe(self):
        for contenido in ('package = "no es una lista"', 'package = 3', 'package = { name = "a" }'):
            with self.subTest(contenido):
                self.proyecto(lock_texto=f'version = 1\n{contenido}\n')
                self.assertEqual(self.bom()['components'], [])
        self.proyecto(lock_texto='version = 1\npackage = [1, "x", { name = "a", version = "1.0", source = { registry = "https://pypi.org/simple" } }]\n')
        self.assertEqual([c['name'] for c in self.bom()['components']], ['a'])  # lo raro se saltea y la entrada válida se lee

    def test_pr1_un_lock_con_la_raiz_y_su_metadata_malformada_no_rompe(self):
        raiz_mala = lock().replace('[package.metadata]\nrequires-dist = [', 'xx = [').replace(
            'source = { editable = "." }', 'source = { editable = "." }\nmetadata = "no es una tabla"')
        self.proyecto(lock_texto=raiz_mala)
        self.assertEqual([c['name'] for c in self.bom()['components']], ['alfa', 'beta'])

    def test_pr2_los_extras_y_marcadores_de_una_dependencia_no_confunden(self):
        self.proyecto(dependencias=("alfa[extra]==1.2.3 ; python_version >= '3.11'", 'beta>=2'), instalado={'alfa': '1.2.3', 'beta': '2.0.1'})
        self.assertEqual(self.diferencias(self.bom()), [])

    def test_pr2_el_nombre_se_compara_normalizado(self):
        self.proyecto(lock_texto=lock(paquetes=[('foo-bar', '1.0', ('a',))], directas=[('foo-bar', '==1.0')]), dependencias=('Foo_Bar==1.0',),
                      instalado={'Foo.Bar': '1.0'})
        self.assertEqual(self.diferencias(self.bom()), [])

    # --- pr3: el inventario queda en el candidato ---------------------------------------------------------------------------------
    def cambio(self):
        f.AGENTE = 'claude-code'
        try:
            ident = f.nuevo('Algo', 'algo')
        finally:
            f.AGENTE = None
        self.proyecto(instalado={'alfa': '1.2.3', 'beta': '2.0.1'})
        self.git('add', '.')
        self.git('commit', '-qm', 'base')
        return ident

    def test_pr3_con_un_cambio_el_inventario_queda_en_su_candidato_y_en_el_registro(self):
        ident = self.cambio()
        sha = self.git('rev-parse', 'HEAD')[:7]
        salida = self.correr(id=ident)
        destino = self.root / '.factory/cambios' / ident / 'candidatos' / sha / 'procedencia/cyclonedx.json'
        self.assertTrue(destino.is_file())
        cuerpo = destino.read_text()
        self.assertEqual(json.loads(cuerpo)['components'][0]['name'], 'alfa')
        evento = f.leer(ident)[1]['eventos'][-1]
        self.assertEqual((evento['accion'], evento['candidato'], evento['componentes'], evento['confiable']), ('procedencia_registrada', sha, 2, True))
        self.assertEqual(evento['huella'], f.sha256(cuerpo.encode()))
        self.assertEqual(evento['archivo'], destino.relative_to(self.root).as_posix())
        self.assertIn(f'Guardado en {destino.relative_to(self.root)}', salida)

    def test_pr3_un_candidato_nuevo_no_pisa_el_inventario_del_anterior(self):
        ident = self.cambio()
        primero = self.git('rev-parse', 'HEAD')[:7]
        self.correr(id=ident)
        viejo = (self.root / '.factory/cambios' / ident / 'candidatos' / primero / 'procedencia/cyclonedx.json').read_text()
        self.proyecto(lock_texto=lock(paquetes=[('alfa', '1.2.4', ('a',)), ('beta', '2.0.1', ('c',))], directas=[('alfa', '==1.2.4'), ('beta', '>=2')]),
                      dependencias=('alfa==1.2.4', 'beta>=2'), instalado={'alfa': '1.2.4', 'beta': '2.0.1'})
        (self.root / 'producto.py').write_text('x = 1\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'producto nuevo')
        segundo = self.git('rev-parse', 'HEAD')[:7]
        self.assertNotEqual(primero, segundo)
        self.correr(id=ident)
        base = self.root / '.factory/cambios' / ident / 'candidatos'
        self.assertEqual((base / primero / 'procedencia/cyclonedx.json').read_text(), viejo)
        self.assertIn('"1.2.4"', (base / segundo / 'procedencia/cyclonedx.json').read_text())
        self.assertEqual(len([e for e in f.leer(ident)[1]['eventos'] if e['accion'] == 'procedencia_registrada']), 2)

    def test_pr3_el_mismo_candidato_se_regraba_con_el_mismo_contenido(self):
        ident = self.cambio()
        sha = self.git('rev-parse', 'HEAD')[:7]
        self.correr(id=ident)
        archivo = self.root / '.factory/cambios' / ident / 'candidatos' / sha / 'procedencia/cyclonedx.json'
        antes = archivo.read_text()
        self.correr(id=ident)
        self.assertEqual(archivo.read_text(), antes)

    def test_pr3_con_json_imprime_exactamente_lo_que_guarda(self):
        ident = self.cambio()
        sha = self.git('rev-parse', 'HEAD')[:7]
        impreso = self.correr(id=ident, json=True)
        self.assertEqual(impreso, (self.root / '.factory/cambios' / ident / 'candidatos' / sha / 'procedencia/cyclonedx.json').read_text())

    def test_pr3_sin_un_cambio_no_se_guarda_nada(self):
        self.cambio()
        antes = sorted(p.as_posix() for p in (self.root / '.factory').rglob('*'))
        self.correr()
        self.assertEqual(sorted(p.as_posix() for p in (self.root / '.factory').rglob('*')), antes)

    def test_pr3_un_cambio_inexistente_o_cerrado_se_rechaza_sin_escribir(self):
        self.cambio()
        antes = sorted(p.as_posix() for p in (self.root / '.factory').rglob('*'))
        with self.assertRaises(f.FactoryError):
            self.correr(id='20260101-000000-no-existe')
        self.assertEqual(sorted(p.as_posix() for p in (self.root / '.factory').rglob('*')), antes)

    def test_pr3_un_commit_que_no_cambia_el_producto_no_abre_otro_candidato(self):
        ident = self.cambio()
        primero = self.git('rev-parse', 'HEAD')[:7]
        self.correr(id=ident)
        (self.root / 'tareas').mkdir(exist_ok=True)
        (self.root / 'tareas/nota.md').write_text('un registro\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'solo un registro')
        self.assertNotEqual(self.git('rev-parse', 'HEAD')[:7], primero)
        self.correr(id=ident)
        self.assertEqual(sorted(p.name for p in (self.root / '.factory/cambios' / ident / 'candidatos').iterdir()), [primero])

    def test_pr3_un_cambio_cerrado_se_rechaza_sin_escribir(self):
        ident = self.cambio()
        carpeta, estado = f.leer(ident)
        estado['fase'] = 'cerrada'
        f.guardar(carpeta, estado)
        antes = sorted(p.as_posix() for p in (self.root / '.factory').rglob('*'))
        with self.assertRaisesRegex(f.FactoryError, 'ya está cerrado'):
            self.correr(id=ident)
        self.assertEqual(sorted(p.as_posix() for p in (self.root / '.factory').rglob('*')), antes)

    def test_pr3_una_carpeta_enlazada_no_deja_escribir_afuera(self):
        ident = self.cambio()
        sha = self.git('rev-parse', 'HEAD')[:7]
        afuera = Path(self.tmp.name) / 'afuera'
        afuera.mkdir()
        carpeta = self.root / '.factory/cambios' / ident / 'candidatos' / sha
        carpeta.mkdir(parents=True)
        (carpeta / 'procedencia').symlink_to(afuera)
        with self.assertRaisesRegex(f.FactoryError, 'enlaces simbólicos'):
            self.correr(id=ident)
        self.assertEqual(list(afuera.iterdir()), [])

    def test_pr3_una_carpeta_enlazada_a_ninguna_parte_da_un_error_claro(self):
        ident = self.cambio()
        sha = self.git('rev-parse', 'HEAD')[:7]
        carpeta = self.root / '.factory/cambios' / ident / 'candidatos' / sha
        carpeta.mkdir(parents=True)
        (carpeta / 'procedencia').symlink_to(Path(self.tmp.name) / 'no-existe')
        with self.assertRaisesRegex(f.FactoryError, 'enlaces simbólicos'):
            self.correr(id=ident)

    # --- ayudantes de pr4 y pr5 ----------------------------------------------------------------------------------------------------
    def inventario(self, cambio, candidato, componentes):
        """Un inventario ya guardado en el candidato de un cambio (sin crear el cambio)."""
        bom = {'bomFormat': 'CycloneDX', 'specVersion': '1.5', 'version': 1,
               'components': [{'type': 'library', 'name': n, 'version': v, 'properties': []} for n, v in componentes]}
        destino = self.root / '.factory/cambios' / cambio / 'candidatos' / candidato / 'procedencia/cyclonedx.json'
        destino.parent.mkdir(parents=True)
        destino.write_text(json.dumps(bom))

    def dos_candidatos(self):
        self.inventario('20260101-000000-uno', 'aaaaaaa', [('alfa', '1.2.3'), ('beta', '2.0.1')])
        self.inventario('20260102-000000-dos', 'bbbbbbb', [('alfa', '1.2.4'), ('beta', '2.0.1')])

    # --- pr4: quién usó una dependencia ---------------------------------------------------------------------------------------
    def test_pr4_un_paquete_y_una_version_lista_solo_a_quien_la_uso(self):
        self.dos_candidatos()
        salida = self.correr(buscar='alfa==1.2.3')
        self.assertIn('alfa==1.2.3 figura en 1 inventario(s):', salida)
        self.assertIn('20260101-000000-uno · candidato aaaaaaa · alfa 1.2.3', salida)
        self.assertNotIn('bbbbbbb', salida)

    def test_pr4_sin_version_lista_a_todos_los_que_lo_usaron(self):
        self.dos_candidatos()
        salida = self.correr(buscar='beta')
        self.assertIn('beta figura en 2 inventario(s):', salida)
        self.assertLess(salida.index('aaaaaaa'), salida.index('bbbbbbb'))

    def test_pr4_un_paquete_que_nadie_uso_lo_dice(self):
        self.dos_candidatos()
        self.assertIn('Ningún candidato con inventario guardado usó gama.', self.correr(buscar='gama'))
        self.assertIn('Ningún candidato con inventario guardado usó alfa==9.9.', self.correr(buscar='alfa==9.9'))

    def test_pr4_una_version_es_exacta_y_no_un_prefijo(self):
        self.dos_candidatos()
        self.assertIn('Ningún candidato', self.correr(buscar='alfa==1.2'))
        self.assertIn('Ningún candidato', self.correr(buscar='alfa==1.2.'))
        self.assertIn('figura en 1 inventario(s)', self.correr(buscar='alfa==1.2.4'))

    def test_pr4_el_nombre_se_busca_normalizado(self):
        self.inventario('20260101-000000-uno', 'aaaaaaa', [('Foo_Bar', '1.0')])
        self.assertIn('figura en 1 inventario(s)', self.correr(buscar='foo-bar'))
        self.assertIn('figura en 1 inventario(s)', self.correr(buscar='FOO.BAR==1.0'))

    def test_pr4_la_busqueda_en_json_y_sin_inventarios(self):
        self.dos_candidatos()
        self.assertEqual(json.loads(self.correr(buscar='alfa', json=True)),
                         [{'cambio': '20260101-000000-uno', 'candidato': 'aaaaaaa', 'paquete': 'alfa', 'version': '1.2.3'},
                          {'cambio': '20260102-000000-dos', 'candidato': 'bbbbbbb', 'paquete': 'alfa', 'version': '1.2.4'}])
        self.assertEqual(json.loads(self.correr(buscar='gama', json=True)), [])

    def test_pr4_sin_inventarios_guardados_no_inventa_nada(self):
        self.assertIn('Ningún candidato', self.correr(buscar='alfa'))

    def test_pr4_un_pedido_vacio_y_las_combinaciones_invalidas_se_rechazan(self):
        for kw, texto in (({'buscar': '  ==1.0'}, 'indicá un paquete'), ({'buscar': 'a', 'auditar': True, 'avisos': 'x'}, 'no se combinan'),
                          ({'buscar': 'a', 'id': 'x'}, 'no llevan un cambio'), ({'auditar': True}, 'necesita --avisos'),
                          ({'avisos': 'x'}, 'es para --auditar')):
            with self.subTest(kw):
                with self.assertRaisesRegex(f.FactoryError, texto):
                    self.correr(**kw)

    def test_pr4_un_inventario_ilegible_se_avisa_y_no_traba_la_busqueda(self):
        self.dos_candidatos()
        malo = self.root / '.factory/cambios/20260103-000000-tres/candidatos/ccccccc/procedencia/cyclonedx.json'
        malo.parent.mkdir(parents=True)
        malo.write_text('{no es json')
        self.assertIn('beta figura en 2 inventario(s)', self.correr(buscar='beta'))

    def test_pr4_un_inventario_enlazado_no_se_lee(self):
        self.dos_candidatos()
        fuera = Path(self.tmp.name) / 'fuera.json'
        fuera.write_text(json.dumps({'components': [{'name': 'beta', 'version': '2.0.1'}]}))
        enlace = self.root / '.factory/cambios/20260103-000000-tres/candidatos/ccccccc/procedencia/cyclonedx.json'
        enlace.parent.mkdir(parents=True)
        enlace.symlink_to(fuera)
        self.assertIn('beta figura en 2 inventario(s)', self.correr(buscar='beta'))

    def test_pr4_una_carpeta_de_cambios_enlazada_no_se_lee(self):
        fuera = Path(self.tmp.name) / 'cambios-de-afuera'
        destino = fuera / '20260101-000000-uno/candidatos/aaaaaaa/procedencia'
        destino.mkdir(parents=True)
        (destino / 'cyclonedx.json').write_text(json.dumps({'components': [{'name': 'alfa', 'version': '1.0'}]}))
        (self.root / '.factory').mkdir(exist_ok=True)
        cambios = self.root / '.factory/cambios'
        if cambios.exists() and not cambios.is_symlink():
            import shutil
            shutil.rmtree(cambios)
        cambios.symlink_to(fuera)
        self.assertIn('Ningún candidato', self.correr(buscar='alfa'))

    # --- pr5: auditar contra avisos OSV, sin red --------------------------------------------------------------------------------
    def avisos(self, contenido, nombre='avisos.json'):
        ruta = self.root / nombre
        ruta.write_text(contenido if isinstance(contenido, str) else json.dumps(contenido))
        return str(ruta)

    def aviso(self, ident='OSV-1', nombre='alfa', eco='PyPI', **afectado):
        return {'id': ident, 'summary': f'Falla en {nombre}', 'affected': [{'package': {'name': nombre, 'ecosystem': eco}, **afectado}]}

    def rango(self, *eventos, tipo='ECOSYSTEM'):
        return {'ranges': [{'type': tipo, 'events': list(eventos)}]}

    def test_pr5_un_aviso_por_version_exacta_afecta_al_candidato_que_la_uso(self):
        self.dos_candidatos()
        salida = self.correr(auditar=True, avisos=self.avisos(self.aviso(versions=['1.2.3'], **self.rango({'introduced': '0'}, {'fixed': '1.2.4'}))))
        self.assertIn('Auditoría local: 1 aviso(s) contra 2 inventario(s) guardado(s); sin red.', salida)
        self.assertIn('Afectados:', salida)
        self.assertIn('OSV-1: alfa 1.2.3 (corregida en: 1.2.4) · 20260101-000000-uno · candidato aaaaaaa', salida)
        self.assertNotIn('bbbbbbb', salida)

    def test_pr5_un_rango_afecta_antes_de_la_correccion_y_no_desde_ella(self):
        self.inventario('20260101-000000-uno', 'aaaaaaa', [('alfa', v) for v in ('0.9', '1.2.3', '1.2.4', '1.3')])
        r = self.rango({'introduced': '1.0'}, {'fixed': '1.2.4'})
        resultado = json.loads(self.correr(auditar=True, json=True, avisos=self.avisos(self.aviso(**r))))
        self.assertEqual([f['version'] for f in resultado['afectados']], ['1.2.3'])

    def test_pr5_un_aviso_sin_version_corregida_lo_dice(self):
        self.inventario('20260101-000000-uno', 'aaaaaaa', [('alfa', '1.2.3')])
        salida = self.correr(auditar=True, avisos=self.avisos(self.aviso(versions=['1.2.3'])))
        self.assertIn('(corregida en: sin versión corregida declarada)', salida)

    def test_pr5_los_rangos_semver_valen_y_los_git_se_ignoran(self):
        self.inventario('20260101-000000-uno', 'aaaaaaa', [('alfa', '1.2.3'), ('alfa', '1.2.5')])
        semver = self.aviso('OSV-S', **self.rango({'introduced': '1.0.0'}, {'fixed': '1.2.4'}, tipo='SEMVER'))
        git = self.aviso('OSV-G', **self.rango({'introduced': '0'}, tipo='GIT'))
        resultado = json.loads(self.correr(auditar=True, json=True, avisos=self.avisos([semver, git])))
        self.assertEqual([(x['aviso'], x['version']) for x in resultado['afectados']], [('OSV-S', '1.2.3')])

    def test_pr5_last_affected_y_varios_tramos(self):
        self.inventario('20260101-000000-uno', 'aaaaaaa', [('alfa', v) for v in ('1.0', '1.5', '1.6', '2.1', '2.6', '3.0')])
        aviso = self.aviso(**self.rango({'introduced': '1.0'}, {'last_affected': '1.5'}, {'introduced': '2.0'}, {'fixed': '2.5'}))
        resultado = json.loads(self.correr(auditar=True, json=True, avisos=self.avisos(aviso)))
        self.assertEqual([f['version'] for f in resultado['afectados']], ['1.0', '1.5', '2.1'])

    def test_pr5_un_evento_introduced_cero_cubre_desde_el_principio(self):
        self.inventario('20260101-000000-uno', 'aaaaaaa', [('alfa', v) for v in ('0.0.1', '1.9', '2.0')])
        aviso = self.aviso(**self.rango({'fixed': '2.0'}, {'introduced': '0'}))  # los eventos llegan desordenados
        resultado = json.loads(self.correr(auditar=True, json=True, avisos=self.avisos(aviso)))
        self.assertEqual([f['version'] for f in resultado['afectados']], ['0.0.1', '1.9'])

    def test_pr5_una_prerrelease_de_la_version_corregida_sigue_afectada(self):
        self.inventario('20260101-000000-uno', 'aaaaaaa', [('alfa', v) for v in ('1.2.4rc1', '1.2.4.dev1', '1.2.4', '1.2.4.post1')])
        aviso = self.aviso(**self.rango({'introduced': '1.0'}, {'fixed': '1.2.4'}))
        resultado = json.loads(self.correr(auditar=True, json=True, avisos=self.avisos(aviso)))
        self.assertEqual([f['version'] for f in resultado['afectados']], ['1.2.4.dev1', '1.2.4rc1'])

    def test_pr5_un_aviso_que_ningun_candidato_uso_no_afecta(self):
        self.dos_candidatos()
        salida = self.correr(auditar=True, avisos=self.avisos([self.aviso(versions=['9.9']), self.aviso('OSV-2', nombre='otro', versions=['1.0'])]))
        self.assertIn('Auditoría local: 2 aviso(s) contra 2 inventario(s)', salida)
        self.assertIn('No hay candidatos afectados.', salida)
        self.assertNotIn('Afectados:', salida)

    def test_pr5_otro_ecosistema_no_cuenta_y_el_nombre_se_compara_normalizado(self):
        self.inventario('20260101-000000-uno', 'aaaaaaa', [('Foo_Bar', '1.0')])
        npm = self.aviso('OSV-NPM', nombre='foo-bar', eco='npm', versions=['1.0'])
        pypi = self.aviso('OSV-PYPI', nombre='FOO.bar', eco='pypi', versions=['1.0'])
        resultado = json.loads(self.correr(auditar=True, json=True, avisos=self.avisos([npm, pypi])))
        self.assertEqual([f['aviso'] for f in resultado['afectados']], ['OSV-PYPI'])

    def test_pr5_los_tres_formatos_de_archivo_se_aceptan(self):
        self.dos_candidatos()
        uno = self.aviso(versions=['1.2.3'])
        for contenido in (uno, [uno], {'vulns': [uno]}):
            resultado = json.loads(self.correr(auditar=True, json=True, avisos=self.avisos(contenido)))
            self.assertEqual((resultado['avisos'], len(resultado['afectados'])), (1, 1))

    def test_pr5_una_version_corregida_por_lightwell_se_lista_aparte(self):
        self.inventario('20260101-000000-uno', 'aaaaaaa', [('alfa', '1.2.3.rhlw-00001')])
        self.inventario('20260102-000000-dos', 'bbbbbbb', [('alfa', '1.2.3')])
        aviso = self.aviso(**self.rango({'introduced': '1.0'}, {'fixed': '1.2.4'}))
        salida = self.correr(auditar=True, avisos=self.avisos(aviso))
        self.assertIn('Afectados pero corregidos por Lightwell (verificá el aviso):', salida)
        resultado = json.loads(self.correr(auditar=True, json=True, avisos=self.avisos(aviso)))
        self.assertEqual([f['candidato'] for f in resultado['afectados']], ['bbbbbbb'])
        self.assertEqual([f['candidato'] for f in resultado['corregidos']], ['aaaaaaa'])

    def test_pr5_una_version_que_no_se_puede_comparar_se_dice_y_no_se_da_por_limpia(self):
        self.inventario('20260101-000000-uno', 'aaaaaaa', [('alfa', 'dos-punto-cero')])
        aviso = self.aviso(**self.rango({'introduced': '1.0'}, {'fixed': '1.2.4'}))
        salida = self.correr(auditar=True, avisos=self.avisos(aviso))
        self.assertIn('No se pudo comparar la versión con los rangos del aviso:', salida)
        self.assertNotIn('No hay candidatos afectados.', salida)

    def test_pr5_la_salida_en_json_y_el_orden_son_estables(self):
        self.dos_candidatos()
        aviso = self.aviso(versions=['1.2.3', '1.2.4'])
        a = self.correr(auditar=True, json=True, avisos=self.avisos(aviso))
        self.assertEqual(a, self.correr(auditar=True, json=True, avisos=self.avisos(aviso)))
        self.assertEqual([x['candidato'] for x in json.loads(a)['afectados']], ['aaaaaaa', 'bbbbbbb'])

    def test_pr5_un_archivo_de_avisos_invalido_falla_diciendo_que_esta_mal(self):
        self.dos_candidatos()
        casos = {
            'no es json': ('{nada', 'no es JSON'),
            'vacío': ('[]', 'no tiene avisos OSV'),
            'un número': ('3', 'no tiene avisos OSV'),
            'sin id': ([{'affected': []}], 'no es OSV válido'),
            'sin affected': ([{'id': 'X'}], 'no es OSV válido'),
            'affected sin package': ([{'id': 'X', 'affected': [{}]}], 'sin «package»'),
            'package sin ecosistema': ([{'id': 'X', 'affected': [{'package': {'name': 'a'}}]}], 'sin «package»'),
            'versions no es lista': ([{'id': 'X', 'affected': [{'package': {'name': 'a', 'ecosystem': 'PyPI'}, 'versions': '1'}]}], 'no son listas'),
            'aviso que no es objeto': (['hola'], 'no es OSV válido'),
            'affected vacío': ([{'id': 'X', 'affected': []}], 'al menos un paquete'),
            'affected no es lista': ([{'id': 'X', 'affected': {'package': {'name': 'a', 'ecosystem': 'PyPI'}}}], 'no es OSV válido'),
            'ranges no es lista': ([{'id': 'X', 'affected': [{'package': {'name': 'a', 'ecosystem': 'PyPI'}, 'ranges': 1}]}], 'no son listas'),
            'ranges nulo': ([{'id': 'X', 'affected': [{'package': {'name': 'a', 'ecosystem': 'PyPI'}, 'ranges': None}]}], 'no son listas'),
            'versions nulo': ([{'id': 'X', 'affected': [{'package': {'name': 'a', 'ecosystem': 'PyPI'}, 'versions': None}]}], 'no son listas'),
            'un affected que no es objeto': ([{'id': 'X', 'affected': ['a']}], 'sin «package»'),
        }
        for nombre, (contenido, texto) in casos.items():
            with self.subTest(nombre):
                with self.assertRaisesRegex(f.FactoryError, texto):
                    self.correr(auditar=True, avisos=self.avisos(contenido))

    def test_pr5_un_rango_mal_armado_falla_y_no_se_lee_como_limpio(self):
        self.dos_candidatos()
        ok = {'name': 'alfa', 'ecosystem': 'PyPI'}
        rangos = {
            'sin events': [{'type': 'ECOSYSTEM'}],
            'events vacío': [{'type': 'ECOSYSTEM', 'events': []}],
            'events nulo': [{'type': 'ECOSYSTEM', 'events': None}],
            'events no es lista': [{'type': 'ECOSYSTEM', 'events': {'introduced': '0'}}],
            'sin type': [{'events': [{'introduced': '0'}]}],
            'type desconocido': [{'type': 'RARO', 'events': [{'introduced': '0'}]}],
            'rango que no es objeto': ['introduced'],
            'evento que no es objeto': [{'type': 'ECOSYSTEM', 'events': ['introduced']}],
            'evento con dos claves': [{'type': 'ECOSYSTEM', 'events': [{'introduced': '0', 'fixed': '1'}]}],
            'evento vacío': [{'type': 'ECOSYSTEM', 'events': [{}]}],
            'evento desconocido': [{'type': 'ECOSYSTEM', 'events': [{'empezo': '0'}]}],
            'valor que no es texto': [{'type': 'ECOSYSTEM', 'events': [{'introduced': 0}]}],
        }
        for nombre, rs in rangos.items():
            with self.subTest(nombre):
                with self.assertRaisesRegex(f.FactoryError, 'rango que no es OSV válido'):
                    self.correr(auditar=True, avisos=self.avisos([{'id': 'X', 'affected': [{'package': ok, 'ranges': rs}]}]))

    def test_pr5_un_rango_git_bien_formado_se_acepta_y_se_ignora(self):
        self.inventario('20260101-000000-uno', 'aaaaaaa', [('alfa', '1.0')])
        aviso = self.aviso(**self.rango({'introduced': '0'}, {'fixed': 'abc123'}, tipo='GIT'))
        salida = self.correr(auditar=True, avisos=self.avisos(aviso))
        self.assertIn('No se pudo comparar la versión con los rangos del aviso:', salida)  # sin rangos de versión aplicables: no se da por limpio

    def test_pr5_un_aviso_sin_versiones_ni_rangos_no_se_da_por_limpio(self):
        self.inventario('20260101-000000-uno', 'aaaaaaa', [('alfa', '1.0')])
        sin_nada = {'id': 'X', 'affected': [{'package': {'name': 'alfa', 'ecosystem': 'PyPI'}}]}
        resultado = json.loads(self.correr(auditar=True, json=True, avisos=self.avisos(sin_nada)))
        self.assertEqual((resultado['afectados'], len(resultado['sin_comparar'])), ([], 1))

    def test_pr5_introduced_cero_cubre_tambien_las_prerreleases_de_la_serie_cero(self):
        versiones = ('0.0.0.dev1', '0.0.0a1', '0a1', '0.0.1', '0.9', '1.0')
        self.inventario('20260101-000000-uno', 'aaaaaaa', [('alfa', v) for v in versiones])
        aviso = self.aviso(**self.rango({'introduced': '0'}, {'fixed': '1.0'}))
        resultado = json.loads(self.correr(auditar=True, json=True, avisos=self.avisos(aviso)))
        self.assertEqual(sorted(x['version'] for x in resultado['afectados']), sorted(['0.0.0.dev1', '0.0.0a1', '0a1', '0.0.1', '0.9']))

    def test_pr5_eventos_en_la_misma_version_se_aplican_en_su_orden_y_no_en_el_del_archivo(self):
        self.inventario('20260101-000000-uno', 'aaaaaaa', [('alfa', v) for v in ('0.9', '1.0', '1.1')])
        solo_la_1_0 = self.aviso(**self.rango({'last_affected': '1.0'}, {'introduced': '1.0'}))  # llegan al revés
        resultado = json.loads(self.correr(auditar=True, json=True, avisos=self.avisos(solo_la_1_0)))
        self.assertEqual([x['version'] for x in resultado['afectados']], ['1.0'])
        vacio = self.aviso(**self.rango({'fixed': '1.0'}, {'introduced': '1.0'}))  # introducida y corregida en la misma: no afecta a nadie
        self.assertEqual(json.loads(self.correr(auditar=True, json=True, avisos=self.avisos(vacio)))['afectados'], [])

    def test_pr5_un_evento_limit_no_afecta_la_evaluacion(self):
        self.inventario('20260101-000000-uno', 'aaaaaaa', [('alfa', v) for v in ('1.0', '2.0')])
        aviso = self.aviso(**self.rango({'introduced': '0'}, {'limit': '1.5'}, {'fixed': '3.0'}))
        resultado = json.loads(self.correr(auditar=True, json=True, avisos=self.avisos(aviso)))
        self.assertEqual([x['version'] for x in resultado['afectados']], ['1.0', '2.0'])

    def test_pr5_una_ruta_de_avisos_con_un_directorio_enlazado_se_rechaza(self):
        fuera = Path(self.tmp.name) / 'avisos-de-afuera'
        fuera.mkdir()
        (fuera / 'avisos.json').write_text(json.dumps([self.aviso(versions=['1.0'])]))
        (self.root / 'enlace').symlink_to(fuera)
        with self.assertRaisesRegex(f.FactoryError, 'enlaces simbólicos'):
            self.correr(auditar=True, avisos=str(self.root / 'enlace/avisos.json'))
        # un archivo de afuera del proyecto, sin enlaces, sí se acepta
        self.inventario('20260101-000000-uno', 'aaaaaaa', [('alfa', '1.0')])
        self.assertIn('Afectados:', self.correr(auditar=True, avisos=str(fuera / 'avisos.json')))

    def test_pr5_un_archivo_que_no_existe_o_enlazado_se_rechaza(self):
        with self.assertRaisesRegex(f.FactoryError, 'no encuentro el archivo de avisos'):
            self.correr(auditar=True, avisos=str(self.root / 'no-existe.json'))
        real = self.avisos([self.aviso(versions=['1'])], 'real.json')
        enlace = self.root / 'enlace.json'
        enlace.symlink_to(real)
        with self.assertRaisesRegex(f.FactoryError, 'no encuentro el archivo de avisos'):
            self.correr(auditar=True, avisos=str(enlace))

    def test_pr5_un_archivo_de_avisos_enlazado_fuera_del_proyecto_tambien_se_rechaza(self):
        fuera = Path(self.tmp.name) / 'otro-lugar'
        fuera.mkdir()
        (fuera / 'real.json').write_text(json.dumps([self.aviso(versions=['1.0'])]))
        (fuera / 'enlace.json').symlink_to(fuera / 'real.json')
        with self.assertRaisesRegex(f.FactoryError, 'no encuentro el archivo de avisos'):
            self.correr(auditar=True, avisos=str(fuera / 'enlace.json'))

    def test_pr5_la_auditoria_no_usa_la_red(self):
        import socket
        self.dos_candidatos()
        real = socket.socket
        socket.socket = lambda *a, **k: (_ for _ in ()).throw(AssertionError('la auditoría abrió un socket'))
        try:
            self.correr(auditar=True, avisos=self.avisos(self.aviso(versions=['1.2.3'])))
            self.correr(buscar='alfa')
            self.proyecto(instalado={'alfa': '1.2.3', 'beta': '2.0.1'})
            self.correr()
        finally:
            socket.socket = real

    # --- la comparación de versiones ----------------------------------------------------------------------------------------------
    def test_las_versiones_se_ordenan_al_estilo_pep_440(self):
        ordenadas = ['1.0.dev1', '1.0a1', '1.0a2', '1.0b1', '1.0rc1', '1.0', '1.0.post1', '1.1', '1.10', '2', '10']
        self.assertEqual(sorted(ordenadas, key=procedencia.clave), ordenadas)
        for menor, mayor in zip(ordenadas, ordenadas[1:]):  # estricto: cada una es menor que la siguiente, no sólo «no mayor»
            self.assertLess(procedencia.clave(menor), procedencia.clave(mayor), (menor, mayor))
        self.assertLess(procedencia.clave('1.0a9'), procedencia.clave('1.0b1'))
        self.assertLess(procedencia.clave('1.0b9'), procedencia.clave('1.0rc1'))
        self.assertEqual(procedencia.clave('1.0c1'), procedencia.clave('1.0rc1'))
        self.assertEqual(procedencia.clave('1.0'), procedencia.clave('1.0.0'))
        self.assertEqual(procedencia.clave('1.0+local'), procedencia.clave('1.0'))
        self.assertIsNone(procedencia.clave('no es una versión'))
        self.assertLess(procedencia.clave('0.1.0a14'), procedencia.clave('0.1.0a15'))
        self.assertLess(procedencia.clave('0.1.0a15'), procedencia.clave('0.1.0'))


if __name__ == '__main__':
    unittest.main()
