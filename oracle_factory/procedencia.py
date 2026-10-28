"""Procedencia de las dependencias de Python de un proyecto: inventario CycloneDX, búsqueda y auditoría contra avisos OSV.

Todo es local: se lee el lock (`uv.lock`), los requisitos de `pyproject.toml` y las distribuciones instaladas; no se usa la red.
El inventario sale ordenado y sin marcas de tiempo, para que dos corridas iguales den el mismo archivo y la misma huella."""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys
import tomllib
from urllib.parse import quote

CORREGIDA = re.compile(r"[.+-]rhlw", re.I)  # el sufijo que Lightwell pone a una versión corregida (.rhlw-0000X, +rhlw…)
FIJADA = re.compile(r"==\s*[0-9A-Za-z.+!_-]+")
REQUISITO = re.compile(r"\s*([A-Za-z0-9][A-Za-z0-9._-]*)\s*(?:\[[^\]]*\])?\s*([^;]*)")
VERSION = re.compile(r"v?(?P<rel>\d+(?:\.\d+)*)(?:[-_.]?(?P<pre>a|b|c|rc|alpha|beta|pre|preview)[-_.]?(?P<pre_n>\d*))?"
                     r"(?P<post>[-_.]?(?:post|rev|r)[-_.]?(?P<post_n>\d*))?(?P<dev>[-_.]?dev[-_.]?(?P<dev_n>\d*))?", re.I)
INFINITO = float("inf")
TIPOS_DE_RANGO = ("ECOSYSTEM", "SEMVER", "GIT")
EVENTOS = {"introduced": 0, "limit": 1, "last_affected": 1, "fixed": 2}  # el orden en que se aplican si coinciden en la versión
DESDE_SIEMPRE = ((-1,), (-INFINITO, 0), -INFINITO, -INFINITO)  # introduced: "0", antes de cualquier versión
VOLCADO = ("import importlib.metadata as m, json; "
           "print(json.dumps({d.metadata['Name']: d.version for d in m.distributions() if d.metadata['Name']}))")


class ProcedenciaError(Exception):
    pass


def normal(nombre: str) -> str:
    """El nombre de un paquete como lo compara PyPI (PEP 503)."""
    return re.sub(r"[-_.]+", "-", nombre).lower()


def corregida(version: str) -> bool:
    return bool(CORREGIDA.search(version))


def sin_correccion(version: str) -> str:
    """La versión sin la marca de una corrección ni la parte local: con la que un aviso la compara."""
    return CORREGIDA.split(version.split("+")[0], 1)[0]


def clave(version: str):
    """Para ordenar versiones al estilo PEP 440 (sin la parte local); None si no se puede leer."""
    m = VERSION.fullmatch(version.strip().split("+")[0])
    if not m:
        return None
    liberada = [int(x) for x in m["rel"].split(".")]
    while len(liberada) > 1 and liberada[-1] == 0:
        liberada.pop()
    orden = {"alpha": 0, "a": 0, "beta": 1, "b": 1, "c": 2, "rc": 2, "pre": 2, "preview": 2}
    pre = (orden[m["pre"].lower()], int(m["pre_n"] or 0)) if m["pre"] else None
    post = int(m["post_n"] or 0) if m["post"] is not None else None
    dev = int(m["dev_n"] or 0) if m["dev"] is not None else None
    if pre is None and post is None and dev is not None:
        pre = (-INFINITO, 0)
    elif pre is None:
        pre = (INFINITO, 0)
    return (tuple(liberada), pre, -INFINITO if post is None else post, INFINITO if dev is None else dev)


