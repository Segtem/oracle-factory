"""Cada comando se comporta igual con y sin almacén (cx1), verificar no reemplaza funciones de cli (cx2) y hay un contexto explícito (cx3).

La matriz corre la CLI como proceso, con HOME y XDG_CONFIG_HOME propios (la conexión al almacén es por usuario), sobre un proyecto sin
almacén y uno conectado a un almacén aparte."""
import argparse
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE))
sys.path.insert(0, str(SOURCE / 'tests'))
import test_archivo as _archivo  # noqa: E402
from oracle_factory import contexto, parser, verificar  # noqa: E402

f = _archivo.f
CLI = [sys.executable, '-c', 'import sys; from oracle_factory.cli import main; sys.exit(main())']
# Cada subcomando con sus argumentos ({id}: el cambio del proyecto; {tmp}: una carpeta nueva al lado del proyecto) y, si difiere a
# propósito entre los dos modos, el motivo. Un subcomando nuevo tiene que entrar acá: si no, cx1 falla.
MATRIZ = {
    'init': ([], None), 'ejemplo': (['{tmp}/ej'], None), 'nuevo': (['--capacidad', 'demo', '--sufijo', 'm2', 'Otro'], None),
    'listar': ([], None), 'pedir-revision': (['{id}', '--a', 'nadie'], None), 'tomar': (['{id}'], None),
    'mensaje': (['{id}', 'hola'], None), 'soltar': (['{id}'], None), 'unir-registro': ([], None), 'unir-generado': ([], None),
    'rehacer-generado': ([], None), 'decidir-union': (['{id}', 'spec_aprobada', 'nuestro'], None), 'kb': (['--verificar'], None),
    'por-que': (['README.md:1'], None), 'log': (['{id}'], None),
    'hooks': ([], 'con almacén no se instala ningún hook en el repo del producto: los commits de Factory van al almacén'),
    'puerta': ([], None), 'verificar': ([], None), 'destinos': ([], None), 'autonomia': ([], None), 'autopilot': (['{id}'], None),
    'desplegar': (['--simular'], None), 'trailer': ([], None), 'tablero': ([], None), 'resumen': ([], None), 'archivar': ([], None),
    'migrar': (['--verificar'], None), 'donde': ([], None), 'trazabilidad': (['{id}'], None), 'ruta': (['{id}', 'evidencia'], None),
    'procedencia': ([], None), 'buscar': (['demo'], None),
    'agentes': (['--verificar'], 'con almacén la guía va en el repo del producto sólo con --en-el-repo; conectar no la escribe'),
    'skill': ([], None), 'mcp': ([], None), 'preguntar': (['qué es demo'], None), 'conectar': (['{tmp}/otro'], None),
    'desconectar': ([], None), 'sincronizar': ([], None), 'modo': (['{id}', 'autonomo'], None), 'medir': (['{id}', '--listar'], None),
    'revisar': (['{id}'], None), 'abandonar': (['{id}', '--motivo', 'x'], None), 'aprobar-spec': (['{id}'], None),
    'revision-preparar': (['{id}'], None), 'importar': (['{id}'], None), 'estado': (['{id}'], None), 'cerrar': (['{id}'], None),
    'revision': (['{id}', '--informe', 'x.md', '--revisor', 'r', '--decision', 'aprobar', '--hallazgos-abiertos', '0'], None),
    'evidencia': (['{id}'], None), 'juzgar': (['{id}'], None),
}


def subcomandos() -> list[str]:
    sub = next(a for a in parser.construir_parser()._actions if isinstance(a, argparse._SubParsersAction))
    return list(sub.choices)


