"""Fricciones del piloto en la CLI: escenarios cp1–cp3, en proyectos temporales."""
import contextlib
import io
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_archivo as _archivo  # noqa: E402

f = _archivo.f


class Base(unittest.TestCase):
    pass


for _nombre in ('setUp', 'escribe', 'git', 'salida'):
    setattr(Base, _nombre, getattr(_archivo.Archivo, _nombre))


class CliPiloto(Base):
    def con_notas(self):
        """Un cambio con el ejemplo notas, aprobado e importado; devuelve el id y sus requisitos."""
        ident = f.nuevo('Nota', con_ejemplo='notas')
        with self.escribe('1'):
            f.aprobar_spec(ident)
        f.importar(ident)
        self.salida()
        return ident, f.leer(ident)[1]['requisitos']

    def medir(self, ident, rid, *medidas):
        with self.escribe('1'):
            f.medir(ident, requisito_id=rid, medidas=list(medidas))
        return self.salida()

    # --- cp1: la plantilla de un cambio nuevo trae la forma de OpenSpec ---------------------------------------------------
    def test_cp1_un_cambio_recien_creado(self):
        ident = f.nuevo('Algo nuevo', 'algo')
        carpeta = self.root / 'openspec/changes' / ident
        spec = (carpeta / 'specs/algo/spec.md').read_text()
        self.assertIn('\n## ADDED Requirements\n\n### Requirement: ', spec)
        self.assertIn('\nTipo: funcional\n', spec)
        propuesta = (carpeta / 'proposal.md').read_text()
        self.assertNotIn('Brian', propuesta)
        self.assertIn('una persona del equipo', propuesta)
        with self.escribe('1'), self.assertRaisesRegex(f.FactoryError, 'completar.*proposal.md'):
            f.aprobar_spec(ident)
        # Con la propuesta completa, la spec también se rechaza por sus propios TODO.
        (carpeta / 'proposal.md').write_text(propuesta.replace('TODO: ', ''))
        with self.escribe('1'), self.assertRaisesRegex(f.FactoryError, 'completar.*spec.md'):
            f.aprobar_spec(ident)

    def test_cp1_la_plantilla_completada_se_importa(self):
        ident = f.nuevo('Algo nuevo', 'algo')
        carpeta = self.root / 'openspec/changes' / ident
        for archivo in (carpeta / 'proposal.md', carpeta / 'design.md', carpeta / 'specs/algo/spec.md'):
            texto = archivo.read_text().replace('TODO: write one testable promise.', 'guardar cada nota.')
            archivo.write_text(texto.replace('TODO: ', ''))
        with self.escribe('1'), contextlib.redirect_stderr(io.StringIO()):
            f.aprobar_spec(ident)
        f.importar(ident)
        estado = f.leer(ident)[1]
        [rid] = estado['requisitos']
        self.assertTrue(rid.endswith('.comportamiento_principal'))
        self.assertEqual(estado['tipos'], {rid: 'funcional'})
        self.assertIn('guardar cada nota', (self.root / 'requisitos' / f'{rid}.requisito').read_text())

    # --- cp2: medir dice qué medidas reemplaza -----------------------------------------------------------------------------
    def test_cp2_reemplazar_las_medidas_de_un_requisito(self):
        ident, (uno,) = self.con_notas()
        self.medir(ident, uno, 'notas.casos_ejecutados', 'notas.resultados')
        # Otro requisito del proyecto (de otro cambio, en una subcarpeta, que Oracle también carga) que usa notas.resultados.
        otro = uno.rsplit('.', 1)[0] + '.otra_promesa'
        texto = (self.root / 'requisitos' / f'{uno}.requisito').read_text().replace(uno, otro)
        (self.root / 'requisitos' / 'otros').mkdir()
        (self.root / 'requisitos' / 'otros' / f'{otro}.requisito').write_text(
            texto.replace('notas.casos_ejecutados, notas.resultados', 'notas.resultados'))
        otra = 'proceso.' + next(m.split('.', 1)[1] for m in self.catalogo() if m.startswith('proceso.'))
        salida = self.medir(ident, uno, otra)
        self.assertIn(f'Reemplaza las medidas que tenía (notas.casos_ejecutados, notas.resultados) por: {otra}', salida)
        self.assertIn('Quedan sin ningún requisito del proyecto que las use: notas.casos_ejecutados\n', salida)
        # Con un requisito que no se puede leer, no se afirma que una medida quedó suelta: podría usarla.
        (self.root / 'requisitos' / 'roto.requisito').write_text('esto no es un requisito\n')
        salida = self.medir(ident, uno, 'notas.casos_ejecutados')
        self.assertIn(f'Reemplaza las medidas que tenía ({otra}) por: notas.casos_ejecutados', salida)
        self.assertIn(f'No pude leer 1 requisito(s) del proyecto (roto.requisito); no sé si {otra} queda(n)', salida)
        self.assertNotIn('Quedan sin', salida)
        # Lo mismo con una subcarpeta que no se puede abrir: lo que tenga adentro podría usarla.
        (self.root / 'requisitos' / 'roto.requisito').unlink()
        cerrada = self.root / 'requisitos' / 'cerrada'
        cerrada.mkdir()
        cerrada.chmod(0)
        self.addCleanup(cerrada.chmod, 0o755)
        salida = self.medir(ident, uno, otra)
        self.assertIn('No pude leer 1 requisito(s) del proyecto (cerrada/); no sé si notas.casos_ejecutados queda(n)', salida)
        self.assertNotIn('Quedan sin', salida)

    def test_cp2_la_primera_vez_no_hay_nada_que_reemplazar(self):
        ident, (uno, *_) = self.con_notas()
        salida = self.medir(ident, uno, 'notas.casos_ejecutados')
        self.assertIn('Asociación guardada', salida)
        self.assertNotIn('Reemplaza', salida)
        self.assertNotIn('Quedan sin', salida)
        salida = self.medir(ident, uno, 'notas.resultados', 'notas.casos_ejecutados')  # agregar sin sacar: no queda ninguna suelta
        self.assertIn('Reemplaza las medidas que tenía (notas.casos_ejecutados)', salida)
        self.assertNotIn('Quedan sin', salida)

    # --- cp3: medir --listar separa las medidas del proyecto de las del catálogo base ------------------------------------
    def test_cp3_un_proyecto_con_medidas_propias(self):
        ident, _ = self.con_notas()
        f.medir(ident, listar_opciones=True)
        salida = self.salida()
        proyecto, base = salida.split('Medidas del proyecto:\n', 1)[1].split('Del catálogo base de Oracle (', 1)
        for mid in ('notas.casos_ejecutados', 'notas.resultados'):  # con archivo, umbral, ámbito y alcance
            self.assertRegex(proyecto, rf'{mid}\n  Archivo: .+\n  Umbral: .+ · según .+\n  Ámbito: universal\n  Alcance: .+\n')
        self.assertNotIn('meta.', proyecto)
        lineas = [l for l in base.splitlines()[1:] if l.startswith('  ') and not l.startswith('   ')]
        cantidad = int(base.split(';', 1)[0])
        ids = [l.split(' · ', 1)[0].strip() for l in lineas[:cantidad]]
        self.assertEqual(len(ids), cantidad)
        self.assertTrue(all(i.split('.')[0] in ('meta', 'proceso', 'simulacion') for i in ids), ids)
        self.assertNotIn('  Archivo: ', base.split('La persona elige')[0])  # una línea cada una, sin detalle
        self.assertNotIn('notas.', base)

    def catalogo(self):
        from oracle_metalenguaje.nucleo.proyecto import resolver, catalogo_efectivo
        return catalogo_efectivo(resolver(['--proyecto', str(self.root)]))


if __name__ == '__main__':
    unittest.main()
