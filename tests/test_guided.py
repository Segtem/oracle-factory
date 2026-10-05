"""Contratos observables con Oracle/Task reales, fallas de escritura y repos temporales."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from oracle_factory import cli as f


def setUpModule():
    # Estas pruebas representan a una persona que escribe en su terminal.
    terminal = patch.object(f, 'terminal_interactiva', return_value=True)
    terminal.start()
    unittest.addModuleCleanup(terminal.stop)


class ProyectoTemporal(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'producto'
        self.root.mkdir()
        for name, value in [('ROOT', self.root), ('CHANGES', self.root / 'openspec/changes')]:
            p = patch.object(f, name, value); p.start(); self.addCleanup(p.stop)
        self.stdout = io.StringIO()
        p = contextlib.redirect_stdout(self.stdout); p.__enter__(); self.addCleanup(p.__exit__, None, None, None)
        f.inicializar()

    def tasks(self):
        return list((self.root / 'tareas').iterdir())

    def crear(self):
        return f.nuevo('Un título de nota', con_ejemplo='notas')


class InicioGuiado(ProyectoTemporal):
    def test_ejemplo_completo_pendiente_y_sin_aprobaciones(self):
        ident = self.crear()
        folder, state = f.leer(ident)
        self.assertEqual(state['fase'], 'espera_aprobacion_spec')
        self.assertIsNone(state['spec_aprobada'])
        self.assertEqual(state['requisitos'], [])
        self.assertEqual((folder / 'proposal.md').read_bytes(), (self.root / 'examples/notas/proposal.md').read_bytes())
        self.assertEqual((self.root / state['spec']).read_bytes(), (self.root / 'examples/notas/spec.md').read_bytes())
        for p in (self.root / 'examples/notas/catalogos').iterdir():
            self.assertEqual(p.read_bytes(), (self.root / 'catalogos' / p.name).read_bytes())
        result = subprocess.run([f.sys.executable, '-m', 'unittest', 'discover', '-s', 'examples/notas', '-v'], cwd=self.root, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.root / '.git').exists())
        self.assertIn('aprobar-spec ' + ident, self.stdout.getvalue())

    def test_conflictos_se_rechazan_antes_de_crear_tarea(self):
        path = self.root / 'catalogos/notas.resultados.oracle'
        path.write_bytes(b'Medida del usuario\n')
        before = self.tasks()
        with self.assertRaises(f.FactoryError): self.crear()
        self.assertEqual(path.read_bytes(), b'Medida del usuario\n')
        self.assertEqual(self.tasks(), before)
        self.assertFalse((self.root / 'examples/notas').exists())

    def test_ejemplo_existente_no_crea_tarea_duplicada_al_reintentar(self):
        self.crear()
        before = self.tasks()
        for _ in range(2):
            with self.assertRaises(f.FactoryError): self.crear()
            self.assertEqual(self.tasks(), before)

    def test_capacidad_incompatible_o_padre_archivo_no_crea_tarea(self):
        before = self.tasks()
        with self.assertRaises(f.FactoryError): f.nuevo('Ajeno', 'otra', 'notas')
        (self.root / 'examples').write_text('No es carpeta')
        with self.assertRaises(f.FactoryError): self.crear()
        self.assertEqual(self.tasks(), before)
        self.assertEqual((self.root / 'examples').read_text(), 'No es carpeta')

    def test_copia_interrumpida_informa_destinos_y_no_crea_tarea(self):
        original = Path.open
        def fail(path, *args, **kwargs):
            if path.name == 'notas.resultados.oracle' and args and args[0] == 'xb':
                raise OSError('disco no disponible')
            return original(path, *args, **kwargs)
        before = self.tasks()
        with patch.object(Path, 'open', fail):
            with self.assertRaisesRegex(f.FactoryError, 'Archivos copiados:'): self.crear()
        self.assertEqual(self.tasks(), before)
        with self.assertRaises(f.FactoryError): self.crear()
        self.assertEqual(self.tasks(), before)

    def test_fallo_despues_de_crear_tarea_reporta_id_real_para_recuperar(self):
        original = Path.mkdir
        def fail(path, *args, **kwargs):
            if 'openspec' in path.parts and path.name == 'notas':
                raise OSError('falló creación del acuerdo')
            return original(path, *args, **kwargs)
        with patch.object(Path, 'mkdir', fail):
            with self.assertRaises(f.FactoryError) as error:
                self.crear()
        creadas = self.tasks()
        self.assertEqual(len(creadas), 1)
        self.assertIn(creadas[0].name, str(error.exception))
        self.assertIn('No crees otra tarea', str(error.exception))
        with self.assertRaises(f.FactoryError): self.crear()
        self.assertEqual(self.tasks(), creadas)

    def test_init_idempotente_conserva_configuracion_y_muestra_pasos_factory(self):
        config = self.root / 'oracle.json'
        original = config.read_bytes()
        ignore = self.root / '.gitignore'
        ignore.write_text('mis-salidas/\n')
        f.inicializar(); f.inicializar()
        self.assertEqual(config.read_bytes(), original)
        self.assertEqual(ignore.read_text(), 'mis-salidas/\n.factory-demo/\n.factory/local/\n__pycache__/\n*.py[cod]\n')
        self.assertNotIn('oracle caso nuevo', self.stdout.getvalue())

    def test_listar_recupera_cambio_y_no_confunde_tareas_solas(self):
        ident = self.crear()
        subprocess.run([f.sys.executable, '-m', 'oracle_task.cli', 'new', 'Sólo tracker', '--sufijo', 'tracker', '--proyecto', str(self.root)], check=True, capture_output=True)
        self.stdout.seek(0); self.stdout.truncate()
        f.listar()
        self.assertIn(ident + '  espera_aprobacion_spec', self.stdout.getvalue())
        self.assertNotIn('Sólo tracker', self.stdout.getvalue())

    def test_enlaces_de_destino_no_escriben_fuera_del_proyecto(self):
        outside = Path(self.tmp.name) / 'ajeno'; outside.mkdir()
        (self.root / 'examples').symlink_to(outside, target_is_directory=True)
        before = self.tasks()
        with self.assertRaises(f.FactoryError): self.crear()
        self.assertEqual(self.tasks(), before)
        self.assertEqual(list(outside.iterdir()), [])


class EleccionMedidas(ProyectoTemporal):
    # No heredar los tests del otro contrato como conteo duplicado.
    def setUp(self):
        super().setUp()
        self.ident = self.crear()
        with patch('builtins.input', return_value='APROBAR ESPECIFICACION ' + self.ident):
            f.aprobar_spec(self.ident)
        f.importar(self.ident)
        self.folder, state = f.leer(self.ident)
        self.rid = state['requisitos'][0]
        self.req = self.root / 'requisitos' / (self.rid + '.requisito')
        self.req.write_text('# Comentario que debe conservarse\n' + self.req.read_text())
        self.selected = ['notas.casos_ejecutados', 'notas.resultados']

    def asociar(self, **kwargs):
        f.medir(self.ident, requisito_id=self.rid, medidas=self.selected, **kwargs)

    def test_asociacion_preserva_prosa_fuente_comentarios_y_limite_parcial(self):
        from oracle_metalenguaje.nucleo.requisito import cargar
        before = cargar(self.req)
        self.asociar()
        after = cargar(self.req)
        self.assertEqual((before.id, before.texto, before.fuente, before.sin_medir), (after.id, after.texto, after.fuente, after.sin_medir))
        self.assertEqual(after.medido_por, tuple(self.selected))
        self.assertEqual(after.cobertura, 'parcial')
        self.assertTrue(self.req.read_text().startswith('# Comentario'))

    def test_quitar_limite_es_explicito_y_nuevo_limite_permanece_parcial(self):
        from oracle_metalenguaje.nucleo.requisito import cargar
        self.asociar(quitar_sin_medir=True)
        self.assertEqual(cargar(self.req).sin_medir, '')
        self.asociar(sin_medir='No se comprobó persistencia ni Unicode.')
        self.assertEqual(cargar(self.req).cobertura, 'parcial')
        self.assertEqual(cargar(self.req).sin_medir, 'No se comprobó persistencia ni Unicode.')

    def test_medida_inexistente_duplicada_o_requisito_ajeno_no_mutan(self):
        before = self.req.read_bytes(); state = (self.folder / 'factory.json').read_bytes()
        cases = [{'medidas':['notas.no_existe']}, {'medidas':[self.selected[0],self.selected[0]]}, {'requisito_id':'otro.requisito'}, {'sin_medir':''}]
        for case in cases:
            kwargs = {'requisito_id':self.rid, 'medidas':self.selected, **case}
            with self.subTest(case=case), self.assertRaises(f.FactoryError): f.medir(self.ident, **kwargs)
            self.assertEqual(self.req.read_bytes(), before)
            self.assertEqual((self.folder / 'factory.json').read_bytes(), state)

    def test_sintaxis_invalida_no_se_repara_ni_sobrescribe(self):
        self.req.write_text(self.req.read_text().replace('    texto ', '\ttexto '))
        before = self.req.read_bytes()
        with self.assertRaises(f.FactoryError): self.asociar()
        self.assertEqual(self.req.read_bytes(), before)

    def test_listado_es_solo_lectura_y_muestra_limites_y_fuentes(self):
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.stdout.seek(0); self.stdout.truncate()
        f.medir(self.ident, listar_opciones=True)
        self.assertEqual(before, {p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
        for value in (self.rid, 'notas.resultados', 'SIN MEDIR', 'Alcance:', 'Fuente:'):
            self.assertIn(value, self.stdout.getvalue())

    def test_cambio_invalida_y_repeticion_identica_conserva_validaciones(self):
        _, state = f.leer(self.ident)
        state.update(revision={'fixture':True}, oracle={'fixture':True})
        f.guardar(self.folder, state)
        self.asociar()
        _, after = f.leer(self.ident)
        self.assertIsNone(after['revision']); self.assertIsNone(after['oracle'])
        after.update(revision={'nueva':True}, oracle={'nuevo':True})
        f.guardar(self.folder, after)
        self.asociar()
        self.assertEqual(f.leer(self.ident)[1], after)

    def test_spec_desactualizada_rechaza_asociacion(self):
        spec = self.root / f.leer(self.ident)[1]['spec']
        spec.write_text(spec.read_text() + '\nCambio del acuerdo.\n')
        before = self.req.read_bytes()
        with self.assertRaises(f.FactoryError): self.asociar()
        self.assertEqual(self.req.read_bytes(), before)

    def test_enlace_en_requisito_rechazado(self):
        outside = Path(self.tmp.name) / 'original.requisito'; outside.write_bytes(self.req.read_bytes())
        self.req.unlink(); self.req.symlink_to(outside)
        before = outside.read_bytes()
        with self.assertRaises(f.FactoryError): self.asociar()
        self.assertEqual(outside.read_bytes(), before)

    def test_edicion_concurrente_detectada_no_sobrescribe_al_editor(self):
        original = f.bloqueo_medidas
        @contextlib.contextmanager
        def changed(*args):
            with original(*args):
                self.req.write_text(self.req.read_text() + '# Editado en otra sesión\n')
                yield
        with patch.object(f, 'bloqueo_medidas', changed):
            with self.assertRaises(f.FactoryError): self.asociar()
        self.assertTrue(self.req.read_text().endswith('# Editado en otra sesión\n'))
        self.assertNotIn('medido_por ', self.req.read_text())

    def test_escritura_fallida_conserva_requisito_y_no_deja_verde_viejo(self):
        before = self.req.read_bytes()
        original = f.os.replace
        def fail(src, dst):
            if Path(dst) == self.req: raise OSError('falló escritura requisito')
            return original(src, dst)
        _, state = f.leer(self.ident)
        state.update(revision={'fixture':True}, oracle={'fixture':True}); f.guardar(self.folder, state)
        with patch.object(f.os, 'replace', fail), self.assertRaises(OSError): self.asociar()
        self.assertEqual(self.req.read_bytes(), before)
        self.assertIsNone(f.leer(self.ident)[1]['oracle'])
        self.assertIsNone(f.leer(self.ident)[1]['revision'])
        self.assertFalse(any(p.name.startswith('.factory-') for p in self.req.parent.iterdir()))

    def test_catalogo_eliminado_durante_asociacion_no_muta(self):
        before = self.req.read_bytes()
        state = (self.folder / 'factory.json').read_bytes()
        original = f.inventario_medidas
        def inventory(*args):
            inventory.calls += 1
            if inventory.calls == 2: raise FileNotFoundError('catálogo eliminado por editor')
            return original(*args)
        inventory.calls = 0
        with patch.object(f, 'inventario_medidas', inventory):
            with self.assertRaisesRegex(f.FactoryError, 'catálogo cambió'):
                self.asociar()
        self.assertEqual(self.req.read_bytes(), before)
        self.assertEqual((self.folder / 'factory.json').read_bytes(), state)

if __name__ == '__main__':
    unittest.main()
