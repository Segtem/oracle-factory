"""Reproduce el ejemplo de la guía en un checkout temporal; usa herramientas reales."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import fabrica as f

SOURCE=Path(__file__).resolve().parents[1]

@unittest.skipUnless(shutil.which('oracle') and shutil.which('tasks'), 'requiere Oracle y Oracle Task')
class GuiaDesdeCero(unittest.TestCase):
    def test_ejemplo_de_la_guia_hasta_el_cierre(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            shutil.copytree(SOURCE/'examples',root/'examples')
            (root/'.gitignore').write_text('.factory-demo/\n__pycache__/\n')
            def run(*args,check=True):
                return subprocess.run(args,cwd=root,capture_output=True,text=True,check=check)
            run('tasks','init',str(root),'--sin-readme');run('oracle','init',str(root))
            (root/'oracle.json').write_text(json.dumps({'esquema':'oracle.proyecto/v1','catalogo_base':False,'perfiles':[]}))
            with patch.object(f,'ROOT',root),patch.object(f,'CHANGES',root/'openspec/changes'),contextlib.redirect_stdout(io.StringIO()):
                ident=f.nuevo('Ejemplo de guía','notas');folder,state=f.leer(ident)
                shutil.copyfile(root/'examples/notas/proposal.md',folder/'proposal.md')
                shutil.copyfile(root/'examples/notas/spec.md',root/state['spec'])
                with patch('builtins.input',return_value=f'APROBAR ESPECIFICACION {ident}'):f.aprobar_spec(ident)
                f.importar(ident)
                for file in (root/'examples/notas/catalogos').iterdir():shutil.copyfile(file,root/'catalogos'/file.name)
                rid=f.leer(ident)[1]['requisitos'][0];req=root/'requisitos'/f'{rid}.requisito'
                req.write_text('\n'.join('    medido_por notas.casos_ejecutados, notas.resultados' if line.strip().startswith('sin_medir ') else line for line in req.read_text().splitlines())+'\n')
                run(sys.executable,'-m','unittest','discover','-s','examples/notas','-p','test_*.py','-v')
                run('git','init','-q','-b','demo/notas');run('git','add','.')
                run('git','-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-qm','ejemplo')
                facts=root/'.factory-demo/hechos.json'
                # El sensor debe detectar una regresión real, no emitir siempre un verde.
                code=root/'examples/notas/notas.py';original=code.read_text();code.write_text(original.replace('titulo.strip()','titulo'))
                run(sys.executable,'examples/notas/sensor.py','--salida',str(facts))
                with self.assertRaises(f.FactoryError):f.juzgar(ident,facts)
                code.write_text(original)
                run(sys.executable,'examples/notas/sensor.py','--salida',str(facts))
                report=root/'.factory-demo/review.md';report.write_text('Informe fixture: se inspeccionaron los tres casos. No es aprobación de un producto real.')
                with patch('builtins.input',return_value=f'REGISTRAR REVISION {ident}'):f.revisar(ident,report,'fixture de guía','aprobar',0)
                f.juzgar(ident,facts)
                self.assertEqual(f.pendientes_actuales(folder,f.leer(ident)[1]),[])
                with patch('builtins.input',return_value=f'CERRAR {ident}'):f.cerrar(ident)
                self.assertIn('ESTADO: CERRADA',(root/'tareas'/ident/'TAREA.md').read_text())
