"""Pedir una revisión independiente desde Factory: escenarios v1–v6 de la spec, con un revisor de prueba y Clue real."""
import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_archivo as _archivo  # noqa: E402

f = _archivo.f
from oracle_factory import revisores as rev_mod  # noqa: E402

AYUDANTES = ('setUp', 'escribe', 'git', 'salida', 'archivos')
# Un revisor de prueba: lee el paquete y deja un informe según el modo (ok, hallazgo, fuera, nada, dormir).
REVISOR = r'''
import json, sys, time
modo, paquete, informe = sys.argv[1], sys.argv[2], sys.argv[3]
if modo == "dormir":
    time.sleep(30)
if modo == "hijo":  # deja un hijo que ignora SIGTERM y sale con SIGTERM como lo haría un envoltorio
    import os, signal, subprocess
    hijo = subprocess.Popen([sys.executable, "-c", "import signal, time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(60)"])
    open(informe + ".pid", "w").write(str(hijo.pid))
    time.sleep(30)
if modo == "nada":
    print("no dejo informe"); sys.exit(0)
p = json.load(open(paquete))
archivo = p["files"][0]
linea = archivo["ranges"]["head"][0][0] if modo != "fuera" else 99999
hallazgos = [] if modo == "ok" else [{"id": "T-01", "kind": "bug", "severity": "baja", "confidence": 0.5, "title": "Un hallazgo",
    "explanation": "Explicación.", "location": {"file": archivo["file"], "start_line": linea, "end_line": linea, "side": "head"},
    "trigger": "t", "evidence": "e", "related_requirement": "r", "status": "pendiente", "verification": "v"}]
json.dump({"schema_version": "oracle-clue.review/v1", "repo": p["repo"], "base": p["base"], "head": p["head"],
           "diff_sha256": p["diff_sha256"], "context_sha256": p["context_sha256"],
           "provider": {"name": "revisor de prueba", "model": "fixture"}, "findings": hallazgos,
           "review_status": "completo", "limitations": ["Revisor de prueba."]}, open(informe, "w"))
print("informe escrito")
'''


class Base(unittest.TestCase):
    pass


for _nombre in AYUDANTES:
    setattr(Base, _nombre, getattr(_archivo.Archivo, _nombre))


