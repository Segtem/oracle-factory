"""El tablero de comando: todo lo de cada cambio abierto y las métricas del proyecto, en un JSON versionado.

Sólo lee lo que la CLI ya sabe —el registro de cada cambio, sus informes de revisión y lo que devuelven `estado` y
`donde`—; no decide ni escribe nada. Las métricas se cuentan de los eventos, así que también valen para los cerrados.
"""
from __future__ import annotations

from datetime import datetime
import json
import re
from pathlib import Path
from statistics import median

ESQUEMA = "oracle-factory.tablero/1"
# Las decisiones que espera una persona: el tablero las pone arriba.
DECISIONES = ("aprobar-spec", "medir", "revisar", "cerrar", "abandonar")
# La fase en la que entra un cambio con cada hito; con el cierre sale de todas.
FASES = {"creado": "acuerdo", "spec": "medidas", "medidas": "construcción y revisión", "revision": "juicio",
         "juicio": "cierre"}
FORMAS_DE_DECIDIR = ("decidio", "confirmo")
SEVERIDADES = ("critica", "alta", "media", "baja", "informativa")


def _cuando(texto) -> datetime | None:
    try:
        return datetime.fromisoformat(str(texto))
    except ValueError:
        return None


def _horas(desde, hasta) -> float | None:
    a, b = _cuando(desde), _cuando(hasta)
    try:
        return round((b - a).total_seconds() / 3600, 2) if a and b else None
    except TypeError:  # un registro viejo sin zona horaria contra uno con zona: no se pueden comparar
        return None


def _hito(e: dict) -> str | None:
    accion = e.get("accion")
    if accion == "cambio_creado":
        return "creado"
    if accion in ("spec_aprobada", "spec_aceptada_en_conversacion"):
        return "spec"
    if accion in ("medidas_confirmadas", "medidas_elegidas"):
        return "medidas"
    if accion == "revision_registrada" and e.get("decision") == "aprobar":
        return "revision"
    if accion == "oracle_ejecutado" and e.get("codigo") == 0:
        return "juicio"
    return "cierre" if accion == "cierre" else None


def hitos(eventos: list[dict]) -> dict[str, str]:
    """Cuándo pasó cada hito del cambio por primera vez (el cierre, la última)."""
    hitos: dict[str, str] = {}
    for e in eventos:
        h = _hito(e)
        if h == "cierre":
            hitos["cierre"] = e.get("cuando")
        elif h:
            hitos.setdefault(h, e.get("cuando"))
    return hitos


def fases(eventos: list[dict]) -> list[dict]:
    """El tiempo en cada fase, sumando cada vez que el cambio estuvo en ella: si después de una revisión se vuelven a
    elegir medidas, el cambio vuelve a construcción y revisión, y ese tramo cuenta ahí. Sólo las fases de las que el
    cambio ya salió; un tramo con fechas que no se pueden comparar o que van hacia atrás no cuenta."""
    tramos: dict[str, dict] = {}
    actual = desde = None
    for e in eventos:
        h = _hito(e)
        if not h:
            continue
        if actual:
            horas = _horas(desde, e.get("cuando"))
            if horas is not None and horas >= 0:
                t = tramos.setdefault(actual, {"fase": actual, "desde": desde, "hasta": None, "horas": 0.0})
                t["hasta"], t["horas"] = e.get("cuando"), round(t["horas"] + horas, 2)
        actual, desde = FASES.get(h), e.get("cuando")
    return [tramos[f] for f in dict.fromkeys(FASES.values()) if f in tramos]


