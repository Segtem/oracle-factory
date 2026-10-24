"""Preguntar al conocimiento del proyecto: búsqueda híbrida (léxica, por embeddings y por el grafo del vault) sobre lo
vigente, con citas. El índice vive en .factory/local/rag/ y se pone al día solo; sólo guarda los embeddings, que es lo
caro de rehacer.

Sin dependencias: SQLite y HTTP de la biblioteca estándar. Recibe el módulo cli (como kb.armar) para leer el proyecto.
"""
from __future__ import annotations

from array import array
import fnmatch
import hashlib
import ipaddress
import contextlib
import json
import math
import os
from pathlib import Path
import re
import sqlite3
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

from . import kb as kb_mod

ESQUEMA = "oracle-factory.preguntar/2"
POR_DEFECTO = {"proveedor": "ollama", "url": "http://localhost:11434", "modelo": "qwen3-embedding:0.6b",
               # qwen3-embedding rinde mejor con la pregunta presentada como consulta (los pasajes van tal cual)
               "prefijo_pregunta": "Instruct: Given a question, retrieve passages that answer it\nQuery: "}
VACIAS = set("""a al algo ante con como cual cuando de del desde donde e el ella en entre es esta este esto la las le
lo los mas me mi muy ni no o otra otro para pero por que se si sin sobre su sus tambien te tiene un una uno unos y ya
hay ser son fue esta estan qu como cuál qué""".split())
TITULO = re.compile(r"^(#{1,3})\s+(.+?)\s*$")
ENLACE = re.compile(r"\[\[([^\]|#]+)")
PRIMEROS = 5  # los que se miran para acertar una pregunta de oro, y para expandir por el grafo
RRF = 60
GRAFO = 0.5  # cuánto del puntaje de un pasaje recibe la nota que enlaza


class SinEmbeddings(Exception):
    """El proveedor de embeddings no está o no respondió: la búsqueda sigue léxica y por el grafo."""


# --- el corpus ----------------------------------------------------------------------------------------------------------
def palabras(texto: str) -> list[str]:
    plano = "".join(c for c in unicodedata.normalize("NFKD", texto.casefold()) if not unicodedata.combining(c))
    return [p for p in re.findall(r"[a-z0-9]+", plano) if len(p) > 1 and p not in VACIAS]


def concepto_presente(concepto, texto):
    """Control léxico mínimo: admite tildes y plurales de sustantivos en -ción/-sión."""
    from . import consultas
    def normalizar(valor):
        return re.sub(r'\b([a-z]+(?:cion|sion))es\b', r'\1', consultas.plano(valor))
    return normalizar(concepto) in normalizar(texto)


def _titulos(texto: str):
    """Los encabezados (nivel, texto) fuera de los bloques de código."""
    en_codigo = False
    for linea in texto.splitlines():
        if linea.lstrip().startswith("```"):
            en_codigo = not en_codigo
        elif not en_codigo and (m := TITULO.match(linea)):
            yield m[1], m[2]


def _secciones(texto: str) -> list[tuple[str, str]]:
    """(título, cuerpo) por cada #, ## o ###; lo de antes del primer título va con el título del archivo."""
    salida, titulo, cuerpo, en_codigo = [], "", [], False
    for linea in texto.splitlines():
        if linea.lstrip().startswith("```"):
            en_codigo = not en_codigo
        m = None if en_codigo else TITULO.match(linea)
        if m:
            if "".join(cuerpo).strip():
                salida.append((titulo, "\n".join(cuerpo).strip()))
            titulo, cuerpo = m[2], []
        else:
            cuerpo.append(linea)
    if "".join(cuerpo).strip():
        salida.append((titulo, "\n".join(cuerpo).strip()))
    return salida


def _frontmatter(texto: str) -> tuple[dict, str]:
    if not texto.startswith("---\n") or "\n---" not in texto[4:]:
        return {}, texto
    cabeza, resto = texto[4:].split("\n---", 1)
    campos = {}
    for linea in cabeza.splitlines():
        if ":" in linea:
            k, v = linea.split(":", 1)
            campos[k.strip()] = v.strip().strip('"')
    return campos, resto.lstrip("\n")


