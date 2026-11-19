"""af1–af2: firmas de abandonos en las lecturas públicas y antes de tocar Oracle Task."""
import contextlib
import io
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_firmas as _firmas  # noqa: E402

f, firmas = _firmas.f, _firmas.firmas


class AbandonoFirmado(_firmas.Base):
    def nuevo(self):
        return f.nuevo("Abandono firmado", "notas")

    def rutas(self, ident):
        return f.ruta_registro(f.ruta_cambio(ident)), self.root / "tareas" / ident / "TAREA.md"

    def abandonar(self, ident):
        with self.escribe("1"):
            f.abandonar(ident)

    def base(self, ident):
        self.git("add", ".")
        self.git("commit", "-qm", "base de firmas")
        sha = self.git("rev-parse", "HEAD")
        self.exigir()
        ruta = self.root / ".factory/config.json"
        config = json.loads(ruta.read_text(encoding="utf-8"))
        config["firmas_base"] = sha
        ruta.write_text(json.dumps(config), encoding="utf-8")

    def consultas(self, ident):
        f.LEIDOS.clear()
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            codigo = f.main(["--proyecto", str(self.root), "verificar", "--json"])
        verificacion = json.loads(salida.getvalue())
        estado = f.datos_estado(ident)
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            f.mostrar(ident)
        return codigo, verificacion, estado, salida.getvalue()

    # af1: las entradas públicas comprueban las decisiones de los abandonos.
    def test_af1_historico_intacto_no_pide_firma_ni_entregables(self):
        ident = self.nuevo()
        self.abandonar(ident)
        self.base(ident)
        codigo, verificacion, estado, texto = self.consultas(ident)
        self.assertEqual((codigo, verificacion["problemas"], estado["pendientes"], estado["proximo_paso"]), (0, [], [], None))
        self.assertIn("Fase: abandonada", texto)

    def test_af1_historico_alterado_falla_en_verificar_y_estado(self):
        ident = self.nuevo()
        self.abandonar(ident)
        self.base(ident)
        registro, _ = self.rutas(ident)
        datos = json.loads(registro.read_text(encoding="utf-8"))
        datos["abandono"]["motivo"] = "motivo cambiado"
        registro.write_text(json.dumps(datos), encoding="utf-8")
        codigo, verificacion, estado, texto = self.consultas(ident)
        self.assertEqual(codigo, 1)
        self.assertTrue(any("abandono" in p["problema"] for p in verificacion["problemas"]))
        self.assertTrue(any("abandono" in p for p in estado["pendientes"]))
        self.assertIn("abandono", texto)
        self.assertIsNone(estado["proximo_paso"])

    def test_af1_historico_sin_decision_falla_en_verificar_y_estado(self):
        ident = self.nuevo()
        self.abandonar(ident)
        self.base(ident)
        registro, _ = self.rutas(ident)
        datos = json.loads(registro.read_text(encoding="utf-8"))
        datos.pop("abandono")
        registro.write_text(json.dumps(datos), encoding="utf-8")
        codigo, verificacion, estado, texto = self.consultas(ident)
        self.assertEqual(codigo, 1)
        self.assertTrue(any("histórica «abandono» fue quitada" in p["problema"] for p in verificacion["problemas"]))
        self.assertTrue(any("histórica «abandono» fue quitada" in p for p in estado["pendientes"]))
        self.assertIn("histórica «abandono» fue quitada", texto)

    def test_af1_abandono_posterior_a_base_no_se_exime(self):
        ident = self.nuevo()
        self.base(ident)
        # El fixture simula una decisión posterior a la activación que entró sin firma.
        registro, _ = self.rutas(ident)
        datos = json.loads(registro.read_text(encoding="utf-8"))
        datos["fase"] = "abandonada"
        datos["abandono"] = {"actor": "Persona fixture", "tipo_actor": "persona", "forma": "decidio",
                            "modo": "confirmacion", "cuando": "2026-11-19T00:00:00Z"}
        registro.write_text(json.dumps(datos), encoding="utf-8")
        codigo, verificacion, estado, texto = self.consultas(ident)
        self.assertEqual(codigo, 1)
        self.assertTrue(any("abandono" in p["problema"] and "sin firma" in p["problema"] for p in verificacion["problemas"]))
        self.assertTrue(any("abandono" in p and "sin firma" in p for p in estado["pendientes"]))
        self.assertIn("sin firma", texto)

    def test_af1_abandono_minimo_se_puede_consultar(self):
        ident = self.nuevo()
        registro, _ = self.rutas(ident)
        registro.write_text(json.dumps({"id": ident, "titulo": "Mínimo", "fase": "abandonada",
                                        "abandono": {"actor": "Persona fixture", "tipo_actor": "persona",
                                                     "forma": "decidio", "modo": "confirmacion"}}), encoding="utf-8")
        self.exigir()
        codigo, verificacion, estado, texto = self.consultas(ident)
        self.assertEqual(codigo, 1)
        self.assertTrue(any("abandono" in p["problema"] for p in verificacion["problemas"]))
        self.assertTrue(any("abandono" in p for p in estado["pendientes"]))
        self.assertIn("Fase: abandonada", texto)
        self.assertNotIn("primero hay que aceptar", str(verificacion))

    # af2: una firma fallida no deja efectos en el tracker.
    def test_af2_sin_llave_no_cierra_tarea(self):
        self.exigir()
        ident = self.nuevo()
        registro, tarea = self.rutas(ident)
        antes = registro.read_bytes(), tarea.read_bytes()
        with patch.dict(os.environ, {"ORACLE_FACTORY_LLAVE": str(self.llaves / "inexistente")}), \
                self.escribe("1"), self.assertRaisesRegex(f.FactoryError, "llave"):
            f.abandonar(ident)
        self.assertEqual((registro.read_bytes(), tarea.read_bytes()), antes)
        self.assertNotEqual(f.leer(ident)[1]["fase"], "abandonada")

    def test_af2_frase_incorrecta_no_cierra_tarea(self):
        self.exigir()
        ident = self.nuevo()
        registro, tarea = self.rutas(ident)
        antes = registro.read_bytes(), tarea.read_bytes()
        malo = self.llaves / "frase-incorrecta"
        malo.write_text("#!/bin/sh\necho otra-frase\n", encoding="utf-8")
        malo.chmod(0o755)
        with patch.object(firmas, "ENTORNO_PRUEBA", {"SSH_ASKPASS": str(malo), "SSH_ASKPASS_REQUIRE": "force"}), \
                self.escribe("1"), self.assertRaisesRegex(f.FactoryError, "firma"):
            f.abandonar(ident)
        self.assertEqual((registro.read_bytes(), tarea.read_bytes()), antes)
        self.assertNotEqual(f.leer(ident)[1]["fase"], "abandonada")

    def test_af2_llave_no_autorizada_no_cierra_tarea(self):
        otra = _firmas.llave(self.llaves, "otra")
        self.exigir(firmantes=[otra])
        ident = self.nuevo()
        registro, tarea = self.rutas(ident)
        antes = registro.read_bytes(), tarea.read_bytes()
        with self.escribe("1"), self.assertRaisesRegex(f.FactoryError, "llave.*no está"):
            f.abandonar(ident)
        self.assertEqual((registro.read_bytes(), tarea.read_bytes()), antes)
        self.assertNotEqual(f.leer(ident)[1]["fase"], "abandonada")

    def test_af2_tracker_falla_despues_de_firmar_y_se_recupera(self):
        self.exigir()
        ident = self.nuevo()
        registro, tarea = self.rutas(ident)
        real = f.ejecutar

        def sin_nota(argv, *args, **kwargs):
            if list(argv[:2]) == ["tasks", "note"]:
                return f.subprocess.CompletedProcess(argv, 1, "", "tracker indisponible")
            return real(argv, *args, **kwargs)

        with patch.object(f, "ejecutar", side_effect=sin_nota), self.escribe("1"), \
                self.assertRaisesRegex(f.FactoryError, "tracker indisponible"):
            f.abandonar(ident)
        self.assertNotEqual(f.leer(ident)[1]["fase"], "abandonada")
        self.assertIn("ESTADO: CERRADA", tarea.read_text(encoding="utf-8"))
        self.assertNotIn("abandono", json.loads(registro.read_text(encoding="utf-8")))
        self.abandonar(ident)
        self.assertEqual(f.leer(ident)[1]["fase"], "abandonada")
        self.assertEqual(tarea.read_text(encoding="utf-8").count("Abandonado por una persona"), 1)
        self.assertEqual(firmas.pendientes(f.leer(ident)[1]), [])


if __name__ == "__main__":
    unittest.main()
