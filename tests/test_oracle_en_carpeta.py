"""El proyecto Oracle en una carpeta del proyecto: escenarios oc1–oc3, en repositorios temporales con Oracle real."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_estructura as _estructura  # noqa: E402

f, estructura = _estructura.f, _estructura.estructura
GIT = _estructura.GIT
ESCALARES = '''from oracle_metalenguaje import escalar


@escalar("caso_conocido")
def caso_conocido(nombre) -> bool:
    return nombre in {"vacío", "espacios", "válido"}
'''
MEDIDA_ESCALAR = '''medida notas.casos_conocidos:
    de comprobacion c
    donde caso_conocido(c.caso)
    resumen contar(1)
    umbral >= 3 segun contrato porque "el ejemplo observa tres casos conocidos"
    requiere comprobacion
    ambito universal
    alcance "cuenta los casos del ejemplo que reconoce el escalar del proyecto"
'''


class Proyecto(unittest.TestCase):
    """Un repositorio Git con su proyecto Oracle en medidas/, como Jam y LyraGASP."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'producto'
        (self.root / 'medidas').mkdir(parents=True)
        for name, value in [('ROOT', self.root), ('CHANGES', self.root / 'openspec/changes'), ('AGENTE', None)]:
            p = patch.object(f, name, value); p.start(); self.addCleanup(p.stop)
        p = patch.object(f, 'terminal_interactiva', return_value=True); p.start(); self.addCleanup(p.stop)
        self.stdout = io.StringIO()
        p = contextlib.redirect_stdout(self.stdout); p.__enter__(); self.addCleanup(p.__exit__, None, None, None)
        subprocess.run(['git', 'init', '-q', '-b', 'main'], cwd=self.root, check=True)
        self.assertEqual(f.ejecutar(['oracle', 'init', str(self.root / 'medidas')]).returncode, 0)

    escribe = _estructura.Estructura.escribe
    git = _estructura.Estructura.git
    salida = _estructura.Estructura.salida
    sha7 = _estructura.Estructura.sha7

    def cambio_juzgado(self, medidas=('notas.casos_ejecutados', 'notas.resultados')):
        ident = f.nuevo('Nota', con_ejemplo='notas')
        with self.escribe('1'):
            f.aprobar_spec(ident)
        f.importar(ident)
        rid = f.leer(ident)[1]['requisitos'][0]
        with self.escribe('1'):
            f.medir(ident, requisito_id=rid, medidas=list(medidas), quitar_sin_medir=True)
        self.git('add', '.')
        self.git('commit', '-qm', 'producto')
        informe = self.root / 'tareas' / ident / 'revision.md'
        informe.write_text('Fixture de revisión; no es una revisión real.\n')
        with self.escribe('1'):
            f.revisar(ident, informe, 'Persona fixture', 'aprobar', 0)
        destino = estructura.ruta_canonica(self.root, ident, 'evidencia', self.sha7()) / 'hechos.json'
        destino.parent.mkdir(parents=True)
        subprocess.run([sys.executable, 'examples/notas/sensor.py', '--salida', destino], cwd=self.root, check=True,
                       capture_output=True)
        f.juzgar(ident, destino)
        return ident, rid

    def config(self, **claves):
        ruta = self.root / '.factory/config.json'
        ruta.write_text(json.dumps({**json.loads(ruta.read_text()), **claves}))

    def arbol(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob('*')
                if p.is_file() and '.git' not in p.parts}