def _archivos(cli) -> list[Path]:
    raiz = cli.ROOT
    # El índice del vault (kb/README.md) lista todos los cambios, también los abandonados: no responde nada por sí mismo.
    salida = sorted(p for p in (raiz / kb_mod.DIR).rglob("*.md") if p != raiz / kb_mod.DIR / "README.md") \
        if (raiz / kb_mod.DIR).is_dir() else []
    if cli.CHANGES.is_dir():
        for cambio in sorted(cli.CHANGES.iterdir()):
            if cambio.is_dir() and cli.ID_RE.fullmatch(cambio.name):
                salida += [cambio / n for n in ("proposal.md", "design.md") if (cambio / n).is_file()]
                salida += sorted((cambio / "specs").rglob("spec.md")) if (cambio / "specs").is_dir() else []
    salida += sorted((raiz / "openspec" / "specs").rglob("spec.md")) if (raiz / "openspec" / "specs").is_dir() else []
    salida += sorted((raiz / "docs").rglob("*.md")) if (raiz / "docs").is_dir() else []
    def seguro(p: Path) -> bool:  # ni el archivo ni ninguna carpeta de su camino es un enlace
        try:
            cli.ruta_segura(p)
            return p.is_file()
        except cli.FactoryError:
            return False
    return [p for p in salida if seguro(p)]


def corpus(cli) -> tuple[list[dict], list[str], int]:
    """Los pasajes vigentes, las notas de personas por revisar (que quedan afuera) y cuántos archivos de cambios
    abandonados se dejaron afuera."""
    raiz = cli.ROOT
    abandonados = {i for i, e in kb_mod.cambios_del_proyecto(cli) if e.get("fase") == "abandonada"}
    por_revisar = sorted(n["nota"] for n in kb_mod.estado_de_notas(cli) if n["faltan"] or n["cambiaron"])
    # Un pasaje que trae dos o más preguntas de oro es la lista de las preguntas (la de un diseño, por ejemplo), no una
    # respuesta: no responde nada y, si quedara, la evaluación se respondería sola. Uno que repite sólo una (una FAQ) sí.
    oro = raiz / kb_mod.DIR / "preguntas-de-oro.json"
    literales = [" ".join(palabras(x["pregunta"])) for x in json.loads(oro.read_text(encoding="utf-8"))] if oro.is_file() else []
    pasajes, fuera = [], 0
    for archivo in _archivos(cli):
        rel = archivo.relative_to(raiz).as_posix()
        if rel in por_revisar or archivo.stat().st_size > cli.estructura.LIMITE_ARCHIVO:
            continue
        campos, texto = _frontmatter(archivo.read_text(encoding="utf-8", errors="replace"))
        partes = rel.split("/")
        cambio = (partes[2] if partes[:2] == ["openspec", "changes"] else
                  partes[2][:-3] if partes[:2] == [kb_mod.DIR, "cambios"] else None)
        if partes[:2] == [kb_mod.DIR, "requisitos"] and (m := re.search(r"\[\[cambios/([^\]|#]+)", texto)):
            cambio = m[1]  # la nota de un requisito nombra su cambio; otro archivo que lo enlace no es de ese cambio
        if cambio in abandonados or campos.get("vigente") == "false":
            fuera += 1
            continue
        enlaces = sorted({f"{kb_mod.DIR}/{e.strip()}.md" for e in ENLACE.findall(texto)})
        titulo = next((t for _, t in _titulos(texto)), rel)  # el primer encabezado, aunque no tenga cuerpo
        for seccion, cuerpo in _secciones(texto):
            if len(cuerpo) < 20 or sum(x in " ".join(palabras(cuerpo)) for x in literales) >= 2:  # «Ninguno.», la lista
                continue
            contenido = f"{titulo}\n{seccion}\n{cuerpo}" if seccion and seccion != titulo else f"{titulo}\n{cuerpo}"
            pasajes.append({"ruta": rel, "seccion": seccion or titulo, "cambio": cambio, "texto": contenido,
                            "huella": hashlib.sha256(contenido.encode("utf-8")).hexdigest(), "enlaces": enlaces})
    return pasajes, por_revisar, fuera


# --- embeddings ---------------------------------------------------------------------------------------------------------
def configuracion(cli) -> dict:
    """La de .factory/config.json → rag.embeddings sobre la de por defecto; otro modelo no hereda el prefijo."""
    propia = cli.config_proyecto()["rag"].get("embeddings", {})
    if not isinstance(propia, dict):
        raise cli.FactoryError('.factory/config.json: "rag.embeddings" tiene que ser un objeto')
    conf = {**POR_DEFECTO, **propia}
    if "modelo" in propia and "prefijo_pregunta" not in propia:
        conf["prefijo_pregunta"] = ""
    if conf["proveedor"] not in ("ollama", "openai", "ninguno"):
        raise cli.FactoryError(f'.factory/config.json: rag.embeddings.proveedor es ollama, openai o ninguno, no «{conf["proveedor"]}»')
    return conf


def es_local(url: str) -> bool:
    host = urllib.parse.urlparse(url).hostname or ""
    try:
        return host == "localhost" or ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


