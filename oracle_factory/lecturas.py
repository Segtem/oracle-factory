"""Las lecturas de sólo lectura y los archivos generados: resumen, kb, por-que, estado, donde y trazabilidad (sacado de cli.py).

Lo que necesita de cli.py lo lee de `cli` en el momento de usarlo (`cli.NOMBRE`), no lo copia: así un valor
cambiado en `cli` (la raíz del proyecto en las pruebas, por ejemplo) vale también acá."""
from __future__ import annotations

from pathlib import Path
import json
import os
import re
import shutil
import subprocess
import sys

from . import archivo
from . import estructura
from . import kb as kb_mod
from . import resumen
from . import tablero as tablero_mod
from . import trazabilidad as trazabilidad_mod


def situacion_requisitos(estado: dict) -> list[tuple[str, str, str | None]]:
    """[(requisito, 'vigente'|'reemplazado'|'ausente', cambio que lo reemplazó)] de un cambio archivado."""
    if not estado.get("archivo"):
        return []
    indice = cli.leer_indice(estado["archivo"]["capacidad"])
    return [(rid, *archivo.situacion(indice, rid)) for rid in estado.get("requisitos", [])]


def _json_de_revision(relativa, nombre: str) -> tuple[dict, str | None]:
    """(datos, problema): un documento ausente, inválido o fuera del proyecto se informa, no se toma por vacío."""
    if not relativa:  # sólo se llama para revisiones guiadas, que siempre registran los dos documentos
        return {}, f"la revisión guiada no registra su {nombre}"
    try:
        datos = json.loads(cli.ruta_segura(cli.ROOT / relativa).read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError, cli.FactoryError) as e:
        return {}, f"no se pudo leer el {nombre} de la revisión ({relativa}): {type(e).__name__}"
    if not isinstance(datos, dict):
        return {}, f"el {nombre} de la revisión ({relativa}) no es un objeto JSON"
    return datos, None


def _lista(valor) -> list:
    return valor if isinstance(valor, list) else []


def texto_resumen(salida: Path | None = None) -> str:
    """Junta los datos de los registros y genera el resumen (sin escribir nada)."""
    destino = cli.ruta_resumen(salida)
    raiz_relativa = os.path.relpath(cli.ROOT, destino.parent).replace(os.sep, "/") + "/"
    return resumen.generar(*cli.insumos_resumen(), "" if raiz_relativa == "./" else raiz_relativa)


def insumos_resumen() -> tuple:
    """(índices, registros, medidas, abiertos, revisiones, sin registro): lo que leen el resumen en texto y en JSON."""
    carpeta_specs = cli.ROOT / estructura.DIR / "specs"
    indices = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(carpeta_specs.glob("*.json"))] \
        if carpeta_specs.is_dir() else []
    registros, abiertos, revisiones, sin_registro = {}, [], {}, []
    for carpeta in sorted(cli.CHANGES.iterdir()) if cli.CHANGES.is_dir() else []:
        if not cli.ID_RE.fullmatch(carpeta.name):
            continue
        if not cli.ruta_registro(carpeta).is_file():
            sin_registro.append(carpeta.name)
            continue
        _, estado = cli.leer(carpeta.name)
        registros[estado["id"]] = estado
        if estado.get("fase") == "abandonada":
            continue  # el resumen los toma de registros, en su sección
        if estado.get("fase") != "cerrada":
            abiertos.append({"id": estado["id"], "titulo": estado.get("titulo", ""), "fase": estado.get("fase", "?"),
                             "modo": cli.modo_de(estado), "capacidad": cli.capacidad_destino(estado.get("capacidad", "?")),
                             "pendientes": cli.pendientes_actuales(carpeta, estado)})
            continue
        rev = estado.get("revision") if isinstance(estado.get("revision"), dict) else {}
        problemas = []
        informe, decisiones = {}, {}
        if rev.get("formato") == "guiado":  # la revisión libre (review.md) no declara riesgos ni límites con estructura
            informe, p1 = cli._json_de_revision(rev.get("informe"), "informe")
            decisiones, p2 = cli._json_de_revision(rev.get("decisiones"), "documento de decisiones")
            problemas = [p for p in (p1, p2) if p]
        hallazgos = {h.get("id"): h for h in cli._lista(informe.get("hallazgos")) if isinstance(h, dict)}
        revisiones[estado["id"]] = {"decisiones": [d for d in cli._lista(decisiones.get("decisiones")) if isinstance(d, dict)],
                                    "hallazgos": hallazgos, "problemas": problemas,
                                    "limites": [l for l in cli._lista(informe.get("limites")) if isinstance(l, str)]}
    medidas = {}
    for indice in indices:
        for req in indice["requisitos"].values():
            ruta = cli.requisitos_dir() / f"{req['requisito']}.requisito"
            texto = ruta.read_text(encoding="utf-8") if ruta.is_file() else ""
            m = re.search(r"(?m)^\s+medido_por\s+(.+?)\s*$", texto)
            medidas[req["requisito"]] = [x.strip() for x in m[1].split(",")] if m else []
    return indices, registros, medidas, abiertos, revisiones, sin_registro


