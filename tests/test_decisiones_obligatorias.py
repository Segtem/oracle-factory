"""do1–do4: las decisiones que pide la fase están (do1), cada una la registra quien puede tomarla (do2), el modo sale de la
historia del cambio (do3) y lo histórico y lo autónomo legítimos siguen contando (do4). A4-01 de la cuarta auditoría: editar el
registro para quitar una decisión o cambiarle el actor la sacaba de lo que se comprueba.

Con la CLI en proceso sobre el ejemplo de notas; las ediciones del registro son las que hizo la auditoría."""
import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_firmas as _firmas  # noqa: E402

f, firmas = _firmas.f, _firmas.firmas
SOURCE = Path(__file__).resolve().parents[1]
NOTAS = ['sh', '-c', 'mkdir -p {salida} && {python} examples/notas/sensor.py --salida {salida}/hechos.json']


class Base(_firmas.Base):
    def editar(self, ident, cambio):
        """Lo que hizo la auditoría: editar a mano el registro del cambio."""
        ruta = f.ruta_registro(f.ruta_cambio(ident))
        estado = json.loads(ruta.read_text(encoding="utf-8"))
        cambio(estado)
        ruta.write_text(json.dumps(estado, indent=2), encoding="utf-8")
        f.LEIDOS.clear()

    def verificar(self):
        f.LEIDOS.clear()
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            codigo = f.main(["--proyecto", str(self.root), "verificar", "--json"])
        return codigo, " · ".join(p["problema"] for p in json.loads(salida.getvalue())["problemas"])

    def pendientes(self, ident):
        f.LEIDOS.clear()
        return " · ".join(f.datos_estado(ident)["pendientes"])

    def hasta_juzgar(self, agente=None):
        """El ejemplo de notas hasta el juicio verde, sin cerrar. Con `agente`, lo hace ese agente (el cambio ya está en un modo
        que se lo deja)."""
        ident = self.ident if agente else f.nuevo("Nota", con_ejemplo="notas")
        con = patch.object(f, "AGENTE", agente) if agente else contextlib.nullcontext()
        with con:
            with self.escribe("1"):
                f.aprobar_spec(ident)
            f.importar(ident)
            rid = f.leer(ident)[1]["requisitos"][0]
            f.medir(ident, requisito_id=rid, medidas=["notas.casos_ejecutados", "notas.resultados"], quitar_sin_medir=True)
            self.git("add", ".")
            self.git("commit", "-qm", "producto fixture")
            informe = self.root / "tareas" / ident / "revision.md"
            informe.write_text("Fixture de revisión; no es una revisión real.\n")
            with self.escribe("1"):
                f.revisar(ident, informe, "Persona fixture", "aprobar", 0)
            hechos = self.root / "tareas" / ident / "hechos.json"
            subprocess.run([sys.executable, "examples/notas/sensor.py", "--salida", hechos], cwd=self.root, check=True, capture_output=True)
            f.juzgar(ident, hechos)
        self.salida()
        return ident

    def cerrado(self, agente=None):
        ident = self.hasta_juzgar(agente)
        with patch.object(f, "AGENTE", agente) if agente else contextlib.nullcontext(), self.escribe("1"):
            f.cerrar(ident)
        self.salida()
        return ident

    def abandonado(self):
        ident = f.nuevo("Abandono", "notas")
        with self.escribe("1"):
            f.abandonar(ident)
        self.salida()
        return ident

    def autonomo(self):
        """Un cambio que una persona crea en modo autónomo (confirma en el menú)."""
        with self.escribe("1"):
            self.ident = f.nuevo("Nota", con_ejemplo="notas", modo="autonomo")
        self.salida()
        return self.ident

    def medida(self, ident):
        return f.leer(ident)[1]["requisitos"][0]


