"""La web y las guías al día: escenarios w1–w6 de la spec del cambio web-y-docs."""
import argparse
import contextlib
from html.parser import HTMLParser
import io
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

from oracle_factory import cli as f

ROOT = Path(__file__).resolve().parents[1]
SITIO = ROOT / 'site'
GUIAS = sorted((ROOT / 'docs').glob('*.md')) + [ROOT / 'README.md']
SECCIONES_COLABORACION = ('reparto', 'checkouts', 'decisiones', 'relevo', 'revision', 'integracion', 'cierre', 'no-probado')


class Pagina(HTMLParser):
    """Lo que las pruebas necesitan de una página: idioma, títulos, ids, enlaces, código y texto visible sin JavaScript."""

    def __init__(self, texto):
        super().__init__()
        self.lang, self.h1, self.ids, self.enlaces, self.codigo, self.texto = None, 0, set(), [], [], []
        self._en_codigo, self._en_script = 0, 0
        self.feed(texto)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html':
            self.lang = a.get('lang')
        if tag == 'h1':
            self.h1 += 1
        if 'id' in a:
            self.ids.add(a['id'])
        if tag == 'a' and a.get('href'):
            self.enlaces.append(a['href'])
        if tag in ('code', 'pre'):
            self._en_codigo += 1
            self.codigo.append('')
        if tag in ('script', 'style'):
            self._en_script += 1

    def handle_endtag(self, tag):
        if tag in ('code', 'pre'):
            self._en_codigo -= 1
        if tag in ('script', 'style'):
            self._en_script -= 1

    def handle_data(self, data):
        if self._en_script:
            return
        self.texto.append(data)
        if self._en_codigo:
            self.codigo[-1] += data


def paginas():
    return {p.name: Pagina(p.read_text(encoding='utf-8')) for p in sorted(SITIO.glob('*.html'))}


def codigo_de_guia(texto):
    """Bloques ``` y código `en línea` de un Markdown."""
    bloques = re.findall(r'```[^\n]*\n(.*?)```', texto, re.S)
    sin_bloques = re.sub(r'```.*?```', '', texto, flags=re.S)
    return bloques + re.findall(r'`([^`\n]+)`', sin_bloques)


def interfaz():
    parser = f.construir_parser()
    globales = {o for a in parser._actions for o in a.option_strings}
    sub = next(a for a in parser._actions if isinstance(a, argparse._SubParsersAction))
    return globales, {nombre: {o for a in p._actions for o in a.option_strings} for nombre, p in sub.choices.items()}


def comandos_nombrados(fragmento):
    """[(subcomando, [opciones])] de cada `oracle-factory …` o `fabrica.py …` del fragmento."""
    encontrados = []
    fragmento = re.sub(r'\\\n\s*', ' ', fragmento)  # una línea continuada con barra invertida es un solo comando
    for linea in fragmento.splitlines():
        for m in re.finditer(r'(?:oracle-factory|fabrica\.py)((?:[ \t]+[^\s|;#`]+)+)', linea):
            tokens, sub, opciones, i = m[1].split(), None, [], 0
            while i < len(tokens):
                t = tokens[i]
                if sub is None and t in ('--proyecto', '--agente'):
                    i += 2
                    continue
                if sub is None and t.startswith('-'):
                    opciones.append(t)
                elif sub is None:
                    sub = t
                elif t.startswith('--'):
                    opciones.append(t.split('=')[0])
                i += 1
            if sub is not None:
                encontrados.append((sub, opciones))
    return encontrados


