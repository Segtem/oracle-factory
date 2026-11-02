"""Un verificador reutilizable para la evidencia de cada cambio: escenarios vg1–vg3, con proyectos temporales de verdad."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE))
from tools import verificar_cambio as vc  # noqa: E402

HERRAMIENTA = SOURCE / 'tools/verificar_cambio.py'
ENTORNO = {**os.environ, 'GIT_AUTHOR_NAME': 'Persona fixture', 'GIT_AUTHOR_EMAIL': 'p@example.invalid',
           'GIT_COMMITTER_NAME': 'Persona fixture', 'GIT_COMMITTER_EMAIL': 'p@example.invalid'}
SPEC = ('# Capability: demo\n\n## ADDED Requirements\n\n### Requirement: el_primero\nTipo: funcional\nEl sistema DEBE a.\n\n'
        '#### Scenario: uno\n- DADO a\n- CUANDO b\n- ENTONCES c\n\n### Requirement: el_segundo\nTipo: funcional\nEl sistema DEBE b.\n\n'
        '#### Scenario: dos\n- DADO a\n- CUANDO b\n- ENTONCES c\n')
MODULO = '''import unittest


class Uno(unittest.TestCase):
    def test_dm1_a(self):
        self.assertTrue(True)

    def test_dm1_b(self):
        self.assertTrue(True)

    def test_dm2_c(self):
        self.assertTrue(True)


class Dos(unittest.TestCase):
    def test_dm2_d(self):
        self.assertTrue(True)

    def test_dm2_e(self):
        self.assertTrue(True)

    def test_sin_numero(self):
        self.assertTrue(True)
'''
CAMBIO = '20261102-000000-abc-demo'


class Contrato(unittest.TestCase):
    # --- vg1: cada caso va al requisito que su nombre indica -------------------------------------------------------------
    def test_vg1_cada_caso_va_al_requisito_que_su_numero_indica_con_su_clase(self):
        casos = vc.casos_del_modulo(MODULO)
        self.assertEqual(casos, {1: ['Uno.test_dm1_a', 'Uno.test_dm1_b'], 2: ['Dos.test_dm2_d', 'Dos.test_dm2_e', 'Uno.test_dm2_c']})
        requisitos = vc.requisitos_de_la_spec(SPEC)
        self.assertEqual(requisitos, ['el_primero', 'el_segundo'])
        self.assertEqual(vc.contrato(requisitos, casos), {'el_primero': ['Uno.test_dm1_a', 'Uno.test_dm1_b'],
                                                          'el_segundo': ['Dos.test_dm2_d', 'Dos.test_dm2_e', 'Uno.test_dm2_c']})

    def test_vg1_un_requisito_sin_casos_falla_y_lo_nombra(self):
        requisitos = ['el_primero', 'el_segundo', 'el_tercero']
        with self.assertRaises(vc.ContratoInvalido) as e:
            vc.contrato(requisitos, vc.casos_del_modulo(MODULO))
        self.assertIn('el_tercero', str(e.exception))
        self.assertNotIn('el_primero', str(e.exception))

    def test_vg1_un_caso_con_un_numero_sin_requisito_falla_y_lo_nombra(self):
        casos = vc.casos_del_modulo(MODULO + '\n\nclass Tres(unittest.TestCase):\n    def test_dm3_f(self):\n        pass\n')
        with self.assertRaises(vc.ContratoInvalido) as e:
            vc.contrato(['el_primero', 'el_segundo'], casos)
        self.assertIn('Tres.test_dm3_f', str(e.exception))
        with self.assertRaises(vc.ContratoInvalido):
            vc.contrato(['el_primero'], {0: ['Uno.test_dm0_x'], 1: ['Uno.test_dm1_a']})  # el requisito 0 no existe

    def test_vg1_un_modulo_sin_casos_falla(self):
        with self.assertRaises(vc.ContratoInvalido):
            vc.contrato(['el_primero'], vc.casos_del_modulo('import unittest\n\n\nclass A(unittest.TestCase):\n    def test_sin_numero(self):\n        pass\n'))
        with self.assertRaises(vc.ContratoInvalido):
            vc.contrato([], {})

    def test_vg1_un_nombre_dentro_de_una_cadena_o_de_una_funcion_anidada_no_es_un_caso(self):
        texto = ('import unittest\n\n\nclass A(unittest.TestCase):\n    def test_dm1_real(self):\n        x = "def test_dm9_falso(self):"\n'
                 '        def test_dm8_anidado():\n            pass\n\n\ndef test_dm7_suelta():\n    pass\n')
        self.assertEqual(vc.casos_del_modulo(texto), {1: ['A.test_dm1_real']})

    def test_vg1_una_clase_sin_base_o_solo_con_object_no_aporta_casos_porque_unittest_no_la_corre(self):
        texto = ('import unittest\n\n\nclass Suelta:\n    def test_dm1_fantasma(self):\n        pass\n\n\nclass Objeto(object):\n'
                 '    def test_dm1_otro(self):\n        pass\n\n\nclass Real(unittest.TestCase):\n    def test_dm1_ok(self):\n        pass\n\n\n'
                 'class Hija(Real):\n    def test_dm1_propio(self):\n        pass\n\n\nclass Ajena(otro.Base):\n    def test_dm1_ajeno(self):\n        pass\n')
        self.assertEqual(vc.casos_del_modulo(texto), {1: ['Ajena.test_dm1_ajeno', 'Hija.test_dm1_ok', 'Hija.test_dm1_propio', 'Real.test_dm1_ok']})  # Hija hereda el de Real

    def test_vg1_los_metodos_heredados_de_una_clase_o_un_mixin_del_modulo_cuentan_en_la_subclase(self):
        texto = ('import unittest\n\n\nclass Mixin:\n    def test_dm1_comun(self):\n        pass\n    def test_dm2_otro(self):\n        pass\n\n\n'
                 'class Uno(Mixin, unittest.TestCase):\n    def test_dm2_otro(self):\n        pass\n\n\nclass Dos(Uno):\n    pass\n\n\n'
                 'class Ciclo(Ciclo2):\n    pass\n\n\nclass Ciclo2(Ciclo):\n    pass\n')
        self.assertEqual(vc.casos_del_modulo(texto), {1: ['Dos.test_dm1_comun', 'Uno.test_dm1_comun'],
                                                      2: ['Dos.test_dm2_otro', 'Uno.test_dm2_otro']})  # el Mixin solo no cuenta; los ciclos no cuelgan
        con_base_importada = 'from x import Base\n\n\nclass A(Base):\n    def test_dm1_a(self):\n        pass\n'
        self.assertEqual(vc.casos_del_modulo(con_base_importada), {1: ['A.test_dm1_a']})  # una base que no está en el módulo no rompe

    def test_vg1_un_encabezado_dentro_de_un_bloque_de_codigo_no_es_un_requisito(self):
        spec = '### Requirement: uno\n\n```markdown\n### Requirement: ejemplo\n```\n\n~~~\n### Requirement: otro\n~~~\n### Requirement: dos\n'
        self.assertEqual(vc.requisitos_de_la_spec(spec), ['uno', 'dos'])

    def test_vg1_las_cercas_se_cierran_como_en_commonmark_mismo_caracter_y_no_mas_cortas(self):
        spec = ('### Requirement: uno\n````markdown\n```\n### Requirement: ejemplo\n```\n### Requirement: otro\n````\n### Requirement: dos\n'
                '~~~\n```\n### Requirement: tilde\n~~~\n### Requirement: tres\n')
        self.assertEqual(vc.requisitos_de_la_spec(spec), ['uno', 'dos', 'tres'])
        self.assertEqual(vc.requisitos_de_la_spec('``` con texto\n### Requirement: x\n``` no cierra\n### Requirement: y\n```\n### Requirement: z\n'), ['z'])
        self.assertEqual(vc.requisitos_de_la_spec('Una `` `cerca` `` en línea\n### Requirement: a\n'), ['a'])  # no abre un bloque
        self.assertEqual(vc.requisitos_de_la_spec('```a`b\n### Requirement: x\n'), ['x'])  # una cerca de backticks no lleva backticks en su texto
        self.assertEqual(vc.requisitos_de_la_spec('    ```\n### Requirement: y\n'), ['y'])  # con cuatro espacios es código indentado, no una cerca
        self.assertEqual(vc.requisitos_de_la_spec('   ```\n### Requirement: z\n```\n### Requirement: w\n'), ['w'])  # con tres sí

    def test_vg1_una_seccion_comun_despues_de_removed_vuelve_a_contar(self):
        spec = '## REMOVED Requirements\n### Requirement: viejo\n## Requirements\n### Requirement: vigente\n'
        self.assertEqual(vc.requisitos_de_la_spec(spec), ['vigente'])

    def test_vg1_la_cabecera_de_la_spec_tolera_los_espacios_que_tolera_factory(self):
        spec = '###  Requirement:   uno  \n###\tRequirement: dos\n##  ADDED   Requirements\n###  Requirement: tres\n'
        self.assertEqual(vc.requisitos_de_la_spec(spec), ['uno', 'dos', 'tres'])
        retirado = '##\tREMOVED\tRequirements\n### Requirement: viejo\n##  added  requirements\n### Requirement: nuevo\n'
        self.assertEqual(vc.requisitos_de_la_spec(retirado), ['nuevo'])

    def test_vg1_los_encabezados_de_la_spec_se_leen_en_orden_y_solo_los_de_nivel_tres(self):
        spec = '### Requirement: uno\n#### Scenario: no\n## Requirement: tampoco\n### Requirement:   dos  \n    ### Requirement: indentado\n'
        self.assertEqual(vc.requisitos_de_la_spec(spec), ['uno', 'dos'])

    def test_vg1_el_nombre_del_requisito_se_pasa_a_slug_como_lo_importa_factory(self):
        spec = '### Requirement: Comportamiento principal\n### Requirement: El año   pasa: ¡bien!\n'
        self.assertEqual(vc.requisitos_de_la_spec(spec), ['comportamiento_principal', 'el_ano_pasa_bien'])

    def test_vg1_una_seccion_removed_no_cuenta_porque_no_se_importa(self):
        spec = '## ADDED Requirements\n### Requirement: uno\n## REMOVED Requirements\n### Requirement: viejo\n## MODIFIED Requirements\n### Requirement: dos\n'
        self.assertEqual(vc.requisitos_de_la_spec(spec), ['uno', 'dos'])

    def test_vg1_un_requisito_repetido_falla_en_vez_de_perder_sus_casos(self):
        with self.assertRaises(vc.ContratoInvalido) as e:
            vc.contrato(['igual', 'otro', 'igual'], {1: ['A.test_dm1_x'], 2: ['A.test_dm2_x'], 3: ['A.test_dm3_x']})
        self.assertIn('igual', str(e.exception))
        self.assertNotIn('otro', str(e.exception))

    def test_vg1_un_requisito_que_declara_pruebas_no_aplica_sigue_necesitando_casos_y_el_limite_esta_documentado(self):
        spec = '### Requirement: uno\n### Requirement: dos\nPruebas: no aplica — motivo\n'
        with self.assertRaises(vc.ContratoInvalido) as e:
            vc.contrato(vc.requisitos_de_la_spec(spec), {1: ['A.test_dm1_x']})
        self.assertIn('dos', str(e.exception))
        documento = (SOURCE / 'docs/tests.md').read_text(encoding='utf-8')
        self.assertRegex(documento, r'(?s)verificar_cambio.*Pruebas: no aplica.*(a mano|no lo cubre|todavía)')

    def test_vg1_el_nombre_del_caso_exige_dos_o_tres_letras_minusculas_y_un_numero(self):
        for nombre, n in (('test_a1_x', None), ('test_ab1_x', 1), ('test_abc12_x', 12), ('test_abcd1_x', None), ('test_AB1_x', None),
                          ('test_ab_x', None), ('test_ab1', None)):
            with self.subTest(nombre=nombre):
                casos = vc.casos_del_modulo(f'import unittest\n\n\nclass A(unittest.TestCase):\n    def {nombre}(self):\n        pass\n')
                self.assertEqual(list(casos), [] if n is None else [n])


class ProyectoTemporal(unittest.TestCase):
    """Un proyecto de verdad (con Git, una spec, un registro y un módulo de pruebas) y la herramienta corrida como proceso."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.raiz = Path(self.tmp.name) / 'proyecto'
        self.escribir('tests/test_demo.py', MODULO)
        self.escribir('datos.txt', 'uno\n')
        self.escribir('.gitignore', '__pycache__/\n')  # como en un proyecto de verdad: la carpeta de evidencia sí cuenta si no se la excluye
        self.escribir(f'openspec/changes/{CAMBIO}/specs/demo/spec.md', SPEC)
        self.escribir(f'.factory/cambios/{CAMBIO}/factory.json',
                      json.dumps({'requisitos': ['demo_h.el_segundo', 'demo_h.el_primero']}))  # fuera de orden a propósito
        self.git('init', '-q', '-b', 'main')
        self.git('add', '-A')
        self.git('commit', '-qm', 'base')

    def escribir(self, ruta, texto):
        (self.raiz / ruta).parent.mkdir(parents=True, exist_ok=True)
        (self.raiz / ruta).write_text(texto, encoding='utf-8')

    def git(self, *args):
        return subprocess.run(['git', *args], cwd=self.raiz, env=ENTORNO, capture_output=True, text=True, check=True).stdout

    def correr(self, *args):
        return subprocess.run([sys.executable, str(HERRAMIENTA), CAMBIO, '--pruebas', 'test_demo', '--raiz', str(self.raiz), *args],
                              env=ENTORNO, capture_output=True, text=True, stdin=subprocess.DEVNULL)

    def evidencia(self):
        return self.raiz / 'evidencia'

    def resultado(self):
        return json.loads((self.evidencia() / 'resultado.json').read_text())


