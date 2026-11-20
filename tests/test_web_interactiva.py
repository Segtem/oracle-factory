"""La web se entiende sola: escenarios wi1–wi4 de la spec del cambio web-interactiva.

Los de HTML se leen sin ejecutar scripts; los de navegador corren tests/test_web_interactiva.cjs en Chromium con Playwright
(npm install --no-save --package-lock=false playwright@1.62.1)."""
from html.parser import HTMLParser
from pathlib import Path
import os
import re
import shutil
import subprocess
import unittest

from oracle_factory import cli as f
from test_web import comandos_nombrados, interfaz

ROOT = Path(__file__).resolve().parents[1]
SITIO = ROOT / 'site'
NODE = shutil.which('node')
CHROMIUM = os.environ.get('CHROMIUM', '/usr/bin/chromium')
HAY = bool(NODE) and (ROOT / 'node_modules/playwright').is_dir() and Path(CHROMIUM).exists()
PASOS = ['pedido', 'spec', 'aprobacion', 'medidas', 'codigo', 'evidencia', 'revision', 'juicio', 'cierre']
DE_PERSONA = {'aprobacion', 'medidas', 'revision', 'cierre'}


class Arbol(HTMLParser):
    """Un árbol mínimo del HTML, sin ejecutar scripts: cada nodo con su etiqueta, atributos, hijos y texto."""

    VACIAS = {'meta', 'link', 'br', 'img', 'input', 'hr', 'source', 'path', 'rect'}

    def __init__(self, texto):
        super().__init__()
        self.raiz = {'tag': 'raiz', 'a': {}, 'hijos': [], 'texto': ''}
        self.pila = [self.raiz]
        self.feed(texto)

    def handle_starttag(self, tag, attrs):
        nodo = {'tag': tag, 'a': dict(attrs), 'hijos': [], 'texto': ''}
        self.pila[-1]['hijos'].append(nodo)
        if tag not in self.VACIAS:
            self.pila.append(nodo)

    def handle_startendtag(self, tag, attrs):
        self.pila[-1]['hijos'].append({'tag': tag, 'a': dict(attrs), 'hijos': [], 'texto': ''})

    def handle_endtag(self, tag):
        for i in range(len(self.pila) - 1, 0, -1):
            if self.pila[i]['tag'] == tag:
                del self.pila[i:]
                return

    def handle_data(self, data):
        self.pila[-1]['hijos'].append(data)


def nodos(n, pred=lambda x: True):
    for h in n['hijos']:
        if isinstance(h, dict):
            if pred(h):
                yield h
            yield from nodos(h, pred)


def texto(n):
    if n['tag'] in ('script', 'style'):
        return ''
    return ''.join(h if isinstance(h, str) else texto(h) for h in n['hijos'])


def plano(t):
    return re.sub(r'\s+', ' ', t).strip()


def clases(n):
    return n['a'].get('class', '').split()


def portada():
    return Arbol((SITIO / 'index.html').read_text(encoding='utf-8')).raiz


def por_id(raiz, ident):
    return next(nodos(raiz, lambda x: x['a'].get('id') == ident))


def comandos_que_faltan(fragmentos):
    globales, subcomandos = interfaz()
    faltan = []
    for fragmento in fragmentos:
        for sub, opciones in comandos_nombrados(fragmento):
            if sub not in subcomandos:
                faltan.append(f'oracle-factory {sub}')
            faltan += [f'oracle-factory {sub} {o}' for o in opciones if o not in subcomandos.get(sub, set()) | globales]
    return faltan


def correr(*args):
    r = subprocess.run([NODE, *args], cwd=ROOT, capture_output=True, text=True, timeout=300)
    return r.returncode, r.stdout + r.stderr


