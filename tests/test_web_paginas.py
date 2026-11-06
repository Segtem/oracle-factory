"""Un menú, un orden de lectura y toda la documentación: escenarios wp1–wp4.
Los de navegador necesitan node, Chromium y Playwright (npm install --no-save --package-lock=false playwright@1.62.1)."""
from pathlib import Path
import os
import re
import shutil
import subprocess
import tempfile
import unittest

from tools import sitio_paginas

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which('node')
CHROMIUM = os.environ.get('CHROMIUM', '/usr/bin/chromium')
HAY = bool(NODE) and (ROOT / 'node_modules/playwright').is_dir() and Path(CHROMIUM).exists()
ORDEN = ['desde-cero.html', 'modos.html', 'colaboracion.html', 'concurrencia.html', 'documentacion.html']
PAGINAS = ['index.html'] + ORDEN


def copia(tmp: Path) -> Path:
    dest = tmp / 'repo'
    shutil.copytree(ROOT / 'site', dest / 'site')
    shutil.copytree(ROOT / 'docs', dest / 'docs')
    return dest


def leer(raiz: Path, nombre: str) -> str:
    return (raiz / 'site' / nombre).read_text(encoding='utf-8')


def menu(texto: str):
    m = re.search(r'<nav aria-label="Navegación principal">(.*?)</nav>', texto, re.S)
    return re.findall(r'<a ([^>]*)>([^<]*)</a>', m[1]) if m else []


def normal(href: str) -> str:
    return re.sub(r'^\.?/?(index\.html)?(?=#)', 'index.html', href.removeprefix('./')) if href.startswith(('#', './index.html#')) else href.removeprefix('./')


