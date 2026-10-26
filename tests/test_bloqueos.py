"""Cada bloqueo de la revisión dice qué falta y cómo seguir: escenarios bl1 a bl4, con revisores de prueba y Clue real."""
import contextlib
import io
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_vueltas as _vueltas  # noqa: E402
from test_cli_humana import Terminal  # noqa: E402

f = _vueltas.f


class Bloqueos(_vueltas.Base):
    preparar = _vueltas.Vueltas.preparar
    candidato_nuevo = _vueltas.Vueltas.candidato_nuevo
    pedir = _vueltas.Vueltas.pedir
    paso = _vueltas.Vueltas.paso

    def declarar_revisor(self, nombre='codex'):
        """Declara un revisor sin pedirle nada."""
        ruta = self.root / '.factory/config.json'
        config = json.loads(ruta.read_text())
        config['revisores'] = {nombre: {'comando': [sys.executable, '-c', 'pass'], 'proveedor': 'p', 'modelo': 'm', 'tope_minutos': 1}}
        ruta.write_text(json.dumps(config))

    def revisar_bloqueada(self):
        with self.escribe(''), contextlib.redirect_stdout(Terminal()), contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(f.FactoryError) as e:
                f.revisar_paso_a_paso(self.ident)
        return str(e.exception)

    # --- bl1: sin revisor, el próximo paso lo explica ---------------------------------------------------------------------
    def test_bl1_sin_revisores_el_proximo_paso_explica_que_falta(self):
        self.preparar()
        paso = self.paso()
        self.assertIn('falta un revisor independiente', paso)
        self.assertIn('.factory/config.json', paso)
        self.assertNotIn('NOMBRE', paso)
        self.assertFalse(f.proximo_paso(self.ident).startswith('oracle-factory '))  # texto: la extensión no lo ofrece para ejecutar

    def test_bl1_con_un_revisor_el_comando_va_completo(self):
        self.preparar()
        self.declarar_revisor('agy')
        self.assertEqual(f.proximo_paso(self.ident), f'oracle-factory pedir-revision {self.ident} --a agy')

    # --- bl2: revisar bloqueado dice cómo seguir -------------------------------------------------------------------------------
    def test_bl2_revisar_sin_candidato_nombra_el_comando_con_el_revisor(self):
        self.preparar()
        self.declarar_revisor('agy')
        self.assertIn(f'oracle-factory pedir-revision {self.ident} --a agy', self.revisar_bloqueada())

    def test_bl2_revisar_con_evidencia_pero_sin_paquete_nombra_el_comando(self):
        self.preparar()
        self.declarar_revisor('agy')
        sha = self.git('rev-parse', '--short=7', 'HEAD')
        carpeta = f.estructura.ruta_canonica(self.root, self.ident, 'evidencia', sha)
        carpeta.mkdir(parents=True)
        (carpeta / 'resultado.json').write_text(json.dumps({'exitoso': True, 'tests': 1}))
        self.git('add', '.')
        self.git('commit', '-qm', 'evidencia')
        mensaje = self.revisar_bloqueada()
        self.assertIn('no tiene informes de revisores ni evidencia', mensaje)
        self.assertIn(f'oracle-factory pedir-revision {self.ident} --a agy', mensaje)

    def test_bl2_sin_revisores_revisar_explica_donde_declararlo(self):
        self.preparar()
        mensaje = self.revisar_bloqueada()
        self.assertIn('falta un revisor independiente', mensaje)
        self.assertNotIn('NOMBRE', mensaje)

    # --- bl3: --base vacio revisa todo el producto sin tocar Git -----------------------------------------------------------
    def test_bl3_base_vacia_incluye_todo_el_producto_y_no_toca_git(self):
        self.preparar()
        antes = {'head': self.git('rev-parse', 'HEAD'), 'ramas': self.git('branch', '--list', '--all'),
                 'config': self.git('config', '--local', '--list'), 'usuario': self.git('config', 'user.name')}
        self.revisor_con_base_vacia()
        despues = {'head': self.git('rev-parse', 'HEAD'), 'ramas': self.git('branch', '--list', '--all'),
                   'config': self.git('config', '--local', '--list'), 'usuario': self.git('config', 'user.name')}
        self.assertEqual(antes, despues)

    def revisor_con_base_vacia(self):
        self.pedir_con_base('vacio')
        paquetes = sorted(f.estructura.ruta_canonica(self.root, self.ident, 'clue', self.git('rev-parse', '--short=7', 'HEAD')).glob('*.json'))
        archivos = {a['file']: a['status'] for p in paquetes for a in json.loads(p.read_text())['files']}
        self.assertEqual(archivos.get('examples/notas/notas.py'), 'A')  # el producto entero entra como agregado

    def pedir_con_base(self, base):
        self.base = base
        return self.pedir('codex')

    def test_bl3_la_base_vacia_es_siempre_la_misma(self):
        self.preparar()
        base = f.base_vacia()
        self.assertEqual(base, f.base_vacia())
        self.assertEqual(self.git('log', '-1', '--format=%cI', base), '2000-01-01T00:00:00Z')  # fecha fija: mismo SHA siempre
        self.assertEqual(self.git('ls-tree', '-r', base), '')  # sin archivos

    # --- bl4: el paquete vacío nombra la salida -------------------------------------------------------------------------------
    def test_bl4_paquete_vacio_nombra_base_vacio(self):
        self.preparar()
        self.declarar_revisor('agy')
        sha = self.git('rev-parse', '--short=7', 'HEAD')
        carpeta = f.estructura.ruta_canonica(self.root, self.ident, 'evidencia', sha)
        carpeta.mkdir(parents=True)
        (carpeta / 'resultado.json').write_text(json.dumps({'exitoso': True, 'tests': 1}))
        self.git('add', '.')
        self.git('commit', '-qm', 'evidencia')  # sólo registros después del candidato: contra esta base no cambia el producto
        with self.assertRaises(f.FactoryError) as e:
            f.pedir_revision(self.ident, 'agy', base=self.git('rev-parse', 'HEAD'))
        self.assertIn('--base vacio', str(e.exception))


if __name__ == '__main__':
    unittest.main()