@unittest.skipUnless(shutil.which('oracle-clue'), 'pedir-revision necesita oracle-clue')
class Revisores(Base):
    def preparar(self, modo='ok'):
        """Un cambio con una base, un commit de producto encima y un revisor de prueba configurado."""
        self.ident = f.nuevo('Nota', con_ejemplo='notas')
        with self.escribe(f'APROBAR ESPECIFICACION {self.ident}'):
            f.aprobar_spec(self.ident)
        f.importar(self.ident)
        self.git('add', '.')
        self.git('commit', '-qm', 'base')
        self.base = self.git('rev-parse', 'HEAD')
        notas = self.root / 'examples/notas/notas.py'
        notas.write_text(notas.read_text() + '\n# un cambio del producto\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'producto')
        script = Path(self.tmp.name) / 'revisor.py'
        script.write_text(REVISOR)
        self.configurar(modo, script)

    def configurar(self, modo, script=None):
        script = script or Path(self.tmp.name) / 'revisor.py'
        config = json.loads((self.root / '.factory/config.json').read_text())
        config['revisores'] = {'prueba': {'comando': [sys.executable, str(script), modo, '{paquete}', '{informe}'],
                                          'proveedor': 'revisor de prueba', 'modelo': 'fixture', 'tope_minutos': 1}}
        (self.root / '.factory/config.json').write_text(json.dumps(config))

    def pedir(self, *args, **kw):
        with contextlib.redirect_stdout(io.StringIO()):
            return f.pedir_revision(self.ident, 'prueba', *args, base=self.base, **kw)

    def carpeta(self):
        return self.root / '.factory/cambios' / self.ident / 'candidatos' / self.git('rev-parse', 'HEAD')[:7]

    def eventos(self):
        return [e for e in f.leer(self.ident)[1]['eventos'] if e['accion'] == 'revision_pedida']

    # --- v1: pedir una revisión del candidato actual --------------------------------------------------------------------
    def test_v1_revision_exitosa(self):
        self.preparar('hallazgo')
        destino = self.pedir()
        self.assertEqual(destino, self.carpeta() / 'revision' / 'prueba-1.json')
        self.assertEqual(len(json.loads(destino.read_text())['findings']), 1)
        self.assertTrue((self.carpeta() / 'revision' / 'prueba-1.pedido.md').is_file())
        self.assertTrue((self.carpeta() / 'clue' / 'paquete-prueba-1.json').is_file())
        self.assertTrue((self.root / '.factory/local/revisiones' / self.git('rev-parse', 'HEAD')[:7]).is_dir())  # el checkout

    def test_v1_guardar_el_informe_no_cambia_de_candidato(self):
        self.preparar()
        primero = self.pedir()
        self.git('add', '.')
        self.git('commit', '-qm', 'informe')  # sólo .factory/: el producto es el mismo
        segundo = self.pedir()
        self.assertEqual(segundo, primero.with_name('prueba-2.json'))
        self.assertEqual(self.eventos()[-1]['candidato'], primero.parent.parent.name)

    # --- v2: revisores configurables -----------------------------------------------------------------------------------
    def test_v2_revisor_no_declarado(self):
        self.preparar()
        antes = self.archivos()
        with self.assertRaises(f.FactoryError) as error:
            f.pedir_revision(self.ident, 'otro', base=self.base)
        self.assertIn('"revisores"', str(error.exception))  # muestra cómo declararlo
        self.assertEqual(self.archivos(), antes)
        self.assertEqual(self.eventos(), [])

    def test_v2_configuracion_invalida(self):
        self.preparar()
        config = json.loads((self.root / '.factory/config.json').read_text())
        for campo, valor in (('tope_minutos', 0), ('comando', ['programa', '{inform}']), ('comando', ['programa', '{Informe2}'])):
            invalida = json.loads(json.dumps(config))
            invalida['revisores']['prueba'][campo] = valor
            (self.root / '.factory/config.json').write_text(json.dumps(invalida))
            with self.assertRaises(f.FactoryError):
                f.config_proyecto()

    # --- v3: el pedido se genera desde el cambio ---------------------------------------------------------------------------
    def test_v3_plantilla_del_proyecto_e_indicaciones(self):
        self.preparar()
        (self.root / '.factory/pedido-revision.md').write_text('Pedido propio para $id sobre $candidato.\n')
        self.pedir('mirá la concurrencia')
        pedido = (self.carpeta() / 'revision' / 'prueba-1.pedido.md').read_text()
        self.assertTrue(pedido.startswith(f'Pedido propio para {self.ident} sobre {self.git("rev-parse", "HEAD")[:7]}.'))
        self.assertTrue(pedido.rstrip().endswith('mirá la concurrencia'))

    def test_v3_la_plantilla_de_factory_lleva_lo_necesario(self):
        self.preparar()
        self.pedir()
        pedido = (self.carpeta() / 'revision' / 'prueba-1.pedido.md').read_text()
        for parte in (self.ident, 'oracle-clue.review/v1', 'NO edites el checkout', 'oracle-clue validar', 'spec.md'):
            self.assertIn(parte, pedido)

    # --- v4: lo que sale mal no se guarda como informe ------------------------------------------------------------------------
    def falla(self, modo, esperado):
        self.preparar(modo)
        with self.assertRaises(f.FactoryError) as error:
            self.pedir()
        self.assertIn(esperado, str(error.exception))
        self.assertEqual(list((self.carpeta() / 'revision').glob('*')), [])
        self.assertTrue(list((self.root / '.factory/local/revisores').glob('*/salida.log')))  # la salida queda
        self.assertEqual(self.eventos()[-1]['resultado'], {'fuera': 'rechazado', 'nada': 'sin_informe', 'dormir': 'tope'}[modo])

    def test_v4_informe_que_clue_rechaza(self):
        self.falla('fuera', 'Clue rechazó')

    def test_v4_sin_informe(self):
        self.falla('nada', 'no dejó el informe')

    def test_v4_tope_superado(self):
        with patch.object(rev_mod, 'SEGUNDOS_POR_MINUTO', 1):
            self.falla('dormir', 'tope')

    def test_v4_tope_detiene_a_los_hijos(self):
        self.preparar('hijo')
        with patch.object(rev_mod, 'SEGUNDOS_POR_MINUTO', 1), self.assertRaises(f.FactoryError):
            self.pedir()
        pid = int(next((self.root / '.factory/local/revisores').glob('*/informe.json.pid')).read_text())
        with self.assertRaises(ProcessLookupError):
            os.kill(pid, 0)

    def test_v4_cambios_sin_commit(self):
        self.preparar()
        (self.root / 'examples/notas/notas.py').write_text('# sin commit\n')
        with self.assertRaises(f.FactoryError) as error:
            self.pedir()
        self.assertIn('sin commit', str(error.exception))
        self.assertEqual(self.eventos(), [])

    # --- v5: el revisor no decide -----------------------------------------------------------------------------------------------
    def test_v5_despues_de_una_revision_exitosa(self):
        self.preparar('hallazgo')
        antes = f.leer(self.ident)[1]
        self.pedir()
        despues = f.leer(self.ident)[1]
        self.assertEqual((despues['fase'], despues.get('revision')), (antes['fase'], antes.get('revision')))
        evento = self.eventos()[-1]
        self.assertEqual({k: evento[k] for k in ('revisor', 'proveedor', 'modelo', 'resultado', 'hallazgos')},
                         {'revisor': 'prueba', 'proveedor': 'revisor de prueba', 'modelo': 'fixture', 'resultado': 'ok', 'hallazgos': 1})
        self.assertEqual(evento['candidato'], self.git('rev-parse', 'HEAD')[:7])

    # --- v6: las vueltas anteriores se muestran sin decidirse otra vez -------------------------------------------------------
    def test_v6_tres_vueltas(self):
        self.preparar('hallazgo')
        self.pedir()
        for i in (2, 3):  # cada corrección es un candidato nuevo con su vuelta
            self.git('add', '.')
            self.git('commit', '-qm', f'informe {i - 1}')
            notas = self.root / 'examples/notas/notas.py'
            notas.write_text(notas.read_text() + f'# corrección {i}\n')
            self.git('add', '.')
            self.git('commit', '-qm', f'corrección {i}')
            self.configurar('ok' if i == 3 else 'hallazgo')
            self.pedir()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            informe, decisiones = f.preparar_revision(self.ident)
        informe = json.loads(informe.read_text())
        self.assertEqual(informe['hallazgos'], [])  # el vigente no tiene hallazgos
        vueltas = [c for c in informe['comprobaciones'] if c['descripcion'].startswith('Vuelta anterior')]
        self.assertEqual(len(vueltas), 2)
        self.assertTrue(all('T-01' in v['descripcion'] for v in vueltas))
        self.assertEqual(json.loads(decisiones.read_text())['decisiones'], [])  # nada para volver a decidir

    def test_v6_vuelta_de_otro_candidato(self):
        self.vuelta_que_no_se_muestra(lambda datos: {**datos, 'head': self.base}, 'es de otro candidato')

    def test_v6_vuelta_que_clue_no_valida(self):
        self.vuelta_que_no_se_muestra(lambda datos: {k: datos[k] for k in ('schema_version', 'head', 'findings')}, 'no lo uso')

    def vuelta_que_no_se_muestra(self, alterar, aviso):
        self.preparar('hallazgo')
        destino = self.pedir()
        destino.write_text(json.dumps(alterar(json.loads(destino.read_text()))))
        self.git('add', '.')
        self.git('commit', '-qm', 'informe')
        notas = self.root / 'examples/notas/notas.py'
        notas.write_text(notas.read_text() + '# corrección\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'corrección')
        self.configurar('ok')
        self.pedir()
        error = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(error):
            informe, _ = f.preparar_revision(self.ident)
        comprobaciones = json.loads(informe.read_text())['comprobaciones'] or []
        self.assertFalse([c for c in comprobaciones if c['descripcion'].startswith('Vuelta anterior')])
        self.assertIn(aviso, error.getvalue())


if __name__ == '__main__':
    unittest.main()
