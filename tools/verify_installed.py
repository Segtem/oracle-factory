"""Prueba el ejecutable instalado fuera del checkout, con confirmaciones fixture."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.terminal import en_terminal  # noqa: E402


def main():
    p=argparse.ArgumentParser();p.add_argument('--factory',required=True);p.add_argument('--python',required=True)
    args=p.parse_args()
    executable=str(Path(args.factory).resolve());python=str(Path(args.python).absolute())
    env={**os.environ,'PATH':os.pathsep.join(['/usr/bin','/bin']),'PYTHONDONTWRITEBYTECODE':'1','PYTHONUTF8':'1'}
    assert not shutil.which('oracle',path=env['PATH']) and not shutil.which('tasks',path=env['PATH'])
    with tempfile.TemporaryDirectory() as tmp:
        work=Path(tmp);root=work/'producto'
        def run(*cmd,answer=None,ok=True,cwd=work):
            # Con answer, una persona fixture escribe en su terminal.
            r=(en_terminal(cmd,cwd=cwd,env=env,entrada=answer) if answer is not None else
               subprocess.run(cmd,cwd=cwd,env=env,text=True,capture_output=True))
            if ok and r.returncode:raise AssertionError(r.stdout+r.stderr)
            if not ok:assert r.returncode,r.stdout+r.stderr
            return r
        def factory(*cmd,**kw):return run(executable,'--proyecto',str(root),*cmd,**kw)
        factory('init');factory('init')
        output=factory('nuevo','--con-ejemplo','notas','Prueba instalada').stdout
        ident=re.search(r'Cambio creado: (\S+)',output)[1]
        change=root/'openspec/changes'/ident
        assert 'espera_aprobacion_spec' in factory('listar').stdout
        factory('nuevo','--con-ejemplo','notas','No duplicar tarea',ok=False)
        factory('aprobar-spec',ident,answer='NO\n',ok=False)
        factory('aprobar-spec',ident,answer='1\n')
        factory('importar',ident)
        state=json.loads((root/'.factory/cambios'/ident/'factory.json').read_text())
        factory('medir',ident,'--listar')
        for rid in state['requisitos']:
            factory('medir',ident,'--requisito',rid,'--medida','notas.no_existe',ok=False,answer='')
            factory('medir',ident,'--requisito',rid,'--medida','notas.casos_ejecutados','--medida','notas.resultados','--quitar-sin-medir',answer='')
        run(python,'-m','unittest','discover','-s','examples/notas','-v',cwd=root)
        run(python,'examples/notas/sensor.py','--salida','.factory-demo/hechos.json',cwd=root)
        run('git','init','-q',cwd=root);run('git','add','.',cwd=root)
        run('git','-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-qm','base',cwd=root)
        (root/'.factory-demo/review.md').write_text('Fixture de instalación; no aprueba un cambio real.')
        factory('revision',ident,'--informe','.factory-demo/review.md','--revisor','fixture','--decision','aprobar','--hallazgos-abiertos','0',answer='1\n')
        factory('juzgar',ident,'--con','.factory-demo/hechos.json')
        factory('cerrar',ident,answer='1\n')
        assert 'ESTADO: CERRADA' in (root/'tareas'/ident/'TAREA.md').read_text()
        assert not (work/'tareas').exists()
    print('OK: wheel instalado, dependencias aisladas, inicio guiado, listado, medidas, importación, revisión, juicio y cierre fixture.')


if __name__=='__main__':main()
