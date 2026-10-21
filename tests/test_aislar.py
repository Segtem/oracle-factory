"""El checkout de un revisor no toca el repositorio: escenario ai1, con Clue real y un revisor de prueba que juega con git
en su checkout."""
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_vueltas as _vueltas  # noqa: E402

f = _vueltas.f

# Antes de dejar su informe, el revisor cambia user.name, crea una rama, hace un commit y deja un archivo suelto en su
# checkout, sin volver al candidato.
TRAVIESO = r'''
import json, subprocess, sys
checkout, paquete, informe = sys.argv[1], sys.argv[2], sys.argv[3]
git = lambda *a: subprocess.run(["git", "-C", checkout, *a], check=True, capture_output=True)
git("config", "user.name", "Persona [[cambios/inexistente]]")
git("checkout", "-q", "-b", "rama-del-revisor")
git("-c", "user.email=r@example.invalid", "commit", "-q", "--allow-empty", "-m", "un commit del revisor")
open(checkout + "/un-archivo-suelto.txt", "w").write("del revisor\n")  # y deja algo suelto
p = json.load(open(paquete))
json.dump({"schema_version": "oracle-clue.review/v1", "repo": p["repo"], "base": p["base"], "head": p["head"],
           "diff_sha256": p["diff_sha256"], "context_sha256": p["context_sha256"],
           "provider": {"name": "revisor de prueba", "model": "fixture"}, "findings": [],
           "review_status": "completo", "limitations": ["Revisor de prueba."]}, open(informe, "w"))
'''


class Aislar(_vueltas.Base):
    preparar, candidato_nuevo = _vueltas.Vueltas.preparar, _vueltas.Vueltas.candidato_nuevo

    # --- ai1: el checkout de un revisor no toca el repositorio ------------------------------------------------------
    def test_ai1_un_revisor_que_juega_con_git_en_su_checkout(self):
        self.preparar()
        self.git('config', 'user.name', 'Persona del proyecto')
        travieso = self.script.with_name('travieso.py')
        travieso.write_text(TRAVIESO)
        config = json.loads((self.root / '.factory/config.json').read_text())
        config['revisores'] = {'travieso': {'comando': [sys.executable, str(travieso), '{checkout}', '{paquete}', '{informe}'],
                                            'proveedor': 'revisor de prueba', 'modelo': 'fixture', 'tope_minutos': 1}}
        (self.root / '.factory/config.json').write_text(json.dumps(config))
        self.git('add', '.')
        self.git('commit', '-qm', 'el revisor')
        antes = (self.git('rev-parse', 'HEAD'), self.git('branch', '--list'), self.git('config', 'user.name'))
        f.pedir_revision(self.ident, 'travieso', base=self.base)
        # Un segundo pedido (otro revisor, o el mismo otra vez) tiene su propio checkout: no ve lo que dejó el primero.
        f.pedir_revision(self.ident, 'travieso', base=self.base)
        self.assertEqual((self.git('rev-parse', 'HEAD'), self.git('branch', '--list'), self.git('config', 'user.name')), antes)
        self.assertNotIn('rama-del-revisor', self.git('branch', '--all'))
        self.assertEqual(self.git('worktree', 'list').count('\n'), 0)  # ningún worktree nuevo
        pedidas = [e for e in f.leer(self.ident)[1]['eventos'] if e['accion'] == 'revision_pedida']
        self.assertEqual([e['resultado'] for e in pedidas], ['ok', 'ok'])
        sha = f.candidato_vigente(self.ident)
        for n in (1, 2):
            self.assertTrue((self.root / '.factory/cambios' / self.ident / 'candidatos' / sha / f'revision/travieso-{n}.json').is_file())
        checkouts = sorted(p.name for p in (self.root / '.factory/local/revisiones').iterdir())
        self.assertEqual(checkouts, [f'{sha}-travieso-1', f'{sha}-travieso-2'])
        # El clon no tiene remoto: un push desde ahí no llega al repositorio.
        self.assertEqual(subprocess.run(['git', '-C', str(self.root / '.factory/local/revisiones' / f'{sha}-travieso-1'), 'remote'],
                                        capture_output=True, text=True).stdout, '')
        # Un pedido que falla antes de su paquete (Clue no lo prepara) deja su clon; el reintento no choca con él.
        ejecutar = f.ejecutar

        def clue_falla(args):
            if args[:2] == ['oracle-clue', 'preparar']:
                return subprocess.CompletedProcess(args, 1, '', 'Clue no pudo')
            return ejecutar(args)
        with patch.object(f, 'ejecutar', side_effect=clue_falla), self.assertRaises(f.FactoryError):
            f.pedir_revision(self.ident, 'travieso', base=self.base)
        self.assertTrue((self.root / '.factory/local/revisiones' / f'{sha}-travieso-3').is_dir())  # el clon que quedó
        # Otro revisor con un nombre que empieza igual no corre la numeración de éste, y un hueco tampoco la repite.
        (self.root / '.factory/cambios' / self.ident / 'candidatos' / sha / 'clue' / 'paquete-travieso-largo-9.json').write_text('{}')
        (self.root / '.factory/local/revisiones' / f'{sha}-travieso-7').mkdir()
        # El clon no depende de los objetos del repositorio (no hay alternates): un gc no lo deja sin el candidato.
        self.assertFalse((self.root / '.factory/local/revisiones' / f'{sha}-travieso-1/.git/objects/info/alternates').exists())
        f.pedir_revision(self.ident, 'travieso', base=self.base)
        self.assertTrue((self.root / '.factory/cambios' / self.ident / 'candidatos' / sha / 'revision/travieso-8.json').is_file())
        # En un clon nuevo del proyecto no están los paquetes ni los checkouts (son locales): el número sale también de los
        # informes y pedidos versionados, y un pedido nuevo no pisa ninguno.
        import shutil
        shutil.rmtree(self.root / '.factory/cambios' / self.ident / 'candidatos' / sha / 'clue')
        shutil.rmtree(self.root / '.factory/local/revisiones')
        f.pedir_revision(self.ident, 'travieso', base=self.base)
        self.assertTrue((self.root / '.factory/cambios' / self.ident / 'candidatos' / sha / 'revision/travieso-9.json').is_file())
        # --base con el nombre de una rama: el clon no tiene la rama, pero la base va como SHA.
        self.git('branch', 'base-con-nombre', self.base)
        f.pedir_revision(self.ident, 'travieso', base='base-con-nombre')
        self.assertTrue((self.root / '.factory/cambios' / self.ident / 'candidatos' / sha / 'revision/travieso-10.json').is_file())
