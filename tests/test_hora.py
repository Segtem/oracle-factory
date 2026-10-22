"""La hora con microsegundos: escenarios ho1–ho2 (y el escenario a4 del banco, sin esperar entre días)."""
import contextlib
import io
import json
from pathlib import Path
import re
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT))
import test_archivo as _archivo  # noqa: E402
from oracle_factory import unir  # noqa: E402
from tools import banco  # noqa: E402

f = _archivo.f
MICRO = re.compile(r'^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{6}\+00:00$')


class Hora(unittest.TestCase):
    setUp, escribe, git = _archivo.Archivo.setUp, _archivo.Archivo.escribe, _archivo.Archivo.git

    # --- ho1: la hora distingue lo escrito en el mismo segundo -------------------------------------------------------
    def test_ho1_dos_mensajes_en_el_mismo_segundo(self):
        f.AGENTE = 'claude-code'
        try:
            ident = f.nuevo('Un cambio', capacidad='otra', sufijo='hora')
            f.mensaje(ident, 'primero')
            f.mensaje(ident, 'segundo')
        finally:
            f.AGENTE = None
        uno, dos = [e['cuando'] for e in f.leer(ident)[1]['eventos'] if e['accion'] == 'mensaje']
        self.assertTrue(MICRO.match(uno) and MICRO.match(dos), (uno, dos))
        self.assertLess(uno, dos)
        # Un registro viejo, con horas en segundos, se sigue mostrando como antes en estado y en el vault.
        carpeta, estado = f.leer(ident)
        for e in estado['eventos']:
            e['cuando'] = e['cuando'][:19] + '+00:00'
        f.ruta_registro(carpeta).write_text(json.dumps(estado))
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            self.assertEqual(f.main(['--proyecto', str(self.root), 'estado', ident, '--json']), 0)
        self.assertEqual(json.loads(salida.getvalue())['id'], ident)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(f.main(['--proyecto', str(self.root), 'kb']), 0)
        nota = (self.root / 'kb/cambios' / f'{ident}.md').read_text()
        self.assertIn(f"- {uno[:16].replace('T', ' ')} · claude-code: primero", nota)

    # --- ho2: al unir dos ramas, lo del mismo segundo queda en orden ----------------------------------------------------
    def test_ho2_unir_lo_del_mismo_segundo(self):
        base = {'eventos': [{'accion': 'cambio_creado', 'cuando': '2026-10-22T12:00:00+00:00'}]}
        ana = [{'accion': 'mensaje', 'texto': 'Ana 1', 'cuando': '2026-10-22T12:00:05.100000+00:00'},
               {'accion': 'mensaje', 'texto': 'Ana 2', 'cuando': '2026-10-22T12:00:05.700000+00:00'}]
        beto = [{'accion': 'mensaje', 'texto': 'Beto', 'cuando': '2026-10-22T12:00:05.400000+00:00'},
                {'accion': 'mensaje', 'texto': 'Beto viejo', 'cuando': '2026-10-22T12:00:04+00:00'}]
        beto.sort(key=lambda e: e['cuando'])
        unido = unir.unir(base, {'eventos': base['eventos'] + ana}, {'eventos': base['eventos'] + beto})
        self.assertEqual([e.get('texto') for e in unido['eventos']], [None, 'Beto viejo', 'Ana 1', 'Beto', 'Ana 2'])
        # Y el banco: mensajes de a turnos en dos ramas, sin esperar entre días, quedan en el orden de los días.
        with patch.object(banco.time, 'sleep', side_effect=AssertionError('el banco esperó entre días')):
            [fila] = banco.correr(20261022, ['a4_mensajes_de_a_turnos'])
        self.assertEqual(fila['resultado'], 'ok', fila['detalle'])


if __name__ == '__main__':
    unittest.main()
