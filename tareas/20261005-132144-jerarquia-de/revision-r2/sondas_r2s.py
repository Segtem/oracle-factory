"""Sondas de R2 sobre 1f3e60b (estructura). Correr desde el checkout:
PYTHONPATH=.:tests:<revision-r2> python -m unittest -v sondas_r2s"""
import contextlib, io, json, os, subprocess, sys, time
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, 'tests')
from test_estructura import Estructura as Base, f, estructura

RAROS = [None, 12, 3.5, True, [], ['a'], {}, {'a': 1}, '', '..', '../..', '/etc/passwd', 'a\nb', 'x' * 5000]


class SondasS(Base):
    def _escribir(self, ident, mutar):
        ruta = self.root / 'openspec/changes' / ident / 'factory.json'
        e = json.loads(ruta.read_text()); mutar(e)
        ruta.write_text(json.dumps(e, ensure_ascii=False, indent=2) + '\n')

    def test_s_01_donde_con_valores_raros(self):
        ident = self.cambio_juzgado()
        original = (self.root / 'openspec/changes' / ident / 'factory.json').read_text()
        campos = [('spec',), ('requisitos',), ('revision', 'informe'), ('revision', 'decisiones'), ('oracle', 'informe'), ('oracle', 'hechos'),
                  ('revision', 'contexto'), ('revision', 'contexto', 'head'), ('oracle', 'contexto', 'head'), ('revision',), ('oracle',)]
        fallos = []
        for campo in campos:
            for valor in RAROS:
                def mutar(e, campo=campo, valor=valor):
                    d = e
                    for k in campo[:-1]:
                        d = d[k]
                    d[campo[-1]] = valor
                self._escribir(ident, mutar)
                for candidato in (None, 'abc'):
                    try:
                        with contextlib.redirect_stdout(io.StringIO()):
                            f.comando_donde(ident, candidato)
                    except f.FactoryError:
                        pass
                    except Exception as e:
                        fallos.append((' > '.join(campo), repr(valor)[:25], candidato, type(e).__name__))
                (self.root / 'openspec/changes' / ident / 'factory.json').write_text(original)
        resumen = {}
        for c, v, cand, t in fallos:
            resumen.setdefault(f'{c} [{t}]', set()).add(v)
        print('\nR2S-donde fallos (campo [excepción] -> valores):', file=sys.stderr)
        for k, v in sorted(resumen.items()):
            print('  ', k, '->', sorted(v)[:6], file=sys.stderr)
        print('R2S-donde total de combinaciones con excepción:', len(fallos), file=sys.stderr)

    def test_s_02_huella_con_factory_raro(self):
        ident = self.cambio_medido()
        base = f.contexto_producto()['archivos_sha256']
        res = {}
        # 1) un archivo común llamado .factory (no carpeta)
        ar = self.root / '.factory'
        import shutil
        shutil.move(str(ar), str(self.root / '.factory-carpeta'))
        ar.write_text('config de otra herramienta\n'); a = f.contexto_producto()['archivos_sha256']
        ar.write_text('config distinta\n'); b = f.contexto_producto()['archivos_sha256']
        res['.factory archivo común: el cambio de contenido altera la huella'] = a != b
        ar.unlink(); shutil.move(str(self.root / '.factory-carpeta'), str(ar))
        # 2) código bajo .factory/ no cambia la huella
        hook = ar / 'hooks'; hook.mkdir(); (hook / 'x.py').write_text('print(1)\n'); c = f.contexto_producto()['archivos_sha256']
        (hook / 'x.py').write_text('print(2)\n'); d = f.contexto_producto()['archivos_sha256']
        res['código bajo .factory/hooks: cambia la huella'] = c != d
        # 3) .factory enlace simbólico a afuera, versionado
        shutil.rmtree(ar); externo = Path(self.tmp.name) / 'externo'; externo.mkdir(); (externo / 'a.txt').write_text('1')
        os.symlink(externo, ar); e1 = f.contexto_producto()['archivos_sha256']; (externo / 'a.txt').write_text('2'); e2 = f.contexto_producto()['archivos_sha256']
        res['.factory enlace a un directorio externo: cambia la huella'] = e1 != e2
        print('\nR2S-huella:', json.dumps(res, ensure_ascii=False, indent=1), file=sys.stderr)

    def test_s_03_doc_dice_que_la_huella_rechaza_local_sin_ignorar(self):
        ident = self.cambio_medido()
        ig = self.root / '.gitignore'
        ig.write_text(ig.read_text().replace('.factory/local/\n', ''))
        wt = self.root / '.factory/local/revisiones/abc1234'; wt.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(['git', 'worktree', 'add', '--detach', str(wt), 'HEAD'], cwd=self.root, check=True, capture_output=True)
        try:
            f.contexto_producto()
            print('\nR2S-doc: la huella NO rechaza .factory/local sin ignorar (la guía dice que sí)', file=sys.stderr)
        except f.FactoryError as e:
            print('\nR2S-doc: la huella rechaza:', e, file=sys.stderr)
            self.fail('la guía es cierta')

    def test_s_04_buscar(self):
        ident = f.nuevo('Nota', con_ejemplo='notas')
        cambio = self.root / 'openspec/changes' / ident
        # mayúsculas y tildes
        (cambio / 'proposal.md').write_text('Straße y ÁRBOL y İstanbul y regex.*+?[ ( \\d\n' + 'x' * 400 + ' fin-lejano\n')
        res = {}
        for aguja in ('STRASSE', 'strasse', 'árbol', 'ARBOL', 'istanbul', 'regex.*+?[ ( \\d', 'fin-lejano', ' '):
            try:
                _, total = estructura.buscar(self.root, aguja)
                res[aguja] = total
            except Exception as e:
                res[aguja] = type(e).__name__
        # la línea muestra el texto buscado si está después de la columna 160?
        lineas, _ = estructura.buscar(self.root, 'fin-lejano')
        res['la línea impresa contiene fin-lejano'] = any('fin-lejano' in l for l in lineas)
        # enlace a carpeta externa dentro de openspec/changes
        externo = Path(self.tmp.name) / 'externo'; externo.mkdir(); (externo / 'secreto.md').write_text('aguja-externa\n')
        os.symlink(externo, cambio / 'enlace')
        _, total = estructura.buscar(self.root, 'aguja-externa'); res['alcanza un directorio externo por enlace'] = total
        # binario y enorme
        (cambio / 'raro.md').write_bytes(b'\xff\xfe aguja-bin \x00\x01')
        (cambio / 'grande.md').write_text('aguja-grande\n' + 'a' * 1_500_000)
        _, t1 = estructura.buscar(self.root, 'aguja-bin'); _, t2 = estructura.buscar(self.root, 'aguja-grande')
        res['binario'] = t1; res['archivo >1MB (se omite sin avisar)'] = t2
        print('\nR2S-buscar:', json.dumps(res, ensure_ascii=False, indent=1), file=sys.stderr)

    def test_s_05_buscar_rendimiento(self):
        ident = f.nuevo('Nota', con_ejemplo='notas')
        base = self.root / 'tareas' / ident / 'evidencia-grande'
        base.mkdir()
        for i in range(30000):
            (base / f'n{i}.md').write_text('linea de relleno\n' * 20)
        t = time.time(); estructura.buscar(self.root, 'no-aparece'); dt = time.time() - t
        print(f'\nR2S-buscar rendimiento: 30000 archivos .md en tareas/ -> {dt:.1f}s', file=sys.stderr)

    def test_s_06_ruta_y_init(self):
        # repo sin commits
        ident = f.nuevo('Nota', con_ejemplo='notas')
        subprocess.run(['git', 'init', '-q', '-b', 'main'], cwd=self.root, check=True)
        antes = self.huellas()
        try:
            f.comando_ruta(ident, 'evidencia')
        except f.FactoryError as e:
            print('\nR2S-ruta sin commits:', e, file=sys.stderr)
        for raro in ('../../x', 'no-existe', '', 'x' * 300):
            try:
                f.comando_ruta(raro, 'evidencia')
            except f.FactoryError as e:
                pass
            except Exception as e:
                print('R2S-ruta id raro', repr(raro)[:20], type(e).__name__, e, file=sys.stderr)
        self.assertEqual(self.huellas(), antes)
        # init: .gitignore sin salto final
        (self.root / '.gitignore').write_text('mis/')
        f.inicializar(); f.inicializar()
        print('R2S-init .gitignore:', repr((self.root / '.gitignore').read_text()), file=sys.stderr)
