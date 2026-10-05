"""Contratos G1–G8 con Git real; confirmaciones sólo fixture en repos temporales."""
import contextlib
import copy
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from oracle_factory import cli as f

SOURCE = Path(__file__).resolve().parents[1]
ID = '20260101-120000-revision'


class RevisionGuiada(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.trace = []
        self.stdout = io.StringIO()
        quiet = contextlib.redirect_stdout(self.stdout)
        quiet.__enter__()
        self.addCleanup(quiet.__exit__, None, None, None)
        for name, value in [('ROOT', self.root), ('CHANGES', self.root / 'openspec/changes')]:
            p = patch.object(f, name, value); p.start(); self.addCleanup(p.stop)
        p = patch.object(f, 'nota_tarea'); self.note = p.start(); self.addCleanup(p.stop)
        self.folder = self.root / 'openspec/changes' / ID
        self.spec = self.folder / 'specs/demo/spec.md'
        self.spec.parent.mkdir(parents=True)
        self.spec.write_text('### Requirement: promesa\nThe system SHALL cumplir.\n#### Scenario: caso\n- THEN cumple\n')
        (self.folder / 'proposal.md').write_text('Contrato fixture.\n')
        (self.folder / 'tasks.md').write_text('- [ ] Implementar\n')
        task = self.root / 'tareas' / ID
        task.mkdir(parents=True)
        (task / 'TAREA.md').write_text('# Fixture\n\n- ESTADO: ABIERTA\n- PRIORIDAD: 50\n- ETIQUETAS:\n')
        (self.root / 'producto.py').write_text('valor = 1\n')
        f.guardar(self.folder, dict(id=ID, titulo='Fixture', spec=str(self.spec.relative_to(self.root)),
                                  fase='espera_aprobacion_spec', requisitos=[], revision=None, oracle=None, eventos=[]))
        self.git('init', '-q', '-b', 'main')
        self.git('add', '.')
        self.git('commit', '-qm', 'base fixture')
        with patch('builtins.input', return_value=f'APROBAR ESPECIFICACION {ID}'):
            f.aprobar_spec(ID)

    def git(self, *args):
        argv = ['git', '-c', 'core.hooksPath=/dev/null', '-c', 'user.name=Fixture',
                '-c', 'user.email=fixture@example.invalid', *args]
        env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
        env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1')
        p = subprocess.run(argv, cwd=self.root, env=env, capture_output=True, text=True, check=True)
        self.trace.append({'argv': argv, 'codigo': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr})
        return p

    def state(self):
        return f.leer(ID)[1]

    def preparar(self):
        self.report, self.decisions = f.preparar_revision(ID)
        self.data = json.loads(self.report.read_text())
        self.data.update(revisor='Revisor fixture', completa=True, archivos_revisados=['producto.py'],
                         comprobaciones=[{'descripcion': 'Inspección fixture', 'resultado': 'cumple', 'evidencia': 'valor = 1'}],
                         limites=['Sólo fixture; no análisis humano real'], hallazgos=[],
                         sin_hallazgos_motivo='Caso sin defectos sembrados para comprobar registro.')
        self.triage = dict(schema_version='oracle-factory.decisiones-revision/v1', informe_sha256=None,
                           actor='Persona fixture', motivo='Ensayo de registro, sin aprobación real.', decisiones=[])
        self.escribir()

    def escribir(self):
        self.report.write_bytes(f.bytes_json(self.data))
        self.triage['informe_sha256'] = f.sha256(self.report.read_bytes())
        self.decisions.write_bytes(f.bytes_json(self.triage))

    def registrar(self, decision='aprobar'):
        f.revisar(ID, self.report, 'Revisor fixture', decision, formato='guiado', decisiones=self.decisions)

    def aprobado(self):
        with patch('builtins.input', return_value=f'REGISTRAR REVISION {ID}'):
            self.registrar()

    def hallazgo(self, fid):
        return dict(id=fid, descripcion='Defecto fixture ' + fid, ubicacion='producto.py:1', evidencia='Caso sembrado')

    def resolucion(self, fid, estado='corregido'):
        return dict(hallazgo_id=fid, estado=estado, motivo='Decisión fixture motivada', actor='Persona fixture', fecha='2026-01-01T12:00:00Z')

    def test_g1_preparar_repetido_deja_pendientes_y_conserva_gates(self):
        before = self.state()
        context = f.contexto_producto()
        first = f.preparar_revision(ID)
        saved = [p.read_bytes() for p in first]
        second = f.preparar_revision(ID)
        self.assertNotEqual(first[0].parent, second[0].parent)
        self.assertEqual(saved, [p.read_bytes() for p in first])
        report, decisions = [json.loads(data) for data in saved]
        self.assertIsNone(report['hallazgos']); self.assertIsNone(report['completa'])
        self.assertIsNone(decisions['decisiones']); self.assertIsNone(decisions['informe_sha256'])
        self.assertEqual(self.state(), before)
        self.assertEqual(f.contexto_producto(), context)

    def test_g1_error_parcial_y_enlace_no_modifican_gates(self):
        before = self.state()
        original = Path.open
        def fail(path, *args, **kw):
            if path.name == 'decisiones.json' and args and args[0] == 'xb':
                raise OSError('falla de disco fixture')
            return original(path, *args, **kw)
        with patch.object(Path, 'open', fail), self.assertRaisesRegex(f.FactoryError, 'residuales'):
            f.preparar_revision(ID)
        self.assertEqual(self.state(), before)
        self.assertEqual(len(list((self.root/'tareas'/ID/'revisiones').glob('preparacion-*/informe.json'))), 1)
        # Probar rechazo de un destino enlazado en otro cambio temporal.
        link_id = '20260101-120001-enlace'
        (self.root / 'tareas' / link_id).symlink_to(self.root / 'tareas' / ID, target_is_directory=True)
        with self.assertRaisesRegex(f.FactoryError, 'enlaces'):
            f.guardar_par_revision(link_id, 'preparacion', b'{}', b'{}')

    def test_g1_sin_aceptacion_o_cambio_cerrado_no_prepara(self):
        old = self.state()
        for change in [dict(spec_aprobada=None), dict(fase='cerrada')]:
            state = copy.deepcopy(old); state.update(change); f.guardar(self.folder, state)
            with self.assertRaises(f.FactoryError): f.preparar_revision(ID)
        self.assertFalse((self.root / 'tareas' / ID / 'revisiones').exists())

    def test_g1_cambio_durante_preparacion_identifica_salida_obsoleta(self):
        before = self.state(); original = f.guardar_par_revision
        def changed(*args):
            result = original(*args)
            (self.root/'producto.py').write_text('valor = 2\n')
            return result
        with patch.object(f,'guardar_par_revision',side_effect=changed):
            with self.assertRaisesRegex(f.FactoryError,'no uses la preparación'): f.preparar_revision(ID)
        self.assertEqual(self.state(),before)

    def test_g2_plantilla_y_entradas_invalidas_no_piden_confirmacion(self):
        self.report, self.decisions = f.preparar_revision(ID)
        before = self.state()
        with patch('builtins.input', side_effect=AssertionError('no pedir confirmación')):
            with self.assertRaisesRegex(f.FactoryError, 'pendiente'): self.registrar()
        self.preparar()
        raw = self.report.read_bytes()
        malformed = [b'{', b'[]', b'\xff', raw.replace(b'"completa": true', b'"completa": NaN'),
                     raw.replace(b'"completa": true', b'"completa": true, "completa": false')]
        for data in malformed:
            with self.subTest(data=data[:30]):
                self.report.write_bytes(data)
                with patch('builtins.input', side_effect=AssertionError('no confirmar')):
                    with self.assertRaises(f.FactoryError): self.registrar()
                self.assertEqual(self.state(), before)

    def test_g2_schema_contexto_campos_y_rutas_se_validan(self):
        self.preparar(); original = copy.deepcopy(self.data); before = self.state()
        mutations = [dict(schema_version='otro/v2'), dict(cambio='otra-tarea'), dict(contexto={}), dict(documentos={}),
                     dict(revisor='Pendiente'), dict(completa=1), dict(desconocido=True), dict(limites=None),
                     dict(archivos_revisados=[]), dict(archivos_revisados=['../secreto']), dict(archivos_revisados=['/tmp/a']),
                     dict(archivos_revisados=['C:\\a']), dict(archivos_revisados=['a', 'a']), dict(archivos_revisados=['./a']),
                     dict(comprobaciones=[{'descripcion':'x','resultado':'desconocido','evidencia':'x'}]),
                     dict(comprobaciones=[{'descripcion':'x','resultado':'cumple','evidencia':'PENDIENTE'}])]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                self.data = {**original, **mutation}; self.escribir()
                with patch('builtins.input', side_effect=AssertionError('no confirmar')):
                    with self.assertRaises(f.FactoryError): self.registrar()
                self.assertEqual(self.state(), before)

    def test_g3_sin_hallazgos_exige_motivo_y_confirmacion(self):
        self.preparar(); self.data['sin_hallazgos_motivo'] = None; self.escribir()
        with self.assertRaisesRegex(f.FactoryError, 'sin_hallazgos_motivo'): self.registrar()
        self.data['sin_hallazgos_motivo'] = 'Casos inspeccionados sin hallazgos fixture'; self.escribir()
        with patch('builtins.input', return_value=''), self.assertRaisesRegex(f.FactoryError, 'cancelado'): self.registrar()
        self.assertIsNone(self.state()['revision'])
        self.aprobado()
        self.assertEqual(self.state()['revision']['hallazgos_abiertos'], 0)

    def test_g3_incompleta_falla_o_no_ejecutada_solo_permite_cambios(self):
        self.preparar(); original = copy.deepcopy(self.data)
        for kind in ('incompleta', 'falla', 'no_ejecutada'):
            with self.subTest(kind=kind):
                self.data = copy.deepcopy(original)
                if kind == 'incompleta': self.data['completa'] = False
                else: self.data['comprobaciones'][0]['resultado'] = kind
                self.escribir()
                with self.assertRaisesRegex(f.FactoryError, 'no se puede aprobar'): self.registrar()
                with patch('builtins.input', return_value=f'REGISTRAR REVISION {ID}'):
                    self.registrar('cambios')
                self.assertEqual(self.state()['fase'], 'cambios_pedidos')

    def test_g4_resoluciones_derivan_abiertos_y_muestran_motivos(self):
        self.preparar()
        self.data.update(hallazgos=[self.hallazgo('H1'), self.hallazgo('H2')], sin_hallazgos_motivo=None)
        self.triage['decisiones'] = [self.resolucion('H1')]; self.escribir()
        with self.assertRaisesRegex(f.FactoryError, 'hallazgos abiertos'): self.registrar()
        with patch('builtins.input', return_value=f'REGISTRAR REVISION {ID}'): self.registrar('cambios')
        self.assertEqual(self.state()['revision']['hallazgos_abiertos'], 1)
        self.triage['decisiones'].append(self.resolucion('H2', 'riesgo_aceptado')); self.escribir()
        def confirm(_):
            output = self.stdout.getvalue()
            for expected in ('riesgo_aceptado', 'H2', 'Persona fixture', 'Decisión fixture motivada', 'Abiertos derivados: 0'):
                self.assertIn(expected, output)
            return f'REGISTRAR REVISION {ID}'
        with patch('builtins.input', side_effect=confirm): self.registrar()
        self.assertEqual(self.state()['revision']['hallazgos_abiertos'], 0)

    def test_g4_hash_ids_y_decisiones_invalidas_se_rechazan(self):
        self.preparar(); self.data.update(hallazgos=[self.hallazgo('H1')], sin_hallazgos_motivo=None)
        original = copy.deepcopy(self.triage)
        mutations = [dict(informe_sha256='0'*64), dict(actor='PENDIENTE'), dict(motivo=''), dict(decisiones=None),
                     dict(decisiones=[self.resolucion('ajeno')]), dict(decisiones=[self.resolucion('H1')]*2),
                     dict(decisiones=[{**self.resolucion('H1'), 'estado':'pendiente'}]),
                     dict(decisiones=[{**self.resolucion('H1'), 'fecha':'2026-02-30T12:00:00Z'}]),
                     dict(decisiones=[{**self.resolucion('H1'), 'fecha':'2026-01-01'}]),
                     dict(decisiones=[{**self.resolucion('H1'), 'motivo':''}]),
                     dict(decisiones=[{**self.resolucion('H1'), 'actor':None}])]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                self.triage = copy.deepcopy(original); self.escribir()
                self.triage.update(mutation); self.decisions.write_bytes(f.bytes_json(self.triage))
                with self.assertRaises(f.FactoryError): self.registrar()
        self.triage = original
        self.data['hallazgos'] *= 2; self.escribir()
        with self.assertRaisesRegex(f.FactoryError, 'duplicado'): self.registrar()
        self.assertIsNone(self.state()['revision'])

    def test_g5_edicion_durante_confirmacion_preserva_revision(self):
        self.preparar(); self.aprobado(); old = self.state()
        report, decisions = self.report.read_bytes(), self.decisions.read_bytes()
        product, spec = (self.root/'producto.py').read_bytes(), self.spec.read_bytes()
        for target in (self.report, self.decisions, self.root/'producto.py', self.spec):
            with self.subTest(target=str(target)):
                def edit(_):
                    target.write_bytes(target.read_bytes() + b'\nmodificado\n')
                    return f'REGISTRAR REVISION {ID}'
                with patch('builtins.input', side_effect=edit), self.assertRaises(f.FactoryError): self.registrar()
                self.assertEqual(self.state(), old)
                self.report.write_bytes(report); self.decisions.write_bytes(decisions)
                (self.root/'producto.py').write_bytes(product); self.spec.write_bytes(spec)
        def concurrent(_):
            state = self.state(); state['eventos'].append({'accion':'otra persona'}); f.guardar(self.folder,state)
            return f'REGISTRAR REVISION {ID}'
        with patch('builtins.input', side_effect=concurrent), self.assertRaisesRegex(f.FactoryError, 'registro cambió'):
            self.registrar()
        self.assertEqual(self.state()['revision'], old['revision'])
        self.assertEqual(self.state()['eventos'][-1]['accion'], 'otra persona')

    def test_g5_cancelar_preserva_y_nueva_revision_invalida_juicio(self):
        self.preparar(); self.aprobado(); old = self.state()
        old['oracle'] = {'fixture':True}; f.guardar(self.folder,old)
        with patch('builtins.input', return_value=''), self.assertRaisesRegex(f.FactoryError, 'cancelado'): self.registrar()
        self.assertEqual(self.state(), old)
        self.aprobado()
        self.assertIsNone(self.state()['oracle'])
        self.assertNotEqual(self.state()['revision']['informe'], old['revision']['informe'])
        self.assertTrue((self.root/old['revision']['informe']).is_file())

    def test_g5_cambio_entre_lectura_y_snapshot_no_se_sobrescribe(self):
        self.preparar(); original = f.abierto
        def changed(ident):
            folder,state = original(ident)
            concurrent = copy.deepcopy(state);concurrent['eventos'].append({'accion':'edición concurrente'})
            f.guardar(folder,concurrent)
            return folder,state
        with patch.object(f,'abierto',side_effect=changed):
            with self.assertRaisesRegex(f.FactoryError,'registro cambió durante la lectura'): self.registrar()
        self.assertEqual(self.state()['eventos'][-1]['accion'],'edición concurrente')
        self.assertIsNone(self.state()['revision'])

    def test_g6_archivos_archivados_y_contexto_se_verifican(self):
        self.preparar(); self.aprobado(); state = self.state()
        for field in ('informe', 'decisiones'):
            path = self.root / state['revision'][field]; original = path.read_bytes()
            for action in ('alterar', 'borrar'):
                with self.subTest(field=field,action=action):
                    if action == 'alterar': path.write_bytes(b'alterado')
                    else: path.unlink()
                    reasons = f.pendientes_actuales(self.folder,self.state())
                    self.assertTrue(any(field in reason for reason in reasons), reasons)
                    with self.assertRaises(f.FactoryError): f.cerrar(ID)
                    path.write_bytes(original)
        self.report.write_text('original cambiado después de archivar')
        self.assertFalse(any('informe de revisión' in reason for reason in f.pendientes_actuales(self.folder,self.state())))
        self.git('commit','--allow-empty','-qm','nuevo candidato')
        self.assertTrue(any('desactualizado' in reason for reason in f.pendientes_actuales(self.folder,self.state())))

    def test_g6_fallas_de_archivo_y_estado_conservan_anterior(self):
        self.preparar(); self.aprobado(); old = self.state()
        original = Path.open
        def fail(path, *args, **kw):
            if path.name == 'decisiones.json' and path.parent.name.startswith('registro-') and args and args[0] == 'xb':
                raise OSError('disco lleno fixture')
            return original(path, *args, **kw)
        with patch.object(Path,'open',fail), patch('builtins.input',return_value=f'REGISTRAR REVISION {ID}'):
            with self.assertRaisesRegex(f.FactoryError,'residuales'): self.registrar()
        self.assertEqual(self.state(),old)
        with patch.object(f.os,'replace',side_effect=OSError('reemplazo fallido')), patch('builtins.input',return_value=f'REGISTRAR REVISION {ID}'):
            with self.assertRaisesRegex(f.FactoryError,'no se publicó'): self.registrar()
        self.assertEqual(self.state(),old)

    def test_g6_nota_fallida_no_finge_revertir_registro(self):
        self.preparar(); self.note.side_effect = f.FactoryError('tracker no disponible')
        with patch('builtins.input',return_value=f'REGISTRAR REVISION {ID}'):
            with self.assertRaisesRegex(f.FactoryError,'quedó registrada.*nota del tracker pendiente'): self.registrar()
        self.assertEqual(self.state()['fase'],'revision_aprobada')
        self.assertTrue((self.root/self.state()['revision']['decisiones']).is_file())

    def test_g7_libre_compatible_historico_y_opciones_explicitas(self):
        report = self.root/'tareas'/ID/'libre.md'; report.write_text('Revisión libre fixture')
        with self.assertRaisesRegex(f.FactoryError,'explícito'): f.revisar(ID,report,'Persona','aprobar')
        with patch('builtins.input',return_value=f'REGISTRAR REVISION {ID}'):
            f.revisar(ID,report,'Persona','aprobar',0)
        self.assertEqual(self.state()['revision']['formato'],'libre')
        state=self.state();del state['revision']['formato'];f.guardar(self.folder,state)
        f.mostrar(ID);self.assertIn('libre histórico',self.stdout.getvalue())
        self.preparar()
        for kw in [dict(formato='guiado',abiertos=0,decisiones=self.decisions), dict(formato='libre',abiertos=0,decisiones=self.decisions),
                   dict(formato='otro',abiertos=0),dict(formato='guiado')]:
            with self.subTest(kw=kw),self.assertRaises(f.FactoryError):
                f.revisar(ID,self.report,'Revisor fixture','aprobar',**kw)

    def test_g8_guia_documenta_el_recorrido(self):
        # La spec pide documentar preparación, completado, decisión y renovación; la prueba de CLI no lee la guía.
        guia = (SOURCE / 'docs/revision-guiada.md').read_text(encoding='utf-8')
        marcas = ('## Preparar el entorno y el candidato', 'revision-preparar',
                  '## Completar lo que realmente se revisó', '## Registrar decisiones humanas',
                  '## Registrar el resultado con confirmación', '--formato guiado',
                  '## Recuperación y revisión libre')
        self.assertEqual([m for m in marcas if m not in guia], [])

    def test_g8_cli_completo_y_oracle_real_en_fixture(self):
        root=self.root/'cli';root.mkdir()
        def run(*args, stdin=None, expected=0):
            p=subprocess.run([str(a) for a in args],cwd=root,input=stdin,text=True,capture_output=True,timeout=90,
                             env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
            self.trace.append({'argv':[str(a) for a in args],'stdin_fixture':stdin,'codigo':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
            self.assertEqual(p.returncode,expected,p.stdout+p.stderr)
            return p
        def cli(*args,**kw):return run(sys.executable,SOURCE/'fabrica.py','--proyecto',root,*args,**kw)
        cli('init')
        run('git','init','-q','-b','main')
        out=cli('nuevo','--con-ejemplo','notas','Fixture revisión guiada')
        ident=re.search(r'Cambio creado: (\S+)',out.stdout)[1]
        cli('aprobar-spec',ident,stdin=f'APROBAR ESPECIFICACION {ident}\n')
        cli('importar',ident)
        state_path=root/'openspec/changes'/ident/'factory.json'
        rid=json.loads(state_path.read_text())['requisitos'][0]
        cli('medir',ident,'--requisito',rid,'--medida','notas.casos_ejecutados','--medida','notas.resultados','--quitar-sin-medir')
        run('git','add','.')
        run('git','-c','core.hooksPath=/dev/null','-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-qm','producto fixture')
        facts=root/'tareas'/ident/'hechos.json'
        run(sys.executable,'examples/notas/sensor.py','--salida',facts)
        out=cli('revision-preparar',ident)
        report=Path(re.search(r'Informe pendiente: (.+)',out.stdout)[1])
        decisions=Path(re.search(r'Decisiones pendientes: (.+)',out.stdout)[1])
        data=json.loads(report.read_text())
        data.update(revisor='Persona fixture',completa=True,archivos_revisados=['examples/notas/notas.py'],
                    comprobaciones=[dict(descripcion='Tres casos del sensor',resultado='cumple',evidencia=f'hechos.json sha256 {f.sha256(facts.read_bytes())}')],
                    limites=['Simulación temporal, no revisión humana'],hallazgos=[],sin_hallazgos_motivo='Sin defectos sembrados en este fixture')
        report.write_bytes(f.bytes_json(data))
        triage=json.loads(decisions.read_text());triage.update(informe_sha256=f.sha256(report.read_bytes()),actor='Persona fixture',motivo='Ensayo de CLI',decisiones=[])
        decisions.write_bytes(f.bytes_json(triage))
        cli('revision',ident,'--informe',report,'--revisor','Persona fixture','--decision','aprobar',expected=1)
        cli('revision',ident,'--formato','desconocido','--informe',report,'--revisor','Persona fixture','--decision','aprobar',expected=2)
        cli('revision',ident,'--formato','guiado','--informe',report,'--decisiones',decisions,'--revisor','Persona fixture','--decision','aprobar',stdin=f'REGISTRAR REVISION {ident}\n')
        cli('juzgar',ident,'--con',facts)
        self.assertIn('Pendiente: ninguno',cli('estado',ident).stdout)
        cli('cerrar',ident,stdin=f'CERRAR {ident}\n')
        self.assertEqual(json.loads(state_path.read_text())['fase'],'cerrada')


if __name__ == '__main__':
    unittest.main()
