"""Decisiones sobre un cambio fuera del flujo principal (sacado de cli.py): qué vale tras unir dos ramas, abandonarlo y
cambiar su modo de trabajo. Sumarse, soltar y dejar un mensaje siguen en cli.py: su decorador (reintentar_si_cambia) se aplica al
importar.

Lo que necesita de cli.py lo lee de `cli` en el momento de usarlo (`cli.NOMBRE`), no lo copia."""
from __future__ import annotations

import json
import sys


def decidir_union(identificador: str, campo: str, cual: str) -> None:
    """Una persona elige cuál de las dos versiones vale de algo que dos ramas decidieron distinto (también en un cambio
    cerrado: dos cierres se eligen acá)."""
    carpeta, estado = cli.leer(identificador)
    pendiente = next((x for x in estado.get("pendientes_de_union") or [] if x.get("campo") == campo), None)
    if pendiente is None:
        raise cli.FactoryError(f"{identificador} no tiene nada pendiente de unir en {campo}; no cambié nada")
    valor = pendiente[cual]
    cli.confirmar_persona((f"¿Vale la versión {cual} de {campo} en {identificador}?",
                       f"Sí, la {cual}: {json.dumps(valor, ensure_ascii=False)[:120]}", "queda esa y se borra el aviso"),
                      "no elegí nada")
    destino, camino = estado, pendiente.get("camino") or campo.split(".")
    for k in camino[:-1]:
        destino = destino.setdefault(k, {})
    if valor is None:
        destino.pop(camino[-1], None)
    else:
        destino[camino[-1]] = valor
    estado["pendientes_de_union"] = [x for x in estado["pendientes_de_union"] if x is not pendiente]
    if not estado["pendientes_de_union"]:
        estado.pop("pendientes_de_union")
    cli.evento(estado, "union_decidida", campo=campo, eligio=cual)
    cli.guardar(carpeta, estado)
    print(f"En {identificador}, {campo} quedó con la versión {cual}.")



def aviso_union(identificador: str, estado: dict) -> list[str]:
    return [f"al unir dos ramas, {x.get('campo')} quedó con dos valores ({json.dumps(x.get('nuestro'), ensure_ascii=False)[:80]} y "
            f"{json.dumps(x.get('suyo'), ensure_ascii=False)[:80]}); Factory no eligió: "
            f"{cli.unir_mod.como_resolver(x.get('campo', ''), identificador)}" for x in estado.get("pendientes_de_union") or []]



