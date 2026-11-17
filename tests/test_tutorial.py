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


def setUpModule():
    # Estas pruebas representan a una persona que escribe en su terminal.
    terminal = patch.object(f, 'terminal_interactiva', return_value=True)
    terminal.start()
    unittest.addModuleCleanup(terminal.stop)

SOURCE=Path(__file__).resolve().parents[1]

@unittest.skipUnless(shutil.which('oracle') and shutil.which('tasks'), 'requiere Oracle y Oracle Task')
class GuiaDesdeCero(unittest.TestCase):
    def test_ejemplo_de_la_guia_hasta_el_cierre(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            (root/'.gitignore').write_text('.factory/local/\n__pycache__/\n')
            def run(*args,check=True):
                return subprocess.run(args,cwd=root,capture_output=True,text=True,check=check)
            run('tasks','init',str(root),'--sin-readme');run('oracle','init',str(root))
            (root/'oracle.json').write_text(json.dumps({'esquema':'oracle.proyecto/v1','catalogo_base':False,'perfiles':[]}))
            (root/'.factory').mkdir();(root/'.factory/config.json').write_text('{}')  # lo que deja init: nuevo declara ahí el sensor
            with patch.object(f,'ROOT',root),patch.object(f,'CHANGES',root/'openspec/changes'),contextlib.redirect_stdout(io.StringIO()):
                ident=f.nuevo('Ejemplo de guía', con_ejemplo='notas');folder,state=f.leer(ident)
                with patch('builtins.input',return_value='1'):f.aprobar_spec(ident)
                f.importar(ident)
                rid=f.leer(ident)[1]['requisitos'][0]
                f.medir(ident, requisito_id=rid, medidas=['notas.casos_ejecutados','notas.resultados'], quitar_sin_medir=True)
                run(sys.executable,'-m','unittest','discover','-s','examples/notas','-p','test_*.py','-v')
                run('git','init','-q','-b','demo/notas');run('git','add','.')
                run('git','-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-qm','ejemplo')
                # El sensor debe detectar una regresión real, no emitir siempre un verde (corrido a mano, sólo para comprobarlo).
                regresion=root/'.factory/local/regresion.json'
                code=root/'examples/notas/notas.py';original=code.read_text();code.write_text(original.replace('titulo.strip()','titulo'))
                run(sys.executable,'examples/notas/sensor.py','--salida',str(regresion))
                with self.assertRaises(f.FactoryError):f.juzgar(ident,regresion)
                code.write_text(original)
                # Como en la guía: una persona aprueba el sensor que declaró el ejemplo y Factory produce los hechos del commit.
                with patch('builtins.input',return_value='1'):f.sensor_mod.aprobar()
                f.sensor_mod.producir(ident,[])
                facts=f.hechos_del_candidato(ident)
                report=root/'.factory/local/review.md';report.write_text('Informe fixture: se inspeccionaron los tres casos. No es aprobación de un producto real.')
                with patch('builtins.input',return_value='1'):f.revisar(ident,report,'fixture de guía','aprobar',0)
                f.juzgar(ident,facts)
                self.assertTrue(f.sensor_mod.hechos_de(ident,f.leer(ident)[1])['producidos_por_factory'])
                self.assertEqual(f.pendientes_actuales(folder,f.leer(ident)[1]),[])
                with patch('builtins.input',return_value='1'):f.cerrar(ident)
                self.assertIn('ESTADO: CERRADA',(root/'tareas'/ident/'TAREA.md').read_text())
