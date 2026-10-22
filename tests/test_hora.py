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
            for _ in range(5):  # hasta que los dos caigan en el mismo segundo
                antes = len(f.leer(ident)[1]['eventos'])
                f.mensaje(ident, 'primero')
                f.mensaje(ident, 'segundo')
                uno, dos = [e['cuando'] for e in f.leer(ident)[1]['eventos'][antes:]]
                if uno[:19] == dos[:19]:
                    break
        finally:
            f.AGENTE = None
        self.assertEqual(uno[:19], dos[:19])
        self.assertTrue(MICRO.match(uno) and MICRO.match(dos), (uno, dos))
        self.assertLess(unir.hora({'cuando': uno}), unir.hora({'cuando': dos}))
        # Un registro viejo, con horas en segundos, se sigue mostrando como antes en estado y en el vault.
        carpeta, estado = f.leer(ident)
        for e in estado['eventos']:
            e['cuando'] = e['cuando'][:19] + '+00:00'
        f.ruta_registro(carpeta).write_text(json.dumps(estado))
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            self.assertEqual(f.main(['--proyecto', str(self.root), 'estado', ident, '--json']), 0)
        self.assertEqual(json.loads(salida.getvalue())['id'], ident)
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida), patch('builtins.input', return_value=''):
            f.mostrar(ident)
        self.assertIn(f'{ident} — Un cambio', salida.getvalue())
        self.assertIn(f"claude-code (mensaje {dos[:16].replace('T', ' ')})", salida.getvalue())
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(f.main(['--proyecto', str(self.root), 'kb']), 0)
        nota = (self.root / 'kb/cambios' / f'{ident}.md').read_text()
        self.assertIn(f"- {uno[:16].replace('T', ' ')} · claude-code: primero", nota)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(f.main(['--proyecto', str(self.root), 'kb', '--verificar']), 0)
        # Ordenar por la hora: un texto que no es fecha va primero y por su texto; uno viejo con Z, antes que uno nuevo.
        claves = sorted([{'cuando': '2026-10-22T12:00:05.100000+00:00'}, {'cuando': '2026-10-22T12:00:05Z'}, {'cuando': '2'},
                         {'cuando': '1'}], key=unir.hora)
        self.assertEqual([c['cuando'] for c in claves], ['1', '2', '2026-10-22T12:00:05Z', '2026-10-22T12:00:05.100000+00:00'])

    def test_ho1_el_reloj_repite_el_microsegundo(self):
        fijo = f.dt.datetime(2026, 10, 22, 12, 0, 5, 100000, tzinfo=f.dt.timezone.utc)

        class Reloj(f.dt.datetime):
            @classmethod
            def now(cls, tz=None):
                return fijo
        with patch.object(f.dt, 'datetime', Reloj):
            horas = [f.ahora() for _ in range(3)]
        self.assertEqual(len(set(horas)), 3)
        self.assertEqual(horas, sorted(horas))
        # Otro proceso (u otro clon) pudo haber escrito el último evento con la misma hora, o una adelantada: el nuevo va después.
        estado = {'eventos': [{'accion': 'mensaje', 'cuando': '2026-10-22T12:00:05.100000+00:00'}]}
        with patch.object(f.dt, 'datetime', Reloj), patch.object(f, '_ULTIMA_HORA', fijo - f.dt.timedelta(seconds=1)):
            f.evento(estado, 'mensaje', forma='mensaje', texto='otro')
        self.assertEqual(estado['eventos'][-1]['cuando'], '2026-10-22T12:00:05.100001+00:00')

    def test_ho1_archivar_ordena_los_cierres_por_la_hora(self):
        # Dos cambios cerrados sin archivar: uno viejo, cerrado al principio del segundo (en segundos y con Z), y uno nuevo,
        # cerrado una décima después, cuyo ID va primero. Se archiva primero el que se cerró antes.
        f.AGENTE = 'claude-code'
        try:
            nuevo, viejo = f.nuevo('Nuevo', capacidad='otra', sufijo='aaa'), f.nuevo('Viejo', capacidad='otra', sufijo='zzz')
        finally:
            f.AGENTE = None
        for ident, cuando in ((nuevo, '2026-10-22T12:00:05.100000+00:00'), (viejo, '2026-10-22T12:00:05Z')):
            carpeta, estado = f.leer(ident)
            estado.update(fase='cerrada', cierre={'cuando': cuando})
            estado.pop('archivo', None)
            f.ruta_registro(carpeta).write_text(json.dumps(estado))
        orden = []

        def plan(estado):
            orden.append(estado['id'])
            raise RuntimeError('alcanza con saber cuál va primero')
        with patch.object(f, 'plan_archivo', plan), self.assertRaises(RuntimeError):
            f.archivar()
        self.assertEqual(orden, [viejo])

    # --- ho2: al unir dos ramas, lo del mismo segundo queda en orden ----------------------------------------------------
    def test_ho2_unir_lo_del_mismo_segundo(self):
        base = {'eventos': [{'accion': 'cambio_creado', 'cuando': '2026-10-22T12:00:00+00:00'}]}
        ana = [{'accion': 'mensaje', 'texto': 'Ana 1', 'cuando': '2026-10-22T12:00:05.100000+00:00'},
               {'accion': 'mensaje', 'texto': 'Ana 2', 'cuando': '2026-10-22T12:00:05.700000+00:00'}]
        # Una rama vieja, con horas en segundos (una con «Z»), y otra nueva, en el mismo segundo: lo viejo cuenta desde el
        # principio de su segundo, y el resto va por su hora con microsegundos.
        beto = [{'accion': 'mensaje', 'texto': 'Beto viejo', 'cuando': '2026-10-22T12:00:05Z'},
                {'accion': 'mensaje', 'texto': 'Beto', 'cuando': '2026-10-22T12:00:05.400000+00:00'},
                {'accion': 'mensaje', 'texto': 'Beto después', 'cuando': '2026-10-22T12:00:06+00:00'}]
        unido = unir.unir(base, {'eventos': base['eventos'] + ana}, {'eventos': base['eventos'] + beto})
        self.assertEqual([e.get('texto') for e in unido['eventos']], [None, 'Beto viejo', 'Ana 1', 'Beto', 'Ana 2', 'Beto después'])
        # Si la unión deja decisiones para una persona, su evento lleva su propia hora con microsegundos, después de todo.
        viejo = {'eventos': [{'accion': 'cambio_creado', 'cuando': '2099-01-01T00:00:00Z'}]}
        unido = unir.unir(viejo, {**viejo, 'fase': 'a'}, {**viejo, 'fase': 'b'})
        [union] = [e for e in unido['eventos'] if e['accion'] == 'union_con_decisiones']
        self.assertRegex(union['cuando'], MICRO)
        self.assertGreater(unir.hora(union), unir.hora(viejo['eventos'][0]))
        pasado = {'eventos': [{'accion': 'cambio_creado', 'cuando': '2000-01-01T00:00:00Z'}]}
        hechas = [unir.unir(pasado, {**pasado, 'fase': 'a'}, {**pasado, 'fase': 'b'}) for _ in range(2)]
        self.assertEqual(hechas[0], hechas[1])  # la misma unión en dos clones da el mismo evento
        # Y el banco: mensajes de a turnos en dos ramas, sin esperar entre días, quedan en el orden de los días.
        # Hasta que en una corrida dos mensajes de las dos ramas caigan en el mismo segundo (casi siempre, la primera).
        for _ in range(5):
            with patch.object(banco.time, 'sleep', side_effect=AssertionError('el banco esperó entre días')):
                [fila] = banco.correr(20261022, ['a4_mensajes_de_a_turnos'])
            self.assertEqual(fila['resultado'], 'ok', fila['detalle'])
            juntos = int(next(d for d in fila['detalle'] if 'en el mismo segundo' in d).split()[0])
            if juntos:
                break
        self.assertGreater(juntos, 0)


if __name__ == '__main__':
    unittest.main()