class WebPaginas(unittest.TestCase):
    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.tmp = Path(self._t.name)

    # --- wp1: el menú ---------------------------------------------------------------------------------------------------------
    def test_wp1_el_menu_es_el_mismo_en_las_seis_paginas_y_marca_la_actual(self):
        self.assertEqual(sorted(p.name for p in (ROOT / 'site').glob('*.html')), sorted(PAGINAS))
        esperado = None
        for nombre in PAGINAS:
            enlaces = menu(leer(ROOT, nombre))
            destinos = [normal(re.search(r'href="([^"]*)"', a)[1]) for a, _ in enlaces]
            for destino in destinos:
                if not destino.startswith('index.html#'):
                    self.assertTrue((ROOT / 'site' / destino).is_file(), f'{nombre}: {destino}')
            esperado = esperado or destinos
            self.assertEqual(destinos, esperado, nombre)
            marcados = [t for a, t in enlaces if 'aria-current="page"' in a]
            self.assertEqual(len(marcados), 0 if nombre == 'index.html' else 1, f'{nombre}: {marcados}')
            if nombre != 'index.html':
                self.assertEqual([normal(re.search(r'href="([^"]*)"', a)[1]) for a, _ in enlaces if 'aria-current="page"' in a], [nombre])
        self.assertEqual([d for d in esperado if not d.startswith('index.html#')], ORDEN)
        self.assertEqual([d for d in esperado if d.startswith('index.html#')],
                         ['index.html#formas', 'index.html#recorrido', 'index.html#herramientas', 'index.html#jugar', 'index.html#novedades'])

    def test_wp1_el_comprobador_acepta_el_repositorio(self):
        self.assertEqual(sitio_paginas.problemas(ROOT), [])

    def test_wp1_un_bloque_editado_a_mano_o_una_pagina_fuera_de_la_tabla_falla(self):
        dest = copia(self.tmp)
        p = dest / 'site' / 'modos.html'
        p.write_text(p.read_text(encoding='utf-8').replace('>En equipo</a>', '>Equipo</a>', 1), encoding='utf-8')
        ps = sitio_paginas.problemas(dest)
        self.assertTrue(any('modos.html' in x and 'menu' in x for x in ps), ps)
        dest = copia(self.tmp / 'b')
        p = dest / 'site' / 'desde-cero.html'
        p.write_text(re.sub(r'<!-- pie -->.*?<!-- /pie -->', '<footer class="wrap">solo</footer>', p.read_text(encoding='utf-8'), flags=re.S), encoding='utf-8')
        self.assertTrue(any('desde-cero.html' in x and 'pie' in x for x in sitio_paginas.problemas(dest)))
        dest = copia(self.tmp / 'c')
        p = dest / 'site' / 'colaboracion.html'
        p.write_text(re.sub(r'<!-- leer -->.*?<!-- /leer -->', '', p.read_text(encoding='utf-8'), flags=re.S), encoding='utf-8')
        self.assertTrue(any('colaboracion.html' in x and 'leer' in x for x in sitio_paginas.problemas(dest)))
        dest = copia(self.tmp / 'f')
        for nombre, bloque in (('index.html', 'leer'), ('modos.html', 'ruta')):
            p = dest / 'site' / nombre
            p.write_text(p.read_text(encoding='utf-8').replace('</main>', f'<!-- {bloque} -->x<!-- /{bloque} --></main>', 1), encoding='utf-8')
        ps = sitio_paginas.problemas(dest)
        self.assertTrue(any('index.html' in x and 'no debería' in x for x in ps) and any('modos.html' in x and 'no debería' in x for x in ps), ps)
        dest = copia(self.tmp / 'd')
        (dest / 'site' / 'suelta.html').write_text('<!doctype html><html lang="es"><body><main></main></body></html>', encoding='utf-8')
        self.assertTrue(any('suelta.html' in x and 'tabla' in x for x in sitio_paginas.problemas(dest)))

    def test_wp1_un_enlace_roto_o_un_ancla_que_no_existe_falla_nombrando_la_pagina(self):
        dest = copia(self.tmp)
        for nombre, antes, despues in (('modos.html', 'href="./colaboracion.html"', 'href="./colaboracionn.html"'),
                                       ('desde-cero.html', 'href="./index.html#formas"', 'href="./index.html#no-existe"'),
                                       ('colaboracion.html', 'href="./concurrencia.html', 'href="./concurrenciaa.html')):
            p = dest / 'site' / nombre
            texto = p.read_text(encoding='utf-8')
            self.assertIn(antes, texto, nombre)
            p.write_text(texto.replace(antes, despues, 1), encoding='utf-8')
        ps = sitio_paginas.problemas(dest)
        for nombre, parte in (('modos.html', 'ninguna página'), ('desde-cero.html', 'ancla que no existe'), ('colaboracion.html', 'ninguna página')):
            self.assertTrue(any(x.startswith(nombre) and parte in x for x in ps), (nombre, ps))

    def test_wp1_una_query_no_hace_roto_un_enlace_y_un_id_duplicado_falla(self):
        dest = copia(self.tmp)
        p = dest / 'site' / 'modos.html'
        texto = p.read_text(encoding='utf-8')
        p.write_text(texto.replace('href="./colaboracion.html"', 'href="./colaboracion.html?ref=menu"', 1).replace('href="./desde-cero.html"', 'href="./desde-cero.html?x=1#instalar"', 1), encoding='utf-8')
        self.assertEqual([x for x in sitio_paginas.problemas_de_enlaces(dest) if x.startswith('modos.html')], [])
        p.write_text(texto.replace('href="./desde-cero.html"', 'href="./desde-cero.html?x=1#no-existe"', 1), encoding='utf-8')
        self.assertTrue(any('modos.html' in x and 'ancla' in x for x in sitio_paginas.problemas_de_enlaces(dest)))
        dest = copia(self.tmp / 'b')
        p = dest / 'site' / 'index.html'
        p.write_text(p.read_text(encoding='utf-8').replace('<main', '<p id="formas">x</p><main', 1), encoding='utf-8')
        self.assertTrue(any('index.html' in x and 'id' in x and 'formas' in x and 'dos veces' in x for x in sitio_paginas.problemas_de_enlaces(dest)))

    def test_wp1_escribir_rehace_los_bloques_y_es_idempotente(self):
        dest = copia(self.tmp)
        for nombre in PAGINAS:
            p = dest / 'site' / nombre
            p.write_text(re.sub(r'<!-- (menu|pie|leer|ruta) -->.*?<!-- /\1 -->', '', p.read_text(encoding='utf-8'), flags=re.S), encoding='utf-8')
        self.assertNotEqual(sitio_paginas.problemas(dest), [])
        sitio_paginas.escribir(dest)
        self.assertEqual(sitio_paginas.problemas(dest), [])
        antes = {n: leer(dest, n) for n in PAGINAS}
        sitio_paginas.escribir(dest)
        self.assertEqual({n: leer(dest, n) for n in PAGINAS}, antes)

    # --- wp2: el orden de lectura ---------------------------------------------------------------------------------------------
    def test_wp2_se_sigue_la_lectura_de_punta_a_punta(self):
        def vecino(nombre, rel):
            m = re.search(r'<nav class="leer"[^>]*>.*?</nav>', leer(ROOT, nombre), re.S)
            self.assertIsNotNone(m, nombre)
            return re.search(rf'<a rel="{rel}" href="\./([^"#]+)"', m[0])[1]
        camino, actual = [], 'desde-cero.html'
        while actual != 'index.html':
            camino.append(actual)
            self.assertLess(len(camino), 10)
            actual = vecino(actual, 'next')
        self.assertEqual(camino, ORDEN)
        # cada anterior y cada siguiente, uno por uno, contra el orden (el primero y el último vuelven a la portada)
        for i, nombre in enumerate(ORDEN):
            self.assertEqual(vecino(nombre, 'prev'), ORDEN[i - 1] if i else 'index.html', nombre)
            self.assertEqual(vecino(nombre, 'next'), ORDEN[i + 1] if i + 1 < len(ORDEN) else 'index.html', nombre)
        self.assertNotIn('<nav class="leer"', leer(ROOT, 'index.html'))

    def test_wp2_un_anterior_que_no_corresponde_falla(self):
        dest = copia(self.tmp)
        p = dest / 'site' / 'documentacion.html'
        p.write_text(p.read_text(encoding='utf-8').replace('<a rel="prev" href="./concurrencia.html"', '<a rel="prev" href="./modos.html"', 1), encoding='utf-8')
        self.assertIn('href="./modos.html"><span>← Anterior', p.read_text(encoding='utf-8'))
        self.assertTrue(any('documentacion.html' in x and 'leer' in x for x in sitio_paginas.problemas(dest)))

    def test_wp2_la_portada_dice_por_donde_seguir_y_el_pie_enlaza_todo(self):
        m = re.search(r'<nav class="ruta[^"]*"[^>]*>(.*?)</nav>', leer(ROOT, 'index.html'), re.S)
        self.assertIsNotNone(m)
        self.assertEqual(re.findall(r'<li><a href="\./([^"]+)">', m[1]), ORDEN)
        self.assertTrue(all(len(re.sub(r'<[^>]+>', '', li)) > 40 for li in re.findall(r'<li>(.*?)</li>', m[1], re.S)))
        self.assertIn('POR DÓNDE SEGUIR', m[1])
        for nombre in PAGINAS:
            pie = re.search(r'<footer.*?</footer>', leer(ROOT, nombre), re.S)[0]
            self.assertEqual([x for x in re.findall(r'href="\./([^"]+\.html)"', pie) if x != 'index.html'], ORDEN, nombre)

    # --- wp3: la documentación -----------------------------------------------------------------------------------------------
    def test_wp3_la_pagina_lista_las_guias_de_docs_con_su_titulo(self):
        guias = sorted(p.stem for p in (ROOT / 'docs').glob('*.md'))
        self.assertEqual(len(guias), 12)
        pagina = leer(ROOT, 'documentacion.html')
        listadas = re.findall(r'data-doc="([^"]+)"', pagina)
        self.assertEqual(sorted(listadas), guias)
        self.assertEqual(len(re.findall(r'<section class="docs-grupo"', pagina)), 4)
        for g in guias:
            titulo = (ROOT / 'docs' / f'{g}.md').read_text(encoding='utf-8').splitlines()[0].removeprefix('# ').strip()
            self.assertRegex(pagina, rf'data-doc="{g}"[^>]*>{re.escape(titulo)}</a>')

    def test_wp3_una_guia_nueva_o_un_titulo_cambiado_falla_nombrandola(self):
        dest = copia(self.tmp)
        (dest / 'docs' / 'nueva.md').write_text('# Una guía nueva\n', encoding='utf-8')
        self.assertTrue(any('nueva' in x and 'documentacion.html' in x for x in sitio_paginas.problemas(dest)))
        dest = copia(self.tmp / 'b')
        g = dest / 'docs' / 'puerta.md'
        g.write_text(g.read_text(encoding='utf-8').replace('# La puerta local de salida', '# Otra cosa', 1), encoding='utf-8')
        self.assertTrue(any('puerta' in x and 'título' in x for x in sitio_paginas.problemas(dest)))
        dest = copia(self.tmp / 'e')
        pagina = dest / 'site' / 'documentacion.html'
        texto = pagina.read_text(encoding='utf-8')
        pagina.write_text(texto.replace('</ul></section>', '<li><a href="x" data-doc="puerta">La puerta local de salida</a></li></ul></section>', 1), encoding='utf-8')
        self.assertTrue(any('dos veces' in x and 'puerta' in x for x in sitio_paginas.problemas(dest)))
        dest = copia(self.tmp / 'g')
        pagina = dest / 'site' / 'documentacion.html'
        pagina.write_text(pagina.read_text(encoding='utf-8').replace('/blob/main/docs/estructura.md', '/blob/main/docs/otra.md', 1), encoding='utf-8')
        self.assertTrue(any('estructura' in x and 'debe ser' in x for x in sitio_paginas.problemas(dest)))
        dest = copia(self.tmp / 'h')
        pagina = dest / 'site' / 'documentacion.html'
        pagina.write_text(re.sub(r'(data-doc="agentes"[^>]*>[^<]*</a>)<p>[^<]*</p>', r'\1<p></p>', pagina.read_text(encoding='utf-8'), count=1), encoding='utf-8')
        self.assertTrue(any('falta la frase' in x and 'agentes' in x for x in sitio_paginas.problemas(dest)))
        dest = copia(self.tmp / 'c')
        (dest / 'docs' / 'tests.md').unlink()
        self.assertTrue(any('tests' in x and 'no existe' in x for x in sitio_paginas.problemas(dest)))

    # --- wp4: pantalla chica ------------------------------------------------------------------------------------------------
    @unittest.skipUnless(HAY, 'hace falta node, Chromium y Playwright')
    def test_wp4_las_seis_paginas_en_360_px(self):
        r = subprocess.run([NODE, 'tests/test_web_paginas.cjs'], cwd=ROOT, capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, (r.stdout + r.stderr)[-3000:])


if __name__ == '__main__':
    unittest.main()
