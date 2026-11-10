"""Autopilot: el agente lanzado recibe un entorno mínimo y una guía de permisos sin Python abierto: escenarios ea1–ea3."""
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import test_tests_editados as _te  # noqa: E402
from oracle_factory import conductor  # noqa: E402

f = _te.f
RAIZ = Path(__file__).resolve().parents[1]
VER = [sys.executable, '-I', '-c', 'import os, json; print(json.dumps(dict(os.environ)))']
PERMITIDAS = {'PATH': '/usr/bin', 'HOME': '/casa', 'USER': 'u', 'LOGNAME': 'u', 'SHELL': '/bin/sh', 'LANG': 'C.UTF-8', 'LANGUAGE': 'es', 'TERM': 'xterm',
              'TZ': 'UTC', 'TMPDIR': '/tmp', 'BASH_DEFAULT_TIMEOUT_MS': '600000', 'BASH_MAX_TIMEOUT_MS': '600000', 'LC_ALL': 'C.UTF-8',
              'XDG_CONFIG_HOME': '/casa/.config'}
OTRAS = {'OPENROUTER_API_KEY': 'secreto', 'MI_TOKEN': 'secreto', 'OTRA_VARIABLE': 'x', 'LCX_OTRA': 'x', 'XDGX': 'x', 'ANTHROPIC_API_KEY': 'clave', 'path': 'x'}


def ve_el_agente(entregar=()):
    """Las variables que ve un agente lanzado de verdad, con un entorno que mezcla permitidas y no permitidas."""
    with tempfile.TemporaryDirectory() as raiz, patch.dict(os.environ, {**PERMITIDAS, **OTRAS}, clear=True):
        _, lanzar = conductor.ejecutor(Path(raiz), 'claude-code', entregar)
        codigo, salida = lanzar(VER, 30)
    assert codigo == 0, salida
    return json.loads(salida)


class Entorno(unittest.TestCase):
    def test_ea1_el_agente_ve_las_permitidas_y_factory_agente_y_nada_mas(self):
        visto = ve_el_agente()
        self.assertEqual(visto, {**PERMITIDAS, 'FACTORY_AGENTE': 'claude-code'})
        for secreto in ('OPENROUTER_API_KEY', 'MI_TOKEN', 'OTRA_VARIABLE', 'ANTHROPIC_API_KEY'):
            self.assertNotIn(secreto, visto)

    def test_ea1_los_prefijos_permitidos_son_exactamente_lc_y_xdg(self):
        visto = ve_el_agente()
        self.assertEqual({k for k in visto if k.startswith(('LC_', 'XDG_'))}, {'LC_ALL', 'XDG_CONFIG_HOME'})
        self.assertNotIn('LCX_OTRA', visto)
        self.assertNotIn('XDGX', visto)
        self.assertNotIn('path', visto)  # los nombres distinguen mayúsculas

    def test_ea1_una_variable_permitida_que_no_existe_no_se_inventa_y_factory_agente_gana(self):
        with tempfile.TemporaryDirectory() as raiz, patch.dict(os.environ, {'PATH': '/usr/bin', 'FACTORY_AGENTE': 'otro'}, clear=True):
            _, lanzar = conductor.ejecutor(Path(raiz), 'claude-code')
            visto = json.loads(lanzar(VER, 30)[1])
        visto.pop('LC_CTYPE', None)  # lo agrega el propio Python al arrancar con el idioma «C» (PEP 538): no viene de Factory
        self.assertEqual(visto, {'PATH': '/usr/bin', 'FACTORY_AGENTE': 'claude-code'})

    def test_ea1_los_comandos_mecanicos_no_cambian(self):
        llamadas = []
        with patch.object(conductor, '_proceso', side_effect=lambda *a, **k: (llamadas.append((a, k)), (0, ''))[1]):
            correr, _ = conductor.ejecutor(RAIZ, 'claude-code')
            correr(['listar'], 5)
        (argumentos, opciones), = llamadas
        self.assertEqual((len(argumentos), opciones), (3, {}))  # sin entorno propio: hereda el de siempre