class FaseDo1(Base):
    def test_do1_un_abandono_sin_su_decision(self):
        self.exigir()
        ident = self.abandonado()
        self.assertEqual(self.verificar()[0], 0)
        self.editar(ident, lambda e: e.pop("abandono"))
        codigo, problemas = self.verificar()
        self.assertEqual(codigo, 1)
        self.assertIn("abandono", problemas)
        self.assertIn("abandono", self.pendientes(ident))

    def test_do1_un_cierre_sin_cada_decision(self):
        ident = self.cerrado()
        self.assertEqual(self.verificar()[0], 0)
        rid = self.medida(ident)
        quitar = {"cierre": lambda e: e.pop("cierre"), "revision": lambda e: e.update(revision=None),
                  "spec_aprobada": lambda e: e.update(spec_aprobada=None), f"medidas de {rid}": lambda e: e["medidas"].pop(rid)}
        ruta = f.ruta_registro(f.ruta_cambio(ident))
        original = ruta.read_bytes()
        for nombre, quita in quitar.items():
            with self.subTest(nombre):
                ruta.write_bytes(original)
                self.editar(ident, quita)
                codigo, problemas = self.verificar()
                self.assertEqual(codigo, 1, nombre)
                self.assertIn(nombre, problemas)
                self.assertIn(nombre, self.pendientes(ident))

    def test_do1_un_cierre_cuya_decision_no_es_un_objeto(self):
        ident = self.cerrado()
        self.editar(ident, lambda e: e.update(cierre="sí"))
        codigo, problemas = self.verificar()
        self.assertEqual(codigo, 1)
        self.assertIn("cierre", problemas)

    def test_do1_un_cambio_abierto_sin_revision_no_es_inconsistente(self):
        ident = f.nuevo("Nota", con_ejemplo="notas")
        with self.escribe("1"):
            f.aprobar_spec(ident)
        f.importar(ident)
        self.assertEqual(self.verificar(), (0, ""))


class ActorDo2(Base):
    def test_do2_un_actor_cambiado_a_agente(self):
        ident = self.cerrado()
        rid = self.medida(ident)
        campos = {"spec_aprobada": lambda e: e["spec_aprobada"], "revision": lambda e: e["revision"], "cierre": lambda e: e["cierre"],
                  f"medidas de {rid}": lambda e: e["medidas"][rid]}
        ruta = f.ruta_registro(f.ruta_cambio(ident))
        original = ruta.read_bytes()
        for nombre, decision in campos.items():
            with self.subTest(nombre):
                ruta.write_bytes(original)
                self.editar(ident, lambda e: decision(e).update(tipo_actor="agente", actor="robot"))
                codigo, problemas = self.verificar()
                self.assertEqual(codigo, 1, nombre)
                self.assertIn(nombre, problemas)

    def test_do2_un_abandono_cambiado_a_agente(self):
        ident = self.abandonado()
        self.editar(ident, lambda e: e["abandono"].update(tipo_actor="agente"))
        codigo, problemas = self.verificar()
        self.assertEqual(codigo, 1)
        self.assertIn("abandono", problemas)

    def test_do2_juzgar_y_cerrar_se_niegan_con_un_actor_que_no_puede(self):
        ident = self.hasta_juzgar()
        self.editar(ident, lambda e: e["spec_aprobada"].update(tipo_actor="agente"))
        with self.assertRaisesRegex(f.FactoryError, "spec"), self.escribe("1"):
            f.cerrar(ident)
        hechos = self.root / "tareas" / ident / "hechos.json"
        with self.assertRaisesRegex(f.FactoryError, "spec"):
            f.juzgar(ident, hechos)

    def test_do2_un_tipo_de_actor_quitado(self):
        ident = self.cerrado()
        self.editar(ident, lambda e: e["revision"].pop("tipo_actor"))
        codigo, problemas = self.verificar()
        self.assertEqual(codigo, 1)
        self.assertIn("revision", problemas)

    def test_do2_un_tipo_de_actor_desconocido(self):
        ident = self.cerrado()
        self.editar(ident, lambda e: e["cierre"].update(tipo_actor="sistema"))
        self.assertEqual(self.verificar()[0], 1)

    def test_do2_un_evento_de_persona_cambiado_a_agente(self):
        ident = self.cerrado()
        self.editar(ident, lambda e: e["eventos"].append({"accion": "soltado", "actor": "robot", "tipo_actor": "agente",
                                                          "modo": "confirmacion", "cuando": "2026-11-27T00:00:00+00:00"}))
        codigo, problemas = self.verificar()
        self.assertEqual(codigo, 1)
        self.assertIn("soltado", problemas)

    def test_do2_un_agente_en_modo_autonomo(self):
        self.autonomo()
        self.cerrado(agente="robot")
        self.assertEqual(self.verificar(), (0, ""))

    def test_do2_un_agente_con_una_medida_no_funcional_en_modo_funcional(self):
        with self.escribe("1"):
            ident = f.nuevo("Rapidez", con_ejemplo="notas", modo="funcional")
        carpeta, estado = f.leer(ident)
        (self.root / estado["spec"]).write_text(
            "# Capability: notas\n\n## ADDED Requirements\n\n### Requirement: rapida\nTipo: no funcional\nLa nota DEBE guardarse "
            "rápido.\n\n#### Scenario: una nota\n- DADO una nota\n- CUANDO se guarda\n- ENTONCES tarda poco\n", encoding="utf-8")
        (carpeta / "proposal.md").write_text("# Rapidez\n\nFixture.\n", encoding="utf-8")
        with self.escribe("1"):
            f.aprobar_spec(ident)
        f.importar(ident)
        with patch.object(f, "AGENTE", "robot"):
            f.medir(ident, requisito_id=self.medida(ident), medidas=["notas.casos_ejecutados"], quitar_sin_medir=True)
        self.assertEqual(f.leer(ident)[1]["medidas"][self.medida(ident)]["tipo_actor"], "agente")
        self.assertEqual(self.verificar(), (0, ""))


    def test_do2_una_aprobacion_del_sensor_de_un_agente_no_cuenta(self):
        self.declarar(NOTAS)
        ruta = self.root / ".factory/sensor-aprobado.json"
        aprobaciones = json.loads(ruta.read_text(encoding="utf-8"))
        aprobaciones[-1]["tipo_actor"] = "agente"
        ruta.write_text(json.dumps(aprobaciones), encoding="utf-8")
        with self.assertRaisesRegex(f.FactoryError, "persona"):
            _firmas._sf.sensor.aprobados()