class Evidencia(ProyectoTemporal):
    # --- vg2: la evidencia completa del cambio -----------------------------------------------------------------------------
    def test_vg2_un_cambio_completo_produce_los_cuatro_archivos_y_declara_exito(self):
        r = self.correr('--salida', str(self.evidencia()))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        for nombre in ('suite.txt', 'hechos.json', 'trazabilidad.json', 'resultado.json'):
            self.assertTrue((self.evidencia() / nombre).is_file(), nombre)
        self.assertTrue(self.resultado()['exitoso'])
        hechos = json.loads((self.evidencia() / 'hechos.json').read_text())
        filas = {(h['requisito'], h['caso']): h['codigo'] for h in hechos['demo_caso']}
        self.assertEqual(set(filas.values()), {0})
        self.assertEqual({r for r, _ in filas}, {'el_primero', 'el_segundo'})
        self.assertEqual(len(filas), 5)
        self.assertEqual(hechos['demo_corrida'], [{'completa': 1, 'casos': 5}])
        traza = json.loads((self.evidencia() / 'trazabilidad.json').read_text())
        self.assertEqual(set(traza['requisitos']), {'demo_h.el_primero', 'demo_h.el_segundo'})  # con el id completo del registro
        self.assertIn('éxito: True', r.stdout)

    def test_vg2_un_caso_que_falla_deja_el_codigo_en_su_hecho_y_no_declara_exito(self):
        self.escribir('tests/test_demo.py', MODULO.replace("def test_dm2_c(self):\n        self.assertTrue(True)",
                                                           "def test_dm2_c(self):\n        self.fail('adrede')"))
        r = self.correr('--salida', str(self.evidencia()))
        self.assertEqual(r.returncode, 1)
        self.assertFalse(self.resultado()['exitoso'])
        hechos = json.loads((self.evidencia() / 'hechos.json').read_text())
        codigos = {h['caso']: h['codigo'] for h in hechos['demo_caso']}
        self.assertNotEqual(codigos['Uno.test_dm2_c'], 0)
        self.assertEqual(hechos['demo_corrida'][0]['completa'], 0)
        self.assertIn('éxito: False', r.stdout)

    def test_vg2_si_las_fuentes_cambian_durante_la_corrida_no_hay_exito(self):
        self.escribir('tests/test_demo.py', MODULO.replace("def test_dm1_a(self):\n        self.assertTrue(True)",
                      "def test_dm1_a(self):\n        (__import__('pathlib').Path(__file__).parents[1] / 'datos.txt').write_text('cambiado\\n')"))
        r = self.correr('--salida', str(self.evidencia()))
        self.assertEqual(r.returncode, 1)
        resultado = self.resultado()
        self.assertFalse(resultado['fuentes_estables'])
        self.assertFalse(resultado['exitoso'])

    def test_vg2_un_caso_del_contrato_que_la_suite_nunca_corre_queda_con_codigo_distinto_de_cero(self):
        self.escribir('tests/test_demo.py', MODULO + '\n\nclass Auxiliar:\n    pass\n\n\nclass NoCorre(Auxiliar):\n    def test_dm1_fantasma(self):\n        pass\n')  # tiene base, no es un TestCase
        r = self.correr('--salida', str(self.evidencia()))
        self.assertEqual(r.returncode, 1)
        codigos = {h['caso']: h['codigo'] for h in json.loads((self.evidencia() / 'hechos.json').read_text())['demo_caso']}
        self.assertEqual(codigos['NoCorre.test_dm1_fantasma'], 1)
        self.assertFalse(self.resultado()['casos_exactos_sin_omisiones_duplicados_ni_fallas'])

    def test_vg2_una_subclase_que_hereda_casos_los_trae_en_el_contrato_y_hay_exito(self):
        self.escribir('tests/test_demo.py', MODULO + '\n\nclass Hija(Uno):\n    pass\n')  # unittest corre también Hija.test_dm1_a, etc.
        r = self.correr('--salida', str(self.evidencia()))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        hechos = json.loads((self.evidencia() / 'hechos.json').read_text())
        self.assertIn('Hija.test_dm1_a', {h['caso'] for h in hechos['demo_caso']})
        self.assertEqual(hechos['demo_corrida'][0]['casos'], 8)

    def test_vg2_si_la_corrida_trae_un_caso_que_el_contrato_no_conoce_no_hay_exito_aunque_todo_pase(self):
        self.escribir('tests/test_demo.py', MODULO + "\n\nDinamica = type('Dinamica', (unittest.TestCase,), {'test_dm1_dinamico': lambda self: None})\n")
        r = self.correr('--salida', str(self.evidencia()))  # una clase creada en tiempo de ejecución: ast no la ve y unittest sí
        self.assertEqual(r.returncode, 1)
        resultado = self.resultado()
        self.assertFalse(resultado['casos_exactos_sin_omisiones_duplicados_ni_fallas'])
        self.assertTrue(resultado['fuentes_estables'])
        self.assertFalse(resultado['exitoso'])

    def test_vg2_un_caso_omitido_no_cuenta_como_pasado(self):
        self.escribir('tests/test_demo.py', MODULO.replace("    def test_dm1_b(self):", "    @unittest.skip('adrede')\n    def test_dm1_b(self):"))
        r = self.correr('--salida', str(self.evidencia()))
        self.assertEqual(r.returncode, 1)
        codigos = {h['caso']: h['codigo'] for h in json.loads((self.evidencia() / 'hechos.json').read_text())['demo_caso']}
        self.assertEqual(codigos['Uno.test_dm1_b'], 1)
        self.assertFalse(self.resultado()['casos_exactos_sin_omisiones_duplicados_ni_fallas'])

    def test_vg2_una_trazabilidad_con_menos_casos_de_los_esperados_no_es_exito(self):
        from unittest.mock import patch
        with patch.object(vc.trazabilidad, 'trazar', return_value={'casos': {}, 'requisitos': {}}), patch.object(sys, 'path', list(sys.path)):
            try:
                self.assertFalse(vc.producir(self.raiz, CAMBIO, 'test_demo', self.evidencia()))
            finally:
                sys.modules.pop('test_demo', None)
        resultado = self.resultado()
        self.assertTrue(resultado['casos_exactos_sin_omisiones_duplicados_ni_fallas'])
        self.assertTrue(resultado['fuentes_estables'])
        self.assertFalse(resultado['exitoso'])

    def test_vg2_un_modulo_cuyo_nombre_parece_un_caso_no_confunde_a_los_demas(self):
        self.escribir('tests/test_dm1_demo.py', MODULO)
        r = subprocess.run([sys.executable, str(HERRAMIENTA), CAMBIO, '--pruebas', 'test_dm1_demo', '--raiz', str(self.raiz),
                            '--salida', str(self.evidencia())], env=ENTORNO, capture_output=True, text=True, stdin=subprocess.DEVNULL)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_vg2_fuentes_tambien_acepta_una_salida_relativa(self):
        cwd = os.getcwd()
        (self.raiz / 'evidencia').mkdir()
        (self.raiz / 'evidencia/algo.txt').write_text('x')
        os.chdir(self.raiz)
        try:
            self.assertNotIn('evidencia/algo.txt', vc.fuentes(self.raiz, Path('evidencia'))['sha256'])
        finally:
            os.chdir(cwd)

    def test_vg2_una_salida_relativa_cuenta_igual_que_una_absoluta_y_producir_no_imprime(self):
        import contextlib
        import io
        from unittest.mock import patch
        salida = io.StringIO()
        cwd = os.getcwd()
        os.chdir(self.raiz)
        try:
            with patch.object(sys, 'path', list(sys.path)), contextlib.redirect_stdout(salida):
                try:
                    self.assertTrue(vc.producir(self.raiz, CAMBIO, 'test_demo', Path('evidencia')))
                finally:
                    sys.modules.pop('test_demo', None)
        finally:
            os.chdir(cwd)
        self.assertTrue(self.resultado()['exitoso'])
        self.assertEqual(salida.getvalue().count('Evidencia:'), 0)  # sólo main() imprime; así una prueba en el mismo proceso no ensucia a quien lee la salida

    def test_vg2_una_spec_o_unas_pruebas_ilegibles_salen_con_el_codigo_2_y_sin_traceback(self):
        (self.raiz / f'openspec/changes/{CAMBIO}/specs/demo/spec.md').write_bytes(b'### Requirement: el_primero\n\xff\xfe\n')
        r = self.correr('--salida', str(self.evidencia()))
        self.assertEqual(r.returncode, 2)
        self.assertNotIn('Traceback', r.stderr)
        self.assertIn('spec', r.stderr)
        self.escribir(f'openspec/changes/{CAMBIO}/specs/demo/spec.md', SPEC)
        (self.raiz / 'tests/test_demo.py').write_bytes(b'def test_dm1_a(:\n')
        r = self.correr('--salida', str(self.evidencia()))
        self.assertEqual(r.returncode, 2)
        self.assertNotIn('Traceback', r.stderr)
        (self.raiz / 'tests/test_demo.py').write_bytes(b'# \xff\n')
        r = self.correr('--salida', str(self.evidencia()))
        self.assertEqual(r.returncode, 2)
        self.assertNotIn('Traceback', r.stderr)
        self.assertFalse(self.evidencia().exists())

    def test_vg2_una_spec_con_nombres_en_lenguaje_natural_se_cotejan_por_slug_con_el_registro(self):
        self.escribir(f'openspec/changes/{CAMBIO}/specs/demo/spec.md', SPEC.replace('el_primero', 'El primero').replace('el_segundo', 'El segundo'))
        r = self.correr('--salida', str(self.evidencia()))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        hechos = json.loads((self.evidencia() / 'hechos.json').read_text())
        self.assertEqual({h['requisito'] for h in hechos['demo_caso']}, {'el_primero', 'el_segundo'})

    def test_vg2_si_la_trazabilidad_falla_la_evidencia_queda_entera_y_en_rojo(self):
        from unittest.mock import patch
        with patch.object(vc.trazabilidad, 'trazar', side_effect=RuntimeError('adrede')), patch.object(sys, 'path', list(sys.path)):
            try:
                self.assertFalse(vc.producir(self.raiz, CAMBIO, 'test_demo', self.evidencia()))
            finally:
                sys.modules.pop('test_demo', None)
        for nombre in ('suite.txt', 'hechos.json', 'trazabilidad.json', 'resultado.json'):
            self.assertTrue((self.evidencia() / nombre).is_file(), nombre)
        self.assertIn('RuntimeError', (self.evidencia() / 'trazabilidad.json').read_text())
        self.assertFalse(self.resultado()['exitoso'])

    def test_vg2_un_archivo_modificado_y_restaurado_durante_la_corrida_tampoco_esta_quieto(self):
        self.escribir('tests/test_demo.py', MODULO.replace("def test_dm1_a(self):\n        self.assertTrue(True)",
            "def test_dm1_a(self):\n        import pathlib, time\n        d = pathlib.Path(__file__).parents[1] / 'datos.txt'\n"
            "        original = d.read_bytes()\n        d.write_bytes(b'otro')\n        time.sleep(0.01)\n        d.write_bytes(original)"))
        r = self.correr('--salida', str(self.evidencia()))
        self.assertEqual(r.returncode, 1)
        resultado = self.resultado()
        self.assertFalse(resultado['fuentes_estables'])
        self.assertEqual(self.git('status', '--porcelain', 'datos.txt'), '')  # los bytes quedaron igual: sólo la hora delata el cambio

    def test_vg2_un_contrato_roto_ni_corre_la_suite_ni_crea_la_carpeta(self):
        self.escribir(f'openspec/changes/{CAMBIO}/specs/demo/spec.md', SPEC + '\n### Requirement: el_tercero\nTipo: funcional\nEl sistema DEBE c.\n')
        self.escribir(f'.factory/cambios/{CAMBIO}/factory.json', json.dumps({'requisitos': ['demo_h.el_primero', 'demo_h.el_segundo', 'demo_h.el_tercero']}))
        r = self.correr('--salida', str(self.evidencia()))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('el_tercero', r.stdout + r.stderr)
        self.assertFalse(self.evidencia().exists())

    def test_vg2_un_requisito_de_la_spec_que_el_registro_no_importo_falla(self):
        self.escribir(f'.factory/cambios/{CAMBIO}/factory.json', json.dumps({'requisitos': ['demo_h.el_primero']}))
        r = self.correr('--salida', str(self.evidencia()))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('el_segundo', r.stdout + r.stderr)

    def test_vg2_la_carpeta_de_evidencia_no_cuenta_como_fuente_y_no_se_pisa(self):
        self.assertEqual(self.correr('--salida', str(self.evidencia())).returncode, 0)
        otra = self.correr('--salida', str(self.evidencia()))  # ya existe
        self.assertNotEqual(otra.returncode, 0)
        fuentes = self.resultado()['origen']['sha256']
        self.assertIn('datos.txt', fuentes)
        self.assertFalse(any(ruta.startswith(('evidencia/', '.factory/', 'kb/', 'tareas/')) for ruta in fuentes))

    def test_vg2_las_fallas_de_la_herramienta_no_dejan_un_exito_falso(self):
        r = subprocess.run([sys.executable, str(HERRAMIENTA), 'no-existe', '--pruebas', 'test_demo', '--raiz', str(self.raiz),
                            '--salida', str(self.evidencia())], env=ENTORNO, capture_output=True, text=True, stdin=subprocess.DEVNULL)
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(self.evidencia().exists())