def abandonar(identificador: str, motivo_agente: str | None = None) -> None:
    """Abandonar descarta las promesas del cambio: lo decide una persona en cualquier modo; un agente sólo propone el motivo."""
    carpeta = cli.ruta_cambio(identificador)
    if cli.ruta_segura(cli.ruta_registro(carpeta)).is_file():
        _, previo = cli.leer(identificador)
        quedan = [r for r in ((previo.get("abandono") or {}).get("requisitos_quitados") or [])
                  if (cli.requisitos_dir() / f"{r}.requisito").is_file()] if previo.get("fase") == "abandonada" else []
        if quedan:  # un corte entre el registro y el borrado: la decisión ya está tomada, sólo falta completarla
            for rid in quedan:
                (cli.requisitos_dir() / f"{rid}.requisito").unlink()
            cli.actualizar_resumen()
            print(f"{identificador} ya estaba abandonado; quité de requisitos/ lo que había quedado: {', '.join(quedan)}.")
            return
        carpeta, estado = cli.abierto(identificador)
    elif (carpeta / "proposal.md").is_file():  # una carpeta anterior al flujo: el abandono le da un registro mínimo
        primera = (carpeta / "proposal.md").read_text(encoding="utf-8").strip().splitlines()[:1]
        estado = {"id": identificador, "titulo": primera[0].lstrip("# ").strip() if primera else identificador,
                  "fase": "sin registro"}
    else:
        raise cli.FactoryError(f"no encuentro el cambio {identificador}: ni su registro ni su propuesta")
    if cli.AGENTE:
        if not (motivo_agente and motivo_agente.strip()):
            raise cli.FactoryError("con --agente, abandonar propone el motivo: indicá --motivo; abandonar lo decide una persona")
        if estado["fase"] == "sin registro":
            raise cli.FactoryError("una carpeta sin registro no guarda propuestas: la persona elige o escribe el motivo al abandonarla")
        # Fuera de «propuestas»: ésas son las decisiones canónicas de modos.DECISIONES.
        estado.setdefault("motivos_propuestos", {})["abandono"] = {"motivo": motivo_agente.strip(), **cli.actor(), "cuando": cli.ahora()}
        cli.evento(estado, "abandono_propuesto", forma="propuso")
        cli.guardar(carpeta, estado)
        print(f"Motivo propuesto por {cli.AGENTE}: «{motivo_agente.strip()}». Abandonar lo decide una persona: "
              f"oracle-factory abandonar {identificador}")
        return
    if motivo_agente:
        raise cli.FactoryError("--motivo es la propuesta de un agente; una persona elige el motivo en el menú")
    requisitos = [r for r in estado.get("requisitos", []) if (cli.requisitos_dir() / f"{r}.requisito").is_file()]
    tarea = cli.ROOT / "tareas" / identificador / "TAREA.md"
    print(f"{identificador} — {estado['titulo']} (fase {estado['fase']}).")
    print("Se quitan de requisitos/ (quedan en la historia de Git): " + (", ".join(requisitos) or "ninguno") + ".")
    print("La propuesta y la spec del cambio quedan como están; nada se fusiona en openspec/specs/.")
    cli.confirmar_persona((f"Abandonar {identificador}", "Abandonar el cambio",
                       "pasa a abandonado, quita sus requisitos de requisitos/ y cierra su tarea"),
                      "abandono cancelado; el cambio sigue como estaba")
    propuesto = ((estado.get("motivos_propuestos") or {}).get("abandono") or {}).get("motivo")
    motivo = cli.elegir_motivo(f"no se va a terminar: queda abandonado en la fase {estado['fase']}"
                           + (f" con {len(requisitos)} requisitos sin cerrar" if requisitos else "")
                           + "; lo que siga va en un cambio nuevo.", propuesto)
    forma = "confirmo" if motivo[1] == "agente" else "decidio"
    estado["fase"] = "abandonada"
    estado["abandono"] = {**cli.registro_decision(estado, forma, motivo), "requisitos_quitados": requisitos}
    (estado.get("motivos_propuestos") or {}).pop("abandono", None)
    cli.evento(estado, "abandono", forma=forma, requisitos_quitados=requisitos)
    cli.firmas_mod.sellar(estado)  # una firma fallida no debe cerrar ni anotar la tarea
    if cli.firmas_mod.exige(cli.config_proyecto()):
        firmantes = (cli.PRODUCTO or cli.ROOT) / cli.firmas_mod.FIRMANTES
        if problema := cli.firmas_mod.problema(identificador, "abandono", estado["abandono"], firmantes):
            raise cli.FactoryError(f"la decisión de abandono no cuenta: {problema}; no modifiqué la tarea")
    if tarea.is_file():
        # El tracker antes que Factory: si falla, el cambio sigue abierto y repetir abandonar lo completa (una tarea ya
        # cerrada no se vuelve a cerrar y la nota no se repite). Cerrar va primero para no dejar la nota en una tarea abierta.
        if "ESTADO: CERRADA" not in tarea.read_text(encoding="utf-8"):
            p = cli.ejecutar(["tasks", "close", identificador, "--proyecto", str(cli.ROOT)])
            if p.returncode:
                raise cli.FactoryError(p.stderr.strip() or "oracle-task no pudo cerrar la tarea")
        nota = f"Abandonado por una persona; motivo: {motivo[0]}"
        if nota not in tarea.read_text(encoding="utf-8"):
            cli.nota_tarea(identificador, nota)
    else:
        print(f"Aviso: {identificador} no tiene tarea en tareas/; no hay nada que cerrar en el tracker.", file=sys.stderr)
    cli.guardar(carpeta, estado)
    for rid in requisitos:  # después del registro: lo que se quitó queda dicho aunque se corte acá
        (cli.requisitos_dir() / f"{rid}.requisito").unlink(missing_ok=True)
    cli.actualizar_resumen()
    print(f"Abandonado: {identificador}; {cli.quien(estado['abandono'])}.")



