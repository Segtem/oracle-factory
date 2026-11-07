"""La vista Destinos del tablero: escenarios td1–td5, con la CLI de verdad, destinos simulados por scripts locales y la extensión en node."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_despliegue as _dd  # noqa: E402
import test_tablero as _tablero  # noqa: E402
from tools import contrato_vscode as cv  # noqa: E402

SOURCE = Path(__file__).resolve().parents[1]
EXTENSION = SOURCE / 'editores/vscode'
NODE = shutil.which('node')
SIMULAR, AUTORIZAR = 'oracle-factory desplegar --simular', 'oracle-factory desplegar --autorizar'


def html_de(datos):
    """El HTML del tablero para unos datos armados a mano (la salida de la CLI más lo que le agrega la extensión)."""
    codigo = ("const t = require(process.argv[1] + '/tablero.js'); const d = JSON.parse(process.argv[2]);"
              "process.stdout.write(t.html(d, {nonce: 'n', cspSource: 'vscode-resource:'}))")
    r = subprocess.run([NODE, '-e', codigo, str(EXTENSION), json.dumps(datos)], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    return r.stdout


def seccion(html):
    """Sólo la sección «Destinos» de la página."""
    inicio = html.index('<section class="destinos"')
    return html[inicio:html.index('</section>', inicio)]


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def cli_falsa(self):
        cli = Path(self.tmp) / 'oracle-factory'
        cli.write_text(f'#!/bin/sh\nPYTHONPATH={SOURCE} exec {sys.executable} -c "import sys; '
                       f'from oracle_factory.cli import main; sys.exit(main())" "$@"\n')
        cli.chmod(0o755)
        return cli

    def tablero(self, raiz, mensajes=(), **entorno):
        r = subprocess.run([NODE, str(SOURCE / 'tests/tablero_en_node.cjs'), str(EXTENSION), str(raiz), json.dumps(list(mensajes)), str(self.cli_falsa())],
                           capture_output=True, text=True, timeout=120, env={**os.environ, **entorno})
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def tres_destinos(self, marca=None):
        """api probado, app que falló en su despliegue, nodo (esp32) sin desplegar. `marca`: archivo donde cada consulta de versión deja una línea."""
        def destino(nombre, **mas):
            d = _dd.destino(nombre, **mas)
            if marca:
                d['version'] = f'echo {nombre} >> {marca}; {d["version"]}'
            return d
        sub = Path(self.tmp) / 'proy'
        sub.mkdir()
        raiz = _dd.proyecto(sub, {'api': destino('api'), 'app': destino('app', tipo='app', depende_de=['api'], desplegar='false'),
                                  'nodo': destino('nodo', tipo='esp32', depende_de=['api'])})
        _dd.desplegar(raiz, destinos=['app'])  # falla: se vuelve atrás también api, de la que depende
        _dd.desplegar(raiz, destinos=['api'])  # api queda probado; app sigue en su fallo
        if marca:
            Path(marca).unlink(missing_ok=True)
        return raiz


@unittest.skipUnless(NODE, 'hace falta node')
class Muestra(Base):
    # --- td1: cada destino con su estado ---------------------------------------------------------------------------------
    def test_td1_tres_destinos_con_estados_distintos_y_el_desconocido_no_se_muestra_al_dia(self):
        raiz = self.tres_destinos()
        salida = self.tablero(raiz)
        s = seccion(salida['html'])
        for texto in ('api', 'app', 'nodo', 'esp32', 'probado', 'fallido', 'sin desplegar', 'depende de api', 'Brian'):
            self.assertIn(texto, s)
        self.assertIn('versión desconocida', s)  # sin consultar no se sabe: no es «al día»
        self.assertNotIn('al día', s)
        self.assertNotIn('class="cambio"', salida['html'])  # (sin cambios) y la sección está en la página
        # Se rehace cuando se escribe el registro de un despliegue.
        self.assertTrue(any('.factory/despliegues' in v['glob'] and v['avisan'] for v in salida['vigilados']), salida['vigilados'])

    def test_td1_el_texto_con_marcas_se_ve_como_texto(self):
        malo = '<script>alert(1)</script>"\''
        datos = {'cambios': [], 'sesion': {'estado': 'sin-live-share'}, 'destinos_error': None,
                 'destinos': {'version': 1, 'rama': 'main', 'ultima_corrida': {'id': 'x', 'commit': 'a' * 40, 'cuando': '2026-11-07T00:00:00+00:00', 'planeo': 'claude-code',
                                                                            'autorizo': malo, 'resultado': 'fallo', 'motivo': malo, 'aviso': None},
                              'destinos': [{'nombre': malo, 'tipo': malo, 'estado': malo, 'version_desplegada': malo, 'version_esperada': 'b' * 40,
                                            'ultima_prueba': None, 'desactualizado': True, 'depende_de': [malo], 'corrida': 'x'}]}}
        s = seccion(html_de(datos))
        self.assertNotIn('<script>', s)
        self.assertIn('&lt;script&gt;', s)
        self.assertIn('desactualizado', s)

    # --- td2: sólo se consulta a pedido ----------------------------------------------------------------------------------
    def test_td2_repintar_el_tablero_no_corre_el_comando_de_version(self):
        marca = Path(self.tmp) / 'consultas'
        raiz = self.tres_destinos(marca=str(marca))
        registro = next((raiz / '.factory/despliegues').glob('*/registro.json'))
        salida = self.tablero(raiz, TABLERO_CAMBIO=json.dumps({'ruta': str(registro), 'contenido': registro.read_text()}))
        self.assertEqual(salida['pintadas'], 2)  # se pintó, se repintó y ningún destino fue consultado
        self.assertFalse(marca.exists())

    def test_td2_consultar_a_pedido_corre_el_comando_una_vez_y_muestra_la_version(self):
        marca = Path(self.tmp) / 'consultas'
        raiz = self.tres_destinos(marca=str(marca))
        _dd.git(raiz, 'commit', '-q', '--allow-empty', '-m', 'algo nuevo')  # main avanzó: api quedó atrás
        salida = self.tablero(raiz, [{'tipo': 'consultar-destinos'}])
        self.assertEqual(sorted(marca.read_text().split()), ['api', 'app', 'nodo'])  # una consulta por destino, y nada más
        consultada = next(h for h in salida['historia'] if 'desactualizado' in seccion(h))
        self.assertIn('desactualizado', seccion(consultada))
        self.assertIn('versión desconocida', seccion(salida['html']))  # antes de apretar el botón no se sabía

    # --- td3: sólo escribe, nunca despliega ------------------------------------------------------------------------------
    def test_td3_los_botones_escriben_en_la_terminal_sin_ejecutar_ni_autorizar(self):
        raiz = self.tres_destinos()
        antes = sorted(p.name for p in (raiz / '.factory/despliegues').iterdir())
        salida = self.tablero(raiz, [{'tipo': 'terminal', 'comando': SIMULAR}, {'tipo': 'terminal', 'comando': AUTORIZAR}])
        s = seccion(salida['html'])
        comandos = [c.split('"')[0] for c in s.split('data-comando="')[1:]]
        self.assertEqual(sorted(comandos), sorted([SIMULAR, AUTORIZAR]))
        self.assertEqual([(t['texto'].split(' ', 1)[1], t['enter']) for t in salida['terminal']],
                         [('desplegar --simular', False), ('desplegar --autorizar', False)])
        self.assertEqual(sorted(p.name for p in (raiz / '.factory/despliegues').iterdir()), antes)  # no se ejecutó nada
        self.assertFalse((raiz / 'srv/nodo').exists())

    def test_td3_el_invitado_no_tiene_consultar_y_el_anfitrion_si(self):
        base = {'cambios': [], 'destinos_error': None,
                'destinos': {'version': 1, 'rama': 'main', 'ultima_corrida': None, 'destinos': []}}
        anfitrion = seccion(html_de({**base, 'sesion': {'estado': 'activa', 'yo': 'Ana', 'rol': 'anfitrión', 'otros': [], 'invitado': False}}))
        invitado = seccion(html_de({**base, 'sesion': {'estado': 'activa', 'yo': 'Iván', 'rol': 'invitado', 'otros': [], 'invitado': True}}))
        self.assertIn('data-consultar', anfitrion)
        self.assertNotIn('data-consultar', invitado)
        self.assertNotIn('Consultar ahora', invitado)
        self.assertIn('terminal de quien comparte', invitado)


@unittest.skipUnless(NODE, 'hace falta node')
class SinDestinos(unittest.TestCase):
    """Con el proyecto de los tests del tablero: un cambio abierto con hallazgos de dos revisores."""
    T = _tablero.Tablero
    escribe, git, salida, cambio_cerrado = T.escribe, T.git, T.salida, T.cambio_cerrado
    candidato_nuevo, pedir, con_dos_revisores = T.candidato_nuevo, T.pedir, T.con_dos_revisores

    def setUp(self):
        _tablero.Tablero.setUp(self)
        self.con_dos_revisores()

    def tablero_html(self):
        cli = Path(self.tmp.name) / 'oracle-factory'
        cli.write_text(f'#!/bin/sh\nPYTHONPATH={SOURCE} exec {sys.executable} -c "import sys; '
                       f'from oracle_factory.cli import main; sys.exit(main())" "$@"\n')
        cli.chmod(0o755)
        r = subprocess.run([NODE, str(SOURCE / 'tests/tablero_en_node.cjs'), str(EXTENSION), str(self.root), '[]', str(cli)],
                           capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)['html']

    # --- td4: sin destinos o con error, el tablero sigue -----------------------------------------------------------------
    def test_td4_un_proyecto_sin_destinos_dice_como_declararlos_y_los_cambios_se_ven(self):
        html = self.tablero_html()
        s = seccion(html)
        self.assertIn('no declara destinos', s)
        self.assertIn('.factory/destinos.json', s)
        self.assertIn('<h3>Hallazgos</h3>', html)

    def test_td4_una_declaracion_invalida_muestra_el_motivo_y_los_cambios_se_ven(self):
        (self.root / '.factory').mkdir(exist_ok=True)
        (self.root / '.factory/destinos.json').write_text(json.dumps({'destinos': {'api': {'tipo': 'vps'}}, 'conjunto': {'probar': 'true'}}))
        html = self.tablero_html()
        s = seccion(html)
        self.assertIn('api', s)
        self.assertIn('desplegar', s)
        self.assertNotIn('no declara destinos', s)
        self.assertIn('<h3>Hallazgos</h3>', html)


class Contrato(unittest.TestCase):
    # --- td5: el contrato cubre destinos ---------------------------------------------------------------------------------
    def test_td5_el_contrato_declara_destinos_y_la_cli_lo_cumple(self):
        todo = cv.cargar()
        self.assertIn('destinos', todo)
        contrato = {'destinos': todo['destinos']}  # los demás comandos los comprueba test_contrato_vscode
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, True)
        raiz = _dd.proyecto(tmp, {'api': _dd.destino('api'), 'app': _dd.destino('app', tipo='app', depende_de=['api'])})
        _dd.desplegar(raiz)  # con una corrida: ultima_corrida y ultima_prueba tienen muestra
        salida = json.loads(_dd.correr(raiz, 'destinos', '--json', '--sin-consultar').stdout)
        self.assertEqual(cv.comprobar_la_cli(contrato, {'destinos': [salida]}), [])
        roto = json.loads(json.dumps(salida))
        for d in roto['destinos']:
            d['situacion'] = d.pop('estado')
        problemas = cv.comprobar_la_cli(contrato, {'destinos': [roto]})
        self.assertTrue(any('destinos' in p and 'estado' in p for p in problemas), problemas)

    def test_td5_el_codigo_de_tablero_no_lee_claves_de_destinos_sin_declarar(self):
        contrato = cv.cargar()
        texto = (EXTENSION / 'tablero.js').read_text(encoding='utf-8')
        self.assertEqual(cv.comprobar_el_codigo(contrato, {'tablero.js': texto}), [])
        problemas = cv.comprobar_el_codigo(contrato, {'tablero.js': texto + '\nfunction x(d) { return d.destinos.campo_nuevo_de_destinos; }'})
        self.assertEqual(len(problemas), 1)
        self.assertIn('campo_nuevo_de_destinos', problemas[0])


if __name__ == '__main__':
    unittest.main()
