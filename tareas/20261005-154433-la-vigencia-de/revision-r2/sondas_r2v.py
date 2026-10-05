"""Sondas de R2 sobre a55b109 (vigencia por contenido). Correr desde el checkout:
PYTHONPATH=.:tests:<revision-r2> python -m unittest -v sondas_r2v"""
import json, os, stat, sys, traceback
from unittest.mock import patch
sys.path.insert(0, 'tests')
from test_vigencia import Vigencia as Base, f


class SondasV(Base):
    def _ruta(self, ident):
        return self.root / 'openspec/changes' / ident / 'factory.json'

    def test_v_01_que_cambios_invalidan(self):
        ident = self.cambio_medido(); self.revision_libre(ident)
        res = {}
        def probar(nombre, accion, deshacer):
            accion(); res[nombre] = self.desactualizado(ident); deshacer()
        n = self.root / 'examples/notas/notas.py'
        modo = n.stat().st_mode
        probar('chmod+x', lambda: n.chmod(modo | 0o111), lambda: n.chmod(modo))
        nuevo = self.root / 'nuevo.py'
        probar('archivo sin seguimiento', lambda: nuevo.write_text('x'), lambda: nuevo.unlink())
        otro = self.root / 'openspec/changes/otro/proposal.md'
        otro.parent.mkdir(parents=True)
        probar('otro cambio de openspec', lambda: otro.write_text('x'), lambda: otro.unlink())
        t = self.root / 'tareas/x.txt'; t.parent.mkdir(exist_ok=True)
        probar('tareas/', lambda: t.write_text('x'), lambda: t.unlink())
        ign = self.root / 'oculto.py'
        ex = self.root / '.git/info/exclude'
        probar('archivo en .git/info/exclude', lambda: (ex.write_text('oculto.py\n'), ign.write_text('x')), lambda: (ign.unlink(), ex.write_text('')))
        probar('.gitignore y archivo ignorado', lambda: ((self.root/'.gitignore').write_text((self.root/'.gitignore').read_text()+'\nfoo.py\n'), (self.root/'foo.py').write_text('x')), lambda: None)
        print('\nR2V-vigencia:', res, file=sys.stderr)

    def test_v_02_head_preparacion_sin_head(self):
        ident = self.cambio_medido()
        informe, decisiones = self.preparar_informe(ident)
        datos = json.loads(informe.read_text()); del datos['contexto']['head']
        informe.write_bytes(f.bytes_json(datos))
        t = json.loads(decisiones.read_text()); t['informe_sha256'] = f.sha256(informe.read_bytes())
        decisiones.write_bytes(f.bytes_json(t))
        try:
            self.registrar_guiado(ident, informe, decisiones)
            print('\nR2V-02: registrado, head_preparacion =', self.estado(ident)['revision'].get('head_preparacion'), file=sys.stderr)
        except Exception as e:
            print('\nR2V-02 excepción:', type(e).__name__, e, file=sys.stderr)
            raise

    def test_v_03_head_preparacion_inventado(self):
        ident = self.cambio_medido()
        informe, decisiones = self.preparar_informe(ident)
        datos = json.loads(informe.read_text()); datos['contexto']['head'] = 'deadbeef' * 5
        informe.write_bytes(f.bytes_json(datos))
        t = json.loads(decisiones.read_text()); t['informe_sha256'] = f.sha256(informe.read_bytes())
        decisiones.write_bytes(f.bytes_json(t))
        self.registrar_guiado(ident, informe, decisiones)
        print('\nR2V-03 head_preparacion registrado:', self.estado(ident)['revision'].get('head_preparacion'), file=sys.stderr)
        self.assertEqual(self.estado(ident)['revision']['head_preparacion'], 'deadbeef' * 5)

    def test_v_04_aviso_con_contexto_sin_head(self):
        ident = self.cambio_medido(); self.revision_libre(ident)
        estado = self.estado(ident); del estado['revision']['contexto']['head']
        self._ruta(ident).write_text(json.dumps(estado, ensure_ascii=False, indent=2) + '\n')
        try:
            f.mostrar(ident)
            print('\nR2V-04: estado ok', file=sys.stderr)
        except Exception as e:
            print('\nR2V-04 excepción en estado:', type(e).__name__, e, file=sys.stderr)
            raise

    def test_v_05_propuesta_con_firma_vieja_queda_como_decidio(self):
        ident = self.cambio_medido()
        informe = self.root / 'tareas' / ident / 'revision.md'
        informe.write_text('Fixture de revisión; no es una revisión real.\n')
        with patch.object(f, 'AGENTE', 'agente-x'):
            f.revisar(ident, informe, 'agente-x', 'aprobar', 0)   # confirmacion: propuesta
        ruta = self._ruta(ident); estado = json.loads(ruta.read_text())
        firma = estado['propuestas']['revision']['firma']
        firma['contexto'] = f.contexto_producto(); firma.pop('producto')   # forma anterior al cambio
        ruta.write_text(json.dumps(estado, ensure_ascii=False, indent=2) + '\n')
        with self.escribe(f'REGISTRAR REVISION {ident}'):
            f.revisar(ident, informe, 'agente-x', 'aprobar', 0)   # la persona repite tal cual
        r = self.estado(ident)['revision']
        print('\nR2V-05 forma:', r['forma'], r['tipo_actor'], file=sys.stderr)
        self.assertEqual(r['forma'], 'decidio')

    def test_v_06_estado_no_muestra_el_commit_observado(self):
        ident = self.cambio_medido(); self.revision_libre(ident); f.juzgar(ident, self.hechos)
        self.stdout.truncate(0); self.stdout.seek(0)
        f.mostrar(ident)
        s = self.stdout.getvalue(); h = self.head()
        print('\nR2V-06 estado contiene el commit revisado:', h[:7] in s, file=sys.stderr)
        self.assertNotIn(h[:7], s)
        self.stdout.truncate(0); self.stdout.seek(0)
        with self.escribe(f'CERRAR {ident}'):
            f.cerrar(ident)
        print('R2V-06 cierre contiene el commit revisado:', h[:7] in self.stdout.getvalue(), file=sys.stderr)
        self.assertNotIn(h[:7], self.stdout.getvalue())
