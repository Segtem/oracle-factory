"""La documentación al día: escenarios dc1 (cuenta lo que Factory hace hoy) y dc2 (se comprueba contra la CLI), sobre los
archivos del repositorio y sobre copias con un problema puesto a propósito."""
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE))
sys.path.insert(0, str(SOURCE / 'tools'))
import docs_al_dia  # noqa: E402

VIEJO = ('Hoy existe una POC de CLI', 'no coordina agentes automáticamente', 'análisis con IA sigue pendiente',
         'AÚN NO IMPLEMENTADA', 'prueba de concepto', 'ni ejecuta agentes, tests, sensores o revisores')
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
        herramientas = readme.split('## Las herramientas', 1)[1].split('\n## ', 1)[0]
        for apartado in re.split(r'\n\n(?=\*\*)', herramientas.strip()):
            self.assertRegex(apartado, r'\]\(docs/[^)]+\)', 'cada herramienta necesita su guía')
        # Las guías no mandan a correr fabrica.py ni nombran un entorno de desarrollo como requisito.
        for guia in [SOURCE / 'README.md', *(SOURCE / 'docs').rglob('*.md')]:
            self.assertNotIn('fabrica.py', guia.read_text(encoding='utf-8'), guia.name)
        # El LEEME que escribe `init` en .factory/ nombra lo local de hoy.
        from oracle_factory import cli
        for carpeta in ('local/revisiones/', 'local/revisores/', 'local/rag/'):
            self.assertTrue(carpeta in cli.LEEME_FACTORY, f'el LEEME de .factory/ no nombra {carpeta}')
        # Los nombres solos no alcanzan: cada carpeta debe describir lo que contiene.
        for texto in (cli.LEEME_FACTORY, (SOURCE / 'docs/estructura.md').read_text(encoding='utf-8')):
            self.assertRegex(texto, r'local/revisiones/[^;\n]*clon')
            self.assertRegex(texto, r'local/revisores/[^;\n]*pedido[^;\n]*informe')
        estructura = (SOURCE / 'docs/estructura.md').read_text(encoding='utf-8')
        self.assertRegex(estructura, r'(?m)^\s+revisores/[^\n]*pedido[^\n]*informe')
        # Los enlaces entre los documentos apuntan a archivos que existen.
        for documento in [SOURCE / 'README.md', *(SOURCE / 'docs').rglob('*.md')]:
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
        self.cambiar(tmp, 'README.md', 'oracle-factory==0.1.0a15`. Con', 'oracle-factory==0.1.0a9`. Con')
        self.cambiar(tmp, 'site/desde-cero.html', 'Usá la 0.1.0a15', 'Usá la 0.1.0a7')
        lista = docs_al_dia.problemas(tmp)
        self.assertIn('README.md: nombra la versión 0.1.0a9; la de pyproject.toml es 0.1.0a15', lista)
        self.assertIn('site/desde-cero.html: nombra la versión 0.1.0a7; la de pyproject.toml es 0.1.0a15', lista)
        self.assertEqual([p for p in lista if '0.1.0a2' in p or '0.1.0a12' in p], [])  # Clue y el historial no cuentan
        # El historial de versiones del README puede nombrar las anteriores; una plantilla, un
        # comando que no existe: la comprobación mira también docs/plantillas/.
        tmp = self.copia()
        readme = tmp / 'README.md'
        readme.write_text(readme.read_text(encoding='utf-8') + '\n## Historial de versiones\nLa 0.1.0a12 agregó una portada nueva; la 0.1.0a9 incorporó Oracle Clue.\n', encoding='utf-8')
        self.assertEqual(docs_al_dia.problemas(tmp), [])
        with readme.open('a') as out:
            out.write('\n## Uso actual\nUsá Factory 0.2.0.\n')
        self.assertIn('README.md: nombra la versión 0.2.0; la de pyproject.toml es 0.1.0a15', docs_al_dia.problemas(tmp))
        tmp = self.copia()
        (tmp / 'docs/notas-de-version.md').write_text('# Notas de versión\nLa 0.1.0 agregó cosas.\n')
        self.assertEqual(docs_al_dia.problemas(tmp), [])
        (tmp / 'docs/plantillas/colaboracion/relevo.md').write_text('Corré `oracle-factory plantilla-vieja ID`.\n', encoding='utf-8')
        self.assertEqual(docs_al_dia.problemas(tmp),
                         ['docs/plantillas/colaboracion/relevo.md: nombra «oracle-factory plantilla-vieja», que no es un subcomando'])
        # Versiones finales y de otra serie también cuentan; las dependencias no son Factory.
        for version in ('0.1.0', '0.2.0', '1.0.0', '2.0.0rc1'):
            with self.subTest(version=version):
                tmp = self.copia()
                self.cambiar(tmp, 'README.md', 'oracle-factory==0.1.0a15`. Con', f'oracle-factory=={version}`. Con')
                self.assertIn(f'README.md: nombra la versión {version}; la de pyproject.toml es 0.1.0a15', docs_al_dia.problemas(tmp))
        tmp = self.copia()
        self.cambiar(tmp, 'pyproject.toml', 'version = "0.1.0a15"', 'version = "0.2.0"')
        self.cambiar(tmp, 'README.md', 'oracle-factory==0.1.0a15`. Con', 'oracle-factory==0.3.0`. Con')
        self.assertIn('README.md: nombra la versión 0.3.0; la de pyproject.toml es 0.2.0', docs_al_dia.problemas(tmp))
        # Un nombre corto, con mayúsculas o con opciones globales válidas no debe escaparse.
        for comando, nombre in (('X', 'X'), ('x', 'x'), ('v2', 'v2'), ('test_cmd', 'test_cmd'),
                                ('--proyecto=/tmp falso', 'falso'), ('--agente=bot falso', 'falso'),
                                ('--proyecto "/tmp/con espacio" falso', 'falso')):
            with self.subTest(comando=comando):
                tmp = self.copia()
                with (tmp / 'README.md').open('a') as out:
                    out.write(f'\n`oracle-factory {comando}`\n')
                self.assertIn(f'README.md: nombra «oracle-factory {nombre}», que no es un subcomando', docs_al_dia.problemas(tmp))
        # «Por ejemplo» no documenta un comando llamado ejemplo, ni la prosa «validar» uno nuevo.
        tmp = self.copia()
        for doc in [tmp / 'README.md', *(tmp / 'docs').rglob('*.md')]:
            doc.write_text(doc.read_text().replace('oracle-factory ejemplo notas', 'oracle-factory nuevo notas'))
        self.assertIn('el subcomando ejemplo no aparece en el README ni en docs/', docs_al_dia.problemas(tmp))
        with patch.object(docs_al_dia, 'subcomandos', return_value=docs_al_dia.subcomandos() | {'validar'}):
            self.assertIn('el subcomando validar no aparece en el README ni en docs/', docs_al_dia.problemas(tmp))


if __name__ == '__main__':
    unittest.main()
