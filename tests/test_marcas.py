"""El comprobador del sitio detecta bloques marcados duplicados (WPG-007): escenarios ma1, sobre copias del sitio."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from test_web_paginas import ROOT, copia  # noqa: E402
from tools import sitio_paginas  # noqa: E402


class MarcasDuplicadas(unittest.TestCase):
    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.addCleanup(self._t.cleanup)
        self.dest = copia(Path(self._t.name))

    def cambiar(self, pagina, viejo, nuevo):
        p = self.dest / 'site' / pagina
        texto = p.read_text(encoding='utf-8')
        self.assertEqual(texto.count(viejo), 1, viejo)
        p.write_text(texto.replace(viejo, nuevo), encoding='utf-8')

    def dichos(self, pagina, bloque):
        return [x for x in sitio_paginas.problemas(self.dest) if x.startswith(pagina) and f'«{bloque}»' in x and 'más de una vez' in x]

    def test_ma1_una_segunda_pareja_alterada_falla_nombrando_la_pagina_y_el_bloque(self):
        self.cambiar('modos.html', '</main>', '<!-- menu --><nav>otro</nav><!-- /menu --></main>')
        self.assertEqual(len(self.dichos('modos.html', 'menu')), 1, sitio_paginas.problemas(self.dest))

    def test_ma1_una_apertura_o_un_cierre_repetidos_fallan(self):
        self.cambiar('desde-cero.html', '<!-- pie -->', '<!-- pie --><!-- pie -->')
        self.assertTrue(self.dichos('desde-cero.html', 'pie'))
        self.setUp()
        self.cambiar('desde-cero.html', '<!-- /pie -->', '<!-- /pie --><!-- /pie -->')
        self.assertTrue(self.dichos('desde-cero.html', 'pie'))

    def test_ma1_cada_bloque_generado_se_vigila(self):
        for pagina, bloque in (('index.html', 'ruta'), ('colaboracion.html', 'leer'), ('modos.html', 'menu'), ('modos.html', 'pie')):
            with self.subTest(pagina=pagina, bloque=bloque):
                self.setUp()
                self.cambiar(pagina, '</main>', f'<!-- {bloque} -->x<!-- /{bloque} --></main>')
                self.assertTrue(self.dichos(pagina, bloque), sitio_paginas.problemas(self.dest))

    def test_ma1_un_bloque_que_la_pagina_no_debe_tener_y_viene_repetido_falla(self):
        self.cambiar('index.html', '</main>', '<!-- leer -->x<!-- /leer --><!-- leer -->y<!-- /leer --></main>')
        ps = [x for x in sitio_paginas.problemas(self.dest) if x.startswith('index.html') and 'leer' in x]
        self.assertTrue(ps)
        self.assertTrue(self.dichos('index.html', 'leer'), ps)

    def test_ma1_el_sitio_actual_no_tiene_ni_un_duplicado(self):
        self.assertEqual(sitio_paginas.problemas(ROOT), [])
        self.assertEqual([x for x in sitio_paginas.problemas(self.dest) if 'más de una vez' in x], [])


if __name__ == '__main__':
    unittest.main()
