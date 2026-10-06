"""Fase 2 de la estructura: el estado de cada cambio y la configuración en .factory/; escenarios s1–s7 de la spec."""
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
from oracle_factory import migracion

GIT = ['git', '-c', 'user.name=Persona fixture', '-c', 'user.email=fixture@example.invalid', '-c', 'core.hooksPath=/dev/null',
       '-c', 'gc.auto=0', '-c', 'maintenance.auto=false']
ESTADO = ('factory.json', 'review.md', 'oracle-veredicto.txt')


class Estructura2(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'producto'
        self.root.mkdir()
        for name, value in [('ROOT', self.root), ('CHANGES', self.root / 'openspec/changes'), ('AGENTE', None)]:
            p = patch.object(f, name, value); p.start(); self.addCleanup(p.stop)
        p = patch.object(f, 'terminal_interactiva', return_value=True); p.start(); self.addCleanup(p.stop)
        p = patch.object(f, 'AVISADOS', set()); p.start(); self.addCleanup(p.stop)
        self.stdout = io.StringIO()
        p = contextlib.redirect_stdout(self.stdout); p.__enter__(); self.addCleanup(p.__exit__, None, None, None)
        f.inicializar()

    # --- ayudantes -----------------------------------------------------------------
    def escribe(self, frase):
        return patch('builtins.input', return_value=frase)

    def git(self, *args):
        return subprocess.run([*GIT, *args], cwd=self.root, check=True, capture_output=True, text=True).stdout.strip()

    def cambio_juzgado(self, titulo='Nota'):
        """Un cambio con revisión libre (review.md) y veredicto (oracle-veredicto.txt)."""
        ident = f.nuevo(titulo, con_ejemplo='notas')
        with self.escribe(f'APROBAR ESPECIFICACION {ident}'):
            f.aprobar_spec(ident)
        f.importar(ident)
        rid = f.leer(ident)[1]['requisitos'][0]
        f.medir(ident, requisito_id=rid, medidas=['notas.casos_ejecutados', 'notas.resultados'], quitar_sin_medir=True)
        if not (self.root / '.git').exists():
            subprocess.run(['git', 'init', '-q', '-b', 'main'], cwd=self.root, check=True)
        self.git('add', '.')
        self.git('commit', '-qm', 'producto fixture')
        informe = self.root / 'tareas' / ident / 'revision.md'
        informe.write_text('Fixture de revisión; no es una revisión real.\n')
        with self.escribe(f'REGISTRAR REVISION {ident}'):
            f.revisar(ident, informe, 'Persona fixture', 'aprobar', 0)
        hechos = self.root / 'tareas' / ident / 'hechos.json'
        subprocess.run([sys.executable, 'examples/notas/sensor.py', '--salida', hechos], cwd=self.root, check=True, capture_output=True)
        f.juzgar(ident, hechos)
        return ident

    def a_lugar_anterior(self, ident):
        """Deja el cambio como lo guardaban las versiones anteriores a la fase 2."""
        nuevo, viejo = self.root / '.factory/cambios' / ident, self.root / 'openspec/changes' / ident
        for nombre in ESTADO:
            if (nuevo / nombre).is_file():
                datos = (nuevo / nombre).read_text(encoding='utf-8')
                for archivo in ('review.md', 'oracle-veredicto.txt'):
                    datos = datos.replace(f'"{f.estructura.DIR}/cambios/{ident}/{archivo}"', f'"openspec/changes/{ident}/{archivo}"')
                (viejo / nombre).write_text(datos, encoding='utf-8')
                (nuevo / nombre).unlink()

    def estado(self, ident):
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            f.mostrar(ident)
        # las únicas diferencias admitidas son las rutas de los archivos movidos
        return salida.getvalue().replace(str(self.root), '<raiz>').replace(f'.factory/cambios/{ident}/', f'openspec/changes/{ident}/')

    def avisos(self, funcion, *args):
        errores = io.StringIO()
        with contextlib.redirect_stderr(errores):
            funcion(*args)
        return errores.getvalue()

    def migrar(self, verificar=False):
        errores = io.StringIO()
        with contextlib.redirect_stderr(errores):
            try:
                f.comando_migrar(verificar)
                return 0, errores.getvalue()
            except SystemExit as e:
                return e.code, errores.getvalue()

    def archivos_estado(self):
        return {str(p.relative_to(self.root)): p.read_bytes() for base in ('openspec/changes', '.factory/cambios')
                for p in sorted((self.root / base).rglob('*')) if p.is_file() and p.name in ESTADO}

    # --- s1: un cambio nuevo guarda su estado en .factory -------------------------------------------------------------
    def test_s1_cambio_nuevo_guarda_su_estado_en_factory(self):
        ident = self.cambio_juzgado()
        for nombre in ESTADO:
            self.assertTrue((self.root / '.factory/cambios' / ident / nombre).is_file(), nombre)
            self.assertFalse((self.root / 'openspec/changes' / ident / nombre).exists(), nombre)
        acuerdo = sorted(p.name for p in (self.root / 'openspec/changes' / ident).iterdir())
        self.assertEqual(acuerdo, ['design.md', 'proposal.md', 'specs', 'tasks.md'])
        estado = f.leer(ident)[1]
        self.assertEqual(estado['oracle']['informe'], f'.factory/cambios/{ident}/oracle-veredicto.txt')

    # --- s2: un proyecto no migrado sigue funcionando ---------------------------------------------------------------------
    def test_s2_cambio_anterior_a_la_fase_2(self):
        ident = self.cambio_juzgado()
        self.a_lugar_anterior(ident)
        self.assertIn('migrar', self.avisos(self.estado, ident))
        rid = f.leer(ident)[1]['requisitos'][0]
        f.medir(ident, requisito_id=rid, medidas=['notas.casos_ejecutados', 'notas.resultados'], quitar_sin_medir=True)
        self.assertTrue((self.root / 'openspec/changes' / ident / 'factory.json').is_file())  # se escribió ahí
        self.assertFalse((self.root / '.factory/cambios' / ident / 'factory.json').exists())  # y no se movió nada

    # --- s3: migrar mueve el estado sin cambiar su contenido ----------------------------------------------------------------
    def test_s3_migrar_mueve_el_estado_y_solo_reescribe_las_rutas_citadas(self):
        ident = self.cambio_juzgado()
        esperado = {n: (self.root / '.factory/cambios' / ident / n).read_bytes() for n in ESTADO}
        self.a_lugar_anterior(ident)
        self.assertEqual(self.migrar(), (0, ''))
        for nombre in ESTADO:
            self.assertEqual((self.root / '.factory/cambios' / ident / nombre).read_bytes(), esperado[nombre], nombre)
            self.assertFalse((self.root / 'openspec/changes' / ident / nombre).exists(), nombre)

    def test_s3_vista_previa_no_escribe_y_falla_mientras_haya_algo(self):
        ident = self.cambio_juzgado()
        self.a_lugar_anterior(ident)
        antes = self.archivos_estado()
        codigo, _ = self.migrar(verificar=True)
        self.assertEqual(codigo, 1)
        self.assertEqual(self.archivos_estado(), antes)
        self.assertIn(f'{ident}: openspec/changes/{ident}/factory.json -> .factory/cambios/{ident}/factory.json', self.stdout.getvalue())
        self.migrar()
        self.assertEqual(self.migrar(verificar=True)[0], 0)

    # --- s4: migrar no pierde ni pisa nada -------------------------------------------------------------------------------------
    def test_s4_segunda_ejecucion_no_cambia_nada(self):
        ident = self.cambio_juzgado()
        self.a_lugar_anterior(ident)
        self.migrar()
        antes = self.archivos_estado()
        self.assertEqual(self.migrar()[0], 0)
        self.assertEqual(self.archivos_estado(), antes)

    def test_s4_interrupcion_despues_de_escribir_y_antes_de_borrar(self):
        ident = self.cambio_juzgado()
        self.a_lugar_anterior(ident)
        movimientos, _ = migracion.planear(self.root)
        for m in movimientos:  # se corta aquí: lo nuevo escrito, lo viejo sin borrar
            migracion._escribir_atomico(m['destino'], m['bytes'])
        self.assertTrue((self.root / 'openspec/changes' / ident / 'factory.json').exists())
        # con el estado en los dos lugares, el vigente es el nuevo
        self.assertEqual(f.ruta_registro(self.root / 'openspec/changes' / ident), self.root / '.factory/cambios' / ident / 'factory.json')
        self.assertEqual(self.migrar()[0], 0)
        for nombre in ESTADO:
            self.assertFalse((self.root / 'openspec/changes' / ident / nombre).exists(), nombre)
            self.assertTrue((self.root / '.factory/cambios' / ident / nombre).exists(), nombre)

    def test_s4_corte_a_mitad_de_la_escritura_deja_el_viejo_entero(self):
        ident = self.cambio_juzgado()
        self.a_lugar_anterior(ident)
        antes = self.archivos_estado()
        with patch.object(migracion.os, 'replace', side_effect=OSError('disco lleno')), self.assertRaises(OSError):
            self.migrar()
        self.assertEqual({k: v for k, v in self.archivos_estado().items() if k.startswith('openspec')},
                         {k: v for k, v in antes.items() if k.startswith('openspec')})
        self.assertEqual(self.migrar()[0], 0)  # y la corrida siguiente termina el trabajo

    def test_s4_el_registro_es_lo_ultimo_que_se_escribe(self):
        ident = self.cambio_juzgado()
        self.a_lugar_anterior(ident)
        nombres = [m['destino'].name for m in migracion.planear(self.root)[0] if m['cambio'] == ident]
        self.assertEqual(nombres[-1], 'factory.json')  # un corte antes de él deja el registro viejo, que sigue siendo el vigente

    def test_s4_estado_en_los_dos_lugares_con_contenido_distinto(self):
        ident = self.cambio_juzgado()
        otro = f.nuevo('Otra nota', 'otra')
        self.a_lugar_anterior(ident)
        self.a_lugar_anterior(otro)
        nuevo = self.root / '.factory/cambios' / ident
        nuevo.mkdir(parents=True, exist_ok=True)
        (nuevo / 'factory.json').write_text('{"distinto": true}\n')
        antes = (self.root / 'openspec/changes' / ident / 'factory.json').read_bytes()
        codigo, errores = self.migrar()
        self.assertEqual(codigo, 1)
        self.assertIn(ident, errores)
        self.assertEqual((self.root / 'openspec/changes' / ident / 'factory.json').read_bytes(), antes)  # no se tocó
        self.assertEqual((nuevo / 'factory.json').read_text(), '{"distinto": true}\n')
        self.assertTrue((self.root / '.factory/cambios' / otro / 'factory.json').is_file())  # el otro sí se migró

    # --- s5: la migración conserva el significado ------------------------------------------------------------------------------
    def test_s5_estado_y_huella_iguales_antes_y_despues(self):
        ident = self.cambio_juzgado()
        self.git('add', '.')
        self.git('commit', '-qm', 'cambio juzgado')
        self.a_lugar_anterior(ident)
        antes = self.estado(ident)
        huella = f.contexto_producto()
        self.migrar()
        self.assertEqual(self.estado(ident), antes)
        self.assertTrue(f.mismo_producto(huella, f.contexto_producto()))
        self.assertEqual(f.pendientes_actuales(*f.leer(ident)), [])
        estado = f.leer(ident)[1]
        informe = self.root / estado['oracle']['informe']
        self.assertEqual(f.sha256(informe.read_bytes()), estado['oracle']['informe_sha256'])

    # --- s6: la configuración vive en .factory ----------------------------------------------------------------------------------------
    def test_s6_init_crea_la_configuracion_en_factory(self):
        config = json.loads((self.root / '.factory/config.json').read_text())
        self.assertEqual(config, {'modo_por_defecto': 'confirmacion', 'tipos_obligatorios': False})
        self.assertFalse((self.root / 'factory.json').exists())

    def test_s6_configuracion_en_factory_manda(self):
        (self.root / '.factory/config.json').write_text(json.dumps({'modo_por_defecto': 'autonomo'}))
        (self.root / 'factory.json').write_text(json.dumps({'modo_por_defecto': 'funcional'}))  # el de la raíz no cuenta
        with patch.object(f, 'terminal_interactiva', return_value=True), self.escribe('ELEGIR MODO autonomo'):
            ident = f.nuevo('Una', con_ejemplo='notas')
        self.assertEqual(f.leer(ident)[1]['modo'], 'autonomo')

    def test_s6_configuracion_en_la_raiz_se_respeta_y_se_avisa(self):
        (self.root / '.factory/config.json').unlink()
        (self.root / 'factory.json').write_text(json.dumps({'tipos_obligatorios': True}))
        errores = self.avisos(f.config_proyecto)
        self.assertIn('migrar', errores)
        self.assertTrue(f.config_proyecto()['tipos_obligatorios'])

    def test_s6_migrar_pasa_la_configuracion(self):
        (self.root / '.factory/config.json').unlink()
        (self.root / 'factory.json').write_text(json.dumps({'tipos_obligatorios': True}))
        self.assertEqual(self.migrar(verificar=True)[0], 1)
        self.assertIn('huella', self.stdout.getvalue())  # avisa que la configuración de la raíz es producto
        self.migrar()
        self.assertEqual(json.loads((self.root / '.factory/config.json').read_text()), {'tipos_obligatorios': True})
        self.assertFalse((self.root / 'factory.json').exists())

    # --- s7: los comandos de lectura entienden los dos lugares ---------------------------------------------------------------------
    def test_s7_lectura_con_cambios_en_los_dos_lugares(self):
        nuevo = self.cambio_juzgado()
        viejo = f.nuevo('Otra nota', 'otra')
        self.a_lugar_anterior(viejo)
        self.stdout.truncate(0); self.stdout.seek(0)
        f.listar(None, False, False)
        listado = self.stdout.getvalue()
        self.assertIn(nuevo, listado)
        self.assertIn(viejo, listado)
        self.stdout.truncate(0); self.stdout.seek(0)
        f.comando_donde(viejo, None)
        self.assertRegex(self.stdout.getvalue(), rf'(?m)^estado\s+existe\s+openspec/changes/{viejo}/factory\.json\s+— anterior a la fase 2')
        self.stdout.truncate(0); self.stdout.seek(0)
        f.comando_donde(nuevo, None)
        self.assertRegex(self.stdout.getvalue(), rf'(?m)^estado\s+existe\s+\.factory/cambios/{nuevo}/factory\.json\s*$')
        self.stdout.truncate(0); self.stdout.seek(0)
        f.comando_buscar('Nota', 50)
        self.assertIn(f'[{viejo}]', self.stdout.getvalue())


if __name__ == '__main__':
    unittest.main()