def ruta_resumen(salida: Path | None = None) -> Path:
    return cli.ruta_segura(cli.ROOT / salida if salida else cli.ROOT / estructura.DIR / "resumen.md")


def comando_resumen(verificar: bool, salida: Path | None, ver: bool = False) -> None:
    destino, texto = cli.ruta_resumen(salida), cli.texto_resumen(salida)
    if verificar:
        actual = destino.read_text(encoding="utf-8") if destino.is_file() else None
        if actual != texto:
            print(f"{destino.relative_to(cli.ROOT)} " + ("no existe" if actual is None else "quedó viejo o se editó a mano")
                  + "; regeneralo con oracle-factory resumen.")
            raise SystemExit(1)
        print(f"{destino.relative_to(cli.ROOT)} está al día.")
        return
    destino.parent.mkdir(parents=True, exist_ok=True)
    cli.escribir_atomico(destino, texto.encode("utf-8"))
    if not ver:
        print(f"Resumen: {destino.relative_to(cli.ROOT)}. Para verlo con formato: oracle-factory resumen --ver")
    elif shutil.which("glow") and sys.stdout.isatty():
        subprocess.run(["glow", "-p", str(destino)], check=False)
    else:
        print(texto, end="")


def escribir_kb(notas: dict[str, str]) -> list[str]:
    """Escribe las notas que cambiaron; devuelve sus rutas."""
    escritas = []
    for rel, texto in notas.items():
        ruta = cli.ruta_segura(cli.ROOT / rel)
        datos = texto.encode("utf-8")
        if not ruta.is_file() or ruta.read_bytes() != datos:
            ruta.parent.mkdir(parents=True, exist_ok=True)
            cli.escribir_atomico(ruta, datos)
            escritas.append(rel)
    return escritas


def generadas_en_disco() -> set[str]:
    """Las notas de kb/ que dicen ser generadas (las de cambios/ y requisitos/, y el índice)."""
    base = cli.ROOT / kb_mod.DIR
    salida = set()
    for ruta in [base / "README.md", *base.glob("cambios/*.md"), *base.glob("requisitos/*.md")]:
        if ruta.is_file() and kb_mod.MARCA in ruta.read_text(encoding="utf-8", errors="replace")[:200]:
            salida.add(ruta.relative_to(cli.ROOT).as_posix())
    return salida


def actualizar_kb(identificador: str) -> None:
    """Después de guardar un registro: las notas de ese cambio, sus requisitos y el índice. Si falla, la decisión ya está
    hecha y `oracle-factory kb` la repara."""
    try:
        cli.escribir_kb(kb_mod.armar(cli, solo=identificador))
    except Exception as e:  # noqa: BLE001
        print(f"Aviso: no pude actualizar kb/ ({type(e).__name__}: {e}); corré oracle-factory kb.", file=sys.stderr)