def cambiar_modo(identificador: str, nuevo_modo: str) -> None:
    carpeta, estado = cli.abierto(identificador)
    actual = cli.modo_de(estado)
    if nuevo_modo not in cli.modos.MODOS:
        raise cli.FactoryError("modo desconocido; usá " + ", ".join(cli.modos.MODOS))
    if nuevo_modo == actual:
        print(f"El cambio ya está en modo {actual}.")
        return
    if cli.modos.baja_intervencion(actual, nuevo_modo):
        if cli.AGENTE:
            raise cli.FactoryError(f"pasar de {actual} a {nuevo_modo} reduce la intervención humana: lo decide una persona, sin --agente")
        cli.confirmar_persona((f"Pasar {identificador} de {actual} a {nuevo_modo}", f"Pasar a {nuevo_modo}",
                           "reduce la intervención humana; las propuestas que dejen de valer se invalidan"),
                          "cambio de modo cancelado; el modo sigue igual")
    estado["modo"] = nuevo_modo
    tipos = cli.tipos_cambio(estado)
    propuestas, invalidadas = estado.setdefault("propuestas", {}), []

    def via_nueva(registro, decision, tipos_):
        # None: sigue valiendo. 'propone': pasa a propuesta. 'rechaza': se descarta, la decide una persona.
        if not registro or registro.get("tipo_actor") != "agente":
            return None
        via = cli.modos.via_agente(nuevo_modo, decision, tipos_)
        return None if via == "decide" else via

    via = via_nueva(estado.get("spec_aprobada"), "spec", tipos)
    if via:
        sa = estado["spec_aprobada"]
        if via == "propone":
            propuestas["spec"] = {"firma": sa["documentos"], "actor": sa["actor"], "tipo_actor": "agente", "cuando": sa["cuando"]}
        estado.update(spec_aprobada=None, revision=None, oracle=None, fase="espera_aprobacion_spec")
        invalidadas.append(("spec", via))
    rev = estado.get("revision")
    via = via_nueva(rev, "revision", tipos)
    if via:
        if via == "propone":
            firma = cli.firma_revision(rev["formato"], rev["sha256"], rev.get("decisiones_sha256"), rev["revisor"], rev["decision"], rev["contexto"])
            if rev["formato"] == "libre":
                firma["abiertos"] = rev["hallazgos_abiertos"]
            propuestas["revision"] = {"firma": firma, "actor": rev["actor"], "tipo_actor": "agente", "cuando": rev["cuando"]}
        estado.update(revision=None, oracle=None)
        invalidadas.append(("revision", via))
    for rid, medida in list((estado.get("medidas") or {}).items()):
        via = via_nueva(medida, "medidas", [(estado.get("tipos") or {}).get(rid, "funcional")])
        if via:
            ruta = cli.requisitos_dir() / f"{rid}.requisito"
            estado.setdefault("medidas_pendientes", {})[rid] = {"sha256": medida.get("sha256") or cli.sha256(ruta.read_bytes()), "actor": medida["actor"],
                                                                "tipo_actor": "agente", "cuando": medida["cuando"],
                                                                "descartada": via == "rechaza"}
            del estado["medidas"][rid]
            estado.update(oracle=None)
            invalidadas.append(("medidas de " + rid, via))
    for decision in list(propuestas):
        if decision != "cierre" and cli.modos.via_agente(nuevo_modo, decision, tipos) == "rechaza":
            del propuestas[decision]
            invalidadas.append((f"propuesta de {decision}", "rechaza"))
    for rid, pendiente in (estado.get("medidas_pendientes") or {}).items():
        tipo_rid = [(estado.get("tipos") or {}).get(rid, "funcional")]
        if not pendiente.get("descartada") and cli.modos.via_agente(nuevo_modo, "medidas", tipo_rid) == "rechaza":
            pendiente["descartada"] = True
            invalidadas.append((f"propuesta de medidas de {rid}", "rechaza"))
    texto = {"propone": "pasa a propuesta: una persona la confirma", "rechaza": "se descarta: la decide una persona"}
    cli.evento(estado, "modo_cambiado", anterior=actual, nuevo=nuevo_modo, invalidadas=[f"{i}: {texto[v]}" for i, v in invalidadas])
    cli.guardar(carpeta, estado)
    cli.nota_tarea(identificador, f"Modo de trabajo: {actual} → {nuevo_modo}." + (
        " Decisiones de agente: " + "; ".join(f"{i} {texto[v]}" for i, v in invalidadas) + "." if invalidadas else ""))
    print(f"Modo de trabajo: {actual} → {nuevo_modo}.")
    for item, via in invalidadas:
        print(f"Decisión de agente sobre {item}: {texto[via]}.")


# Al final a propósito: `cli` importa este módulo y lo usa sólo al llamar a sus funciones.
from . import cli  # noqa: E402
