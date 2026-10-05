"""Sondas de R2 sobre 2509c13: valores raros en factory.json y repos sha256."""
import json, subprocess, sys
from unittest.mock import patch
sys.path.insert(0, 'tests')
from test_vigencia import Vigencia as Base, f

RAROS = [None, '', [], {}, ['a'*40], {'x': 1}, 12345, True, 'x' * 100000, 'abc\ndef\x1b[31mrojo', 'ABCDEF1' * 6, 3.5]


class SondasX(Base):
    def _poner(self, ident, clave, valor, donde):
        ruta = self.root / 'openspec/changes' / ident / 'factory.json'
        e = json.loads(ruta.read_text())
        if donde == 'contexto.head': e[clave]['contexto']['head'] = valor
        else: e[clave]['head_preparacion'] = valor
        ruta.write_text(json.dumps(e, ensure_ascii=False, indent=2) + '\n')

    def test_x_01_valores_raros(self):
        ident = self.cambio_medido(); self.revision_libre(ident); f.juzgar(ident, self.hechos)
        fallos = []
        for donde, clave in (('contexto.head', 'revision'), ('contexto.head', 'oracle'), ('head_preparacion', 'revision')):
            for v in RAROS:
                self._poner(ident, clave, v, donde)
                for nombre, acc in (('estado', lambda: f.mostrar(ident)), ('cierre', lambda: f.cerrar(ident))):
                    try:
                        with self.escribe(f'NO CERRAR {ident}'):
                            acc()
                    except f.FactoryError:
                        pass          # el cierre cancelado es lo esperado
                    except Exception as e:
                        fallos.append((donde, clave, repr(v)[:30], nombre, type(e).__name__))
        print('\nR2X-01 fallos:', fallos, file=sys.stderr)
        self.stdout.truncate(0); self.stdout.seek(0)
        self._poner(ident, 'revision', 'abc\ndef\x1b[31mrojo', 'contexto.head')
        f.mostrar(ident)
        print('R2X-01 salida con saltos de línea:', repr([l for l in self.stdout.getvalue().splitlines() if 'commit' in l or 'desconocido' in l or 'Aviso' in l]), file=sys.stderr)
        self.assertEqual(fallos, [])

    def test_x_02_repo_sha256_pierde_head_preparacion(self):
        # repo con object-format sha256: el HEAD tiene 64 hexadecimales
        probe = subprocess.run(['git', 'init', '-q', '--object-format=sha256', '/tmp/__r2x_probe'], capture_output=True, text=True)
        if probe.returncode:
            print('\nR2X-02: este git no soporta sha256:', probe.stderr, file=sys.stderr); return
        ident = f.nuevo('Nota', con_ejemplo='notas')
        with self.escribe(f'APROBAR ESPECIFICACION {ident}'): f.aprobar_spec(ident)
        f.importar(ident)
        rid = self.estado(ident)['requisitos'][0]
        f.medir(ident, requisito_id=rid, medidas=['notas.casos_ejecutados', 'notas.resultados'], quitar_sin_medir=True)
        subprocess.run(['git', 'init', '-q', '-b', 'main', '--object-format=sha256'], cwd=self.root, check=True)
        self.git('add', '.'); self.git('commit', '-qm', 'producto fixture')
        self.hechos = self.root / 'tareas' / ident / 'hechos.json'
        subprocess.run([sys.executable, 'examples/notas/sensor.py', '--salida', self.hechos], cwd=self.root, check=True, capture_output=True)
        informe, decisiones = self.preparar_informe(ident)
        preparado = self.head(); self.commit_de_registros()
        self.registrar_guiado(ident, informe, decisiones)
        r = self.estado(ident)['revision']
        print('\nR2X-02 largo del HEAD:', len(preparado), 'head_preparacion:', r.get('head_preparacion'), file=sys.stderr)
        self.assertNotIn('head_preparacion', r)
