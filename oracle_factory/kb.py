"""El conocimiento del proyecto: `kb/` generado desde el registro, y notas humanas que vencen cuando cambian sus fuentes.

Las notas generadas (`kb/README.md`, `kb/cambios/`, `kb/requisitos/`) no se editan a mano: su texto sale del registro y
no depende de cuándo se genera, así que `kb --verificar` las compara byte a byte. Las notas humanas viven en
`kb/notas/` y declaran sus `fuentes:`; la huella de cada fuente, del momento en que una persona la marcó revisada, va en
`.factory/kb.json`.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

DIR = "kb"
MARCA = "generado: oracle-factory kb"
AVISO = "> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano."
DECIDE = ("decidio", "confirmo")
NOMBRES = {"cambio_creado": "Cambio creado", "spec_aprobada": "Spec aprobada", "spec_aceptada_en_conversacion": "Spec aceptada en la conversación",
           "requisitos_importados": "Requisitos importados", "medidas_confirmadas": "Medidas confirmadas",
           "medidas_elegidas": "Medidas elegidas", "revision_registrada": "Revisión registrada", "oracle_ejecutado": "Juicio de Oracle",
           "cierre": "Cerrado", "abandono": "Abandonado", "archivado": "Archivado"}


def sha(datos: bytes) -> str:
    return hashlib.sha256(datos).hexdigest()


def _texto(valor) -> str:
    """Un texto del registro (título, mensaje, motivo) en una sola línea y sin sintaxis de Markdown: no puede abrir
    un encabezado, una viñeta ni un enlace que parezca del registro."""
    return re.sub(r"([\\`*_\[\]#<>|!~])", r"\\\1", " ".join(str(valor or "").split()))


def _fecha(cuando) -> str:
    return str(cuando or "")[:16].replace("T", " ")


def _requisito(texto: str) -> dict:
    """Los campos de un .requisito: texto, fuente y medido_por (o sin_medir)."""
    campo = lambda k: (re.search(rf'^\s+{k} "((?:[^"\\]|\\.)*)"', texto, re.M) or [None, None])[1]
    medido = re.search(r"^\s+medido_por (.+)$", texto, re.M)
    return {"texto": campo("texto") or "", "fuente": campo("fuente"), "sin_medir": campo("sin_medir"),
            "medidas": [m.strip() for m in medido[1].split(",")] if medido else []}


def veredictos(raiz: Path, oracle: dict | None) -> dict[str, str]:
    """Del informe de Oracle registrado: cumple, no cumple o sin juicio, por requisito."""
    informe = (oracle or {}).get("informe")
    if not isinstance(informe, str) or not (raiz / informe).is_file():
        return {}
    salida = {}
    for linea in (raiz / informe).read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^([✓✗?◐·])\s+(\S+)\s", linea)
        if m:
            salida[m[2]] = {"✓": "cumple", "✗": "no cumple"}.get(m[1], "sin juicio")
    return salida


def _encabezado(campos: dict) -> str:
    return "---\n" + MARCA + "\n" + "".join(f"{k}: {json.dumps(v, ensure_ascii=False)}\n" for k, v in campos.items()) + "---\n"


def decisiones(estado: dict) -> list[tuple[dict, str | None]]:
    """Las decisiones del registro (decidió o confirmó), cada una con su motivo: el del evento si lo trae, o el de su
    sección del registro para la última de su tipo (la revisión, el abandono, el cierre, las medidas de un requisito)."""
    eventos = [e for e in estado.get("eventos") or [] if e.get("forma") in DECIDE]
    seccion = {"revision_registrada": (estado.get("revision") or {}).get("motivo"),
               "abandono": (estado.get("abandono") or {}).get("motivo"), "cierre": (estado.get("cierre") or {}).get("motivo")}
    ultimos = {e.get("accion"): e for e in eventos}
    ultimos_medidas = {e.get("requisito"): e for e in eventos if e.get("accion") in ("medidas_confirmadas", "medidas_elegidas")}
    salida = []
    for e in eventos:
        motivo = e.get("motivo")
        if not motivo and ultimos.get(e.get("accion")) is e:
            motivo = seccion.get(e.get("accion"))
        if not motivo and ultimos_medidas.get(e.get("requisito")) is e:
            motivo = ((estado.get("medidas") or {}).get(e.get("requisito")) or {}).get("motivo")
        salida.append((e, motivo if isinstance(motivo, str) and motivo.strip() else None))
    return salida


def nota_de_cambio(cli, ident: str, estado: dict) -> str:
    raiz = cli.ROOT
    v = veredictos(raiz, estado.get("oracle"))
    r = estado.get("responsable") or {}
    lineas = [_encabezado({"id": ident, "fase": estado.get("fase"), "capacidad": estado.get("capacidad")}),
              f"# {_texto(estado.get('titulo') or ident)}", "", AVISO, "",
              f"- Fase: {estado.get('fase')}", f"- Capacidad: {estado.get('capacidad') or '—'}",
              f"- Responsable: {_texto(r['persona']) + ' desde ' + _fecha(r.get('desde')) if r.get('persona') else 'nadie'}"]
    if estado.get("spec"):
        lineas.append(f"- Spec: [{estado['spec']}](../../{estado['spec']})")
    lineas += ["", "## Requisitos", ""]
    lineas += [f"- [[requisitos/{rid}]] — {v.get(rid, 'sin juicio')}" for rid in sorted(estado.get("requisitos") or [])] or ["- Ninguno importado."]
    lineas += ["", "## Decisiones", ""]
    tomadas = decisiones(estado)
    for e, motivo in tomadas:
        extra = f" — {_texto(e.get('decision'))}" if e.get("decision") else ""
        if motivo:
            extra += f"{':' if extra else ' —'} {_texto(motivo)}"
        lineas.append(f"- {_fecha(e.get('cuando'))} · {NOMBRES.get(e.get('accion'), _texto(e.get('accion')))} · "
                      f"{_texto(e.get('actor'))} ({_texto(e.get('tipo_actor'))}){extra}")
    if not tomadas:
        lineas.append("- Ninguna todavía.")
    lineas += ["", "## Riesgos aceptados", ""]
    lineas += [f"- `{' '.join(str(a.get('archivo') or '').replace('`', "'").split())}`: {_texto(a.get('titulo'))} — aceptado por {_texto(a.get('actor'))}: {_texto(a.get('motivo'))}"
               for a in estado.get("aceptados") or []] or ["- Ninguno."]
    lineas += ["", "## Commits", ""]
    # Hasta el cierre o, en uno abierto, hasta su última decisión: un commit nuevo entra con la decisión siguiente (que es
    # cuando el vault se rehace), y el merge que lo integra después no lo cambia. Sólo los que llevan su trailer y sus
    # candidatos: los que se deducen de un merge aparecen recién al integrarlo.
    eventos = estado.get("eventos") or []
    corte = str((estado.get("cierre") or {}).get("cuando") or (eventos[-1].get("cuando") if eventos else "") or "")
    if estado.get("fase") == "abandonada":
        lineas.append(f"- Abandonado: `oracle-factory log {ident}`.")
    else:
        commits = [c for c in cli.commits_del_cambio(ident, estado) if (c["union"] == "trailer" or c["candidato"])
                   and (not corte or _antes(c["fecha_commit"], corte))]  # cuándo entró, no la fecha de autor (cherry-pick)
        lineas += [f"- `{c['corto']}` {_texto(c['asunto'])} ({c['union']})" for c in sorted(commits, key=lambda c: (c["fecha"], c["sha"]))] \
            or ["- Ninguno con su trailer ni candidato."]
        lineas.append(f"- Todos, también los que se deducen al integrarlo o los posteriores a la última decisión: `oracle-factory log {ident}`.")
    mensajes = [e for e in estado.get("eventos") or [] if e.get("accion") == "mensaje"]
    lineas += ["", "## Mensajes", ""]
    lineas += [f"- {_fecha(e.get('cuando'))} · {_texto(e.get('actor'))}: {_texto(e.get('texto'))}" for e in mensajes] or ["- Ninguno."]
    return "\n".join(lineas) + "\n"


def _antes(fecha: str, cierre: str) -> bool:
    from datetime import datetime
    try:
        # Estricto: un commit del mismo segundo que la decisión pudo hacerse después de rehacer el vault.
        return datetime.fromisoformat(fecha) < datetime.fromisoformat(cierre)
    except (TypeError, ValueError):
        return True


def nota_de_requisito(rid: str, datos: dict, cambio: dict | None, veredicto: str | None, vigente: bool) -> str:
    lineas = [_encabezado({"id": rid, "vigente": vigente}), f"# {rid.split('.', 1)[-1].replace('_', ' ')}", "", AVISO, "",
              f"- Id: `{rid}`", f"- Vigente: {'sí' if vigente else 'no (ya no está en requisitos/)'}",
              f"- Cambio: [[cambios/{cambio['id']}]]" if cambio else "- Cambio: ninguno registrado",
              f"- Veredicto: {veredicto or 'sin juicio'}",
              f"- Medidas: {', '.join(f'`{m}`' for m in datos['medidas']) or 'ninguna'}"]
    if datos.get("sin_medir"):
        lineas.append(f"- Sin medir: {datos['sin_medir']}")
    if datos.get("fuente"):
        lineas.append(f"- Fuente: {datos['fuente']}")
    lineas += ["", datos["texto"] or "(sin texto)"]
    return "\n".join(lineas) + "\n"


def cambios_del_proyecto(cli) -> list[tuple[str, dict]]:
    if not cli.CHANGES.is_dir():
        return []
    return [(c.name, cli.leer(c.name)[1]) for c in sorted(cli.CHANGES.iterdir())
            if cli.ID_RE.fullmatch(c.name) and cli.ruta_registro(c).exists()]


def armar(cli, solo: str | None = None) -> dict[str, str]:
    """Las notas generadas, {ruta relativa a la raíz: texto}. Con `solo`, sólo las de ese cambio, sus requisitos y el índice."""
    raiz = cli.ROOT
    cambios = cambios_del_proyecto(cli)
    req_dir = cli.requisitos_dir()
    vigentes = {p.stem: p for p in req_dir.glob("*.requisito")} if req_dir.is_dir() else {}
    de_cambio: dict[str, tuple[str, dict]] = {}
    for ident, estado in cambios:
        for rid in estado.get("requisitos") or []:
            de_cambio.setdefault(rid, (ident, estado))  # el que lo trajo: los cambios van en orden de creación
    salida: dict[str, str] = {}
    for ident, estado in cambios:
        if solo is None or ident == solo:
            salida[f"{DIR}/cambios/{ident}.md"] = nota_de_cambio(cli, ident, estado)
    for rid in sorted(set(vigentes) | set(de_cambio)):
        dueño = de_cambio.get(rid)
        if solo is not None and (not dueño or dueño[0] != solo):
            continue
        texto = vigentes[rid].read_text(encoding="utf-8") if rid in vigentes else ""
        veredicto = veredictos(raiz, dueño[1].get("oracle")).get(rid) if dueño else None
        salida[f"{DIR}/requisitos/{rid}.md"] = nota_de_requisito(rid, _requisito(texto), {"id": dueño[0]} if dueño else None,
                                                                 veredicto, rid in vigentes)
    indice = [_encabezado({}), "# Conocimiento del proyecto", "", AVISO,
              "Las notas de personas van en `notas/` y declaran sus `fuentes:`; `oracle-factory kb --verificar` avisa las que vencieron.",
              "", "## Cambios", ""]
    indice += [f"- [[cambios/{i}]] — {_texto(e.get('titulo') or i)} ({e.get('fase')})" for i, e in cambios] or ["- Ninguno."]
    indice += ["", "## Requisitos", ""]
    indice += [f"- [[requisitos/{rid}]]{'' if rid in vigentes else ' (ya no vigente)'}" for rid in sorted(set(vigentes) | set(de_cambio))] \
        or ["- Ninguno."]
    salida[f"{DIR}/README.md"] = "\n".join(indice) + "\n"
    return salida


# --- notas humanas -----------------------------------------------------------------------------------------------
def _fuentes_crudas(nota: Path) -> list[str]:
    """Las fuentes del frontmatter de una nota: `fuentes: [a, b]` o una lista con guiones."""
    texto = nota.read_text(encoding="utf-8", errors="replace")
    if not texto.startswith("---\n") or "\n---" not in texto[4:]:
        return []
    cabeza = texto[4:texto.index("\n---", 4)]
    m = re.search(r"^fuentes:\s*\[(.*)\]\s*$", cabeza, re.M)
    if m:
        return [x.strip().strip("'\"") for x in m[1].split(",") if x.strip()]
    m = re.search(r"^fuentes:[ \t]*\n((?:[ \t]*-\s.*\n?)+)", cabeza + "\n", re.M)
    return [x.strip()[1:].strip().strip("'\"") for x in m[1].splitlines() if x.strip()] if m else []


def fuentes_de(nota: Path) -> list[str]:
    """Las fuentes del frontmatter de una nota: `fuentes: [a, b]` o una lista con guiones; `./x` es `x`."""
    return [f[2:] if f.startswith("./") else f for f in _fuentes_crudas(nota)]


def huella_de_fuente(cli, fuente: str) -> str | None:
    """La huella de una fuente: un archivo (su contenido), un requisito (su .requisito) o un cambio (su spec)."""
    raiz = cli.ROOT
    archivo = cli.requisitos_dir() / f"{fuente}.requisito"
    adentro = lambda ruta: ruta.resolve().is_relative_to(raiz.resolve())  # un enlace simbólico tampoco sale del proyecto
    if re.fullmatch(r"[a-z0-9_]+\.[a-z0-9_]+", fuente) and archivo.is_file() and adentro(archivo):  # un id: no sale de requisitos/
        return sha(archivo.read_bytes())
    if cli.ID_RE.fullmatch(fuente) and cli.ruta_registro(cli.CHANGES / fuente).exists():
        # Lo que se sabe del cambio, como lo muestra su nota generada: decisiones, riesgos, fase, requisitos, mensajes.
        return sha(nota_de_cambio(cli, fuente, cli.leer(fuente)[1]).encode("utf-8"))
    relativa = cli.carpeta_relativa(fuente)
    if relativa is not None and (raiz / relativa).is_file() and adentro(raiz / relativa):
        return sha((raiz / relativa).read_bytes())
    return None


def ruta_huellas(cli) -> Path:
    return cli.ROOT / ".factory" / "kb.json"


def huellas(cli) -> dict:
    ruta = ruta_huellas(cli)
    try:
        return json.loads(ruta.read_text(encoding="utf-8")) if ruta.is_file() else {}
    except ValueError:
        return {}


def estado_de_notas(cli) -> list[dict]:
    """Cada nota humana: sus fuentes, cuáles faltan y cuáles cambiaron desde que se marcó revisada."""
    raiz = cli.ROOT
    guardadas = huellas(cli)
    salida = []
    for nota in sorted((raiz / DIR / "notas").glob("*.md")) if (raiz / DIR / "notas").is_dir() else []:
        rel = nota.relative_to(raiz).as_posix()
        fuentes = fuentes_de(nota)
        previas = (guardadas.get(rel) or {}).get("fuentes") or {}
        faltan, cambiaron = [], []
        for f in fuentes:
            h = huella_de_fuente(cli, f)
            if h is None:
                faltan.append(f)
            elif previas.get(f) != h:
                cambiaron.append(f)
        salida.append({"nota": rel, "fuentes": fuentes, "faltan": faltan, "cambiaron": cambiaron,
                       "revisada": guardadas.get(rel, {}).get("revisada_por")})
    return salida