class _SinRedirecciones(urllib.request.HTTPRedirectHandler):
    """Una redirección llevaría los textos a una URL que el proyecto no configuró: no se sigue."""
    def redirect_request(self, *args, **kwargs):
        return None


ABRIR = urllib.request.build_opener(_SinRedirecciones).open


def embeber(conf: dict, textos: list[str], configurada: bool) -> list[list[float]]:
    """Los embeddings de los textos, en lotes. Una URL que no es local sólo se usa si el proyecto la configuró él mismo
    (configurada: la URL está en su .factory/config.json), y nunca se sigue una redirección."""
    if conf["proveedor"] == "ninguno":
        raise SinEmbeddings("el proyecto apagó los embeddings (rag.embeddings.proveedor: ninguno)")
    if not configurada and not es_local(conf["url"]):
        raise SinEmbeddings(f"la URL {conf['url']} no es local y el proyecto no la configuró")
    salida = []
    for i in range(0, len(textos), 32):
        lote = textos[i:i + 32]
        if conf["proveedor"] == "ollama":
            url, cuerpo, cabeceras = conf["url"].rstrip("/") + "/api/embed", {"model": conf["modelo"], "input": lote}, {}
        else:
            clave = os.environ.get(conf.get("clave_env") or "", "")
            if not clave:
                raise SinEmbeddings(f'falta la clave del proveedor en la variable {conf.get("clave_env") or "(clave_env sin configurar)"}')
            url, cuerpo, cabeceras = conf["url"].rstrip("/") + "/embeddings", {"model": conf["modelo"], "input": lote}, \
                {"Authorization": f"Bearer {clave}"}
        pedido = urllib.request.Request(url, json.dumps(cuerpo).encode("utf-8"),
                                        {"Content-Type": "application/json", **cabeceras})
        try:
            timeout = min(300, conf.get('_plazo', time.monotonic() + 300) - time.monotonic())
            if timeout <= 0:
                raise SinEmbeddings('se alcanzó el plazo de la consulta')
            with ABRIR(pedido, timeout=timeout) as r:
                datos = json.loads(r.read())
        except (urllib.error.URLError, OSError, ValueError) as e:
            raise SinEmbeddings(f"{conf['proveedor']} en {conf['url']} no respondió ({getattr(e, 'reason', e)})") from e
        vectores = datos.get("embeddings") if conf["proveedor"] == "ollama" else [d.get("embedding") for d in datos.get("data") or []]
        if not isinstance(vectores, list) or len(vectores) != len(lote):
            raise SinEmbeddings(f"{conf['proveedor']} devolvió {len(vectores or [])} embeddings para {len(lote)} textos")
        salida += vectores
    return salida


# --- el índice ----------------------------------------------------------------------------------------------------------
def ruta_indice(cli) -> Path:
    return cli.ROOT / cli.estructura.DIR / "local" / "rag" / "indice.sqlite"


def vectores(cli, pasajes: list[dict], conf: dict, configurada: bool) -> tuple[dict[str, list[float]], int]:
    """Los embeddings de los pasajes: los guardados si son de este modelo, y sólo los que faltan se piden. Lo que ya no
    está en el corpus se borra. Devuelve también cuántos se pidieron."""
    ruta = cli.ruta_segura(ruta_indice(cli))  # un enlace en el camino lo llevaría fuera de .factory/local/rag/
    ruta.parent.mkdir(parents=True, exist_ok=True)
    cli.ruta_segura(ruta)
    clave = f"{conf['proveedor']}:{conf['url']}:{conf['modelo']}"  # otro servidor puede dar otros vectores
    with contextlib.closing(sqlite3.connect(ruta)) as db, db:
        db.execute("CREATE TABLE IF NOT EXISTS pasajes (huella TEXT PRIMARY KEY, modelo TEXT, vector BLOB)")
        guardados = {h: v for h, m, v in db.execute("SELECT huella, modelo, vector FROM pasajes") if m == clave}
        vigentes = {p["huella"] for p in pasajes}
        db.executemany("DELETE FROM pasajes WHERE huella = ?", [(h,) for h in
                       {h for (h,) in db.execute("SELECT huella FROM pasajes")} - (vigentes & set(guardados))])
        faltan = sorted({p["huella"]: p["texto"] for p in pasajes if p["huella"] not in guardados}.items())
        if faltan:
            nuevos = embeber(conf, [t for _, t in faltan], configurada)
            for (h, _), v in zip(faltan, nuevos):
                guardados[h] = array("f", v).tobytes()
                db.execute("INSERT OR REPLACE INTO pasajes VALUES (?, ?, ?)", (h, clave, guardados[h]))
    return {h: array("f", v).tolist() for h, v in guardados.items() if h in vigentes}, len(faltan)


