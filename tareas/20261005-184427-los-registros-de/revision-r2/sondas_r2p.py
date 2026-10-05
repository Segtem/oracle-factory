"""Sondas de R2 sobre 78f0eb0 (portabilidad). Correr desde el checkout:
PYTHONPATH=.:tests:<revision-r2> python -m unittest -v sondas_r2p"""
import json, os, re, subprocess, sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, 'tests')
from test_portabilidad import Portabilidad as Base, f, GIT


class SondasP(Base):
    def _privadas(self, raiz):
        archivos = self.git('ls-files', '--cached', '--others', '--exclude-standard').splitlines()
        hallados = []
        for n in archivos:
            try:
                if str(raiz) in (raiz / n).read_text(encoding='utf-8'): hallados.append(n)
            except (UnicodeDecodeError, OSError): pass
        return hallados

    def test_p_01_recuperacion_de_un_registro_anterior(self):
        ident = self.cambio_juzgado()
        ruta = self.root / 'openspec/changes' / ident / 'factory.json'
        e = json.loads(ruta.read_text())
        e['oracle']['hechos'] = str(self.root / 'tareas' / ident / 'hechos.json')   # como escribía la versión anterior
        ruta.write_text(json.dumps(e, ensure_ascii=False, indent=2) + '\n')
        self.git('add', '.'); self.git('commit', '-qm', 'registro anterior')
        clon = self.clon()
        with self.en(clon):
            carpeta, estado = f.leer(ident)
            pend = f.pendientes_actuales(carpeta, estado)
            print('\nR2P-01 pendiente:', pend, file=sys.stderr)
            self.assertTrue(any('hechos ausentes' in p and 'juzgando de nuevo' in p for p in pend))
            hechos = clon / 'tareas' / ident / 'hechos.json'
            f.juzgar(ident, hechos)
            e2 = f.leer(ident)[1]
            print('R2P-01 tras juzgar: fase', e2['fase'], '| hechos', e2['oracle']['hechos'], '| revisión', e2['revision']['decision'],
                  '| pendientes', f.pendientes_actuales(*f.leer(ident)), file=sys.stderr)
            self.assertEqual(f.pendientes_actuales(*f.leer(ident)), [])

    def test_p_02_raiz_con_caracteres_especiales(self):
        for nombre in ('producto ñ #1', 'prod con "comillas"', 'prod\\barra'):
            tmp = Path(self.tmp.name) / 'raros' / nombre
            tmp.mkdir(parents=True)
            with patch.object(f, 'ROOT', tmp), patch.object(f, 'CHANGES', tmp / 'openspec/changes'):
                try:
                    f.inicializar()
                    ident = f.nuevo('Nota', con_ejemplo='notas')
                    with self.escribe(f'APROBAR ESPECIFICACION {ident}'): f.aprobar_spec(ident)
                    f.importar(ident)
                    rid = f.leer(ident)[1]['requisitos'][0]
                    fuente = [l for l in (tmp / 'requisitos' / f'{rid}.requisito').read_text(encoding='utf-8').splitlines() if 'fuente' in l][0]
                    print(f'\nR2P-02 [{nombre}] fuente:', fuente[:110], '| contiene la ruta:', str(tmp) in fuente or str(tmp).replace('\\', '\\\\') in fuente, file=sys.stderr)
                except Exception as e:
                    print(f'\nR2P-02 [{nombre}] excepción:', type(e).__name__, str(e)[:120], file=sys.stderr)

    def test_p_03_flujo_guiado_modo_y_cierre_sin_rutas(self):
        ident = self.cambio_medido()
        # modo guiado
        informe, decisiones = f.preparar_revision(ident)
        d = json.loads(informe.read_text())
        d.update(revisor='Persona fixture', completa=True, archivos_revisados=['examples/notas/notas.py'],
                 comprobaciones=[dict(descripcion='x', resultado='cumple', evidencia='y')], limites=['l'], hallazgos=[], sin_hallazgos_motivo='m')
        informe.write_bytes(f.bytes_json(d))
        t = json.loads(decisiones.read_text()); t.update(informe_sha256=f.sha256(informe.read_bytes()), actor='P', motivo='m', decisiones=[])
        decisiones.write_bytes(f.bytes_json(t))
        with self.escribe(f'REGISTRAR REVISION {ident}'):
            f.revisar(ident, informe, 'Persona fixture', 'aprobar', formato='guiado', decisiones=decisiones)
        f.juzgar(ident, self.sensor(self.root / 'tareas' / ident / 'hechos.json'))
        with self.escribe(f'CAMBIAR MODO {ident} autonomo'):
            f.cambiar_modo(ident, 'autonomo')
        with self.escribe(f'CAMBIAR MODO {ident} confirmacion'): pass
        f.cambiar_modo(ident, 'funcional')
        f.cambiar_modo(ident, 'confirmacion')
        self.git('add', '.'); self.git('commit', '-qm', 'todo')
        hallados = self._privadas(self.root)
        print('\nR2P-03 archivos versionados con la ruta de la máquina:', hallados, file=sys.stderr)
        self.assertEqual(hallados, [])
