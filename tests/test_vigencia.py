"""Vigencia por contenido del producto: escenarios v1–v4 de la spec."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from oracle_factory import cli as f

GIT = ['git', '-c', 'user.name=Persona fixture', '-c', 'user.email=fixture@example.invalid', '-c', 'core.hooksPath=/dev/null']


class Vigencia(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'producto'
        self.root.mkdir()
        for name, value in [('ROOT', self.root), ('CHANGES', self.root / 'openspec/changes'), ('AGENTE', None)]:
            p = patch.object(f, name, value); p.start(); self.addCleanup(p.stop)
        p = patch.object(f, 'terminal_interactiva', return_value=True); p.start(); self.addCleanup(p.stop)
        self.stdout = io.StringIO()
        p = contextlib.redirect_stdout(self.stdout); p.__enter__(); self.addCleanup(p.__exit__, None, None, None)
        f.inicializar()

    # --- ayudantes -----------------------------------------------------------------
    def escribe(self, frase):
        return patch('builtins.input', return_value=frase)

    def git(self, *args):
        return subprocess.run([*GIT, *args], cwd=self.root, check=True, capture_output=True, text=True).stdout.strip()

    def head(self):
        return self.git('rev-parse', 'HEAD')

    def estado(self, ident):
        return f.leer(ident)[1]

    def cambio_medido(self):
        """Cambio con spec aceptada, requisitos importados, medidas elegidas y el producto commiteado."""
        ident = f.nuevo('Nota', con_ejemplo='notas')
        with self.escribe(f'APROBAR ESPECIFICACION {ident}'):
            f.aprobar_spec(ident)
        f.importar(ident)
        rid = self.estado(ident)['requisitos'][0]
        f.medir(ident, requisito_id=rid, medidas=['notas.casos_ejecutados', 'notas.resultados'], quitar_sin_medir=True)
        subprocess.run(['git', 'init', '-q', '-b', 'main'], cwd=self.root, check=True)
        self.git('add', '.')
        self.git('commit', '-qm', 'producto fixture')
        self.hechos = self.root / 'tareas' / ident / 'hechos.json'
        subprocess.run([sys.executable, 'examples/notas/sensor.py', '--salida', self.hechos], cwd=self.root,
                       check=True, capture_output=True)
        return ident

    def revision_libre(self, ident):
        informe = self.root / 'tareas' / ident / 'revision.md'
        informe.write_text('Fixture de revisión; no es una revisión real.\n')
        with self.escribe(f'REGISTRAR REVISION {ident}'):
            f.revisar(ident, informe, 'Persona fixture', 'aprobar', 0)

    def commit_de_registros(self, mensaje='registros'):
        (self.root / 'tareas').mkdir(exist_ok=True)
        (self.root / 'tareas' / 'nota.txt').write_text(mensaje + '\n')
        self.git('add', '.')
        self.git('commit', '-qm', mensaje)

    def desactualizado(self, ident):
        carpeta, estado = f.leer(ident)
        return any('desactualizado' in p for p in f.pendientes_actuales(carpeta, estado))

    def tocar_producto(self):
        notas = self.root / 'examples/notas/notas.py'
        notas.write_text(notas.read_text() + '\n# cambio del producto\n')

    # --- v1: vigencia por contenido ---------------------------------------------------
    def test_v1_commit_posterior_que_no_toca_el_producto(self):
        ident = self.cambio_medido()
        self.revision_libre(ident)
        antes = self.head()
        self.commit_de_registros()
        self.assertNotEqual(self.head(), antes)
        self.assertFalse(self.desactualizado(ident))
        f.juzgar(ident, self.hechos)
        self.commit_de_registros('otro commit de registros')
        self.assertFalse(self.desactualizado(ident))
        with self.escribe(f'CERRAR {ident}'):
            f.cerrar(ident)
        self.assertEqual(self.estado(ident)['fase'], 'cerrada')

    def test_v1_cambia_un_archivo_del_producto(self):
        ident = self.cambio_medido()
        self.revision_libre(ident)
        self.tocar_producto()
        self.assertTrue(self.desactualizado(ident))  # sin commit
        self.git('add', '.')
        self.git('commit', '-qm', 'cambio del producto')
        self.assertTrue(self.desactualizado(ident))  # con commit
        with self.assertRaisesRegex(f.FactoryError, 'desactualizado'):
            f.cerrar(ident)

    def test_v1_mismo_contenido_por_otra_historia(self):
        ident = self.cambio_medido()
        self.revision_libre(ident)
        antes = self.head()
        self.git('commit', '--amend', '-qm', 'el mismo producto con otro mensaje')
        self.assertNotEqual(self.head(), antes)
        self.assertFalse(self.desactualizado(ident))

    def test_v1_cambia_el_modo_ejecutable_del_producto(self):
        ident = self.cambio_medido()
        self.revision_libre(ident)
        (self.root / 'examples/notas/notas.py').chmod(0o755)  # el contenido es el mismo; el modo no
        self.assertTrue(self.desactualizado(ident))

    def test_v1_registro_sin_huella_queda_desactualizado(self):
        ident = self.cambio_medido()
        self.revision_libre(ident)
        ruta = self.root / 'openspec/changes' / ident / 'factory.json'
        estado = json.loads(ruta.read_text())
        del estado['revision']['contexto']['archivos_sha256']  # no hay con qué comparar: falla cerrado
        ruta.write_text(json.dumps(estado, ensure_ascii=False, indent=2) + '\n')
        self.assertTrue(self.desactualizado(ident))

    # --- v2: el commit observado se conserva y se muestra ---------------------------------
    def test_v2_aviso_de_head_distinto(self):
        ident = self.cambio_medido()
        self.revision_libre(ident)
        registrado = self.head()
        self.commit_de_registros()
        self.assertEqual(self.estado(ident)['revision']['contexto']['head'], registrado)  # se conserva
        self.stdout.truncate(0); self.stdout.seek(0)
        f.mostrar(ident)
        salida = self.stdout.getvalue()
        self.assertIn(f'registrada en {registrado[:7]}', salida)
        self.assertIn(f'HEAD actual {self.head()[:7]}', salida)
        self.assertIn('producto idéntico', salida)

    def test_v2_head_igual_sin_aviso(self):
        ident = self.cambio_medido()
        self.revision_libre(ident)
        self.stdout.truncate(0); self.stdout.seek(0)
        f.mostrar(ident)
        salida = self.stdout.getvalue()
        self.assertNotIn('Aviso:', salida)
        self.assertIn(f'revisión registrada sobre el commit {self.head()[:7]}', salida)  # el commit se muestra siempre

    def test_v2_cierre_muestra_el_commit_y_avisa(self):
        ident = self.cambio_medido()
        self.revision_libre(ident)
        registrado = self.head()
        f.juzgar(ident, self.hechos)
        self.commit_de_registros()
        self.stdout.truncate(0); self.stdout.seek(0)
        with self.escribe(f'CERRAR {ident}'):
            f.cerrar(ident)
        salida = self.stdout.getvalue()
        self.assertIn(f'revisión registrada sobre el commit {registrado[:7]}', salida)
        self.assertIn(f'HEAD actual {self.head()[:7]} con el producto idéntico', salida)

    def test_v2_contexto_sin_head_no_rompe(self):
        ident = self.cambio_medido()
        self.revision_libre(ident)
        ruta = self.root / 'openspec/changes' / ident / 'factory.json'
        estado = json.loads(ruta.read_text())
        del estado['revision']['contexto']['head']
        ruta.write_text(json.dumps(estado, ensure_ascii=False, indent=2) + '\n')
        self.stdout.truncate(0); self.stdout.seek(0)
        f.mostrar(ident)  # antes: KeyError
        self.assertIn('commit desconocido', self.stdout.getvalue())

    # --- v3: informe guiado vinculado al contenido -------------------------------------------
    def preparar_informe(self, ident):
        informe, decisiones = f.preparar_revision(ident)
        datos = json.loads(informe.read_text())
        datos.update(revisor='Persona fixture', completa=True, archivos_revisados=['examples/notas/notas.py'],
                     comprobaciones=[dict(descripcion='Tres casos del sensor', resultado='cumple', evidencia='hechos.json')],
                     limites=['Fixture; no es una revisión humana'], hallazgos=[],
                     sin_hallazgos_motivo='Sin defectos sembrados en este fixture')
        informe.write_bytes(f.bytes_json(datos))
        triage = json.loads(decisiones.read_text())
        triage.update(informe_sha256=f.sha256(informe.read_bytes()), actor='Persona fixture', motivo='Ensayo', decisiones=[])
        decisiones.write_bytes(f.bytes_json(triage))
        return informe, decisiones

    def registrar_guiado(self, ident, informe, decisiones):
        with self.escribe(f'REGISTRAR REVISION {ident}'):
            f.revisar(ident, informe, 'Persona fixture', 'aprobar', formato='guiado', decisiones=decisiones)

    def test_v3_informe_preparado_antes_de_un_commit_de_registros(self):
        ident = self.cambio_medido()
        informe, decisiones = self.preparar_informe(ident)
        preparado_en = self.head()
        self.commit_de_registros()  # commitear el informe completo no lo invalida
        self.registrar_guiado(ident, informe, decisiones)
        revision = self.estado(ident)['revision']
        self.assertEqual((revision['contexto']['head'], revision['head_preparacion']), (self.head(), preparado_en))
        self.assertFalse(self.desactualizado(ident))

    def test_v3_informe_de_otro_producto(self):
        ident = self.cambio_medido()
        informe, decisiones = self.preparar_informe(ident)
        notas = self.root / 'examples/notas/notas.py'
        original = notas.read_text()
        self.tocar_producto()
        antes = (self.root / 'openspec/changes' / ident / 'factory.json').read_bytes()
        with self.assertRaisesRegex(f.FactoryError, 'desactualizados.*prepará una nueva revisión'):
            self.registrar_guiado(ident, informe, decisiones)
        self.assertEqual((self.root / 'openspec/changes' / ident / 'factory.json').read_bytes(), antes)
        notas.write_text(original)  # la causa era el producto: restituido, el mismo informe se acepta
        self.registrar_guiado(ident, informe, decisiones)
        self.assertEqual(self.estado(ident)['revision']['decision'], 'aprobar')

    def test_v3_head_de_preparacion_que_no_es_un_commit_no_rompe(self):
        ident = self.cambio_medido()
        informe, decisiones = self.preparar_informe(ident)
        datos = json.loads(informe.read_text())
        datos['contexto']['head'] = 12345  # un informe puede traer cualquier cosa en el HEAD que declara
        informe.write_bytes(f.bytes_json(datos))
        triage = json.loads(decisiones.read_text())
        triage['informe_sha256'] = f.sha256(informe.read_bytes())
        decisiones.write_bytes(f.bytes_json(triage))
        self.registrar_guiado(ident, informe, decisiones)
        self.assertNotIn('head_preparacion', self.estado(ident)['revision'])
        self.stdout.truncate(0); self.stdout.seek(0)
        f.mostrar(ident)  # antes: TypeError
        self.commit_de_registros()
        f.juzgar(ident, self.hechos)
        with self.escribe(f'CERRAR {ident}'):
            f.cerrar(ident)  # antes: TypeError
        self.assertEqual(self.estado(ident)['fase'], 'cerrada')

    # --- v4: respetar los registros existentes --------------------------------------------------
    def test_v4_registro_anterior_a_este_cambio(self):
        ident = self.cambio_medido()
        self.revision_libre(ident)
        ruta = self.root / 'openspec/changes' / ident / 'factory.json'
        estado = json.loads(ruta.read_text())
        estado['revision']['contexto']['head'] = '0' * 40  # un registro de antes: otro HEAD, mismo producto
        ruta.write_text(json.dumps(estado, ensure_ascii=False, indent=2) + '\n')
        antes = ruta.read_bytes()
        self.assertFalse(self.desactualizado(ident))
        f.mostrar(ident)
        self.assertEqual(ruta.read_bytes(), antes)  # evaluarlo no migra ni reescribe nada


if __name__ == '__main__':
    unittest.main()
