"""El conocimiento del proyecto: escenarios kb1–kb3, con la CLI en proyectos temporales, git de verdad y la extensión en
node con un `vscode` falso."""
import contextlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_tablero as _tablero  # noqa: E402

f = _tablero.f
SOURCE = Path(__file__).resolve().parents[1]


class Conocimiento(unittest.TestCase):
    T = _tablero.Tablero
    escribe, git, salida, cambio_cerrado = T.escribe, T.git, T.salida, T.cambio_cerrado
    candidato_nuevo, pedir, con_dos_revisores = T.candidato_nuevo, T.pedir, T.con_dos_revisores

    def setUp(self):
        _tablero.Tablero.setUp(self)
        self.assertEqual(Path(self.git('rev-parse', '--show-toplevel')).resolve(), self.root.resolve())
        # Quien tiene la terminal en estos tests (no el user.name global de la máquina).
        subprocess.run(['git', 'config', 'user.name', 'Persona fixture'], cwd=self.root, check=True)

    def correr(self, *args):
        """La CLI en proceso; devuelve (código, salida, errores)."""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            codigo = f.main(['--proyecto', str(self.root), *args])
        return codigo, out.getvalue(), err.getvalue()

    def proyecto(self):
        """Un cambio cerrado con un riesgo aceptado y otro abierto tomado por una persona."""
        self.con_dos_revisores()
        registro = self.root / '.factory/cambios' / self.cerrado / 'factory.json'
        datos = json.loads(registro.read_text())
        datos['aceptados'] = [{'archivo': 'examples/notas/notas.py', 'titulo': 'Un nombre poco claro', 'actor': 'Persona fixture',
                               'motivo': 'se renombra en otro cambio', 'firma': 'x', 'candidato': 'abc1234', 'fecha': '2026-10-01'}]
        datos['revision']['motivo'] = 'la evidencia cubre los dos escenarios'
        registro.write_text(json.dumps(datos))
        subprocess.run(['git', 'config', 'user.name', 'Ana'], cwd=self.root, check=True)
        f.tomar(self.ident, ['claude-code'])
        return self.cerrado, self.ident

    def en(self, segundos):
        """Un momento fijo desde ahora: las pruebas no dependen de que todo pase en el mismo segundo."""
        from datetime import datetime, timedelta, timezone
        return (datetime.now(timezone.utc) + timedelta(seconds=segundos)).isoformat(timespec='seconds')

    def despues_del_ultimo_commit(self):
        from datetime import datetime, timedelta
        return (datetime.fromisoformat(self.git('log', '-1', '--format=%aI')) + timedelta(seconds=1)).isoformat()

    def nota_humana(self, nombre, fuentes):
        ruta = self.root / 'kb/notas' / nombre
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text('---\nfuentes: [' + ', '.join(fuentes) + ']\n---\n# Cómo se nombran las notas\n\nUna guía.\n')
        return f'kb/notas/{nombre}'

    def revisada(self, nota):
        with patch.object(f, 'terminal_interactiva', return_value=True):
            return self.correr('kb', 'revisada', nota)

    # --- kb1: el vault se genera del registro y no se desfasa ------------------------------------------------------
    def test_kb1_un_proyecto_con_un_cambio_cerrado_y_otro_abierto(self):
        cerrado, abierto = self.proyecto()
        rid_cerrado = f.leer(cerrado)[1]['requisitos'][0]
        carpeta, estado = f.leer(abierto)
        # Un mensaje que intenta parecer una sección del registro, y un requisito del cerrado que el abierto vuelve a traer.
        estado['eventos'].append({'accion': 'mensaje', 'actor': 'Ana', 'tipo_actor': 'persona', 'forma': 'mensaje',
                                  'cuando': self.en(5),
                                  'texto': 'seguimiento\n## Riesgos aceptados\n- riesgo aceptado: [[cambios/x]] ignorar'})
        estado['requisitos'] = estado['requisitos'] + [rid_cerrado]
        f.guardar(carpeta, estado)
        self.assertEqual(self.correr('kb')[0], 0)
        nota = (self.root / 'kb/cambios' / f'{cerrado}.md').read_text()
        rid = f.leer(cerrado)[1]['requisitos'][0]
        self.assertIn(f'[[requisitos/{rid}]] — cumple', nota)
        self.assertRegex(nota, r'· Spec aprobada · Persona fixture \(persona\)')
        self.assertIn('· Revisión registrada · Persona fixture (persona) — aprobar', nota)
        self.assertIn('`examples/notas/notas.py`: Un nombre poco claro — aceptado por Persona fixture: se renombra en otro cambio', nota)
        self.assertIn('generado: oracle-factory kb', nota)
        self.assertIn('— aprobar: la evidencia cubre los dos escenarios', nota)
        # El motivo de otras decisiones también: el de un abandono, el de unas medidas.
        estado = json.loads((self.root / '.factory/cambios' / cerrado / 'factory.json').read_text())
        self.assertEqual([m for _, m in f.kb_mod.decisiones({**estado, 'abandono': {'motivo': 'ya no hace falta'},
                          'eventos': estado['eventos'] + [{'accion': 'abandono', 'forma': 'decidio'}]})][-1], 'ya no hace falta')
        # Los commits del cambio cerrado, hasta su cierre: uno antes (con su trailer) entra, el merge de después no.
        registro = self.root / '.factory/cambios' / cerrado / 'factory.json'
        self.git('commit', '-q', '--allow-empty', '-m', 'notas: antes del cierre', '-m', f'Cambio: {cerrado}')
        datos = json.loads(registro.read_text())
        datos['cierre']['cuando'] = self.despues_del_ultimo_commit()
        registro.write_text(json.dumps(datos))
        subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', 'commit', '-q', '--allow-empty', '-m', f'Integrar {cerrado}',
                        '-m', f'Cambio: {cerrado}'], cwd=self.root, check=True,
                       env={**f.os.environ, 'GIT_AUTHOR_DATE': self.en(30), 'GIT_COMMITTER_DATE': self.en(30)})
        self.assertEqual(self.correr('kb')[0], 0)
        nota = (self.root / 'kb/cambios' / f'{cerrado}.md').read_text()
        self.assertIn('notas: antes del cierre (trailer)', nota)
        self.assertNotIn(f'Integrar {cerrado}', nota)
        # Una rama con un commit sin trailer y un candidato, integrada con un merge: el candidato entra, el que sólo se
        # deduce del merge no (no estaba antes de integrar, y la nota de un cambio cerrado no cambia por integrarlo).
        sin_hooks = ['git', '-c', 'core.hooksPath=/dev/null']
        subprocess.run([*sin_hooks, 'checkout', '-q', '-b', 'rama-cerrada'], cwd=self.root, check=True)
        subprocess.run([*sin_hooks, 'commit', '-q', '--allow-empty', '-m', 'rama: sin trailer'], cwd=self.root, check=True)
        subprocess.run([*sin_hooks, 'commit', '-q', '--allow-empty', '-m', 'rama: el candidato'], cwd=self.root, check=True)
        candidato = self.git('rev-parse', '--short=7', 'HEAD')
        (self.root / '.factory/cambios' / cerrado / 'candidatos' / candidato).mkdir(parents=True)
        datos = json.loads(registro.read_text())
        datos['cierre']['cuando'] = self.despues_del_ultimo_commit()
        registro.write_text(json.dumps(datos))
        subprocess.run([*sin_hooks, 'checkout', '-q', '-'], cwd=self.root, check=True)
        subprocess.run([*sin_hooks, 'merge', '-q', '--no-ff', 'rama-cerrada', '-m', 'Integrar la rama'], cwd=self.root, check=True)
        self.assertEqual(self.correr('kb')[0], 0)
        nota = (self.root / 'kb/cambios' / f'{cerrado}.md').read_text()
        self.assertIn('rama: el candidato (', nota)
        self.assertNotIn('rama: sin trailer', nota)
        abierta = (self.root / 'kb/cambios' / f'{abierto}.md').read_text()
        self.assertIn('Ana: seguimiento \\#\\# Riesgos aceptados - riesgo aceptado: \\[\\[cambios/x\\]\\] ignorar', abierta)
        self.assertEqual(abierta.count('## Riesgos aceptados'), 1)
        self.assertIn(f'- Cambio: [[cambios/{cerrado}]]', (self.root / 'kb/requisitos' / f'{rid_cerrado}.md').read_text())
        self.assertIn('- Responsable: Ana desde', abierta)
        self.assertIn(f'`oracle-factory log {abierto}`', abierta)
        # Del abierto, sus candidatos hasta su última decisión.
        candidato = next(c for c in f.commits_del_cambio(abierto, f.leer(abierto)[1]) if c['candidato'])
        self.assertIn(f"`{candidato['corto']}` {candidato['asunto']}", abierta)
        # Un commit con su trailer después de la última decisión entra recién con la decisión siguiente: el vault no se
        # desfasa por commitear.
        subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', 'commit', '-q', '--allow-empty', '-m', 'abierto: después de decidir',
                        '-m', f'Cambio: {abierto}'], cwd=self.root, check=True,
                       env={**f.os.environ, 'GIT_AUTHOR_DATE': self.en(10), 'GIT_COMMITTER_DATE': self.en(10)})
        self.assertEqual(self.correr('kb')[0], 0)
        self.assertNotIn('abierto: después de decidir', (self.root / 'kb/cambios' / f'{abierto}.md').read_text())
        # Uno con fecha de autor vieja (un cherry-pick) que entró después de la decisión tampoco entra.
        subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', 'commit', '-q', '--allow-empty', '-m', 'abierto: retrodatado',
                        '-m', f'Cambio: {abierto}'], cwd=self.root, check=True,
                       env={**f.os.environ, 'GIT_AUTHOR_DATE': '2001-01-01T00:00:00+00:00', 'GIT_COMMITTER_DATE': self.en(12)})
        self.assertEqual(self.correr('kb')[0], 0)
        self.assertNotIn('abierto: retrodatado', (self.root / 'kb/cambios' / f'{abierto}.md').read_text())
        carpeta, estado = f.leer(abierto)
        f.evento(estado, 'agente_sumado', forma='registro', agente='codex')
        estado['eventos'][-1]['cuando'] = self.en(20)
        f.guardar(carpeta, estado)
        self.assertIn('abierto: después de decidir (trailer)', (self.root / 'kb/cambios' / f'{abierto}.md').read_text())
        self.git('add', '.')
        self.git('commit', '-qm', 'registros')
        requisito = (self.root / 'kb/requisitos' / f'{rid}.md').read_text()
        self.assertIn(f'- Cambio: [[cambios/{cerrado}]]', requisito)
        self.assertIn('- Veredicto: cumple', requisito)
        # Todo enlace resuelve a una nota.
        for ruta in (self.root / 'kb').rglob('*.md'):
            for enlace in re.findall(r'\[\[([^\]|]+)', ruta.read_text()):
                self.assertTrue((self.root / 'kb' / f'{enlace}.md').is_file(), f'{ruta}: [[{enlace}]]')
        # El texto no depende de cuándo se genera.
        antes = {p: p.read_bytes() for p in (self.root / 'kb').rglob('*.md')}
        self.assertEqual(self.correr('kb')[0], 0)
        self.assertEqual({p: p.read_bytes() for p in (self.root / 'kb').rglob('*.md')}, antes)
        codigo, salida, _ = self.correr('kb', '--verificar')
        self.assertEqual(codigo, 0)
        self.assertIn('kb/ está al día', salida)

    def test_kb1_el_vault_queda_viejo(self):
        self.proyecto()
        self.assertEqual(self.correr('kb')[0], 0)
        # Una decisión (aprobar la spec de un cambio nuevo) rehace sus notas sola.
        f.AGENTE = 'claude-code'
        try:
            nuevo = f.nuevo('Otro cambio', capacidad='otra', sufijo='otro')
        finally:
            f.AGENTE = None
        (self.root / 'openspec/changes' / nuevo / 'proposal.md').write_text(
            '# Otro cambio\n\n## Why\n\nPorque sí.\n\n## What changes\n\nAlgo.\n\n## Out of scope\n\nNada.\n\n## Human decisions\n\nNinguna.\n')
        (self.root / 'openspec/changes' / nuevo / 'specs/otra/spec.md').write_text(
            '# Capability: otra\n\n## ADDED Requirements\n\n### Requirement: algo\nTipo: funcional\nThe system SHALL do it.\n\n'
            '#### Scenario: uno\n- GIVEN a\n- WHEN b\n- THEN c\n')
        with self.escribe('1'):
            f.aprobar_spec(nuevo)
        self.assertIn('Spec aprobada', (self.root / 'kb/cambios' / f'{nuevo}.md').read_text())
        self.assertIn(f'[[cambios/{nuevo}]]', (self.root / 'kb/README.md').read_text())
        self.assertEqual(self.correr('kb', '--verificar')[0], 0)
        # importar y medir escriben los requisitos después del registro: al terminar el comando, el vault también está al día.
        self.assertEqual(self.correr('--agente', 'claude-code', 'importar', nuevo)[0], 0)
        [rid] = f.leer(nuevo)[1]['requisitos']
        self.assertEqual(self.correr('--agente', 'claude-code', 'medir', nuevo, '--requisito', rid, '--medida', 'notas.casos_ejecutados',
                                     '--quitar-sin-medir')[0], 0)
        self.assertIn('`notas.casos_ejecutados`', (self.root / 'kb/requisitos' / f'{rid}.md').read_text())
        self.assertEqual(self.correr('kb', '--verificar')[0], 0)
        # Una nota generada de algo que ya no está (un requisito retirado): el próximo comando que cambia algo la saca.
        huerfana = self.root / 'kb/requisitos/otra_c0.ya_no_esta.md'
        huerfana.write_text('---\ngenerado: oracle-factory kb\n---\n# ya no está\n')
        self.assertIn('sobra kb/requisitos/otra_c0.ya_no_esta.md', self.correr('kb', '--verificar')[2])
        self.assertEqual(self.correr('--agente', 'claude-code', 'mensaje', nuevo, 'listo el primer paso')[0], 0)
        self.assertFalse(huerfana.exists())
        self.assertEqual(self.correr('kb', '--verificar')[0], 0)
        # Las notas generadas no son producto: rehacerlas con cada decisión no vence la revisión ni el juicio. Las de
        # personas sí.
        self.assertTrue(any(n.startswith('kb/') for n in subprocess.run(['git', 'status', '--porcelain', 'kb'], cwd=self.root,
                                                                       capture_output=True, text=True).stdout.split()))
        self.assertEqual([n for n in f.cambios_locales_de_producto() if n.startswith('kb/')], [])
        self.assertFalse(f.es_producto('kb/README.md') or f.es_producto(f'kb/cambios/{nuevo}.md') or f.es_producto(f'kb/requisitos/{rid}.md'))
        self.assertTrue(f.es_producto('kb/notas/guia.md'))
        # Una nota generada editada a mano: la verificación falla y no la toca.
        nota = self.root / 'kb/cambios' / f'{nuevo}.md'
        nota.write_text(nota.read_text() + '\nUna línea a mano.\n')
        editada = nota.read_text()
        codigo, _, errores = self.correr('kb', '--verificar')
        self.assertEqual(codigo, 1)
        self.assertIn(f'kb/cambios/{nuevo}.md no coincide con el registro', errores)
        self.assertEqual(nota.read_text(), editada)

    # --- kb2: una nota humana vence cuando cambian sus fuentes -----------------------------------------------------
    def test_kb2_una_guia_cuyo_archivo_cambio(self):
        _, abierto = self.proyecto()
        self.correr('kb')
        nota = self.nota_humana('nombres.md', ['examples/notas/notas.py'])
        # Las fuentes también se leen de una lista de YAML sin sangría.
        (self.root / nota).write_text('---\nfuentes:\n- examples/notas/notas.py\n---\n# Cómo se nombran las notas\n')
        self.assertEqual(f.kb_mod.fuentes_de(self.root / nota), ['examples/notas/notas.py'])
        f.AGENTE = 'claude-code'
        try:
            otro = f.nuevo('Otro cambio abierto', capacidad='otra', sufijo='otro')
        finally:
            f.AGENTE = None
        self.assertEqual(self.revisada(nota)[0], 0)
        self.assertEqual(self.correr('kb', '--verificar')[0], 0)
        self.git('add', '.')
        self.git('commit', '-qm', 'la guía')
        # El cambio abierto modifica el archivo: la nota queda por revisar, y estado lo avisa.
        notas = self.root / 'examples/notas/notas.py'
        notas.write_text(notas.read_text() + '\n# otro cambio más\n')
        codigo, _, errores = self.correr('kb', '--verificar')
        self.assertEqual(codigo, 1)
        self.assertIn(f'{nota} está por revisar: cambió examples/notas/notas.py', errores)
        self.assertTrue(any(f'la nota {nota} está por revisar' in a for a in f.datos_estado(abierto)['avisos']))
        # Una fuente con espacios en su ruta también se reconoce como tocada.
        espaciada = self.root / 'docs/guia de inicio.md'
        espaciada.parent.mkdir(exist_ok=True)
        espaciada.write_text('Guía.\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'una guía con espacios')
        nota2 = self.nota_humana('inicio.md', ['docs/guia de inicio.md'])
        self.assertEqual(self.revisada(nota2)[0], 0)
        espaciada.write_text('Guía, cambiada.\n')
        self.assertTrue(any(f'la nota {nota2} está por revisar' in a for a in f.datos_estado(abierto)['avisos']))
        # El otro cambio abierto no tocó ese archivo (el checkout es el del que tomó Ana): no lo avisa.
        self.assertFalse(any('por revisar' in a for a in f.datos_estado(otro)['avisos']))
        self.assertEqual(self.revisada(nota)[0], 0)
        self.assertEqual(self.revisada(nota2)[0], 0)
        self.assertEqual(self.correr('kb', '--verificar')[0], 0)
        self.assertFalse(any('por revisar' in a for a in f.datos_estado(abierto)['avisos']))

    def test_kb2_revisar_sin_terminal_o_una_fuente_que_no_existe(self):
        self.proyecto()
        self.correr('kb')
        guia = self.nota_humana('guia.md', ['examples/notas/notas.py'])
        rota = self.nota_humana('rota.md', ['no/existe.py'])
        codigo, _, errores = self.correr('--agente', 'claude-code', 'kb', 'revisada', guia)
        self.assertEqual(codigo, 1)
        self.assertIn('lo decide una persona', errores)
        with patch.object(f, 'terminal_interactiva', return_value=False):
            self.assertEqual(self.correr('kb', 'revisada', guia)[0], 1)
        self.assertFalse((self.root / '.factory/kb.json').exists())
        codigo, _, errores = self.correr('kb', '--verificar')
        self.assertEqual(codigo, 1)
        self.assertIn(f'{rota}: su fuente no/existe.py no existe', errores)
        self.assertIn(f'{guia} está por revisar', errores)
        # Un .requisito que es un enlace simbólico hacia afuera del proyecto no es una fuente.
        (self.root / 'requisitos/sec.externo.requisito').symlink_to(afuera := Path(self.tmp.name) / 'secreto.requisito')
        afuera.write_text('requisito sec.externo:\n')
        self.assertIsNone(f.kb_mod.huella_de_fuente(f, 'sec.externo'))
        # Una fuente con forma de requisito no sale de requisitos/ (ni con .. ni absoluta), y ./x es x.
        afuera = Path(self.tmp.name) / 'externo.requisito'
        afuera.write_text('requisito x.y:\n')
        self.assertIsNone(f.kb_mod.huella_de_fuente(f, str(afuera.with_suffix(''))))
        self.assertIsNone(f.kb_mod.huella_de_fuente(f, '../externo'))
        punto = self.nota_humana('punto.md', ['./examples/notas/notas.py'])
        self.assertEqual(f.kb_mod.fuentes_de(self.root / punto), ['examples/notas/notas.py'])
        # Un cambio como fuente: vence cuando cambia lo que se sabe de él (una decisión, un riesgo), no sólo su spec.
        decision = self.nota_humana('decision.md', [self.ident])
        self.assertEqual(self.revisada(decision)[0], 0)
        self.assertNotIn(f'{decision} está por revisar', self.correr('kb', '--verificar')[2])
        carpeta, estado = f.leer(self.ident)
        estado['aceptados'] = [{'archivo': 'x.py', 'titulo': 't', 'actor': 'Ana', 'motivo': 'm', 'firma': 'f'}]
        f.guardar(carpeta, estado)
        self.assertIn(f'{decision} está por revisar: cambió {self.ident}', self.correr('kb', '--verificar')[2])
        codigo, _, errores = self.revisada(rota)
        self.assertEqual(codigo, 1)
        self.assertIn('no/existe.py no existe', errores)

    # --- kb3: por qué existe una línea ------------------------------------------------------------------------------
    def linea_de(self, archivo, texto):
        return next(i for i, l in enumerate((self.root / archivo).read_text().splitlines(), 1) if texto in l)

    @unittest.skipUnless(_tablero.NODE, 'hace falta node')
    def test_kb3_una_linea_escrita_en_un_cambio_cerrado(self):
        cerrado, _ = self.proyecto()
        archivo = self.root / 'examples/notas/notas.py'
        archivo.write_text(archivo.read_text() + '\nLIMITE = 80  # el título no pasa de 80\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'notas: un límite al título', '-m', f'Cambio: {cerrado}')
        self.nota_humana('limites.md', ['examples/notas/notas.py'])
        linea = self.linea_de('examples/notas/notas.py', 'LIMITE = 80')
        # Un commit sin trailer del cambio abierto, antes de su último candidato (integrado sin merge): es de ese cambio.
        guia = self.root / 'examples/notas/README.md'
        guia.write_text(guia.read_text() + '\nUna línea del tramo.\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'tramo sin trailer')
        self.git('commit', '-q', '--allow-empty', '-m', 'el candidato nuevo')
        (self.root / '.factory/cambios' / self.ident / 'candidatos' / self.git('rev-parse', '--short=7', 'HEAD')).mkdir(parents=True)
        tramo = json.loads(self.correr('por-que', f'examples/notas/README.md:{self.linea_de("examples/notas/README.md", "Una línea del tramo")}',
                                       '--json')[1])
        self.assertEqual((tramo['cambio']['id'], tramo['cambio']['union']), (self.ident, 'deducido por su tramo'))
        self.assertIn('puede ser otro trabajo de ese tiempo', self.correr('por-que', f'examples/notas/README.md:{self.linea_de("examples/notas/README.md", "Una línea del tramo")}')[1])
        codigo, salida, _ = self.correr('por-que', f'examples/notas/notas.py:{linea}', '--json')
        self.assertEqual(codigo, 0)
        datos = json.loads(salida)
        self.assertEqual(datos['commit']['asunto'], 'notas: un límite al título')
        c = datos['cambio']
        self.assertEqual((c['id'], c['union']), (cerrado, 'trailer'))
        self.assertEqual({r['veredicto'] for r in c['requisitos']}, {'cumple'})
        aprobada = next(d for d in c['decisiones'] if d['accion'] == 'spec_aprobada')
        self.assertEqual((aprobada['actor'], aprobada['tipo_actor']), ('Persona fixture', 'persona'))
        self.assertTrue(aprobada['cuando'])
        self.assertEqual(c['riesgos_aceptados'], [{'titulo': 'Un nombre poco claro', 'actor': 'Persona fixture',
                                                   'motivo': 'se renombra en otro cambio'}])
        self.assertEqual(datos['notas'], ['kb/notas/limites.md'])
        # En VS Code, para la línea del cursor: un documento de sólo lectura con la misma respuesta.
        r = subprocess.run([_tablero.NODE, str(SOURCE / 'tests/porque_en_node.cjs'), str(_tablero.EXTENSION), str(self.root),
                            str(self.cli_falsa()), 'examples/notas/notas.py', str(linea)], capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr)
        [doc] = json.loads(r.stdout)['documentos']
        self.assertEqual(doc['lenguaje'], 'markdown')
        self.assertIn(f'Cambio {cerrado} (trailer)', doc['contenido'])
        self.assertIn('riesgo aceptado en este archivo: Un nombre poco claro', doc['contenido'])
        self.assertIn('nota: kb/notas/limites.md', doc['contenido'])

    def test_kb3_una_linea_que_no_es_de_ningun_cambio(self):
        self.proyecto()
        suelto = self.root / 'suelto.txt'
        suelto.write_text('una línea suelta\n')
        self.git('add', 'suelto.txt')
        self.git('commit', '-qm', 'algo suelto')
        codigo, salida, _ = self.correr('por-que', 'suelto.txt:1')
        self.assertEqual(codigo, 0)
        self.assertIn('no es de ningún cambio de Factory', salida)
        self.assertIn(self.git('rev-parse', '--short=7', 'HEAD'), salida)

    def cli_falsa(self):
        cli = Path(self.tmp.name) / 'oracle-factory'
        cli.write_text(f'#!/bin/sh\nPYTHONPATH={SOURCE} exec {sys.executable} -c "import sys; '
                       f'from oracle_factory.cli import main; sys.exit(main())" "$@"\n')
        cli.chmod(0o755)
        return cli


if __name__ == '__main__':
    unittest.main()
