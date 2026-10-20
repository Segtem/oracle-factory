"""El checkout de un revisor no toca el repositorio: escenario ai1, con Clue real y un revisor de prueba que juega con git
en su checkout."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_vueltas as _vueltas  # noqa: E402

f = _vueltas.f

# Antes de dejar su informe, el revisor cambia user.name, crea una rama y hace un commit en su checkout (y vuelve al
# candidato, como pide el pedido).
TRAVIESO = r'''
import json, subprocess, sys
checkout, paquete, informe = sys.argv[1], sys.argv[2], sys.argv[3]
git = lambda *a: subprocess.run(["git", "-C", checkout, *a], check=True, capture_output=True)
inicio = subprocess.run(["git", "-C", checkout, "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
git("config", "user.name", "Persona [[cambios/inexistente]]")
git("checkout", "-q", "-b", "rama-del-revisor")
git("-c", "user.email=r@example.invalid", "commit", "-q", "--allow-empty", "-m", "un commit del revisor")
git("checkout", "-q", "--detach", inicio)  # vuelve al candidato: Clue valida el informe contra el checkout
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
        self.assertEqual((self.git('rev-parse', 'HEAD'), self.git('branch', '--list'), self.git('config', 'user.name')), antes)
        self.assertNotIn('rama-del-revisor', self.git('branch', '--all'))
        self.assertEqual(self.git('worktree', 'list').count('\n'), 0)  # ningún worktree nuevo
        [pedida] = [e for e in f.leer(self.ident)[1]['eventos'] if e['accion'] == 'revision_pedida']
        self.assertEqual(pedida['resultado'], 'ok')
        sha = f.candidato_vigente(self.ident)
        self.assertTrue((self.root / '.factory/cambios' / self.ident / 'candidatos' / sha / 'revision/travieso-1.json').is_file())