# --- el ranking ---------------------------------------------------------------------------------------------------------
def bm25(pasajes: list[dict], pregunta: list[str], k1: float = 1.2, b: float = 0.75) -> list[float]:
    docs = [palabras(p["texto"]) for p in pasajes]
    n, media = len(docs), (sum(map(len, docs)) / len(docs)) if docs else 1
    df = {t: sum(1 for d in docs if t in d) for t in set(pregunta)}
    puntajes = []
    for d in docs:
        tf = {t: d.count(t) for t in set(pregunta)}
        puntajes.append(sum(math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5)) * tf[t] * (k1 + 1)
                            / (tf[t] + k1 * (1 - b + b * len(d) / media)) for t in tf if tf[t]))
    return puntajes


def coseno(a: list[float], b: list[float]) -> float:
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(x * x for x in b))
    return sum(x * y for x, y in zip(a, b)) / (na * nb) if na and nb else 0.0


def _rangos(puntajes: list[float]) -> dict[int, int]:
    orden = sorted((i for i, s in enumerate(puntajes) if s > 0), key=lambda i: -puntajes[i])
    return {i: r for r, i in enumerate(orden, 1)}


def recuperar(cli, pregunta: str, maximo: int = 8, *, plazo: float | None = None, alcance: str = 'todos') -> dict:
    from . import generacion
    if alcance not in generacion.ALCANCES_FUENTES:
        raise cli.FactoryError('Alcance de recuperación inválido.')
    if not pregunta.strip():
        raise cli.FactoryError("indicá la pregunta")
    pasajes, por_revisar, fuera = corpus(cli)
    conf = configuracion(cli)
    if plazo is not None:
        conf = {**conf, '_plazo': plazo}
    configurada = "url" in cli.config_proyecto()["rag"].get("embeddings", {})
    lexico = bm25(pasajes, palabras(pregunta))
    semantico, aviso, pedidos = [0.0] * len(pasajes), None, 0
    try:
        guardados, pedidos = vectores(cli, pasajes, conf, configurada)
        [v] = embeber(conf, [conf.get("prefijo_pregunta", "") + pregunta], configurada)
        semantico = [coseno(v, guardados[p["huella"]]) for p in pasajes]
        modo = "hibrido"
    except SinEmbeddings as e:
        modo, aviso = "lexico", f"sin embeddings ({e}): la búsqueda es sólo léxica y por el grafo"
    aportes = [{"lexico": 0.0, "semantico": 0.0, "grafo": 0.0} for _ in pasajes]
    for via, puntajes in (("lexico", lexico), ("semantico", semantico)):
        for i, r in _rangos(puntajes).items():
            aportes[i][via] = 1 / (RRF + r)
    total = [a["lexico"] + a["semantico"] for a in aportes]
    # Grafo: cada nota enlazada con uno de los primeros (un cambio y sus requisitos, en las dos direcciones) suma, en su
    # mejor pasaje, la mitad del puntaje de quien la enlaza.
    mejor: dict[str, int] = {}
    for i in sorted(range(len(pasajes)), key=lambda i: -total[i]):
        mejor.setdefault(pasajes[i]["ruta"], i)
    rutas = {p["ruta"]: p["enlaces"] for p in pasajes}
    for i in sorted(range(len(pasajes)), key=lambda i: -total[i])[:PRIMEROS]:
        origen = pasajes[i]["ruta"]
        for ruta in set(rutas[origen]) | {r for r, enl in rutas.items() if origen in enl}:
            j = mejor.get(ruta)
            if j is not None and ruta != origen:
                aportes[j]["grafo"] = max(aportes[j]["grafo"], total[i] * GRAFO)
    def compatible(p):
        if alcance == 'todos':
            return True
        clase = generacion.procedencia({**p, 'cita': f"{p['ruta']}#{p['seccion']}"})['clase']
        return (clase in generacion.CLASES_ACTUALES if alcance == 'actual' else
                clase in generacion.CLASES_ANTECEDENTES if alcance == 'antecedentes' else clase == 'exclusion')
    # Filtrar después de indexar y puntuar: un alcance no debe borrar embeddings de los otros.
    orden = sorted((i for i in range(len(pasajes)) if sum(aportes[i].values()) > 0 and compatible(pasajes[i])),
                   key=lambda i: -sum(aportes[i].values()))[:maximo]
    return {"esquema": ESQUEMA, "pregunta": pregunta, "modo": modo, "modelo": conf["modelo"] if modo == "hibrido" else None,
            "aviso": aviso, "embeddings_pedidos": pedidos, "por_revisar": por_revisar, "fuera_por_no_vigentes": fuera,
            "resultados": [{"cita": f"{pasajes[i]['ruta']}#{pasajes[i]['seccion']}", "ruta": pasajes[i]["ruta"],
                            "seccion": pasajes[i]["seccion"], "cambio": pasajes[i]["cambio"],
                            "puntaje": round(sum(aportes[i].values()), 6),
                            "similitud_semantica": round(semantico[i], 6),
                            "aportes": {k: round(v, 6) for k, v in aportes[i].items()},
                            "texto": pasajes[i]["texto"]} for i in orden]}


