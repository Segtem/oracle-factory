"""Sondas de R2 sobre 3bf20b6."""
import json, sys
sys.path.insert(0, 'tests')
from test_vigencia import Vigencia as Base, f


class SondasW(Base):
    def _informe_con_head(self, ident, valor, quitar=False):
        informe, decisiones = self.preparar_informe(ident)
        d = json.loads(informe.read_text())
        if quitar: del d['contexto']['head']
        else: d['contexto']['head'] = valor
        informe.write_bytes(f.bytes_json(d))
        t = json.loads(decisiones.read_text()); t['informe_sha256'] = f.sha256(informe.read_bytes())
        decisiones.write_bytes(f.bytes_json(t))
        return informe, decisiones

    def test_w_01_informe_sin_head_se_registra_y_estado_y_cierre_andan(self):
        ident = self.cambio_medido()
        informe, decisiones = self._informe_con_head(ident, None, quitar=True)
        self.registrar_guiado(ident, informe, decisiones)
        f.juzgar(ident, self.hechos)
        r = self.estado(ident)['revision']
        print('\nR2W-01 head_preparacion:', repr(r.get('head_preparacion')), file=sys.stderr)
        self.stdout.truncate(0); self.stdout.seek(0)
        f.mostrar(ident); print('R2W-01 estado:', [l for l in self.stdout.getvalue().splitlines() if 'commit' in l], file=sys.stderr)
        with self.escribe(f'CERRAR {ident}'):
            f.cerrar(ident)
        self.assertEqual(self.estado(ident)['fase'], 'cerrada')

    def test_w_02_head_no_texto_en_el_informe_rompe_estado_y_cierre(self):
        ident = self.cambio_medido()
        informe, decisiones = self._informe_con_head(ident, 12345)
        self.registrar_guiado(ident, informe, decisiones)
        print('\nR2W-02 head_preparacion registrado:', repr(self.estado(ident)['revision'].get('head_preparacion')), file=sys.stderr)
        f.juzgar(ident, self.hechos)
        for nombre, accion in (('estado', lambda: f.mostrar(ident)), ('cerrar', lambda: f.cerrar(ident))):
            try:
                with self.escribe(f'CERRAR {ident}'):
                    accion()
                print('R2W-02', nombre, 'ok', file=sys.stderr)
            except Exception as e:
                print('R2W-02', nombre, 'excepción:', type(e).__name__, e, file=sys.stderr)
        with self.assertRaises(TypeError):
            f.mostrar(ident)

    def test_w_03_cierre_con_contexto_sin_head(self):
        ident = self.cambio_medido(); self.revision_libre(ident); f.juzgar(ident, self.hechos)
        ruta = self.root / 'openspec/changes' / ident / 'factory.json'
        e = json.loads(ruta.read_text()); del e['revision']['contexto']['head']; del e['oracle']['contexto']['head']
        ruta.write_text(json.dumps(e, ensure_ascii=False, indent=2) + '\n')
        self.stdout.truncate(0); self.stdout.seek(0)
        with self.escribe(f'CERRAR {ident}'):
            f.cerrar(ident)
        print('\nR2W-03 cierre:', [l for l in self.stdout.getvalue().splitlines() if 'commit' in l or 'Aviso' in l], file=sys.stderr)
        self.assertEqual(self.estado(ident)['fase'], 'cerrada')