class Proyectos(unittest.TestCase):
    """Dos proyectos —uno sin almacén y uno conectado a un almacén— con un cambio cada uno. Sin pruebas: la base de Matriz y Contexto."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        base = Path(cls.tmp.name).resolve()
        casa = base / 'casa'
        casa.mkdir()
        cls.entorno = {**{k: v for k, v in os.environ.items() if not k.startswith('GIT_') and k != 'FACTORY_AGENTE'},
                       'HOME': str(casa), 'XDG_CONFIG_HOME': str(casa / '.config'), 'PYTHONPATH': str(SOURCE),
                       'GIT_AUTHOR_NAME': 'P', 'GIT_AUTHOR_EMAIL': 'p@example.invalid', 'GIT_COMMITTER_NAME': 'P',
                       'GIT_COMMITTER_EMAIL': 'p@example.invalid', 'GIT_CEILING_DIRECTORIES': str(base)}
        cls.proyectos = {modo: cls.armar(base / modo, modo == 'con') for modo in ('sin', 'con')}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    @classmethod
    def git(cls, carpeta, *args):
        subprocess.run(['git', *args], cwd=carpeta, env=cls.entorno, check=True, capture_output=True)

    @classmethod
    def correr(cls, producto, *args, agente='claude-code'):
        r = subprocess.run([*CLI, '--proyecto', str(producto), *(['--agente', agente] if agente else []), *args], env=cls.entorno,
                           capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=300)
        return r.returncode, r.stdout + r.stderr

    @classmethod
    def armar(cls, carpeta, con_almacen):
        producto = carpeta / 'producto'
        producto.mkdir(parents=True)
        cls.git(producto, 'init', '-q', '-b', 'main')
        (producto / 'README.md').write_text('producto\n', encoding='utf-8')
        cls.git(producto, 'add', '-A')
        cls.git(producto, 'commit', '-qm', 'inicio')
        if con_almacen:
            almacen = carpeta / 'almacen'
            almacen.mkdir()
            cls.git(almacen, 'init', '-q', '-b', 'main')
            codigo, salida = cls.correr(producto, 'conectar', str(almacen), agente=None)
        else:
            codigo, salida = cls.correr(producto, 'init', agente=None)
        assert codigo == 0, salida
        codigo, salida = cls.correr(producto, 'nuevo', '--capacidad', 'demo', '--sufijo', 'mx', 'Demo')
        assert codigo == 0, salida
        ident = next(l.rstrip('/').split('/')[-2] for l in salida.splitlines() if l.rstrip().endswith('TAREA.md'))
        return producto, ident

class Matriz(Proyectos):
    # --- cx1: cada subcomando se comporta igual con y sin almacén ------------------------------------------------------------
    def test_cx1_un_subcomando_nuevo(self):
        self.assertEqual(sorted(subcomandos()), sorted(MATRIZ))

    def test_cx1_los_dos_modos(self):
        distintos = {}
        for comando, (argumentos, motivo) in MATRIZ.items():
            resultados = []
            for modo in ('sin', 'con'):
                producto, ident = self.proyectos[modo]
                args = [a.replace('{id}', ident).replace('{tmp}', str(producto.parent)) for a in argumentos]
                codigo, salida = self.correr(producto, comando, *args)
                self.assertNotIn('Traceback', salida, f'{comando} ({modo} almacén) tiró un traceback:\n{salida[-1500:]}')
                resultados.append(codigo)
            if resultados[0] != resultados[1]:
                distintos[comando] = resultados
        self.assertEqual(sorted(distintos), sorted(c for c, (_, motivo) in MATRIZ.items() if motivo), distintos)


class Verificar(unittest.TestCase):
    setUp, git = _archivo.Archivo.setUp, _archivo.Archivo.git  # su proyecto temporal, no sus pruebas

    # --- cx2: verificar no reemplaza funciones de cli -----------------------------------------------------------------------
    def test_cx2_varios_cambios(self):
        for i in range(3):
            ident = f.nuevo(f'Cambio {i}', 'demo')
            carpeta, estado = f.leer(ident)  # con una revisión registrada, verificar compara cada cambio con el producto
            estado['revision'] = {'decision': 'aprobar', 'contexto': {'head': '0' * 40, 'archivos_sha256': '0' * 64}}
            f.guardar(carpeta, estado)
        (self.root / 'openspec/changes' / '20990101-000000-abc-sin-registro').mkdir()  # nombre de cambio, pero sin registro: no cuenta
        self.git('add', '-A')
        self.git('commit', '-qm', 'tres cambios')
        self.assertEqual(verificar.datos(f)['cambios'], 3)
        original = f.contexto_producto
        vistos, listas = [], []
        real_del_cambio, real_git = verificar.del_cambio, f.git_producto

        def del_cambio(cli, ident):
            vistos.append(cli.contexto_producto)
            return real_del_cambio(cli, ident)

        def git_producto(args):
            if args[:3] == ['git', 'ls-files', '-z']:
                listas.append(args)
            return real_git(args)

        with patch.object(verificar, 'del_cambio', del_cambio), patch.object(f, 'git_producto', git_producto), \
                contextlib.redirect_stdout(io.StringIO()):
            verificar.comando(f, False)
        self.assertEqual(len(vistos), 3)
        self.assertTrue(all(v is original for v in vistos))
        self.assertIs(f.contexto_producto, original)
        self.assertEqual(len(listas), 1, listas)  # la huella del producto, una vez por corrida
        antes = f.contexto_producto()  # y al terminar la corrida deja de valer: un producto que cambia, cambia su huella
        (self.root / 'despues.txt').write_text('nuevo\n')
        self.assertNotEqual(f.contexto_producto(), antes)

    def test_cx2_fuera_de_verificar(self):
        (self.root / 'producto.txt').write_text('uno\n')
        self.git('add', '-A')
        self.git('commit', '-qm', 'producto')
        antes = f.contexto_producto()
        (self.root / 'producto.txt').write_text('dos\n')
        self.assertNotEqual(f.contexto_producto(), antes)


class Contexto(Proyectos):
    # --- cx3: hay un contexto explícito -------------------------------------------------------------------------------------
    def leer(self, modo):
        producto, _ = self.proyectos[modo]
        # Mientras corre el comando: al terminar, la CLI deja de apuntar al producto (PRODUCTO vuelve a None).
        guion = ('import json, sys; from oracle_factory import cli, contexto; vistos = []; listar = cli.listar\n'
                 'def espia(*a, **k):\n'
                 '    c = contexto.actual(cli)\n'
                 '    vistos.append({"producto": str(c.producto), "registros": str(c.registros), "agente": c.agente, '
                 '"con_almacen": c.con_almacen, "raiz": str(cli.ROOT), "prod": str(cli.PRODUCTO or cli.ROOT)})\n'
                 '    return listar(*a, **k)\n'
                 'cli.listar = espia; cli.main(sys.argv[1:]); print(json.dumps(vistos[0]))')
        r = subprocess.run([sys.executable, '-c', guion, '--proyecto', str(producto), '--agente', 'agente-x', 'listar'], env=self.entorno,
                           capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=120)
        return json.loads(r.stdout.strip().splitlines()[-1])

    def test_cx3_sin_almacen_y_con_almacen(self):
        sin, con = self.leer('sin'), self.leer('con')
        for datos in (sin, con):
            self.assertEqual((datos['producto'], datos['registros'], datos['agente']), (datos['prod'], datos['raiz'], 'agente-x'))
        self.assertFalse(sin['con_almacen'])
        self.assertEqual(sin['producto'], sin['registros'])
        self.assertTrue(con['con_almacen'])
        self.assertEqual(Path(con['producto']), self.proyectos['con'][0])
        self.assertEqual(Path(con['registros']), self.proyectos['con'][0].parent / 'almacen')
        with self.assertRaises(AttributeError):  # inmutable: lo arma la CLI, nadie lo cambia por el camino
            contexto.Contexto(producto=Path('a'), registros=Path('a'), agente=None).agente = 'otro'


if __name__ == '__main__':
    unittest.main()