class SinJavascript(unittest.TestCase):
    # --- wi1: el recorrido se lee como una lista ---------------------------------------------------------------------
    def test_wi1_sin_javascript_estan_los_nueve_pasos_con_actor_y_comando(self):
        camino = por_id(portada(), 'camino-pasos')
        self.assertEqual(camino['tag'], 'ol')
        pasos = [h for h in camino['hijos'] if isinstance(h, dict)]
        self.assertEqual([p['a'].get('data-paso') for p in pasos], PASOS)
        for p in pasos:
            actor = next(nodos(p, lambda x: 'actor' in clases(x)))
            self.assertGreater(len(plano(texto(actor))), 8, p['a']['data-paso'])
            codigo = [texto(c) for c in nodos(p, lambda x: x['tag'] == 'code')]
            self.assertTrue(any('oracle-factory' in c for c in codigo), p['a']['data-paso'])
            queda = next(nodos(p, lambda x: 'queda' in clases(x)))
            self.assertGreater(len(plano(texto(queda))), 20, p['a']['data-paso'])
            self.assertNotIn('hidden', p['a'])  # el HTML los muestra todos; el script es el que oculta
            persona = 'decision-persona' in clases(p)
            self.assertEqual(persona, p['a']['data-paso'] in DE_PERSONA, p['a']['data-paso'])
            if persona:  # la marca se lee también como texto, no sólo como color
                self.assertIn('Decisión de una persona', plano(texto(p)))
        self.assertEqual(comandos_que_faltan([texto(c) for c in nodos(camino, lambda x: x['tag'] == 'code')]), [])

    # --- wi3: lo primero que se lee ----------------------------------------------------------------------------------
    def test_wi3_la_primera_seccion_dice_que_es_para_quien_y_tres_pasos(self):
        main = next(nodos(portada(), lambda x: x['tag'] == 'main'))
        primera = next(h for h in main['hijos'] if isinstance(h, dict))
        self.assertEqual(primera['a'].get('id'), 'empezar')
        t = plano(texto(primera))
        self.assertIn('Oracle Factory es', t)
        self.assertIn('Te sirve si', t)
        self.assertIn('Todavía no te sirve si', t)
        for lista in ('para-quien-si', 'para-quien-no'):
            self.assertGreaterEqual(len([x for x in por_id(primera, lista)['hijos'] if isinstance(x, dict)]), 3, lista)
        pasos = [h for h in por_id(primera, 'tres-pasos')['hijos'] if isinstance(h, dict)]
        self.assertEqual(len(pasos), 3)
        for p in pasos:
            codigo = [texto(c) for c in nodos(p, lambda x: x['tag'] == 'code')]
            self.assertTrue(comandos_nombrados('\n'.join(codigo)), codigo)
            self.assertEqual(comandos_que_faltan(codigo), [])
        instalar = texto(next(nodos(pasos[0], lambda x: x['tag'] == 'code')))
        from tools.docs_al_dia import versiones_admitidas
        publicada = next(iter(versiones_admitidas(ROOT, f.__version__) - {f.__version__}), f.__version__)
        self.assertIn(f'oracle-factory=={publicada}', instalar)  # instala la última versión publicada
        # Antes de cualquier otro contenido: ninguna otra sección del main va antes.
        self.assertEqual([h['a'].get('id') for h in main['hijos'] if isinstance(h, dict)][:3], ['empezar', 'camino', 'ejemplos'])

    # --- wi2: los ejemplos, también sin JavaScript --------------------------------------------------------------------
    def test_wi2_cada_ejemplo_tiene_su_comando_su_respuesta_y_su_version_en_texto(self):
        ejemplos = por_id(portada(), 'ejemplos')
        for ident, comando, respuesta in (
                ('ej-romper', 'oracle-factory --agente claude-code evidencia ID', 'Hechos producidos por Factory'),
                ('ej-sensor', 'oracle-factory aprobar-sensor', 'el sensor declarado no es uno que haya aprobado una persona'),
                ('ej-mutacion', 'oracle-factory --agente claude-code evidencia ID', '"porcentaje": 60')):
            ej = por_id(ejemplos, ident)
            codigo = [plano(texto(c)) for c in nodos(ej, lambda x: x['tag'] == 'code')]
            self.assertIn(comando, codigo, ident)
            self.assertIn(respuesta, texto(ej), ident)
        # Los dos estados de «rompé el código» y de «cambiá el sensor» están escritos en el HTML.
        romper = plano(texto(por_id(ejemplos, 'ej-romper')))
        self.assertIn('return bool(titulo.strip())', romper)
        self.assertIn('return bool(titulo)', romper)
        self.assertIn('Oracle no confirmó cada requisito', romper)
        sensor = plano(texto(por_id(ejemplos, 'ej-sensor')))
        self.assertIn('Sensor aprobado por', sensor)
        self.assertIn('es de una persona, sin --agente', sensor)
        tabla = por_id(ejemplos, 'mutacion-tabla')
        self.assertEqual(tabla['tag'], 'table')
        filas = list(nodos(tabla, lambda x: x['tag'] == 'tr' and 'data-mata' in x['a']))
        self.assertEqual(len(filas), 5)

    def test_wi2_los_numeros_de_la_mutacion_salen_de_correr_el_codigo_mostrado(self):
        # Hallazgo WI-MUTACION-MARCAS-FIJAS de codex: la tabla no se copia de ningún lado. Esta prueba toma el código que
        # muestra la página y las pruebas que arma portada.js, aplica cada mutante y corre cada prueba contra él.
        ejemplo = por_id(por_id(portada(), 'ejemplos'), 'ej-mutacion')
        [codigo] = [texto(n) for n in nodos(ejemplo, lambda x: x['tag'] == 'pre')
                    if 'def puede_guardar' in texto(n)]
        js = (SITIO / 'portada.js').read_text(encoding='utf-8')
        cuerpo = re.search(r"var PRUEBAS = \{(.*?)\};", js, re.S).group(1)
        pruebas = dict(re.findall(r"(\w+): '(self\.assert\w+\(.*?\))'", cuerpo))
        self.assertEqual(set(pruebas), {'vacio', 'una_letra', 'con_texto', 'justo_80', 'largo_81'})
        reemplazos = {'80 → 81': ('maximo=80', 'maximo=81'), 'and → or': (' and ', ' or '),
                      '> → <=': ('> 0', '<= 0'), '<= → >': ('<= maximo', '> maximo'), '0 → 1': ('> 0', '> 1')}

        def mata(fuente, prueba):
            espacio = {}
            exec(fuente, espacio)
            caso = unittest.TestCase()
            try:
                eval(prueba, {'self': caso, 'puede_guardar': espacio['puede_guardar']})
            except AssertionError:
                return True
            return False

        for nombre, prueba in pruebas.items():
            self.assertFalse(mata(codigo, prueba), f'{nombre} tiene que pasar con el código original')
        medido = {}
        for etiqueta, (viejo, nuevo) in reemplazos.items():
            self.assertEqual(codigo.count(viejo), 1, etiqueta)
            mutante = codigo.replace(viejo, nuevo)
            for nombre, prueba in pruebas.items():
                if mata(mutante, prueba):
                    medido.setdefault(nombre, set()).add(etiqueta)
        tabla = por_id(ejemplo, 'mutacion-tabla')
        mutantes = {m['a']['data-mutante']: plano(texto(m)) for m in nodos(tabla, lambda x: 'data-mutante' in x['a'])}
        self.assertEqual(set(mutantes.values()), set(reemplazos))
        filas = {x['a']['data-prueba']: {mutantes[m] for m in x['a']['data-mata'].split()}
                 for x in nodos(tabla, lambda x: x['tag'] == 'tr' and 'data-mata' in x['a'])}
        self.assertEqual(filas, medido)
        self.assertNotIn('mutar_cambio', plano(texto(tabla)))