class Web(unittest.TestCase):
    # --- w1: la página de colaboración ------------------------------------------------------------------------------
    def test_w1_pagina_de_colaboracion_enlazada_y_completa(self):
        todas = paginas()
        self.assertIn('colaboracion.html', todas)
        self.assertTrue(any(e.removeprefix('./').split('#')[0] == 'colaboracion.html' for e in todas['index.html'].enlaces))
        colaboracion = todas['colaboracion.html']
        self.assertEqual(sorted(set(SECCIONES_COLABORACION) - colaboracion.ids), [])
        texto = ' '.join(colaboracion.texto)
        self.assertIn('no se probó', texto.lower())  # lo no probado con personas se dice

    # --- w2: el sitio cuenta lo que trae la versión publicada ---------------------------------------------------------
    def test_w2_el_sitio_cuenta_la_version_publicada(self):
        version = f.__version__
        todas = paginas()
        guia = ' '.join(todas['desde-cero.html'].texto)
        self.assertIn(f'oracle-factory=={version}', guia)
        sitio = ' '.join(t for p in todas.values() for t in p.texto)
        for tema in ('--agente', 'modo', 'revisión guiada', '.factory/', 'openspec/specs/', 'resumen', 'glow -p'):
            self.assertTrue(tema in sitio, tema)

    # --- w3: lo que la web nombra existe ------------------------------------------------------------------------------
    def test_w3_los_comandos_nombrados_existen(self):
        globales, subcomandos = interfaz()
        fuentes = [(n, c) for n, p in paginas().items() for c in p.codigo]
        fuentes += [(g.name, c) for g in GUIAS for c in codigo_de_guia(g.read_text(encoding='utf-8'))]
        faltan = []
        for nombre, fragmento in fuentes:
            for sub, opciones in comandos_nombrados(fragmento):
                if sub not in subcomandos and sub not in globales:
                    faltan.append(f'{nombre}: oracle-factory {sub}')
                    continue
                faltan += [f'{nombre}: oracle-factory {sub} {o}' for o in opciones
                           if o not in subcomandos.get(sub, set()) | globales]
        self.assertEqual(faltan, [])

    def test_w3_la_comprobacion_detecta_un_comando_inexistente(self):
        self.assertEqual(comandos_nombrados('oracle-factory --proyecto x comando-inexistente --opcion'),
                         [('comando-inexistente', ['--opcion'])])
        self.assertEqual(comandos_nombrados('oracle-factory \\\n  --proyecto . nuevo --capacidad notas'),
                         [('nuevo', ['--capacidad'])])  # continuada con barra invertida

    def test_w3_los_enlaces_internos_resuelven(self):
        todas = paginas()
        rotos = []
        for nombre, pagina in todas.items():
            for enlace in pagina.enlaces:
                if re.match(r'^[a-z]+:', enlace) or enlace.startswith('//'):
                    continue  # externos
                archivo, _, ancla = enlace.removeprefix('./').partition('#')
                destino = nombre if not archivo else archivo
                if destino not in todas and not (SITIO / destino).exists():
                    rotos.append(f'{nombre}: {enlace}')
                elif ancla and destino in todas and ancla not in todas[destino].ids:
                    rotos.append(f'{nombre}: {enlace}')
        self.assertEqual(rotos, [])

    # --- w4: guía de colaboración sin las fricciones del piloto ---------------------------------------------------------
    def test_w4_la_guia_resuelve_las_fricciones(self):
        guia = (ROOT / 'docs/colaboracion.md').read_text(encoding='utf-8')
        titulos = re.findall(r'(?m)^#{2,4} (.+)$', guia)
        for necesario in ('Archivos compartidos por diseño', 'Commit de producto y commit de evidencia',
                          'Quién actualiza el reparto', 'Dónde va el registro de una integración',
                          'Riesgos aceptados contra el candidato integrado', 'Verificarse antes de registrar'):
            self.assertTrue(any(necesario in t for t in titulos), necesario)
        self.assertIn('oracle cobertura', guia)
        self.assertIn('tareas/integracion-', guia)  # dice por qué no es un ID válido

    # --- w5: el ID de un cambio termina en un sufijo legible -------------------------------------------------------------
    def test_w5_sufijo_por_defecto_y_elegido(self):
        with tempfile.TemporaryDirectory() as tmp, self._proyecto(Path(tmp)):
            self.assertTrue(f.nuevo('Una nota con un título bastante largo', 'notas').endswith('-notas'))
            self.assertTrue(f.nuevo('Otra', 'notas', sufijo='titulos-largos').endswith('-titulos-largos'))

    def test_w5_sufijo_invalido_no_crea_nada(self):
        with tempfile.TemporaryDirectory() as tmp, self._proyecto(Path(tmp)):
            antes = sorted(p.name for p in (Path(tmp) / 'tareas').iterdir())
            for malo in ('Con_Mayusculas', '1empieza-con-numero', 'x' * 41):
                with self.assertRaises(f.FactoryError):
                    f.nuevo('Algo', 'notas', sufijo=malo)
            self.assertEqual(sorted(p.name for p in (Path(tmp) / 'tareas').iterdir()), antes)

    @contextlib.contextmanager
    def _proyecto(self, raiz):
        with patch.object(f, 'ROOT', raiz), patch.object(f, 'CHANGES', raiz / 'openspec/changes'), \
                patch.object(f, 'AGENTE', None), contextlib.redirect_stdout(io.StringIO()):
            f.inicializar()
            yield

    # --- w6: la página nueva es accesible sin JavaScript ------------------------------------------------------------------
    def test_w6_pagina_nueva_accesible_sin_javascript(self):
        colaboracion = paginas()['colaboracion.html']
        self.assertEqual(colaboracion.lang, 'es')
        self.assertEqual(colaboracion.h1, 1)
        self.assertIn('index.html', [e.removeprefix('./').split('#')[0] for e in colaboracion.enlaces])
        self.assertGreater(len(' '.join(colaboracion.texto).split()), 600)  # el contenido está en el HTML, no en un script


if __name__ == '__main__':
    unittest.main()
