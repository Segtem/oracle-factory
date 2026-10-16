"""La extensión de VS Code (editores/vscode/): escenarios vs1–vs3, en node con un `vscode` falso, sobre proyectos
temporales de Factory y la CLI de verdad."""
import json
import re
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_estructura as _estructura  # noqa: E402

f = _estructura.f
EXTENSION = _estructura.SOURCE / 'editores/vscode'
NODE = shutil.which('node')


def nodos(arbol):
    for nodo in arbol:
        yield nodo
        yield from nodos(nodo.get('hijos', []))


@unittest.skipUnless(NODE, 'hace falta node')
class Vscode(unittest.TestCase):
    # Los ayudantes de test_estructura sin heredar sus pruebas.
    setUp_estructura = _estructura.Estructura.setUp
    escribe, git, estado = _estructura.Estructura.escribe, _estructura.Estructura.git, _estructura.Estructura.estado
    cambio_medido, cambio_juzgado = _estructura.Estructura.cambio_medido, _estructura.Estructura.cambio_juzgado
    sha7 = _estructura.Estructura.sha7

    def setUp(self):
        self.setUp_estructura()
        # La CLI del proyecto, como la encuentra la extensión: .venv/bin/oracle-factory.
        self.cli = self.root / '.venv/bin/oracle-factory'
        self.cli.parent.mkdir(parents=True)
        self.cli.write_text(f'#!/bin/sh\nexec {sys.executable} -c "import sys; from oracle_factory.cli import main; '
                            f'sys.exit(main())" "$@"\n')
        self.cli.chmod(0o755)

    def vista(self, proyecto=None, comando=None):
        args = [NODE, str(_estructura.SOURCE / 'tests/vscode_en_node.cjs'), str(EXTENSION), str(proyecto or self.root)]
        r = subprocess.run(args + ([comando] if comando else []), capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def test_vs1_un_proyecto_con_un_cambio_abierto(self):
        cerrado = self.cambio_juzgado()
        with self.escribe('1'):
            f.cerrar(cerrado)
        self.assertEqual(self.estado(cerrado)['fase'], 'cerrada')
        abandonado = f.nuevo('Abandonado', capacidad='otra')
        with self.escribe('1'):
            f.abandonar(abandonado)
        self.assertEqual(self.estado(abandonado)['fase'], 'abandonada')
        # El ejemplo se trae una sola vez por proyecto: se saca el del cerrado y el abierto lo vuelve a traer igual.
        shutil.rmtree(self.root / 'examples/notas')
        for catalogo in (self.root / 'catalogos').glob('notas.*'):
            catalogo.unlink()
        abierto = self.cambio_medido()
        vista = self.vista()
        [cambio] = vista['arbol']
        self.assertEqual(cambio['descripcion'], self.estado(abierto)['fase'])
        self.assertEqual(cambio['etiqueta'], self.estado(abierto)['titulo'])
        hijos = {h['etiqueta'].split(':')[0]: h for h in cambio['hijos']}
        [requisito] = hijos['Requisitos']['hijos']
        rid = self.estado(abierto)['requisitos'][0]
        self.assertEqual(requisito['etiqueta'], rid.split('.')[-1])
        etiquetas = [h['etiqueta'] for h in requisito['hijos']]
        self.assertEqual(etiquetas[:2], ['notas.casos_ejecutados', 'notas.resultados'])
        self.assertRegex(etiquetas[2], r'^decidió .+ \(persona, ')
        self.assertEqual(hijos['Revisión']['etiqueta'], 'Revisión: aprobar')
        self.assertEqual(hijos['Revisión']['descripcion'], '0 hallazgos abiertos')
        self.assertEqual(hijos['Revisión']['abre'], self.estado(abierto)['revision']['informe'])
        self.assertTrue((self.root / hijos['Revisión']['abre']).is_file())
        self.assertEqual(hijos['Veredicto']['etiqueta'], 'Veredicto: pendiente')
        paso = f.pasos(abierto)[0]
        self.assertEqual(cambio['hijos'][0]['descripcion'], 'próximo paso')
        self.assertEqual(cambio['hijos'][0]['etiqueta'], paso.replace('oracle-factory', str(self.cli), 1))
        self.assertNotRegex(json.dumps(vista), re.escape(cerrado) + r'(?!-)')  # en el mismo segundo el abierto es <id>-1
        self.assertNotIn('Abandonado', json.dumps(vista))

    def test_vs1_una_carpeta_sin_factory_o_una_cli_que_falla(self):
        sin = Path(self.tmp.name) / 'sin-factory'
        sin.mkdir()
        self.assertEqual(self.vista(sin)['arbol'], [{'etiqueta': 'Esta carpeta no es un proyecto de Factory (no tiene '
                                                     '.factory/)', 'icono': 'info'}])
        falla = Path(self.tmp.name) / 'falla.sh'
        falla.write_text('#!/bin/sh\necho "la CLI se rompió" >&2\nexit 3\n')
        falla.chmod(0o755)
        [nodo] = self.vista(comando=str(falla))['arbol']
        self.assertEqual((nodo['etiqueta'], nodo['icono']), ('Factory falló: la CLI se rompió', 'error'))

    def test_vs2_los_artefactos_de_un_cambio(self):
        ident = self.cambio_medido()
        (self.root / 'openspec/changes' / ident / 'design.md').unlink()
        [cambio] = self.vista()['arbol']
        [artefactos] = [h for h in cambio['hijos'] if h['etiqueta'] == 'Artefactos']
        filas = {a['ruta']: a for a in f.datos_donde(ident, None)['artefactos']}
        self.assertEqual(len(artefactos['hijos']), len(filas))
        self.assertEqual(filas[f'openspec/changes/{ident}/design.md']['situacion'], 'ausente')
        for nodo, (ruta, fila) in zip(artefactos['hijos'], filas.items()):
            self.assertEqual(nodo['etiqueta'], ruta.split('/')[-1])
            if fila['situacion'] in ('existe', 'historico'):
                self.assertEqual(nodo['abre'], ruta)
                self.assertTrue((self.root / ruta).is_file())
            else:
                self.assertNotIn('abre', nodo)
                self.assertEqual((nodo['icono'], nodo['descripcion']), ('warning', f"{fila['gate']} · ausente"))
        self.assertLessEqual({'proposal.md', 'spec.md', 'factory.json', 'revision.md'},
                             {n['etiqueta'] for n in artefactos['hijos']})

    def test_vs3_un_paso_que_es_un_comando(self):
        ident = f.nuevo('Nota', con_ejemplo='notas')
        vista = self.vista()
        [cambio] = vista['arbol']
        esperado = f'{self.cli} aprobar-spec {ident}'
        self.assertEqual((cambio['hijos'][0]['etiqueta'], cambio['hijos'][0]['contexto']), (esperado, 'paso'))
        self.assertEqual(vista['terminal'], [{'terminal': 'Factory', 'cwd': str(self.root), 'texto': esperado,
                                              'enter': False}])
        self.assertIsNone(self.estado(ident).get('spec_aprobada'))  # escribirlo no lo decidió
        # Con factory.comando, la terminal recibe esa CLI, entre comillas si tiene espacios.
        otra = Path(self.tmp.name) / 'con espacio/oracle-factory'
        otra.parent.mkdir()
        shutil.copy2(self.cli, otra)
        self.assertEqual([t['texto'] for t in self.vista(comando=str(otra))['terminal']],
                         [f"'{otra}' aprobar-spec {ident}"])

    def test_vs3_un_paso_que_no_es_un_comando(self):
        ident = f.nuevo('Nota', con_ejemplo='notas')
        with self.escribe('1'):
            f.aprobar_spec(ident)
        f.importar(ident)
        rid = self.estado(ident)['requisitos'][0]
        f.medir(ident, requisito_id=rid, medidas=['notas.casos_ejecutados', 'notas.resultados'], quitar_sin_medir=True)
        subprocess.run(['git', 'init', '-q', '-b', 'main'], cwd=self.root, check=True)
        self.git('add', '.')
        self.git('commit', '-qm', 'producto fixture')
        (self.root / 'producto.txt').write_text('sin commitear\n')
        vista = self.vista()
        [cambio] = vista['arbol']
        paso = cambio['hijos'][0]
        self.assertTrue(paso['etiqueta'].startswith('commiteá los cambios del producto'), paso)
        self.assertNotIn('contexto', paso)
        self.assertEqual(vista['terminal'], [])
        self.assertEqual(vista['terminales'], 0)


if __name__ == '__main__':
    unittest.main()
