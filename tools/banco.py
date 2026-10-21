"""El banco de concurrencia: dos personas con sus agentes sobre un mismo proyecto, a la vez y de a turnos.

    python tools/banco.py --salida CARPETA [--semilla N] [--solo ESCENARIO ...] [--simultaneo]
    python tools/banco.py --salida CARPETA --real FILAS.json   # una corrida con agentes reales, aparte

Cada escenario arma un repositorio central (bare) con un proyecto de Factory, y dos clones: Ana y Beto, cada uno con su
identidad de Git, sus hooks y un agente de prueba (agente-ana, agente-beto). Las decisiones de una persona se toman en una
terminal (tools/terminal.py), como cuando la persona escribe; las de un agente, con --agente. Lo simultáneo corre en
el orden que sale de la semilla (reproducible, queda en la traza), o con --simultaneo en procesos simultáneos de verdad.
Al terminar cada escenario se audita: cada decisión que alguien tomó tiene que seguir en el registro y a su nombre.

Por escenario se anota: si terminó bien, si hubo conflicto y cuándo se detectó (antes de integrar, al integrar, después,
o nunca), las decisiones perdidas o atribuidas a otra persona, la evidencia o revisión vieja que se dio por vigente, y el
trabajo rehecho. Un escenario que encuentra un defecto de Factory no se esconde: queda con resultado «defecto» y su
detalle. El informe es banco.json y banco.txt.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from importlib import metadata
import json
import os
from pathlib import Path
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.terminal import en_terminal  # noqa: E402

CLI = [sys.executable, '-c', 'import sys; from oracle_factory.cli import main; sys.exit(main())']
DETECCIONES = ('ninguno', 'antes', 'al_integrar', 'despues', 'nunca')
ID = re.compile(r'^\d{8}-\d{6}-[a-z0-9_-]+$')
PERSONAS = ('Ana', 'Beto')
AGENTES = ('agente-ana', 'agente-beto', 'oracle-factory')


def clave(evento: dict) -> str:
    """Un evento sin su autor: para encontrarlo en otro registro y ver si quedó a nombre de quien lo hizo."""
    return json.dumps({k: v for k, v in evento.items() if k not in ('actor', 'tipo_actor')}, sort_keys=True, ensure_ascii=False)


class Persona:
    """Una persona en su clon: git con su identidad, la CLI como persona (en una terminal) o como su agente."""

    def __init__(self, banco: 'Escenario', nombre: str):
        self.banco, self.nombre = banco, nombre
        self.agente = f'agente-{nombre.lower()}'
        self.dir = banco.tmp / nombre.lower()
        self.env = {**os.environ, 'PYTHONPATH': str(ROOT), 'GIT_CEILING_DIRECTORIES': str(banco.tmp),
                    'GIT_AUTHOR_EMAIL': f'{nombre.lower()}@banco.invalid', 'GIT_COMMITTER_EMAIL': f'{nombre.lower()}@banco.invalid'}

    def git(self, *args, ok=True) -> subprocess.CompletedProcess:
        p = subprocess.run(['git', *args], cwd=self.dir, env=self.env, capture_output=True, text=True)
        if ok and p.returncode:
            raise AssertionError(f'{self.nombre}: git {" ".join(args)}: {p.stderr.strip()}')
        return p

    def agente_hace(self, *args, ok=True) -> subprocess.CompletedProcess:
        antes = self._antes(args)
        p = subprocess.run([*CLI, '--agente', self.agente, *args], cwd=self.dir, env=self.env, capture_output=True,
                           text=True, stdin=subprocess.DEVNULL)
        if ok and p.returncode:
            raise AssertionError(f'{self.agente}: {" ".join(args)}: {(p.stderr or p.stdout).strip()[-400:]}')
        self._anotar(args, antes, self.agente, p)
        return p

    def decide(self, *args, entrada='1\n1\n1\n', ok=True) -> subprocess.CompletedProcess:
        """Una decisión de la persona, desde su terminal: elige la primera opción de cada menú."""
        antes = self._antes(args)
        p = en_terminal([*CLI, *args], cwd=self.dir, env=self.env, entrada=entrada)
        if ok and p.returncode:
            raise AssertionError(f'{self.nombre}: {" ".join(args)}: {(p.stderr or p.stdout).strip()[-400:]}')
        self._anotar(args, antes, self.nombre, p)
        return p

    # Lo que cada orden agregó al registro de su cambio queda anotado con quién la dio: al final del escenario,
    # Escenario.auditar comprueba que siga estando y a nombre de quien la dio.
    def _ident(self, args) -> str | None:
        return next((a for a in args if ID.match(str(a)) and (self.dir / '.factory/cambios' / a).is_dir()), None)

    def _antes(self, args) -> set:
        ident = self._ident(args)
        return {clave(x) for x in self.registro(ident)['eventos']} if ident else set()

    def _anotar(self, args, antes: set, autor: str, p) -> None:
        ident = self._ident(args) or (self.banco.ultimo_cambio(self) if args and args[0] == 'nuevo' else None)
        if p.returncode or not ident:
            return
        nuevos = [x for x in self.registro(ident)['eventos'] if clave(x) not in antes]
        if args[0] == 'mensaje':  # con otros procesos escribiendo a la vez, el suyo es el de su texto
            nuevos = [x for x in nuevos if x.get('accion') == 'mensaje' and x.get('texto') == args[2]]
        for x in nuevos:
            if x.get('actor') == autor or args[0] == 'mensaje':
                self.banco.esperados.append((ident, clave(x), autor, self))

    def registro(self, ident: str) -> dict:
        return json.loads((self.dir / '.factory/cambios' / ident / 'factory.json').read_text())

    def escribir(self, ruta: str, texto: str) -> None:
        destino = self.dir / ruta
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(texto)

    def commit(self, mensaje: str) -> str:
        self.git('add', '-A')
        self.git('commit', '-q', '-m', mensaje)
        return self.git('rev-parse', 'HEAD').stdout.strip()

    def nuevo_cambio(self, sufijo: str, titulo: str) -> str:
        """Un cambio con su spec aprobada por la persona y sus requisitos importados por su agente."""
        self.agente_hace('nuevo', '--capacidad', 'calc', '--sufijo', sufijo, titulo)
        ident = sorted(p.name for p in (self.dir / 'openspec/changes').iterdir() if p.name.endswith(sufijo))[-1]
        carpeta = self.dir / 'openspec/changes' / ident
        (carpeta / 'proposal.md').write_text(f'# {titulo}\n\n## Why\n\nPara el banco.\n\n## What changes\n\n{titulo}.\n\n'
                                             '## Out of scope\n\nNada.\n\n## Human decisions\n\nNinguna.\n')
        (carpeta / 'specs/calc/spec.md').write_text(
            '# Capability: calc\n\n## ADDED Requirements\n\n'
            f'### Requirement: {sufijo} funciona\nTipo: funcional\nThe system SHALL {titulo.lower()}.\n\n'
            '#### Scenario: uno\n- GIVEN a\n- WHEN b\n- THEN c\n')
        self.decide('aprobar-spec', ident)
        self.agente_hace('importar', ident)
        return ident


class Escenario:
    def __init__(self, nombre: str, tmp: Path, semilla: int, tal_cual: bool = False, simultaneo: bool = False):
        self.nombre, self.tmp = nombre, tmp
        self.azar = random.Random(f'{semilla}:{nombre}')
        self.fila = {'escenario': nombre, 'resultado': 'ok', 'conflicto': 'ninguno', 'decisiones_perdidas': 0,
                     'mal_atribuidas': 0, 'evidencia_vieja_aceptada': 0, 'rehecho': 0, 'detalle': []}
        self.central = tmp / 'central.git'
        self.tal_cual = tal_cual  # el proyecto como lo deja init, sin ayudas del banco
        self.simultaneo = simultaneo
        self.esperados: list = []  # (cambio, evento sin autor, autor, persona en cuyo clon se escribió)
        self.final: Persona | None = None  # donde todo tiene que haber llegado al terminar (quien integra), si lo hay
        self.traza: list = []  # el orden en que corrió lo que se intercala
        self.armar()
        self.ana, self.beto = Persona(self, 'Ana'), Persona(self, 'Beto')
        for p in (self.ana, self.beto):
            subprocess.run(['git', 'clone', '-q', str(self.central), str(p.dir)], check=True, capture_output=True)
            p.git('config', 'user.name', p.nombre)
            p.git('config', 'user.email', f'{p.nombre.lower()}@banco.invalid')
            p.agente_hace('hooks')

    def armar(self) -> None:
        """El proyecto de prueba: Factory inicializado, un módulo calc con su prueba, en main del repositorio central."""
        semilla = self.tmp / 'semilla'
        semilla.mkdir()
        env = {**os.environ, 'PYTHONPATH': str(ROOT), 'GIT_CEILING_DIRECTORIES': str(self.tmp)}
        git = lambda *a: subprocess.run(['git', '-c', 'user.name=Banco', '-c', 'user.email=banco@banco.invalid', *a],
                                        cwd=semilla, env=env, check=True, capture_output=True)
        git('init', '-q', '-b', 'main')
        subprocess.run([*CLI, 'init'], cwd=semilla, env=env, check=True, capture_output=True, stdin=subprocess.DEVNULL)
        (semilla / 'calc.py').write_text('def sumar(a, b):\n    return a + b\n')
        (semilla / 'test_calc.py').write_text('import calc\n\nassert calc.sumar(2, 3) == 5\n')
        if not self.tal_cual:  # s0 mide que init deje lo que un clon necesita; los demás escenarios no dependen de eso
            for carpeta in [d for d in semilla.rglob('*') if d.is_dir() and '.git' not in d.parts and not any(d.iterdir())]:
                (carpeta / '.gitkeep').write_text('')
        git('add', '-A')
        git('commit', '-q', '-m', 'el proyecto de prueba')
        subprocess.run(['git', 'clone', '-q', '--bare', str(semilla), str(self.central)], check=True, capture_output=True)

    def nota(self, texto: str) -> None:
        self.fila['detalle'].append(texto)

    def a_la_vez(self, *trabajos):
        """Lo que dos personas (o una y su agente) hacen al mismo tiempo: en modo simultáneo, en procesos simultáneos de
        verdad (el orden lo decide el sistema); si no, uno tras otro en el orden que sale de la semilla, que queda en la traza.
        Cada trabajo es (etiqueta, función, *argumentos); devuelve los resultados en el orden dado."""
        if self.simultaneo:
            with ThreadPoolExecutor(len(trabajos)) as pool:
                futuros = [pool.submit(f, *a) for _, f, *a in trabajos]
                return [x.result() for x in futuros]
        orden = list(range(len(trabajos)))
        self.azar.shuffle(orden)
        resultados = [None] * len(trabajos)
        for i in orden:
            etiqueta, f, *a = trabajos[i]
            self.traza.append(etiqueta)
            resultados[i] = f(*a)
        return resultados

    def ultimo_cambio(self, p: 'Persona') -> str | None:
        cambios = sorted((x for x in (p.dir / '.factory/cambios').iterdir() if x.is_dir()), key=lambda x: x.stat().st_mtime)
        return cambios[-1].name if cambios else None

    def auditar(self) -> None:
        """Para todos los escenarios: cada decisión que alguien tomó sigue en el registro (en el clon de quien integra si
        el cambio llegó ahí; si no, en el de quien la tomó) y a nombre de quien la tomó; y nadie aparece como autor de
        algo sin ser una de las dos personas o sus agentes."""
        vistos: dict = {}
        for ident, k, autor, p in self.esperados:
            donde = self.final if self.final and (self.final.dir / '.factory/cambios' / ident).is_dir() else p
            if (donde.nombre, ident) not in vistos:
                vistos[(donde.nombre, ident)] = donde.registro(ident)['eventos']
            # Dos personas pueden hacer lo mismo en el mismo segundo: sin el autor, sus eventos son iguales.
            actores = [x.get('actor') for x in vistos[(donde.nombre, ident)] if clave(x) == k]
            if not actores:
                self.fila['decisiones_perdidas'] += 1
                self.defecto(f'en el clon de {donde.nombre}, {ident} perdió un evento de {autor}: {k[:120]}')
            elif autor not in actores:
                self.fila['mal_atribuidas'] += 1
                self.defecto(f'en {ident}, un evento de {autor} quedó a nombre de {actores}')
        for (nombre, ident), eventos in vistos.items():
            for x in eventos:
                if x.get('actor') not in (*PERSONAS, *AGENTES, 'Banco'):
                    self.fila['mal_atribuidas'] += 1
                    self.defecto(f'en {ident} hay un evento de «{x.get("actor")}», que no es nadie del banco')
        malas = sum(self.fila[k] for k in ('decisiones_perdidas', 'mal_atribuidas', 'evidencia_vieja_aceptada'))
        if malas and self.fila['resultado'] == 'ok':  # un número malo nunca queda en un escenario ok
            self.defecto(f'{malas} decisiones perdidas, mal atribuidas o evidencia vieja aceptada')
        self.nota(f'auditadas {len(self.esperados)} decisiones: ninguna perdida ni mal atribuida' if self.fila['resultado'] == 'ok'
                  else f'auditadas {len(self.esperados)} decisiones')

    def defecto(self, texto: str) -> None:
        self.fila['resultado'] = 'defecto'
        self.nota(texto)

    def detectado(self, cuando: str) -> None:
        if DETECCIONES.index(cuando) > DETECCIONES.index(self.fila['conflicto']):
            self.fila['conflicto'] = cuando

    def pruebas_pasan(self, persona: Persona) -> bool:
        return subprocess.run([sys.executable, 'test_calc.py'], cwd=persona.dir, capture_output=True).returncode == 0

    def integrar(self, quien: Persona, rama: str) -> bool:
        """Quien integra trae la rama del central y la mergea en main; un conflicto se cuenta como detectado al integrar."""
        quien.git('checkout', '-q', 'main')
        quien.git('pull', '-q', '--no-rebase', 'origin', 'main')
        quien.git('fetch', '-q', 'origin', rama)
        p = quien.git('merge', '--no-ff', '-q', '-m', f'Integrar {rama}', f'origin/{rama}', ok=False)
        if p.returncode:
            self.detectado('al_integrar')
            en_conflicto = quien.git('diff', '--name-only', '--diff-filter=U').stdout.split()
            self.nota(f'conflicto al integrar {rama}: ' + (', '.join(en_conflicto) or (p.stderr or p.stdout).strip()[-300:]))
            return False
        quien.git('push', '-q', 'origin', 'main')
        return True


# --- los escenarios --------------------------------------------------------------------------------------------------
def eventos_de(registro: dict) -> list[tuple]:
    return [(e.get('accion'), e.get('actor'), e.get('cuando')) for e in registro.get('eventos') or []]


def s0_clon_recien_hecho(e: Escenario) -> None:
    """Beto clona el proyecto tal como lo dejó init y crea un cambio: tiene que poder."""
    vacias = sorted(str(d.relative_to(e.tmp / 'semilla')) for d in (e.tmp / 'semilla').rglob('*')
                    if d.is_dir() and '.git' not in d.parts and 'local' not in d.parts and not any(d.iterdir()))  # local/ es local
    if vacias:
        e.nota(f'init deja carpetas vacías, que Git no versiona y un clon no tiene: {vacias}')
    p = e.beto.agente_hace('nuevo', '--capacidad', 'calc', '--sufijo', 'primero', 'El primer cambio de Beto', ok=False)
    if p.returncode:
        e.detectado('antes')
        e.defecto('en un clon recién hecho no se puede crear un cambio: '
                  + (p.stderr or p.stdout).strip().splitlines()[-1][:300])


def s1_paralelo_disjunto(e: Escenario) -> None:
    """Ana y Beto, cada uno con su cambio y su archivo, a la vez; Ana integra los dos."""
    def frente(p: Persona, sufijo: str, archivo: str) -> tuple[str, list]:
        p.git('checkout', '-q', '-b', f'tarea/{sufijo}')
        ident = p.nuevo_cambio(sufijo, f'Agregar {archivo}')
        p.decide('tomar', ident)
        p.escribir(archivo, f'# {archivo}\n')
        p.commit(f'{sufijo}: {archivo}')
        p.git('push', '-q', 'origin', f'tarea/{sufijo}')
        return ident, eventos_de(p.registro(ident))
    e.final = e.ana
    (id_a, ev_a), (id_b, ev_b) = e.a_la_vez(('Ana', frente, e.ana, 'restar', 'restar.py'),
                                             ('Beto', frente, e.beto, 'multiplicar', 'multiplicar.py'))
    for rama in e.azar.sample(['tarea/restar', 'tarea/multiplicar'], 2):  # el orden de integración sale de la semilla
        if not e.integrar(e.ana, rama):
            e.defecto(f'dos frentes que no comparten archivos chocaron al integrar {rama}')
            return
    for ident, antes, autor in ((id_a, ev_a, 'Ana'), (id_b, ev_b, 'Beto')):
        despues = eventos_de(e.ana.registro(ident))
        e.fila['decisiones_perdidas'] += len(set(antes) - set(despues))
        e.fila['mal_atribuidas'] += sum(1 for x in e.ana.registro(ident)['eventos']
                                        if x.get('tipo_actor') == 'persona' and x.get('actor') != autor)
    # Cada commit de producto lleva el trailer de su cambio.
    for ident, archivo in ((id_a, 'restar.py'), (id_b, 'multiplicar.py')):
        trailer = e.ana.git('log', '-1', '--format=%(trailers:key=Cambio,valueonly)', '--', archivo).stdout.strip()
        if trailer != ident:
            e.fila['mal_atribuidas'] += 1
            e.nota(f'{archivo}: el commit dice Cambio «{trailer}», no {ident}')


def s2_mismo_archivo(e: Escenario) -> None:
    """Los dos tocan la misma línea de calc.py en sus cambios: el conflicto se ve al integrar, no después."""
    e.final = e.ana
    for p, sufijo, cuerpo in ((e.ana, 'redondeo', 'round(a + b, 2)'), (e.beto, 'enteros', 'int(a) + int(b)')):
        p.git('checkout', '-q', '-b', f'tarea/{sufijo}')
        p.nuevo_cambio(sufijo, f'Sumar con {sufijo}')
        p.escribir('calc.py', f'def sumar(a, b):\n    return {cuerpo}\n')
        p.commit(f'{sufijo}: calc.py')
        p.git('push', '-q', 'origin', f'tarea/{sufijo}')
    e.integrar(e.ana, 'tarea/redondeo')
    if e.integrar(e.ana, 'tarea/enteros'):
        e.detectado('nunca')
        e.defecto('dos cambios de la misma línea se integraron sin conflicto')
    e.ana.git('merge', '--abort', ok=False)


def s3_semantico(e: Escenario) -> None:
    """Ana renombra sumar; Beto agrega un uso de sumar. Cada uno pasa sus pruebas; juntos fallan."""
    e.final = e.ana
    e.ana.git('checkout', '-q', '-b', 'tarea/renombrar')
    e.ana.nuevo_cambio('renombrar', 'Renombrar sumar a suma')
    e.ana.escribir('calc.py', 'def suma(a, b):\n    return a + b\n')
    e.ana.escribir('test_calc.py', 'import calc\n\nassert calc.suma(2, 3) == 5\n')
    e.ana.commit('renombrar: suma')
    e.beto.git('checkout', '-q', '-b', 'tarea/doble')
    e.beto.nuevo_cambio('doble', 'Agregar doble')
    e.beto.escribir('doble.py', 'import calc\n\ndef doble(a):\n    return calc.sumar(a, a)\n')
    e.beto.escribir('test_doble.py', 'import doble\n\nassert doble.doble(2) == 4\n')
    e.beto.commit('doble: doble.py')
    solos = e.pruebas_pasan(e.ana) and subprocess.run([sys.executable, 'test_doble.py'], cwd=e.beto.dir).returncode == 0
    if not solos:
        e.defecto('las pruebas no pasaban por separado: el escenario no prueba lo que dice')
        return
    for p, rama in ((e.ana, 'tarea/renombrar'), (e.beto, 'tarea/doble')):
        p.git('push', '-q', 'origin', rama)
    e.integrar(e.ana, 'tarea/renombrar')
    e.integrar(e.ana, 'tarea/doble')
    juntos = subprocess.run([sys.executable, 'test_doble.py'], cwd=e.ana.dir, capture_output=True).returncode == 0
    if juntos:
        e.defecto('el escenario semántico no falló junto')
        return
    # Al integrar, el protocolo pide correr las pruebas antes de dar el merge por bueno: ahí se ve.
    e.detectado('al_integrar')
    e.nota('pasan solos y fallan juntos: lo detectan las pruebas de quien integra (Factory no corre nada al mergear)')


def s4_tomar_a_la_vez(e: Escenario) -> None:
    """Ana crea un cambio y lo sube; Ana y Beto lo toman a la vez desde sus clones. Al juntar las ramas Factory no elige
    responsable: avisa, Beto lo releva acordado con Ana, y el cambio se integra con las dos tomas en su historia."""
    e.final = e.ana
    e.ana.git('checkout', '-q', '-b', 'tarea/compartido')
    ident = e.ana.nuevo_cambio('compartido', 'Un cambio para dos')
    e.ana.commit('compartido: el cambio')
    e.ana.git('push', '-q', 'origin', 'tarea/compartido')
    e.beto.git('fetch', '-q', 'origin')
    e.beto.git('checkout', '-q', '-b', 'tarea/compartido', 'origin/tarea/compartido')
    e.a_la_vez(('Ana', e.ana.decide, 'tomar', ident), ('Beto', e.beto.decide, 'tomar', ident))
    for p in (e.ana, e.beto):
        p.commit(f'compartido: lo tomó {p.nombre}')
    e.ana.git('push', '-q', 'origin', 'tarea/compartido')
    if not e.beto.git('push', '-q', 'origin', 'tarea/compartido', ok=False).returncode:
        e.detectado('nunca')
        e.defecto('el segundo push no chocó')
        return
    e.detectado('al_integrar')
    if e.beto.git('pull', '-q', '--no-rebase', 'origin', 'tarea/compartido', ok=False).returncode:
        e.defecto('dos «tomar» del mismo cambio chocan en factory.json al sincronizar')
        return
    registro = e.beto.registro(ident)
    if [x.get('campo') for x in registro.get('pendientes_de_union') or []] != ['responsable']:
        e.defecto(f'al unir las dos tomas, Factory no dejó el responsable para decidir: {registro.get("pendientes_de_union")}')
    if 'al unir dos ramas, responsable' not in e.beto.agente_hace('estado', ident).stdout:
        e.defecto('estado no avisa que el responsable quedó sin decidir')
    # Lo acuerdan: Beto lo releva. El aviso se va y queda constancia.
    e.beto.decide('tomar', ident, '--relevo')
    registro = e.beto.registro(ident)
    if registro.get('pendientes_de_union') or registro['responsable']['persona'] != 'Beto':
        e.defecto('el relevo acordado no resolvió el responsable')
    e.beto.commit('compartido: Beto lo releva, acordado')
    e.beto.git('push', '-q', 'origin', 'tarea/compartido')
    if e.integrar(e.ana, 'tarea/compartido'):
        tomas = [x.get('actor') for x in e.ana.registro(ident)['eventos'] if x.get('accion') == 'tomado']
        e.nota(f'integrado en main con las tomas de {tomas}')


def s5_decisiones_simultaneas(e: Escenario) -> None:
    """Un mismo registro, escrito a la vez: en el clon de Ana, Ana en su terminal y su agente (seis mensajes cada uno), y en
    el de Beto, Beto con otros seis en su rama del mismo cambio. Al integrar, los dieciocho están, cada uno a nombre de
    quien lo escribió."""
    e.final = e.ana
    e.ana.git('checkout', '-q', '-b', 'tarea/charla')
    ident = e.ana.nuevo_cambio('charla', 'Un registro concurrido')
    e.ana.commit('charla: el cambio')
    e.ana.git('push', '-q', 'origin', 'tarea/charla')
    e.beto.git('fetch', '-q', 'origin')
    e.beto.git('checkout', '-q', '-b', 'tarea/charla-beto', 'origin/tarea/charla')
    trabajos = [(f'Ana {i}', e.ana.decide, 'mensaje', ident, f'Ana {i}') for i in range(6)]
    trabajos += [(f'agente-ana {i}', e.ana.agente_hace, 'mensaje', ident, f'agente-ana {i}') for i in range(6)]
    trabajos += [(f'Beto {i}', e.beto.decide, 'mensaje', ident, f'Beto {i}') for i in range(6)]
    e.a_la_vez(*trabajos)
    e.ana.commit('charla: los de Ana')
    e.ana.git('push', '-q', 'origin', 'tarea/charla')
    e.beto.commit('charla: los de Beto')
    e.beto.git('push', '-q', 'origin', 'tarea/charla-beto')
    e.integrar(e.ana, 'tarea/charla')
    if not e.integrar(e.ana, 'tarea/charla-beto'):
        e.defecto('los mensajes del mismo cambio en dos ramas chocaron al integrar')
        return
    autores = sorted(x.get('actor') for x in e.ana.registro(ident)['eventos'] if x.get('accion') == 'mensaje')
    if autores != sorted(['Ana'] * 6 + ['agente-ana'] * 6 + ['Beto'] * 6):
        e.defecto(f'en main los mensajes quedaron a nombre de {autores}')


def s6_mismo_id(e: Escenario) -> None:
    """Ana y Beto crean, en el mismo segundo y en sus clones, un cambio con el mismo sufijo: los IDs tienen que salir
    distintos (los separan los caracteres al azar) y los dos cambios integrarse sin conflicto."""
    e.final = e.ana
    for p in (e.ana, e.beto):
        p.git('checkout', '-q', '-b', f'tarea/igual-{p.nombre.lower()}')
    for intento in range(3):
        time.sleep(1 - time.time() % 1)  # el principio de un segundo, con el reloj de verdad
        ids = e.a_la_vez(('Ana', e.ana.nuevo_cambio, f'igual{intento}', 'Un cambio con el mismo nombre'),
                         ('Beto', e.beto.nuevo_cambio, f'igual{intento}', 'Un cambio con el mismo nombre'))
        if ids[0][:15] == ids[1][:15]:
            break
    else:
        e.defecto(f'tres intentos sin crear los dos cambios en el mismo segundo: {ids}')
        return
    e.nota(f'IDs del mismo segundo: {ids}')
    for p in (e.ana, e.beto):
        p.commit(f'igual: de {p.nombre}')
        p.git('push', '-q', 'origin', f'tarea/igual-{p.nombre.lower()}')
    if ids[0] == ids[1]:
        e.defecto('dos cambios creados en el mismo segundo en dos clones tienen el mismo ID')
        return
    e.integrar(e.ana, 'tarea/igual-ana')
    if not e.integrar(e.ana, 'tarea/igual-beto'):
        e.defecto('dos cambios con IDs distintos chocaron al integrar')


def s7_generados(e: Escenario) -> None:
    """Dos cambios integrados uno tras otro tocan resumen.md y kb/: con los hooks de Factory no chocan, porque después del
    merge se rehacen solos (en un commit aparte, sin trabajo de nadie)."""
    e.final = e.ana
    e.ana.agente_hace('kb')  # el vault se genera una vez en main y lo trae cada clon
    e.ana.agente_hace('resumen')
    e.ana.commit('el vault')
    e.ana.git('push', '-q', 'origin', 'main')
    e.beto.git('pull', '-q', '--no-rebase', 'origin', 'main')
    for p, sufijo in ((e.ana, 'uno'), (e.beto, 'dos')):
        p.git('checkout', '-q', '-b', f'tarea/{sufijo}')
        p.nuevo_cambio(sufijo, f'El cambio {sufijo}')
        p.agente_hace('resumen')
        p.commit(f'{sufijo}: el cambio')
        p.git('push', '-q', 'origin', f'tarea/{sufijo}')
    e.integrar(e.ana, 'tarea/uno')
    if not e.integrar(e.ana, 'tarea/dos'):
        e.defecto('los archivos generados chocaron al integrar aunque Factory los rehace después del merge')
        e.ana.git('merge', '--abort', ok=False)
        return
    if 'Rehacer lo generado' in e.ana.git('log', '-3', '--format=%s').stdout:
        e.nota('Factory rehízo resumen.md y kb/ después del merge, en un commit aparte (no es trabajo de nadie)')
    for orden in (['kb', '--verificar'], ['resumen', '--verificar']):
        if e.ana.agente_hace(*orden, ok=False).returncode:
            e.defecto(f'después de integrar, {" ".join(orden)} falla')


def a1_relevo_atrasado(e: Escenario) -> None:
    """El lunes Ana toma un cambio y avanza; el jueves Beto, con su clon del lunes, lo releva y sigue."""
    e.final = e.beto
    e.ana.git('checkout', '-q', '-b', 'tarea/semana')
    ident = e.ana.nuevo_cambio('semana', 'Un cambio de toda la semana')
    e.ana.decide('tomar', ident)
    e.ana.escribir('semana.py', 'LUNES = 1\n')
    e.ana.commit('semana: lunes')
    e.ana.agente_hace('mensaje', ident, 'dejé el lunes hecho; falta el jueves')
    e.ana.commit('semana: nota')
    e.ana.git('push', '-q', 'origin', 'tarea/semana')
    # Beto no sincronizó desde el lunes: trae la rama recién al retomar.
    e.beto.git('fetch', '-q', 'origin')
    e.beto.git('checkout', '-q', '-b', 'tarea/semana', 'origin/tarea/semana')
    visto = e.beto.registro(ident)
    if not any(x.get('accion') == 'mensaje' for x in visto['eventos']):
        e.defecto('Beto no ve el mensaje que dejó Ana')
    sin_relevo = e.beto.decide('tomar', ident, ok=False)
    if sin_relevo.returncode == 0:
        e.defecto('Beto tomó el cambio de Ana sin --relevo')
    else:
        e.detectado('antes')
    e.beto.decide('tomar', ident, '--relevo')
    r = e.beto.registro(ident)
    if r['responsable']['persona'] != 'Beto' or r['eventos'][-1].get('relevo_de') != 'Ana':
        e.defecto('el relevo no dejó constancia de quién lo tenía')
    e.beto.escribir('semana.py', 'LUNES = 1\nJUEVES = 4\n')
    e.beto.commit('semana: jueves')
    trailer = e.beto.git('log', '-1', '--format=%(trailers:key=Cambio,valueonly)').stdout.strip()
    if trailer != ident:
        e.fila['mal_atribuidas'] += 1
        e.nota(f'el commit de Beto dice Cambio «{trailer}»')


def a2_evidencia_vieja(e: Escenario) -> None:
    """Beto tiene evidencia y una revisión aprobada de su candidato; Ana integra antes un cambio de producto. Al traer
    main, ni la evidencia ni la revisión valen, y Factory no deja cerrar con ellas."""
    e.final = e.beto
    e.beto.git('checkout', '-q', '-b', 'tarea/lento')
    ident = e.beto.nuevo_cambio('lento', 'Un cambio que tarda')
    e.beto.escribir('lento.py', 'X = 1\n')
    e.beto.commit('lento: producto')
    sha = e.beto.git('rev-parse', '--short=7', 'HEAD').stdout.strip()
    evidencia = e.beto.dir / '.factory/cambios' / ident / 'candidatos' / sha / 'evidencia'
    evidencia.mkdir(parents=True)
    (evidencia / 'resultado.json').write_text('{"exitoso": true}\n')
    informe = e.beto.dir / 'tareas' / ident / 'revision.md'
    informe.write_text('Revisión del banco: sin hallazgos.\n')
    e.beto.decide('revision', ident, '--informe', str(informe), '--revisor', 'Beto', '--decision', 'aprobar',
                  '--hallazgos-abiertos', '0')
    e.beto.commit('lento: evidencia y revisión')
    antes = json.loads(e.beto.agente_hace('estado', ident, '--json').stdout)
    if not (antes.get('revision') or {}).get('vigente'):
        e.defecto(f'la revisión recién registrada no figura vigente: {antes.get("revision")}')
        return
    # Ana integra antes un cambio de producto.
    e.ana.escribir('calc.py', 'def sumar(a, b):\n    return b + a\n')
    e.ana.commit('otro: calc.py')
    e.ana.git('push', '-q', 'origin', 'main')
    e.beto.git('pull', '-q', '--no-rebase', 'origin', 'main')
    despues = json.loads(e.beto.agente_hace('estado', ident, '--json').stdout)
    if despues.get('candidato') == sha:
        e.fila['evidencia_vieja_aceptada'] += 1
        e.defecto('después de traer main con otro producto, el candidato viejo sigue vigente')
    if (despues.get('revision') or {}).get('vigente'):
        e.fila['evidencia_vieja_aceptada'] += 1
        e.defecto('después de traer main con otro producto, la revisión vieja sigue vigente')
    if e.beto.decide('cerrar', ident, ok=False).returncode == 0:
        e.fila['evidencia_vieja_aceptada'] += 1
        e.defecto('Factory dejó cerrar con la evidencia y la revisión viejas')
    if e.fila['evidencia_vieja_aceptada'] == 0:
        e.detectado('antes')
        e.nota('al traer main, el candidato y la revisión viejos dejan de estar vigentes y cerrar se niega: hay que '
               'producir evidencia y revisar otra vez')
        e.fila['rehecho'] += 1


def a3_registro_en_dos_ramas(e: Escenario) -> None:
    """Un mismo cambio: Ana deja un mensaje en su rama y Beto otro en la suya; al juntarlas, ¿se conservan los dos?"""
    e.final = e.beto
    e.ana.git('checkout', '-q', '-b', 'tarea/doble-rama')
    ident = e.ana.nuevo_cambio('dobl', 'Un cambio en dos ramas')
    e.ana.commit('dobl: el cambio')
    e.ana.git('push', '-q', 'origin', 'tarea/doble-rama')
    e.beto.git('fetch', '-q', 'origin')
    e.beto.git('checkout', '-q', '-b', 'tarea/doble-beto', 'origin/tarea/doble-rama')
    e.ana.agente_hace('mensaje', ident, 'de Ana')
    e.ana.commit('dobl: mensaje de Ana')
    e.ana.git('push', '-q', 'origin', 'tarea/doble-rama')
    e.beto.agente_hace('mensaje', ident, 'de Beto')
    e.beto.commit('dobl: mensaje de Beto')
    p = e.beto.git('pull', '-q', '--no-rebase', 'origin', 'tarea/doble-rama', ok=False)
    if p.returncode:
        e.detectado('al_integrar')
        e.defecto('el registro del cambio editado en dos ramas choca en factory.json: hay que unir los eventos a mano '
                  'y Factory no ayuda (un «ours» o «theirs» pierde los de la otra persona)')
        e.fila['decisiones_perdidas'] += 1  # con la resolución más común (quedarse con un lado), se pierde un mensaje
        return
    textos = {x.get('texto') for x in e.beto.registro(ident)['eventos'] if x.get('accion') == 'mensaje'}
    if textos != {'de Ana', 'de Beto'}:
        e.fila['decisiones_perdidas'] += 2 - len(textos & {'de Ana', 'de Beto'})
        e.defecto(f'al unir el registro quedaron {sorted(textos)}')


def a4_mensajes_de_a_turnos(e: Escenario) -> None:
    """Durante la semana, Ana y Beto escriben en el mismo cambio, cada uno en su clon y sin traer lo del otro antes; al
    final de cada día sincronizan. Ningún mensaje se pierde y quedan en el orden en que se escribieron."""
    e.final = e.ana
    e.ana.git('checkout', '-q', '-b', 'tarea/charla')
    ident = e.ana.nuevo_cambio('charlas', 'Un cambio conversado')
    e.ana.commit('charlas: el cambio')
    e.ana.git('push', '-q', '-u', 'origin', 'tarea/charla')
    e.beto.git('fetch', '-q', 'origin')
    e.beto.git('checkout', '-q', '-b', 'tarea/charla', '--track', 'origin/tarea/charla')
    escritos = []
    for dia in range(1, 4):
        hoy = e.a_la_vez(*[(f'día {dia}: {p.nombre}', lambda p=p, t=f'día {dia}: {p.nombre}': (p.agente_hace('mensaje', ident, t), t)[1])
                           for p in (e.ana, e.beto)])
        escritos += hoy
        for p in e.azar.sample([e.ana, e.beto], 2):  # quién sincroniza primero sale de la semilla
            p.commit(f'charlas: día {dia}')
            p.git('pull', '-q', '--no-rebase', 'origin', 'tarea/charla')
            if p.git('push', '-q', 'origin', 'tarea/charla', ok=False).returncode:
                e.defecto(f'el día {dia} {p.nombre} no pudo subir después de traer lo del otro')
                return
    e.ana.git('pull', '-q', '--no-rebase', 'origin', 'tarea/charla')
    eventos = [x for x in e.ana.registro(ident)['eventos'] if x.get('accion') == 'mensaje']
    vistos = [x.get('texto') for x in eventos]
    e.fila['decisiones_perdidas'] = len(set(escritos) - set(vistos))
    if sorted(vistos) != sorted(escritos):
        e.defecto(f'los mensajes quedaron {vistos}, no {escritos}')
    if [x.get('cuando') for x in eventos] != sorted(x.get('cuando') for x in eventos):
        e.defecto('los mensajes no quedaron en el orden en que se escribieron')


def a5_trailers_y_vault_en_otro_clon(e: Escenario) -> None:
    """Ana escribe una línea en su cambio; Beto, desde su clon, ve el vault al día y sabe por qué existe esa línea."""
    e.final = e.beto
    e.ana.agente_hace('kb')  # el proyecto usa kb/: se genera una vez en main y lo trae cada clon
    e.ana.commit('el vault')
    e.ana.git('push', '-q', 'origin', 'main')
    e.beto.git('pull', '-q', '--no-rebase', 'origin', 'main')
    e.ana.git('checkout', '-q', '-b', 'tarea/limite')
    ident = e.ana.nuevo_cambio('limite', 'Un límite al resultado')
    e.ana.decide('tomar', ident)
    e.ana.escribir('calc.py', 'LIMITE = 1000\n\ndef sumar(a, b):\n    return min(a + b, LIMITE)\n')
    e.ana.commit('limite: calc.py')
    e.ana.git('push', '-q', 'origin', 'tarea/limite')
    e.beto.git('fetch', '-q', 'origin')
    e.beto.git('checkout', '-q', '-b', 'tarea/limite', 'origin/tarea/limite')
    verificar = e.beto.agente_hace('kb', '--verificar', ok=False)
    if verificar.returncode:
        e.defecto('en el clon de Beto el vault no está al día con lo que subió Ana: ' + verificar.stderr.strip()[-300:])
    datos = json.loads(e.beto.agente_hace('por-que', 'calc.py:1', '--json').stdout)
    if (datos.get('cambio') or {}).get('id') != ident:
        e.fila['mal_atribuidas'] += 1
        e.defecto(f'desde el clon de Beto, la línea de Ana no lleva a su cambio: {datos.get("cambio")}')


ESCENARIOS = {
    's0_clon_recien_hecho': s0_clon_recien_hecho, 's1_paralelo_disjunto': s1_paralelo_disjunto, 's2_mismo_archivo': s2_mismo_archivo, 's3_semantico': s3_semantico,
    's4_tomar_a_la_vez': s4_tomar_a_la_vez, 's5_decisiones_simultaneas': s5_decisiones_simultaneas,
    's6_mismo_id': s6_mismo_id, 's7_generados': s7_generados,
    'a1_relevo_atrasado': a1_relevo_atrasado, 'a2_evidencia_vieja': a2_evidencia_vieja,
    'a3_registro_en_dos_ramas': a3_registro_en_dos_ramas, 'a4_mensajes_de_a_turnos': a4_mensajes_de_a_turnos,
    'a5_trailers_y_vault_en_otro_clon': a5_trailers_y_vault_en_otro_clon,
}


def correr(semilla: int, solo: list[str] | None = None, simultaneo: bool = False) -> list[dict]:
    filas = []
    for nombre, funcion in ESCENARIOS.items():
        if solo and nombre not in solo:
            continue
        with tempfile.TemporaryDirectory(prefix=f'banco-{nombre}-') as d:
            inicio = time.monotonic()
            try:
                esc = Escenario(nombre, Path(d), semilla, tal_cual=nombre == 's0_clon_recien_hecho', simultaneo=simultaneo)
                funcion(esc)
                esc.auditar()
                fila = {**esc.fila, 'traza': esc.traza}
            except Exception as error:  # noqa: BLE001 — un escenario que se rompe es un resultado, no un corte del banco
                fila = {'escenario': nombre, 'resultado': 'error', 'conflicto': 'nunca', 'decisiones_perdidas': 0,
                        'mal_atribuidas': 0, 'evidencia_vieja_aceptada': 0, 'rehecho': 0,
                        'detalle': [f'{type(error).__name__}: {error}'[:600]], 'traza': []}
            fila['segundos'] = round(time.monotonic() - inicio, 1)
            filas.append(fila)
    return filas


def informe(filas: list[dict], semilla: int, real: bool = False, simultaneo: bool = False) -> dict:
    # Reproducible: lo que se intercala corre en el orden de la semilla (la traza lo muestra). Simultáneo, no.
    return {'esquema': 'oracle-factory.banco/1', 'semilla': semilla, 'reproducible': not real and not simultaneo,
            'modo': 'real' if real else 'simultaneo' if simultaneo else 'ordenado',
            'versiones': {p: metadata.version(p) for p in ('oracle-factory', 'oracle-metalenguaje', 'oracle-task', 'oracle-clue')}
            | {'python': sys.version.split()[0], 'git': subprocess.run(['git', '--version'], capture_output=True, text=True).stdout.strip()},
            'escenarios': filas}


def texto(datos: dict) -> str:
    modo = {'real': ' (corrida real, no reproducible)', 'simultaneo': ' (procesos simultáneos, no reproducible)'}.get(datos.get('modo'), '')
    lineas = [f"Banco de concurrencia — semilla {datos['semilla']}{modo}", '']
    for f in datos['escenarios']:
        lineas.append(f"{f['resultado']:<8} {f['escenario']:<28} conflicto: {f['conflicto']:<11} perdidas {f['decisiones_perdidas']} · "
                      f"mal atribuidas {f['mal_atribuidas']} · evidencia vieja {f['evidencia_vieja_aceptada']} · rehecho {f['rehecho']} "
                      f"· {f['segundos']} s")
        lineas += [f'           {d}' for d in f['detalle']]
    return '\n'.join(lineas) + '\n'


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--salida', type=Path, required=True)
    parser.add_argument('--semilla', type=int, default=20261021)
    parser.add_argument('--solo', nargs='*')
    parser.add_argument('--simultaneo', action='store_true', help='lo que se intercala, en procesos simultáneos de verdad '
                                                                  '(si no, en el orden de la semilla)')
    parser.add_argument('--real', type=Path, help='registrar una corrida con agentes reales: un JSON con sus filas, en el '
                                                  'mismo formato; queda en banco-real.json/.txt, marcada no reproducible')
    args = parser.parse_args(argv)
    args.salida.mkdir(parents=True, exist_ok=True)
    real = args.real is not None
    filas = json.loads(args.real.read_text(encoding='utf-8')) if real else correr(args.semilla, args.solo, args.simultaneo)
    datos = informe(filas, args.semilla, real=real, simultaneo=args.simultaneo)
    nombre = 'banco-real' if real else 'banco-simultaneo' if args.simultaneo else 'banco'
    (args.salida / f'{nombre}.json').write_text(json.dumps(datos, ensure_ascii=False, indent=2) + '\n')
    (args.salida / f'{nombre}.txt').write_text(texto(datos))
    print(texto(datos), end='')
    return 0


if __name__ == '__main__':
    sys.exit(main())
