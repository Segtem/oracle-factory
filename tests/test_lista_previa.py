"""La lista previa a la revisión: escenarios lp1–lp3, con un revisor de prueba y la CLI de verdad."""
import contextlib
import io
from pathlib import Path
import re
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_agentes as _agentes  # noqa: E402
import test_archivo as _archivo  # noqa: E402
import test_revisores as _revisores  # noqa: E402
from oracle_factory import agentes, lista_previa  # noqa: E402

f = _archivo.f
SOURCE = Path(__file__).resolve().parents[1]
CLAVES = {'reusar', 'rutas', 'valores', 'paridad', 'avisos', 'pruebas', 'textos', 'evidencia', 'clase'}


class PedirRevision(unittest.TestCase):
    setUp, escribe, git, salida, archivos = (_archivo.Archivo.setUp, _archivo.Archivo.escribe, _archivo.Archivo.git,
                                             _archivo.Archivo.salida, _archivo.Archivo.archivos)
    preparar, configurar, carpeta = _revisores.Revisores.preparar, _revisores.Revisores.configurar, _revisores.Revisores.carpeta

    def pedir_y_capturar(self, **kw):
        """(lo que imprime pedir-revision, el informe que deja)."""
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            destino = f.pedir_revision(self.ident, 'prueba', base=self.base, **kw)
        return salida.getvalue(), destino

    # --- lp1: pedir una revisión muestra la lista, sin bloquear ------------------------------------------------------
    def test_lp1_la_lista_sale_antes_de_anunciar_al_revisor(self):
        self.preparar('ok')
        texto, _ = self.pedir_y_capturar()
        anuncio = texto.index('Revisor prueba (')
        for clave, pregunta in lista_previa.ITEMS:
            with self.subTest(clave=clave):
                self.assertIn(pregunta, texto)
                self.assertLess(texto.index(pregunta), anuncio)

    def test_lp1_el_revisor_se_lanza_igual_y_deja_su_informe(self):
        self.preparar('hallazgo')
        texto, destino = self.pedir_y_capturar()
        self.assertTrue(destino.is_file())
        self.assertIn('Comando: ', texto)
        self.assertEqual(len([e for e in f.leer(self.ident)[1]['eventos'] if e['accion'] == 'revision_pedida']), 1)

    def test_lp1_la_lista_se_muestra_aunque_el_revisor_falle(self):
        self.preparar('nada')  # el revisor no deja informe: la revisión se corta
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida), self.assertRaises(f.FactoryError):
            f.pedir_revision(self.ident, 'prueba', base=self.base)
        self.assertIn(lista_previa.ITEMS[0][1], salida.getvalue())

    def test_lp1_el_pedido_que_recibe_el_revisor_no_cambia(self):
        self.preparar('ok')
        _, primero = self.pedir_y_capturar()
        con = primero.with_name('prueba-1.pedido.md').read_text(encoding='utf-8')
        from unittest.mock import patch
        with patch.object(lista_previa, 'texto', return_value=''):
            sin_texto, segundo = self.pedir_y_capturar()
        sin = segundo.with_name('prueba-2.pedido.md').read_text(encoding='utf-8')
        for _, pregunta in lista_previa.ITEMS:
            self.assertNotIn(pregunta, sin_texto)  # con el texto apagado, no sale
            self.assertNotIn(pregunta, con)  # y nunca viaja en el pedido
        self.assertEqual(con.replace('prueba-1', 'prueba-N'), sin.replace('prueba-2', 'prueba-N'))


