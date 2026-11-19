"""fa1: los abandonos de la base se conservan sólo mientras sigan intactos."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from oracle_factory import cli, firmas


ID = "20261119-124201-8d6-prueba"


class FirmasAbandonadas(unittest.TestCase):
    def setUp(self):
        temporal = tempfile.TemporaryDirectory()
        self.addCleanup(temporal.cleanup)
        self.raiz = Path(temporal.name)
        subprocess.run(["git", "init", "-q", str(self.raiz)], check=True)
        self.config = self.raiz / ".factory" / "config.json"
        self.registro = self.raiz / ".factory" / "cambios" / ID / "factory.json"
        self.registro.parent.mkdir(parents=True)
        for parche in (patch.object(cli, "ROOT", self.raiz), patch.object(cli, "PRODUCTO", None)):
            parche.start()
            self.addCleanup(parche.stop)

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.raiz), *args], check=True, capture_output=True, text=True).stdout.strip()

    def estado(self, fase="abandonada"):
        decision = {"actor": "Brian", "tipo_actor": "persona", "cuando": "2026-01-01T00:00:00Z"}
        return {"id": ID, "fase": fase, "abandono": decision.copy() if fase == "abandonada" else None,
                "cierre": decision.copy() if fase == "cerrada" else None}

    def base(self, estado):
        self.registro.write_text(json.dumps(estado), encoding="utf-8")
        self.git("add", ".")
        self.git("-c", "user.name=Prueba", "-c", "user.email=prueba@example.test", "commit", "-qm", "base")
        self.config.write_text(json.dumps({"firmas": "exigir", "firmas_base": self.git("rev-parse", "HEAD")}), encoding="utf-8")

    def test_fa1_un_abandono_historico_intacto_cuenta(self):
        estado = self.estado()
        self.base(estado)
        self.assertEqual(firmas.pendientes(estado), [])

    def test_fa1_un_abandono_historico_alterado_no_cuenta(self):
        estado = self.estado()
        self.base(estado)
        estado["abandono"]["actor"] = "Otro"
        self.assertEqual(len(firmas.pendientes(estado)), 1)

    def test_fa1_un_abandono_historico_quitado_se_nombra(self):
        estado = self.estado()
        self.base(estado)
        estado["abandono"] = None
        self.assertIn("fue quitada", " ".join(firmas.pendientes(estado)))

    def test_fa1_un_abandono_historico_reetiquetado_como_agente_no_cuenta(self):
        estado = self.estado()
        self.base(estado)
        estado["abandono"]["tipo_actor"] = "agente"
        self.assertIn("cambió su tipo de actor", " ".join(firmas.pendientes(estado)))

    def test_fa1_un_abandono_posterior_a_la_base_no_se_exime(self):
        self.base(self.estado("requisitos_importados"))
        self.assertEqual(len(firmas.pendientes(self.estado())), 1)

    def test_fa1_un_cambio_posterior_a_la_base_no_se_exime(self):
        self.base(self.estado())
        nuevo = self.estado()
        nuevo["id"] = "20261119-124202-8d6-nuevo"
        self.assertEqual(len(firmas.pendientes(nuevo)), 1)

    def test_fa1_una_fase_distinta_de_la_base_no_se_exime(self):
        anterior = self.estado()
        self.base(anterior)
        actual = {**anterior, "fase": "cerrada"}
        self.assertEqual(len(firmas.pendientes(actual)), 1)

    def test_fa1_los_cierres_historicos_siguen_contando(self):
        estado = self.estado("cerrada")
        self.base(estado)
        self.assertEqual(firmas.pendientes(estado), [])