def refrescar_kb(comando: str, identificador: str | None) -> None:
    """Al terminar un comando que cambió algo: las notas de ese cambio (o todas, si tocó varios). Algunos comandos escriben
    los requisitos después del registro (medir, importar), así que guardar() no alcanza."""
    if comando in cli.SOLO_LECTURA or not (cli.ROOT / kb_mod.DIR).is_dir():
        return
    try:  # entero: un abandono o un requisito retirado dejan notas que sobran
        notas = kb_mod.armar(cli)
        cli.escribir_kb(notas)
        for rel in cli.generadas_en_disco() - set(notas):
            (cli.ROOT / rel).unlink()
    except Exception as e:  # noqa: BLE001
        print(f"Aviso: no pude actualizar kb/ ({type(e).__name__}: {e}); corré oracle-factory kb.", file=sys.stderr)


def comando_kb(verificar: bool) -> None:
    notas = kb_mod.armar(cli)
    if not verificar:
        escritas = cli.escribir_kb(notas)
        sobran = sorted(cli.generadas_en_disco() - set(notas))
        for rel in sobran:
            (cli.ROOT / rel).unlink()
        print(f"kb/: {len(notas)} notas generadas ({len(escritas)} escritas, {len(sobran)} quitadas). "
              "Las de personas van en kb/notas/ con sus fuentes:.")
        return
    problemas = []
    for rel, texto in sorted(notas.items()):
        ruta = cli.ROOT / rel
        if not ruta.is_file():
            problemas.append(f"falta {rel}")
        elif ruta.read_bytes() != texto.encode("utf-8"):
            problemas.append(f"{rel} no coincide con el registro (quedó vieja o se editó a mano)")
    problemas += [f"sobra {rel}: es una nota generada de algo que ya no está" for rel in sorted(cli.generadas_en_disco() - set(notas))]
    for n in kb_mod.estado_de_notas(cli):
        if n["faltan"]:
            problemas.append(f"{n['nota']}: su fuente {', '.join(n['faltan'])} no existe")
        if n["cambiaron"]:
            problemas.append(f"{n['nota']} está por revisar: cambió {', '.join(n['cambiaron'])} desde que se revisó; "
                             f"actualizala si hace falta y marcala con oracle-factory kb revisada {n['nota']}")
    if problemas:
        raise cli.FactoryError("kb/ no está al día:\n- " + "\n- ".join(problemas) + "\nLas generadas se rehacen con oracle-factory kb.")
    print(f"kb/ está al día: {len(notas)} notas generadas y las de personas revisadas.")


