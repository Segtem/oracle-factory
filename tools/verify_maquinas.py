"""Evidencia de portabilidad entre máquinas con contenedores Docker.

Tres «máquinas» sin sistema de archivos compartido —un remoto Git y dos estaciones con
usuarios y rutas distintos—. Ana prepara un cambio hasta el veredicto y lo sube; Bruno lo
clona y lo cierra. Las personas son fixtures con una terminal simulada, no personas reales.
Necesita Docker y tarda un minuto: se corre a pedido, no dentro de la suite.
"""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.terminal import en_terminal  # noqa: E402

CASOS = {
    'M1': 'la huella del producto es la misma en las dos máquinas',
    'M2': 'estado en la otra máquina no tiene pendientes',
    'M3': 'nada versionado contiene la ruta privada de la primera máquina',
    'M4': 'la otra persona cierra el cambio desde su máquina',
    'M5': 'la otra máquina ve que el HEAD cambió con el producto idéntico',
}
LIMITE = ('Una estación por persona en una sola máquina real: no mide latencia de red, relojes distintos ni sistemas '
          'operativos distintos. Las personas y sus confirmaciones son fixtures.')
DOCKERFILE = """FROM python:3.13-slim
RUN apt-get update -qq && apt-get install -y -qq --no-install-recommends git >/dev/null && rm -rf /var/lib/apt/lists/*
COPY *.whl /tmp/
RUN pip install -q --no-cache-dir /tmp/*.whl && rm /tmp/*.whl
RUN useradd -m ana && useradd -m -d /srv/trabajo/bruno bruno
"""


class Maquina:
    def __init__(self, contenedor, usuario, home):
        self.c, self.u, self.home = contenedor, usuario, home
        self.p = f'{home}/producto'


def docker(*argv, check=True):
    r = subprocess.run(['docker', *argv], capture_output=True, text=True, timeout=300)
    if check and r.returncode:
        raise SystemExit(f"docker {' '.join(argv)}: {r.stderr or r.stdout}")
    return r


def construir_imagen(etiqueta):
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(['uv', 'build', '-q', '--wheel', '-o', tmp], cwd=ROOT, check=True, capture_output=True)
        (Path(tmp) / 'Dockerfile').write_text(DOCKERFILE)
        docker('build', '-q', '-t', etiqueta, tmp)


