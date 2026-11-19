"""fh1: la base de firmas conserva sólo decisiones intactas de cambios ya cerrados."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import yaml
from oracle_factory import cli, firmas


ID = "20261119-101036-9u8-test"


class FirmasHistoricas(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        self.config = self.root / ".factory" / "config.json"
        self.config.parent.mkdir()
        self.registro = self.root / ".factory" / "cambios" / ID / "factory.json"
        self.registro.parent.mkdir(parents=True)
        for p in (patch.object(cli, "ROOT", self.root), patch.object(cli, "PRODUCTO", None)):
            p.start()
            self.addCleanup(p.stop)

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args], capture_output=True, text=True, check=True).stdout.strip()

    def estado(self, fase="cerrada"):
        return {"id": ID, "fase": fase,
                "spec_aprobada": {"actor": "Brian", "tipo_actor": "persona", "cuando": "2026-01-01T00:00:00Z"},
                "cierre": {"actor": "Brian", "tipo_actor": "persona", "cuando": "2026-01-02T00:00:00Z"} if fase == "cerrada" else None}

    def base(self, estado):
        self.registro.write_text(json.dumps(estado), encoding="utf-8")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.test", "commit", "-qm", "base")
        sha = self.git("rev-parse", "HEAD")
        self.config.write_text(json.dumps({"firmas": "exigir", "firmas_base": sha}), encoding="utf-8")
        return sha

    def problemas(self, estado):
        return firmas.pendientes(estado)

    def test_fh1_un_cierre_historico_intacto_cuenta(self):
        estado = self.estado()
        self.base(estado)
        self.assertEqual(self.problemas(estado), [])

    def test_fh1_una_decision_historica_alterada_no_cuenta(self):
        estado = self.estado()
        self.base(estado)
        estado["spec_aprobada"]["actor"] = "Otro"
        self.assertEqual(len(self.problemas(estado)), 1)

    def test_fh1_una_decision_historica_reetiquetada_como_agente_no_cuenta(self):
        estado = self.estado()
        self.base(estado)
        estado["spec_aprobada"]["tipo_actor"] = "agente"
        self.assertEqual(len(self.problemas(estado)), 1)

    def test_fh1_una_decision_nueva_en_un_cierre_historico_no_se_exime(self):
        estado = self.estado()
        self.base(estado)
        estado["medidas"] = {"requisito": {"actor": "Brian", "tipo_actor": "persona"}}
        self.assertEqual(len(self.problemas(estado)), 1)

    def test_fh1_una_decision_historica_con_firma_inventada_no_se_exime(self):
        estado = self.estado()
        self.base(estado)
        estado["spec_aprobada"]["firma"] = "inventada"
        self.assertEqual(len(self.problemas(estado)), 1)

    def test_fh1_una_decision_historica_reemplazada_con_firma_valida_cuenta(self):
        estado = self.estado()
        self.base(estado)
        estado["spec_aprobada"]["firma"] = "firma de prueba"
        with patch.object(firmas, "problema", return_value=None):
            self.assertEqual(self.problemas(estado), [])

    def test_fh1_duplicar_un_evento_historico_no_exime_la_copia(self):
        estado = self.estado()
        evento = {"accion": "modo_cambiado", "actor": "Brian", "tipo_actor": "persona", "cuando": "2026-01-01T12:00:00Z"}
        estado["eventos"] = [evento]
        self.base(estado)
        estado["eventos"].append(dict(evento))
        self.assertEqual(len(self.problemas(estado)), 1)

    def test_fh1_quitar_un_evento_historico_no_queda_oculto(self):
        estado = self.estado()
        estado["eventos"] = [{"accion": "modo_cambiado", "actor": "Brian", "tipo_actor": "persona", "cuando": "2026-01-01T12:00:00Z"}]
        self.base(estado)
        estado["eventos"] = []
        self.assertEqual(len(self.problemas(estado)), 1)

    def test_fh1_un_cambio_abierto_en_la_base_no_se_exime(self):
        estado = self.estado("requisitos_importados")
        self.base(estado)
        self.assertEqual(len(self.problemas(estado)), 1)

    def test_fh1_un_cambio_posterior_a_la_base_no_se_exime(self):
        self.base(self.estado())
        nuevo = self.estado()
        nuevo["id"] = "20261119-101037-9u8-nuevo"
        self.assertEqual(len(self.problemas(nuevo)), 2)

    def test_fh1_sin_base_no_hay_excepcion(self):
        estado = self.estado()
        self.base(estado)
        self.config.write_text('{"firmas": "exigir"}', encoding="utf-8")
        self.assertEqual(len(self.problemas(estado)), 2)

    def test_fh1_base_mal_formada_se_rechaza(self):
        estado = self.estado()
        self.base(estado)
        self.config.write_text('{"firmas": "exigir", "firmas_base": "mal"}', encoding="utf-8")
        with self.assertRaisesRegex(cli.FactoryError, "firmas_base"):
            self.problemas(estado)

    def test_fh1_base_ilegible_no_exime(self):
        estado = self.estado()
        self.base(estado)
        self.config.write_text('{"firmas": "exigir", "firmas_base": "' + "f" * 40 + '"}', encoding="utf-8")
        self.assertEqual(len(self.problemas(estado)), 2)

    def test_fh1_el_ci_del_almacen_trae_el_commit_base(self):
        plantilla = Path(__file__).resolve().parents[1] / "docs/plantillas/verificar-almacen.yml"
        pasos = yaml.safe_load(plantilla.read_text(encoding="utf-8"))["jobs"]["verificar"]["steps"]
        almacen = next(p for p in pasos if p.get("with", {}).get("path") == "almacen")
        self.assertEqual(almacen["with"].get("fetch-depth"), 0)
