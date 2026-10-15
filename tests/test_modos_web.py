"""Los modos de trabajo en la documentación y el sitio: escenarios mw1–mw2."""
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_web as _web  # noqa: E402

from oracle_factory import modos  # noqa: E402

ROOT = _web.ROOT
SECCIONES = ('modos', 'quien-decide', 'tipos', 'estado', 'cambiar', 'ejemplo', 'limites')
TITULOS_DOC = ('Los tres modos', 'Quién decide qué', 'Requisitos funcionales y no funcionales', 'Cómo leer estado',
               'Cambiar de modo', 'Un ejemplo real', 'Límites')
TEXTO = {'decide el agente': 'decide', 'el agente propone; una persona confirma': 'propone', 'sólo una persona': 'rechaza'}
FILAS_DOC = {  # la primera columna de la tabla del documento → (decisión, tipo)
    'Aceptar la propuesta y la spec (el cambio tiene algún requisito funcional)': ('spec', 'funcional'),
    'Aceptar la propuesta y la spec (todos sus requisitos son no funcionales)': ('spec', 'no funcional'),
    'Elegir las medidas de un requisito funcional': ('medidas', 'funcional'),
    'Elegir las medidas de un requisito no funcional': ('medidas', 'no funcional'),
    'Registrar la revisión (el cambio tiene algún requisito funcional)': ('revision', 'funcional'),
    'Registrar la revisión (todos sus requisitos son no funcionales)': ('revision', 'no funcional'),
    'Cerrar el cambio': ('cierre', 'cualquiera'),
}


class TablaHtml(HTMLParser):
    """La tabla de quién decide como la ve una persona: encabezados de columna, el título visible de cada fila y sus celdas.

    celdas: {(decisión, tipo, modo): texto}, con la decisión y el tipo tomados del título visible de la fila (FILAS_DOC) y el
    modo del encabezado de su columna. Si los atributos data-* dicen otra cosa, se anota en errores."""

    def __init__(self, texto):
        super().__init__()
        self.encabezados, self.celdas, self.errores = [], {}, []
        self._en_thead, self._celda, self._texto = False, None, ''
        self._atributos, self._visible, self._columna = None, None, 0
        self.feed(texto)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'thead':
            self._en_thead = True
        elif tag == 'tr':
            self._atributos, self._visible, self._columna = (a.get('data-decision'), a.get('data-tipo')), None, 0
        elif tag in ('th', 'td'):
            self._celda, self._texto = (tag, a.get('data-modo')), ''

    def handle_endtag(self, tag):
        if tag == 'thead':
            self._en_thead = False
        if tag not in ('th', 'td') or not self._celda:
            return
        texto, (_, modo_atributo) = ' '.join(self._texto.split()), self._celda
        self._celda = None
        if self._en_thead:
            self.encabezados.append(texto)
        elif tag == 'th':
            self._visible = FILAS_DOC.get(texto, (texto, None))
        elif self._visible:
            self._columna += 1
            modo = self.encabezados[self._columna] if self._columna < len(self.encabezados) else None
            if (*self._visible, modo) != (*self._atributos, modo_atributo):
                self.errores.append(f'«{texto}»: la página muestra {self._visible[0]}/{self._visible[1]} en modo {modo}; '
                                    f'los atributos dicen {self._atributos[0]}/{self._atributos[1]} en modo {modo_atributo}')
            self.celdas[(*self._visible, modo)] = texto

    def handle_data(self, data):
        if self._celda:
            self._texto += data


def tabla_del_documento(texto):
    """{(decisión, tipo, modo): texto} de la tabla Markdown de «Quién decide qué»."""
    lineas = [l for l in texto.split('## Quién decide qué', 1)[1].split('\n## ', 1)[0].splitlines() if l.startswith('|')]
    modos_ = [c.strip(' `') for c in lineas[0].strip('|').split('|')[1:]]
    celdas = {}
    for linea in lineas[2:]:
        primera, *resto = [c.strip() for c in linea.strip('|').split('|')]
        decision, tipo = FILAS_DOC.get(primera, (primera, None))
        celdas.update({(decision, tipo, m): t for m, t in zip(modos_, resto)})
    return celdas


def diferencias(celdas):
    """Lo que la tabla dice distinto de modos.via_agente, y lo que le falta o le sobra."""
    esperadas = {(d, t, m) for d, t in FILAS_DOC.values() for m in modos.MODOS}
    errores = [f'falta {d}/{t} en modo {m}' for d, t, m in sorted(esperadas - set(celdas))]
    errores += [f'sobra {d}/{t} en modo {m}' for d, t, m in sorted(set(celdas) - esperadas)]
    for (d, t, m), texto in sorted(celdas.items()):
        if (d, t, m) not in esperadas:
            continue
        codigo = modos.via_agente(m, d, ['funcional'] if t == 'cualquiera' else [t])
        dice = TEXTO.get(re.sub(r'\s+', ' ', texto).strip())
        if dice != codigo:
            errores.append(f'{d}/{t} en modo {m}: la tabla dice «{texto.strip()}», el código {codigo}')
    return errores