class SinRecursosDeAfuera(unittest.TestCase):
    # --- wi4: lo que cargan las páginas ------------------------------------------------------------------------------
    def test_wi4_ninguna_pagina_carga_recursos_de_otro_dominio(self):
        afuera = []
        for p in sorted(SITIO.glob('*.html')):
            for n in nodos(Arbol(p.read_text(encoding='utf-8')).raiz):
                for attr in ('src', 'srcset', 'poster', 'data'):
                    if re.match(r'^(https?:)?//', n['a'].get(attr) or ''):
                        afuera.append(f'{p.name}: <{n["tag"]} {attr}>')
                if n['tag'] == 'link' and re.match(r'^(https?:)?//', n['a'].get('href') or ''):
                    afuera.append(f'{p.name}: <link href>')
        for p in sorted([*SITIO.glob('*.css'), *SITIO.glob('*.js')]):
            if re.search(r'url\(\s*["\']?(https?:)?//|@import|fetch\(|import\(', p.read_text(encoding='utf-8')):
                afuera.append(p.name)
        self.assertEqual(afuera, [])

    def test_wi4_los_comandos_existen_y_los_limites_se_dicen(self):
        raiz = portada()
        nuevas = [por_id(raiz, i) for i in ('empezar', 'camino', 'ejemplos')]
        codigo = [texto(c) for s in nuevas for c in nodos(s, lambda x: x['tag'] in ('code', 'pre'))]
        self.assertEqual(comandos_que_faltan(codigo), [])
        js = (SITIO / 'portada.js').read_text(encoding='utf-8')
        self.assertEqual(comandos_que_faltan([s.replace('\\n', '\n') for s in re.findall(r"'([^'\n]*oracle-factory[^'\n]*)'", js)]), [])
        t = plano(texto(por_id(raiz, 'ejemplos'))).lower()
        self.assertIn('el sensor es código del proyecto', t)
        # publicada-a20: la aprobación del sensor puede firmarse, pero cada corrida no lleva firma propia.
        self.assertIn('cada ejecución del sensor sigue sin firma propia', t)
        # La versión final de evidencia no acepta argumentos para el sensor: ningún «evidencia ID -- …».
        self.assertNotRegex(' '.join(codigo), r'evidencia\s+\S+\s+--(\s|$)')

    def test_wi4_cada_dibujo_tiene_su_texto_alternativo(self):
        raiz = portada()
        for s in ('empezar', 'camino', 'ejemplos'):
            escenas = list(nodos(por_id(raiz, s), lambda x: 'pixel-scene' in clases(x)))
            self.assertTrue(escenas, s)
            for e in escenas:
                self.assertEqual(e['a'].get('role'), 'img', e['a'])
                self.assertGreater(len(e['a'].get('aria-label', '')), 30, e['a'])


