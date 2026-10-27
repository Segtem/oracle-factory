"""El idioma de la propuesta y la spec de un cambio nuevo: escenarios id1–id3, en proyectos temporales."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_archivo as _archivo  # noqa: E402

f = _archivo.f
SOURCE = Path(__file__).resolve().parents[1]
ARCHIVOS = ('proposal.md', 'specs/algo/spec.md', 'design.md', 'tasks.md')
# Palabras que sólo trae el texto de un idioma: si aparecen en el otro, se mezclaron.
SOLO_ES = ('Por qué', 'Qué cambia', 'Fuera de alcance', 'Decisiones humanas', 'DEBE', 'DADO', 'CUANDO', 'ENTONCES', 'Diseño',
           'Tareas', 'Persona:', 'Agente:', 'Revisor:', 'comportamiento principal', 'caso esperado')
SOLO_EN = ('## Why', 'What changes', 'Out of scope', 'Human decisions', 'SHALL', 'GIVEN', 'WHEN', 'THEN', '# Design', '# Tasks',
           'Person:', 'Agent:', 'Reviewer:', 'main behaviour', 'expected case')
ESTRUCTURA = ('# Capability: algo', '## ADDED Requirements', '### Requirement: ', '#### Scenario: ', 'Tipo: funcional', 'TODO:')


class Idioma(unittest.TestCase):
    setUp, escribe, git, salida = (_archivo.Archivo.setUp, _archivo.Archivo.escribe, _archivo.Archivo.git,
                                   _archivo.Archivo.salida)

    def declarar(self, idioma):
        ruta = self.root / '.factory/config.json'
        datos = json.loads(ruta.read_text())
        ruta.write_text(json.dumps({**datos, 'idioma': idioma}))

    def textos(self, ident):
        carpeta = self.root / 'openspec/changes' / ident
        return {a: (carpeta / a).read_text(encoding='utf-8') for a in ARCHIVOS}

    def foto(self):
        """Todo lo que `nuevo` toca: el contenido de tareas, openspec y .factory."""
        return sorted(str(p.relative_to(self.root)) for d in ('tareas', 'openspec/changes', '.factory/cambios')
                      for p in (self.root / d).rglob('*') if (self.root / d).exists())

    # --- id1: el idioma de la plantilla ------------------------------------------------------------------------------
    def test_id1_sin_idioma_declarado_sale_en_espanol(self):
        textos = self.textos(f.nuevo('Algo nuevo', 'algo'))
        todo = '\n'.join(textos.values())
        for palabra in SOLO_ES:
            self.assertIn(palabra, todo, palabra)
        for palabra in SOLO_EN:
            self.assertNotIn(palabra, todo, palabra)
        self.assertIn('# Algo nuevo', textos['proposal.md'])

    def test_id1_el_proyecto_declara_ingles(self):
        self.declarar('en')
        textos = self.textos(f.nuevo('Algo nuevo', 'algo'))
        todo = '\n'.join(textos.values())
        for palabra in SOLO_EN:
            self.assertIn(palabra, todo, palabra)
        for palabra in SOLO_ES:
            self.assertNotIn(palabra, todo, palabra)

    def test_id1_el_cambio_elige_otro_idioma_y_el_proyecto_no_cambia(self):
        antes = (self.root / '.factory/config.json').read_text()
        en = self.textos(f.nuevo('Uno', 'algo', idioma='en'))
        self.assertIn('SHALL', en['specs/algo/spec.md'])
        self.assertEqual((self.root / '.factory/config.json').read_text(), antes)
        self.assertIn('DEBE', self.textos(f.nuevo('Dos', 'algo'))['specs/algo/spec.md'])
        self.declarar('en')
        self.assertIn('DEBE', self.textos(f.nuevo('Tres', 'algo', idioma='es'))['specs/algo/spec.md'])

    def test_id1_lo_que_exige_el_formato_no_se_traduce(self):
        for idioma in ('es', 'en'):
            spec = self.textos(f.nuevo(f'Algo {idioma}', 'algo', idioma=idioma, sufijo=f'a{idioma}'))['specs/algo/spec.md']
            for marca in ESTRUCTURA:
                self.assertIn(marca, spec, (idioma, marca))

    def test_id1_el_ejemplo_notas_no_depende_del_idioma(self):
        self.declarar('en')
        ident = f.nuevo('Nota', con_ejemplo='notas')
        spec = (self.root / 'openspec/changes' / ident / 'specs/notas/spec.md').read_bytes()
        self.assertEqual(spec, (self.root / 'examples/notas/spec.md').read_bytes())

    # --- id2: un idioma no admitido ------------------------------------------------------------------------------------
    def test_id2_un_idioma_desconocido_en_la_configuracion(self):
        for valor in ('fr', 'ES', '', 5, ['es'], None):
            self.declarar(valor)
            with self.assertRaisesRegex(f.FactoryError, 'idioma no admitido.*se admiten es y en'):
                f.config_proyecto()
            with self.assertRaisesRegex(f.FactoryError, 'idioma no admitido'):
                f.nuevo('Algo', 'algo')

    def test_id2_un_idioma_desconocido_en_la_linea_de_comandos_no_crea_nada(self):
        antes = self.foto()
        for valor in ('fr', 'EN', ''):
            with self.assertRaisesRegex(f.FactoryError, 'idioma .* no admitido: se admiten es y en; no creé nada'):
                f.nuevo('Algo', 'algo', idioma=valor)
        self.assertEqual(self.foto(), antes)

    def test_id2_por_la_cli_de_verdad(self):
        antes = self.foto()
        r = subprocess.run([sys.executable, '-c', 'import sys; from oracle_factory.cli import main; sys.exit(main())',
                            'nuevo', '--capacidad', 'algo', '--idioma', 'fr', 'Algo'], cwd=self.root, capture_output=True,
                           text=True, stdin=subprocess.DEVNULL, env={**os.environ, 'PYTHONPATH': str(SOURCE)})
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('se admiten es y en', r.stderr + r.stdout)
        self.assertEqual(self.foto(), antes)

    # --- id3: aprobar e importar en cualquier idioma -----------------------------------------------------------------
    def completar(self, ident, promesa):
        carpeta = self.root / 'openspec/changes' / ident
        for archivo in (carpeta / 'proposal.md', carpeta / 'design.md', carpeta / 'tasks.md', carpeta / 'specs/algo/spec.md'):
            texto = archivo.read_text(encoding='utf-8')
            texto = texto.replace('TODO: escribir una promesa que se pueda comprobar.', promesa)
            texto = texto.replace('TODO: write one testable promise.', promesa)
            archivo.write_text(texto.replace('TODO: ', ''), encoding='utf-8')

    def test_id3_una_spec_completa_se_aprueba_y_se_importa_en_cada_idioma(self):
        for idioma, promesa in (('es', 'guardar cada nota.'), ('en', 'save every note.')):
            ident = f.nuevo(f'Algo {idioma}', 'algo', idioma=idioma, sufijo=f'c{idioma}')
            self.completar(ident, promesa)
            with self.escribe('1'), contextlib.redirect_stderr(io.StringIO()):
                f.aprobar_spec(ident)
            f.importar(ident)
            [rid] = f.leer(ident)[1]['requisitos']
            texto = (self.root / 'requisitos' / f'{rid}.requisito').read_text()
            self.assertIn(promesa, texto)
            self.assertIn('El sistema DEBE ' if idioma == 'es' else 'The system SHALL ', texto)
            self.salida()

    def test_id3_una_plantilla_sin_completar_no_se_aprueba(self):
        for idioma in ('es', 'en'):
            ident = f.nuevo(f'Algo {idioma}', 'algo', idioma=idioma, sufijo=f'd{idioma}')
            with self.escribe('1'), self.assertRaisesRegex(f.FactoryError, 'completar.*proposal.md'):
                f.aprobar_spec(ident)
            carpeta = self.root / 'openspec/changes' / ident
            (carpeta / 'proposal.md').write_text('# Algo\n\nCompleta.\n')
            (carpeta / 'tasks.md').write_text('# Tareas\n\n- [ ] hecho\n')
            with self.escribe('1'), self.assertRaisesRegex(f.FactoryError, 'completar.*spec.md'):
                f.aprobar_spec(ident)


if __name__ == '__main__':
    unittest.main()
