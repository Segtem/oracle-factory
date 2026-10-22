"""Unir al integrar: escenarios un1–un3, con git de verdad, un repositorio central y dos clones; más la unión pura."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE))
from oracle_factory import unir as unir_mod  # noqa: E402
from tools.terminal import en_terminal  # noqa: E402

CLI = [sys.executable, '-c', 'import sys; from oracle_factory.cli import main; sys.exit(main())']


class Unir(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.env = {**os.environ, 'PYTHONPATH': str(SOURCE), 'GIT_CEILING_DIRECTORIES': str(base),
                    'GIT_AUTHOR_EMAIL': 'p@x.invalid', 'GIT_COMMITTER_EMAIL': 'p@x.invalid'}
        semilla = base / 'semilla'
        semilla.mkdir()
        self.git(semilla, 'init', '-q', '-b', 'main')
        self.git(semilla, 'config', 'user.name', 'Semilla')
        self.cli(semilla, 'init')
        self.git(semilla, 'add', '-A')
        self.git(semilla, 'commit', '-qm', 'init')
        self.cli(semilla, 'nuevo', '--capacidad', 'calc', '--sufijo', 'comun', 'Un cambio de los dos')
        self.cli(semilla, 'kb')
        self.git(semilla, 'add', '-A')
        self.git(semilla, 'commit', '-qm', 'el cambio')
        [self.ident] = [p.name for p in (semilla / 'openspec/changes').iterdir() if p.is_dir()]
        self.central = base / 'central.git'
        subprocess.run(['git', 'clone', '-q', '--bare', str(semilla), str(self.central)], check=True, capture_output=True)
        self.ana, self.beto = self.clon('Ana'), self.clon('Beto')

    def git(self, donde, *args):
        r = subprocess.run(['git', *args], cwd=donde, env=self.env, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        return r.stdout.strip()

    def cli(self, donde, *args):
        r = subprocess.run([*CLI, '--agente', 'agente-prueba', *args], cwd=donde, env=self.env, capture_output=True,
                           text=True, stdin=subprocess.DEVNULL)
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        return r.stdout

    def persona(self, donde, *args, entrada='', ok=True):
        r = en_terminal([*CLI, *args], cwd=donde, env=self.env, entrada=entrada)
        if ok:
            self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
            return r.stdout
        return r

    def clon(self, nombre):
        destino = Path(self.tmp.name) / nombre.lower()
        subprocess.run(['git', 'clone', '-q', str(self.central), str(destino)], check=True, capture_output=True)
        self.git(destino, 'config', 'user.name', nombre)
        self.cli(destino, 'hooks')
        return destino

    def registro(self, donde):
        return json.loads((donde / '.factory/cambios' / self.ident / 'factory.json').read_text())

    def en_rama(self, donde, rama, *orden, persona=False):
        """En una rama propia, hace la orden (o la función), commitea y sube."""
        self.git(donde, 'checkout', '-q', '-b', rama)
        if callable(orden[0]):
            orden[0]()
        else:
            (self.persona if persona else self.cli)(donde, *orden)
        self.git(donde, 'add', '-A')
        self.git(donde, 'commit', '-qm', rama)
        self.git(donde, 'push', '-q', 'origin', rama)

    def integrar_las_dos(self, queda=''):
        """Ana integra su rama y la de Beto en main; ninguna de las dos chocan."""
        self.git(self.ana, 'checkout', '-q', 'main')
        self.git(self.ana, 'fetch', '-q', 'origin')
        for rama in ('origin/tarea/ana', 'origin/tarea/beto'):
            self.git(self.ana, 'merge', '-q', '--no-ff', '-m', f'Integrar {rama}', rama)
        self.assertEqual(self.git(self.ana, 'status', '--porcelain'), queda)
        self.git(self.ana, 'push', '-q', 'origin', 'main')

    def fase(self, donde, fase):
        """Lo que deja una decisión que cambia la fase (abandonar, cerrar), escrito a mano en el registro."""
        def escribir():
            registro = self.registro(donde)
            registro['fase'] = fase
            (donde / '.factory/cambios' / self.ident / 'factory.json').write_text(json.dumps(registro, indent=2) + '\n')
        return escribir

    # --- un1: el registro editado en dos ramas se une --------------------------------------------------------------
    def test_un1_mensajes_en_dos_ramas(self):
        self.en_rama(self.ana, 'tarea/ana', 'mensaje', self.ident, 'de Ana')
        self.en_rama(self.beto, 'tarea/beto', 'mensaje', self.ident, 'de Beto')
        self.integrar_las_dos()
        eventos = self.registro(self.ana)['eventos']
        self.assertEqual(sorted(e['texto'] for e in eventos if e['accion'] == 'mensaje'), ['de Ana', 'de Beto'])
        self.assertEqual([e['cuando'] for e in eventos], sorted(e['cuando'] for e in eventos))
        self.assertNotIn('pendientes_de_union', self.registro(self.ana))
        # Instalar otra vez, con las líneas alineadas con más espacios, no las repite.
        atributos = self.ana / '.gitattributes'
        atributos.write_text(atributos.read_text().replace(' merge=', '    merge='))
        self.cli(self.ana, 'hooks')
        self.assertEqual(atributos.read_text().count('merge=oracle-factory-registro'), 1)

    # --- un2: lo que las dos ramas decidieron distinto lo decide una persona ---------------------------------------
    def test_un2_dos_personas_lo_toman(self):
        self.en_rama(self.ana, 'tarea/ana', 'tomar', self.ident, persona=True)
        self.en_rama(self.beto, 'tarea/beto', 'tomar', self.ident, persona=True)
        self.integrar_las_dos()
        registro = self.registro(self.ana)
        self.assertEqual(registro['responsable']['persona'], 'Ana')  # el de la rama que integra, sin elegir
        self.assertEqual([p['campo'] for p in registro['pendientes_de_union']], ['responsable'])
        self.assertIn('union_con_decisiones', [e['accion'] for e in registro['eventos']])
        estado = self.cli(self.ana, 'estado', self.ident)
        self.assertIn('Beto', estado)
        self.assertIn(f'tomar {self.ident} --relevo', estado)
        avisos = json.loads(self.cli(self.ana, 'estado', self.ident, '--json'))['avisos']
        self.assertTrue(any('al unir dos ramas, responsable quedó' in x and 'Beto' in x for x in avisos), avisos)
        # Beto trae main: sin --relevo no puede, porque lo tiene Ana; con --relevo lo toma y el aviso se va.
        self.git(self.beto, 'checkout', '-q', 'main')
        self.git(self.beto, 'pull', '-q', '--no-rebase', 'origin', 'main')
        self.assertNotEqual(self.persona(self.beto, 'tomar', self.ident, ok=False).returncode, 0)
        self.assertIn('pendientes_de_union', self.registro(self.beto))
        self.persona(self.beto, 'tomar', self.ident, '--relevo')
        self.assertEqual(self.registro(self.beto)['responsable']['persona'], 'Beto')
        self.assertNotIn('pendientes_de_union', self.registro(self.beto))
        self.assertNotIn('Factory no eligió', self.cli(self.beto, 'estado', self.ident))

    # --- un2: dos fases no se eligen en silencio; una persona elige, también en un cambio cerrado ------------------
    def test_un2_dos_fases(self):
        self.en_rama(self.ana, 'tarea/ana', self.fase(self.ana, 'abandonada'))
        self.en_rama(self.beto, 'tarea/beto', self.fase(self.beto, 'cerrada'))
        self.integrar_las_dos()
        registro = self.registro(self.ana)
        self.assertEqual(registro['fase'], 'abandonada')
        [pendiente] = registro['pendientes_de_union']
        self.assertEqual((pendiente['campo'], pendiente['suyo']), ('fase', 'cerrada'))
        self.assertIn(f'decidir-union {self.ident} fase nuestro (o suyo)', self.cli(self.ana, 'estado', self.ident))
        self.assertNotEqual(self.persona(self.ana, 'decidir-union', self.ident, 'fase', 'suyo', ok=False).returncode, 0)
        self.assertEqual(self.registro(self.ana)['fase'], 'abandonada')  # sin confirmar, nada
        self.persona(self.ana, 'decidir-union', self.ident, 'fase', 'suyo', entrada='1\n')
        registro = self.registro(self.ana)
        self.assertEqual(registro['fase'], 'cerrada')
        self.assertNotIn('pendientes_de_union', registro)
        self.assertEqual(registro['eventos'][-1]['accion'], 'union_decidida')

    # --- un3: lo generado no choca y queda al día ------------------------------------------------------------------
    def test_un3_lo_generado_se_rehace(self):
        self.en_rama(self.ana, 'tarea/ana', 'nuevo', '--capacidad', 'calc', '--sufijo', 'ana', 'El de Ana')
        self.en_rama(self.beto, 'tarea/beto', 'nuevo', '--capacidad', 'calc', '--sufijo', 'beto', 'El de Beto')
        self.git(self.ana, 'checkout', '-q', 'main')
        (self.ana / 'kb/borrador.md').write_text('a medio escribir\n')  # de una persona, sin seguimiento
        self.integrar_las_dos(queda='?? kb/borrador.md')
        self.assertNotIn('kb/borrador.md', self.git(self.ana, 'show', '--name-only', '--format=', 'HEAD'))
        resumen = (self.ana / '.factory/resumen.md').read_text()
        self.assertIn('El de Ana', resumen)
        self.assertIn('El de Beto', resumen)
        self.assertIn('Rehacer lo generado', self.git(self.ana, 'log', '-1', '--format=%s'))
        self.assertEqual(len(self.git(self.ana, 'log', '-1', '--format=%P').split()), 1)
        self.cli(self.ana, 'resumen', '--verificar')
        self.cli(self.ana, 'kb', '--verificar')
        self.assertEqual(len(list((self.ana / 'kb/cambios').glob('*.md'))), 3)

    # --- un3: un merge con conflictos termina con git commit, y lo generado se rehace igual ------------------------
    def test_un3_con_conflicto_de_texto(self):
        def con_archivo(donde, texto):
            def hacer():
                (donde / 'x.txt').write_text(texto)
                self.cli(donde, 'nuevo', '--capacidad', 'calc', '--sufijo', texto.strip(), f'El de {texto.strip()}')
            return hacer
        self.en_rama(self.ana, 'tarea/ana', con_archivo(self.ana, 'ana\n'))
        self.en_rama(self.beto, 'tarea/beto', con_archivo(self.beto, 'beto\n'))
        self.git(self.ana, 'checkout', '-q', 'main')
        self.git(self.ana, 'fetch', '-q', 'origin')
        self.git(self.ana, 'merge', '-q', '--no-ff', '-m', 'Integrar ana', 'origin/tarea/ana')
        r = subprocess.run(['git', 'merge', '--no-ff', '-m', 'Integrar beto', 'origin/tarea/beto'], cwd=self.ana, env=self.env,
                           capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(self.git(self.ana, 'diff', '--name-only', '--diff-filter=U'), 'x.txt')  # sólo el de texto
        (self.ana / 'x.txt').write_text('ana y beto\n')
        self.git(self.ana, 'add', 'x.txt')
        self.git(self.ana, 'commit', '-q', '--no-edit')
        self.assertIn('Rehacer lo generado', self.git(self.ana, 'log', '-1', '--format=%s'))
        self.assertIn('El de beto', (self.ana / '.factory/resumen.md').read_text())
        self.assertEqual(self.git(self.ana, 'status', '--porcelain'), '')
        self.cli(self.ana, 'resumen', '--verificar')
        self.cli(self.ana, 'kb', '--verificar')


class UnirPuro(unittest.TestCase):
    """La unión sola, con registros como los que escribe Factory."""
    def decision(self, actor, cuando, **mas):
        return {'actor': actor, 'tipo_actor': 'persona', 'forma': 'decidio', 'modo': 'confirmacion', 'cuando': cuando, **mas}

    def medidas(self, *nombres):
        return {**self.decision('Ana', '2'), 'catalogos': {n: 'h' + n for n in nombres},
                'archivos_catalogo': {f'catalogos/{n}.oracle': 'a' + n for n in nombres}}

    def test_lo_de_una_sola_rama_se_toma(self):
        base = {'fase': 'spec', 'titulo': 'T', 'eventos': [{'accion': 'creado', 'cuando': '1'}],
                'medidas': {'r.uno': self.medidas('m1'), 'r.dos': self.medidas('m2')}}
        nuestro = {**base, 'modo': 'pair', 'eventos': base['eventos'] + [{'accion': 'mensaje', 'cuando': '3'}]}
        suyo = {**base, 'titulo': 'Otro', 'fase': 'rev', 'medidas': {'r.uno': self.medidas('m1')},  # sacó las de r.dos
                'eventos': base['eventos'] + [{'accion': 'mensaje', 'cuando': '2'}]}
        unido = unir_mod.unir(base, nuestro, suyo)
        self.assertEqual((unido['titulo'], unido['modo'], unido['fase']), ('Otro', 'pair', 'rev'))
        self.assertEqual(unido['medidas'], {'r.uno': self.medidas('m1')})  # sin r.dos, y no como None
        self.assertEqual([e['cuando'] for e in unido['eventos']], ['1', '2', '3'])
        self.assertNotIn('pendientes_de_union', unido)
        # Un pendiente que una rama ya resolvió no vuelve porque la otra no lo tocó.
        viejo = {'campo': 'cierre', 'camino': ['cierre'], 'nuestro': 1, 'suyo': 2}
        self.assertEqual(unir_mod.unir({'pendientes_de_union': [viejo]}, {}, {'pendientes_de_union': [viejo], 'x': 1}), {'x': 1})
        # Eventos del mismo segundo: cada rama conserva su orden.
        z, a, b = ({'accion': 'mensaje', 'texto': t, 'cuando': '5'} for t in ('z primero', 'a después', 'b de la otra'))
        # La misma hora: cada rama en su orden (z antes que a) y, entre ramas, un desempate que no depende de quién integra.
        self.assertEqual(unir_mod.unir({}, {'eventos': [z, a]}, {'eventos': [b]})['eventos'], [b, z, a])
        self.assertEqual(unir_mod.unir({}, {'eventos': [b]}, {'eventos': [z, a]})['eventos'], [b, z, a])
        # Un evento que una rama perdió sigue estando: el historial no se borra.
        self.assertEqual(unir_mod.unir({'eventos': [z, a]}, {'eventos': [a]}, {'eventos': [z, a, b]})['eventos'], [z, a, b])

    def test_lo_que_las_dos_cambiaron_distinto_queda_pendiente(self):
        # Dos cierres: una sola decisión pendiente, entera, que se elige con decidir-union.
        ana, beto = self.decision('Ana', '7', motivo='listo'), self.decision('Beto', '8', motivo='también')
        unido = unir_mod.unir({'cierre': None}, {'cierre': ana}, {'cierre': beto})
        self.assertEqual(unido['cierre'], ana)
        self.assertEqual(unido['pendientes_de_union'], [{'campo': 'cierre', 'camino': ['cierre'], 'nuestro': ana, 'suyo': beto}])
        self.assertIn('decidir-union X cierre nuestro (o suyo)', unir_mod.como_resolver('cierre', 'X'))
        # Dos responsables: no se mezcla la persona de una con los agentes de la otra.
        unido = unir_mod.unir({'responsable': {'persona': 'Cero', 'desde': '0', 'con': []}},
                              {'responsable': {'persona': 'Ana', 'desde': '1', 'con': []}},
                              {'responsable': {'persona': 'Beto', 'desde': '1', 'con': ['codex']}})
        self.assertEqual(unido['responsable'], {'persona': 'Ana', 'desde': '1', 'con': []})
        self.assertEqual([p['campo'] for p in unido['pendientes_de_union']], ['responsable'])
        # Dos medidas distintas del mismo requisito: no se juntan los catálogos; una pendiente por requisito.
        dos = unir_mod.unir({'medidas': {}}, {'medidas': {'r.uno': self.medidas('a'), 'r.dos': self.medidas('a')}},
                            {'medidas': {'r.uno': self.medidas('b'), 'r.dos': self.medidas('b')}})
        self.assertEqual(dos['medidas']['r.uno'], self.medidas('a'))
        self.assertEqual([p['campo'] for p in dos['pendientes_de_union']], ['medidas.r.uno', 'medidas.r.dos'])
        # Las medidas de un requisito resuelven sólo las de ese requisito (cuyo id lleva puntos).
        caminos = unir_mod.resueltos_por('medidas_confirmadas', 'r.uno')
        self.assertEqual([p['campo'] for p in dos['pendientes_de_union'] if not unir_mod.resuelto(p, caminos)], ['medidas.r.dos'])
        # Dos fases: pendiente, que resuelve la próxima decisión que la fija; aprobar la spec resuelve también su huella.
        self.assertEqual(unir_mod.unir({'fase': 'a'}, {'fase': 'b'}, {'fase': 'c'})['pendientes_de_union'][0]['campo'], 'fase')
        for accion, campo in (('revision_registrada', 'fase'), ('spec_aprobada', 'spec_sha256'), ('spec_aprobada', 'fase')):
            self.assertTrue(unir_mod.resuelto({'campo': campo, 'camino': [campo]}, unir_mod.resueltos_por(accion)), (accion, campo))
        self.assertFalse(unir_mod.resuelto({'campo': 'cierre', 'camino': ['cierre']}, unir_mod.resueltos_por('oracle_ejecutado')))

if __name__ == '__main__':
    unittest.main()
