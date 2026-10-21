"""Tres defectos de Factory a la vista: escenarios av1–av3, en proyectos temporales con la CLI en proceso."""
import contextlib
import io
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_archivo as _archivo  # noqa: E402

f = _archivo.f
SPEC = ('# Capability: {c}\n\n## ADDED Requirements\n\n### Requirement: {r}\nTipo: funcional\nThe system SHALL {t}.\n\n'
        '#### Scenario: uno\n- GIVEN a\n- WHEN b\n- THEN c\n')


class Avisos(unittest.TestCase):
    setUp, escribe, git, cambio_importado = (_archivo.Archivo.setUp, _archivo.Archivo.escribe, _archivo.Archivo.git,
                                             _archivo.Archivo.cambio_importado)

    def requisitos(self):
        return sorted(p.stem for p in (self.root / 'requisitos').glob('*.requisito'))

    # --- av1: una spec de otra capacidad no se pierde en silencio ----------------------------------------------------
    def test_av1_un_cambio_con_dos_specs(self):
        ident = f.nuevo('Dos specs', 'uno')
        carpeta, estado = f.leer(ident)
        (self.root / estado['spec']).write_text(SPEC.format(c='uno', r='algo', t='do it'))
        (carpeta / 'proposal.md').write_text('# Dos specs\n\nFixture.\n')
        otra = carpeta / 'specs/dos/spec.md'
        otra.parent.mkdir(parents=True)
        otra.write_text(SPEC.format(c='dos', r='otra cosa', t='do more'))
        registro = (self.root / '.factory/cambios' / ident / 'factory.json').read_text()
        with self.escribe('1'), self.assertRaisesRegex(f.FactoryError, f'importa sólo su spec .*openspec/changes/{ident}/specs/dos/spec.md'):
            f.aprobar_spec(ident)
        self.assertEqual((self.root / '.factory/cambios' / ident / 'factory.json').read_text(), registro)
        # Anidada en specs/, o un enlace a la propia: también es otra spec, y se nombran todas, en orden.
        anidada = carpeta / 'specs/a/sub/spec.md'
        anidada.parent.mkdir(parents=True)
        anidada.write_text(SPEC.format(c='sub', r='anidada', t='hide'))
        enlace = carpeta / 'specs/b/spec.md'
        enlace.parent.mkdir()
        enlace.symlink_to(self.root / estado['spec'])
        rutas = [f'openspec/changes/{ident}/specs/{r}/spec.md' for r in ('a/sub', 'b', 'dos')]
        with self.escribe('1'), self.assertRaisesRegex(f.FactoryError, ', '.join(rutas)):
            f.aprobar_spec(ident)
        for x in (otra, anidada, enlace):
            x.unlink()
        for x in (otra.parent, anidada.parent, anidada.parent.parent, enlace.parent):
            x.rmdir()
        with self.escribe('1'):
            f.aprobar_spec(ident)
        self.assertTrue(f.leer(ident)[1]['spec_aprobada'])

    # --- av2: reimportar no deja requisitos huérfanos ----------------------------------------------------------------
    def test_av2_una_spec_aprobada_otra_vez(self):
        otro = self.cambio_importado('Otro', 'otra', SPEC.format(c='otra', r='ajeno', t='stay'))
        del_otro = self.requisitos()
        ident = self.cambio_importado('Primero', 'uno', SPEC.format(c='uno', r='algo', t='do it'))
        [viejo] = f.leer(ident)[1]['requisitos']
        _, estado = f.leer(ident)
        (self.root / estado['spec']).write_text(SPEC.format(c='uno', r='algo', t='do it better'))
        with self.escribe('1'):
            f.aprobar_spec(ident)
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            f.importar(ident)
        [nuevo] = f.leer(ident)[1]['requisitos']
        self.assertNotEqual(nuevo, viejo)
        self.assertIn(f'Quité de requisitos/ los de la importación anterior de este cambio: {viejo}', salida.getvalue())
        self.assertEqual(self.requisitos(), sorted(del_otro + [nuevo]))
        self.assertEqual(f.leer(otro)[1]['requisitos'], del_otro)
        # Reimportar la misma spec (otra aprobación de los mismos bytes) conserva sus requisitos.
        with self.escribe('1'):
            f.aprobar_spec(ident)
        f.importar(ident)
        self.assertEqual(f.leer(ident)[1]['requisitos'], [nuevo])
        self.assertEqual(self.requisitos(), sorted(del_otro + [nuevo]))

    # --- av3: un requisito que quedó sin medir se avisa a tiempo ----------------------------------------------------
    def test_av3_medidas_confirmadas_con_la_marca_todavia_puesta(self):
        ident = f.nuevo('Nota', con_ejemplo='notas')
        with self.escribe('1'):
            f.aprobar_spec(ident)
        f.importar(ident)
        rid = f.leer(ident)[1]['requisitos'][0]
        # Recién importado, sin medidas decididas, no hay nada que avisar todavía.
        self.assertEqual([a for a in f.datos_estado(ident)['avisos'] if 'sin medir' in a], [])
        # La persona decide las medidas sin quitar la marca «sin medir».
        with self.escribe('1'):
            f.medir(ident, requisito_id=rid, medidas=['notas.casos_ejecutados', 'notas.resultados'])
        [aviso] = [a for a in f.datos_estado(ident)['avisos'] if 'sin medir' in a]
        self.assertIn(f'{rid} tiene sus medidas decididas pero todavía dice «sin medir»', aviso)
        self.assertIn(f'medir {ident} --requisito {rid} --medida … --quitar-sin-medir', aviso)
        self.assertIn(f'medir {ident} --confirmar', aviso)
        self.assertNotIn('declará por qué', aviso)  # declarar el motivo deja la marca y juzgar sigue sin pasar
        texto = io.StringIO()
        with contextlib.redirect_stdout(texto), self.escribe('3'):
            f.mostrar(ident)
        self.assertIn(f'Aviso: {aviso}.', texto.getvalue())
        self.git('add', '.')
        self.git('commit', '-qm', 'producto')
        informe = self.root / 'tareas' / ident / 'revision.md'
        informe.write_text('Fixture de revisión.\n')
        with self.escribe('1'):
            f.revisar(ident, informe, 'Persona fixture', 'aprobar', 0)
        hechos = self.root / 'tareas' / ident / 'hechos.json'
        subprocess.run([sys.executable, 'examples/notas/sensor.py', '--salida', hechos], cwd=self.root, check=True, capture_output=True)
        with self.assertRaisesRegex(f.FactoryError, f'Todavía dicen «sin medir»: {rid} \\(proponé sus medidas con --quitar-sin-medir\\)'):
            f.juzgar(ident, hechos)
        # Con la marca quitada, ya no avisa.
        with self.escribe('1'):
            f.medir(ident, requisito_id=rid, medidas=['notas.casos_ejecutados', 'notas.resultados'], quitar_sin_medir=True)
        self.assertEqual([a for a in f.datos_estado(ident)['avisos'] if 'sin medir' in a], [])


if __name__ == '__main__':
    unittest.main()