def preguntar(cli, pregunta: str, maximo: int = 8) -> dict:
    from . import consultas, generacion
    if not isinstance(pregunta, str) or not 1 <= len(pregunta.strip()) <= 2000:
        raise cli.FactoryError('indicá una pregunta de entre 1 y 2000 caracteres')
    if type(maximo) is not int or not 1 <= maximo <= 50:
        raise cli.FactoryError('max debe estar entre 1 y 50')
    base = {'esquema': ESQUEMA, 'pregunta': pregunta, 'modo': 'registro', 'modelo': None,
            'modelo_generativo': None, 'proveedor_generativo': None, 'modelo_embeddings': None,
            'aviso': None, 'embeddings_pedidos': 0, 'por_revisar': [], 'fuera_por_no_vigentes': 0,
            'resultados': [], 'fuentes': [], 'herramientas': [], 'limites': generacion.limites(),
            'max_pasajes': maximo}
    directa = consultas.directa(cli, pregunta)
    if directa is not None:
        return {**base, **directa}
    datos = recuperar(cli, pregunta, maximo)
    terminos = set(palabras(pregunta))
    def raices(t):
        variantes = {t}
        if len(t) > 3 and t.endswith('s'):
            variantes.add(t[:-1])
        if len(t) > 4 and t.endswith('es'):
            variantes.add(t[:-2])
        return variantes
    def cobertura(r):
        documento = set().union(*(raices(p) for p in palabras(r['texto'])))
        return sum(bool(raices(t) & documento) for t in terminos)
    respaldo = any(cobertura(r) >= min(2, len(terminos)) > 0
                   or r['similitud_semantica'] >= 0.65 for r in datos['resultados'])
    respuesta = {**base, **datos, 'modelo_embeddings': datos['modelo'],
                 'tipo': 'documentos' if respaldo else 'sin_respaldo',
                 'respuesta': ('Encontré pasajes candidatos; no se elaboró una respuesta generativa.' if respaldo else
                               'No encontré respaldo suficiente para responder.'),
                 'fuentes': [{'ruta': r['ruta'], 'cita': r['cita'], 'texto': r['texto']} for r in datos['resultados']]}
    avisos = [datos['aviso']] if datos['aviso'] else []
    if not respaldo:
        # El modelo no puede convertir candidatos sin respaldo en una respuesta ni pedir datos de otro tema.
        respuesta['fuentes'] = []
        respuesta['aviso'] = '; '.join(avisos) or None
        return respuesta
    try:
        conf = generacion.configuracion(cli)
    except cli.FactoryError as error:
        respuesta['generacion_error'] = type(error).__name__
        respuesta['generacion_error_codigo'] = 'configuracion_invalida'
        avisos.append('La configuración generativa es inválida; se conserva la recuperación documental.')
        respuesta['aviso'] = '; '.join(avisos)
        return respuesta
    if conf is None:
        avisos.append('Sin modelo generativo configurado: se muestran sólo resultados directos o pasajes candidatos.')
    else:
        respuesta['limites'] = generacion.limites(conf)
        try:
            actuales = recuperar(cli, pregunta, 5, alcance='actual')
            respuesta.update(generacion.elaborar(cli, pregunta, actuales, conf))
            if respuesta.get('aviso_generativo'):
                avisos.append(respuesta['aviso_generativo'])
        except (OSError, ValueError, TypeError, KeyError, IndexError) as error:
            respuesta['generacion_error'] = type(error).__name__
            respuesta['generacion_error_codigo'] = generacion.codigo_error(error)
            avisos.append('La generación no produjo una respuesta válida dentro de sus límites; se conserva la recuperación documental.')
    respuesta['aviso'] = '; '.join(avisos) or None
    return respuesta


