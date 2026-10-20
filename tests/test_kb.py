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
        self.assertEqual(self.correr('kb')[0], 0)
        nota = (self.root / 'kb/cambios' / f'{cerrado}.md').read_text()
        rid = f.leer(cerrado)[1]['requisitos'][0]
        self.assertIn(f'[[requisitos/{rid}]] — cumple', nota)
        self.assertRegex(nota, r'· Spec aprobada · Persona fixture \(persona\)')
        self.assertIn('· Revisión registrada · Persona fixture (persona) — aprobar', nota)
        self.assertIn('`examples/notas/notas.py`: Un nombre poco claro — aceptado por Persona fixture: se renombra en otro cambio', nota)
        self.assertIn('generado: oracle-factory kb', nota)
        self.assertIn('— aprobar: la evidencia cubre los dos escenarios', nota)
        # Los commits del cambio cerrado, hasta su cierre: uno antes (con su trailer) entra, el merge de después no.
        registro = self.root / '.factory/cambios' / cerrado / 'factory.json'
        self.git('commit', '-q', '--allow-empty', '-m', 'notas: antes del cierre', '-m', f'Cambio: {cerrado}')
        datos = json.loads(registro.read_text())
        datos['cierre']['cuando'] = self.git('log', '-1', '--format=%aI')
        registro.write_text(json.dumps(datos))
        subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', 'commit', '-q', '--allow-empty', '-m', f'Integrar {cerrado}',
                        '-m', f'Cambio: {cerrado}', '--date', '2099-01-01T00:00:00+00:00'], cwd=self.root, check=True)
        self.assertEqual(self.correr('kb')[0], 0)
        nota = (self.root / 'kb/cambios' / f'{cerrado}.md').read_text()
        self.assertIn('notas: antes del cierre (trailer)', nota)
        self.assertNotIn(f'Integrar {cerrado}', nota)
        abierta = (self.root / 'kb/cambios' / f'{abierto}.md').read_text()
        self.assertIn('- Responsable: Ana desde', abierta)
        self.assertIn(f'En curso: `oracle-factory log {abierto}`', abierta)
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
        self.assertEqual(self.revisada(nota)[0], 0)
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