class Catalogos(ProyectoTemporal):
    # --- vg3: los catálogos del cambio -------------------------------------------------------------------------------------
    def carpeta(self):
        return self.raiz / 'catalogos'

    def test_vg3_hay_un_catalogo_por_requisito_y_el_de_la_corrida_con_los_numeros_de_casos(self):
        r = self.correr('--catalogos')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(sorted(p.name for p in self.carpeta().glob('*.oracle')),
                         ['factory_demo.corrida_completa.oracle', 'factory_demo.el_primero.oracle', 'factory_demo.el_segundo.oracle'])
        primero = (self.carpeta() / 'factory_demo.el_primero.oracle').read_text()
        segundo = (self.carpeta() / 'factory_demo.el_segundo.oracle').read_text()
        corrida = (self.carpeta() / 'factory_demo.corrida_completa.oracle').read_text()
        self.assertIn('umbral == 2 segun contrato', primero)
        self.assertIn('umbral == 3 segun contrato', segundo)
        self.assertIn('c.casos == 5', corrida)
        self.assertIn('medida factory_demo.el_primero:', primero)
        self.assertIn('de demo_caso c', primero)
        self.assertIn('c.requisito == "el_segundo"', segundo)
        self.assertIn('de demo_corrida c', corrida)

    def test_vg3_escribirlos_de_nuevo_con_los_mismos_casos_no_cambia_nada(self):
        self.correr('--catalogos')
        antes = {p.name: p.read_bytes() for p in self.carpeta().glob('*.oracle')}
        marcas = {p.name: p.stat().st_mtime_ns for p in self.carpeta().glob('*.oracle')}
        r = self.correr('--catalogos')
        self.assertEqual(r.returncode, 0)
        self.assertEqual({p.name: p.read_bytes() for p in self.carpeta().glob('*.oracle')}, antes)
        self.assertEqual({p.name: p.stat().st_mtime_ns for p in self.carpeta().glob('*.oracle')}, marcas)  # ni siquiera se reescriben
        self.assertIn('sin cambios', r.stdout)

    def test_vg3_si_cambia_el_numero_de_casos_se_reescribe_solo_lo_que_cambio(self):
        self.correr('--catalogos')
        antes = {p.name: p.read_bytes() for p in self.carpeta().glob('*.oracle')}
        self.escribir('tests/test_demo.py', MODULO + '\n\nclass Tres(unittest.TestCase):\n    def test_dm1_nuevo(self):\n        pass\n')
        self.correr('--catalogos')
        despues = {p.name: p.read_bytes() for p in self.carpeta().glob('*.oracle')}
        cambiados = {n for n in despues if despues[n] != antes[n]}
        self.assertEqual(cambiados, {'factory_demo.el_primero.oracle', 'factory_demo.corrida_completa.oracle'})
        self.assertIn('umbral == 3 segun contrato', despues['factory_demo.el_primero.oracle'].decode())

    def test_vg3_el_catalogo_de_un_requisito_es_exactamente_este_texto(self):
        self.correr('--catalogos', '--alcance', 'mi alcance')
        self.assertEqual((self.carpeta() / 'factory_demo.el_primero.oracle').read_text(), (
            'medida factory_demo.el_primero:\n    de demo_caso c\n    donde c.requisito == "el_primero" y c.codigo == 0\n    resumen contar(1)\n'
            '    umbral == 2 segun contrato porque "deben pasar los 2 casos enumerados para este requisito en tests/test_demo.py; '
            'asociar junto a corrida_completa"\n    requiere demo_caso\n    ambito universal\n    alcance "mi alcance"\n'))

    def test_vg3_un_alcance_con_comillas_o_saltos_de_linea_se_rechaza_y_no_escribe_nada(self):
        for alcance in ('escenarios con "mock"', 'dos\nlíneas', 'con\rretorno', 'con\ttab', 'en C:\\tests\\', 'uno\u2028dos', 'uno\u2029dos', 'uno\x85dos', 'uno\x0bdos', 'uno\x1cdos'):
            with self.subTest(alcance=alcance):
                r = self.correr('--catalogos', '--alcance', alcance)
                self.assertEqual(r.returncode, 2)
                self.assertIn('alcance', r.stderr)
                self.assertFalse(self.carpeta().exists())

    def test_vg3_un_requisito_renombrado_retira_su_catalogo_viejo_y_no_toca_los_de_otros_modulos(self):
        self.correr('--catalogos')
        ajeno = self.carpeta() / 'factory_demo_extra.el_primero.oracle'  # otro módulo cuyo nombre empieza igual
        ajeno.write_text('medida ajena\n')
        otro = self.carpeta() / 'factory_otro.cosa.oracle'
        otro.write_text('medida otra\n')
        self.escribir(f'openspec/changes/{CAMBIO}/specs/demo/spec.md', SPEC.replace('el_segundo', 'el_nuevo'))
        self.escribir(f'.factory/cambios/{CAMBIO}/factory.json', json.dumps({'requisitos': ['demo_h.el_nuevo', 'demo_h.el_primero']}))
        r = self.correr('--catalogos')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse((self.carpeta() / 'factory_demo.el_segundo.oracle').exists())
        self.assertTrue((self.carpeta() / 'factory_demo.el_nuevo.oracle').is_file())
        self.assertTrue(ajeno.is_file())
        self.assertTrue(otro.is_file())
        self.assertIn('factory_demo.el_segundo.oracle (retirado)', r.stdout)
        self.assertIn('factory_demo.el_primero.oracle', sorted(p.name for p in self.carpeta().glob('factory_demo.*.oracle')))
        again = self.correr('--catalogos')
        self.assertIn('sin cambios', again.stdout)  # y ya no hay nada que retirar

    def test_vg3_con_un_contrato_roto_no_escribe_nada(self):
        self.escribir('tests/test_demo.py', 'import unittest\n')
        r = self.correr('--catalogos')
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(self.carpeta().exists())

    def test_vg3_los_catalogos_escritos_tienen_la_misma_forma_que_los_que_ya_usa_factory(self):
        self.correr('--catalogos')
        real = ((SOURCE / 'catalogos/factory_alarmas_flujo.corrida_completa.oracle').read_text()
                .replace('alarmas_flujo', 'demo').replace('c.casos == 26', 'c.casos == 5'))
        self.assertEqual((self.carpeta() / 'factory_demo.corrida_completa.oracle').read_text(), real)

    def test_vg3_este_modulo_se_verifica_a_si_mismo_con_su_propia_convencion(self):
        """El contrato derivado de los nombres de este archivo cubre cada caso vg que existe, y sólo los vg1 a vg3."""
        casos = vc.casos_del_modulo(Path(__file__).read_text(encoding='utf-8'))
        self.assertEqual(sorted(casos), [1, 2, 3])
        existentes = {'.'.join(t.id().split('.')[-2:]) for suite in unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
                      for t in suite if '.test_vg' in t.id()}
        self.assertEqual({c for lista in casos.values() for c in lista}, existentes)


if __name__ == '__main__':
    unittest.main()