def texto(datos: dict) -> str:
    lineas = []
    if datos.get('respuesta'):
        lineas.append(datos['respuesta'])
    if datos.get('tipo') in ('registro', 'respuesta_elaborada') and datos.get('fuentes'):
        lineas.append('\nFuentes:')
        for fuente in datos['fuentes']:
            lineas.append(f'- {fuente.get("id", "Registro")}: {fuente["cita"]}')
            if 'directorio' in fuente:
                lineas.append(f'  Inventario consultado: {fuente["directorio"]}' + ('' if fuente.get('directorio_existe') else ' (no existe)'))
            archivos = fuente.get('archivos', [])
            if archivos and 'directorio' in fuente:
                lineas.append('  Registros inspeccionados para verificar el filtro (pueden no coincidir):')
            lineas.extend(f'  - {ruta}' for ruta in archivos[:10])
            omitidos = max(0, len(archivos) - 10) + fuente.get('archivos_omitidos', 0)
            if omitidos:
                lineas.append(f'  Referencias adicionales no mostradas: {omitidos}.')
    if datos.get('resultados'):
        lineas.append('\nPasajes candidatos (no equivalen a una respuesta elaborada):')
    for n, r in enumerate(datos["resultados"], 1):
        a = r["aportes"]
        lineas.append(f"{n}. {r['cita']}" + (f" ({r['cambio']})" if r["cambio"] else "")
                      + f" — léxico {a['lexico']:.4f} · semántico {a['semantico']:.4f} · grafo {a['grafo']:.4f}")
        cuerpo = " ".join(r["texto"].split("\n", 1)[-1].split())
        lineas.append(f"   {cuerpo[:280]}{'…' if len(cuerpo) > 280 else ''}")
    if not datos["resultados"] and not datos.get('respuesta'):
        lineas.append("Nada en el conocimiento del proyecto responde a eso.")
    if datos["aviso"]:
        lineas.append(f"Aviso: {datos['aviso']}.")
    if datos["por_revisar"]:
        lineas.append("Quedaron afuera por revisar (sus fuentes cambiaron): " + ", ".join(datos["por_revisar"]) + ".")
    if datos.get('limites'):
        limite = datos['limites']
        lineas.append(f"Límites: registro paginado de {limite['registro']['pagina_predeterminada']} en {limite['registro']['pagina_predeterminada']}; "
                      + (f"generación hasta {limite['generacion']['max_llamadas']} llamadas a herramientas y {limite['generacion']['segundos']} s."
                         if limite['generacion']['usada'] else 'sin elaboración generativa en esta respuesta.'))
    return "\n".join(lineas)


# --- preguntas de oro ---------------------------------------------------------------------------------------------------
def _calculo_respaldado(datos, filtro):
    """Una pregunta mixta exige cálculo consultado y citado, no sólo palabras esperadas en una explicación."""
    for fuente in datos.get('fuentes', []):
        criterio = fuente.get('criterio', {})
        if fuente.get('ruta') != 'registro' or criterio.get('id'):
            continue
        if criterio.get('estado') == filtro:
            valor = fuente.get('valor')
        elif criterio.get('operacion') == 'agrupar' and criterio.get('estado') == 'todos':
            agregados = fuente.get('agregados', {})
            if filtro == 'cerrados':
                valor = agregados.get('cerrada', 0)
            elif filtro == 'abandonados':
                valor = agregados.get('abandonada', 0)
            elif filtro == 'abiertos':
                valor = sum(v for k, v in agregados.items() if k not in ('cerrada', 'abandonada'))
            else:
                valor = fuente.get('valor')
        else:
            continue
        llamada = any(t.get('herramienta') == 'registro' and t.get('exitoso')
                      and t.get('argumentos', {}).get('operacion') == criterio.get('operacion')
                      and t.get('argumentos', {}).get('estado', 'todos') == criterio.get('estado')
                      for t in datos.get('herramientas', []))
        if not llamada or type(valor) is not int:
            continue
        for afirmacion in datos.get('afirmaciones', []):
            if (str(valor) in re.findall(r'\b\d+\b', afirmacion['texto'])
                    and any(c.get('fuente') == fuente.get('id') for c in afirmacion['citas'])):
                return True
    return False


