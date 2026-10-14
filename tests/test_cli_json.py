"""estado, donde y resumen en JSON: escenarios cj1–cj3 de la spec, sobre repositorios temporales."""
import contextlib
import io
import json
import os
from pathlib import Path
import re
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_autoproduccion as _ap  # noqa: E402

f = _ap.f
REFERENCIA = Path(__file__).resolve().parent / 'datos' / 'cli_texto'


class CliJson(_ap.Base):
    def setUp(self):
        super().setUp()
        p = _ap.clue_acepta(); p.__enter__(); self.addCleanup(p.__exit__, None, None, None)

    cambio_medido = _ap.Autoproduccion.cambio_medido
    head = _ap.Autoproduccion.head
    carpeta = _ap.Autoproduccion.carpeta
    producir_evidencia = _ap.Autoproduccion.producir_evidencia

    def cambio_revisado(self, hallazgos=()):
        """Un cambio medido, con evidencia, un informe de codex y la revisión aprobada por la persona (acepta cada hallazgo)."""
        with contextlib.redirect_stdout(io.StringIO()):
            ident = self.cambio_medido()
        self.producir_evidencia(ident)
        carpeta = self.carpeta(ident)
        (carpeta / 'revision').mkdir(parents=True)
        (carpeta / 'revision' / 'codex-1.json').write_text(json.dumps(_ap.informe_clue(self.head(), list(hallazgos))))
        (carpeta / 'clue').mkdir()
        (carpeta / 'clue' / 'paquete.json').write_text(json.dumps({
            'schema_version': 'oracle-clue.bundle/v1', 'repo': str(self.root), 'diff_sha256': 'd' * 64, 'context_sha256': 'c' * 64,
            'files': [{'file': 'examples/notas/notas.py'}]}))
        with self.escribe('1'), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            f.revisar_paso_a_paso(ident)  # cada hallazgo: aceptar con motivo armado; completa; aprobar; motivo armado
        self.git('add', '.')
        self.git('commit', '-qm', 'revisión')
        return ident

    def correr(self, *argv):
        """(código, stdout, stderr) de la CLI, sin terminal: nada que preguntar."""
        salida, errores = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(errores):
            codigo = f.main(['--proyecto', str(self.root), *argv])
        return codigo, salida.getvalue(), errores.getvalue()

    def json_de(self, *argv):
        codigo, salida, errores = self.correr(*argv)
        self.assertEqual(codigo, 0, errores)
        return json.loads(salida)

    # --- cj1: estado se lee como JSON --------------------------------------------------------------------------------------
    def test_cj1_un_cambio_en_revision(self):
        ident = self.cambio_revisado()
        antes = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file() and '.git' not in p.parts}
        with self.escribe('1') as entrada:
            datos = self.json_de('estado', ident, '--json')
        entrada.assert_not_called()  # no ofrece ejecutar nada
        self.assertEqual(antes, {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file() and '.git' not in p.parts})
        self.assertEqual((datos['esquema'], datos['id'], datos['fase'], datos['modo']),
                         ('oracle-factory.estado/1', ident, 'revision_aprobada', f.modo_de(f.leer(ident)[1])))
        medido = next(r for r in datos['requisitos'] if r['medidas'])
        self.assertEqual(medido['medidas'], ['notas.casos_ejecutados', 'notas.resultados'])
        self.assertEqual((medido['decision']['actor'], medido['decision']['tipo_actor']), (f.actor()['actor'], 'persona'))
        rev = datos['revision']
        self.assertEqual((rev['decision'], rev['hallazgos_abiertos'], rev['vigente']), ('aprobar', 0, True))
        self.assertEqual(rev['head'], f.leer(ident)[1]['revision']['contexto']['head'])
        self.assertEqual(datos['decisiones']['revision']['motivo'], f.leer(ident)[1]['revision']['motivo'])
        self.assertEqual(datos['decisiones']['spec']['tipo_actor'], 'persona')
        self.assertEqual(datos['proximo_paso'], f.proximo_paso(ident))
        self.assertEqual(datos['candidato'], f.candidato_vigente(ident))
        self.assertIsInstance(datos['pendientes'], list)
        self.assertEqual(datos['aceptados'], [])
        self.assertIsNone(datos['oracle'])
        # Un registro anterior a los modos guarda al actor en «por»: el JSON lo muestra igual que el texto.
        carpeta, estado = f.leer(ident)
        estado['spec_aprobada'] = {'por': 'Alguien de antes', 'cuando': '2026-10-01T00:00:00+00:00'}
        f.guardar(carpeta, estado)
        self.assertEqual(self.json_de('estado', ident, '--json')['decisiones']['spec']['actor'], 'Alguien de antes')

    def test_cj1_la_revision_vence(self):
        ident = self.cambio_revisado()
        hechos = self.carpeta(ident, f.candidato_vigente(ident)) / 'evidencia' / 'hechos.json'
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            f.juzgar(ident, hechos)
        datos = self.json_de('estado', ident, '--json')
        self.assertEqual((datos['oracle']['codigo'], datos['oracle']['vigente']), (0, True))
        self.assertEqual(datos['oracle']['head'], f.leer(ident)[1]['oracle']['contexto']['head'])
        # Los hechos juzgados cambian sin tocar el producto: el juicio ya no vale, como dice estado en texto.
        hechos.write_text(hechos.read_text() + ' ')
        datos = self.json_de('estado', ident, '--json')
        self.assertEqual((datos['oracle']['vigente'], datos['revision']['vigente']), (False, True))
        self.assertEqual(datos['proximo_paso'], f.proximo_paso(ident))
        # El informe de la revisión cambia sin tocar el producto: la revisión deja de valer, como en estado en texto.
        informe = self.root / f.leer(ident)[1]['revision']['informe']
        original = informe.read_bytes()
        informe.write_bytes(original + b'\n')
        self.assertFalse(self.json_de('estado', ident, '--json')['revision']['vigente'])
        informe.write_bytes(original)
        notas = self.root / 'examples/notas/notas.py'
        notas.write_text(notas.read_text() + '\n# cambio después de revisar\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'producto nuevo')
        datos = self.json_de('estado', ident, '--json')
        self.assertFalse(datos['revision']['vigente'])
        self.assertIsNone(datos['candidato'])  # el producto cambió: no hay candidato con su carpeta todavía

    def test_cj1_un_cambio_abandonado(self):
        with contextlib.redirect_stdout(io.StringIO()):
            ident = self.cambio_medido()
        with self.escribe('1'), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            f.abandonar(ident)  # confirmar; motivo armado
        datos = self.json_de('estado', ident, '--json')
        self.assertEqual((datos['fase'], datos['proximo_paso']), ('abandonada', None))
        self.assertTrue(datos['decisiones']['abandono']['motivo'])
        self.assertEqual(datos['decisiones']['abandono']['tipo_actor'], 'persona')

    # --- cj2: donde y resumen se leen como JSON ----------------------------------------------------------------------------
    def test_cj2_donde_con_un_artefacto_ausente(self):
        ident = self.cambio_revisado()
        hechos = self.carpeta(ident, f.candidato_vigente(ident)) / 'evidencia' / 'hechos.json'
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            f.juzgar(ident, hechos)
        hechos.unlink()  # la evidencia del juicio registrado ya no está
        datos = self.json_de('donde', ident, '--json')
        self.assertEqual((datos['esquema'], datos['id'], datos['candidato']), ('oracle-factory.donde/1', ident, None))
        ruta = hechos.relative_to(self.root).as_posix()
        self.assertEqual([(a['gate'], a['situacion']) for a in datos['artefactos'] if a['ruta'] == ruta], [('juicio', 'ausente')])
        self.assertIn(('spec', 'existe'), {(a['gate'], a['situacion']) for a in datos['artefactos']})
        # Fuera de lo histórico y lo no válido, la situación dice si el artefacto está en el disco.
        # Se eligen por gate, no por la situación que se comprueba: un histórico figura como histórico.
        self.assertTrue(all(a['situacion'] == 'historico' for a in datos['artefactos'] if a['gate'] == 'histórico'))
        propios = [a for a in datos['artefactos'] if a['gate'] != 'histórico']
        for a in propios:
            self.assertEqual(a['situacion'], 'existe' if (self.root / a['ruta']).exists() else 'ausente', a)
        self.assertEqual(sum(a['situacion'] == 'ausente' for a in propios), 1)
        cambio = f'openspec/changes/{ident}'  # y están los fijos de la convención
        self.assertLessEqual({f'{cambio}/proposal.md', f'{cambio}/design.md', f'{cambio}/tasks.md', f'tareas/{ident}/TAREA.md'},
                             {a['ruta'] for a in propios})
        self.assertTrue(all(set(a) == {'gate', 'ruta', 'situacion', 'nota'} for a in datos['artefactos']))

    def test_cj2_resumen_sin_escribir(self):
        cerrado = self.cambio_revisado(hallazgos=('H1',))
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            f.juzgar(cerrado, self.carpeta(cerrado, f.candidato_vigente(cerrado)) / 'evidencia' / 'hechos.json')
            with self.escribe('1'):
                f.cerrar(cerrado)
            abierto = f.nuevo('Otra nota', capacidad='otra')
            # Dos requisitos con el mismo pendiente de medidas: resumen los agrupa en un renglón.
            (self.root / 'openspec/changes' / abierto / 'specs/otra/spec.md').write_text(
                '# Capability: otra\n\n## ADDED Requirements\n' + ''.join(
                    f'\n### Requirement: promesa {n}\nTipo: funcional\nEl sistema SHALL cumplir la promesa {n}.\n\n'
                    f'#### Scenario: caso {n}\n- GIVEN algo\n- WHEN pasa\n- THEN se cumple\n' for n in ('uno', 'dos')))
            for nombre in ('proposal.md', 'design.md'):
                (self.root / 'openspec/changes' / abierto / nombre).write_text(f'# Otra nota\n\nCompleto: {nombre}.\n')
            with self.escribe('1'):
                f.aprobar_spec(abierto)
            f.importar(abierto)
            for rid in f.leer(abierto)[1]['requisitos']:  # medidas escritas a mano en el archivo, sin decisión registrada
                requisito = self.root / 'requisitos' / f'{rid}.requisito'
                requisito.write_text(requisito.read_text() + '    medido_por notas.casos_ejecutados\n')
            abandonado = f.nuevo('Una que no sigue', capacidad='tercera')
            with self.escribe('1'):
                f.abandonar(abandonado)  # confirmar; motivo armado
        (self.root / 'openspec/changes/20260101-000000-vieja').mkdir()  # una carpeta sin registro
        resumen = self.root / '.factory/resumen.md'
        antes = resumen.read_bytes()
        _, uno, _ = self.correr('resumen', '--json')
        _, dos, _ = self.correr('resumen', '--json')
        self.assertEqual(uno, dos)
        self.assertEqual(resumen.read_bytes(), antes)
        datos = json.loads(uno)
        self.assertEqual(datos['esquema'], 'oracle-factory.resumen/1')
        vigentes = [r for c in datos['capacidades'] for r in c['requisitos']]
        self.assertTrue(any(r['cambio'] == cerrado and r['medidas'] for r in vigentes))
        [abiertos] = [a for a in datos['abiertos'] if a['id'] == abierto]
        self.assertTrue(abiertos['pendientes'])
        [vigente] = [r for r in vigentes if r['cambio'] == cerrado]
        self.assertEqual([vigente['requisito']], f.leer(cerrado)[1]['requisitos'])  # el requisito de Oracle de ese cambio
        de_estado = f.pendientes_actuales(*f.leer(abierto))
        medidas = [p for p in de_estado if p.startswith('medidas de ')]
        self.assertEqual(len(medidas), 2)
        self.assertEqual(abiertos['pendientes'], [p for p in de_estado if p not in medidas]
                         + [f'medidas de 2 requisitos: {medidas[0].split(": ", 1)[1]}'])
        self.assertEqual(len({p.split(': ', 1)[1] for p in medidas}), 1)  # el mismo motivo
        self.assertEqual((vigente['tipo'], vigente['veredicto_al_cerrar'][:5]), ('funcional', 'verde'))
        self.assertEqual([(a['id'], bool(a['motivo'])) for a in datos['abandonados']], [(abandonado, True)])
        self.assertEqual(datos['sin_registro'], ['20260101-000000-vieja'])
        self.assertEqual([(r['cambio'], r['hallazgo'], r['vigente']) for r in datos['riesgos_aceptados']], [(cerrado, 'H1', True)])
        self.assertIn({'cambio': cerrado, 'vigente': True, 'limite': 'codex (gpt-x): Límite de codex.'}, datos['limites'])

    # --- cj3: el texto no cambia y los errores no se mezclan con el JSON -----------------------------------------------------
    def normalizar(self, texto, ident):
        texto = texto.replace(str(self.root), '<raiz>').replace(ident, '<id>').replace(f.actor()['actor'], '<actor>')
        texto = re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[^ )»;,\n]*', '<fecha>', texto)
        texto = re.sub(r'\b\d{4}-\d{2}-\d{2}\b', '<dia>', texto)
        texto = re.sub(r'\b[0-9a-f]{40}\b', '<sha>', texto)
        texto = re.sub(r'\b[0-9a-f]{7}\b', '<sha7>', texto)
        texto = re.sub(r'\b[0-9a-f]{64}\b', '<hash>', texto)
        texto = re.sub(r'_c[0-9a-f]{16}\.', '_c<h>.', texto)  # el id del requisito lleva un hash del cambio
        texto = re.sub(r'registro-[a-z0-9_]+', 'registro-<x>', texto)
        return re.sub(r'sha256:[0-9a-f]+', 'sha256:<hash>', texto)

    def test_cj3_el_texto_sigue_igual(self):
        ident = self.cambio_revisado()
        with self.escribe('3'):  # estado ofrece seguir: «Nada por ahora»
            salidas = {'estado': self.correr('estado', ident)[1], 'donde': self.correr('donde', ident)[1]}
        self.correr('resumen')
        salidas['resumen'] = (self.root / '.factory/resumen.md').read_text()
        for nombre, texto in salidas.items():
            ruta = REFERENCIA / f'{nombre}.txt'
            texto = self.normalizar(texto, ident)
            if os.environ.get('FACTORY_GENERAR_REFERENCIA'):
                ruta.parent.mkdir(parents=True, exist_ok=True)
                ruta.write_text(texto)
            with self.subTest(nombre=nombre):
                self.assertEqual(texto, ruta.read_text())

    def test_cj3_un_cambio_inexistente(self):
        for argv in (('estado', '20260101-000000-no-existe', '--json'), ('donde', '20260101-000000-no-existe', '--json')):
            with self.subTest(argv=argv):
                codigo, salida, errores = self.correr(*argv)
                self.assertEqual((codigo, salida), (1, ''))
                self.assertIn('FACTORY BLOQUEADA', errores)


if __name__ == '__main__':
    unittest.main()