class ModoDo3(Base):
    def test_do3_un_modo_editado(self):
        ident = self.cerrado()
        self.editar(ident, lambda e: (e.update(modo="autonomo"), e["cierre"].update(tipo_actor="agente", actor="robot")))
        codigo, problemas = self.verificar()
        self.assertEqual(codigo, 1)
        self.assertIn("modo", problemas)
        self.assertIn("cierre", problemas)
        self.assertIn("modo", self.pendientes(ident))

    def test_do3_un_modo_creado_autonomo_por_un_agente(self):
        ident = self.cerrado()
        self.editar(ident, lambda e: (e.update(modo="autonomo"), e["eventos"][0].update(modo="autonomo", tipo_actor="agente", actor="robot"),
                                      e["cierre"].update(tipo_actor="agente", actor="robot")))
        codigo, problemas = self.verificar()
        self.assertEqual(codigo, 1)
        self.assertIn("cierre", problemas)

    def test_do3_un_modo_bajado_por_un_agente(self):
        ident = self.cerrado()
        self.editar(ident, lambda e: (e.update(modo="autonomo"), e["eventos"].append(
            {"accion": "modo_cambiado", "actor": "robot", "tipo_actor": "agente", "modo": "confirmacion", "forma": "decidio",
             "cuando": "2026-11-27T00:00:00+00:00", "anterior": "confirmacion", "nuevo": "autonomo", "invalidadas": []}),
            e["cierre"].update(tipo_actor="agente", actor="robot")))
        codigo, problemas = self.verificar()
        self.assertEqual(codigo, 1)
        self.assertIn("cierre", problemas)

    def test_do3_un_cambio_de_modo_que_no_parte_del_modo_vigente(self):
        # D1 de la primera revisión de codex: una persona baja de funcional a autónomo, pero el cambio estaba en confirmación.
        ident = self.cerrado()
        self.editar(ident, lambda e: (e.update(modo="autonomo"), e["eventos"].append(
            {"accion": "modo_cambiado", "actor": "Persona fixture", "tipo_actor": "persona", "modo": "funcional", "forma": "decidio",
             "cuando": "2026-11-27T00:00:00+00:00", "anterior": "funcional", "nuevo": "autonomo", "invalidadas": []}),
            e["cierre"].update(tipo_actor="agente", actor="robot")))
        codigo, problemas = self.verificar()
        self.assertEqual(codigo, 1)
        self.assertIn("modo", problemas)
        self.assertIn("cierre", problemas)

    def test_do3_un_cambio_de_modo_anterior_a_la_creacion(self):
        # D1 de la segunda revisión de codex: el modo sale de la creación en adelante, no de lo que se anteponga.
        ident = self.cerrado()
        self.editar(ident, lambda e: (e.update(modo="autonomo"), e["eventos"].insert(0,
            {"accion": "modo_cambiado", "actor": "Persona fixture", "tipo_actor": "persona", "modo": "confirmacion", "forma": "decidio",
             "cuando": "2026-11-27T00:00:00+00:00", "anterior": "confirmacion", "nuevo": "autonomo", "invalidadas": []}),
            e["cierre"].update(tipo_actor="agente", actor="robot")))
        codigo, problemas = self.verificar()
        self.assertEqual(codigo, 1)
        self.assertIn("modo", problemas)
        self.assertIn("cierre", problemas)

    def test_do3_dos_cambios_de_modo_encadenados(self):
        self.ident = f.nuevo("Nota", con_ejemplo="notas")
        with self.escribe("1"):
            f.cambiar_modo(self.ident, "funcional")
        with self.escribe("1"):
            f.cambiar_modo(self.ident, "autonomo")
        self.salida()
        self.cerrado(agente="robot")
        self.assertEqual(self.verificar(), (0, ""))

    def test_do3_un_modo_bajado_por_una_persona(self):
        self.ident = f.nuevo("Nota", con_ejemplo="notas")
        with self.escribe("1"):
            f.cambiar_modo(self.ident, "autonomo")
        self.salida()
        self.cerrado(agente="robot")
        self.assertEqual(self.verificar(), (0, ""))

    def test_do3_una_creacion_autonoma_se_firma(self):
        self.exigir()
        ident = self.autonomo()
        creado = f.leer(ident)[1]["eventos"][0]
        self.assertEqual(creado["accion"], "cambio_creado")
        self.assertTrue(creado.get("firma", "").startswith("-----BEGIN SSH SIGNATURE-----"))
        self.assertEqual(self.verificar(), (0, ""))
        self.editar(ident, lambda e: e["eventos"][0].pop("firma"))
        codigo, problemas = self.verificar()
        self.assertEqual(codigo, 1)
        self.assertIn("cambio_creado", problemas)
        self.assertIn("modo", problemas)

    def test_do3_una_creacion_en_confirmacion_no_pide_firma(self):
        self.exigir()
        ident = f.nuevo("Nota", con_ejemplo="notas")
        self.assertNotIn("firma", f.leer(ident)[1]["eventos"][0])
        self.assertEqual(self.verificar(), (0, ""))


