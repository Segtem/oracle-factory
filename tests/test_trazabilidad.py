"""Trazabilidad por candidato: escenarios tz1–tz3 de la spec, con casos reales trazados y repositorios temporales."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_autoproduccion as _ap  # noqa: E402

f = _ap.f
from oracle_factory import estructura, trazabilidad  # noqa: E402

MODULO = '''def doble(x):
    return x * 2


def triple(x):
    y = x * 3
    return y


def externo(x):
    import ext_tz
    return ext_tz.uno(x)
'''
PRUEBAS = '''import unittest
from modulo_tz import doble, triple


class T(unittest.TestCase):
    def test_doble(self):
        self.assertEqual(doble(2), 4)

    def test_triple(self):
        self.assertEqual(triple(2), 6)

    def test_falla(self):
        self.assertEqual(doble(2), 5)

    def test_externo(self):
        from modulo_tz import externo
        self.assertEqual(externo(1), 1)
'''


@contextlib.contextmanager
def importable(carpeta: Path, *modulos: str):
    """La carpeta en sys.path y los módulos importados de nuevo desde ahí; al salir, todo como estaba."""
    sys.path.insert(0, str(carpeta))
    for m in modulos:
        sys.modules.pop(m, None)
    try:
        yield
    finally:
        sys.path.remove(str(carpeta))
        for m in modulos:
            sys.modules.pop(m, None)


def numero(texto: str, fragmento: str) -> int:
    return next(i for i, l in enumerate(texto.splitlines(), 1) if fragmento in l)


class Trazar(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.raiz = Path(tmp.name)
        (self.raiz / 'modulo_tz.py').write_text(MODULO)
        (self.raiz / 'test_modulo_tz.py').write_text(PRUEBAS)
        (self.raiz / '.venv').mkdir()
        (self.raiz / '.venv' / 'ext_tz.py').write_text('def uno(x):\n    return x\n')  # como una dependencia instalada

    def trazar(self, contratos):
        with importable(self.raiz, 'modulo_tz', 'test_modulo_tz'), importable(self.raiz / '.venv', 'ext_tz'):
            return trazabilidad.trazar(self.raiz, contratos)

    # --- tz1: el sensor registra qué líneas ejecuta cada caso ----------------------------------------------------------------
    def test_tz1_dos_requisitos_con_sus_casos(self):
        afuera = sys.gettrace()  # bajo el sensor de Factory, su traza

        def marca(frame, evento, arg):
            return None
        sys.settrace(marca)  # quien trazaba antes recupera su traza al terminar
        try:
            datos = self.trazar({'r_doble': ['test_modulo_tz.T.test_doble'],
                                 'r_triple': ['test_modulo_tz.T.test_triple', 'test_modulo_tz.T.test_externo']})
            self.assertIs(sys.gettrace(), marca)
        finally:
            sys.settrace(afuera)
        self.assertEqual(datos['esquema'], 'oracle-factory.trazabilidad-casos/1')
        self.assertEqual(datos['requisitos'], {'r_doble': ['test_modulo_tz.T.test_doble'],
                                               'r_triple': ['test_modulo_tz.T.test_externo', 'test_modulo_tz.T.test_triple']})
        externo = datos['casos']['test_modulo_tz.T.test_externo']['lineas']
        self.assertEqual(externo['modulo_tz.py'], [10, 11, 12])
        self.assertNotIn('.venv/ext_tz.py', externo)  # una dependencia instalada no es del proyecto
        doble = datos['casos']['test_modulo_tz.T.test_doble']
        triple = datos['casos']['test_modulo_tz.T.test_triple']
        self.assertEqual((doble['resultado'], triple['resultado']), ('ok', 'ok'))
        self.assertEqual(doble['lineas']['modulo_tz.py'], [1, 2])  # el def (se llamó) y su cuerpo
        self.assertEqual(triple['lineas']['modulo_tz.py'], [5, 6, 7])
        self.assertIn(numero(PRUEBAS, 'doble(2), 4'), doble['lineas']['test_modulo_tz.py'])
        self.assertTrue(all(not a.startswith(('.venv', '/')) for c in datos['casos'].values() for a in c['lineas']))

    def test_tz1_un_caso_que_falla(self):
        datos = self.trazar({'r': ['test_modulo_tz.T.test_falla', 'test_modulo_tz.T.test_triple']})
        self.assertEqual(datos['casos']['test_modulo_tz.T.test_falla']['resultado'], 'falla')
        self.assertEqual(datos['casos']['test_modulo_tz.T.test_falla']['lineas']['modulo_tz.py'], [1, 2])
        self.assertEqual(datos['casos']['test_modulo_tz.T.test_triple'],
                         {'resultado': 'ok', 'lineas': {'modulo_tz.py': [5, 6, 7], 'test_modulo_tz.py': [9, 10]}})


NOTAS = '''"""Ejemplo mínimo: decidir si una nota se puede guardar."""
MAXIMO = 80

def puede_guardar(titulo: str) -> bool:
    """Un título válido contiene al menos un carácter que no sea espacio."""
    limpio = titulo.strip()
    return bool(limpio)

# Un comentario agregado por el candidato.

def largo(titulo: str) -> int:
    return len(titulo)
'''


class Cruce(_ap.Base):
    cambio_medido = _ap.Autoproduccion.cambio_medido
    head = _ap.Autoproduccion.head

    def candidato(self, con_trazabilidad=True):
        """Un cambio en una rama, con un candidato que cambia notas.py y el README, y su evidencia."""
        with contextlib.redirect_stdout(io.StringIO()):
            self.ident = self.cambio_medido()
        self.git('checkout', '-qb', 'tarea')
        (self.root / 'examples/notas/notas.py').write_text(NOTAS)
        readme = self.root / 'examples/notas/README.md'
        readme.write_text(readme.read_text() + '\nUna línea más.\n')
        tarea = self.root / 'tareas' / self.ident / 'TAREA.md'
        tarea.write_text(tarea.read_text() + '\nUn registro que viaja con el candidato.\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'candidato')
        evidencia = estructura.ruta_canonica(self.root, self.ident, 'evidencia', self.head()[:7])
        evidencia.mkdir(parents=True)
        (evidencia / 'hechos.json').write_text('{}')
        self.rid = f.leer(self.ident)[1]['requisitos'][0]
        if con_trazabilidad:
            with importable(self.root / 'examples/notas', 'notas', 'test_notas'):
                datos = trazabilidad.trazar(self.root, {self.rid: ['test_notas.Notas.test_acepta_titulo_con_texto']})
            (evidencia / 'trazabilidad.json').write_text(json.dumps(datos))
        self.git('add', '.')
        self.git('commit', '-qm', 'evidencia')  # sólo .factory/: el candidato sigue siendo el commit anterior
        return evidencia

    def correr(self, *argv):
        salida, errores = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(errores):
            codigo = f.main(['--proyecto', str(self.root), *argv])
        return codigo, salida.getvalue(), errores.getvalue()

    # --- tz2: trazabilidad cruza los casos con el diff del candidato -----------------------------------------------------------
    def test_tz2_una_linea_cambiada_sin_respaldo(self):
        self.candidato()
        codigo, salida, errores = self.correr('trazabilidad', self.ident, '--json')
        self.assertEqual(codigo, 0, errores)
        datos = json.loads(salida)
        self.assertEqual((datos['esquema'], datos['candidato']), ('oracle-factory.trazabilidad/1', f.candidato_vigente(self.ident)))
        self.assertEqual(datos['base'], self.git('merge-base', 'HEAD', 'main'))
        notas = 'examples/notas/notas.py'
        respaldadas = datos['requisitos'][self.rid]['lineas'][notas]
        self.assertEqual(respaldadas, [numero(NOTAS, 'limpio = '), numero(NOTAS, 'return bool(limpio)')])
        self.assertEqual(datos['requisitos'][self.rid]['casos'],
                         [{'caso': 'test_notas.Notas.test_acepta_titulo_con_texto', 'resultado': 'ok'}])
        self.assertEqual(datos['sin_respaldo'], {notas: [numero(NOTAS, 'def largo'), numero(NOTAS, 'return len')]})
        comentario = numero(NOTAS, '# Un comentario')
        self.assertNotIn(comentario, respaldadas + datos['sin_respaldo'][notas])
        self.assertEqual(datos['no_rastreables'], ['examples/notas/README.md'])
        self.assertNotIn(numero(NOTAS, 'MAXIMO'), datos['sin_respaldo'][notas])  # corre al importar: la traza no lo ve
        # Un hunk que sólo borra no agrega líneas; y cada requisito ve sólo las líneas de sus casos.
        self.assertEqual(trazabilidad.cambios_del_diff('+++ b/a.py\n@@ -3,2 +2,0 @@\n'), {})
        dos = trazabilidad.cruzar({'requisitos': {'r1': ['c1'], 'r2': ['c2']},
                                   'casos': {'c1': {'lineas': {'a.py': [1]}}, 'c2': {'lineas': {'a.py': [2]}}}},
                                  {'a.py': {1, 2}}, {'a.py': {1, 2}})
        self.assertEqual((dos['requisitos']['r1']['lineas'], dos['requisitos']['r2']['lineas']), ({'a.py': [1]}, {'a.py': [2]}))
        _, texto, _ = self.correr('trazabilidad', self.ident)
        self.assertIn(f'{notas}: {numero(NOTAS, "limpio = ")}-{numero(NOTAS, "return bool(limpio)")}', texto)
        self.assertIn(f'{notas}: {numero(NOTAS, "def largo")}-{numero(NOTAS, "return len")}', texto)

    def test_tz2_sin_trazabilidad_en_la_evidencia(self):
        evidencia = self.candidato(con_trazabilidad=False)
        antes = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file() and '.git' not in p.parts}
        codigo, salida, errores = self.correr('trazabilidad', self.ident, '--json')
        self.assertEqual((codigo, salida), (1, ''))
        self.assertIn((evidencia / 'trazabilidad.json').relative_to(self.root).as_posix(), errores)
        self.assertIn('oracle_factory.trazabilidad.trazar', errores)
        self.assertEqual(antes, {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file() and '.git' not in p.parts})

    # --- tz3: los límites de la trazabilidad se declaran ---------------------------------------------------------------------
    def test_tz3_limites_a_la_vista(self):
        self.candidato()
        _, salida, _ = self.correr('trazabilidad', self.ident, '--json')
        _, texto, _ = self.correr('trazabilidad', self.ident)
        self.assertEqual(json.loads(salida)['limites'], list(trazabilidad.LIMITES))
        for limite in trazabilidad.LIMITES:
            self.assertIn(limite, texto)
        self.assertIn('no prueba que sea correcta', texto)
        self.assertIn('otro proceso', texto)


if __name__ == '__main__':
    unittest.main()