class OracleEnCarpeta(Proyecto):
    # --- oc1: el proyecto Oracle puede estar en una carpeta ------------------------------------------------------------------
    def test_oc1_un_proyecto_con_su_oracle_en_medidas(self):
        f.inicializar('medidas')
        ident, rid = self.cambio_juzgado()
        self.assertTrue((self.root / 'medidas/requisitos' / f'{rid}.requisito').is_file())
        self.assertFalse((self.root / 'requisitos').exists())
        self.assertFalse((self.root / 'catalogos').exists())
        self.assertTrue((self.root / 'medidas/catalogos/notas.resultados.oracle').is_file())
        self.assertEqual(f.leer(ident)[1]['oracle']['codigo'], 0)  # el juicio usó los catálogos de medidas/
        self.assertIn(f'fuente "openspec/changes/{ident}/', (self.root / 'medidas/requisitos' / f'{rid}.requisito').read_text())
        self.assertIn(('medidas', f'medidas/requisitos/{rid}.requisito', True),
                      {(x['gate'], x['ruta'], x['existe']) for x in estructura.donde(self.root, ident, f.leer(ident)[1], oracle='medidas')})
        self.salida()
        f.comando_donde(ident, None)
        self.assertIn(f'medidas/requisitos/{rid}.requisito', self.salida())
        f.comando_buscar(rid.rsplit('.', 1)[1], 50)
        self.assertRegex(self.salida(), rf'medidas/requisitos/{rid}\.requisito:\d+: .*\[{ident}\]')
        # Abandonar otro cambio quita sus requisitos de medidas/requisitos/.
        otro = f.nuevo('Otra', 'otra')
        spec = self.root / 'openspec/changes' / otro / 'specs/otra/spec.md'
        spec.write_text('# Capability: otra\n\n## ADDED Requirements\n\n### Requirement: algo\nTipo: funcional\n'
                        'El sistema SHALL hacer algo.\n\n#### Scenario: caso\n- GIVEN x\n- WHEN y\n- THEN z\n')
        for nombre in ('proposal.md', 'design.md'):
            (self.root / 'openspec/changes' / otro / nombre).write_text('# Otra\n\nCompleto.\n')
        with self.escribe('1'):
            f.aprobar_spec(otro)
        f.importar(otro)
        [suyo] = f.leer(otro)[1]['requisitos']
        self.assertTrue((self.root / 'medidas/requisitos' / f'{suyo}.requisito').is_file())
        with self.escribe('1'):
            f.abandonar(otro)
        self.assertFalse((self.root / 'medidas/requisitos' / f'{suyo}.requisito').exists())

    def test_oc1_sin_la_clave_todo_sigue_en_la_raiz(self):
        f.inicializar()
        self.assertNotIn('oracle', json.loads((self.root / '.factory/config.json').read_text()))
        self.assertEqual(f.proyecto_oracle(), self.root)
        ident, rid = self.cambio_juzgado()
        self.assertTrue((self.root / 'requisitos' / f'{rid}.requisito').is_file())
        self.assertFalse((self.root / 'medidas/requisitos' / f'{rid}.requisito').exists())
        self.assertEqual(f.leer(ident)[1]['oracle']['codigo'], 0)

    def test_oc1_una_carpeta_invalida(self):
        f.inicializar('medidas')
        ident = f.nuevo('Nota', con_ejemplo='notas')
        (self.root / 'vacia').mkdir()
        afuera = Path(self.tmp.name) / 'afuera'
        afuera.mkdir()
        (afuera / 'oracle.json').write_text('{}')
        (self.root / 'enlace').symlink_to(afuera)
        for carpeta, causa in ((str(self.root / 'medidas'), 'relativa al proyecto, sin ..'), ('../afuera', 'relativa al proyecto, sin ..'),
                               ('\\afuera', 'relativa al proyecto, sin ..'), ('C:/afuera', 'relativa al proyecto, sin ..'),
                               ('medidas\\..\\..', 'relativa al proyecto, sin ..'),
                               ('vacia', 'ahí no hay un proyecto Oracle'), ('enlace', 'ahí no hay un proyecto Oracle')):
            self.config(oracle=carpeta)
            antes = self.arbol()
            errores = io.StringIO()
            with contextlib.redirect_stderr(errores), self.escribe('1'):
                codigo = f.main(['--proyecto', str(self.root), 'aprobar-spec', ident])
            self.assertEqual(codigo, 1, carpeta)
            self.assertIn(causa, errores.getvalue(), carpeta)
            self.assertEqual(self.arbol(), antes, carpeta)  # no escribió nada
            errores = io.StringIO()
            with contextlib.redirect_stderr(errores):
                self.assertEqual(f.main(['--proyecto', str(self.root), 'buscar', 'algo']), 1, carpeta)  # buscar también
            self.assertIn(causa, errores.getvalue(), carpeta)
        self.config(oracle=3)
        with self.assertRaisesRegex(f.FactoryError, 'oracle \\(la carpeta del proyecto Oracle\\)'):
            f.proyecto_oracle()

    # --- oc2: init adopta un proyecto Oracle existente ------------------------------------------------------------------------
    def test_oc2_un_repositorio_con_medidas_y_tareas(self):
        self.assertEqual(f.ejecutar(['tasks', 'init', str(self.root), '--sin-readme']).returncode, 0)
        self.assertEqual(f.ejecutar(['tasks', 'new', 'Una tarea de antes', '--proyecto', str(self.root)]).returncode, 0)
        (self.root / 'medidas/requisitos').mkdir(exist_ok=True)
        (self.root / 'medidas/requisitos/viejo.algo.requisito').write_text('requisito viejo.algo:\n    texto "de antes"\n')
        antes = {p: v for p, v in self.arbol().items() if p.startswith(('tareas/', 'medidas/'))}
        f.inicializar('medidas')
        self.assertEqual(json.loads((self.root / '.factory/config.json').read_text())['oracle'], 'medidas')
        for nombre in ('oracle.json', 'catalogos', 'requisitos', 'corpus', 'diferencial', 'relaciones', 'macros'):
            self.assertFalse((self.root / nombre).exists(), nombre)
        despues = self.arbol()
        self.assertEqual({p: v for p, v in despues.items() if p in antes}, antes)  # las tareas y medidas/ siguen iguales
        self.assertTrue((self.root / 'openspec/changes').is_dir())
        # Un init posterior, sin --oracle, respeta la carpeta configurada y tampoco crea Oracle en la raíz.
        f.inicializar()
        self.assertEqual(json.loads((self.root / '.factory/config.json').read_text())['oracle'], 'medidas')
        self.assertFalse((self.root / 'oracle.json').exists())
        self.assertFalse((self.root / 'catalogos').exists())
        # Una carpeta sin proyecto Oracle no se adopta, y no se crea nada.
        otra = Path(self.tmp.name) / 'otro'
        otra.mkdir()
        (otra / 'medidas').mkdir()
        with patch.object(f, 'ROOT', otra), patch.object(f, 'CHANGES', otra / 'openspec/changes'):
            with self.assertRaisesRegex(f.FactoryError, '--oracle es la carpeta de un proyecto Oracle que ya existe'):
                f.inicializar('medidas')
        self.assertEqual(sorted(p.name for p in otra.iterdir()), ['medidas'])

    # --- oc3: los escalares del proyecto se ejecutan sólo si el proyecto lo declara ------------------------------------------
    def preparar_escalares(self):
        f.inicializar('medidas')
        (self.root / 'medidas/escalares.py').write_text(ESCALARES)
        (self.root / 'medidas/catalogos/notas.casos_conocidos.oracle').write_text(MEDIDA_ESCALAR)

    def llamadas_a_oracle(self):
        """Un doble de f.ejecutar que anota cada llamada y la deja pasar."""
        llamadas, ejecutar = [], f.ejecutar

        def mirar(args):
            llamadas.append(args)
            return ejecutar(args)
        return llamadas, patch.object(f, 'ejecutar', mirar)

    def test_oc3_un_proyecto_con_escalares(self):
        self.preparar_escalares()
        self.config(confiar_escalares=True)
        llamadas, mirar = self.llamadas_a_oracle()
        with mirar:
            ident, _ = self.cambio_juzgado(medidas=('notas.casos_conocidos', 'notas.resultados'))
        coberturas = [a for a in llamadas if a[:2] == ['oracle', 'cobertura']]
        self.assertEqual(len(coberturas), 2)  # la cobertura y la cobertura con los hechos
        self.assertTrue(all('--confiar-escalares' in a for a in coberturas))
        self.assertEqual(f.con_escalares(), ['--confiar-escalares'])
        self.assertEqual(f.leer(ident)[1]['oracle']['codigo'], 0)
        veredicto = (self.root / f.leer(ident)[1]['oracle']['informe']).read_text()
        self.assertIn('notas.casos_conocidos', veredicto)

    def test_oc3_sin_declararlo(self):
        self.preparar_escalares()
        # Medido y juzgado con la clave; después el proyecto la saca y se vuelve a juzgar.
        self.config(confiar_escalares=True)
        ident, rid = self.cambio_juzgado(medidas=('notas.casos_conocidos', 'notas.resultados'))
        self.config(confiar_escalares=False)
        hechos = self.root / f.leer(ident)[1]['oracle']['hechos']
        self.assertEqual(f.con_escalares(), [])  # sin la clave, Factory no pasa --confiar-escalares
        llamadas, mirar = self.llamadas_a_oracle()
        with mirar, contextlib.redirect_stderr(io.StringIO()), self.assertRaises(f.FactoryError) as error:
            f.juzgar(ident, hechos)
        # El error de Oracle (no ejecuta escalares externas sin confianza) llega a la persona, con la clave que lo resuelve,
        # antes de correr nada: ninguna llamada a Oracle ni un juicio a medias.
        self.assertIn('repetí con `--confiar-escalares`', str(error.exception))
        self.assertIn('"confiar_escalares": true', str(error.exception))
        self.assertEqual([a for a in llamadas if a[0] == 'oracle'], [])
        self.assertEqual(f.leer(ident)[1]['oracle']['codigo'], 0)  # el juicio anterior no se toca
        # medir, que carga el catálogo, dice la causa y la clave que lo resuelve; estado no se cae.
        with self.assertRaises(f.FactoryError) as error:
            f.medir(ident, listar_opciones=True)
        self.assertIn('--confiar-escalares', str(error.exception))
        self.assertIn('"confiar_escalares": true', str(error.exception))
        texto = io.StringIO()
        with contextlib.redirect_stdout(texto), contextlib.redirect_stderr(io.StringIO()):
            f.mostrar(ident)
        self.assertIn(f'medidas de {rid}: el catálogo de notas.casos_conocidos', texto.getvalue())
        self.config(confiar_escalares='sí')
        with self.assertRaisesRegex(f.FactoryError, 'confiar_escalares \\(true/false\\)'):
            f.config_proyecto()


if __name__ == '__main__':
    unittest.main()
