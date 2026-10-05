"""Regresiones del flujo con Git real; las respuestas Oracle se modelan por separado."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import fabrica as f


def setUpModule():
    # Estas pruebas representan a una persona que escribe en su terminal.
    terminal = patch.object(f, 'terminal_interactiva', return_value=True)
    terminal.start()
    unittest.addModuleCleanup(terminal.stop)

ID = '20260101-120000-ejemplo'
RID = 'demo.promesa'

class Flujo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'repo'
        self.root.mkdir()
        self.folder = self.root / 'openspec/changes' / ID
        self.folder.mkdir(parents=True)
        self.spec = self.folder / 'specs/demo/spec.md'
        self.spec.parent.mkdir(parents=True)
        self.spec.write_text('### Requirement: promesa\nSHALL funcionar.\n#### Scenario: esperado\n- THEN resultado\n')
        (self.folder / 'proposal.md').write_text('Un cambio aprobado de prueba.\n')
        (self.folder / 'tasks.md').write_text('- [ ] Implementar\n')
        (self.root / 'producto.py').write_text('valor = 1\n')
        self.facts = Path(self.tmp.name) / 'hechos.json'
        self.facts.write_text('{}')
        self.report = Path(self.tmp.name) / 'revision.md'
        self.report.write_text('Revisión del producto: sin hallazgos.\n')
        for name, value in [('ROOT', self.root), ('CHANGES', self.root / 'openspec/changes')]:
            patcher = patch.object(f, name, value); patcher.start(); self.addCleanup(patcher.stop)
        patcher = patch.object(f, 'nota_tarea'); self.note = patcher.start(); self.addCleanup(patcher.stop)
        quiet = contextlib.redirect_stdout(io.StringIO()); quiet.__enter__(); self.addCleanup(quiet.__exit__, None, None, None)
        f.guardar(self.folder, {'id': ID, 'titulo': 'Ejemplo', 'capacidad': 'demo', 'spec': str(self.spec.relative_to(self.root)), 'fase': 'espera_aprobacion_spec', 'eventos': [], 'requisitos': [], 'revision': None, 'oracle': None})
        self.git('init', '-q', '-b', 'main')
        self.git('add', '.')
        self.git('-c', 'user.name=Prueba', '-c', 'user.email=prueba@example.invalid', 'commit', '-qm', 'base')
        self.aprobar()
        s=self.state(); s['requisitos']=[RID]; f.guardar(self.folder,s)
        self.exec_real = f.ejecutar

    def git(self, *args):
        return subprocess.run(['git', *args], cwd=self.root, text=True, capture_output=True, check=True)

    def state(self):
        return json.loads((self.folder / 'factory.json').read_text())

    def aprobar(self):
        with patch('builtins.input', return_value=f'APROBAR ESPECIFICACION {ID}'):
            f.aprobar_spec(ID)

    def revisar(self):
        with patch('builtins.input', return_value=f'REGISTRAR REVISION {ID}'):
            f.revisar(ID, self.report, 'humano', 'aprobar', 0)

    def oracle(self, juicio=None, coverage=None):
        def execute(args):
            if args[0] == 'oracle':
                output = juicio if '--con' in args else coverage
                if output is None: output = f'✓ {RID}   cumple · demo.medida cumple\n'
                return subprocess.CompletedProcess(args, 0, output, '')
            return self.exec_real(args)
        return patch.object(f, 'ejecutar', side_effect=execute)

    def verde(self):
        self.revisar()
        with self.oracle(): f.juzgar(ID, self.facts)
        self.assertEqual(f.pendientes_actuales(self.folder,self.state()), [])

    def test_flujo_completo_y_cierre(self):
        self.verde()
        with patch('builtins.input', return_value=f'CERRAR {ID}'), patch.object(f,'ejecutar', wraps=self.exec_real) as run:
            # Sólo se sustituye el cierre del tracker; las huellas usan Git real.
            def execute(args):
                if args[:2] == ['tasks','close']: return subprocess.CompletedProcess(args,0,'Cerrada','')
                return self.exec_real(args)
            run.side_effect=execute
            f.cerrar(ID)
        self.assertEqual(self.state()['fase'],'cerrada')
        with self.assertRaises(f.FactoryError): self.aprobar()

    def test_sin_juicio_o_sombra_no_son_verde_aunque_oracle_sale_cero(self):
        for row in (f'? {RID}   sin juicio · demo.medida sin evidencia\n',
                    f'✗ {RID}   no cumple · demo.medida falla en sombra\n'):
            with self.subTest(row=row), self.oracle(juicio=row):
                with self.assertRaises(f.FactoryError): f.juzgar(ID, self.facts)
                self.assertEqual(self.state()['oracle']['codigo'],1)
                self.assertEqual(self.state()['oracle']['codigo_oracle'],0)

    def test_parcial_y_requisito_ausente_bloquean(self):
        for row in (f'◐ {RID}   demo.medida · SIN MEDIR: otro caso\n',
                    f'✓ {RID}_otro   demo.medida\n'):
            with self.subTest(row=row), self.oracle(coverage=row):
                with self.assertRaises(f.FactoryError): f.juzgar(ID,self.facts)
                self.assertIsNone(self.state()['oracle'])

    def test_codigo_nuevo_modificado_o_borrado_invalida_el_cierre(self):
        for kind in ('modificado','nuevo','borrado'):
            with self.subTest(kind=kind):
                self.verde()
                p=self.root/('nuevo.py' if kind=='nuevo' else 'producto.py')
                old=p.read_bytes() if p.exists() else None
                if kind=='borrado': p.unlink()
                else: p.write_text('valor = 2\n')
                with patch('builtins.input', side_effect=AssertionError('no debe pedir cierre')):
                    with self.assertRaises(f.FactoryError): f.cerrar(ID)
                if old is None: p.unlink()
                else: p.write_bytes(old)

    def test_cambio_de_head_invalida_aunque_los_archivos_sean_iguales(self):
        self.verde()
        self.git('-c','user.name=Prueba','-c','user.email=prueba@example.invalid','commit','--allow-empty','-qm','otro commit')
        self.assertTrue(any('desactualizado' in x for x in f.pendientes_actuales(self.folder,self.state())))

    def test_informes_y_hechos_se_verifican_al_cierre(self):
        self.verde()
        for p in (self.folder/'review.md', self.folder/'oracle-veredicto.txt', self.facts):
            with self.subTest(path=p.name):
                old=p.read_bytes(); p.write_text('alterado')
                with self.assertRaises(f.FactoryError): f.cerrar(ID)
                p.write_bytes(old)
                p.unlink()
                with self.assertRaises(f.FactoryError): f.cerrar(ID)
                p.write_bytes(old)

    def test_spec_y_propuesta_modificadas_bloquean_juicio_y_cierre(self):
        self.verde()
        for p in (self.spec,self.folder/'proposal.md'):
            with self.subTest(path=p.name):
                old=p.read_bytes(); p.write_text(p.read_text()+'Alcance nuevo\n')
                with self.assertRaises(f.FactoryError): f.cerrar(ID)
                with self.assertRaises(f.FactoryError): f.juzgar(ID,self.facts)
                p.write_bytes(old)

    def test_reaprobacion_borra_validaciones_anteriores(self):
        self.verde(); self.aprobar()
        s=self.state()
        self.assertEqual(s['requisitos'],[])
        self.assertIsNone(s['revision']); self.assertIsNone(s['oracle'])

    def test_revisar_cancelado_no_sobrescribe_informe_ni_estado(self):
        self.verde(); before=self.state(); old=(self.folder/'review.md').read_bytes()
        self.report.write_text('Otro informe')
        with patch('builtins.input',return_value='cancelar'):
            with self.assertRaises(f.FactoryError): f.revisar(ID,self.report,'otra','aprobar',0)
        self.assertEqual(self.state(), before)
        self.assertEqual((self.folder/'review.md').read_bytes(),old)

    def test_fallo_de_segundo_juicio_descarta_verde_previo(self):
        self.verde()
        with self.assertRaises(f.FactoryError): f.juzgar(ID,self.facts.with_name('ausente.json'))
        self.assertIsNone(self.state()['oracle'])

    def test_aprobacion_antigua_sin_documentos_no_es_vigente(self):
        s=self.state(); s['spec_aprobada']={'por':'humano'}; f.guardar(self.folder,s)
        with self.assertRaises(f.FactoryError): f.importar(ID)

    def test_cambios_durante_confirmacion_no_se_aceptan(self):
        old=self.state()
        def respuesta(_):
            self.spec.write_text(self.spec.read_text()+'cambio simultáneo\n')
            return f'APROBAR ESPECIFICACION {ID}'
        with patch('builtins.input',side_effect=respuesta):
            with self.assertRaises(f.FactoryError): f.aprobar_spec(ID)
        self.assertEqual(self.state(),old)

    def test_importacion_separa_versiones_de_una_promesa(self):
        domains=[]
        def execute(args):
            if args[0]=='oracle':
                domains.append(args[args.index('--dominio')+1])
                return subprocess.CompletedProcess(args,0,'+ demo.promesa   sin medir\n','')
            return self.exec_real(args)
        with patch.object(f,'ejecutar',side_effect=execute):
            f.importar(ID)
            self.spec.write_text(self.spec.read_text().replace('SHALL funcionar.','SHALL cambiar.'))
            self.aprobar(); f.importar(ID)
        self.assertNotEqual(*domains)

class ParserCobertura(unittest.TestCase):
    def test_exige_id_exacto_y_una_sola_fila_verde(self):
        self.assertTrue(f.requisitos_verdes('✓ a.b   medida\n',['a.b']))
        for output in ('✓ a.bc   medida\n','? a.b   sin juicio\n','✓ a.b   medida\n✗ a.b   falla\n','1 requisitos: a.b'):
            self.assertFalse(f.requisitos_verdes(output,['a.b']))
        self.assertFalse(f.requisitos_verdes('',[]))
