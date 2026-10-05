"""Flujo con Oracle y Oracle Task instalados; aprobaciones simuladas sólo en /tmp."""
import contextlib
import io
import json
from pathlib import Path
import shutil
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

@unittest.skipUnless(shutil.which('oracle') and shutil.which('tasks'), 'requiere Oracle y Oracle Task instalados')
class IntegracionReal(unittest.TestCase):
    def test_importacion_juicio_y_cierre_con_herramientas_reales(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/'repo'; root.mkdir()
            def run(*args):
                return subprocess.run(args,cwd=root,capture_output=True,text=True,check=True)
            run('tasks','init',str(root),'--sin-readme')
            run('oracle','init',str(root))
            (root/'oracle.json').write_text(json.dumps({'esquema':'oracle.proyecto/v1','catalogo_base':False,'perfiles':[]}))
            with patch.object(f,'ROOT',root), patch.object(f,'CHANGES',root/'openspec/changes'), contextlib.redirect_stdout(io.StringIO()):
                ident=f.nuevo('Prueba temporal: corrida exitosa','demo')
                folder,state=f.leer(ident); spec=root/state['spec']
                (folder/'proposal.md').write_text('Rechazar corridas con errores.')
                spec.write_text('### Requirement: codigo cero\nThe system SHALL reject nonzero codes.\n#### Scenario: error\n- WHEN codigo es uno\n- THEN rechazar\n')
                with patch('builtins.input',return_value=f'APROBAR ESPECIFICACION {ident}'):
                    f.aprobar_spec(ident)
                f.importar(ident)
                rid=f.leer(ident)[1]['requisitos'][0]
                requisito=root/'requisitos'/f'{rid}.requisito'
                self.assertIn('sin_medir',requisito.read_text())
                requisito.write_text('\n'.join('    medido_por demo.medida' if x.strip().startswith('sin_medir ') else x for x in requisito.read_text().splitlines())+'\n')
                (root/'catalogos/demo.medida.oracle').write_text('ninguno demo.medida:\n    de corrida c\n    donde c.codigo != 0\n    umbral <= 0 segun contrato porque "cero"\n    ambito universal\n    alcance "prueba temporal"\n')
                run('git','init','-q','-b','main'); run('git','add','.')
                run('git','-c','user.name=Prueba','-c','user.email=prueba@example.invalid','commit','-qm','base revisada')
                report=Path(temp)/'revision.md'; report.write_text('Informe ficticio para probar el protocolo, sin hallazgos.')
                with patch('builtins.input',return_value=f'REGISTRAR REVISION {ident}'):
                    f.revisar(ident,report,'fixture de integración','aprobar',0)
                facts=Path(temp)/'hechos.json'; facts.write_text(json.dumps({'otra':[{'x':1}]}))
                with self.assertRaises(f.FactoryError): f.juzgar(ident,facts)
                verdict=f.leer(ident)[1]['oracle']
                self.assertEqual(verdict['codigo_oracle'],0)
                self.assertEqual(verdict['codigo'],1)
                config=root/'oracle.json'; original=config.read_text()
                data=json.loads(original); data['sombra']={'demo.medida':{'desde':'2026-09-30','porque':'prueba temporal','cota':5}}
                config.write_text(json.dumps(data)); facts.write_text(json.dumps({'corrida':[{'codigo':1}]}))
                with self.assertRaises(f.FactoryError): f.juzgar(ident,facts)
                self.assertEqual(f.leer(ident)[1]['oracle']['codigo_oracle'],0)
                config.write_text(original)
                facts.write_text(json.dumps({'corrida':[{'codigo':0}]}))
                f.juzgar(ident,facts)
                self.assertEqual(f.pendientes_actuales(folder,f.leer(ident)[1]),[])
                with patch('builtins.input',return_value=f'CERRAR {ident}'):
                    f.cerrar(ident)
                self.assertEqual(f.leer(ident)[1]['fase'],'cerrada')
                self.assertIn('ESTADO: CERRADA',(root/'tareas'/ident/'TAREA.md').read_text())
