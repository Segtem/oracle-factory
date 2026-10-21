"""El banco de concurrencia: dos personas con sus agentes sobre un mismo proyecto, a la vez y de a turnos.

    python tools/banco.py --salida CARPETA [--semilla N] [--solo ESCENARIO ...]

Cada escenario arma un repositorio central (bare) con un proyecto de Factory, y dos clones: Ana y Beto, cada uno con su
identidad de Git, sus hooks y un agente de prueba (agente-ana, agente-beto). Las decisiones de una persona se toman en una
terminal (tools/terminal.py), como cuando la persona escribe; las de un agente, con --agente. Lo simultáneo corre en
procesos simultáneos de verdad; el orden de lo que se intercala sale de la semilla.

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
        p = subprocess.run([*CLI, '--agente', self.agente, *args], cwd=self.dir, env=self.env, capture_output=True,
                           text=True, stdin=subprocess.DEVNULL)
        if ok and p.returncode:
            raise AssertionError(f'{self.agente}: {" ".join(args)}: {(p.stderr or p.stdout).strip()[-400:]}')
        return p

    def decide(self, *args, entrada='1\n1\n1\n', ok=True) -> subprocess.CompletedProcess:
        """Una decisión de la persona, desde su terminal: elige la primera opción de cada menú."""
        p = en_terminal([*CLI, *args], cwd=self.dir, env=self.env, entrada=entrada)
        if ok and p.returncode:
            raise AssertionError(f'{self.nombre}: {" ".join(args)}: {(p.stderr or p.stdout).strip()[-400:]}')
        return p

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
    def __init__(self, nombre: str, tmp: Path, semilla: int, tal_cual: bool = False):
        self.nombre, self.tmp = nombre, tmp
        self.azar = random.Random(f'{semilla}:{nombre}')
        self.fila = {'escenario': nombre, 'resultado': 'ok', 'conflicto': 'ninguno', 'decisiones_perdidas': 0,
                     'mal_atribuidas': 0, 'evidencia_vieja_aceptada': 0, 'rehecho': 0, 'detalle': []}
        self.central = tmp / 'central.git'
        self.tal_cual = tal_cual  # el proyecto como lo deja init, sin ayudas del banco
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
            self.nota(f'conflicto al integrar {rama}: '
                      + ', '.join(quien.git('diff', '--name-only', '--diff-filter=U').stdout.split()))
            return False
        quien.git('push', '-q', 'origin', 'main')
        return True


# --- los escenarios --------------------------------------------------------------------------------------------------
def eventos_de(registro: dict) -> list[tuple]:
    return [(e.get('accion'), e.get('actor'), e.get('cuando')) for e in registro.get('eventos') or []]


def s0_clon_recien_hecho(e: Escenario) -> None:
    """Beto clona el proyecto tal como lo dejó init y crea un cambio: tiene que poder."""
    vacias = sorted(str(d.relative_to(e.tmp / 'semilla')) for d in (e.tmp / 'semilla').rglob('*')
                    if d.is_dir() and '.git' not in d.parts and not any(d.iterdir()))
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
    with ThreadPoolExecutor(2) as pool:
        a, b = pool.submit(frente, e.ana, 'restar', 'restar.py'), pool.submit(frente, e.beto, 'multiplicar', 'multiplicar.py')
        (id_a, ev_a), (id_b, ev_b) = a.result(), b.result()
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
    """Ana crea un cambio y lo sube; Ana y Beto lo toman a la vez desde sus clones. ¿Quién queda responsable?"""
    e.ana.git('checkout', '-q', '-b', 'tarea/compartido')
    ident = e.ana.nuevo_cambio('compartido', 'Un cambio para dos')
    e.ana.commit('compartido: el cambio')
    e.ana.git('push', '-q', 'origin', 'tarea/compartido')
    e.beto.git('fetch', '-q', 'origin')
    e.beto.git('checkout', '-q', '-b', 'tarea/compartido', 'origin/tarea/compartido')
    with ThreadPoolExecutor(2) as pool:
        for f in [pool.submit(p.decide, 'tomar', ident) for p in (e.ana, e.beto)]:
            f.result()
    duenos = {p.nombre: (p.registro(ident).get('responsable') or {}).get('persona') for p in (e.ana, e.beto)}
    e.nota(f'responsable en cada clon después de tomar a la vez: {duenos}')
    for p in (e.ana, e.beto):
        p.commit(f'compartido: lo tomó {p.nombre}')
    e.ana.git('push', '-q', 'origin', 'tarea/compartido')
    p = e.beto.git('push', '-q', 'origin', 'tarea/compartido', ok=False)
    if p.returncode:
        e.detectado('al_integrar')
        traer = e.beto.git('pull', '-q', '--no-rebase', 'origin', 'tarea/compartido', ok=False)
        if traer.returncode:
            e.defecto('dos «tomar» del mismo cambio en dos clones chocan en factory.json al sincronizar: Factory no avisa antes '
                      'ni ayuda a unir el registro (cada clon cree que el cambio es suyo)')
        else:
            e.nota('el pull unió el registro sin conflicto de texto')
    else:
        e.detectado('nunca')
        e.defecto('el segundo push no chocó')


def s5_decisiones_simultaneas(e: Escenario) -> None:
    """Dos procesos del mismo clon (Ana y su agente) escriben el mismo registro a la vez: no se pierde ningún evento."""
    e.ana.git('checkout', '-q', '-b', 'tarea/charla')
    ident = e.ana.nuevo_cambio('charla', 'Un registro concurrido')
    antes = len(e.ana.registro(ident)['eventos'])
    n = 12
    with ThreadPoolExecutor(6) as pool:
        trabajos = [pool.submit(e.ana.agente_hace, 'mensaje', ident, f'mensaje {i}', ok=False) for i in range(n)]
        codigos = [t.result().returncode for t in trabajos]
    despues = e.ana.registro(ident)['eventos']
    guardados = sum(1 for x in despues if x.get('accion') == 'mensaje')
    rechazados = sum(1 for c in codigos if c)
    e.fila['decisiones_perdidas'] = n - guardados - rechazados
    if rechazados:
        e.detectado('antes')
        e.fila['rehecho'] = rechazados
        e.nota(f'{rechazados} de {n} escrituras simultáneas se rechazaron (el registro cambió mientras tanto) y hay que repetirlas')
    if e.fila['decisiones_perdidas']:
        e.defecto(f'{e.fila["decisiones_perdidas"]} mensajes simultáneos se perdieron sin error')
    if len(despues) != antes + guardados:
        e.defecto('el registro perdió eventos anteriores')


def s6_mismo_id(e: Escenario) -> None:
    """Ana y Beto crean, a la vez y en sus clones, un cambio con el mismo sufijo: ¿chocan los IDs al integrar?"""
    for p in (e.ana, e.beto):
        p.git('checkout', '-q', '-b', f'tarea/igual-{p.nombre.lower()}')
    with ThreadPoolExecutor(2) as pool:
        ids = [f.result() for f in [pool.submit(p.nuevo_cambio, 'igual', 'Un cambio con el mismo nombre') for p in (e.ana, e.beto)]]
    for p in (e.ana, e.beto):
        p.commit(f'igual: de {p.nombre}')
        p.git('push', '-q', 'origin', f'tarea/igual-{p.nombre.lower()}')
    e.nota(f'IDs: {ids}')
    e.integrar(e.ana, 'tarea/igual-ana')
    limpio = e.integrar(e.ana, 'tarea/igual-beto')
    if ids[0] == ids[1]:
        if limpio:
            e.detectado('nunca')
            e.defecto('dos cambios distintos con el mismo ID se mezclaron al integrar sin conflicto')
        else:
            e.defecto('dos cambios distintos con el mismo ID chocan al integrar: Factory no los distingue antes')
    else:
        e.nota('los IDs salieron distintos (el segundo de creación los separó)')


def s7_generados(e: Escenario) -> None:
    """Dos cambios integrados uno tras otro tocan resumen.md y kb/: chocan, y se resuelven rehaciéndolos."""
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
        en_conflicto = set(e.ana.git('diff', '--name-only', '--diff-filter=U').stdout.split())
        generados = {n for n in en_conflicto if n == '.factory/resumen.md' or n.startswith('kb/')}
        if en_conflicto - generados:
            e.defecto(f'chocaron archivos que no son generados: {sorted(en_conflicto - generados)}')
        for n in generados:
            e.ana.git('checkout', '--theirs', '--', n)
        e.ana.agente_hace('resumen')
        e.ana.agente_hace('kb')
        e.ana.git('add', '-A')
        e.ana.git('commit', '-q', '--no-edit')
        e.fila['rehecho'] += len(generados)
        e.nota(f'chocaron {sorted(generados)}: se rehicieron con resumen y kb')
    for orden in (['kb', '--verificar'], ['resumen', '--verificar']):
        if e.ana.agente_hace(*orden, ok=False).returncode:
            e.defecto(f'después de integrar, {" ".join(orden)} falla')


def a1_relevo_atrasado(e: Escenario) -> None:
    """El lunes Ana toma un cambio y avanza; el jueves Beto, con su clon del lunes, lo releva y sigue."""
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
    """Beto tiene evidencia de su candidato; Ana integra antes un cambio de producto; al traer main, la evidencia ya no vale."""
    e.beto.git('checkout', '-q', '-b', 'tarea/lento')
    ident = e.beto.nuevo_cambio('lento', 'Un cambio que tarda')
    e.beto.escribir('lento.py', 'X = 1\n')
    e.beto.commit('lento: producto')
    sha = e.beto.git('rev-parse', '--short=7', 'HEAD').stdout.strip()
    evidencia = e.beto.dir / '.factory/cambios' / ident / 'candidatos' / sha / 'evidencia'
    evidencia.mkdir(parents=True)
    (evidencia / 'resultado.json').write_text('{"exitoso": true}\n')
    e.beto.commit('lento: evidencia')
    # Ana integra antes un cambio de producto.
    e.ana.escribir('calc.py', 'def sumar(a, b):\n    return b + a\n')
    e.ana.commit('otro: calc.py')
    e.ana.git('push', '-q', 'origin', 'main')
    e.beto.git('pull', '-q', '--no-rebase', 'origin', 'main')
    vigente = json.loads(e.beto.agente_hace('estado', ident, '--json').stdout).get('candidato')
    if vigente == sha:
        e.fila['evidencia_vieja_aceptada'] += 1
        e.defecto('después de traer main con otro producto, el candidato viejo sigue vigente')
    else:
        e.detectado('antes')
        e.nota('al traer main, el candidato viejo deja de estar vigente: hay que producir evidencia otra vez')
        e.fila['rehecho'] += 1


def a3_registro_en_dos_ramas(e: Escenario) -> None:
    """Un mismo cambio: Ana deja un mensaje en su rama y Beto otro en la suya; al juntarlas, ¿se conservan los dos?"""
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
    """Durante la semana, Ana y Beto se dejan mensajes en el mismo cambio, cada uno trayendo lo del otro antes de escribir."""
    e.ana.git('checkout', '-q', '-b', 'tarea/charla')
    ident = e.ana.nuevo_cambio('charlas', 'Un cambio conversado')
    e.ana.commit('charlas: el cambio')
    e.ana.git('push', '-q', '-u', 'origin', 'tarea/charla')
    e.beto.git('fetch', '-q', 'origin')
    e.beto.git('checkout', '-q', '-b', 'tarea/charla', '--track', 'origin/tarea/charla')
    turnos = [p for p in (e.ana, e.beto) for _ in range(3)]
    e.azar.shuffle(turnos)  # quién escribe cada día sale de la semilla
    escritos = []
    for dia, p in enumerate(turnos, 1):
        p.git('pull', '-q', '--no-rebase', 'origin', 'tarea/charla')
        texto = f'día {dia}: {p.nombre}'
        p.agente_hace('mensaje', ident, texto)
        p.commit(f'charlas: {texto}')
        if p.git('push', '-q', 'origin', 'tarea/charla', ok=False).returncode:
            e.defecto(f'el día {dia} {p.nombre} no pudo subir aunque trajo lo del otro antes de escribir')
            return
        escritos.append(texto)
    e.ana.git('pull', '-q', '--no-rebase', 'origin', 'tarea/charla')
    vistos = [x.get('texto') for x in e.ana.registro(ident)['eventos'] if x.get('accion') == 'mensaje']
    e.fila['decisiones_perdidas'] = len(set(escritos) - set(vistos))
    if vistos != escritos:
        e.defecto(f'los mensajes quedaron {vistos}, no {escritos}')


def a5_trailers_y_vault_en_otro_clon(e: Escenario) -> None:
    """Ana escribe una línea en su cambio; Beto, desde su clon, ve el vault al día y sabe por qué existe esa línea."""
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


def correr(semilla: int, solo: list[str] | None = None) -> list[dict]:
    filas = []
    for nombre, funcion in ESCENARIOS.items():
        if solo and nombre not in solo:
            continue
        with tempfile.TemporaryDirectory(prefix=f'banco-{nombre}-') as d:
            inicio = time.monotonic()
            try:
                esc = Escenario(nombre, Path(d), semilla, tal_cual=nombre == 's0_clon_recien_hecho')
                funcion(esc)
                fila = esc.fila
            except Exception as error:  # noqa: BLE001 — un escenario que se rompe es un resultado, no un corte del banco
                fila = {'escenario': nombre, 'resultado': 'error', 'conflicto': 'nunca', 'decisiones_perdidas': 0,
                        'mal_atribuidas': 0, 'evidencia_vieja_aceptada': 0, 'rehecho': 0,
                        'detalle': [f'{type(error).__name__}: {error}'[:600]]}
            fila['segundos'] = round(time.monotonic() - inicio, 1)
            filas.append(fila)
    return filas


def informe(filas: list[dict], semilla: int, real: bool = False) -> dict:
    return {'esquema': 'oracle-factory.banco/1', 'semilla': semilla, 'reproducible': not real,
            'versiones': {p: metadata.version(p) for p in ('oracle-factory', 'oracle-metalenguaje', 'oracle-task', 'oracle-clue')}
            | {'python': sys.version.split()[0], 'git': subprocess.run(['git', '--version'], capture_output=True, text=True).stdout.strip()},
            'escenarios': filas}


def texto(datos: dict) -> str:
    lineas = [f"Banco de concurrencia — semilla {datos['semilla']}{'' if datos['reproducible'] else ' (corrida real, no reproducible)'}", '']
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
    args = parser.parse_args(argv)
    args.salida.mkdir(parents=True, exist_ok=True)
    datos = informe(correr(args.semilla, args.solo), args.semilla)
    (args.salida / 'banco.json').write_text(json.dumps(datos, ensure_ascii=False, indent=2) + '\n')
    (args.salida / 'banco.txt').write_text(texto(datos))
    print(texto(datos), end='')
    return 0


if __name__ == '__main__':
    sys.exit(main())