class HistoricoDo4(Base):
    def base(self):
        self.git("add", ".")
        self.git("commit", "-qm", "base de firmas")
        sha = self.git("rev-parse", "HEAD")
        self.exigir()
        ruta = self.root / ".factory/config.json"
        config = json.loads(ruta.read_text(encoding="utf-8"))
        config["firmas_base"] = sha
        ruta.write_text(json.dumps(config), encoding="utf-8")

    def viejo(self):
        """Un cierre anterior a los modos: la aprobación de la spec sin tipo de actor, la creación sin modo."""
        ident = self.cerrado()
        self.editar(ident, lambda e: (e["spec_aprobada"].pop("tipo_actor"), e.pop("modo"), e["eventos"][0].pop("modo")))
        return ident

    def test_do4_un_cierre_historico_intacto(self):
        self.viejo()
        self.base()
        self.assertEqual(self.verificar(), (0, ""))

    def test_do4_un_cierre_historico_alterado(self):
        ident = self.viejo()
        self.base()
        ruta = f.ruta_registro(f.ruta_cambio(ident))
        original = ruta.read_bytes()
        for nombre, cambio in {"cierre": lambda e: e.pop("cierre"),
                               "revision": lambda e: e["revision"].update(tipo_actor="agente")}.items():
            with self.subTest(nombre):
                ruta.write_bytes(original)
                self.editar(ident, cambio)
                codigo, problemas = self.verificar()
                self.assertEqual(codigo, 1, nombre)
                self.assertIn(nombre, problemas)

    def test_do4_sin_exigir_un_cierre_anterior_a_los_modos(self):
        self.viejo()
        self.assertEqual(self.verificar(), (0, ""))

    def test_do4_sin_exigir_un_cambio_con_modos_y_sin_tipo_de_actor(self):
        ident = self.cerrado()
        self.editar(ident, lambda e: e["spec_aprobada"].pop("tipo_actor"))
        self.assertEqual(self.verificar()[0], 1)

    def test_do4_con_exigir_quitar_el_modo_no_vuelve_historico_un_cambio(self):
        # D1 de la tercera revisión de codex: sin firmas el registro entero es editable (la spec lo declara); con «exigir», borrar el
        # modo de la creación y el tipo de actor de una decisión de agente la deja como de persona sin firma, y no cuenta.
        self.exigir()
        self.autonomo()
        ident = self.cerrado(agente="robot")
        self.assertEqual(self.verificar(), (0, ""))
        self.editar(ident, lambda e: (e.pop("modo", None), e["eventos"][0].pop("modo"), e["eventos"][0].pop("firma"),
                                      e["eventos"][0].pop("tipo_actor"), e["cierre"].pop("tipo_actor")))
        codigo, problemas = self.verificar()
        self.assertEqual(codigo, 1)
        self.assertIn("cierre", problemas)

    def test_do4_el_almacen_real(self):
        """El almacén de registros de Factory, si esta corrida lo tiene (el sensor de Factory lo pasa en ORACLE_FACTORY_REGISTROS)."""
        registros = os.environ.get("ORACLE_FACTORY_REGISTROS")
        if not registros or not Path(registros, ".factory").is_dir():
            self.skipTest("sin el almacén de registros de Factory en ORACLE_FACTORY_REGISTROS")
        if not (SOURCE / ".git").exists():
            self.skipTest("el producto no es un repositorio Git (la copia de la mutación): verificar no puede compararlo")
        copia = Path(tempfile.mkdtemp(prefix="almacen-"))
        self.addCleanup(shutil.rmtree, copia, True)
        subprocess.run(["git", "clone", "-q", "--no-hardlinks", registros, str(copia / "r")], check=True)
        p = subprocess.run([sys.executable, "-c", "import sys; from oracle_factory import cli; sys.exit(cli.main(sys.argv[1:]))",
                            "--proyecto", str(SOURCE), "--registros", str(copia / "r"), "verificar", "--json"],
                           capture_output=True, text=True, cwd=SOURCE, stdin=subprocess.DEVNULL)
        # Un cambio abierto en otro worktree se compara con este producto y sale desactualizado, por diseño: lo que se pide es que
        # ningún cambio terminado tenga problemas y que ninguno tenga problemas de sus decisiones.
        problemas = json.loads(p.stdout)["problemas"]
        terminados = {c.name for c in (copia / "r/.factory/cambios").iterdir()
                      if json.loads((c / "factory.json").read_text(encoding="utf-8")).get("fase") in ("cerrada", "abandonada")}
        self.assertGreater(len(terminados), 100)
        self.assertEqual([x for x in problemas if x["cambio"] in terminados], [])
        de_decisiones = ("falta la decisión", "no dice quién", "la registró el agente", "no coincide con el de su historia")
        self.assertEqual([x for x in problemas if any(m in x["problema"] for m in de_decisiones)], [])


if __name__ == "__main__":
    unittest.main()
