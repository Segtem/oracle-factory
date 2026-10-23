"""La documentación al día: escenarios dc1 (cuenta lo que Factory hace hoy) y dc2 (se comprueba contra la CLI), sobre los
archivos del repositorio y sobre copias con un problema puesto a propósito."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE))
sys.path.insert(0, str(SOURCE / 'tools'))
import docs_al_dia  # noqa: E402

VIEJO = ('Hoy existe una POC de CLI', 'no coordina agentes automáticamente', 'análisis con IA sigue pendiente',
         'AÚN NO IMPLEMENTADA', 'prueba de concepto')
GUIAS = {'tablero': 'docs/tablero.md', 'conocimiento': 'docs/conocimiento.md', 'agentes': 'docs/agentes.md'}


class Docs(unittest.TestCase):
    # --- dc1: la documentación cuenta lo que Factory hace hoy -------------------------------------------------------
    def test_dc1_alguien_llega_al_proyecto(self):
        readme = (SOURCE / 'README.md').read_text(encoding='utf-8')
        portada = (SOURCE / 'site/index.html').read_text(encoding='utf-8')
        for archivo in ('README.md', 'site/index.html', 'site/desde-cero.html', *[g for g in GUIAS.values()]):
            texto = (SOURCE / archivo).read_text(encoding='utf-8')
            for viejo in VIEJO:
                self.assertFalse(viejo in texto, f'{archivo} todavía dice «{viejo}»')
        # Cada herramienta tiene su guía, enlazada desde el README, y la portada enlaza las guías nuevas.
        for nombre, ruta in GUIAS.items():
            self.assertTrue((SOURCE / ruta).is_file(), ruta)
            self.assertTrue(f']({ruta})' in readme, f'el README no enlaza {ruta}')
            self.assertTrue(f'/docs/{nombre}.md' in portada, f'la portada no enlaza docs/{nombre}.md')
        for herramienta in ('oracle-factory tablero', 'oracle-factory preguntar', 'oracle-factory --proyecto RUTA mcp',
                            'oracle-factory agentes', 'oracle-factory kb', 'oracle-factory decidir-union'):
            self.assertTrue(herramienta in readme, f'el README no nombra «{herramienta}»')
        # Las guías no mandan a correr fabrica.py ni nombran un entorno de desarrollo como requisito.
        for guia in (SOURCE / 'docs').glob('*.md'):
            self.assertNotIn('fabrica.py', guia.read_text(encoding='utf-8'), guia.name)
        # El LEEME que escribe `init` en .factory/ nombra lo local de hoy.
        from oracle_factory import cli
        for carpeta in ('local/revisiones/', 'local/revisores/', 'local/rag/'):
            self.assertTrue(carpeta in cli.LEEME_FACTORY, f'el LEEME de .factory/ no nombra {carpeta}')
        # Los enlaces entre los documentos apuntan a archivos que existen.
        for documento in [SOURCE / 'README.md', *(SOURCE / 'docs').glob('*.md')]:
            for destino in docs_al_dia.ENLACE.findall(documento.read_text(encoding='utf-8')):
                if destino.startswith(('http', '#', 'mailto')):
                    continue
                ruta = (documento.parent / destino.split('#')[0]).resolve()
                self.assertTrue(ruta.exists(), f'{documento.name} enlaza {destino}, que no existe')

    # --- dc2: la documentación se comprueba contra la CLI -----------------------------------------------------------
    def copia(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        for nombre in ('README.md', 'pyproject.toml'):
            shutil.copy(SOURCE / nombre, tmp / nombre)
        shutil.copytree(SOURCE / 'docs', tmp / 'docs')
        shutil.copytree(SOURCE / 'site', tmp / 'site', ignore=shutil.ignore_patterns('*.js', '*.css', '*.svg'))
        return tmp

    def cambiar(self, tmp, archivo, antes, despues):
        ruta = tmp / archivo
        texto = ruta.read_text(encoding='utf-8')
        self.assertIn(antes, texto, archivo)
        ruta.write_text(texto.replace(antes, despues), encoding='utf-8')

    def test_dc2_un_comando_sin_documentar_otro_que_no_existe_y_otra_version(self):
        self.assertEqual(docs_al_dia.problemas(SOURCE), [])  # el repositorio está al día
        self.assertEqual(subprocess.run([sys.executable, str(SOURCE / 'tools/docs_al_dia.py')], capture_output=True,
                                        text=True).returncode, 0)
        tmp = self.copia()
        self.assertEqual(docs_al_dia.problemas(tmp), [])
        # Un subcomando que ningún documento nombra.
        for doc in [tmp / 'README.md', *(tmp / 'docs').glob('*.md')]:
            doc.write_text(doc.read_text(encoding='utf-8').replace('rehacer-generado', 'otra-cosa'), encoding='utf-8')
        self.assertEqual(docs_al_dia.problemas(tmp), ['el subcomando rehacer-generado no aparece en el README ni en docs/'])
        # Un comando que no existe, en el README y en una página de la web (con sus etiquetas).
        tmp = self.copia()
        self.cambiar(tmp, 'README.md', 'oracle-factory agentes', 'oracle-factory comando-falso')
        self.cambiar(tmp, 'site/modos.html', '<code>oracle-factory estado ID</code>', '<code>oracle-factory</code> <b>fantasma</b> ID')
        self.cambiar(tmp, 'site/index.html', 'oracle-factory --help</code>', 'oracle-factory --proyecto x inventado</code>')
        lista = docs_al_dia.problemas(tmp)
        self.assertIn('README.md: nombra «oracle-factory comando-falso», que no es un subcomando', lista)
        self.assertIn('site/index.html: nombra «oracle-factory inventado», que no es un subcomando', lista)
        self.assertIn('site/modos.html: nombra «oracle-factory fantasma», que no es un subcomando', lista)  # el texto sin etiquetas
        # Otra versión de Factory (no la de Clue, ni la del historial), en el README y en una página de la web.
        tmp = self.copia()
        self.cambiar(tmp, 'README.md', 'oracle-factory==0.1.0a13`, y', 'oracle-factory==0.1.0a9`, y')
        self.cambiar(tmp, 'site/desde-cero.html', 'Usá la 0.1.0a13', 'Usá la 0.1.0a7')
        lista = docs_al_dia.problemas(tmp)
        self.assertIn('README.md: nombra la versión 0.1.0a9; la de pyproject.toml es 0.1.0a13', lista)
        self.assertIn('site/desde-cero.html: nombra la versión 0.1.0a7; la de pyproject.toml es 0.1.0a13', lista)
        self.assertEqual([p for p in lista if '0.1.0a2' in p or '0.1.0a12' in p], [])  # Clue y el historial no cuentan
        # El historial de versiones del README («La 0.1.0aN trajo…») puede nombrar las anteriores; una plantilla, un
        # comando que no existe: la comprobación mira también docs/plantillas/.
        tmp = self.copia()
        readme = tmp / 'README.md'
        readme.write_text(readme.read_text(encoding='utf-8') + '\nLa 0.1.0a12 trajo una portada nueva; la 0.1.0a9 trajo Oracle Clue.\n', encoding='utf-8')
        self.assertEqual(docs_al_dia.problemas(tmp), [])
        (tmp / 'docs/plantillas/colaboracion/relevo.md').write_text('Corré `oracle-factory plantilla-vieja ID`.\n', encoding='utf-8')
        self.assertEqual(docs_al_dia.problemas(tmp),
                         ['docs/plantillas/colaboracion/relevo.md: nombra «oracle-factory plantilla-vieja», que no es un subcomando'])


if __name__ == '__main__':
    unittest.main()