class Recorrido:
    def __init__(self, imagen):
        sufijo = f'{os.getpid()}'
        self.red, self.remoto = f'fmred{sufijo}', f'fmr{sufijo}'
        self.a = Maquina(f'fma{sufijo}', 'ana', '/home/ana')
        self.b = Maquina(f'fmb{sufijo}', 'bruno', '/srv/trabajo/bruno')
        self.imagen, self.logs, self.observaciones = imagen, [], []

    # -- infraestructura -------------------------------------------------------------
    def levantar(self):
        # El remoto no autentica (git daemon con receive-pack): sólo existe dentro de esta red privada y no publica puertos.
        docker('network', 'create', self.red)
        docker('run', '-d', '--name', self.remoto, '--network', self.red, '--hostname', 'remoto', self.imagen, 'sh', '-c',
               'git init -q --bare -b main /srv/producto.git && git daemon --base-path=/srv --export-all '
               '--enable=receive-pack --reuseaddr')
        for m, nombre in ((self.a, 'maquina-a'), (self.b, 'maquina-b')):
            docker('run', '-d', '--name', m.c, '--network', self.red, '--hostname', nombre, self.imagen, 'sleep', 'infinity')
        time.sleep(2)

    def bajar(self):
        for nombre in (self.a.c, self.b.c, self.remoto):
            docker('rm', '-f', nombre, check=False)
        docker('network', 'rm', self.red, check=False)

    def ex(self, m, *cmd, cwd=None, tty=None, ok=True):
        """tty=None: sin terminal; tty='texto': una persona escribe en su terminal."""
        base = ['docker', 'exec', '-u', m.u, '-e', f'HOME={m.home}', '-w', cwd or m.p]
        if tty is None:
            r = subprocess.run([*base, m.c, *cmd], capture_output=True, text=True, timeout=120)
        else:
            r = en_terminal([*base, '-it', m.c, *cmd], cwd='/tmp', entrada=tty)
        self.logs.append({'maquina': m.u, 'comando': list(cmd), 'codigo': r.returncode,
                          'salida': r.stdout[-1500:], 'error': r.stderr[-500:]})
        if ok and r.returncode:
            raise SystemExit(f"[{m.u}] {' '.join(cmd)} -> {r.returncode}\n{r.stdout}\n{r.stderr}")
        return r

    def of(self, m, *cmd, **kw):
        return self.ex(m, *cmd, **kw).stdout.strip()

    def observar(self, caso, cumple, detalle):
        self.observaciones.append({'caso': caso, 'descripcion': CASOS[caso], 'cumple': bool(cumple), 'detalle': detalle})

    # -- el recorrido ------------------------------------------------------------------
    def ana_prepara(self):
        a = self.a
        for m, nombre in ((a, 'Ana'), (self.b, 'Bruno')):
            self.ex(m, 'git', 'config', '--global', 'user.name', nombre, cwd=m.home)
            self.ex(m, 'git', 'config', '--global', 'user.email', f'{m.u}@{m.c}.invalid', cwd=m.home)
        self.ex(a, 'mkdir', '-p', a.p, cwd=a.home)
        self.ex(a, 'git', 'init', '-q', '-b', 'main')
        self.ex(a, 'git', 'remote', 'add', 'origin', 'git://' + self.remoto + '/producto.git')
        self.ex(a, 'oracle-factory', 'init')
        salida = self.of(a, 'oracle-factory', 'nuevo', '--con-ejemplo', 'notas', 'Comprobar el título de una nota')
        self.ident = re.search(r'Cambio creado: (\S+)', salida)[1]
        self.ex(a, 'oracle-factory', 'aprobar-spec', self.ident, tty=f'APROBAR ESPECIFICACION {self.ident}\n')
        rid = re.search(r'(?m)^\+\s+(\S+)', self.of(a, 'oracle-factory', 'importar', self.ident))[1]
        self.ex(a, 'oracle-factory', 'medir', self.ident, '--requisito', rid, '--medida', 'notas.casos_ejecutados',
                '--medida', 'notas.resultados', '--quitar-sin-medir', tty='')
        self.ex(a, 'python', 'examples/notas/sensor.py', '--salida', f'tareas/{self.ident}/hechos.json')
        self.ex(a, 'sh', '-c', f'echo "Informe fixture de Ana" > tareas/{self.ident}/informe.md')
        self.ex(a, 'git', 'add', '.'); self.ex(a, 'git', 'commit', '-qm', 'producto de Ana')
        self.ex(a, 'oracle-factory', 'revision', self.ident, '--informe', f'tareas/{self.ident}/informe.md',
                '--revisor', 'Ana', '--decision', 'aprobar', '--hallazgos-abiertos', '0', tty=f'REGISTRAR REVISION {self.ident}\n')
        self.ex(a, 'oracle-factory', 'juzgar', self.ident, '--con', f'tareas/{self.ident}/hechos.json')
        self.ex(a, 'git', 'add', '.'); self.ex(a, 'git', 'commit', '-qm', 'registros de Ana')
        self.ex(a, 'git', 'push', '-q', 'origin', 'main')

    def bruno_continua(self):
        a, b = self.a, self.b
        self.ex(b, 'git', 'clone', '-q', 'git://' + self.remoto + '/producto.git', b.p, cwd=b.home)
        estado = self.ex(b, 'oracle-factory', 'estado', self.ident, ok=False).stdout
        pendiente = re.search(r'(?m)^Pendiente: (.*)$', estado)
        pendiente = pendiente[1] if pendiente else '(sin línea Pendiente)'
        huella = "from oracle_factory import cli; print(cli.contexto_producto()['archivos_sha256'])"
        ha, hb = self.of(a, 'python', '-c', huella), self.of(b, 'python', '-c', huella)
        self.observar('M1', ha == hb, f'A {ha[:12]} · B {hb[:12]}')
        self.observar('M2', pendiente == 'ninguno', f'Pendiente en B: {pendiente}')
        privadas = self.ex(b, 'sh', '-c', f"grep -rIl '{a.home}' . --exclude-dir=.git | sort", ok=False).stdout.split()
        self.observar('M3', not privadas, 'archivos con la ruta de Ana: ' + (', '.join(privadas) or 'ninguno'))
        self.observar('M5', 'con el producto idéntico' in estado, 'aviso de HEAD distinto con producto idéntico')
        cierre = self.ex(b, 'oracle-factory', 'cerrar', self.ident, tty=f'CERRAR {self.ident}\n', ok=False)
        fase = self.of(b, 'python', '-c', f"import json; print(json.load(open('openspec/changes/{self.ident}/factory.json'))['fase'])")
        quien = self.of(b, 'python', '-c', f"import json; print((json.load(open('openspec/changes/{self.ident}/factory.json')).get('cierre') or {{}}).get('actor'))")
        self.observar('M4', cierre.returncode == 0 and fase == 'cerrada' and quien == 'Bruno',
                      f'código {cierre.returncode}; fase {fase}; cerró {quien}; ' + cierre.stdout.strip().splitlines()[-1][-150:])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida', required=True, type=Path, help='carpeta nueva para la evidencia')
    parser.add_argument('--imagen', help='imagen ya construida; si falta, se construye con el wheel de este checkout')
    args = parser.parse_args(argv)
    if not shutil.which('docker') or docker('info', check=False).returncode:
        parser.error('hace falta Docker accesible sin sudo')
    # SIGTERM (un timeout, un kill) también tiene que limpiar los contenedores: se trata como una interrupción.
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))
    salida = args.salida.expanduser().resolve()
    salida.mkdir(parents=True, exist_ok=False)
    imagen = args.imagen or f'factory-maquina-{os.getpid()}'
    if not args.imagen:
        construir_imagen(imagen)
    recorrido = Recorrido(imagen)
    try:
        recorrido.levantar()
        recorrido.ana_prepara()
        recorrido.bruno_continua()
    finally:
        recorrido.bajar()
        if not args.imagen:
            docker('rmi', '-f', imagen, check=False)
    filas = [{'caso': o['caso'], 'codigo': 0 if o['cumple'] else 1} for o in recorrido.observaciones]
    ok = {f['caso'] for f in filas} == set(CASOS) and all(f['codigo'] == 0 for f in filas)
    (salida / 'maquinas.json').write_text(json.dumps({'observaciones': recorrido.observaciones, 'comandos': recorrido.logs,
                                                       'limite': LIMITE}, ensure_ascii=False, indent=2) + '\n')
    (salida / 'hechos.json').write_text(json.dumps({'maquinas_caso': filas, 'maquinas_corrida': [{'completa': int(ok), 'casos': len(CASOS)}]},
                                                    ensure_ascii=False, indent=2) + '\n')
    for o in recorrido.observaciones:
        print(('OK    ' if o['cumple'] else 'FALLA ') + f"{o['caso']}: {o['descripcion']} — {o['detalle']}")
    print(LIMITE)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
