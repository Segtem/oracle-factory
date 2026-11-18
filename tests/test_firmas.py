"""Las decisiones de una persona van firmadas (fi1), una decisión sin firma válida no cuenta (fi2) y sin «exigir» se avisa (fi3).

Con la CLI en proceso, una llave ed25519 de prueba con frase y la frase entregada por SSH_ASKPASS sólo a través de
`firmas.ENTORNO_PRUEBA` (Factory no hereda SSH_ASKPASS ni SSH_AUTH_SOCK de su entorno)."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_sensor_de_factory as _sf  # noqa: E402
from oracle_factory import firmas  # noqa: E402

f = _sf.f
FRASE = "una frase de prueba"


def llave(carpeta: Path, nombre: str, frase: str = FRASE) -> Path:
    ruta = carpeta / nombre
    subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", frase, "-C", nombre, "-f", str(ruta)], check=True)
    return ruta


class Base(_sf.Base):
    def setUp(self):
        super().setUp()
        self.llaves = Path(tempfile.mkdtemp(prefix="llaves-"))
        self.addCleanup(subprocess.run, ["rm", "-rf", str(self.llaves)])
        self.mia = llave(self.llaves, "mia")
        pide = self.llaves / "pide"
        pide.write_text(f'#!/bin/sh\necho "{FRASE}"\n', encoding="utf-8")
        pide.chmod(0o755)
        for p in (patch.object(firmas, "ENTORNO_PRUEBA", {"SSH_ASKPASS": str(pide), "SSH_ASKPASS_REQUIRE": "force"}),
                  patch.dict(os.environ, {"ORACLE_FACTORY_LLAVE": str(self.mia)})):
            p.start()
            self.addCleanup(p.stop)

    def exigir(self, firmantes=None):
        ruta = self.root / ".factory/config.json"
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        datos["firmas"] = "exigir"
        ruta.write_text(json.dumps(datos, indent=2), encoding="utf-8")
        publicas = firmantes if firmantes is not None else [self.mia]
        (self.root / firmas.FIRMANTES).write_text(
            "".join(f"persona{i} {Path(str(p) + '.pub').read_text(encoding='utf-8')}" for i, p in enumerate(publicas)), encoding="utf-8")

    def aprobado(self):
        ident = f.nuevo("Nota", con_ejemplo="notas")
        with self.escribe("1"):
            f.aprobar_spec(ident)
        return ident

    def registro(self, ident):
        return json.loads(f.ruta_registro(f.ruta_cambio(ident)).read_text(encoding="utf-8"))

    def pendientes(self, ident):
        carpeta, estado = f.leer(ident)
        return f.pendientes_actuales(carpeta, estado)


class FirmaFi1(Base):
    # --- fi1: una decisión de persona lleva su firma ----------------------------------------------------------------------
    def test_fi1_una_decision_firmada_verifica_contra_su_texto(self):
        self.exigir()
        ident = self.aprobado()
        spec = self.registro(ident)["spec_aprobada"]
        self.assertTrue(spec["firma"].startswith("-----BEGIN SSH SIGNATURE-----"))
        huella = subprocess.run(["ssh-keygen", "-lf", str(self.mia) + ".pub"], capture_output=True, text=True, check=True).stdout.split()[1]
        self.assertEqual(spec["firma_llave"], huella)
        self.assertIsNone(firmas.problema(ident, "spec_aprobada", spec, self.root / firmas.FIRMANTES))
        self.assertFalse([p for p in self.pendientes(ident) if "firma" in p])

    def test_fi1_sin_llave_no_se_registra_nada(self):
        self.exigir()
        ident = f.nuevo("Nota", con_ejemplo="notas")
        antes = self.registro(ident)
        with patch.dict(os.environ, {"ORACLE_FACTORY_LLAVE": str(self.llaves / "no-existe")}), self.escribe("1"), \
                self.assertRaisesRegex(f.FactoryError, "llave"):
            f.aprobar_spec(ident)
        self.assertEqual(self.registro(ident), antes)

    def test_fi1_una_llave_sin_frase_no_firma(self):
        self.exigir()
        sin = llave(self.llaves, "sin-frase", frase="")
        ident = f.nuevo("Nota", con_ejemplo="notas")
        antes = self.registro(ident)
        with patch.dict(os.environ, {"ORACLE_FACTORY_LLAVE": str(sin)}), self.escribe("1"), self.assertRaisesRegex(f.FactoryError, "frase"):
            f.aprobar_spec(ident)
        self.assertEqual(self.registro(ident), antes)

    def test_fi1_una_firma_que_no_sale_no_registra_nada(self):
        self.exigir()
        ident = f.nuevo("Nota", con_ejemplo="notas")
        antes = self.registro(ident)
        malo = self.llaves / "mal"
        malo.write_text('#!/bin/sh\necho "otra frase"\n', encoding="utf-8")
        malo.chmod(0o755)
        with patch.object(firmas, "ENTORNO_PRUEBA", {"SSH_ASKPASS": str(malo), "SSH_ASKPASS_REQUIRE": "force"}), self.escribe("1"), \
                self.assertRaisesRegex(f.FactoryError, "firma"):
            f.aprobar_spec(ident)
        self.assertEqual(self.registro(ident), antes)

    def test_fi1_la_frase_no_llega_por_el_entorno_heredado(self):
        pide = self.llaves / "pide"
        with patch.dict(os.environ, {"SSH_ASKPASS": str(pide), "SSH_ASKPASS_REQUIRE": "force", "SSH_AUTH_SOCK": "/tmp/agente"}), \
                patch.object(firmas, "ENTORNO_PRUEBA", {}):
            entorno = firmas.entorno()
            self.assertFalse({"SSH_ASKPASS", "SSH_ASKPASS_REQUIRE", "SSH_AUTH_SOCK"} & set(entorno))
            with self.assertRaisesRegex(f.FactoryError, "firma"):
                firmas.firmar(b'{"cambio":"x"}', entrada=subprocess.DEVNULL)

    def test_fi1_un_agente_no_firma_y_solo_propone(self):
        self.exigir()
        ident = f.nuevo("Nota", con_ejemplo="notas")
        with patch.object(f, "AGENTE", "claude-code"), patch.object(firmas, "firmar", side_effect=AssertionError("no se firma")):
            f.aprobar_spec(ident)
        registro = self.registro(ident)
        self.assertIsNone(registro.get("spec_aprobada"))
        self.assertIn("spec", registro["propuestas"])


    def test_fi1_cada_decision_de_persona_del_flujo_se_firma(self):
        self.exigir()
        ident = self.medido()  # aprobar la spec, importar y elegir las medidas, como persona
        with self.escribe("1"):
            f.cambiar_modo(ident, "funcional")
        estado = self.registro(ident)
        firmadas = [c for c, r in firmas.registros(estado) if r.get("tipo_actor") == "persona"]
        self.assertTrue(any(c.startswith("medidas/") for c in firmadas), firmadas)
        self.assertTrue(any(c.startswith("eventos/modo_cambiado@") for c in firmadas), firmadas)
        for campo, registro in firmas.registros(estado):
            if registro.get("tipo_actor") == "persona":
                self.assertIsNone(firmas.problema(ident, campo, registro, self.root / firmas.FIRMANTES), campo)
        self.assertFalse([p for p in self.pendientes(ident) if "firma" in p])

    def test_fi1_la_aprobacion_del_sensor_se_firma_y_sin_firma_no_cuenta(self):
        self.declarar()  # aprobado antes de «exigir»: sin firma
        config = f.config_proyecto()["sensor"]
        self.assertTrue(_sf.sensor.aprobado(config))
        self.exigir()
        self.assertFalse(_sf.sensor.aprobado(config))  # con «exigir», una aprobación sin firma no cuenta
        with self.escribe("1"):
            _sf.sensor.aprobar()
        ultima = json.loads((self.root / ".factory/sensor-aprobado.json").read_text(encoding="utf-8"))[-1]
        self.assertTrue(ultima["firma"].startswith("-----BEGIN SSH SIGNATURE-----"))
        self.assertTrue(_sf.sensor.aprobado(config))


    def test_fi1_el_texto_firmado_es_canonico(self):
        registro = {"tipo_actor": "persona", "actor": "Ñandú", "firma": "x", "firma_llave": "y", "cuando": "t"}
        esperado = '{"cambio":"c","campo":"spec_aprobada","registro":{"actor":"Ñandú","cuando":"t","tipo_actor":"persona"}}'.encode("utf-8")
        self.assertEqual(firmas.texto("c", "spec_aprobada", registro), esperado)  # ordenado, en UTF-8 y sin la firma
        self.assertEqual(firmas.texto("c", "spec_aprobada", dict(reversed(list(registro.items())))), esperado)

    def test_fi1_el_motivo_queda_en_lo_que_se_firma(self):
        carpeta, estado = f.leer(f.nuevo("Nota", con_ejemplo="notas"))
        registro = f.registro_decision(estado, "decidio", ("lo leí", "persona"))
        self.assertEqual((registro["motivo"], registro["origen_motivo"]), ("lo leí", "persona"))
        self.assertIn('"motivo":"lo leí","origen_motivo":"persona"'.encode("utf-8"), firmas.texto("c", "x", registro))


    def test_fi1_un_registro_preparado_con_el_mismo_instante_no_queda_firmado(self):
        # Hallazgo firmas-01 de codex: sellar reconocía la decisión nueva sólo por su «cuando».
        self.exigir()
        carpeta, estado = f.leer(f.nuevo("Nota", con_ejemplo="notas"))
        nueva = f.registro_decision(estado, "decidio")
        viejo = {k: v for k, v in nueva.items() if k != firmas.MARCA}  # el mismo instante, sin la marca
        estado["cierre"], estado["spec_aprobada"] = dict(nueva), {**viejo, "forma": "confirmo"}
        firmas.sellar(estado)
        self.assertNotIn("firma", estado["spec_aprobada"])
        self.assertIsNone(firmas.problema(estado["id"], "cierre", estado["cierre"], self.root / firmas.FIRMANTES))
        self.assertNotIn(firmas.MARCA, estado["cierre"])
        # Con una marca inventada, no se firma nada: se nombra la decisión y no se registra.
        otra = f.registro_decision(estado, "decidio")
        estado["revision"], estado["abandono"] = dict(otra), {**viejo, firmas.MARCA: "0" * 32}
        with self.assertRaisesRegex(f.FactoryError, "«abandono».*no armó este proceso"):
            firmas.sellar(estado)
        self.assertNotIn("firma", estado["abandono"])
        self.assertNotIn("firma", estado["revision"])  # ni la legítima: se comprueban todas antes de firmar

    def test_fi1_la_marca_de_por_firmar_no_queda_en_el_registro(self):
        self.exigir()
        ident = self.aprobado()
        self.assertNotIn(firmas.MARCA, json.dumps(self.registro(ident)))


class SinFirmaFi2(Base):
    # --- fi2: una decisión sin firma válida no cuenta ---------------------------------------------------------------------
    def test_fi2_una_decision_sin_firma_no_deja_cerrar(self):
        ident = self.aprobado()  # sin «exigir»: se registró sin firma
        self.exigir()
        [problema] = [p for p in self.pendientes(ident) if "firma" in p]
        self.assertIn("spec_aprobada", problema)
        self.assertIn("sin firma", problema)
        with self.escribe("1"), self.assertRaisesRegex(f.FactoryError, "spec_aprobada.*sin firma"):
            f.cerrar(ident)

    def test_fi2_una_firma_de_otro_texto_hace_fallar_verificar(self):
        self.exigir()
        ident = self.aprobado()
        ruta = f.ruta_registro(f.ruta_cambio(ident))
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        datos["spec_aprobada"]["forma"] = "confirmo" if datos["spec_aprobada"]["forma"] != "confirmo" else "decidio"
        ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        f.LEIDOS.clear()
        salida, errores = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(errores):
            codigo = f.main(["--proyecto", str(self.root), "verificar"])
        self.assertEqual(codigo, 1)
        self.assertIn("spec_aprobada", salida.getvalue() + errores.getvalue())
        self.assertIn("no corresponde", salida.getvalue() + errores.getvalue())

    def test_fi2_una_llave_que_no_esta_en_la_lista_no_deja_juzgar(self):
        otra = llave(self.llaves, "otra")
        self.exigir(firmantes=[otra])
        ident = self.aprobado()
        with self.assertRaisesRegex(f.FactoryError, r"no se puede juzgar.*spec_aprobada.*\.factory-firmantes"):
            f.juzgar(ident, self.root / "hechos.json")

    def test_fi2_sin_la_lista_de_firmantes_ninguna_firma_cuenta(self):
        self.exigir()
        ident = self.aprobado()
        (self.root / firmas.FIRMANTES).unlink()
        self.assertTrue(any("spec_aprobada" in p and firmas.FIRMANTES in p for p in self.pendientes(ident)))

    def test_fi2_un_evento_de_persona_alterado_se_nombra(self):
        self.exigir()
        ident = self.aprobado()
        with self.escribe("1"):
            f.cambiar_modo(ident, "funcional")
        ruta = f.ruta_registro(f.ruta_cambio(ident))
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        [evento] = [e for e in datos["eventos"] if e["accion"] == "modo_cambiado"]
        evento["nuevo"] = "autonomo"
        ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        f.LEIDOS.clear()
        self.assertTrue(any("«modo_cambiado»" in p and "no corresponde" in p for p in self.pendientes(ident)), self.pendientes(ident))

    def test_fi2_cada_campo_de_decision_se_comprueba(self):
        self.exigir()
        ident = self.aprobado()
        carpeta, estado = f.leer(ident)
        persona = {"actor": "Alguien", "tipo_actor": "persona", "forma": "decidio", "modo": "confirmacion", "cuando": "2026-11-18T00:00:00"}
        for campo in ("revision", "cierre", "abandono"):
            estado[campo] = dict(persona)
        estado.setdefault("medidas", {})["req.x"] = dict(persona)
        estado["cierre_de_agente"] = {**persona, "tipo_actor": "agente"}
        nombrados = " ".join(firmas.pendientes(estado))
        for campo in ("revision", "cierre", "abandono", "medidas de req.x"):
            self.assertIn(campo, nombrados)
        self.assertNotIn("spec_aprobada", nombrados)  # la firmada sigue valiendo


class SinExigirFi3(Base):
    # --- fi3: sin «exigir», las firmas se avisan ---------------------------------------------------------------------------
    def test_fi3_sin_exigir_se_registra_sin_firma_y_estado_avisa(self):
        with patch.object(firmas, "firmar", side_effect=AssertionError("no se firma sin exigir")):
            ident = self.aprobado()
        self.assertNotIn("firma", self.registro(ident)["spec_aprobada"])
        avisos = f.datos_estado(ident)["avisos"]
        self.assertTrue(any("no están firmadas" in a for a in avisos), avisos)
        self.salida()
        f.mostrar(ident)
        self.assertIn("no están firmadas", self.salida())

    def test_fi3_un_registro_viejo_se_lee_como_siempre(self):
        ident = f.nuevo("Nota", con_ejemplo="notas")
        self.salida()
        f.mostrar(ident)
        f.listar()
        self.assertIn(ident, self.salida())
        self.assertFalse([a for a in f.datos_estado(ident)["avisos"] if "firmadas" in a])  # sin decisiones de persona, nada que avisar
        self.exigir()
        self.assertEqual(firmas.pendientes(f.leer(ident)[1]), [])

    def test_fi3_un_valor_invalido_de_firmas_se_rechaza(self):
        ruta = self.root / ".factory/config.json"
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        datos["firmas"] = "a veces"
        ruta.write_text(json.dumps(datos), encoding="utf-8")
        with self.assertRaisesRegex(f.FactoryError, "firmas"):
            f.config_proyecto()


if __name__ == "__main__":
    unittest.main()