class ModosWeb(unittest.TestCase):
    def pagina(self):
        return _web.paginas()['modos.html']

    def textos(self):
        return (ROOT / 'site/modos.html').read_text(encoding='utf-8'), (ROOT / 'docs/modos.md').read_text(encoding='utf-8')

    # --- mw1: los modos de trabajo están explicados -------------------------------------------------------------------------
    def test_mw1_la_pagina_y_el_documento_estan_completos(self):
        pagina = self.pagina()
        self.assertEqual(sorted(set(SECCIONES) - pagina.ids), [])
        documento = self.textos()[1]
        self.assertEqual(re.findall(r'(?m)^## (.+)$', documento), list(TITULOS_DOC))
        portada = (ROOT / 'site/index.html').read_text(encoding='utf-8')
        tarjeta = next(t for t in re.findall(r'<article class="kit-item">.*?</article>', portada, re.S) if 'Modos de trabajo' in t)
        self.assertIn('href="./modos.html"', tarjeta)  # el enlace está en la tarjeta de los modos
        self.assertIn('](docs/modos.md)', (ROOT / 'README.md').read_text(encoding='utf-8'))
        texto = ' '.join(pagina.texto)
        for tema in ('confirmacion', 'funcional', 'autonomo', 'tipos_obligatorios', 'decidio', 'propuso', 'confirmo',
                     'oracle-factory modo', 'no autentica'):
            self.assertIn(tema, texto)
            self.assertIn(tema, documento)

    def test_mw1_la_pagina_se_lee_sin_javascript(self):
        pagina = self.pagina()
        self.assertEqual(pagina.lang, 'es')
        self.assertEqual(pagina.h1, 1)
        self.assertIn('index.html', [e.removeprefix('./').split('#')[0] for e in pagina.enlaces])
        self.assertGreater(len(' '.join(pagina.texto).split()), 600)

    # --- mw2: la tabla de quién decide coincide con el código ---------------------------------------------------------------
    def test_mw2_las_tablas_dicen_lo_que_hace_el_codigo(self):
        html, documento = self.textos()
        tabla = TablaHtml(html)
        self.assertEqual(tabla.encabezados, ['Decisión', 'confirmacion', 'funcional', 'autonomo'])
        self.assertEqual(tabla.errores, [])
        for celdas in (tabla.celdas, tabla_del_documento(documento)):
            self.assertEqual(len(celdas), len(FILAS_DOC) * len(modos.MODOS))
            self.assertEqual(diferencias(celdas), [])
        self.assertEqual({d for d, _ in FILAS_DOC.values()}, set(modos.DECISIONES))

    def test_mw2_una_celda_equivocada_se_detecta(self):
        html, documento = self.textos()
        esperado = ['cierre/cualquiera en modo confirmacion: la tabla dice «decide el agente», el código rechaza']
        # En la página: la celda del cierre en confirmacion, cambiada en el HTML y leída por el parser.
        celda = '<td data-modo="confirmacion">sólo una persona</td><td data-modo="funcional">sólo una persona</td>'
        self.assertEqual(html.count(celda), 1)
        mal = html.replace(celda, celda.replace('sólo una persona', 'decide el agente', 1))
        self.assertEqual(diferencias(TablaHtml(mal).celdas), esperado)
        # En el documento: la misma celda, cambiada en la tabla Markdown.
        fila = '| Cerrar el cambio | sólo una persona | sólo una persona | decide el agente |'
        self.assertEqual(diferencias(tabla_del_documento(documento.replace(fila, fila.replace('sólo una persona', 'decide el agente', 1)))),
                         esperado)
        # Una fila que falta, y en la página, columnas cambiadas de lugar o un título de fila que no corresponde.
        sin_fila = documento.replace('| Elegir las medidas de un requisito no funcional |', '| Otra cosa |')
        self.assertIn('falta medidas/no funcional en modo funcional', diferencias(tabla_del_documento(sin_fila)))
        cruzadas = html.replace('<th scope="col"><code>confirmacion</code></th><th scope="col"><code>funcional</code></th>',
                                '<th scope="col"><code>funcional</code></th><th scope="col"><code>confirmacion</code></th>')
        self.assertNotEqual(cruzadas, html)
        self.assertTrue(TablaHtml(cruzadas).errores)
        otro_titulo = html.replace('<th scope="row">Cerrar el cambio</th>', '<th scope="row">Abrir el cambio</th>')
        self.assertNotEqual(otro_titulo, html)
        self.assertTrue(TablaHtml(otro_titulo).errores)


if __name__ == '__main__':
    unittest.main()
