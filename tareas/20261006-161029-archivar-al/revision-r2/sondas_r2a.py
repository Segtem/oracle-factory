"""Sondas de R2 sobre archivar (31a930f)."""
import json, subprocess, sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, 'tests')
from test_archivo import Archivo as Base, f, MODIFICA, QUITA
from oracle_factory import archivo


class SondasA(Base):
    def test_x_01_cierre_fallido_y_spec_cambiada_despues(self):
        # el cierre se corta después de fusionar; la persona sigue trabajando, cambia la spec y vuelve a cerrar
        real = f.ejecutar
        def falla(argv, *a, **k):
            if argv[:2] == ['tasks', 'close']:
                return subprocess.CompletedProcess(argv, 1, '', 'tracker no disponible')
            return real(argv, *a, **k)
        with patch.object(f, 'ejecutar', falla):
            try: self.cambio_cerrado()
            except f.FactoryError: pass
        ident = sorted(p.name for p in (self.root / 'openspec/changes').iterdir())[0]
        carpeta, estado = f.leer(ident)
        spec = self.root / estado['spec']
        spec.write_text(spec.read_text().replace('### Requirement: titulo valido', '### Requirement: titulo valido\nTEXTO-NUEVO-DE-LA-SPEC'))
        with self.escribe(f'APROBAR ESPECIFICACION {ident}'): f.aprobar_spec(ident)
        f.importar(ident)
        rid = f.leer(ident)[1]['requisitos'][0]
        f.medir(ident, requisito_id=rid, medidas=['notas.casos_ejecutados', 'notas.resultados'], quitar_sin_medir=True)
        self.git('add', '.'); self.git('commit', '-qm', 'spec nueva')
        informe = self.root / 'tareas' / ident / 'revision.md'
        with self.escribe(f'REGISTRAR REVISION {ident}'): f.revisar(ident, informe, 'Persona fixture', 'aprobar', 0)
        hechos = self.root / 'tareas' / ident / 'hechos.json'
        subprocess.run([sys.executable, 'examples/notas/sensor.py', '--salida', hechos], cwd=self.root, check=True, capture_output=True)
        f.juzgar(ident, hechos)
        with self.escribe(f'CERRAR {ident}'): f.cerrar(ident)
        cons = self.consolidada()
        idx = json.loads((self.root / '.factory/specs/notas.json').read_text())
        print('\nR2A-01 fase:', f.leer(ident)[1]['fase'], '| la consolidada tiene el texto nuevo:', 'TEXTO-NUEVO-DE-LA-SPEC' in cons,
              '| requisito de Oracle en el índice:', list(idx['requisitos'].values())[0]['requisito'], '| vigente según el registro:', f.leer(ident)[1]['requisitos'], file=sys.stderr)

    def test_x_02_edicion_a_mano_se_pisa_sin_aviso(self):
        self.cambio_cerrado()
        cons = self.root / 'openspec/specs/notas/spec.md'
        cons.write_text(cons.read_text() + '\n### Requirement: agregado a mano\nNadie lo aprobó.\n')
        otro = self.cambio_importado('Fechas', 'notas', '# Capability: notas\n\n## ADDED Requirements\n\n### Requirement: nota con fecha\nTipo: funcional\nThe system SHALL record dates.\n\n#### Scenario: s\n- THEN fecha\n')
        self.marcar_cerrado(otro, '2099-01-01T00:00:00+00:00')
        salida = self.salida(); f.archivar(); salida = self.salida()
        print('\nR2A-02 tras archivar otro cambio: la edición a mano sigue:', 'agregado a mano' in cons.read_text(), '| se avisó:', 'mano' in salida or 'difiere' in salida, file=sys.stderr)
        # y la huella del producto no notó la edición
        self.git('add', '.'); self.git('commit', '-qm', 'x')
        h1 = f.contexto_producto()['archivos_sha256']; cons.write_text(cons.read_text() + 'otra edición\n'); h2 = f.contexto_producto()['archivos_sha256']
        print('R2A-02 editar openspec/specs cambia la huella:', h1 != h2, file=sys.stderr)
        # un archivo de openspec/specs que Factory no maneja
        ajeno = self.root / 'openspec/specs/escrita-a-mano/spec.md'; ajeno.parent.mkdir(parents=True); ajeno.write_text('a'); h3 = f.contexto_producto()['archivos_sha256']
        ajeno.write_text('b'); h4 = f.contexto_producto()['archivos_sha256']
        print('R2A-02 una spec de openspec/specs que Factory no escribió cambia la huella:', h3 != h4, file=sys.stderr)

    def test_x_03_fusion_casos_raros(self):
        base = archivo.fusionar(archivo.indice_vacio('x'), '## ADDED Requirements\n### Requirement: uno\nTipo: funcional\nA SHALL b.\n#### Scenario: s\n- THEN x\n', 'c1', {'uno': 'x_c1.uno'})
        casos = {
          'repetido en la misma spec (ADDED)': ('## ADDED Requirements\n### Requirement: dos\nA.\n### Requirement: dos\nB.\n', {'dos': 'x_c2.dos'}),
          'MODIFIED dos veces en la misma spec': ('## MODIFIED Requirements\n### Requirement: uno\nA1.\n### Requirement: uno\nA2.\n', {'uno': 'x_c2.uno'}),
          'ADDED y REMOVED del mismo en la misma spec': ('## ADDED Requirements\n### Requirement: dos\nA.\n## REMOVED Requirements\n### Requirement: dos\n', {'dos': 'x_c2.dos'}),
          'encabezado en minúsculas (Modified)': ('## Modified Requirements\n### Requirement: uno\nOtro texto.\n', {'uno': 'x_c2.uno'}),
          'REMOVED en minúsculas después de ADDED': ('## ADDED Requirements\n### Requirement: tres\nT.\n## Removed requirements\n### Requirement: cuatro\nX.\n', {'tres': 'x_c2.tres', 'cuatro': 'x_c2.cuatro'}),
          'Purpose y otra sección con ###': ('## Purpose\nAlgo.\n## ADDED Requirements\n### Requirement: cinco\nC.\n### Notas internas\nEsto no es un requisito.\n', {'cinco': 'x_c2.cinco'}),
          'sin escenarios': ('### Requirement: seis\nTipo: no funcional\nS.\n', {'seis': 'x_c2.seis'}),
        }
        print('\nR2A-03 fusión:', file=sys.stderr)
        for nombre, (delta, dom) in casos.items():
            try:
                n = archivo.fusionar(base, delta, 'c2', dom)
                print(f'   {nombre:44} -> requisitos {list(n["requisitos"])} | reemplazados {[(r["nombre"], r["requisito"]) for r in n["reemplazados"]]}'
                      + (f' | cuerpo cinco: {n["requisitos"]["cinco"]["cuerpo"]}' if 'cinco' in n['requisitos'] else ''), file=sys.stderr)
            except archivo.Conflicto as e:
                print(f'   {nombre:44} -> CONFLICTO {str(e)[:90]}', file=sys.stderr)

    def test_x_04_archivar_un_cerrado_sin_cierre(self):
        ident = self.cambio_importado('Viejo', 'notas', QUITA.replace('## REMOVED Requirements\n\n### Requirement: titulo valido\nYa no aplica.\n\n', ''))
        carpeta, estado = f.leer(ident); estado['fase'] = 'cerrada'; estado.pop('cierre', None); f.guardar(carpeta, estado)
        try:
            f.archivar(); r = 'ok'
        except Exception as e:
            r = f'{type(e).__name__}: {e}'
        print('\nR2A-04 archivar un cambio cerrado sin registro «cierre» (como los anteriores a los modos):', r, file=sys.stderr)
