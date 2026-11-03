"""El contrato entre la CLI y la extensión de VS Code: escenarios cv1–cv3, con proyectos temporales de Factory, la CLI de verdad y node."""
import contextlib
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_estructura as _estructura  # noqa: E402
from tools import contrato_vscode as cv  # noqa: E402

f = _estructura.f
SOURCE = _estructura.SOURCE
EXTENSION = SOURCE / 'editores/vscode'
NODE = shutil.which('node')
COMANDOS = ('resumen', 'estado', 'donde', 'tablero')


class Pura(unittest.TestCase):
    """Las dos comprobaciones sobre datos armados a mano: no hace falta un proyecto ni node."""

    CONTRATO = {'estado': [{'ruta': 'proximo_paso', 'tipos': ['string', 'null']},
                           {'ruta': 'requisitos', 'tipos': ['array']},
                           {'ruta': 'requisitos[].id', 'tipos': ['string']},
                           {'ruta': 'revision', 'tipos': ['object', 'null']},
                           {'ruta': 'revision.decision', 'tipos': ['string'], 'opcional': True}]}
    BUENO = [{'proximo_paso': 'oracle-factory x', 'requisitos': [{'id': 'a'}, {'id': 'b'}], 'revision': {'decision': 'aprobar'}, 'de_mas': 1},
             {'proximo_paso': None, 'requisitos': [], 'revision': None}]

    # --- cv2: la CLI entrega cada clave declarada con un tipo permitido -----------------------------------------------------
    def test_cv2_la_cli_cumple_el_contrato_y_las_claves_de_mas_no_molestan(self):
        self.assertEqual(cv.comprobar_la_cli(self.CONTRATO, {'estado': self.BUENO}), [])

    def test_cv2_una_clave_renombrada_se_nombra_con_su_comando(self):
        malo = [dict(d) for d in self.BUENO]
        for d in malo:
            d['siguiente_paso'] = d.pop('proximo_paso')
        [problema] = cv.comprobar_la_cli(self.CONTRATO, {'estado': malo})
        self.assertIn('estado', problema)
        self.assertIn('proximo_paso', problema)
        self.assertIn('no da', problema)

    def test_cv2_un_tipo_cambiado_dice_el_esperado_y_el_encontrado(self):
        malo = copy.deepcopy(self.BUENO)
        malo[0]['requisitos'] = {'a': 1}
        problemas = cv.comprobar_la_cli(self.CONTRATO, {'estado': malo})
        [problema] = [p for p in problemas if 'esperaba' in p]
        self.assertIn('requisitos', problema)
        self.assertIn('array', problema)
        self.assertIn('object', problema)

    def test_cv2_una_clave_declarada_que_falta_en_un_solo_elemento_de_un_arreglo_tambien_falla(self):
        malo = copy.deepcopy(self.BUENO)
        malo[0]['requisitos'].append({})
        [problema] = cv.comprobar_la_cli(self.CONTRATO, {'estado': malo})
        self.assertIn('requisitos[].id', problema)
        self.assertIn('1 de 3', problema)

    def test_cv2_una_clave_opcional_o_bajo_un_padre_nulo_no_falla(self):
        sin_ids = {'estado': [e for e in self.CONTRATO['estado'] if e['ruta'] != 'requisitos[].id']}
        self.assertEqual(cv.comprobar_la_cli(sin_ids, {'estado': [self.BUENO[1]]}), [])  # revision es null: revision.decision no se pide
        sin = [{'proximo_paso': None, 'requisitos': [], 'revision': {}}]
        self.assertEqual(cv.comprobar_la_cli(sin_ids, {'estado': sin}), [])  # opcional

    def test_cv2_una_clave_obligatoria_con_el_tipo_equivocado_o_ausente_en_el_padre_vacio_se_distingue(self):
        sin_requisitos = [{'proximo_paso': None, 'requisitos': [], 'revision': None}]
        contrato = {'estado': [{'ruta': 'requisitos[].id', 'tipos': ['string']}]}
        [problema] = cv.comprobar_la_cli(contrato, {'estado': sin_requisitos})
        self.assertIn('sin muestra', problema)  # ningún estado la ejercita: no se puede decir que está bien
        self.assertEqual(cv.comprobar_la_cli(contrato, {'estado': sin_requisitos + self.BUENO}), [])

    def test_cv2_los_objetos_que_se_recorren_se_comprueban_valor_por_valor(self):
        contrato = {'tablero': [{'ruta': 'por.*', 'tipos': ['array']}]}
        self.assertEqual(cv.comprobar_la_cli(contrato, {'tablero': [{'por': {'ana': [], 'luis': ['x']}}]}), [])
        [problema] = cv.comprobar_la_cli(contrato, {'tablero': [{'por': {'ana': [], 'luis': 'x'}}]})
        self.assertIn('por.*', problema)

    def test_cv2_los_tipos_se_distinguen_incluidos_booleanos_y_nulos(self):
        self.assertEqual([cv.tipo_de(v) for v in ('a', 1, 1.5, True, None, [], {})],
                         ['string', 'number', 'number', 'boolean', 'null', 'array', 'object'])

    # --- cv1: la extensión sólo lee lo que el contrato declara ----------------------------------------------------------------
    def test_cv1_una_clave_leida_y_no_declarada_se_nombra_con_su_comando(self):
        leidas = {'estado': ['proximo_paso', 'requisitos', 'requisitos[].id', 'avisos'], 'tablero': ['cambios[].avisos']}
        problemas = cv.comprobar_la_extension(self.CONTRATO, leidas)
        self.assertEqual(len(problemas), 2)
        self.assertTrue(any('estado' in p and 'avisos' in p for p in problemas))
        self.assertTrue(any('tablero' in p and 'cambios[].avisos' in p for p in problemas))
        self.assertEqual(cv.comprobar_la_extension(self.CONTRATO, {'estado': ['proximo_paso', 'revision.decision']}), [])

    def test_cv1_el_contrato_del_repositorio_declara_tipos_validos_y_rutas_sin_repetir(self):
        contrato = cv.cargar()
        self.assertEqual(set(contrato), set(COMANDOS))
        for comando, entradas in contrato.items():
            rutas = [e['ruta'] for e in entradas]
            self.assertEqual(len(rutas), len(set(rutas)), f'{comando}: rutas repetidas')
            self.assertEqual(rutas, sorted(rutas), f'{comando}: las rutas van ordenadas')
            for e in entradas:
                self.assertTrue(e['tipos'] and set(e['tipos']) <= set(cv.TIPOS), (comando, e))
                self.assertLessEqual(set(e), {'ruta', 'tipos', 'opcional'}, (comando, e))