def leer_lock(raiz: Path) -> dict | None:
    """El lock de uv: {'proyecto': {...}, 'paquetes': {nombre normal: [{...}, ...]}} (un paquete puede estar en varias versiones); None si no hay."""
    ruta = raiz / "uv.lock"
    if ruta.is_symlink() or not ruta.is_file():
        return None
    try:
        datos = tomllib.loads(ruta.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as e:
        raise ProcedenciaError(f"uv.lock no se puede leer: {e}") from e
    proyecto, paquetes = {}, {}
    for p in datos.get("package", []) if isinstance(datos.get("package"), list) else []:
        if not isinstance(p, dict):
            continue
        nombre, version, origen = p.get("name"), p.get("version"), p.get("source")
        if not isinstance(nombre, str) or not isinstance(version, str):
            continue
        origen = origen if isinstance(origen, dict) else {}
        metadatos = p.get("metadata") if isinstance(p.get("metadata"), dict) else {}
        if "editable" in origen or "virtual" in origen:
            proyecto = {"nombre": nombre, "version": version, "requiere": [r.get("name") for r in metadatos.get("requires-dist", []) if isinstance(r, dict)]}
            continue
        artefactos = ([p["sdist"]] if isinstance(p.get("sdist"), dict) else []) + [w for w in p.get("wheels", []) if isinstance(w, dict)]
        hashes = sorted({a["hash"].split(":", 1)[1] for a in artefactos if isinstance(a.get("hash"), str) and a["hash"].startswith("sha256:")})
        paquetes.setdefault(normal(nombre), []).append({"nombre": nombre, "version": version, "hashes": hashes,
                                                         "origen": origen.get("registry") or next(iter(origen.values()), "desconocido")})
    return {"proyecto": proyecto, "paquetes": paquetes}


def requisitos(raiz: Path) -> tuple[dict, dict[str, tuple[str, str]], str | None]:
    """Los datos del proyecto, sus dependencias directas de pyproject.toml {nombre normal: (nombre, especificación)} y, si no se pudo
    comparar contra ellas, el motivo."""
    ruta = raiz / "pyproject.toml"
    if ruta.is_symlink():
        return {}, {}, "pyproject.toml es un enlace simbólico y no se sigue: no se puede comprobar que el lock coincida con lo que pide el proyecto"
    if not ruta.is_file():
        return {}, {}, "no hay pyproject.toml: no se puede comprobar que el lock coincida con lo que pide el proyecto"
    try:
        datos = tomllib.loads(ruta.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as e:
        raise ProcedenciaError(f"pyproject.toml no se puede leer: {e}") from e
    proyecto = datos.get("project", {})
    if not isinstance(proyecto, dict):
        raise ProcedenciaError("pyproject.toml: «project» tiene que ser una tabla")
    dependencias = proyecto.get("dependencies", [])
    if not isinstance(dependencias, list):
        raise ProcedenciaError("pyproject.toml: «dependencies» tiene que ser una lista")
    directas = {}
    for texto in dependencias:
        m = REQUISITO.fullmatch(texto) if isinstance(texto, str) else None
        if m:
            directas[normal(m[1])] = (m[1], m[2].strip())
    nombre, version = proyecto.get("name", ""), proyecto.get("version", "")
    return {"nombre": nombre if isinstance(nombre, str) else "", "version": version if isinstance(version, str) else ""}, directas, None


def instalados(python: Path | None) -> dict[str, tuple[str, str]] | None:
    """Las distribuciones instaladas en ese Python: {nombre normal: (nombre, versión)}; None si no se pudo preguntar."""
    if python is None or not python.exists():
        return None
    try:
        r = subprocess.run([str(python), "-I", "-c", VOLCADO], capture_output=True, text=True, timeout=60, stdin=subprocess.DEVNULL)
        crudo = json.loads(r.stdout) if r.returncode == 0 else None
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
        return None
    if not isinstance(crudo, dict):
        return None
    return {normal(n): (n, v) for n, v in crudo.items() if isinstance(n, str) and isinstance(v, str)}


def _componente(nombre: str, version: str, origen: str, hashes: list[str], fuente: str, exigida: str | None, fijada: bool) -> dict:
    propiedades = [("factory:origen", origen), ("factory:fuente", fuente), ("factory:directa", "true" if exigida is not None else "false"),
                   ("factory:exigida", exigida or ""), ("factory:fijada", "true" if fijada else "false")]
    if corregida(version):
        propiedades.append(("factory:corregida", "lightwell"))
    purl = f"pkg:pypi/{normal(nombre)}@{quote(version, safe='')}"
    return {"type": "library", "bom-ref": purl, "name": nombre, "version": version, "purl": purl,
            "hashes": [{"alg": "SHA-256", "content": h} for h in hashes],
            "properties": [{"name": n, "value": v} for n, v in propiedades]}


def inventario(raiz: Path, python: Path | None = None) -> tuple[dict, list[str], bool]:
    """(el inventario CycloneDX, las diferencias que lo hacen no confiable, si es confiable)."""
    lock = leer_lock(raiz)
    proyecto, directas, sin_requisitos = requisitos(raiz)
    puestos = instalados(python)
    diferencias: list[str] = [sin_requisitos] if sin_requisitos else []
    componentes = []
    if lock is None:
        diferencias.append("no hay uv.lock: el origen y los hashes de las dependencias no se pueden verificar")
        for n, (nombre, version) in sorted((puestos or {}).items()):
            if n == normal(proyecto.get("nombre", "")):
                continue
            exigida = directas[n][1] if n in directas else None
            componentes.append(_componente(nombre, version, "desconocido", [], "instalado", exigida, False))
        if puestos is None:
            diferencias.append("no se pudo leer el entorno instalado: no hay ningún componente que listar")
    else:
        paquetes, raiz_lock = lock["paquetes"], lock["proyecto"]
        if raiz_lock and proyecto.get("version") and raiz_lock["version"] != proyecto["version"]:
            diferencias.append(f"el lock es de la versión {raiz_lock['version']} del proyecto y pyproject.toml dice {proyecto['version']}")
        for n, (nombre, especificacion) in sorted(directas.items()):
            fijadas = [p["version"] for p in paquetes.get(n, [])]
            if not fijadas:
                diferencias.append(f"{nombre}: lo exige pyproject.toml ({especificacion or 'sin versión'}) y no está en el lock")
            elif FIJADA.fullmatch(especificacion) and especificacion.replace("==", "").strip() not in fijadas:
                diferencias.append(f"{nombre}: pyproject.toml exige {especificacion} y el lock fija {', '.join(fijadas)}")
        for n, entradas in sorted(paquetes.items()):
            fijadas = [p["version"] for p in entradas]
            if puestos is not None and n not in puestos:
                diferencias.append(f"{entradas[0]['nombre']}: está en el lock ({', '.join(fijadas)}) y no está instalado")
            elif puestos is not None and puestos[n][1] not in fijadas:
                diferencias.append(f"{entradas[0]['nombre']}: el lock fija {', '.join(fijadas)} y está instalada la {puestos[n][1]}")
            for p in entradas:
                exigida = directas[n][1] if n in directas else None
                componentes.append(_componente(p["nombre"], p["version"], p["origen"], p["hashes"], "uv.lock", exigida, bool(p["hashes"])))
    componentes.sort(key=lambda c: (normal(c["name"]), c["version"]))
    confiable = not diferencias  # sin lock siempre hay una diferencia
    propiedades = [{"name": "factory:confiable", "value": "true" if confiable else "false"},
                   {"name": "factory:entorno", "value": "consultado" if puestos is not None else "no consultado"}]
    propiedades += [{"name": "factory:diferencia", "value": d} for d in diferencias]
    bom = {"bomFormat": "CycloneDX", "specVersion": "1.5", "version": 1,
           "metadata": {"component": {"type": "application", "name": proyecto.get("nombre", ""), "version": proyecto.get("version", "")},
                        "properties": propiedades},
           "components": componentes}
    return bom, diferencias, confiable


def texto(bom: dict) -> str:
    """El inventario tal como se guarda: ordenado, con sangría y sin marcas de tiempo."""
    return json.dumps(bom, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def propiedad(componente: dict, nombre: str) -> str | None:
    return next((p.get("value") for p in componente.get("properties", []) if p.get("name") == nombre), None)


def pedido(texto_pedido: str) -> tuple[str, str | None]:
    """«paquete» o «paquete==versión»."""
    nombre, _, version = texto_pedido.strip().partition("==")
    if not nombre.strip():
        raise ProcedenciaError("indicá un paquete, por ejemplo requests o requests==2.31.0")
    return normal(nombre.strip()), (version.strip() or None)


def usados(inventarios: list[tuple[str, str, dict]], nombre: str, version: str | None) -> list[tuple[str, str, str, str]]:
    """[(cambio, candidato, nombre, versión)] de los inventarios guardados que tienen ese paquete (y esa versión, si se pide)."""
    salida = []
    for cambio, candidato, bom in inventarios:
        for c in bom.get("components", []):
            if isinstance(c, dict) and normal(str(c.get("name", ""))) == nombre and (version is None or c.get("version") == version):
                salida.append((cambio, candidato, c["name"], str(c.get("version"))))
    return sorted(salida)


def avisos(contenido: str, origen: str) -> list[dict]:
    """Los avisos OSV de un archivo (uno, una lista, o {"vulns": [...]}); falla si no son avisos OSV válidos."""
    try:
        datos = json.loads(contenido)
    except json.JSONDecodeError as e:
        raise ProcedenciaError(f"{origen} no es JSON: {e}") from e
    if isinstance(datos, dict) and isinstance(datos.get("vulns"), list):
        datos = datos["vulns"]
    elif isinstance(datos, dict):
        datos = [datos]
    if not isinstance(datos, list) or not datos:
        raise ProcedenciaError(f"{origen} no tiene avisos OSV: se espera un aviso, una lista o un objeto con «vulns»")
    for i, a in enumerate(datos):
        if not isinstance(a, dict) or not isinstance(a.get("id"), str) or not isinstance(a.get("affected"), list) or not a["affected"]:
            raise ProcedenciaError(f"{origen}: el aviso {i + 1} no es OSV válido (necesita «id» y un «affected» con al menos un paquete)")
        for af in a["affected"]:
            paquete = af.get("package") if isinstance(af, dict) else None
            if not isinstance(paquete, dict) or not isinstance(paquete.get("name"), str) or not isinstance(paquete.get("ecosystem"), str):
                raise ProcedenciaError(f"{origen}: el aviso {a['id']} tiene un «affected» sin «package» con «name» y «ecosystem»")
            if not isinstance(af.get("versions", []), list) or not isinstance(af.get("ranges", []), list):
                raise ProcedenciaError(f"{origen}: el aviso {a['id']} tiene «versions» o «ranges» que no son listas")
            for r in af.get("ranges", []):
                eventos = r.get("events") if isinstance(r, dict) else None
                if (not isinstance(r, dict) or r.get("type") not in TIPOS_DE_RANGO or not isinstance(eventos, list) or not eventos
                        or not all(isinstance(e, dict) and len(e) == 1 and next(iter(e)) in EVENTOS and isinstance(next(iter(e.values())), str)
                                   for e in eventos)):
                    raise ProcedenciaError(f"{origen}: el aviso {a['id']} tiene un rango que no es OSV válido (necesita «type» "
                                           f"{'/'.join(TIPOS_DE_RANGO)} y una lista no vacía de «events» de la forma {{\"introduced\": \"1.0\"}})")
    return datos


def _afectada(version: str, afectado: dict) -> bool | None:
    """Si la versión cae en lo afectado; None si no se la puede comparar (sin rangos aplicables o con una versión ilegible)."""
    if version in [str(v) for v in afectado.get("versions", [])]:
        return True
    k = clave(version)
    rangos = [r for r in afectado.get("ranges", []) if r.get("type") in ("ECOSYSTEM", "SEMVER")]
    if not rangos:
        return None if not afectado.get("versions") else False
    for rango in rangos:
        dentro = False
        eventos = []
        for e in rango["events"]:
            tipo, valor = next(iter(e.items()))
            origen = tipo == "introduced" and valor == "0"
            kv = DESDE_SIEMPRE if origen else clave(valor)
            if kv is None or k is None:
                return None
            eventos.append((kv, EVENTOS[tipo], tipo))
        for kv, _, tipo in sorted(eventos):
            if tipo == "introduced" and k >= kv:
                dentro = True
            elif tipo == "fixed" and k >= kv:
                dentro = False
            elif tipo == "last_affected" and k > kv:
                dentro = False
        if dentro:
            return True
    return False


def auditar(inventarios: list[tuple[str, str, dict]], lista: list[dict]) -> dict:
    """Cruza los inventarios con los avisos. {'afectados': [...], 'corregidos': [...], 'sin_comparar': [...]}"""
    afectados, corregidos, sin_comparar = [], [], []
    for aviso in lista:
        for af in aviso["affected"]:
            if af["package"]["ecosystem"].lower() != "pypi":
                continue
            nombre = normal(af["package"]["name"])
            arreglos = sorted({str(e["fixed"]) for r in af.get("ranges", []) if isinstance(r, dict) for e in r.get("events", [])
                               if isinstance(e, dict) and "fixed" in e})
            for cambio, candidato, bom in inventarios:
                for c in bom.get("components", []):
                    if not isinstance(c, dict) or normal(str(c.get("name", ""))) != nombre:
                        continue
                    version = str(c.get("version"))
                    base = sin_correccion(version)
                    veredicto = _afectada(base, af)
                    fila = {"aviso": aviso["id"], "resumen": aviso.get("summary", ""), "paquete": c["name"], "version": version,
                            "corregidas": arreglos, "cambio": cambio, "candidato": candidato}
                    if veredicto is None:
                        sin_comparar.append(fila)
                    elif veredicto and corregida(version):
                        corregidos.append(fila)
                    elif veredicto:
                        afectados.append(fila)
    clave_fila = lambda f: (f["aviso"], normal(f["paquete"]), f["version"], f["cambio"], f["candidato"])  # noqa: E731
    return {"afectados": sorted(afectados, key=clave_fila), "corregidos": sorted(corregidos, key=clave_fila),
            "sin_comparar": sorted(sin_comparar, key=clave_fila)}


def sin_enlaces(raiz: Path, ruta: Path) -> None:
    """Falla si la ruta o alguna carpeta del camino hasta ella es un enlace simbólico."""
    relativa = ruta.relative_to(raiz)  # sólo se la llama con rutas de adentro
    actual = raiz
    for parte in relativa.parts:
        actual /= parte
        if actual.is_symlink():
            raise ProcedenciaError(f"no se siguen enlaces simbólicos: {actual}")


def guardados(raiz: Path) -> list[tuple[str, str, dict]]:
    """[(cambio, candidato, inventario)] de los inventarios guardados en las carpetas de candidatos; los ilegibles se avisan y se saltean."""
    base = raiz / ".factory" / "cambios"
    salida = []
    for archivo in sorted(base.glob("*/candidatos/*/procedencia/cyclonedx.json")):
        try:
            sin_enlaces(raiz, archivo)
            bom = json.loads(archivo.read_text(encoding="utf-8"))
            if not isinstance(bom, dict) or not isinstance(bom.get("components"), list):
                raise ValueError("no es un inventario CycloneDX")
        except (ProcedenciaError, OSError, ValueError) as e:
            print(f"Aviso: no leí el inventario {archivo.relative_to(raiz)} ({e}).", file=sys.stderr)
            continue
        salida.append((archivo.parents[3].name, archivo.parents[1].name, bom))
    return salida


def informe_buscar(raiz: Path, pedido_texto: str, como_json: bool) -> str:
    nombre, version = pedido(pedido_texto)
    encontrados = usados(guardados(raiz), nombre, version)
    if como_json:
        return json.dumps([dict(zip(("cambio", "candidato", "paquete", "version"), f)) for f in encontrados], ensure_ascii=False, indent=2) + "\n"
    if not encontrados:
        return f"Ningún candidato con inventario guardado usó {pedido_texto.strip()}.\n"
    lineas = [f"{pedido_texto.strip()} figura en {len(encontrados)} inventario(s):"]
    lineas += [f"  - {cambio} · candidato {candidato} · {paquete} {v}" for cambio, candidato, paquete, v in encontrados]
    return "\n".join(lineas) + "\n"


def informe_auditar(raiz: Path, archivo: str, como_json: bool) -> str:
    ruta = Path(archivo)
    absoluta = ruta.absolute()
    try:
        if absoluta.is_relative_to(raiz):
            sin_enlaces(raiz, absoluta)  # dentro del proyecto, ningún directorio del camino es un enlace
    except ProcedenciaError as e:
        raise ProcedenciaError(f"no encuentro el archivo de avisos {archivo} ({e})") from e
    if ruta.is_symlink() or not ruta.is_file():
        raise ProcedenciaError(f"no encuentro el archivo de avisos {archivo}")
    try:
        lista = avisos(ruta.read_text(encoding="utf-8"), archivo)
    except UnicodeDecodeError as e:
        raise ProcedenciaError(f"{archivo} no está en UTF-8: {e}") from e
    inventarios = guardados(raiz)
    resultado = auditar(inventarios, lista)
    if como_json:
        return json.dumps({"avisos": len(lista), "inventarios": len(inventarios), **resultado}, ensure_ascii=False, indent=2) + "\n"
    lineas = [f"Auditoría local: {len(lista)} aviso(s) contra {len(inventarios)} inventario(s) guardado(s); sin red."]
    if not any(resultado.values()):
        lineas.append("No hay candidatos afectados.")
    for titulo, filas in (("Afectados", resultado["afectados"]), ("Afectados pero corregidos por Lightwell (verificá el aviso)", resultado["corregidos"]),
                          ("No se pudo comparar la versión con los rangos del aviso", resultado["sin_comparar"])):
        if filas:
            lineas.append(f"{titulo}:")
        for f in filas:
            corregidas = ", ".join(f["corregidas"]) or "sin versión corregida declarada"
            lineas.append(f"  - {f['aviso']}: {f['paquete']} {f['version']} (corregida en: {corregidas}) · {f['cambio']} · candidato {f['candidato']}")
    return "\n".join(lineas) + "\n"


def python_del_proyecto(raiz: Path, indicado: str | None) -> Path | None:
    """El Python del que se leen las distribuciones: el indicado o el .venv del proyecto; ninguno si no hay."""
    if indicado:
        return Path(indicado)
    for candidato in (raiz / ".venv" / "bin" / "python", raiz / ".venv" / "Scripts" / "python.exe"):
        if candidato.exists():
            return candidato
    return None


if __name__ == "__main__":  # una comprobación mínima de la comparación de versiones
    ordenadas = ["1.0.dev1", "1.0a1", "1.0b2", "1.0rc1", "1.0", "1.0.post1", "1.1", "2"]
    assert [clave(v) for v in ordenadas] == sorted(clave(v) for v in ordenadas), ordenadas
    assert clave("1.0") == clave("1.0.0") and clave("1.0+local") == clave("1.0") and clave("no es una versión") is None
    print("ok", file=sys.stderr)