def evaluar(cli, salida: Path, *, simulado: bool = False, casos: Path | None = None) -> dict:
    """Corre las preguntas de oro y deja en salida/hechos.json lo que Oracle juzga, y el detalle en salida/detalle.json."""
    archivo = cli.ROOT / kb_mod.DIR / "preguntas-de-oro.json"
    if not archivo.is_file():
        raise cli.FactoryError(f"no hay preguntas de oro: falta {archivo.relative_to(cli.ROOT)}")
    preguntas = json.loads(archivo.read_text(encoding="utf-8"))
    if not isinstance(preguntas, list):
        raise cli.FactoryError('Las preguntas de oro deben ser una lista.')
    if casos is not None:
        ruta = cli.ruta_segura(casos if casos.is_absolute() else cli.ROOT / casos)
        if not ruta.is_file() or ruta.stat().st_size > cli.estructura.LIMITE_ARCHIVO:
            raise cli.FactoryError('El archivo de casos adicionales falta o supera el tamaño admitido.')
        adicionales = json.loads(ruta.read_text(encoding='utf-8'))
        if not isinstance(adicionales, list):
            raise cli.FactoryError('Los casos adicionales deben ser una lista.')
        preguntas += adicionales
    if (not isinstance(preguntas, list) or not preguntas or len(preguntas) > 200
            or any(not isinstance(p, dict) or not isinstance(p.get('id'), str) or not isinstance(p.get('pregunta'), str)
                   for p in preguntas) or len({p['id'] for p in preguntas}) != len(preguntas)):
        raise cli.FactoryError('Las preguntas deben ser una lista de hasta 200 objetos con id único y pregunta.')
    filas, detalle, modos, grupos = [], [], set(), []
    class SinGeneracion:
        """El grupo documental mide la selección de respaldo de producción, separada de la elaboración real."""
        def __getattr__(self, nombre):
            return getattr(cli, nombre)
        def config_proyecto(self):
            conf = cli.config_proyecto()
            return {**conf, 'rag': {**conf['rag'], 'generacion': {'proveedor': 'ninguno'}}}
    for p in preguntas:
        grupo = p.get('grupo', 'documental')
        if grupo not in ('documental', 'registro', 'abstencion', 'generativa'):
            raise cli.FactoryError('Grupo de evaluación no admitido: ' + str(grupo))
        def lista_textos(valor, vacia=False):
            return isinstance(valor, list) and (vacia or bool(valor)) and all(isinstance(t, str) and bool(t) for t in valor)
        if (not 1 <= len(p['pregunta'].strip()) <= 2000
                or (grupo == 'documental' and not lista_textos(p.get('esperadas')))
                or (grupo == 'registro' and (type(p.get('valor')) is not int or p['valor'] < 0))
                or (grupo == 'registro' and (type(p.get('requiere_listado', False)) is not bool
                                            or (p.get('requiere_listado') and not lista_textos(p.get('ids'), vacia=True))))
                or (grupo == 'abstencion' and p.get('tipo') not in ('sin_respaldo', 'requiere_aclaracion', 'consulta_no_admitida'))
                or (grupo == 'generativa' and (not lista_textos(p.get('contiene'))
                                              or not isinstance(p.get('contiene_alguno', []), list)
                                              or any(not lista_textos(g) for g in p.get('contiene_alguno', []))
                                              or not lista_textos(p.get('excluye', []), vacia=True)
                                              or not lista_textos(p.get('fuentes', []), vacia=True)
                                              or not lista_textos(p.get('fuentes_cualquiera', []), vacia=True)
                                              or not (p.get('fuentes') or p.get('fuentes_cualquiera'))
                                              or type(p.get('requiere_registro', False)) is not bool
                                              or p.get('filtro_registro', 'todos') not in ('todos', 'abiertos', 'cerrados', 'abandonados')))):
            raise cli.FactoryError('Caso de evaluación incompleto o inválido: ' + p['id'])
        if grupo != 'documental':
            datos = preguntar(cli, p['pregunta'], maximo=PRIMEROS)
            if grupo == 'registro':
                acierto = datos['tipo'] == 'registro' and type(datos.get('valor')) is int and datos['valor'] == p['valor']
                if p.get('requiere_listado'):
                    ids = datos.get('ids')
                    pagina = datos.get('pagina', {})
                    acierto = (acierto and isinstance(ids, list) and (bool(ids) or not p['ids'])
                               and ids == p['ids'][:len(ids)] and pagina.get('omitidos') == len(p['ids']) - len(ids))
            elif grupo == 'abstencion':
                acierto = datos['tipo'] == p['tipo']
            else:
                acierto = (datos['tipo'] == 'respuesta_elaborada' and bool(datos.get('afirmaciones')) and bool(p.get('contiene'))
                           and all(concepto_presente(t, datos['respuesta']) for t in p['contiene'])
                           and all(any(concepto_presente(t, datos['respuesta']) for t in g)
                                   for g in p.get('contiene_alguno', []))
                           and not any(t.casefold() in a['texto'].casefold() for t in p.get('excluye', [])
                                       for a in datos.get('afirmaciones', []) if a.get('alcance') != 'exclusion')
                           and bool(datos['fuentes']) and all(any(fuente['ruta'] == ruta for fuente in datos['fuentes'])
                                                            for ruta in p.get('fuentes', [])))
                if p.get('fuentes_cualquiera'):
                    acierto = acierto and any(fnmatch.fnmatchcase(s['ruta'], patron)
                                              or (patron.endswith('/') and s['ruta'].startswith(patron))
                                              for s in datos.get('fuentes', []) for patron in p['fuentes_cualquiera'])
                if p.get('requiere_registro'):
                    acierto = acierto and _calculo_respaldado(datos, p.get('filtro_registro', 'todos'))
            degradada = grupo == 'generativa' and datos['tipo'] == 'documentos'
            grupos.append({'id': p['id'], 'grupo': grupo, 'acierto': int(acierto), 'tipo': datos['tipo'],
                           'abstuvo': int(degradada or datos['tipo'] in ('sin_respaldo', 'requiere_aclaracion', 'consulta_no_admitida')),
                           'degradada': int(degradada),
                           'modelo_generativo': datos.get('modelo_generativo') or 'ninguno', 'simulado': int(simulado)})
            detalle.append({**grupos[-1], 'pregunta': p['pregunta'], 'respuesta': datos})
            continue
        datos = preguntar(SinGeneracion(), p["pregunta"], maximo=PRIMEROS)
        rutas = [r["ruta"] for r in datos["resultados"]]  # los cinco primeros pasajes: lo mismo que ve quien pregunta
        puesto = next((n for n, r in enumerate(rutas, 1)
                       if any(r == e or (e.endswith("/") and r.startswith(e)) for e in p["esperadas"])), 0)
        modos.add(datos["modo"])
        filas.append({"id": p["id"], "acierto": int(puesto > 0), "puesto": puesto, "modo": datos["modo"],
                      'criterio': 'recuperacion_en_cinco'})
        abstuvo = int(datos['tipo'] in ('sin_respaldo', 'requiere_aclaracion', 'consulta_no_admitida'))
        detalle.append({**filas[-1], "pregunta": p["pregunta"], "esperadas": p["esperadas"], "primeros": rutas,
                        'tipo': datos['tipo'], 'abstuvo': abstuvo, 'generacion_desactivada': True,
                        'recuperacion_correcta': int(puesto > 0), 'respaldo_suficiente': int(datos['tipo'] == 'documentos'),
                        'respuesta_correcta': int(puesto > 0 and datos['tipo'] == 'documentos')})
        grupos.append({'id': p['id'], 'grupo': grupo, 'acierto': int(puesto > 0 and datos['tipo'] == 'documentos'), 'abstuvo': abstuvo,
                       'degradada': 0, 'tipo': datos['tipo'], 'modelo_generativo': 'ninguno', 'simulado': int(simulado)})
    modo = modos.pop() if len(modos) == 1 else "mixto"
    corrida = {"preguntas": len(filas), "aciertos": sum(f["acierto"] for f in filas),
               "mrr": round(sum(1 / f["puesto"] for f in filas if f["puesto"]) / len(filas), 4) if filas else 0.0,
               "modo": modo, "modelo": configuracion(cli)["modelo"] if modo == "hibrido" else "ninguno",
               'criterio': 'recuperacion_en_cinco'}
    criterios = {'documental': 'recuperacion_con_respaldo', 'registro': 'exactitud_del_registro',
                 'generativa': 'explicacion_con_fuentes', 'abstencion': 'abstencion_esperada'}
    for fila in grupos:
        fila['criterio'] = criterios[fila['grupo']]
    salida.mkdir(parents=True, exist_ok=False)
    resumen = [{'grupo': grupo, 'preguntas': sum(f['grupo'] == grupo for f in grupos),
                'aciertos': sum(f['acierto'] for f in grupos if f['grupo'] == grupo),
                'errores': sum(1 - f['acierto'] for f in grupos if f['grupo'] == grupo),
                'abstenciones': sum(f['abstuvo'] for f in grupos if f['grupo'] == grupo),
                'abstenciones_correctas': sum(f['abstuvo'] * f['acierto'] for f in grupos if f['grupo'] == grupo),
                'abstenciones_incorrectas': sum(f['abstuvo'] * (1 - f['acierto']) for f in grupos if f['grupo'] == grupo),
                'degradaciones': sum(f['degradada'] for f in grupos if f['grupo'] == grupo),
                'simulado': int(simulado), 'criterio': criterios[grupo]} for grupo in sorted({f['grupo'] for f in grupos})]
    (salida / "hechos.json").write_text(json.dumps({"rag_pregunta": filas, "rag_corrida": [corrida],
                                                   'preguntar_pregunta': grupos, 'preguntar_grupo': resumen}, ensure_ascii=False,
                                                   indent=2) + "\n", encoding="utf-8")
    (salida / "detalle.json").write_text(json.dumps(detalle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return corrida