def informes(raiz: Path, carpeta_cambio: Path) -> list[dict]:
    """Cada informe de revisor de todos los candidatos del cambio: [{revisor, candidato, ruta, hallazgos}].

    Como en revision-preparar, el informe más nuevo de un revisor en un candidato (<revisor>-<n>.json) reemplaza a
    los anteriores del mismo revisor en ese candidato: los reemplazados no cuentan."""
    ultimo: dict[tuple, tuple[int, Path]] = {}
    for ruta in carpeta_cambio.glob("candidatos/*/revision/*.json"):
        m = re.fullmatch(r"(.+)-(\d+)\.json", ruta.name)
        clave = (ruta.parent, m[1] if m else ruta.stem)
        n = int(m[2]) if m else 0
        if clave not in ultimo or n > ultimo[clave][0]:
            ultimo[clave] = (n, ruta)
    salida = []
    for (_, revisor), (_, ruta) in sorted(ultimo.items(), key=lambda x: x[1][1]):
        try:
            datos = json.loads(ruta.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(datos, dict) or not isinstance(datos.get("findings"), list):
            continue
        salida.append({"revisor": revisor, "candidato": ruta.parent.parent.name,
                       "ruta": ruta.relative_to(raiz).as_posix(),
                       "hallazgos": [h for h in datos["findings"] if isinstance(h, dict)]})
    return salida


def _contar_severidades(hallazgos: list[dict]) -> dict[str, int]:
    cuenta = {s: 0 for s in SEVERIDADES}
    for h in hallazgos:
        s = h.get("severity") if h.get("severity") in SEVERIDADES else "informativa"
        cuenta[s] += 1
    return cuenta


def metricas_del_cambio(estado: dict, todos_los_informes: list[dict], cumplidos: int | None) -> dict:
    eventos = estado.get("eventos") or []
    h = hitos(eventos)
    actores = {"persona": 0, "agente": 0, "sin_identificar": 0}
    for e in eventos:  # sólo decisiones: no propuestas, registros de un revisor ni migraciones
        if e.get("forma") in FORMAS_DE_DECIDIR and e.get("tipo_actor") in actores:
            actores[e["tipo_actor"]] += 1
    por_revisor: dict[str, dict[str, int]] = {}
    for informe in todos_los_informes:
        cuenta = por_revisor.setdefault(informe["revisor"], {s: 0 for s in SEVERIDADES})
        for s, n in _contar_severidades(informe["hallazgos"]).items():
            cuenta[s] += n
    # Una vuelta por candidato al que se le pidieron revisores, más cada revisión registrada sin revisores pedidos desde
    # la anterior (una vuelta a mano: su evento no dice el candidato).
    pedidos, a_mano, desde_la_anterior = set(), 0, False
    for e in eventos:
        if e.get("accion") == "revision_pedida":
            pedidos.add(e.get("candidato"))
            desde_la_anterior = True
        elif e.get("accion") == "revision_registrada":
            a_mano += not desde_la_anterior
            desde_la_anterior = False
    vueltas = len(pedidos) + a_mano
    requisitos = estado.get("requisitos") or []
    medidos = sum(1 for rid in requisitos if (estado.get("medidas") or {}).get(rid))
    return {
        "fases": fases(eventos),
        "horas_hasta_cierre": _horas(h.get("creado"), h.get("cierre")),
        "vueltas_de_revision": vueltas,
        "hallazgos_por_severidad": _contar_severidades([x for i in todos_los_informes for x in i["hallazgos"]]),
        "hallazgos_por_revisor": por_revisor,
        "riesgos_aceptados": len(estado.get("aceptados") or []),
        "decisiones_por_actor": actores,
        "requisitos": {"total": len(requisitos), "medidos": medidos, "cumplidos": cumplidos},
    }


def _paso(texto: str | None) -> dict | None:
    if not texto:
        return None
    comando = texto if texto.startswith("oracle-factory ") else None
    partes = comando.split() if comando else []
    verbo = partes[1] if len(partes) > 1 else None
    # medir decide sólo con --confirmar; --listar muestra lo que hay para que un agente proponga
    decide = verbo in DECISIONES and (verbo != "medir" or "--confirmar" in partes)
    return {"texto": texto, "comando": comando, "decision_de_la_persona": decide}


def _cumplidos(raiz: Path, oracle: dict | None, requisitos: list[str]) -> int | None:
    """Cuántos requisitos marcó Oracle con ✓ en el último juicio registrado; None si no hubo juicio o no está vigente."""
    informe = (oracle or {}).get("informe")
    if (oracle or {}).get("vigente") is False:  # un juicio de otro producto u otros hechos ya no dice qué se cumple
        return None
    if not isinstance(informe, str) or not (raiz / informe).is_file():
        return None
    texto = (raiz / informe).read_text(encoding="utf-8", errors="replace")
    return sum(1 for rid in requisitos if re.search(r"^✓\s+" + re.escape(rid) + r"\s", texto, re.M))


def armar(cli) -> dict:
    """El JSON del tablero, con el módulo de la CLI ya apuntado al proyecto (ROOT)."""
    raiz = cli.ROOT
    cambios, cerrados_horas, totales = [], [], {"abiertos": 0, "cerrados": 0, "abandonados": 0}
    con_revision = en_una_vuelta = 0
    actores_proyecto = {"persona": 0, "agente": 0, "sin_identificar": 0}
    revisores_proyecto: dict[str, dict[str, int]] = {}
    carpetas = sorted(c for c in cli.CHANGES.iterdir() if cli.ID_RE.fullmatch(c.name)) if cli.CHANGES.exists() else []
    for carpeta in carpetas:
        if not cli.ruta_registro(carpeta).exists():
            continue
        ident = carpeta.name
        _, estado = cli.leer(ident)
        carpeta_estado = raiz / ".factory" / "cambios" / ident
        todos = informes(raiz, carpeta_estado)
        abierto = estado.get("fase") not in ("cerrada", "abandonada")
        datos = cli.datos_estado(ident) if abierto else None
        cumplidos = _cumplidos(raiz, (datos or {}).get("oracle") or estado.get("oracle"), estado.get("requisitos") or [])
        metricas = metricas_del_cambio(estado, todos, cumplidos)
        # Lo del proyecto
        totales["abiertos" if abierto else "cerrados" if estado.get("fase") == "cerrada" else "abandonados"] += 1
        if estado.get("fase") == "cerrada":
            if metricas["horas_hasta_cierre"] is not None:
                cerrados_horas.append(metricas["horas_hasta_cierre"])
            if metricas["vueltas_de_revision"]:
                con_revision += 1
                en_una_vuelta += metricas["vueltas_de_revision"] == 1
        for k, n in metricas["decisiones_por_actor"].items():
            actores_proyecto[k] += n
        for revisor, cuenta in metricas["hallazgos_por_revisor"].items():
            total = revisores_proyecto.setdefault(revisor, {s: 0 for s in SEVERIDADES})
            for s, n in cuenta.items():
                total[s] += n
        if not abierto:
            continue
        # Lo de cada cambio abierto
        sha = datos.get("candidato")
        firmas = {a.get("firma") for a in estado.get("aceptados") or []} - {None}
        hallazgos = []
        for informe in todos:
            if informe["candidato"] != sha:
                continue
            for h in informe["hallazgos"]:
                lugar = h.get("location") if isinstance(h.get("location"), dict) else {}
                archivo, titulo = lugar.get("file"), str(h.get("title") or "")
                hallazgos.append({
                    "revisor": informe["revisor"], "id": h.get("id"), "severidad": h.get("severity"), "titulo": titulo,
                    "archivo": archivo if isinstance(archivo, str) else None,
                    "linea": lugar.get("start_line") if isinstance(lugar.get("start_line"), int) else None,
                    "estado": "aceptado" if isinstance(archivo, str) and cli.preparacion.firma(archivo, titulo) in firmas
                    else "abierto",
                    "informe": informe["ruta"]})
        oracle_dir = cli.proyecto_oracle()
        requisitos = []
        for r in datos["requisitos"]:
            archivo = cli.requisitos_dir() / f"{r['id']}.requisito"
            medidas = []
            for m in r["medidas"]:
                catalogo = oracle_dir / "catalogos" / f"{m}.oracle"
                medidas.append({"id": m, "archivo": catalogo.relative_to(raiz).as_posix() if catalogo.is_file() else None})
            requisitos.append({"id": r["id"], "tipo": r["tipo"], "decision": r["decision"], "propuesta": r["propuesta"],
                               "archivo": archivo.relative_to(raiz).as_posix() if archivo.is_file() else None,
                               "medidas": medidas})
        cambios.append({
            "id": ident, "titulo": datos["titulo"], "fase": datos["fase"], "modo": datos["modo"],
            "capacidad": datos["capacidad"], "candidato": sha,
            "proximo_paso": _paso(datos["proximo_paso"]), "alternativas": [_paso(a) for a in datos["alternativas"]],
            "pendientes": datos["pendientes"], "avisos": datos["avisos"],
            "linea_de_tiempo": [{"cuando": e.get("cuando"), "accion": e.get("accion"), "actor": e.get("actor"),
                                 "tipo_actor": e.get("tipo_actor"), "forma": e.get("forma"),
                                 "detalle": {k: v for k, v in e.items()
                                             if k in ("revisor", "candidato", "resultado", "hallazgos", "decision",
                                                      "abiertos", "codigo", "requisito", "medidas", "causa")}}
                                for e in estado.get("eventos") or []],
            "hallazgos": hallazgos, "requisitos": requisitos,
            "commits": datos["commits"],
            "quien": datos["quien"],
            "artefactos": cli.datos_donde(ident, None)["artefactos"],
            "metricas": metricas,
        })
    return {
        "esquema": ESQUEMA,
        "cambios": cambios,
        "proyecto": {
            "cambios": totales,
            "mediana_horas_hasta_cierre": round(median(cerrados_horas), 2) if cerrados_horas else None,
            "primera_vuelta": {"cerrados_con_revision": con_revision, "en_una_vuelta": en_una_vuelta,
                               "proporcion": round(en_una_vuelta / con_revision, 3) if con_revision else None},
            "hallazgos_por_revisor": revisores_proyecto,
            "decisiones_por_actor": actores_proyecto,
            # Quién está en qué: los cambios abiertos por persona responsable, y los que no tienen.
            "por_responsable": {persona: [c["id"] for c in cambios if (c["quien"]["responsable"] or {}).get("persona") == persona]
                                for persona in sorted({c["quien"]["responsable"]["persona"] for c in cambios
                                                       if c["quien"]["responsable"]})},
            "sin_responsable": [c["id"] for c in cambios if not c["quien"]["responsable"]],
        },
    }