class Explicito(_te.Base):
    def lanza(self, **opciones):
        with patch.object(f, 'AGENTE', 'claude-code'):
            return f.comando_autopilot(self.ident, False, ejecutar=True, **opciones)

    def test_ea2_una_variable_entregada_a_proposito_llega_en_esa_corrida_y_en_la_siguiente_no(self):
        self.assertEqual(ve_el_agente(['ANTHROPIC_API_KEY'])['ANTHROPIC_API_KEY'], 'clave')
        self.assertNotIn('ANTHROPIC_API_KEY', ve_el_agente())
        with tempfile.TemporaryDirectory() as raiz, patch.dict(os.environ, {'PATH': '/usr/bin', 'FACTORY_AGENTE': 'otro'}, clear=True):
            _, lanzar = conductor.ejecutor(Path(raiz), 'claude-code', ['FACTORY_AGENTE'])  # no se puede entregar el nombre de otro agente
            self.assertEqual(json.loads(lanzar(VER, 30)[1])['FACTORY_AGENTE'], 'claude-code')
        with tempfile.TemporaryDirectory() as raiz, patch.dict(os.environ, {'PATH': '/usr/bin'}, clear=True):  # una que no existe no se inventa
            _, lanzar = conductor.ejecutor(Path(raiz), 'claude-code', ['NO_EXISTE'])
            visto = json.loads(lanzar(VER, 30)[1])
            visto.pop('LC_CTYPE', None)
            self.assertEqual(visto, {'PATH': '/usr/bin', 'FACTORY_AGENTE': 'claude-code'})

    def test_ea2_el_comando_pasa_la_lista_al_ejecutor_y_no_guarda_nada(self):
        self.preparar()
        config = (self.root / '.factory' / 'config.json').read_bytes()
        recibido = {}

        def ejecutor(raiz, agente, entorno=()):
            recibido['entorno'] = list(entorno)
            return (lambda *a: (0, '')), (lambda *a: (0, ''))
        resultado = {'motivo': 'x', 'pasos': [], 'decision': {'accion': 'frenar', 'quien': 'persona', 'comando': None, 'instruccion': None, 'motivo': 'x', 'frenos': []},
                     'fallo': False}
        with patch.object(conductor, 'ejecutor', side_effect=ejecutor), patch.object(conductor, 'bucle', return_value=resultado):
            self.lanza(lanzar='claude -p', entorno=['ANTHROPIC_API_KEY', 'OTRA'])
            self.assertEqual(recibido['entorno'], ['ANTHROPIC_API_KEY', 'OTRA'])
            self.lanza(lanzar='claude -p')
            self.assertEqual(recibido['entorno'], [])
            # y desde la línea de comandos de verdad, con las opciones repetidas
            self.assertEqual(f.main(['--agente', 'claude-code', '--proyecto', str(self.root), 'autopilot', self.ident, '--ejecutar', '--lanzar', 'claude -p',
                                     '--entorno', 'A', '--entorno', 'B']), 0)
            self.assertEqual(recibido['entorno'], ['A', 'B'])
        self.assertEqual((self.root / '.factory' / 'config.json').read_bytes(), config)  # no se guarda nada

    def test_ea2_un_nombre_que_no_sirve_o_sin_lanzar_se_rechaza_antes_de_correr_nada(self):
        self.preparar()
        config = (self.root / '.factory' / 'config.json').read_bytes()
        with patch.object(conductor, 'ejecutor', side_effect=AssertionError('no debe correr')), patch.object(conductor, 'bucle', side_effect=AssertionError('no debe correr')):
            for malo in ('A B', '1A', '', 'A-B', 'A=B', 'ÑU', 'A;B', ' ', 'A\nB'):
                with self.subTest(nombre=malo), self.assertRaises(f.FactoryError) as e:
                    self.lanza(lanzar='claude -p', entorno=['BUENA', malo])
                self.assertIn('--entorno', str(e.exception))
            for bueno_sin_lanzar in ({'entorno': ['BUENA']},):
                with self.subTest(sin='lanzar'), self.assertRaises(f.FactoryError) as e:
                    self.lanza(**bueno_sin_lanzar)
                self.assertIn('--lanzar', str(e.exception))
        self.assertEqual((self.root / '.factory' / 'config.json').read_bytes(), config)

    def test_ea2_los_nombres_validos_pasan_el_filtro(self):
        self.preparar()
        validos = ['A', '_', 'a1', 'ANTHROPIC_API_KEY', '_X9']
        with patch.object(conductor, 'ejecutor', return_value=((lambda *a: (0, '')), (lambda *a: (0, '')))) as e, \
                patch.object(conductor, 'bucle', return_value={'motivo': 'x', 'pasos': [], 'decision': {'accion': 'frenar', 'quien': 'persona', 'comando': None,
                                                              'instruccion': None, 'motivo': 'x', 'frenos': []}, 'fallo': False}):
            self.lanza(lanzar='claude -p', entorno=validos)
        self.assertEqual(list(e.call_args.args[2]), validos)

    def test_ea2_la_opcion_existe_en_el_parser_y_es_repetible(self):
        args = f.construir_parser().parse_args(['--agente', 'a', 'autopilot', 'ID', '--ejecutar', '--lanzar', 'x', '--entorno', 'A', '--entorno', 'B'])
        self.assertEqual(args.entorno, ['A', 'B'])
        self.assertIsNone(f.construir_parser().parse_args(['autopilot', 'ID']).entorno)


class Guia(unittest.TestCase):
    def test_ea3_la_guia_filtra_el_entorno_acota_python_y_advierte_del_patron_abierto(self):
        texto = (RAIZ / 'docs' / 'modos.md').read_text(encoding='utf-8')
        bloques = re.findall(r'```[^\n]*\n(.*?)```', texto, re.DOTALL)
        ejemplo = [b for b in bloques if '--lanzar' in b and 'allowedTools' in b]
        self.assertEqual(len(ejemplo), 1)
        self.assertIn('Bash(.venv/bin/python -m unittest:*)', ejemplo[0])
        self.assertIn('Bash(.venv/bin/python tools/verificar_cambio.py:*)', ejemplo[0])
        self.assertNotIn('python:*', ''.join(bloques))  # ningún ejemplo trae el patrón abierto
        self.assertIn('`Bash(.venv/bin/python:*)`', texto)  # pero el texto lo nombra para advertir
        for frase in ('filtra el entorno', '--entorno', 'red', 'git'):
            self.assertIn(frase, texto)


if __name__ == '__main__':
    unittest.main()