@unittest.skipUnless(HAY, 'hace falta node, Chromium y Playwright en node_modules')
class EnElNavegador(unittest.TestCase):
    def escenario(self, nombre):
        codigo, salida = correr('tests/test_web_interactiva.cjs', nombre)
        self.assertEqual(codigo, 0, salida[-3000:])

    def test_wi1_avanzar_y_retroceder(self):
        self.escenario('avanzar_y_retroceder')

    def test_wi1_con_el_teclado(self):
        self.escenario('con_el_teclado')

    def test_wi1_sin_javascript_en_el_navegador(self):
        self.escenario('sin_javascript')

    def test_wi2_romper_el_codigo(self):
        self.escenario('romper_el_codigo')

    def test_wi2_cambiar_el_sensor(self):
        self.escenario('cambiar_el_sensor')

    def test_wi2_la_mutacion(self):
        self.escenario('la_mutacion')

    def test_wi2_copiar_un_comando(self):
        self.escenario('copiar_un_comando')

    def test_wi3_lo_primero_que_se_ve(self):
        self.escenario('lo_primero_que_se_ve')

    def test_wi4_accesible(self):
        self.escenario('accesible')

    def test_wi4_sin_recursos_de_afuera_en_el_navegador(self):
        self.escenario('sin_recursos_de_afuera')


if __name__ == '__main__':
    unittest.main()
