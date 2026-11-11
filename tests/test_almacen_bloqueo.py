"""Registros fuera del repo del producto, etapa 4b1: escenarios ab1–ab2 de la spec (cada comando commitea sólo lo de su
cambio, con un bloqueo corto).

Mismo entorno que tests/test_almacen_commits.py (de donde se toman setUp y los ayudantes): producto y almacén son repos Git
temporales; HOME, XDG_CONFIG_HOME, GIT_CONFIG_GLOBAL y GIT_CONFIG_SYSTEM apuntan a archivos y carpetas temporales, también
en los procesos hijos, que heredan ese entorno. Ninguna prueba lee ni escribe el HOME real ni el ~/.gitconfig real.

ab1 corre la CLI en el mismo proceso y simula «otro cambio escribe mientras tanto» envolviendo el comando de verdad. ab2 usa
procesos de verdad (sys.executable) sincronizados con archivos. La interfaz que ab2 espera del bloqueo:
`almacenes.bloqueo(almacen, plazo=None)` es un context manager que espera el bloqueo exclusivo del commit del almacén (sin
plazo, hasta conseguirlo) y da True si lo consiguió; `almacenes.PLAZO_DEL_BLOQUEO` es el plazo, en segundos, de cada comando.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_almacen_commits as _commits  # noqa: E402

f = _commits.f
_Base = _commits.AlmacenCommits
RAIZ = Path(__file__).resolve().parents[1]

# El proceso hijo: corre la CLI con un punto de sincronización. argv: raíz del repo, modo, carpeta de sincronización, argumentos.
HIJO = r'''
import os, sys, time
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from oracle_factory import cli as f
modo, sinc, resto = sys.argv[2], Path(sys.argv[3]), sys.argv[4:]

def esperar(condicion):
    limite = time.monotonic() + 30
    while not condicion():
        if time.monotonic() > limite:
            sys.exit("plazo vencido esperando la sincronización")
        time.sleep(0.01)

if modo == "barrera":  # los dos procesos llegan juntos al commit
    real = f.almacenes.commitear
    def commitear(*a, **k):
        (sinc / f"llego-{os.getpid()}").touch()
        esperar(lambda: len(list(sinc.glob("llego-*"))) >= 2)
        return real(*a, **k)
    f.almacenes.commitear = commitear
elif modo == "trabaja":  # escribió su registro y sigue trabajando hasta que le digan
    real = f.mensaje
    def mensaje(*a, **k):
        real(*a, **k)
        (sinc / "trabajando").touch()
        esperar(lambda: (sinc / "seguir").exists())
    f.mensaje = mensaje
elif modo == "tiene-bloqueo":  # toma el bloqueo del commit del almacén y no lo suelta hasta que le digan
    with f.almacenes.bloqueo(Path(resto[0])) as tomado:
        if not tomado:
            sys.exit("no conseguí el bloqueo")
        (sinc / "tomado").touch()
        esperar(lambda: (sinc / "soltar").exists())
    sys.exit(0)
sys.exit(f.main(resto))
'''


def _de_cambio(ruta, ident):
    """¿La ruta del almacén es de ese cambio? Su carpeta en .factory/cambios/, tareas/ u openspec/changes/, o su nota."""
    return (any(ruta.startswith(f'{carpeta}/{ident}/') for carpeta in ('.factory/cambios', 'tareas', 'openspec/changes'))
            or ruta == f'kb/cambios/{ident}.md')


class AlmacenBloqueo(unittest.TestCase):
    setUp = _Base.setUp
    git_en, corre, bien, arbol, commits, estado_git = _Base.git_en, _Base.corre, _Base.bien, _Base.arbol, _Base.commits, _Base.estado_git
    archivos_del_ultimo, mensaje_del_ultimo, comando_que_escribe, registro = (_Base.archivos_del_ultimo, _Base.mensaje_del_ultimo,
                                                                              _Base.comando_que_escribe, _Base.registro)

    # --- ayudantes -----------------------------------------------------------------
    def nuevo(self, sufijo, raiz=None):
        self.bien('nuevo', f'Cambio {sufijo}', '--capacidad', 'notas', '--sufijo', sufijo, agente='claude-code')
        return next(p.name for p in ((raiz or self.almacen) / 'openspec/changes').iterdir() if p.is_dir() and p.name.endswith(f'-{sufijo}'))

    def conectado_con_dos(self):
        self.bien('conectar', str(self.almacen))
        self.bien('kb')  # el vault generado existe desde el primer `kb`; después cada comando lo refresca
        a, b = self.nuevo('aa'), self.nuevo('bb')
        self.assertEqual(self.estado_git(), '')
        return a, b

    def pendientes(self, repo=None):
        # en crudo y con -z: git_en recorta la salida, y eso le comía el espacio de « M» a la primera línea (y el «.» de .factory)
        salida = subprocess.run([*_commits.GIT, 'status', '--porcelain', '-z', '--untracked-files=all'], cwd=repo or self.almacen, check=True,
                                capture_output=True).stdout
        return {os.fsdecode(e[3:]) for e in salida.split(b'\0') if len(e) > 3}

    def b_escribe_durante(self, comando, b):
        """Envuelve la función de un comando de la CLI: antes de que termine, «otro» escribe en el cambio B (su registro, por
        Factory; y un archivo suyo en tareas/ a mano). Devuelve el patch."""
        real, mensaje = getattr(f, comando), f.mensaje

        def envuelto(*a, **k):
            resultado = real(*a, **k)
            otro = f.AGENTE
            f.AGENTE = 'codex'
            try:
                mensaje(b, 'B escribe mientras tanto', None)
            finally:
                f.AGENTE = otro
            (f.ROOT / 'tareas' / b / 'notas-de-b.md').write_text('B escribe a mano\n', encoding='utf-8')
            (f.ROOT / 'openspec/changes' / b / 'notas-de-b.md').write_text('B anota su propuesta\n', encoding='utf-8')  # también en openspec/
            comun = f.ROOT / 'tareas/plantillas/comun.md'  # una carpeta común que no tiene forma de ID: no es de ningún cambio
            comun.parent.mkdir(parents=True, exist_ok=True)
            comun.write_text('común a todos\n', encoding='utf-8')
            return resultado
        return patch.object(f, comando, envuelto)

    def hijo(self, modo, sinc, *args, esperar=True):
        orden = [sys.executable, '-c', HIJO, str(RAIZ), modo, str(sinc), *args]
        if not esperar:
            return subprocess.Popen(orden, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                    env=dict(os.environ))
        return subprocess.run(orden, stdin=subprocess.DEVNULL, capture_output=True, text=True, env=dict(os.environ), timeout=60)

    def esperar_archivo(self, ruta, proceso=None):
        limite = time.monotonic() + 30
        while not ruta.exists():
            if proceso is not None and proceso.poll() is not None:
                self.fail(f'el proceso terminó antes de {ruta.name}: {proceso.communicate()}')
            if time.monotonic() > limite:
                self.fail(f'plazo vencido esperando {ruta.name}')
            time.sleep(0.01)

    def commits_por_cambio(self, cuantos):
        """{id del cambio (o None): rutas} de los últimos `cuantos` commits del almacén."""
        vistos = {}
        for sha in self.git_en(self.almacen, 'rev-list', f'-{cuantos}', 'HEAD').splitlines():
            pie = self.git_en(self.almacen, 'log', '-1', '--format=%B', sha)
            ident = next((linea.split(': ', 1)[1] for linea in pie.splitlines() if linea.startswith('Cambio: ')), None)
            vistos.setdefault(ident, set()).update(self.git_en(self.almacen, 'show', '--name-only', '--format=', sha).splitlines())
        return vistos

    # --- ab1: con almacén aparte, cada comando commitea sólo lo de su cambio ---------------------------------------------
    def test_ab1_otro_cambio_escribe_mientras_tanto_y_su_archivo_no_entra(self):
        a, b = self.conectado_con_dos()
        cuenta = self.commits()
        with self.b_escribe_durante('mensaje', b):
            self.bien('mensaje', a, 'A trabaja', agente='claude-code')
        self.assertEqual(self.commits(), cuenta + 1)
        self.assertEqual(self.mensaje_del_ultimo()[-3], f'Cambio: {a}')
        del_ultimo = self.archivos_del_ultimo()
        self.assertIn(f'.factory/cambios/{a}/factory.json', del_ultimo)
        self.assertEqual({n for n in del_ultimo if _de_cambio(n, b)}, set())
        # lo de B quedó sin commitear: su registro (por Factory), su nota de kb (rehecha por el comando de A) y lo escrito a mano
        de_b = {f'.factory/cambios/{b}/factory.json', f'kb/cambios/{b}.md', f'tareas/{b}/notas-de-b.md', f'openspec/changes/{b}/notas-de-b.md'}
        self.assertIn('tareas/plantillas/comun.md', del_ultimo)  # lo común escrito mientras tanto sí entra
        self.assertEqual(self.pendientes(), de_b)
        self.assertIn('B escribe mientras tanto', self.registro(b))
        # y lo commitea el comando de B, aunque ya estuviera cambiado antes de empezar
        self.bien('mensaje', b, 'B sigue', agente='codex')
        self.assertEqual(self.mensaje_del_ultimo()[-3], f'Cambio: {b}')
        self.assertTrue(de_b <= self.archivos_del_ultimo(), self.archivos_del_ultimo())
        self.assertEqual({n for n in self.archivos_del_ultimo() if _de_cambio(n, a)}, set())
        self.assertEqual(self.estado_git(), '')

    def test_ab1_lo_comun_si_entra_y_nuevo_tampoco_lleva_lo_de_otro_cambio(self):
        self.bien('conectar', str(self.almacen))
        self.bien('kb')
        b = self.nuevo('bb')
        indice = (self.almacen / 'kb/README.md').read_bytes()
        cuenta = self.commits()
        with self.b_escribe_durante('nuevo', b):  # `nuevo` no recibe el ID del cambio: B escribe mientras A se crea
            tocados, _ = self.comando_que_escribe('nuevo', 'Cambio aa', '--capacidad', 'notas', '--sufijo', 'aa', agente='claude-code')
        a = next(p.name for p in (self.almacen / 'openspec/changes').iterdir() if p.name.endswith('-aa'))
        self.assertEqual(self.commits(), cuenta + 1)
        self.assertEqual(self.mensaje_del_ultimo()[-3], f'Cambio: {a}')
        self.assertNotEqual((self.almacen / 'kb/README.md').read_bytes(), indice)
        esperado = {n for n in tocados if not _de_cambio(n, b)}
        self.assertIn('kb/README.md', esperado)  # lo común
        self.assertIn(f'.factory/cambios/{a}/factory.json', esperado)  # lo suyo
        self.assertIn(f'openspec/changes/{a}/proposal.md', esperado)
        self.assertEqual(self.archivos_del_ultimo(), esperado)
        self.assertEqual(self.pendientes(), {n for n in tocados if _de_cambio(n, b)})

    def test_ab1_un_comando_sin_cambio_commitea_todo(self):
        a, b = self.conectado_con_dos()
        self.git_en(self.almacen, 'rm', '-q', f'kb/cambios/{a}.md', f'kb/cambios/{b}.md')
        self.git_en(self.almacen, 'commit', '-q', '-m', 'saca las notas para que kb las rehaga')
        cuenta = self.commits()
        tocados, _ = self.comando_que_escribe('kb')
        self.assertTrue({f'kb/cambios/{a}.md', f'kb/cambios/{b}.md'} <= tocados, tocados)
        self.assertEqual(self.commits(), cuenta + 1)
        self.assertEqual(self.archivos_del_ultimo(), tocados)
        self.assertFalse([linea for linea in self.mensaje_del_ultimo() if linea.startswith('Cambio:')])
        self.assertEqual(self.estado_git(), '')

    def test_ab1_sin_almacen_aparte_nada_cambia(self):
        self.bien('init')
        self.bien('kb')
        a, b = self.nuevo('aa', self.producto), self.nuevo('bb', self.producto)
        with self.b_escribe_durante('mensaje', b):
            self.bien('mensaje', a, 'A trabaja', agente='claude-code')
        self.assertEqual(self.commits(self.producto), 1)  # sólo el inicial de la fixture: sin almacén nadie commitea
        self.assertIn('B escribe mientras tanto', (self.producto / f'.factory/cambios/{b}/factory.json').read_text(encoding='utf-8'))
        self.assertIn('A trabaja', (self.producto / f'.factory/cambios/{a}/factory.json').read_text(encoding='utf-8'))
        self.assertEqual(self.commits(), 1)
        self.assertEqual(self.estado_git(), '')

    # --- ab2: el commit del almacén se hace con un bloqueo corto ----------------------------------------------------------
    def test_ab2_dos_comandos_que_terminan_a_la_vez_commitean_uno_despues_del_otro(self):
        a, b = self.conectado_con_dos()
        sinc = self.base / 'sinc'
        sinc.mkdir()
        # Un hook que tarda un poco y anota si dos commits se solaparon; Git tiene tomado el index.lock mientras corre.
        hook = self.almacen / '.git/hooks/pre-commit'
        hook.parent.mkdir(exist_ok=True)
        hook.write_text(f'#!/bin/sh\nd="{sinc}"\nif ls "$d"/dentro-* >/dev/null 2>&1; then touch "$d/solapados"; fi\n'
                        'touch "$d/dentro-$$"\nsleep 0.3\nrm -f "$d/dentro-$$"\n', encoding='utf-8')
        hook.chmod(0o755)
        cuenta = self.commits()
        procesos = [self.hijo('barrera', sinc, '--agente', agente, '--proyecto', str(self.producto), 'mensaje', ident, f'hola de {ident}',
                              esperar=False) for agente, ident in (('claude-code', a), ('codex', b))]
        salidas = [p.communicate(timeout=60) for p in procesos]
        for proceso, (salida, error) in zip(procesos, salidas):
            with self.subTest(pid=proceso.pid):
                self.assertEqual(proceso.returncode, 0, error)
                self.assertNotIn('index.lock', salida + error)
                self.assertNotIn('no se pudo commitear', salida + error)
        self.assertEqual(len(list(sinc.glob('llego-*'))), 2)  # los dos llegaron juntos al commit
        self.assertFalse((sinc / 'solapados').exists())
        self.assertEqual(self.commits(), cuenta + 2)
        vistos = self.commits_por_cambio(2)
        self.assertEqual(set(vistos), {a, b})
        for propio, otro in ((a, b), (b, a)):
            with self.subTest(cambio=propio):
                self.assertIn(f'.factory/cambios/{propio}/factory.json', vistos[propio])
                self.assertEqual({n for n in vistos[propio] if _de_cambio(n, otro)}, set())
        self.assertEqual(self.estado_git(), '')

    def test_ab2_el_bloqueo_no_se_toma_mientras_el_comando_trabaja(self):
        a, b = self.conectado_con_dos()
        sinc = self.base / 'sinc'
        sinc.mkdir()
        cuenta = self.commits()
        primero = self.hijo('trabaja', sinc, '--agente', 'claude-code', '--proyecto', str(self.producto), 'mensaje', a, 'A trabaja',
                            esperar=False)
        self.addCleanup(lambda: primero.poll() is None and primero.kill())
        self.esperar_archivo(sinc / 'trabajando', primero)
        segundo = self.hijo('normal', sinc, '--agente', 'codex', '--proyecto', str(self.producto), 'mensaje', b, 'B termina')
        self.assertEqual(segundo.returncode, 0, segundo.stderr)
        self.assertNotIn('no se pudo commitear', segundo.stdout + segundo.stderr)
        self.assertIsNone(primero.poll())  # el primero sigue trabajando: el segundo commiteó sin esperarlo
        self.assertEqual(self.commits(), cuenta + 1)
        self.assertEqual(self.mensaje_del_ultimo()[-3], f'Cambio: {b}')
        self.assertEqual({n for n in self.archivos_del_ultimo() if _de_cambio(n, a)}, set())
        (sinc / 'seguir').touch()
        salida, error = primero.communicate(timeout=60)
        self.assertEqual(primero.returncode, 0, error)
        self.assertNotIn('no se pudo commitear', salida + error)
        self.assertEqual(self.commits(), cuenta + 2)
        self.assertEqual(self.mensaje_del_ultimo()[-3], f'Cambio: {a}')
        self.assertIn(f'.factory/cambios/{a}/factory.json', self.archivos_del_ultimo())
        self.assertEqual(self.estado_git(), '')

    def test_ab2_si_el_bloqueo_no_se_consigue_avisa_y_deja_los_registros(self):
        a, _ = self.conectado_con_dos()
        sinc = self.base / 'sinc'
        sinc.mkdir()
        dueño = self.hijo('tiene-bloqueo', sinc, str(self.almacen), esperar=False)
        self.addCleanup(lambda: dueño.poll() is None and dueño.kill())
        self.esperar_archivo(sinc / 'tomado', dueño)
        cuenta = self.commits()
        with patch.object(f.almacenes, 'PLAZO_DEL_BLOQUEO', 0.3):
            inicio = time.monotonic()
            codigo, salida, error = self.corre('mensaje', a, 'A sin bloqueo', agente='claude-code')
            demora = time.monotonic() - inicio
        self.assertEqual(codigo, 0, error)
        self.assertLess(demora, 20)  # respetó el plazo: no se quedó esperando al otro
        impreso = (salida + error).casefold()
        self.assertIn('no se pudo commitear', impreso)
        self.assertIn('bloqueo', impreso)
        self.assertNotIn('traceback', impreso)
        self.assertIn('A sin bloqueo', self.registro(a))  # los registros quedaron en el disco
        self.assertEqual(self.commits(), cuenta)
        self.assertIn(f'.factory/cambios/{a}/factory.json', self.pendientes())
        (sinc / 'soltar').touch()
        dueño.communicate(timeout=60)
        self.assertEqual(dueño.returncode, 0)
        # con el bloqueo libre, el próximo comando de A commitea también lo que había quedado
        self.bien('mensaje', a, 'A otra vez', agente='claude-code')
        self.assertEqual(self.commits(), cuenta + 1)
        self.assertIn(f'.factory/cambios/{a}/factory.json', self.archivos_del_ultimo())
        self.assertEqual(self.estado_git(), '')


del _Base  # que el cargador no vuelva a correr las pruebas de la etapa 4a desde este módulo


if __name__ == '__main__':
    unittest.main()
