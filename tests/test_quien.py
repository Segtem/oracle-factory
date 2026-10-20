"""Quién trabaja en qué: escenarios qn1–qn3, con la CLI en proyectos temporales, git de verdad y el panel en node."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_archivo as _archivo  # noqa: E402
import test_commits as _commits  # noqa: E402
import test_tablero as _tablero  # noqa: E402

f = _archivo.f
SOURCE = Path(__file__).resolve().parents[1]


class Quien(unittest.TestCase):
    git = _archivo.Archivo.git

    def setUp(self):
        _archivo.Archivo.setUp(self)
        # Los registros se commitean en el temporal: git no puede subir a un repositorio que lo contenga.
        self.assertEqual(Path(self.git('rev-parse', '--show-toplevel')).resolve(), self.root.resolve())

    def nuevo(self, sufijo):
        f.AGENTE = 'claude-code'
        try:
            return f.nuevo(f'Cambio {sufijo}', capacidad='otra', sufijo=sufijo)
        finally:
            f.AGENTE = None

    def como(self, persona):
        """La persona que tiene la terminal: su user.name de Git."""
        subprocess.run(['git', 'config', 'user.name', persona], cwd=self.root, check=True)

    def eventos(self, ident):
        return f.leer(ident)[1]['eventos']

    # --- qn1: un cambio dice quién lo tiene -----------------------------------------------------------------------
    def test_qn1_tomar_soltar_y_relevar(self):
        ident = self.nuevo('uno')
        self.como('Ana')
        f.tomar(ident, ['claude-code'])
        r = f.leer(ident)[1]['responsable']
        self.assertEqual((r['persona'], r['con']), ('Ana', ['claude-code']))
        self.assertEqual((self.eventos(ident)[-1]['accion'], self.eventos(ident)[-1]['con']), ('tomado', ['claude-code']))
        # Otra persona sin --relevo: se niega y no cambia nada.
        self.como('Beto')
        antes = (self.root / '.factory/cambios' / ident / 'factory.json').read_text()
        with self.assertRaisesRegex(f.FactoryError, 'lo tiene Ana .*--relevo. No cambié nada'):
            f.tomar(ident)
        self.assertEqual((self.root / '.factory/cambios' / ident / 'factory.json').read_text(), antes)
        # Beto no puede soltarlo por Ana.
        with self.assertRaisesRegex(f.FactoryError, 'lo tiene Ana'):
            f.soltar(ident)
        # Con --relevo, queda constancia de quién lo tenía.
        f.tomar(ident, relevo=True)
        self.assertEqual(f.leer(ident)[1]['responsable']['persona'], 'Beto')
        self.assertEqual(self.eventos(ident)[-1]['relevo_de'], 'Ana')
        f.soltar(ident)
        self.assertIsNone(f.leer(ident)[1]['responsable'])
        self.assertEqual(self.eventos(ident)[-1]['accion'], 'soltado')

    def test_qn1_un_agente_se_suma(self):
        ident = self.nuevo('dos')
        self.como('Ana')
        f.tomar(ident)
        f.AGENTE = 'codex'
        try:
            f.tomar(ident)
        finally:
            f.AGENTE = None
        estado = f.leer(ident)[1]
        self.assertEqual(estado['responsable']['persona'], 'Ana')
        self.assertEqual((estado['eventos'][-1]['accion'], estado['eventos'][-1]['agente']), ('agente_sumado', 'codex'))
        # Sin terminal ni --agente: se niega.
        with patch.object(f, 'terminal_interactiva', return_value=False), \
                self.assertRaisesRegex(f.FactoryError, 'una persona desde su terminal, o un agente'):
            f.tomar(ident)

    # --- qn2: estado y el tablero muestran quién trabaja en qué ----------------------------------------------------
    def test_qn2_un_cambio_con_persona_agentes_y_un_revisor_en_curso(self):
        ident = self.nuevo('tres')
        self.como('Ana')
        f.tomar(ident, ['claude-code'])
        f.AGENTE = 'codex'
        try:
            f.tomar(ident)
        finally:
            f.AGENTE = None
        carpeta, estado = f.leer(ident)
        estado['eventos'].append({'accion': 'revision_lanzada', 'revisor': 'agy', 'candidato': 'abc1234',
                                  'cuando': f.ahora(), 'lanzamiento': 'x1'})
        # Un agente que actuó hace dos días y no está declarado ya no cuenta.
        estado['eventos'].insert(0, {'accion': 'medidas_propuestas', 'actor': 'viejo-agente', 'tipo_actor': 'agente',
                                     'cuando': '2020-01-01T00:00:00+00:00'})
        # gemini actuó hace un rato sin declararse: cuenta. Uno con la fecha en el futuro (otro reloj) no, y uno sin zona
        # horaria de hace una hora sí (Factory escribe en UTC).
        hace_un_rato = (f.dt.datetime.now(f.dt.timezone.utc) - f.dt.timedelta(hours=1)).isoformat(timespec='seconds')
        estado['eventos'].insert(1, {'accion': 'medidas_propuestas', 'actor': 'gemini', 'tipo_actor': 'agente', 'cuando': hace_un_rato})
        estado['eventos'].insert(1, {'accion': 'medidas_propuestas', 'actor': 'futuro', 'tipo_actor': 'agente',
                                     'cuando': '2999-01-01T00:00:00+00:00'})
        estado['eventos'].insert(1, {'accion': 'medidas_propuestas', 'actor': 'sin-zona', 'tipo_actor': 'agente',
                                     'cuando': hace_un_rato[:19]})
        f.guardar(carpeta, estado)
        q = f.datos_estado(ident)['quien']
        self.assertEqual(q['responsable']['persona'], 'Ana')
        self.assertEqual({a['nombre']: (a['declarado'], a['ultima_accion']) for a in q['agentes']},
                         {'claude-code': (True, 'cambio_creado'), 'codex': (True, 'agente_sumado'),
                          'gemini': (False, 'medidas_propuestas'), 'sin-zona': (False, 'medidas_propuestas')})
        self.git('add', '.')
        self.git('commit', '-qm', 'registros')
        [cambio] = _tablero.cli_json(self.root, 'tablero', '--json')['cambios']
        self.assertEqual(cambio['quien']['agentes'], q['agentes'])
        self.assertEqual(cambio['quien']['revisores_en_curso'], q['revisores_en_curso'])
        self.assertEqual(q['revisores_en_curso'], [{'revisor': 'agy', 'candidato': 'abc1234',
                                                     'cuando': estado['eventos'][-1]['cuando']}])
        texto = io.StringIO()
        with contextlib.redirect_stdout(texto), patch('builtins.input', return_value='3'):
            f.mostrar(ident)
        self.assertIn('Responsable: Ana desde', texto.getvalue())
        self.assertIn('agentes: claude-code (cambio_creado', texto.getvalue())
        self.assertIn('revisando: agy sobre abc1234', texto.getvalue())

    def test_qn2_quien_esta_en_que_en_el_proyecto(self):
        tomado, libre = self.nuevo('cuatro'), self.nuevo('cinco')
        self.como('Ana')
        f.tomar(tomado, ['claude-code'])
        self.git('add', '.')
        self.git('commit', '-qm', 'registros')
        datos = _tablero.cli_json(self.root, 'tablero', '--json')
        self.assertEqual(datos['proyecto']['por_responsable'], {'Ana': [tomado]})
        self.assertEqual(datos['proyecto']['sin_responsable'], [libre])
        if not _tablero.NODE:
            self.skipTest('hace falta node')
        r = subprocess.run([_tablero.NODE, str(SOURCE / 'tests/tablero_en_node.cjs'), str(_tablero.EXTENSION), str(self.root),
                            '[]', str(self.cli_falsa())], capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr)
        html = json.loads(r.stdout)['html']
        self.assertIn('Responsable: <b>Ana</b>', html)
        self.assertIn('<b>claude-code</b> (declarado)', html)
        self.assertIn(f'<li><b>Ana</b>: {tomado}</li>', html)
        self.assertIn(f'sin responsable</span>: {libre}', html)

    def cli_falsa(self):
        cli = Path(self.tmp.name) / 'oracle-factory'
        cli.write_text(f'#!/bin/sh\nPYTHONPATH={SOURCE} exec {sys.executable} -c "import sys; '
                       f'from oracle_factory.cli import main; sys.exit(main())" "$@"\n')
        cli.chmod(0o755)
        return cli


class Trailer(unittest.TestCase):
    """qn3, con git de verdad: el hook corre en cada commit."""
    setUp, git, cli, nuevo = _commits.Commits.setUp, _commits.Commits.git, _commits.Commits.cli, _commits.Commits.nuevo
    commit, cerrar_a_mano = _commits.Commits.commit, _commits.Commits.cerrar_a_mano

    # --- qn3: el trailer elige bien el cambio -----------------------------------------------------------------------
    def test_qn3_un_merge_que_nombra_el_cambio_que_integra(self):
        integrado = self.nuevo('integrado')
        self.cerrar_a_mano(integrado)
        abierto = self.nuevo('abierto')
        mensaje = self.commit('a.txt', f'Integrar {integrado}: lo que hace')
        self.assertIn(f'Cambio: {integrado}', mensaje)
        self.assertNotIn(abierto, mensaje)
        # Si nombra dos cambios, ninguno; y un ID que no es de un cambio no cuenta.
        self.assertNotIn('Cambio:', self.commit('b.txt', f'Junta {integrado} y {abierto}'))
        self.assertIn(f'Cambio: {abierto}', self.commit('c.txt', 'Menciona 20200101-000000-no-existe'))

    def test_qn3_varios_abiertos_y_uno_tomado_por_quien_commitea(self):
        mio, otro = self.nuevo('mio'), self.nuevo('otro')
        self.assertNotIn('Cambio:', self.commit('a.txt', 'nadie tomó nada'))
        self.git('config', 'user.name', 'Persona fixture')
        registro = self.root / '.factory/cambios' / mio / 'factory.json'
        datos = json.loads(registro.read_text())
        datos['responsable'] = {'persona': 'Persona fixture', 'desde': '2026-10-19T10:00:00+00:00', 'con': []}
        registro.write_text(json.dumps(datos))
        self.assertIn(f'Cambio: {mio}', self.commit('b.txt', 'lo que tomé'))
        # Si tomó los dos, no se sabe cuál: sin trailer.
        registro = self.root / '.factory/cambios' / otro / 'factory.json'
        datos = json.loads(registro.read_text())
        datos['responsable'] = {'persona': 'Persona fixture', 'desde': '2026-10-19T10:00:00+00:00', 'con': []}
        registro.write_text(json.dumps(datos))
        self.assertNotIn('Cambio:', self.commit('b2.txt', 'tomé los dos'))
        # Otra persona, que no tomó ninguno: sin trailer.
        self.git('config', 'user.name', 'Otra persona')
        self.assertNotIn('Cambio:', self.commit('c.txt', 'no tomé nada'))
        self.assertNotIn(otro, self.git('log', '--format=%B'))


if __name__ == '__main__':
    unittest.main()