class FuenteUnica(unittest.TestCase):
    documento = (SOURCE / 'docs/lista-previa.md').read_text(encoding='utf-8') if (SOURCE / 'docs/lista-previa.md').is_file() else ''

    # --- lp2: una sola fuente ---------------------------------------------------------------------------------------------
    def test_lp2_la_lista_tiene_una_pregunta_por_clase_y_la_regla_de_la_clase(self):
        self.assertEqual({clave for clave, _ in lista_previa.ITEMS}, CLAVES)
        self.assertEqual(len({clave for clave, _ in lista_previa.ITEMS}), len(lista_previa.ITEMS))  # claves únicas
        for clave, pregunta in lista_previa.ITEMS:
            with self.subTest(clave=clave):
                self.assertTrue(pregunta.endswith('?'), pregunta)
                self.assertGreater(len(pregunta), 40)
        preguntas = dict(lista_previa.ITEMS)
        self.assertIn('ayudante', preguntas['reusar'])
        self.assertIn('clase', preguntas['clase'])

    def test_lp2_cada_pregunta_esta_en_el_documento_con_el_mismo_texto(self):
        self.assertTrue(self.documento, 'falta docs/lista-previa.md')
        for clave, pregunta in lista_previa.ITEMS:
            with self.subTest(clave=clave):
                self.assertIn(pregunta, self.documento)
        lista_previa.comprobar_documento(self.documento)  # y la comprobación lo da por bueno

    def test_lp2_una_pregunta_nueva_sin_documento_se_nombra(self):
        nueva = lista_previa.ITEMS + (('nueva', '¿Revisaste algo que el documento todavía no dice, y por qué importa?'),)
        with self.assertRaises(lista_previa.ListaPreviaInvalida) as e:
            lista_previa.comprobar_documento(self.documento, nueva)
        self.assertIn('nueva', str(e.exception))
        self.assertIn('Revisaste algo que el documento todavía no dice', str(e.exception))

    def test_lp2_varias_preguntas_faltantes_se_nombran_todas_y_un_documento_vacio_falla(self):
        with self.assertRaises(lista_previa.ListaPreviaInvalida) as e:
            lista_previa.comprobar_documento('')
        for clave, _ in lista_previa.ITEMS:
            self.assertIn(clave, str(e.exception))

    def test_lp2_el_texto_para_mostrar_trae_cada_pregunta_numerada_y_es_estable(self):
        texto = lista_previa.texto()
        self.assertEqual(texto, lista_previa.texto())
        for i, (_, pregunta) in enumerate(lista_previa.ITEMS, 1):
            self.assertIn(f'{i}. {pregunta}', texto)
        self.assertTrue(texto.endswith('\n'))
        self.assertIn('docs/lista-previa.md', texto)

    def test_lp2_el_documento_no_promete_que_bloquea(self):
        self.assertRegex(self.documento, r'(?i)no bloquea')
        self.assertNotRegex(self.documento, r'(?i)\bbloquea la revisi')


class GuiaDeLaLista(unittest.TestCase):
    setUp, git, correr = _agentes.Agentes.setUp, _agentes.Agentes.git, _agentes.Agentes.correr

    # --- lp3: la guía para agentes nombra la lista --------------------------------------------------------------------
    def test_lp3_la_guia_generada_nombra_la_lista(self):
        self.correr('init')
        self.assertEqual(self.correr('agentes').returncode, 0)
        texto = (self.root / 'AGENTS.md').read_text(encoding='utf-8')
        self.assertIn('docs/lista-previa.md', texto)
        self.assertRegex(texto, r'(?i)antes de pedir una revisión')
        self.assertIn('docs/lista-previa.md', agentes.bloque('confirmacion'))

    def test_lp3_una_guia_vieja_sin_la_mencion_se_detecta(self):
        self.correr('init')
        self.assertEqual(self.correr('agentes', '--verificar').returncode, 0)
        vieja = '\n'.join(l for l in agentes.bloque('confirmacion').splitlines() if 'lista-previa' not in l)
        self.assertNotEqual(vieja, agentes.bloque('confirmacion'))
        (self.root / 'AGENTS.md').write_text(vieja + '\n')
        r = self.correr('agentes', '--verificar')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('oracle-factory agentes', r.stdout + r.stderr)
        self.assertEqual(self.correr('agentes').returncode, 0)
        self.assertIn('docs/lista-previa.md', (self.root / 'AGENTS.md').read_text())


if __name__ == '__main__':
    unittest.main()