def kb_revisada(nota: str) -> None:
    """Una persona marca una nota de kb/notas/ como revisada: guarda la huella de sus fuentes de este momento."""
    if cli.AGENTE:
        raise cli.FactoryError("marcar una nota como revisada lo decide una persona, sin --agente")
    cli.exigir_terminal("marcar una nota como revisada")
    relativa = cli.carpeta_relativa(nota)
    ruta = cli.ROOT / relativa if relativa is not None else None
    if ruta is None or not ruta.is_file() or ruta.parent != cli.ROOT / kb_mod.DIR / "notas":
        raise cli.FactoryError(f"{nota} no es una nota de kb/notas/; no marqué nada")
    fuentes = kb_mod.fuentes_de(ruta)
    huellas_ = {f: kb_mod.huella_de_fuente(cli, f) for f in fuentes}
    faltan = [f for f, h in huellas_.items() if h is None]
    if faltan:
        raise cli.FactoryError(f"{nota}: su fuente {', '.join(faltan)} no existe; corregí la nota antes de marcarla revisada")
    todas = kb_mod.huellas(cli)
    todas[relativa.as_posix()] = {"fuentes": huellas_, "revisada_por": cli.actor()["actor"], "cuando": cli.ahora()}
    cli.escribir_atomico(kb_mod.ruta_huellas(cli),
                     (json.dumps(todas, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    print(f"{nota} revisada por {cli.actor()['actor']}" + (f", con sus fuentes {', '.join(fuentes)}." if fuentes else " (no declara fuentes)."))


def tocados_por(identificador: str, estado: dict) -> set[str]:
    """Lo que un cambio abierto tocó: los archivos de sus commits, lo que no se commiteó si es el cambio de este checkout
    (el que tomaría un commit nuevo), sus requisitos y su ID."""
    archivos = cli.archivos_de(c["sha"] for c in cli.commits_del_cambio(identificador, estado))
    if cli.cambio_del_commit("") == identificador:
        archivos |= cli.nombres(["git", "diff", "--name-only", "-z", "HEAD"])
        archivos |= cli.nombres(["git", "ls-files", "-z", "--others", "--exclude-standard"])
    return archivos | set(estado.get("requisitos") or []) | {identificador}


def nombres(comando: list[str]) -> set[str]:
    """Las rutas de una salida de git con -z (una ruta puede tener espacios)."""
    return {n for n in cli.ejecutar(comando).stdout.split("\0") if n}


def archivos_de(commits) -> set[str]:
    salida: set[str] = set()
    for sha in commits:
        salida |= cli.nombres(["git", "show", "-z", "--name-only", "--format=", sha])
    return salida


def aviso_notas(identificador: str, estado: dict) -> list[str]:
    if estado.get("fase") in ("cerrada", "abandonada") or not (cli.ROOT / kb_mod.DIR / "notas").is_dir():
        return []
    tocados = cli.tocados_por(identificador, estado)
    return [f"la nota {n['nota']} está por revisar: este cambio tocó {', '.join(sorted(set(n['cambiaron']) & tocados))}; "
            f"marcala con oracle-factory kb revisada {n['nota']}"
            for n in kb_mod.estado_de_notas(cli) if set(n["cambiaron"]) & tocados]


def por_que(referencia: str, como_json: bool) -> None:
    """Del commit que escribió una línea a su cambio, sus requisitos, decisiones, riesgos, hallazgos y notas."""
    m = re.fullmatch(r"(.+):(\d+)", referencia or "")
    relativa = cli.carpeta_relativa(m[1]) if m else None
    if not m or relativa is None or not (cli.ROOT / relativa).is_file():
        raise cli.FactoryError("por-que espera ARCHIVO:LÍNEA de un archivo del proyecto (por ejemplo oracle_factory/cli.py:120)")
    archivo, linea = relativa.as_posix(), int(m[2])
    p = cli.ejecutar(["git", "blame", "--porcelain", "-L", f"{linea},{linea}", "--", archivo])
    if p.returncode or not p.stdout:
        raise cli.FactoryError(f"git no pudo decir quién escribió {archivo}:{linea}: {(p.stderr or '').strip()[:200]}")
    sha_ = p.stdout.split()[0]
    if set(sha_) == {"0"}:
        datos = {"esquema": "oracle-factory.por-que/1", "archivo": archivo, "linea": linea, "commit": None, "cambio": None}
        return cli.imprimir_json(datos) if como_json else print(f"{archivo}:{linea} todavía no está en un commit.")
    l = cli.ejecutar(["git", "log", "-1", "--format=%H%x1f%an%x1f%aI%x1f%s%x1f%(trailers:key=Cambio,valueonly,separator=%x20)", sha_])
    completo_, autor, fecha, asunto, trailer = (l.stdout.rstrip("\n").split("\x1f") + [""] * 5)[:5]
    commit = {"sha": completo_, "corto": completo_[:7], "autor": autor, "fecha": fecha, "asunto": asunto}
    cambios = {i: e for i, e in kb_mod.cambios_del_proyecto(cli)}
    ident = next((t for t in trailer.split() if t in cambios), None)
    union = "trailer" if ident else None
    if not ident:  # sin trailer: el cambio cuyos commits (de sus candidatos o su merge) lo contienen
        ident = next((i for i, e in cambios.items() if any(c["sha"] == completo_ for c in cli.commits_del_cambio(i, e))), None)
        union = "deducido" if ident else None
    if not ident:  # integrado sin merge (fast-forward, squash): el tramo desde que se creó su propuesta hasta su último candidato
        ident = next((i for i in cambios if cli.dentro_del_tramo(i, cambios[i], completo_)), None)
        union = "deducido por su tramo" if ident else None
    notas = [n["nota"] for n in kb_mod.estado_de_notas(cli) if archivo in n["fuentes"]]
    datos = {"esquema": "oracle-factory.por-que/1", "archivo": archivo, "linea": linea, "commit": commit, "cambio": None,
             "notas": notas}
    if ident:
        e = cambios[ident]
        v = kb_mod.veredictos(cli.ROOT, e.get("oracle"))
        decisiones = [{"accion": x.get("accion"), "actor": x.get("actor"), "tipo_actor": x.get("tipo_actor"),
                       "cuando": x.get("cuando"), "decision": x.get("decision"), "motivo": motivo}
                      for x, motivo in kb_mod.decisiones(e)]
        hallazgos = [{"revisor": i["revisor"], "candidato": i["candidato"], "severidad": h.get("severity"), "titulo": h.get("title")}
                     for i in tablero_mod.informes(cli.ROOT, cli.ROOT / estructura.DIR / "cambios" / ident)
                     for h in i["hallazgos"] if isinstance(h.get("location"), dict) and h["location"].get("file") == archivo]
        datos["cambio"] = {"id": ident, "titulo": e.get("titulo"), "fase": e.get("fase"), "union": union,
                           "requisitos": [{"id": r, "veredicto": v.get(r, "sin juicio")} for r in e.get("requisitos") or []],
                           "decisiones": decisiones,
                           "riesgos_aceptados": [{"titulo": a.get("titulo"), "actor": a.get("actor"), "motivo": a.get("motivo")}
                                                 for a in e.get("aceptados") or [] if a.get("archivo") == archivo],
                           "hallazgos": hallazgos}
    if como_json:
        return cli.imprimir_json(datos)
    print(f"{archivo}:{linea} — commit {commit['corto']} de {autor} ({fecha[:10]}): {asunto}")
    c = datos["cambio"]
    if not c:
        print("Esa línea no es de ningún cambio de Factory: su commit no lleva «Cambio:» ni está entre los de un cambio.")
    else:
        print(f"Cambio {c['id']} ({c['union']}) — {c['titulo']} [{c['fase']}]")
        if c["union"] == "deducido por su tramo":
            print("  (deducido porque el commit cae entre la propuesta y un candidato del cambio, sin «Cambio:»: puede ser otro trabajo de ese tiempo)")
        for r in c["requisitos"]:
            print(f"  requisito {r['id']}: {r['veredicto']}")
        for d in c["decisiones"]:
            print(f"  {cli._fecha_corta(d['cuando'])} {kb_mod.NOMBRES.get(d['accion'], d['accion'])} — {d['actor']} ({d['tipo_actor']})"
                  + (f": {d['decision']}" if d["decision"] else "") + (f" — {d['motivo']}" if d["motivo"] else ""))
        for a in c["riesgos_aceptados"]:
            print(f"  riesgo aceptado en este archivo: {a['titulo']} — {a['actor']}: {a['motivo']}")
        for h in c["hallazgos"]:
            print(f"  hallazgo de {h['revisor']} ({h['severidad']}) sobre el candidato {h['candidato']}: {h['titulo']}")
    for n in notas:
        print(f"  nota: {n}")


def dentro_del_tramo(identificador: str, estado: dict, sha: str) -> bool:
    """Si un commit sin trailer cae en el tramo de un cambio: después del commit que creó su propuesta y antes de alguno
    de sus candidatos. Es una deducción: un commit ajeno hecho en esa rama en ese tiempo también cae, y por eso la unión
    dice «por su tramo» (con el hook, los commits nuevos llevan su trailer y no llegan acá)."""
    candidatos = [c["sha"] for c in cli.commits_del_cambio(identificador, estado) if c["candidato"]]
    alta = cli.ejecutar(["git", "log", "--diff-filter=A", "--format=%H", "--", f"openspec/changes/{identificador}/proposal.md"]).stdout.split()
    if not candidatos or not alta:
        return False
    es = lambda a, b: cli.ejecutar(["git", "merge-base", "--is-ancestor", a, b]).returncode == 0
    return es(alta[-1], sha) and any(es(sha, c) for c in candidatos)


def _fecha_corta(cuando) -> str:
    return str(cuando or "")[:16].replace("T", " ")


def actualizar_resumen() -> None:
    """Después de cerrar o archivar: si falla, lo cerrado ya está hecho y `resumen` lo repara."""
    try:
        cli.escribir_atomico(cli.ruta_resumen(), cli.texto_resumen().encode("utf-8"))
    except Exception as e:  # noqa: BLE001 — el cierre ya está hecho; cualquier falla del resumen sólo se avisa
        print(f"Aviso: no pude actualizar el resumen ({type(e).__name__}: {e}); corré oracle-factory resumen.", file=sys.stderr)


def datos_estado(identificador: str) -> dict:
    """Lo que muestra `estado`, como datos con esquema versionado; no pregunta ni escribe nada."""
    carpeta, estado = cli.leer(identificador)
    abandonado = estado.get("fase") == "abandonada"
    try:
        actual = None if abandonado else cli.contexto_producto()
    except (cli.FactoryError, OSError):
        actual = None
    medido_por: dict[str, list[str]] = {}
    if not abandonado and estado.get("requisitos"):
        try:
            requisitos, _, _ = cli.inventario_medidas(estado)
            medido_por = {rid: list(r.medido_por) for rid, r in requisitos.items()}
        except (ValueError, OSError, cli.FactoryError):
            pass  # un requisito o catálogo que Oracle rechaza: las medidas quedan vacías y pendientes lo dice

    def gate(registro: dict | None, campos: tuple, vigente: bool) -> dict | None:
        if not registro:
            return None
        return {**{c: registro.get(c) for c in campos}, "head": (registro.get("contexto") or {}).get("head"),
                "cuando": registro.get("cuando"), "vigente": vigente}

    pendientes_medidas = estado.get("medidas_pendientes") or {}
    return {
        "esquema": cli.ESQUEMA_ESTADO, "id": estado["id"], "titulo": estado.get("titulo", ""), "fase": estado.get("fase"),
        "modo": cli.modo_de(estado), "capacidad": estado.get("capacidad"),
        "candidato": None if abandonado else cli.candidato_vigente(identificador),
        "requisitos": [{"id": rid, "tipo": (estado.get("tipos") or {}).get(rid, "funcional"), "medidas": medido_por.get(rid, []),
                        "decision": cli._decision((estado.get("medidas") or {}).get(rid)),
                        "propuesta": cli._decision(None if (pendientes_medidas.get(rid) or {}).get("descartada")
                                               else pendientes_medidas.get(rid))}
                       for rid in estado.get("requisitos") or []],
        "pendientes": [] if abandonado else cli.pendientes_actuales(carpeta, estado),
        "proximo_paso": (todos := cli.pasos(identificador) or [None])[0], "alternativas": todos[1:],
        "decisiones": {"spec": cli._decision(estado.get("spec_aprobada")), "revision": cli._decision(estado.get("revision")),
                       "cierre": cli._decision(estado.get("cierre")), "abandono": cli._decision(estado.get("abandono"))},
        # Vigencia con las mismas reglas que estado en texto y proximo_paso.
        "revision": gate(estado.get("revision"), ("decision", "hallazgos_abiertos", "revisor", "formato", "informe"),
                         actual is not None and cli.mismo_producto((estado.get("revision") or {}).get("contexto"), actual)
                         and not cli.problemas_de_revision(estado)),
        "oracle": gate(estado.get("oracle"), ("codigo", "informe", "hechos", "hechos_mas"),
                       cli.juicio_vigente(estado.get("oracle") or {}, actual)),
        "aceptados": estado.get("aceptados") or [],
        "avisos": cli.aviso_union(identificador, estado) if abandonado else (cli.avisos_head(estado) + cli.aviso_revision(estado) + cli.aviso_lanzamientos(estado)
                                         + cli.aviso_sin_autor(estado) + cli.aviso_sin_medir(identificador, estado)
                                         + cli.aviso_notas(identificador, estado) + cli.aviso_union(identificador, estado)),
        "commits": cli.commits_del_cambio(identificador, estado),
        "quien": cli.quien_del_cambio(estado),
    }


def datos_donde(identificador: str, candidato: str | None) -> dict:
    _, estado = cli.leer(identificador)
    return {"esquema": cli.ESQUEMA_DONDE, "id": estado["id"], "titulo": estado.get("titulo", ""), "candidato": candidato,
            "artefactos": [{"gate": fila["gate"], "ruta": fila["ruta"], "nota": fila["nota"] or None,
                            "situacion": ("no_valido" if fila.get("invalida") else "historico" if fila["gate"] == "histórico"
                                          else "existe" if fila["existe"] else "ausente")}
                           for fila in estructura.donde(cli.ROOT, identificador, estado, candidato, cli.oracle_rel())]}


def datos_trazabilidad(identificador: str, base: str | None = None) -> dict:
    """La trazabilidad del candidato vigente: lo que dejó el sensor, cruzado con el diff contra la base."""
    cli.leer(identificador)
    sha = cli.candidato_vigente(identificador)
    if sha is None:
        raise cli.FactoryError("no hay candidato vigente: hace falta un commit con su carpeta de candidato y sin cambios de "
                           f"producto después; producí la evidencia con oracle-factory ruta {identificador} evidencia")
    ruta = estructura.ruta_canonica(cli.ROOT, identificador, "evidencia", sha) / "trazabilidad.json"
    if not cli.ruta_segura(ruta).is_file():
        raise cli.FactoryError(f"no hay trazabilidad del candidato {sha}: el sensor la deja en {ruta.relative_to(cli.ROOT)} con "
                           "oracle_factory.trazabilidad.trazar (ver docs/trazabilidad.md)")
    trazas = json.loads(ruta.read_text(encoding="utf-8"))
    if not isinstance(trazas, dict) or trazas.get("esquema") != trazabilidad_mod.ESQUEMA_CASOS:
        raise cli.FactoryError(f"{ruta.relative_to(cli.ROOT)} no es una trazabilidad de casos ({trazabilidad_mod.ESQUEMA_CASOS})")
    candidato = cli.ejecutar(["git", "rev-parse", sha]).stdout.strip()
    # La base es la del candidato (no la de HEAD), como el paquete de pedir-revision; --base la cambia.
    p = cli.ejecutar(["git", "merge-base", candidato, base or "main"])
    if p.returncode:
        raise cli.FactoryError(f"no encuentro la base del diff ({base or 'main'}): indicá otra con --base REF")
    base = p.stdout.strip()
    # Nombres exactos (-z, sin comillas ni tabuladores) y renombres detectados: un archivo movido no es uno nuevo entero.
    lista = cli.ejecutar(["git", "diff", "--name-status", "-z", "-M", base, candidato])
    if lista.returncode:
        raise cli.FactoryError(f"git diff falló: {lista.stderr.strip()[:300]}")
    cambios, borrados, ejecutables = {}, [], {}
    for archivo in trazabilidad_mod.archivos_cambiados(lista.stdout):
        if not cli.es_producto(archivo["ruta"]):
            if archivo["origen"] and cli.es_producto(archivo["origen"]):
                borrados.append(archivo["origen"])  # movido fuera del producto: para el producto, se borró
            continue
        if archivo["estado"] == "D":
            borrados.append(archivo["ruta"])
            continue
        rutas = [archivo["origen"], archivo["ruta"]] if archivo["origen"] else [archivo["ruta"]]
        diff = cli.ejecutar(["git", "diff", "-U0", "-M", "--no-color", base, candidato, "--", *rutas])
        cambios[archivo["ruta"]] = trazabilidad_mod.lineas_agregadas(diff.stdout)
        # El archivo como está en el candidato, no en el árbol de trabajo.
        texto = cli.ejecutar(["git", "show", f"{candidato}:{archivo['ruta']}"]) if archivo["ruta"].endswith(".py") else None
        ejecutables[archivo["ruta"]] = (trazabilidad_mod.lineas_ejecutables(texto.stdout)
                                        if texto is not None and not texto.returncode else None)
    return {"esquema": trazabilidad_mod.ESQUEMA, "id": identificador, "candidato": sha, "base": base,
            "trazabilidad": ruta.relative_to(cli.ROOT).as_posix(),
            **trazabilidad_mod.cruzar(trazas, cambios, ejecutables, borrados)}


def comando_trazabilidad(identificador: str, como_json: bool, base: str | None = None) -> None:
    datos = cli.datos_trazabilidad(identificador, base)
    if como_json:
        cli.imprimir_json(datos)
        return
    print(f"{identificador} · candidato {datos['candidato']} contra la base {datos['base'][:7]}")
    for rid, r in datos["requisitos"].items():
        print(f"\n{rid}")
        print("  Casos: " + (", ".join(f"{c['caso']} ({c['resultado']})" for c in r["casos"]) or "ninguno"))
        for archivo, lineas in r["lineas"].items():
            print(f"  {archivo}: {cli.rangos(lineas)}")
        if not r["lineas"]:
            print("  Ninguna línea cambiada ejecutada por sus casos.")
    print("\nSin respaldo (líneas cambiadas que no ejecuta ningún caso del contrato):")
    for archivo, lineas in datos["sin_respaldo"].items():
        print(f"  {archivo}: {cli.rangos(lineas)}")
    if not datos["sin_respaldo"]:
        print("  ninguna")
    if datos["al_importar"]:
        print("Corren al importar (antes de los casos; sin decir si tienen respaldo):")
        for archivo, lineas in datos["al_importar"].items():
            print(f"  {archivo}: {cli.rangos(lineas)}")
    if datos["no_rastreables"]:
        print("No rastreables (no son Python o no compilan): " + ", ".join(datos["no_rastreables"]))
    if datos["borrados"]:
        print("Borrados: " + ", ".join(datos["borrados"]))
    for limite in datos["limites"]:
        print(f"Límite: {limite}.")


def rangos(lineas: list[int]) -> str:
    """[3, 4, 5, 9] → «3-5, 9»."""
    partes, inicio = [], None
    for i, n in enumerate(lineas):
        if inicio is None:
            inicio = n
        if i + 1 == len(lineas) or lineas[i + 1] != n + 1:
            partes.append(str(inicio) if inicio == n else f"{inicio}-{n}")
            inicio = None
    return ", ".join(partes)


def comando_donde(identificador: str, candidato: str | None) -> None:
    _, estado = cli.leer(identificador)
    print(f"{estado['id']} — {estado['titulo']}" + (f" (candidato {candidato})" if candidato else ""))
    for fila in estructura.donde(cli.ROOT, identificador, estado, candidato, cli.oracle_rel()):
        marca = ("no válido" if fila.get("invalida") else "histórico" if fila["gate"] == "histórico"
                 else "existe" if fila["existe"] else "AUSENTE")
        print(f"{fila['gate']:<10} {marca:<9} {fila['ruta']}" + (f"  — {fila['nota']}" if fila["nota"] else ""))


# Al final a propósito: `cli` importa este módulo, y así se puede importar cualquiera de los dos primero. Acá `cli` sólo se usa
# cuando se llama a una función, no al importar.
from . import cli  # noqa: E402
