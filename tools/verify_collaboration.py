"""Demostración local con CLI reales. Las decisiones humanas son fixtures en /tmp.

No publica, no modifica el producto observado y no cierra tareas reales. Los casos
ejercitan las herramientas; los acuerdos de reparto y relevo siguen siendo humanos.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.terminal import en_terminal  # noqa: E402
TEMPLATES = ROOT / 'docs/plantillas/colaboracion'
GUIDE = ROOT / 'docs/colaboracion.md'
# Lo que la spec exige que la guía describa; sin esto, los casos medirían sólo las herramientas.
GUIDE_MARKERS = {
    'C1': ('## 2. Aislar cada frente', 'git worktree add', 'git clone', 'git fetch'),
    'C5': ('## 4. Revisar el candidato', 'oracle-clue preparar', 'oracle-clue validar', '--triage'),
}
CASES = {
    'C1': 'aislamiento y dos entregas',
    'C2': 'solapamiento textual y semántico',
    'C3': 'relevo e interrupción',
    'C4': 'clones y registros divergentes',
    'C5': 'revisión de versión y checkout',
    'C6': 'integración y renovación de evidencia',
    'C7': 'spec y medidas cambiadas',
    'C8': 'gates y cierre rechazado',
    'C9': 'integridad de evidencia y piloto pendiente',
}
LIMIT = ('Casos C1–C9 en repositorios temporales, Linux. Reparto, recepción, '
         'triage y aprobaciones son fixtures. No mide usabilidad, productividad, '
         'autoridad humana, locks distribuidos ni ausencia universal de conflictos.')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def validate_results(rows):
    """Exigir identidad, unicidad, completitud y éxito; no basta contar verdes."""
    counts = Counter(row['caso'] for row in rows)
    if counts != Counter({case: 1 for case in CASES}):
        raise ValueError('casos ausentes, desconocidos o duplicados')
    if any(type(row['codigo']) is not int or row['codigo'] != 0 for row in rows):
        raise ValueError('caso fallido o sin resultado válido')


def validate_artifacts(output, artifacts):
    if not artifacts:
        raise ValueError('no hay artefactos observados')
    for name, expected in artifacts.items():
        path = (output / name).resolve()
        if not path.is_relative_to(output.resolve()) or not path.is_file() or digest(path) != expected:
            raise ValueError('artefacto ausente, fuera de salida o alterado: ' + name)


def missing_guide_markers(case, text=None):
    text = GUIDE.read_text(encoding='utf-8') if text is None else text
    return [marker for marker in GUIDE_MARKERS[case] if marker not in text]


def render_template(name, values):
    text = (TEMPLATES / name).read_text(encoding='utf-8')
    keys = set(re.findall(r'\{\{([a-z_]+)\}\}', text))
    if set(values) != keys or any(not str(v).strip() for v in values.values()):
        raise ValueError('campos incompletos o desconocidos en ' + name)
    return re.sub(r'\{\{([a-z_]+)\}\}', lambda match: str(values[match[1]]), text)


class Demo:
    def __init__(self, temporary, output, clue):
        self.temporary, self.output, self.clue = temporary, output, clue
        self.artifacts = {}
        self.logs, self.observations = [], []
        # Las pruebas Git no heredan hooks, identidad ni configuración del usuario.
        self.env = {k: v for k, v in os.environ.items()
                    if not k.startswith('GIT_') and k not in ('PYTHONPATH', 'ORACLE_PROYECTO')}
        self.env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1',
                        GIT_AUTHOR_NAME='Participante fixture', GIT_COMMITTER_NAME='Participante fixture',
                        GIT_AUTHOR_EMAIL='fixture@example.invalid', GIT_COMMITTER_EMAIL='fixture@example.invalid',
                        PYTHONDONTWRITEBYTECODE='1', LC_ALL='C.UTF-8')

    def run(self, cwd, *argv, expected=0, stdin=None):
        if not cwd.resolve().is_relative_to(self.temporary.resolve()):
            raise ValueError('los comandos de la demostración sólo operan en su directorio temporal')
        argv = [str(a) for a in argv]
        record = {'cwd': str(cwd), 'argv': argv, 'stdin_fixture': stdin, 'esperado': expected}
        self.logs.append(record)
        # Con stdin, una persona fixture escribe en su terminal; sin stdin, no hay terminal.
        p = (en_terminal(argv, cwd=cwd, env=self.env, entrada=stdin) if stdin is not None else
             subprocess.run(argv, cwd=cwd, env=self.env, capture_output=True, text=True, encoding='utf-8', timeout=90))
        record.update(codigo=p.returncode, stdout=p.stdout, stderr=p.stderr)
        if p.returncode != expected:
            raise AssertionError(f'{argv}: esperaba {expected}, obtuvo {p.returncode}: {p.stderr}\n{p.stdout}')
        return p

    def git(self, cwd, *argv, **kw):
        return self.run(cwd, 'git', '-c', 'core.hooksPath=/dev/null', '-c', 'gc.auto=0', '-c', 'maintenance.auto=false', *argv, **kw)

    def task(self, cwd, *argv):
        # Igual entorno instalado que Factory, sin depender del alias global.
        code = ('import sys; from importlib.metadata import distribution; '
                'e=next(e for e in distribution("oracle-task").entry_points '
                'if e.group=="console_scripts" and e.name=="tasks"); sys.exit(e.load()())')
        return self.run(cwd, sys.executable, '-c', code, *argv, '--proyecto', cwd)

    def factory(self, cwd, *argv, **kw):
        return self.run(cwd, sys.executable, ROOT / 'fabrica.py', '--proyecto', cwd, *argv, **kw)

    def check(self, condition, message):
        self.observations.append({'comprobacion': message, 'cumple': bool(condition)})
        if not condition:
            raise AssertionError(message)

    def save(self, name, content):
        path = self.output / self.case / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            raise ValueError('no sobrescribir evidencia: ' + name)
        path.write_bytes(content if isinstance(content, bytes) else content.encode('utf-8'))
        self.artifacts[str(path.relative_to(self.output))] = digest(path)
        return path

    def save_json(self, name, value):
        return self.save(name, json.dumps(value, ensure_ascii=False, indent=2) + '\n')

    def repo(self, path):
        path.mkdir()
        self.git(path, 'init', '-q', '-b', 'main')
        (path / 'producto.txt').write_text('base\n')
        self.commit(path, 'base fixture')
        return path

    def commit(self, repo, message):
        self.git(repo, 'add', '.')
        self.git(repo, 'commit', '-qm', message)
        return self.git(repo, 'rev-parse', 'HEAD').stdout.strip()

    def state(self, repo, ident):
        nuevo = repo / '.factory/cambios' / ident / 'factory.json'
        return json.loads((nuevo if nuevo.is_file() else repo / 'openspec/changes' / ident / 'factory.json').read_text())

    def fixture(self, path, approve=True, measured=True):
        path.mkdir()
        self.factory(path, 'init')
        self.git(path, 'init', '-q', '-b', 'main')
        result = self.factory(path, 'nuevo', '--con-ejemplo', 'notas', 'Fixture colaboración ' + self.case)
        ident = re.search(r'Cambio creado: (\S+)', result.stdout)[1]
        if approve:
            self.factory(path, 'aprobar-spec', ident, stdin=f'APROBAR ESPECIFICACION {ident}\n')
            self.factory(path, 'importar', ident)
            if measured:
                self.measure(path, ident)
        self.commit(path, ident + ': base fixture aceptada sólo para el arnés')
        return path, ident

    def measure(self, repo, ident, measures=('notas.casos_ejecutados', 'notas.resultados'), partial=None, **kw):
        rid = self.state(repo, ident)['requisitos'][0]
        args = ['medir', ident, '--requisito', rid]
        for measure in measures:
            args.extend(['--medida', measure])
        args.extend(['--sin-medir', partial] if partial else ['--quitar-sin-medir'])
        kw.setdefault('stdin', '')  # elegir medidas es una decisión de persona: terminal sin frase
        return self.factory(repo, *args, **kw)

    def review(self, repo, ident):
        report = repo / 'tareas' / ident / 'informe-fixture.md'
        report.write_text('FIXTURE: decisión simulada para el arnés; no es revisión humana del producto real.\n')
        self.factory(repo, 'revision', ident, '--informe', report, '--revisor', 'Fixture automatizado',
                     '--decision', 'aprobar', '--hallazgos-abiertos', '0', stdin=f'REGISTRAR REVISION {ident}\n')

    def observe(self, repo, ident):
        self.run(repo, sys.executable, '-m', 'unittest', 'discover', '-s', 'examples/notas', '-v')
        facts = repo / 'tareas' / ident / 'hechos-fixture.json'
        self.run(repo, sys.executable, 'examples/notas/sensor.py', '--salida', facts)
        return facts

    def green(self, repo, ident):
        facts = self.observe(repo, ident)
        self.review(repo, ident)
        self.factory(repo, 'juzgar', ident, '--con', facts)
        self.check('Pendiente: ninguno' in self.factory(repo, 'estado', ident).stdout,
                   'gates completos en fixture sobre candidato vigente')

    def guide(self):
        missing = missing_guide_markers(self.case)
        self.check(not missing, 'la guía describe lo que exige la spec; faltan: ' + (', '.join(missing) or 'ninguno'))

    def C1(self, base):
        self.guide()
        origin = self.repo(base / 'integracion')
        a, b = base / 'a', base / 'b'
        head = self.git(origin, 'rev-parse', 'HEAD').stdout.strip()
        for name, path in [('a', a), ('b', b)]:
            self.git(origin, 'worktree', 'add', '-b', name, path, head)
        (b / 'b.txt').write_text('aporte B en índice\n')
        self.git(b, 'add', 'b.txt')
        snapshot = [self.git(b, *args).stdout for args in [('rev-parse', 'HEAD'), ('write-tree',), ('status', '--porcelain')]]
        (a / 'a.txt').write_text('aporte A\n')
        delivery_a = self.commit(a, 'entrega A')
        after = [self.git(b, *args).stdout for args in [('rev-parse', 'HEAD'), ('write-tree',), ('status', '--porcelain')]]
        self.check(snapshot == after and (b / 'b.txt').read_text() == 'aporte B en índice\n' and not (b / 'a.txt').exists(),
                   'A no modifica HEAD, índice ni archivos de B')
        delivery_b = self.commit(b, 'entrega B')
        for delivery in [delivery_a, delivery_b]:
            self.git(origin, 'merge', '--no-ff', '-m', 'integración fixture', delivery)
        self.check((origin / 'a.txt').read_text() == 'aporte A\n' and (origin / 'b.txt').read_text() == 'aporte B en índice\n',
                   'integración serial preserva ambos aportes')
        self.save_json('entregas.json', {'base': head, 'a': delivery_a, 'b': delivery_b,
                                       'candidato': self.git(origin, 'rev-parse', 'HEAD').stdout.strip()})
        self.save('reparto.md', render_template('reparto.md', dict(tarea='20260101-000000-frente-a', persona='A (fixture)',
                  sesion='A1 fixture', escritor='A', base=head, rama='a', checkout=a, alcance='a.txt',
                  interfaces='texto UTF-8; ninguna interfaz con b.txt', dependencias='ninguna', revisor='B fixture',
                  integrador='A fixture', proximo='revisar entrega', confirmacion='simulada; no aceptación humana')))

    def C2(self, base):
        repo = self.repo(base / 'producto')
        self.git(repo, 'switch', '-c', 'a')
        (repo / 'producto.txt').write_text('decisión A\n')
        a = self.commit(repo, 'A cambia contrato')
        self.git(repo, 'switch', '-c', 'b', 'main')
        (repo / 'producto.txt').write_text('decisión B\n')
        b = self.commit(repo, 'B cambia contrato')
        conflict = self.git(repo, 'merge', 'a', expected=1)
        self.check('CONFLICT' in conflict.stdout and self.git(repo, 'rev-parse', 'HEAD').stdout.strip() == b,
                   'conflicto no reemplaza silenciosamente HEAD de B')
        self.save('conflicto.patch', self.git(repo, 'diff').stdout)
        self.check(self.git(repo, 'show', a + ':producto.txt').stdout == 'decisión A\n', 'original A recuperable')
        self.check(self.git(repo, 'show', b + ':producto.txt').stdout == 'decisión B\n', 'original B recuperable')
        (repo / 'producto.txt').write_text('decisión A\ndecisión B\n')
        self.commit(repo, 'resolución fixture conserva ambos aportes')
        self.save_json('decision-fixture.json', {'tipo': 'simulación, no decisión humana', 'escritor': 'B',
                                               'orden': ['A', 'B'], 'originales': [a, b], 'alcance': 'producto.txt'})
        (repo / 'api.py').write_text('dato = {"titulo": "nota"}\n')
        (repo / 'vista.py').write_text('from api import dato\nassert dato["titulo"] == "nota"\n')
        shared = self.commit(repo, 'contrato compartido')
        self.git(repo, 'switch', '-c', 'api')
        (repo / 'api.py').write_text('dato = {"nombre": "nota"}\n')
        self.commit(repo, 'API cambia interfaz')
        self.git(repo, 'switch', '-c', 'vista', shared)
        (repo / 'vista.py').write_text('from api import dato\nassert dato["titulo"].upper() == "NOTA"\n')
        self.commit(repo, 'vista usa contrato previo')
        self.git(repo, 'merge', '--no-ff', '-m', 'merge sin conflicto textual', 'api')
        failed = self.run(repo, sys.executable, 'vista.py', expected=1)
        self.check('KeyError' in failed.stderr, 'merge limpio puede romper una interfaz compartida')

    def C3(self, base):
        repo, ident = self.fixture(base / 'producto')
        head = self.git(repo, 'rev-parse', 'HEAD').stdout.strip()
        pending = repo / 'trabajo-pendiente.txt'
        pending.write_text('preservar trabajo de A\n')
        self.git(repo, 'add', pending.name)
        index = self.git(repo, 'write-tree').stdout
        lock = repo / '.factory-demo/locks' / (ident + '.medir.lock')
        lock.parent.mkdir(parents=True, exist_ok=True)
        # Proceso fixture conocido que deja un lock y termina; no se infiere por edad.
        exited = self.run(repo, sys.executable, '-c', 'import os,sys; os.close(os.open(sys.argv[1],os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600))', lock)
        state_before = self.state(repo, ident)
        blocked = self.measure(repo, ident, measures=('notas.resultados',), expected=1)
        self.check('otra operación medir' in blocked.stderr and lock.exists() and self.state(repo, ident) == state_before,
                   'lock existente rechaza medir sin cambiar estado ni retirarlo')
        self.check(exited.returncode == 0, 'proceso propietario fixture terminó y fue esperado explícitamente')
        lock.unlink()
        self.measure(repo, ident, measures=('notas.resultados',))
        self.check(pending.read_text() == 'preservar trabajo de A\n' and self.git(repo, 'write-tree').stdout == index,
                   'recuperación conserva trabajo pendiente e índice')
        self.save('pendiente.txt', pending.read_bytes())
        values = dict(tarea=ident, emisor='A / A1 fixture', receptor='B / B1 fixture', ubicacion=f'main / {repo}',
                      base=head, head=head, terminado='ejemplo de notas preparado', pendientes='trabajo-pendiente.txt en índice',
                      pruebas='medir rechazado con lock residual; recuperación exitosa', evidencia=f'pendiente.txt sha256={digest(pending)}',
                      bloqueos='proceso fixture terminó; lock retirado por recuperación simulada', decisiones='piloto humano pendiente',
                      proximo='B revisar trabajo pendiente', entrega='A fixture, propuesta simulada', recepcion='pendiente', escritor_siguiente='B al confirmar')
        self.save('relevo-propuesto.md', render_template('relevo.md', values))
        values.update(recepcion=f'B fixture confirmó {head}; confirmación simulada', escritor_siguiente='B fixture')
        self.save('relevo-recibido-fixture.md', render_template('relevo.md', values))

    def C4(self, base):
        origin = self.repo(base / 'origen')
        self.task(origin, 'init', '--sin-readme')
        ident = json.loads(self.task(origin, 'new', 'Relevo compartido fixture', '--json').stdout)['id']
        self.commit(origin, 'tarea común')
        a, b = base / 'a', base / 'b'
        for path in [a, b]:
            self.git(base, 'clone', '--no-hardlinks', origin, path)
        original = (a / 'tareas' / ident / 'TAREA.md').read_text()
        for path, author in [(a, 'A'), (b, 'B')]:
            self.task(path, 'note', ident, f'Aporte independiente {author}')
            self.commit(path, 'nota ' + author)
        self.git(a, 'fetch', b, 'main')
        before = self.git(a, 'rev-parse', 'HEAD').stdout.strip()
        self.git(a, 'merge', 'FETCH_HEAD', expected=1)
        self.check(self.git(a, 'rev-parse', 'HEAD').stdout.strip() == before, 'divergencia no avanza HEAD sin resolución')
        self.save('divergencia.patch', self.git(a, 'diff').stdout)
        ours = self.git(a, 'show', f'HEAD:tareas/{ident}/TAREA.md').stdout
        theirs = self.git(a, 'show', f'FETCH_HEAD:tareas/{ident}/TAREA.md').stdout
        self.check(ours.startswith(original) and theirs.startswith(original), 'ambos registros conservan el antecedente común')
        self.save('original-a.md', ours)
        self.save('original-b.md', theirs)
        merged = original + ours[len(original):] + theirs[len(original):]
        (a / 'tareas' / ident / 'TAREA.md').write_text(merged)
        self.commit(a, 'conciliación fixture: mismo ID y misma identidad; conservar ambas notas')
        self.task(a, 'review', '--json')
        self.check('Aporte independiente A' in merged and 'Aporte independiente B' in merged,
                   'conciliación conserva aportes de la misma tarea')
        self.save('conciliado.md', merged)
        collision = self.collision(base, origin)
        collision_changes = self.collision_changes(base)
        self.save_json('identidad.json', {'id': ident, 'misma_identidad': True, 'colision': collision,
                    'colision_cambios': collision_changes,
                    'limite': 'Clones locales en una máquina; la migración la hace B como fixture, no una persona. '
                              'Las referencias se buscan con tasks refs, que sólo ve menciones textuales. '
                              'La colisión de cambios Factory se mide antes de aceptar la spec: un cambio con spec aceptada '
                              'o requisitos importados necesita además renovar la aceptación y reimportar, que no se observa.'})

    def collision_changes(self, base):
        """Dos cambios Factory nuevos con el mismo ID, creados a la vez en clones distintos."""
        for attempt in range(3):
            pair = base / f'choque-cambios{attempt}'
            pair.mkdir()
            origin = pair / 'origen'
            origin.mkdir()
            self.factory(origin, 'init')
            self.git(origin, 'init', '-q', '-b', 'main')
            self.commit(origin, 'proyecto Factory vacío')
            a, b = pair / 'a', pair / 'b'
            for path in [a, b]:
                self.git(pair, 'clone', '--no-hardlinks', origin, path)
                # Git no versiona carpetas vacías: un clon de un proyecto sin cambios no trae tareas/. init lo repone.
                self.factory(path, 'init')
            time.sleep(1 - time.time() % 1)
            # En paralelo: dos ejecuciones seguidas pueden caer en segundos distintos.
            jobs = []
            for path in [a, b]:
                argv = [str(x) for x in (sys.executable, ROOT / 'fabrica.py', '--proyecto', path,
                                         'nuevo', '--capacidad', 'colision', 'Frente compartido fixture')]
                jobs.append((path, argv, subprocess.Popen(argv, cwd=path, env=self.env, stdout=subprocess.PIPE,
                                                          stderr=subprocess.PIPE, text=True, encoding='utf-8')))
            ids = []
            for path, argv, process in jobs:
                out, err = process.communicate(timeout=90)
                self.logs.append({'cwd': str(path), 'argv': argv, 'esperado': 0, 'codigo': process.returncode,
                                  'stdout': out, 'stderr': err})
                if process.returncode:
                    raise AssertionError(f'{argv}: {err}\n{out}')
                ids.append(re.search(r'Cambio creado: (\S+)', out)[1])
            if ids[0] == ids[1]:
                break
        else:
            raise AssertionError('tres intentos sin coincidir en el segundo: ' + repr(ids))
        old = ids[0]
        proposal, spec = f'openspec/changes/{old}/proposal.md', f'openspec/changes/{old}/specs/colision/spec.md'
        for path, who in [(a, 'A'), (b, 'B')]:
            for name in (proposal, spec):
                with (path / name).open('a', encoding='utf-8') as out:
                    out.write(f'\nAporte de {who}\n')
            self.commit(path, f'{who} crea su cambio {old}')
        self.git(a, 'fetch', b, 'main')
        before = self.git(a, 'rev-parse', 'HEAD').stdout.strip()
        clash = self.git(a, 'merge', 'FETCH_HEAD', expected=1)
        self.check('CONFLICT (add/add)' in clash.stdout and self.git(a, 'rev-parse', 'HEAD').stdout.strip() == before,
                   'mismo ID de cambio Factory en dos clones produce conflicto add/add sin avanzar HEAD')
        self.save('colision-cambios.patch', self.git(a, 'diff').stdout)
        self.git(a, 'merge', '--abort')
        ours = self.git(a, 'show', f'HEAD:{proposal}').stdout
        theirs = self.git(a, 'show', f'FETCH_HEAD:{proposal}').stdout
        self.check('Aporte de A' in ours and 'Aporte de B' in theirs, 'ambos originales del cambio recuperables')
        self.save('colision-cambios-original-a.md', ours)
        self.save('colision-cambios-original-b.md', theirs)
        # Migración fixture: B crea un cambio con otra identidad, traslada su contenido y retira el que choca.
        migrated = self.factory(b, 'nuevo', '--capacidad', 'colision', 'Frente compartido fixture de B')
        new = re.search(r'Cambio creado: (\S+)', migrated.stdout)[1]
        self.check(new != old, 'la identidad nueva del cambio difiere de la colisionada')
        for name in ('proposal.md', 'specs/colision/spec.md'):
            (b / 'openspec/changes' / new / name).write_text((b / 'openspec/changes' / old / name).read_text(encoding='utf-8'),
                                                            encoding='utf-8')
        self.git(b, 'rm', '-rq', f'openspec/changes/{old}', f'tareas/{old}')
        migration = self.commit(b, f'B migra su cambio de {old} a {new}')
        self.git(a, 'fetch', b, 'main')
        self.git(a, 'merge', '--no-ff', '-m', 'integración tras migrar la identidad del cambio', 'FETCH_HEAD')
        self.task(a, 'review', '--json')
        listed = self.factory(a, 'listar').stdout
        self.check(old in listed and new in listed, 'listar muestra los dos cambios con identidades distintas')
        self.check((a / proposal).read_text(encoding='utf-8') == ours
                   and 'Aporte de B' in (a / 'openspec/changes' / new / 'proposal.md').read_text(encoding='utf-8')
                   and 'Aporte de B' not in (a / proposal).read_text(encoding='utf-8'),
                   'integración conserva ambos cambios sin fusionar sus identidades')
        self.check('espera_aprobacion_spec' in self.factory(a, 'estado', new).stdout,
                   'el cambio migrado es consultable y sigue sin spec aceptada')
        return {'id_colisionado': old, 'id_migrado': new, 'migracion': migration, 'intentos': attempt + 1,
                'candidato': self.git(a, 'rev-parse', 'HEAD').stdout.strip()}

    def collision(self, base, origin):
        # Dos tareas nuevas con el mismo ID: Task sólo evita colisiones dentro de una carpeta.
        for attempt in range(3):
            pair = base / f'choque{attempt}'
            pair.mkdir()
            a, b = pair / 'a', pair / 'b'
            for path in [a, b]:
                self.git(pair, 'clone', '--no-hardlinks', origin, path)
            time.sleep(1 - time.time() % 1)  # mismo segundo con la CLI real, sin falsear el reloj
            ids = [json.loads(self.task(path, 'new', f'Frente {who} fixture', '--sufijo', 'frente', '--json').stdout)['id']
                   for path, who in [(a, 'A'), (b, 'B')]]
            if ids[0] == ids[1]:
                break
        else:
            raise AssertionError('tres intentos sin coincidir en el segundo: ' + repr(ids))
        ident = ids[0]
        (b / 'frente-b.md').write_text(f'Trabajo de B registrado en {ident}\n')
        for path, who in [(a, 'A'), (b, 'B')]:
            self.commit(path, f'{who} crea su tarea')
        self.git(a, 'fetch', b, 'main')
        before = self.git(a, 'rev-parse', 'HEAD').stdout.strip()
        clash = self.git(a, 'merge', 'FETCH_HEAD', expected=1)
        self.check('CONFLICT (add/add)' in clash.stdout and self.git(a, 'rev-parse', 'HEAD').stdout.strip() == before,
                   'mismo ID en dos clones produce conflicto add/add sin avanzar HEAD')
        self.save('colision.patch', self.git(a, 'diff').stdout)
        self.git(a, 'merge', '--abort')
        task_a = self.git(a, 'show', f'HEAD:tareas/{ident}/TAREA.md').stdout
        task_b = self.git(a, 'show', f'FETCH_HEAD:tareas/{ident}/TAREA.md').stdout
        self.check('Frente A' in task_a and 'Frente B' in task_b, 'ambos originales recuperables con identidades distintas')
        self.save('colision-original-a.md', task_a)
        self.save('colision-original-b.md', task_b)
        # Migración fixture: B reserva un ID nuevo con la CLI, mueve su registro y actualiza sus referencias.
        new = json.loads(self.task(b, 'new', 'Frente B fixture', '--sufijo', 'frente-b', '--json').stdout)['id']
        self.check(new != ident, 'la identidad nueva difiere de la colisionada')
        self.git(b, 'mv', '-f', f'tareas/{ident}/TAREA.md', f'tareas/{new}/TAREA.md')
        ref = b / 'frente-b.md'
        ref.write_text(ref.read_text().replace(ident, new))
        migrated = self.commit(b, f'B migra su tarea de {ident} a {new}')
        self.git(a, 'fetch', b, 'main')
        self.git(a, 'merge', '--no-ff', '-m', 'integración tras migrar identidad', 'FETCH_HEAD')
        self.task(a, 'review', '--json')
        refs = json.loads(self.task(a, 'refs', ident, '--json').stdout)['coincidencias']
        refs_new = json.loads(self.task(a, 'refs', new, '--json').stdout)['coincidencias']
        self.check((a / 'tareas' / ident / 'TAREA.md').read_text() == task_a
                   and (a / 'tareas' / new / 'TAREA.md').read_text() == task_b,
                   'integración conserva ambas tareas sin fusionarlas')
        self.check(not any(r['ruta'] == 'frente-b.md' for r in refs) and any(r['ruta'] == 'frente-b.md' for r in refs_new),
                   'las referencias de B apuntan sólo a su identidad nueva')
        return {'id_colisionado': ident, 'id_migrado': new, 'migracion': migrated, 'intentos': attempt + 1,
                'candidato': self.git(a, 'rev-parse', 'HEAD').stdout.strip()}

    def clue_report(self, bundle):
        return {'schema_version': 'oracle-clue.review/v1',
                **{k: bundle[k] for k in ('repo', 'base', 'head', 'diff_sha256', 'context_sha256')},
                'provider': {'name': 'fixture sembrado; no revisión real', 'model': None},
                'review_status': 'completo', 'limitations': ['Hallazgo fixture sobre un defecto sembrado.'],
                'findings': [{'id': 'F1', 'kind': 'bug', 'severity': 'media', 'confidence': 1,
                             'title': 'Suma implementada como resta', 'explanation': '2+1 devuelve 1.',
                             'location': {'file': 'calc.py', 'start_line': 2, 'end_line': 2, 'side': 'head'},
                             'trigger': 'sumar(2,1)', 'evidence': 'return a-b', 'status': 'pendiente',
                             'verification': 'Ejecutar assert sumar(2,1)==3'}]}

    def C5(self, base):
        self.guide()
        repo = self.repo(base / 'producto')
        (repo / 'calc.py').write_text('def sumar(a, b):\n    return a+b\n')
        (repo / 'contrato.md').write_text('sumar devuelve la suma\n')
        previous = self.commit(repo, 'suma correcta')
        (repo / 'calc.py').write_text('def sumar(a, b):\n    return a-b\n')
        self.commit(repo, 'defecto sembrado')
        self.run(repo, sys.executable, '-c', 'from calc import sumar; assert sumar(2,1)==3', expected=1)
        bundle_path, report_path, triage_path = [base / name for name in ['paquete.json', 'informe.json', 'triage.json']]
        self.run(repo, self.clue, 'preparar', '--repo', repo, '--base', previous,
                 '--contexto', 'contrato.md', '--salida', bundle_path)
        bundle = json.loads(bundle_path.read_text())
        write_json(report_path, self.clue_report(bundle))
        write_json(triage_path, {'schema_version': 'oracle-clue.triage/v1', 'report_sha256': digest(report_path),
                   'decisions': [{'finding_id': 'F1', 'status': 'riesgo_aceptado', 'reason': 'Sólo fixture de validación, no aceptación real.',
                                  'actor': 'persona simulada', 'at': '2026-01-01T00:00:00Z'}]})
        def validate(path, expected=0):
            return self.run(path, self.clue, 'validar', report_path, '--paquete', bundle_path,
                            '--repo', path, '--triage', triage_path, expected=expected)
        validate(repo)
        other = base / 'otra-ruta'
        self.git(base, 'clone', '--no-hardlinks', repo, other)
        self.check(self.git(repo, 'rev-parse', 'HEAD').stdout == self.git(other, 'rev-parse', 'HEAD').stdout,
                   'mismo HEAD en otra ruta para aislar el rechazo de portabilidad')
        rejected = validate(other, expected=1)
        self.check('no coincide' in rejected.stderr, 'Clue rechaza paquete de otro checkout')
        new_bundle, new_report = base / 'nuevo-paquete.json', base / 'nuevo-informe.json'
        self.run(other, self.clue, 'preparar', '--repo', other, '--base', previous,
                 '--contexto', 'contrato.md', '--salida', new_bundle)
        write_json(new_report, self.clue_report(json.loads(new_bundle.read_text())))
        self.run(other, self.clue, 'validar', new_report, '--paquete', new_bundle, '--repo', other)
        (repo / 'contrato.md').write_text('contrato modificado sin revisar\n')
        self.check('sin commit' in validate(repo, expected=1).stderr, 'Clue rechaza contexto versionado modificado')
        (repo / 'contrato.md').write_text('sumar devuelve la suma\n')
        (repo / 'calc.py').write_text('def sumar(a, b):\n    return a+b\n# corregido\n')
        self.commit(repo, 'corrección cambia candidato')
        self.check('no coincide' in validate(repo, expected=1).stderr, 'Clue rechaza informe de HEAD anterior')
        for path in [bundle_path, report_path, triage_path, new_bundle, new_report]:
            self.save(path.name, path.read_bytes())

    def C6(self, base):
        repo, ident = self.fixture(base / 'producto')
        head = self.git(repo, 'rev-parse', 'HEAD').stdout.strip()
        other = base / 'otra-entrega'
        self.git(repo, 'worktree', 'add', '-b', 'otra-entrega', other, head)
        (other / 'aporte-b.txt').write_text('aporte B\n')
        delivery = self.commit(other, 'entrega B fixture')
        self.green(repo, ident)
        self.save_json('estado-revisado.json', self.state(repo, ident))
        self.git(repo, 'merge', '--no-ff', '-m', 'integrar B', delivery)
        rejected = self.factory(repo, 'cerrar', ident, expected=1)
        self.check('desactualizado respecto del producto' in rejected.stderr,
                   'merge invalida revisión y juicio y bloquea cierre antes de pedir confirmación')
        self.green(repo, ident)
        self.check(self.state(repo, ident)['oracle']['contexto']['head'] != head, 'nuevo juicio observa candidato integrado')
        self.save_json('estado-renovado.json', self.state(repo, ident))
        state = self.state(repo, ident)
        self.save('integracion.md', render_template('integracion.md', dict(tareas=ident,
                  integrador='A fixture; acuerdo simulado', ubicacion=f'main / {repo}', base=head,
                  entregas=f'base A {head}; entrega B {delivery}', dependencias='aporte-b.txt independiente del ejemplo',
                  revisiones='estado-revisado.json y estado-renovado.json; hashes en resultado.json',
                  conflictos='ninguno', candidato=state['oracle']['contexto']['head'],
                  pruebas='unittest y sensor de notas; comandos en ejecucion.json',
                  renovaciones='revisión y juicio renovados después del merge', decision='fixture; sin decisión humana real',
                  oracle=f"fixture verde; hechos sha256={state['oracle']['hechos_sha256']}",
                  pendientes='confirmación humana de cierre; no se cierra en este caso', cierre='pendiente', commit_cierre='pendiente')))

    def C7(self, base):
        repo, ident = self.fixture(base / 'producto')
        self.green(repo, ident)
        self.measure(repo, ident, measures=('notas.resultados',))
        state = self.state(repo, ident)
        self.check(state['revision'] is None and state['oracle'] is None, 'cambiar medidas invalida revisión y juicio')
        self.measure(repo, ident)
        self.commit(repo, 'asociación renovada')
        self.green(repo, ident)
        state = self.state(repo, ident)
        previous_ids = state['requisitos']
        spec = repo / state['spec']
        spec.write_text(spec.read_text() + '\n### Requirement: conservar texto\nThe system SHALL preserve note text.\n#### Scenario: texto\n- THEN el texto permanece\n')
        blocked = self.factory(repo, 'cerrar', ident, expected=1)
        self.check('propuesta/spec cambió' in blocked.stderr, 'spec modificada necesita nueva aceptación')
        self.factory(repo, 'aprobar-spec', ident, stdin=f'APROBAR ESPECIFICACION {ident}\n')
        renewed = self.state(repo, ident)
        self.check(renewed['requisitos'] == [] and renewed['revision'] is None and renewed['oracle'] is None,
                   'aceptación nueva descarta validaciones dependientes')
        self.factory(repo, 'importar', ident)
        state = self.state(repo, ident)
        self.check(set(previous_ids).isdisjoint(state['requisitos']) and all('sin_medir' in (repo / 'requisitos' / (rid + '.requisito')).read_text()
                   for rid in state['requisitos']), 'importación aísla nueva spec y conserva requisitos sin medir')
        self.save_json('estado-nueva-spec.json', state)

    def C8(self, base):
        repo, ident = self.fixture(base / 'producto', approve=False)
        self.check('aprobación humana' in self.factory(repo, 'cerrar', ident, expected=1).stderr, 'cierre sin aceptación rechazado')
        self.factory(repo, 'aprobar-spec', ident, stdin=f'APROBAR ESPECIFICACION {ident}\n')
        self.factory(repo, 'importar', ident)
        facts = self.observe(repo, ident)
        self.check('cobertura completa' in self.factory(repo, 'juzgar', ident, '--con', facts, expected=1).stderr,
                   'JSON válido sin medidas no habilita juicio completo')
        self.measure(repo, ident, partial='piloto humano pendiente (fixture)')
        self.review(repo, ident)
        self.check('cobertura completa' in self.factory(repo, 'juzgar', ident, '--con', facts, expected=1).stderr,
                   'medidas asociadas con alcance sin medir no habilitan verde')
        self.measure(repo, ident)
        self.factory(repo, 'juzgar', ident, '--con', facts)
        self.check('revisión humana aprobada' in self.factory(repo, 'cerrar', ident, expected=1).stderr,
                   'Oracle verde sin revisión no habilita cierre')
        self.green(repo, ident)
        self.check('cierre cancelado' in self.factory(repo, 'cerrar', ident, stdin='\n', expected=1).stderr,
                   'confirmación de cierre vacía no es aceptación')
        self.check('ESTADO: ABIERTA' in (repo / 'tareas' / ident / 'TAREA.md').read_text(), 'tarea fixture permanece abierta')
        self.save_json('estado-abierto.json', self.state(repo, ident))

    def C9(self, base):
        rows = [{'caso': case, 'codigo': 0} for case in CASES]
        validate_results(rows)
        for mutation in [rows[:-1], rows + rows[:1], rows[:-1] + [{'caso': 'C0', 'codigo': 0}],
                         rows[:-1] + [{'caso': 'C9', 'codigo': 1}]]:
            try:
                validate_results(mutation)
            except ValueError:
                continue
            raise AssertionError('sensor aceptó casos incompletos, duplicados, desconocidos o fallidos')
        self.check(True, 'sensor rechaza omisiones, duplicados, casos ajenos y fallas')
        validate_artifacts(self.output, self.artifacts)
        probe = base / 'probe.txt'
        probe.write_text('original')
        expected = {'probe.txt': digest(probe)}
        probe.write_text('alterado')
        try:
            validate_artifacts(base, expected)
        except ValueError:
            self.check(True, 'verificador rechaza artefactos alterados')
        else:
            raise AssertionError('aceptó artefacto alterado')
        values = {key: 'pendiente; no observado por el arnés' for key in re.findall(r'\{\{([a-z_]+)\}\}',
                  (TEMPLATES / 'piloto.md').read_text())}
        values['estado'] = 'pendiente'
        values['limites'] = LIMIT
        self.save('piloto-pendiente.md', render_template('piloto.md', values))


def source_context():
    paths = [ROOT / p for p in ('fabrica.py', 'pyproject.toml', 'README.md', 'MANIFEST.in',
                               'docs/colaboracion.md', 'tests/test_collaboration_sensor.py')]
    paths += [Path(__file__), *TEMPLATES.glob('*.md'), *ROOT.glob('oracle_factory/*.py'),
              *ROOT.glob('catalogos/factory_colaboracion.*.oracle')]
    paths += [p for p in (ROOT / 'oracle_factory/data/notas').rglob('*')
              if p.is_file() and '__pycache__' not in p.parts]
    paths = sorted(set(paths))
    head = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
    return {'head': head, 'sha256': {str(p.relative_to(ROOT)): digest(p) for p in paths}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida', required=True, type=Path, help='carpeta nueva para evidencia')
    parser.add_argument('--clue', default='oracle-clue', help='ejecutable de Clue 0.1.0a1')
    args = parser.parse_args(argv)
    output = args.salida.expanduser().resolve()
    versions = {p: metadata.version(p) for p in ('oracle-metalenguaje', 'oracle-task')}
    if versions != {'oracle-metalenguaje': '0.38.1', 'oracle-task': '0.2.0'}:
        parser.error('usar dependencias fijadas de Factory: oracle-metalenguaje 0.38.1 y oracle-task 0.2.0')
    clue = shutil.which(args.clue)
    if not clue:
        parser.error('falta oracle-clue; instalar 0.1.0a1 o indicar --clue /ruta/al/ejecutable')
    clue_version = subprocess.run([clue, '--version'], text=True, capture_output=True, check=True).stdout.strip()
    if clue_version != 'oracle-clue 0.1.0a1':
        parser.error('se requiere oracle-clue 0.1.0a1 para estos contratos')
    source = source_context()
    output.mkdir(parents=True, exist_ok=False)
    rows = []
    with tempfile.TemporaryDirectory(prefix='factory-colaboracion-') as temp:
        demo = Demo(Path(temp), output, clue)
        for case, description in CASES.items():
            demo.case, demo.logs, demo.observations = case, [], []
            base = Path(temp) / case
            base.mkdir()
            row = {'caso': case, 'descripcion': description, 'codigo': 1}
            try:
                getattr(demo, case)(base)
                row['codigo'] = 0
            except Exception:
                row['error'] = traceback.format_exc()
            finally:
                demo.save_json('ejecucion.json', {'comandos': demo.logs, 'observaciones': demo.observations})
                rows.append(row)
                print(f'{case}: {"OK" if row["codigo"] == 0 else "FALLO"} — {description}', flush=True)
        same_source = source == source_context()
        ok = same_source
        try:
            validate_results(rows)
            validate_artifacts(output, demo.artifacts)
        except ValueError:
            ok = False
        # C9 no oculta una falla anterior: este hecho exige todos los casos reales.
        facts = {'colaboracion_caso': [{'caso': r['caso'], 'codigo': r['codigo']} for r in rows],
                 'colaboracion_corrida': [{'completa': int(ok), 'casos': len(rows)}]}
        write_json(output / 'hechos.json', facts)
        write_json(output / 'resultado.json', {'exitoso': ok, 'casos': rows, 'origen': source,
                   'origen_sin_cambios_durante_corrida': same_source, 'versiones': {**versions, 'clue': clue_version,
                   'python': sys.version, 'plataforma': sys.platform}, 'limites': LIMIT, 'piloto_humano': 'pendiente',
                   'artefactos_sha256': demo.artifacts, 'hechos_sha256': digest(output / 'hechos.json')})
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
