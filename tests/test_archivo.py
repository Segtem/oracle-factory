"""Archivar al cerrar: la spec de cada cambio se fusiona en openspec/specs/; escenarios a1–a6 de la spec."""
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

GIT = ['git', '-c', 'user.name=Persona fixture', '-c', 'user.email=fixture@example.invalid', '-c', 'core.hooksPath=/dev/null',
       '-c', 'gc.auto=0', '-c', 'maintenance.auto=false']
MODIFICA = '''# Capability: notas

## MODIFIED Requirements

### Requirement: titulo valido
Tipo: funcional
The system SHALL reject titles longer than 80 characters as well as empty ones.

#### Scenario: título largo
- WHEN el título tiene 81 caracteres
- THEN no se puede guardar la nota
'''
QUITA = '''# Capability: notas

## REMOVED Requirements

### Requirement: titulo valido
Ya no aplica.

## ADDED Requirements

### Requirement: nota con fecha
Tipo: funcional
The system SHALL record the creation date of each note.

#### Scenario: nota nueva
- WHEN se guarda una nota
- THEN tiene fecha de creación
'''


class Archivo(unittest.TestCase):
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
        subprocess.run(['git', 'init', '-q', '-b', 'main'], cwd=self.root, check=True)

    # --- ayudantes -----------------------------------------------------------------
    def escribe(self, frase):
        return patch('builtins.input', return_value=frase)

    def git(self, *args):
        return subprocess.run([*GIT, *args], cwd=self.root, check=True, capture_output=True, text=True).stdout.strip()

    def salida(self):
        texto = self.stdout.getvalue()
        self.stdout.truncate(0); self.stdout.seek(0)
        return texto

    def cambio_cerrado(self):
        """El ejemplo de notas recorrido de punta a punta y cerrado por una persona."""
        ident = f.nuevo('Nota', con_ejemplo='notas')
        with self.escribe(f'APROBAR ESPECIFICACION {ident}'):
            f.aprobar_spec(ident)
        f.importar(ident)
        rid = f.leer(ident)[1]['requisitos'][0]
        f.medir(ident, requisito_id=rid, medidas=['notas.casos_ejecutados', 'notas.resultados'], quitar_sin_medir=True)
        self.git('add', '.')
        self.git('commit', '-qm', 'producto fixture')
        informe = self.root / 'tareas' / ident / 'revision.md'
        informe.write_text('Fixture de revisión; no es una revisión real.\n')
        with self.escribe(f'REGISTRAR REVISION {ident}'):
            f.revisar(ident, informe, 'Persona fixture', 'aprobar', 0)
        hechos = self.root / 'tareas' / ident / 'hechos.json'
        subprocess.run([sys.executable, 'examples/notas/sensor.py', '--salida', hechos], cwd=self.root, check=True, capture_output=True)
        f.juzgar(ident, hechos)
        with self.escribe(f'CERRAR {ident}'):
            f.cerrar(ident)
        return ident

    def cambio_importado(self, titulo, capacidad, spec):
        """Un cambio con la spec dada, aceptada e importada (sin el recorrido de medidas, revisión y juicio)."""
        ident = f.nuevo(titulo, capacidad)
        carpeta, estado = f.leer(ident)
        (self.root / estado['spec']).write_text(spec, encoding='utf-8')
        (carpeta / 'proposal.md').write_text(f'# {titulo}\n\nFixture.\n', encoding='utf-8')
        with self.escribe(f'APROBAR ESPECIFICACION {ident}'):
            f.aprobar_spec(ident)
        f.importar(ident)
        return ident

    def marcar_cerrado(self, ident, cuando):
        """Cierra el registro sin el recorrido completo: archivar sólo mira la fase y el orden de cierre."""
        carpeta, estado = f.leer(ident)
        estado.update(fase='cerrada', cierre={'actor': 'Persona fixture', 'tipo_actor': 'persona', 'forma': 'decidio', 'modo': 'confirmacion',
                                              'cuando': cuando})
        f.guardar(carpeta, estado)

    def consolidada(self, capacidad='notas'):
        return (self.root / 'openspec/specs' / capacidad / 'spec.md').read_text(encoding='utf-8')

    def archivos(self):
        return {str(p.relative_to(self.root)): p.read_bytes() for p in sorted(self.root.rglob('*'))
                if p.is_file() and '.git' not in p.relative_to(self.root).parts}

    # --- a1: la spec de un cambio se fusiona al cerrarlo -------------------------------------------------------
    def test_a1_primer_cambio_de_una_capacidad(self):
        ident = self.cambio_cerrado()
        estado = f.leer(ident)[1]
        texto = self.consolidada()
        self.assertIn('### Requirement: titulo valido', texto)
        self.assertIn(f'Origen: {ident} · {estado["requisitos"][0]}', texto)
        self.assertIn('#### Scenario: título vacío', texto)
        self.assertEqual(estado['archivo']['spec'], 'openspec/specs/notas/spec.md')
        self.assertEqual([e['accion'] for e in estado['eventos']][-2:], ['cierre', 'archivado'])

    def test_a1_un_cambio_que_modifica_y_quita_requisitos(self):
        primero = self.cambio_cerrado()
        modifica = self.cambio_importado('Títulos largos', 'notas', MODIFICA)
        self.marcar_cerrado(modifica, '2099-01-01T00:00:00+00:00')
        f.archivar()
        texto = self.consolidada()
        self.assertIn('longer than 80 characters', texto)
        self.assertIn(f'Origen: {modifica} ·', texto)
        self.assertNotIn('whitespace-only', texto)  # el texto viejo ya no está
        quita = self.cambio_importado('Fechas', 'notas', QUITA)
        self.marcar_cerrado(quita, '2099-01-02T00:00:00+00:00')
        f.archivar()
        texto = self.consolidada()
        self.assertNotIn('titulo valido', texto)
        self.assertIn('### Requirement: nota con fecha', texto)
        self.assertTrue(primero)

    # --- a2: un conflicto impide cerrar --------------------------------------------------------------------------
    def test_a2_agregar_un_requisito_que_ya_existe(self):
        self.cambio_cerrado()
        repetido = self.cambio_importado('Otra vez', 'notas', (self.root / 'examples/notas/spec.md').read_text())
        antes = self.archivos()
        with patch.object(f, 'pendientes_actuales', return_value=[]), self.escribe(f'CERRAR {repetido}'), \
                self.assertRaises(f.FactoryError) as error:
            f.cerrar(repetido)
        self.assertIn('titulo valido', str(error.exception))
        self.assertEqual(self.archivos(), antes)  # ni el registro ni la spec consolidada cambiaron
        self.assertNotEqual(f.leer(repetido)[1]['fase'], 'cerrada')

    def test_a2_modificar_un_requisito_que_no_existe(self):
        ident = self.cambio_importado('Sin base', 'notas', MODIFICA)
        self.marcar_cerrado(ident, '2099-01-01T00:00:00+00:00')
        antes = self.archivos()
        with self.assertRaises(f.FactoryError) as error:
            f.archivar()
        self.assertIn('no existe', str(error.exception))
        self.assertEqual(self.archivos(), antes)

    # --- a3: lo cerrado no se mueve ni se reescribe ---------------------------------------------------------------
    def test_a3_archivar_solo_agrega_la_marca(self):
        primero = self.cambio_cerrado()
        otro = self.cambio_importado('Títulos largos', 'notas', MODIFICA)
        self.marcar_cerrado(otro, '2099-01-01T00:00:00+00:00')
        antes = self.archivos()
        estado_primero = f.leer(primero)[1]
        f.archivar()
        despues = self.archivos()
        cambiados = {k for k in set(antes) | set(despues) if antes.get(k) != despues.get(k)}
        self.assertEqual(cambiados, {f'.factory/cambios/{otro}/factory.json', 'openspec/specs/notas/spec.md',
                                     '.factory/specs/notas.json'})
        self.assertEqual(f.leer(primero)[1], estado_primero)  # el cambio anterior no se tocó
        nuevo = f.leer(otro)[1]
        self.assertEqual(nuevo['eventos'][-1]['accion'], 'archivado')

    # --- a4: se distingue lo vigente de lo reemplazado --------------------------------------------------------------
    def test_a4_requisito_reemplazado(self):
        primero = self.cambio_cerrado()
        modifica = self.cambio_importado('Títulos largos', 'notas', MODIFICA)
        self.marcar_cerrado(modifica, '2099-01-01T00:00:00+00:00')
        f.archivar()
        self.salida()
        f.mostrar(primero)
        rid = f.leer(primero)[1]['requisitos'][0]
        self.assertIn(f'{rid}: reemplazado por {modifica}', self.salida())
        f.mostrar(modifica)
        self.assertIn(f'{f.leer(modifica)[1]["requisitos"][0]}: vigente', self.salida())

    # --- a5: una capacidad con un solo nombre -----------------------------------------------------------------------
    def test_a5_capacidad_con_alias(self):
        config = self.root / '.factory/config.json'
        config.write_text(json.dumps({'capacidades': {'notas2': 'notas'}}))
        self.cambio_cerrado()
        errores = io.StringIO()
        with contextlib.redirect_stderr(errores):
            ident = self.cambio_importado('Fechas', 'notas2', QUITA.replace('Capability: notas', 'Capability: notas2'))
        self.assertIn('alias de notas', errores.getvalue())
        self.marcar_cerrado(ident, '2099-01-01T00:00:00+00:00')
        f.archivar()
        self.assertIn('### Requirement: nota con fecha', self.consolidada())
        self.assertFalse((self.root / 'openspec/specs/notas2').exists())

    def test_a5_un_alias_de_un_alias_se_rechaza(self):
        (self.root / '.factory/config.json').write_text(json.dumps({'capacidades': {'a': 'b', 'b': 'c'}}))
        with self.assertRaises(f.FactoryError):
            f.config_proyecto()

    # --- a6: archivar es repetible y los comandos de lectura lo muestran -----------------------------------------------
    def test_a6_segunda_ejecucion_no_cambia_nada(self):
        self.cambio_cerrado()
        ident = self.cambio_importado('Títulos largos', 'notas', MODIFICA)
        self.marcar_cerrado(ident, '2099-01-01T00:00:00+00:00')
        f.archivar()
        antes = self.archivos()
        self.salida()
        f.archivar()
        self.assertIn('No hay cambios cerrados sin archivar', self.salida())
        self.assertEqual(self.archivos(), antes)

    def test_a6_reintento_de_un_cierre_cortado_no_duplica(self):
        real = f.ejecutar

        def falla_al_cerrar_la_tarea(argv, *a, **k):
            if argv[:2] == ['tasks', 'close']:
                return subprocess.CompletedProcess(argv, 1, '', 'tracker no disponible')
            return real(argv, *a, **k)

        with patch.object(f, 'ejecutar', falla_al_cerrar_la_tarea), self.assertRaises(f.FactoryError):
            self.cambio_cerrado()  # la spec ya se fusionó, pero el cierre no se completó
        ident = f.leer(sorted(p.name for p in (self.root / 'openspec/changes').iterdir())[0])[1]['id']
        with self.escribe(f'CERRAR {ident}'):
            f.cerrar(ident)  # el reintento no choca con su propia fusión
        self.assertEqual(self.consolidada().count('### Requirement: titulo valido'), 1)
        self.assertEqual(f.leer(ident)[1]['fase'], 'cerrada')

    def test_a6_solo_se_archivan_los_cerrados_y_en_el_orden_de_cierre(self):
        self.cambio_cerrado()
        quita = self.cambio_importado('Fechas', 'notas', QUITA)  # creado antes, cerrado después
        modifica = self.cambio_importado('Títulos largos', 'notas', MODIFICA)
        abierto = self.cambio_importado('Abierto', 'otra', '# Capability: otra\n\n' + QUITA.split('Ya no aplica.\n\n')[1])
        self.marcar_cerrado(modifica, '2099-01-01T00:00:00+00:00')
        self.marcar_cerrado(quita, '2099-01-02T00:00:00+00:00')
        f.archivar()  # en orden de creación chocaría: quitar «titulo valido» y después modificarlo
        self.assertIn('### Requirement: nota con fecha', self.consolidada())
        self.assertNotIn('archivo', f.leer(abierto)[1])
        self.assertFalse((self.root / 'openspec/specs/otra').exists())

    def test_a6_lectura_de_un_cambio_archivado(self):
        ident = self.cambio_cerrado()
        self.salida()
        f.listar(None, False, False)
        self.assertRegex(self.salida(), rf'{ident}  cerrada \(archivado\)')
        f.comando_donde(ident, None)
        self.assertRegex(self.salida(), r'(?m)^archivo\s+existe\s+openspec/specs/notas/spec\.md')
        f.comando_buscar('whitespace-only', 50)
        self.assertIn('openspec/specs/notas/spec.md', self.salida())


if __name__ == '__main__':
    unittest.main()
