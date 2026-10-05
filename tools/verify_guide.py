"""Ejecuta los comandos del HTML desde un proyecto vacío, usando un wheel instalado.
Las confirmaciones e informe son fixtures dentro de /tmp; no aprueban software real.
"""
import argparse
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.terminal import en_terminal  # noqa: E402

class Blocks(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.section = None; self.pre = False; self.code = False; self.blocks = {}
        self.feed(html)
    def handle_starttag(self, tag, attrs):
        if tag == 'section': self.section = dict(attrs).get('id')
        if tag == 'pre': self.pre = True
        if tag == 'code' and self.pre:
            self.code = True; self.blocks.setdefault(self.section, []).append('')
    def handle_endtag(self, tag):
        if tag == 'code': self.code = False
        if tag == 'pre': self.pre = False
        if tag == 'section': self.section = None
    def handle_data(self, text):
        if self.code: self.blocks[self.section][-1] += text

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--factory', required=True, type=Path)
    p.add_argument('--evidencia', type=Path)
    args=p.parse_args()
    root=Path(__file__).resolve().parents[1]
    guide=Blocks((root/'site/desde-cero.html').read_text()).blocks
    executable=str(args.factory.absolute())
    bin_dir=str(args.factory.absolute().parent)
    evidence=[]; identifiers={'ID_DEL_CAMBIO':None,'ID_DEL_REQUISITO':None}
    with tempfile.TemporaryDirectory(prefix='factory-guia-') as tmp:
        cwd=Path(tmp)
        env={**os.environ,'PATH':bin_dir+os.pathsep+os.environ['PATH'],'PYTHONDONTWRITEBYTECODE':'1',
             'GIT_CONFIG_GLOBAL':os.devnull,'GIT_CONFIG_NOSYSTEM':'1','UV_CACHE_DIR':str(cwd/'uv-cache')}
        env.pop('PYTHONPATH',None)
        def commands(text):
            nonlocal cwd
            for line in text.strip().splitlines():
                for token,value in identifiers.items():
                    if token in line:
                        if value is None: raise AssertionError('No se recuperó ' + token)
                        line=line.replace(token,value)
                argv=shlex.split(line)
                if argv[0]=='mkdir': (cwd/argv[1]).mkdir(); continue
                if argv[0]=='cd': cwd=(cwd/argv[1]).resolve(); continue
                if argv[0]=='oracle-factory': argv[0]=executable
                stdin=None
                if len(argv)>1 and argv[1]=='medir':
                    stdin=''  # decisión de persona: terminal, sin frase
                if len(argv)>1 and argv[1] in ('aprobar-spec','revision','cerrar'):
                    action={'aprobar-spec':'APROBAR ESPECIFICACION','revision':'REGISTRAR REVISION','cerrar':'CERRAR'}[argv[1]]
                    stdin=f'{action} {identifiers["ID_DEL_CAMBIO"]}\n'
                result=(en_terminal(argv,cwd=cwd,env=env,entrada=stdin) if stdin is not None else
                        subprocess.run(argv,cwd=cwd,env=env,text=True,capture_output=True,timeout=90))
                evidence.append({'command':line,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
                if result.returncode: raise AssertionError(evidence[-1])
                if len(argv)>1 and argv[1]=='nuevo':
                    identifiers['ID_DEL_CAMBIO']=re.search(r'Cambio creado: (\S+)',result.stdout)[1]
                if len(argv)>1 and argv[1]=='importar':
                    ids=re.findall(r'(?m)^[+=]\s+(\S+)',result.stdout)
                    if len(ids)!=1: raise AssertionError('El ejemplo debe producir un requisito: '+result.stdout)
                    identifiers['ID_DEL_REQUISITO']=ids[0]
        commands(guide['descargar'][0])
        actual=(cwd/'.gitignore').read_text().splitlines()
        for entry in guide['descargar'][1].splitlines():
            if entry not in actual: raise AssertionError('Falta ignore: '+entry)
        commands(guide['descargar'][2])
        for block in guide['pedido']: commands(block)
        for block in guide['acuerdo']: commands(block)
        for block in guide['probar']: commands(block)
        fixture=guide['revisar'][0].replace('PENDIENTE','Fixture automatizado; no aprueba un proyecto real.')
        (cwd/'.factory-demo/review.md').write_text(fixture)
        for block in guide['revisar'][1:]: commands(block)
        for block in guide['cerrar']: commands(block)
        state=json.loads((cwd/'openspec/changes'/identifiers['ID_DEL_CAMBIO']/'factory.json').read_text())
        if state['fase']!='cerrada': raise AssertionError(state['fase'])
    report={'resultado':'OK','plataforma':'Linux','confirmaciones':'fixtures, sin aprobación de producto real', 'identificadores':identifiers,'comandos':evidence}
    if args.evidencia: args.evidencia.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(f'OK: {len(evidence)} comandos extraídos del HTML, wheel instalado y cierre de fixture desde carpeta vacía.')

if __name__=='__main__':main()
