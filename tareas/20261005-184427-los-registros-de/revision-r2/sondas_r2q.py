"""Sondas de R2 sobre fd1bfe7: fuente_relativa con raíces raras."""
import contextlib, io, json, sys, re
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, 'tests')
from test_portabilidad import Portabilidad as Base, f


class SondasQ(Base):
    def test_q_01_raices_raras_con_oracle_real(self):
        resultados = {}
        for nombre in ('producto ñ #1', 'prod con "comillas"', 'prod\\barra', "prod 'simple'", 'prod\ttab', 'prod ü{llaves}%', 'prod \\"mixto'):
            tmp = Path(self.tmp.name) / 'raros' / nombre
            try:
                tmp.mkdir(parents=True)
            except OSError as e:
                resultados[nombre] = f'no se pudo crear: {e}'; continue
            avisos = io.StringIO()
            with patch.object(f, 'ROOT', tmp), patch.object(f, 'CHANGES', tmp / 'openspec/changes'), contextlib.redirect_stderr(avisos):
                try:
                    f.inicializar()
                    ident = f.nuevo('Nota', con_ejemplo='notas')
                    with self.escribe(f'APROBAR ESPECIFICACION {ident}'): f.aprobar_spec(ident)
                    f.importar(ident)
                    rid = f.leer(ident)[1]['requisitos'][0]
                    fuente = [l for l in (tmp / 'requisitos' / f'{rid}.requisito').read_text(encoding='utf-8').splitlines() if l.strip().startswith('fuente')][0]
                    resultados[nombre] = ('relativa' if fuente.strip().startswith('fuente "openspec/') else 'ABSOLUTA: ' + fuente[:90], 'avisos: ' + str(avisos.getvalue().count('no pude hacer relativa')))
                except Exception as e:
                    resultados[nombre] = f'excepción {type(e).__name__}: {str(e)[:100]}'
        print('\nR2Q-01', json.dumps(resultados, ensure_ascii=False, indent=1), file=sys.stderr)

    def test_q_02_prefijo_y_otras_lineas(self):
        raiz = Path('/tmp/a')
        r = Path(self.tmp.name) / 'x.requisito'
        r.write_text('requisito x.y:\n    texto "ver fuente \\"/tmp/a/x\\" y fuente \\"/tmp/a/y\\""\n    fuente "/tmp/ab/otro.md#t"\n'
                     '    fuente "/tmp/a/openspec/x.md#t"\n    fuente "https://ejemplo.org/x"\n    fuente "openspec/ya-relativa.md#t"\n', encoding='utf-8')
        avisos = io.StringIO()
        with patch.object(f, 'ROOT', raiz), contextlib.redirect_stderr(avisos):
            f.fuente_relativa(r)
        print('\nR2Q-02 resultado:\n' + r.read_text(), '\nR2Q-02 avisos:', avisos.getvalue().count('no pude'), file=sys.stderr)
        t = r.read_text()
        self.assertIn('fuente "/tmp/ab/otro.md#t"', t)          # no tocó el prefijo parecido
        self.assertIn('fuente \\"/tmp/a/x\\"', t)                # ni el texto citado
        self.assertIn('    fuente "openspec/x.md#t"', t)

    def test_q_03_aviso_legitimo_y_duplicados(self):
        raiz = Path('/tmp/proyecto')
        for contenido, esperado in (('requisito x:\n    fuente "openspec/x.md#t"\n', 0), ('requisito x:\n    fuente "https://x.org/a"\n', 0),
                                    ('requisito x:\n    fuente "/otro/x.md"\n', 1)):
            r = Path(self.tmp.name) / 'a.requisito'; r.write_text(contenido, encoding='utf-8')
            av = io.StringIO()
            with patch.object(f, 'ROOT', raiz), contextlib.redirect_stderr(av):
                f.fuente_relativa(r)
            print('\nR2Q-03', repr(contenido.splitlines()[1].strip()), '-> avisos', av.getvalue().count('no pude'), file=sys.stderr)
            self.assertEqual(av.getvalue().count('no pude'), esperado)