@unittest.skipUnless(NODE, 'hace falta node')
class Real(unittest.TestCase):
    """Un proyecto de verdad con cambios en varios estados, la CLI de verdad y la extensión en node."""
    setUp_estructura = _estructura.Estructura.setUp
    escribe, git, estado = _estructura.Estructura.escribe, _estructura.Estructura.git, _estructura.Estructura.estado
    cambio_medido, cambio_juzgado = _estructura.Estructura.cambio_medido, _estructura.Estructura.cambio_juzgado
    sha7 = _estructura.Estructura.sha7

    def setUp(self):
        self.setUp_estructura()
        self.cli = self.root / '.venv/bin/oracle-factory'
        self.cli.parent.mkdir(parents=True)
        self.cli.write_text(f'#!/bin/sh\nexec {sys.executable} -c "import sys; from oracle_factory.cli import main; '
                            f'sys.exit(main())" "$@"\n')
        self.cli.chmod(0o755)

    def json(self, *args):
        r = subprocess.run([str(self.cli), *args, '--json'], cwd=self.root, capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def estados(self):
        """{comando: [JSON de cada estado]}: un cambio juzgado, uno sin avanzar, uno de otra persona con mensajes y uno abandonado."""
        juzgado = self.cambio_juzgado()
        sin_avanzar = f.nuevo('Sin avanzar', capacidad='otra')
        con_dueno = f.nuevo('Con dueño', capacidad='otra2')
        for accion in (lambda: f.tomar(con_dueno), lambda: f.mensaje(con_dueno, 'una nota del equipo')):
            with contextlib.suppress(Exception):
                accion()
        abandonado = f.nuevo('Abandonado', capacidad='otra3')
        with self.escribe('1'):
            f.abandonar(abandonado)
        abiertos = [juzgado, sin_avanzar, con_dueno]
        return {'resumen': [self.json('resumen')], 'tablero': [self.json('tablero')],
                'estado': [self.json('estado', i) for i in abiertos], 'donde': [self.json('donde', i) for i in abiertos]}

    def leidas(self, salidas):
        carpeta = Path(self.tmp.name) / 'json'
        carpeta.mkdir()
        (carpeta / 'resumen.json').write_text(json.dumps(salidas['resumen'][0]))
        (carpeta / 'tablero.json').write_text(json.dumps(salidas['tablero'][0]))
        for i, (e, d) in enumerate(zip(salidas['estado'], salidas['donde'])):
            (carpeta / f'estado-{i}.json').write_text(json.dumps(e))
            (carpeta / f'donde-{i}.json').write_text(json.dumps(d))
        r = subprocess.run([NODE, str(SOURCE / 'tests/contrato_en_node.cjs'), str(EXTENSION), str(carpeta)], capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    # --- cv1 y cv2 con la CLI y la extensión de verdad -----------------------------------------------------------------------
    def test_cv1_la_extension_solo_lee_lo_declarado_y_la_cli_lo_entrega(self):
        salidas = self.estados()
        self.assertEqual(len(salidas['estado']), 3)
        leidas = self.leidas(salidas)
        self.assertEqual(set(leidas), set(COMANDOS))
        self.assertTrue(all(leidas[c] for c in COMANDOS), leidas)  # la extensión leyó algo de cada JSON
        contrato = cv.cargar()
        self.assertEqual(cv.comprobar_la_extension(contrato, leidas), [])
        self.assertEqual(cv.comprobar_la_cli(contrato, salidas), [])

    def test_cv1_si_el_contrato_pierde_una_clave_que_la_extension_lee_la_prueba_lo_nota(self):
        leidas = self.leidas(self.estados())
        contrato = {c: [e for e in entradas if not (c == 'estado' and e['ruta'] == 'proximo_paso')] for c, entradas in cv.cargar().items()}
        problemas = cv.comprobar_la_extension(contrato, leidas)
        self.assertEqual(len(problemas), 1)
        self.assertIn('estado', problemas[0])
        self.assertIn('proximo_paso', problemas[0])

    def test_cv2_si_la_cli_renombra_una_clave_que_la_extension_lee_la_prueba_lo_nota(self):
        salidas = self.estados()
        roto = copy.deepcopy(salidas)
        for e in roto['estado']:
            e['paso_siguiente'] = e.pop('proximo_paso')
        problemas = cv.comprobar_la_cli(cv.cargar(), roto)
        self.assertTrue(any('estado' in p and 'proximo_paso' in p for p in problemas), problemas)


@unittest.skipUnless(NODE, 'hace falta node')
class Registrador(unittest.TestCase):
    """El registrador de lecturas, con una «extensión» de juguete que lee cosas conocidas de JSON también de juguete."""

    def test_cv1_el_registrador_anota_claves_arreglos_mapas_y_lecturas_de_lo_que_no_esta(self):
        with tempfile.TemporaryDirectory() as tmp:
            ext, datos = Path(tmp) / 'ext', Path(tmp) / 'datos'
            ext.mkdir()
            datos.mkdir()
            (ext / 'modelo.js').write_text(
                "exports.raiz = r => { r.lista.map(x => x); Object.entries(r.mapa).forEach(([k, v]) => v.n); r.ausente; String(r); r.objeto.toString(); r.numeros.forEach(n => n); return []; };\n"
                "exports.hijosCambio = (e, d) => { e.a; d.b.c; };\n")
            (ext / 'tablero.js').write_text("exports.html = d => { d.x; d.sesion.estado; d.y.z; return ''; };\n")
            (datos / 'resumen.json').write_text(json.dumps({'lista': ['a', 'b'], 'mapa': {'uno': {'n': 1}, 'dos': {'n': 2}}, 'objeto': {}, 'numeros': [1, 2]}))
            (datos / 'tablero.json').write_text(json.dumps({'x': 1, 'y': {'z': 2}}))
            (datos / 'estado-0.json').write_text(json.dumps({'a': 1}))
            (datos / 'donde-0.json').write_text(json.dumps({'b': {'c': 1}}))
            r = subprocess.run([NODE, str(SOURCE / 'tests/contrato_en_node.cjs'), str(ext), str(datos)], capture_output=True, text=True, timeout=60)
            self.assertEqual(r.returncode, 0, r.stderr)
            leidas = json.loads(r.stdout)
        self.assertEqual(leidas['resumen'], ['ausente', 'lista', 'lista[]', 'mapa', 'mapa.*', 'mapa.*.n', 'numeros', 'numeros[]', 'objeto'])
        # toString no es una clave; los nombres de un mapa que se recorre ('uno', 'dos') tampoco; un elemento escalar de un arreglo sí.
        self.assertEqual(leidas['estado'], ['a'])
        self.assertEqual(leidas['donde'], ['b', 'b.c'])
        self.assertEqual(leidas['tablero'], ['x', 'y', 'y.z'])  # `sesion` la pone la extensión: no viene de la CLI


class Documento(unittest.TestCase):
    # --- cv3: el documento explica cómo actualizar el contrato ----------------------------------------------------------------
    def test_cv3_el_documento_nombra_los_comandos_el_archivo_y_como_actualizar(self):
        documento = (SOURCE / 'docs/tablero.md').read_text(encoding='utf-8')
        self.assertIn('editores/vscode/contrato.json', documento)
        for comando in cv.cargar():
            self.assertIn(f'`{comando}', documento)
        self.assertRegex(documento, r'(?is)contrato.*(actualiz|declar)')


if __name__ == '__main__':
    unittest.main()
