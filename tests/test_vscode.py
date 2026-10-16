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
        falla.write_text('#!/bin/sh\nprintf "Traceback (most recent call last):\\n  ...\\nla CLI se rompió\\n" >&2\nexit 3\n')
        falla.chmod(0o755)
        [nodo] = self.vista(comando=str(falla))['arbol']
        self.assertEqual((nodo['etiqueta'], nodo['icono']), ('Factory falló: la CLI se rompió', 'error'))

    def test_vs2_los_artefactos_de_un_cambio(self):
        ident = self.cambio_juzgado()  # con carpetas de candidato, informe de revisión y veredicto
        self.assertEqual(self.estado(ident)['oracle']['codigo'], 0)
        [cambio] = self.vista()['arbol']
        self.assertEqual(next(h for h in cambio['hijos'] if h['etiqueta'].startswith('Veredicto'))['etiqueta'],
                         'Veredicto: exitoso')
        # Lo que falta: design.md y el informe de revisión, borrados.
        (self.root / 'openspec/changes' / ident / 'design.md').unlink()
        (self.root / self.estado(ident)['revision']['informe']).unlink()
        [cambio] = self.vista()['arbol']
        hijos = {h['etiqueta'].split(':')[0]: h for h in cambio['hijos']}
        self.assertNotIn('abre', hijos['Revisión'])
        self.assertEqual(hijos['Veredicto']['abre'], self.estado(ident)['oracle']['informe'])
        filas = f.datos_donde(ident, None)['artefactos']
        self.assertLessEqual({'existe', 'ausente'}, {a['situacion'] for a in filas})
        [artefactos] = [h for h in cambio['hijos'] if h['etiqueta'] == 'Artefactos']
        self.assertEqual(len(artefactos['hijos']), len(filas))
        carpetas = 0
        for nodo, fila in zip(artefactos['hijos'], filas):
            ruta = self.root / fila['ruta']
            self.assertEqual(nodo['etiqueta'], fila['ruta'].split('/')[-1])
            if fila['situacion'] in ('existe', 'historico') and ruta.is_file():
                self.assertEqual((nodo.get('abre'), nodo['icono']), (fila['ruta'], 'file'))
            elif fila['situacion'] in ('existe', 'historico') and ruta.is_dir():  # una carpeta se muestra, no se abre
                self.assertEqual((nodo.get('muestra'), nodo['icono']), (fila['ruta'], 'folder'))
                self.assertNotIn('abre', nodo)
                carpetas += 1
            else:
                self.assertNotIn('abre', nodo)
                self.assertNotIn('muestra', nodo)
                self.assertEqual(nodo['icono'], 'warning')
                self.assertIn(' · ', nodo['descripcion'])
        self.assertGreater(carpetas, 0)
        # Un valor no válido en el registro: donde lo marca (estado y resumen hoy no lo leen), y modelo.js no lo ofrece.
        estado = f.datos_estado(ident)
        registro = self.root / '.factory/cambios' / ident / 'factory.json'
        datos = json.loads(registro.read_text())
        datos['oracle']['informe'] = 5
        registro.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + '\n')
        estado['oracle']['informe'] = 5
        donde = f.datos_donde(ident, None)
        self.assertIn('no_valido', {a['situacion'] for a in donde['artefactos']})
        programa = ("const m = require(process.argv[1]); const fs = require('fs'), path = require('path');"
                    "const [e, d, raiz] = JSON.parse(fs.readFileSync(0, 'utf8'));"
                    "const tipo = r => { try { const s = fs.statSync(path.resolve(raiz, r));"
                    " return s.isFile() ? 'archivo' : s.isDirectory() ? 'carpeta' : null; } catch (x) { return null; } };"
                    "process.stdout.write(JSON.stringify(m.hijosCambio(e, d, 'oracle-factory', tipo)));")
        r = subprocess.run([NODE, '-e', programa, str(EXTENSION / 'modelo.js')], capture_output=True, text=True,
                           input=json.dumps([estado, donde, str(self.root)]))
        self.assertEqual(r.returncode, 0, r.stderr)
        hijos = json.loads(r.stdout)
        [veredicto] = [h for h in hijos if h['etiqueta'].startswith('Veredicto')]
        self.assertNotIn('abrir', veredicto)
        # Un informe vacío no es la carpeta del proyecto.
        estado['revision']['informe'] = ''
        r = subprocess.run([NODE, '-e', programa, str(EXTENSION / 'modelo.js')], capture_output=True, text=True,
                           input=json.dumps([estado, donde, str(self.root)]))
        [revision] = [h for h in json.loads(r.stdout) if h['etiqueta'].startswith('Revisión')]
        self.assertFalse({'abrir', 'mostrar'} & set(revision))
        [artefactos] = [h for h in hijos if h['etiqueta'] == 'Artefactos']
        for nodo, fila in zip(artefactos['hijos'], donde['artefactos']):
            if fila['situacion'] == 'no_valido':
                self.assertEqual((nodo['icono'], nodo['descripcion']), ('warning', f"{fila['gate']} · no_valido"))
                self.assertNotIn('abrir', nodo)
                self.assertNotIn('mostrar', nodo)

    def test_vs3_un_paso_que_es_un_comando(self):
        ident = f.nuevo('Nota', con_ejemplo='notas')
        vista = self.vista()
        [cambio] = vista['arbol']
        esperado = f'{self.cli} aprobar-spec {ident}'
        self.assertEqual((cambio['hijos'][0]['etiqueta'], cambio['hijos'][0]['contexto']), (esperado, 'paso'))
        # Sin requisitos importados todavía, «Requisitos» no se despliega.
        [requisitos] = [h for h in cambio['hijos'] if h['etiqueta'] == 'Requisitos']
        self.assertEqual((requisitos['descripcion'], 'hijos' in requisitos), ('0', False))
        self.assertEqual(vista['terminal'], [{'terminal': 'Factory', 'cwd': str(self.root), 'texto': esperado,
                                              'enter': False}])
        self.assertIsNone(self.estado(ident).get('spec_aprobada'))  # escribirlo no lo decidió
        # Con factory.comando, la terminal recibe esa CLI, entre comillas si tiene espacios.
        otra = Path(self.tmp.name) / 'con espacio/oracle-factory'
        otra.parent.mkdir()
        shutil.copy2(self.cli, otra)
        self.assertEqual([t['texto'] for t in self.vista(comando=str(otra))['terminal']],
                         [f"'{otra}' aprobar-spec {ident}"])
        # Una ' en la ruta: lo que se escribe lo leen bien bash y fish (la persona lo ejecuta en su shell).
        rara = Path(self.tmp.name) / "it's/oracle-factory"
        rara.parent.mkdir()
        shutil.copy2(self.cli, rara)
        [texto] = [t['texto'] for t in self.vista(comando=str(rara))['terminal']]
        self.assertEqual(texto, "'" + str(rara).replace("'", "'\\''") + f"' aprobar-spec {ident}")
        for shell in ('bash', 'fish'):
            if shutil.which(shell):
                r = subprocess.run([shell, '-c', texto.replace(f' aprobar-spec {ident}', ' --version')],
                                   capture_output=True, text=True, cwd=self.root)
                self.assertEqual(r.returncode, 0, (shell, r.stderr))

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
