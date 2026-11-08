"""Despliegue a varios destinos: lo que el proyecto declara en `.factory/destinos.json`, el plan, la ejecución y la evidencia.

Factory no conoce ninguna tecnología: un **destino** es un nombre con comandos (construir, desplegar, probar, versión, volver) que el proyecto
escribe, y esta capa los ordena por sus dependencias, los ejecuta sólo cuando una persona autoriza, prueba cada destino y el conjunto, y deja
un registro en `.factory/despliegues/<ID>/registro.json`. Nada de acá decide quién puede autorizar: eso lo hace la CLI (`cli.desplegar`).

Las funciones reciben `correr` (el que ejecuta un comando) para que las pruebas usen destinos simulados; por defecto es `_correr`, un `sh -c`."""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import tempfile
import time
from typing import Callable

ARCHIVO = Path(".factory") / "destinos.json"
DIR_REGISTROS = Path(".factory") / "despliegues"
CAMPOS_DESTINO = {"tipo", "construir", "desplegar", "probar", "version", "volver", "alcanzable", "depende_de", "secretos", "tope_segundos", "alcance"}
CAMPOS_COMANDO = ("construir", "desplegar", "probar", "version", "volver", "alcanzable")
CAMPOS_RAIZ = {"rama", "politica_ante_fallo", "destinos", "conjunto"}
POLITICAS = ("cortar", "seguir")
NOMBRE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*")
VARIABLE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
TOPE = 900  # segundos por comando si el destino no declara otro
MAX_SALIDA = 4000  # caracteres de salida que se guardan por paso


class DeclaracionInvalida(ValueError):
    """`.factory/destinos.json` no sirve; el mensaje nombra el destino y el campo."""


class DespliegueNegado(Exception):
    """El plan no se arma o no se ejecuta; el mensaje dice por qué."""


def cargar(raiz: Path) -> dict:
    """La declaración del proyecto, validada: {rama, politica, destinos: {nombre: {...}}, conjunto}."""
    ruta = raiz / ARCHIVO
    if not ruta.is_file():
        raise DeclaracionInvalida(f"no hay {ARCHIVO.as_posix()}: declará ahí los destinos del proyecto (hay un ejemplo en docs/plantillas/destinos.json)")
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise DeclaracionInvalida(f"{ARCHIVO.as_posix()} no se puede leer: {e}") from e
    if not isinstance(datos, dict):
        raise DeclaracionInvalida(f"{ARCHIVO.as_posix()}: se esperaba un objeto JSON")
    for extra in sorted(set(datos) - CAMPOS_RAIZ):
        raise DeclaracionInvalida(f"{ARCHIVO.as_posix()}: el campo «{extra}» no existe (los válidos: {', '.join(sorted(CAMPOS_RAIZ))})")
    rama = datos.get("rama", "main")
    politica = datos.get("politica_ante_fallo", "cortar")
    if not isinstance(rama, str) or not rama.strip():
        raise DeclaracionInvalida("rama: tiene que ser el nombre de una rama")
    if politica not in POLITICAS:
        raise DeclaracionInvalida(f"politica_ante_fallo: «{politica}» no es ninguna de {', '.join(POLITICAS)}")
    crudos = datos.get("destinos")
    if not isinstance(crudos, dict) or not crudos:
        raise DeclaracionInvalida("destinos: tiene que haber al menos un destino")
    destinos = {}
    for nombre, d in crudos.items():
        destinos[nombre] = _destino(nombre, d, crudos)
    _sin_ciclos(destinos)
    conjunto = datos.get("conjunto")
    if conjunto is None:
        raise DeclaracionInvalida("falta «conjunto»: la prueba de que todo anda junto ({\"probar\": \"comando\"}); sin ella no se puede decir "
                                  "«todo quedó funcionando» (con un solo destino puede ser la misma prueba de humo)")
    if not isinstance(conjunto, dict) or set(conjunto) - {"probar", "tope_segundos"} or not isinstance(conjunto.get("probar"), str) or not conjunto["probar"].strip():
        raise DeclaracionInvalida("conjunto: se espera {\"probar\": \"comando\"}")
    tope = conjunto.get("tope_segundos", TOPE)
    if not isinstance(tope, int) or isinstance(tope, bool) or tope <= 0:
        raise DeclaracionInvalida("conjunto: «tope_segundos» es un número entero positivo")
    return {"rama": rama, "politica": politica, "destinos": destinos, "conjunto": conjunto}


def _destino(nombre: str, d: object, todos: dict) -> dict:
    if not NOMBRE.fullmatch(str(nombre)):
        raise DeclaracionInvalida(f"destino «{nombre}»: el nombre usa letras, números, «_», «.» o «-»")
    if not isinstance(d, dict):
        raise DeclaracionInvalida(f"destino «{nombre}»: se esperaba un objeto con sus comandos")
    for extra in sorted(set(d) - CAMPOS_DESTINO):
        raise DeclaracionInvalida(f"destino «{nombre}»: el campo «{extra}» no existe (los válidos: {', '.join(sorted(CAMPOS_DESTINO))})")
    for campo in CAMPOS_COMANDO:
        if campo in d and (not isinstance(d[campo], str) or not d[campo].strip()):
            raise DeclaracionInvalida(f"destino «{nombre}»: «{campo}» tiene que ser un comando (texto)")
    if "desplegar" not in d:
        raise DeclaracionInvalida(f"destino «{nombre}»: falta el campo «desplegar» (el comando que lo despliega)")
    if "version" not in d:
        raise DeclaracionInvalida(f"destino «{nombre}»: falta el campo «version» (el comando que imprime el commit que corre): sin él no se puede "
                                  "comprobar que el destino quedó con la versión del plan")
    tipo = d.get("tipo", "otro")
    if not isinstance(tipo, str) or not tipo.strip():
        raise DeclaracionInvalida(f"destino «{nombre}»: «tipo» es una etiqueta de texto")
    deps = d.get("depende_de", [])
    if not isinstance(deps, list) or not all(isinstance(x, str) for x in deps):
        raise DeclaracionInvalida(f"destino «{nombre}»: «depende_de» es una lista de nombres de destinos")
    for dep in deps:
        if dep not in todos:
            raise DeclaracionInvalida(f"destino «{nombre}»: depende_de «{dep}», que no está declarado")
        if dep == nombre:
            raise DeclaracionInvalida(f"destino «{nombre}»: ciclo, depende de sí mismo")
    secretos = d.get("secretos", [])
    if not isinstance(secretos, list) or not all(isinstance(x, str) and VARIABLE.fullmatch(x) for x in secretos):
        # No se repite lo escrito: podría ser el valor de un secreto.
        raise DeclaracionInvalida(f"destino «{nombre}»: «secretos» lleva sólo NOMBRES de variables de entorno (A-Z, 0-9, «_»), nunca el valor")
    tope = d.get("tope_segundos", TOPE)
    if not isinstance(tope, int) or isinstance(tope, bool) or tope <= 0:
        raise DeclaracionInvalida(f"destino «{nombre}»: «tope_segundos» es un número entero positivo")
    extra = {}
    if "alcance" in d:
        alcance = d["alcance"]
        if not isinstance(alcance, list) or not alcance or not all(isinstance(x, str) and x.strip() for x in alcance):
            raise DeclaracionInvalida(f"destino «{nombre}»: «alcance» es una lista no vacía de rutas de Git (carpetas o patrones)")
        extra["alcance"] = list(alcance)
    return {"nombre": nombre, "tipo": tipo, "depende_de": list(deps), "secretos": list(secretos), "tope_segundos": tope,
            **{c: d[c] for c in CAMPOS_COMANDO if c in d}, **extra}


def _sin_ciclos(destinos: dict) -> None:
    pendientes = {n: set(d["depende_de"]) for n, d in destinos.items()}
    while pendientes:
        listos = [n for n, deps in pendientes.items() if not deps]
        if not listos:
            raise DeclaracionInvalida(f"ciclo de dependencias entre {', '.join(sorted(pendientes))}")
        for n in listos:
            del pendientes[n]
        for deps in pendientes.values():
            deps.difference_update(listos)


def orden(destinos: dict, elegidos: list[str] | None = None) -> list[str]:
    """Los destinos en el orden de sus dependencias; entre los que no dependen uno de otro, el de la declaración."""
    incluidos = set(elegidos or destinos)
    pendientes = list(incluidos)
    while pendientes:  # lo que se elige arrastra, de forma transitiva, lo que necesita: no se despliega un consumidor sin su dependencia
        for dep in destinos[pendientes.pop()]["depende_de"]:
            if dep not in incluidos:
                incluidos.add(dep)
                pendientes.append(dep)
    queda = [n for n in destinos if n in incluidos]
    hecho: list[str] = []
    while queda:
        siguiente = next(n for n in queda if all(dep in hecho or dep not in queda for dep in destinos[n]["depende_de"]))
        hecho.append(siguiente)
        queda.remove(siguiente)
    return hecho


def _git(raiz: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=raiz, capture_output=True, text=True)


def _version_previa(raiz: Path, nombre: str) -> str | None:
    """La versión que la última corrida dejó `desplegado` o `probado` en ese destino, o None si nunca se desplegó."""
    for r in reversed(registros(raiz)):
        d = r.get("destinos", {}).get(nombre)
        if d and d.get("estado") in ("desplegado", "probado") and d.get("version_despues"):
            return d["version_despues"]
    return None


def elegir_por_cambios(raiz: Path, decl: dict, commit: str) -> tuple[list[str], dict[str, str], dict[str, str]]:
    """(elegidos, motivos, omitidos): los destinos con archivos cambiados dentro de su alcance desde su última versión desplegada.
    Entran siempre los que no tienen alcance, los que nunca se desplegaron y los que no se pueden comparar. Sólo se miran las rutas declaradas."""
    elegidos, motivos, omitidos = [], {}, {}
    for n, d in decl["destinos"].items():
        previa = _version_previa(raiz, n)
        if "alcance" not in d:
            motivos[n] = "sin alcance declarado: entra siempre"
        elif previa is None:
            motivos[n] = "nunca se desplegó"
        elif _git(raiz, "cat-file", "-e", f"{previa}^{{commit}}").returncode != 0:
            motivos[n] = f"su versión anterior ({previa[:12]}) no se conoce en este repositorio: no se puede comparar"
        else:
            r = _git(raiz, "diff", "--name-only", f"{previa}..{commit}", "--", *d["alcance"])
            archivos = [a for a in r.stdout.splitlines() if a]
            if r.returncode != 0:
                motivos[n] = f"no se pudo comparar con {previa[:12]}: {r.stderr.strip()[:120]}"
            elif archivos:
                motivos[n] = f"cambió {archivos[0]}" + (f" y {len(archivos) - 1} más" if len(archivos) > 1 else "") + f" desde {previa[:12]}"
            else:
                omitidos[n] = f"sin cambios en su alcance desde {previa[:12]}"
                continue
        elegidos.append(n)
    return elegidos, motivos, omitidos


def armar_plan(raiz: Path, decl: dict, commit: str | None = None, destinos: list[str] | None = None,
               puerta: Callable[[], tuple[bool, str]] | None = None, cambios: bool = False) -> dict:
    """El plan de un commit de la rama de despliegue. Se niega si el commit no está en la rama o si la puerta local no está en verde."""
    rama = decl["rama"]
    punta = _git(raiz, "rev-parse", "--verify", "--quiet", f"{rama}^{{commit}}")
    if punta.returncode != 0:
        raise DespliegueNegado(f"la rama de despliegue «{rama}» no existe en este repositorio")
    elegido = punta.stdout.strip()
    if commit:
        r = _git(raiz, "rev-parse", "--verify", "--quiet", f"{commit}^{{commit}}")
        if r.returncode != 0:
            raise DespliegueNegado(f"el commit «{commit}» no existe")
        elegido = r.stdout.strip()
        if _git(raiz, "merge-base", "--is-ancestor", elegido, rama).returncode != 0:
            raise DespliegueNegado(f"el commit {elegido[:12]} no está en la rama de despliegue «{rama}»: integralo primero")
    for n in destinos or []:
        if n not in decl["destinos"]:
            raise DespliegueNegado(f"el destino «{n}» no está declarado")
    if puerta is not None:
        ok, texto = puerta()
        if not ok:
            raise DespliegueNegado("la puerta local de salida no está en verde, así que no se arma el plan:\n" + texto.strip())
    if cambios:
        if destinos:
            raise DespliegueNegado("--cambios y --destino no se combinan: elegí los destinos por sus cambios o por su nombre")
        elegidos, motivos, omitidos = elegir_por_cambios(raiz, decl, elegido)
        ordenados = orden(decl["destinos"], elegidos) if elegidos else []
        for n in ordenados:
            motivos.setdefault(n, "lo necesita un destino elegido (depende_de)")
        return {"commit": elegido, "rama": rama, "orden": ordenados, "motivos": {n: motivos[n] for n in ordenados}, "omitidos": omitidos}
    return {"commit": elegido, "rama": rama, "orden": orden(decl["destinos"], destinos)}


def texto_plan(decl: dict, plan: dict) -> str:
    lineas = [f"Plan de despliegue del commit {plan['commit'][:12]} (rama {plan['rama']}), política ante un fallo: {decl['politica']}."]
    for i, n in enumerate(plan["orden"], 1):
        d = decl["destinos"][n]
        deps = f" (después de {', '.join(d['depende_de'])})" if d["depende_de"] else ""
        lineas.append(f"{i}. {n} [{d['tipo']}]{deps}")
        if n in plan.get("motivos", {}):
            lineas.append(f"     por qué: {plan['motivos'][n]}")
        for paso in ("alcanzable", "construir", "desplegar", "version", "probar", "volver"):
            if paso in d:
                lineas.append(f"     {paso}: {d[paso]}")
    for n, motivo in plan.get("omitidos", {}).items():
        lineas.append(f"Se omite {n}: {motivo}")
    if "motivos" in plan and not plan["orden"]:
        lineas.append("No hay nada que desplegar: ningún destino tiene cambios en su alcance.")
    elif decl["conjunto"]:
        lineas.append(f"Al final, la prueba de conjunto: {decl['conjunto']['probar']}")
    return "\n".join(lineas)


def faltan_secretos(decl: dict, plan: dict) -> list[str]:
    return sorted({f"{s} (destino {n})" for n in plan["orden"] for s in decl["destinos"][n]["secretos"] if not os.environ.get(s)})


def _correr(comando: str, raiz: Path, env: dict, tope: int) -> tuple[int, str, float]:
    """(código, salida, segundos). Un comando que se pasa del tope o no arranca es un fallo, no un cuelgue."""
    inicio = time.monotonic()
    try:
        # Su propia sesión: si se pasa del tope se mata todo el grupo, no sólo el shell (un hijo en segundo plano seguiría tocando el destino).
        p = subprocess.Popen(["sh", "-c", comando], cwd=raiz, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                             stdin=subprocess.DEVNULL, start_new_session=True)
    except OSError as e:
        return 127, f"no se pudo ejecutar: {e}", time.monotonic() - inicio
    try:
        salida, _ = p.communicate(timeout=tope)
        return p.returncode, salida or "", time.monotonic() - inicio
    except subprocess.TimeoutExpired:
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        salida, _ = p.communicate()
        return 124, (salida or "") + f"\n[se pasó del tope de {tope} s y se mató el grupo de procesos]", time.monotonic() - inicio


def _tapar(texto: str, secretos: dict[str, str]) -> str:
    for nombre, valor in sorted(secretos.items(), key=lambda kv: -len(kv[1])):
        if valor:
            texto = texto.replace(valor, f"«secreto:{nombre}»")
    return texto


def ejecutar(raiz: Path, decl: dict, plan: dict, autorizo: str, planeo: str, correr: Callable | None = None, ahora: Callable[[], str] | None = None) -> dict:
    """Ejecuta el plan que una persona autorizó y guarda el registro. Devuelve el registro."""
    correr = correr or _correr
    faltan = faltan_secretos(decl, plan)
    if faltan:
        raise DespliegueNegado("faltan en el entorno estos secretos, y no se ejecutó nada: " + ", ".join(faltan))
    todos = {s: os.environ[s] for n in plan["orden"] for s in decl["destinos"][n]["secretos"]}
    commit = plan["commit"]
    cuando = (ahora or _ahora)()
    registro: dict = {"id": _id_nuevo(raiz, cuando, commit), "commit": commit, "rama": plan["rama"], "cuando": cuando, "planeo": planeo,
                      "autorizo": autorizo, "politica": decl["politica"], "orden": list(plan["orden"]), "destinos": {}, "conjunto": {"resultado": "no_corrio"},
                      "resultado": "fallido", "motivo": "", "aviso": ""}
    for n in plan["orden"]:
        registro["destinos"][n] = {"estado": "sin_desplegar", "motivo": "", "version_antes": None, "version_despues": None, "ultima_prueba": None, "pasos": {}, "sin_volver": False}

    def paso(n: str, nombre: str, comando: str) -> tuple[int, str]:
        d = decl["destinos"][n]
        env = {**os.environ, "FACTORY_COMMIT": commit, "FACTORY_DESTINO": n, "FACTORY_RAMA": plan["rama"]}
        codigo, salida, seg = correr(comando, raiz, env, d["tope_segundos"])
        salida = _tapar(salida, todos)
        registro["destinos"][n]["pasos"][nombre] = {"comando": _tapar(comando, todos), "codigo": codigo, "segundos": round(seg, 2), "salida": salida[-MAX_SALIDA:]}
        return codigo, salida.strip()

    corte = False
    for n in plan["orden"]:
        d, r = decl["destinos"][n], registro["destinos"][n]
        if corte:
            r["motivo"] = "no se tocó: la corrida se cortó antes"
            continue
        caidos = [dep for dep in d["depende_de"] if dep in registro["destinos"] and registro["destinos"][dep]["estado"] != "probado"]
        if caidos:
            r["motivo"] = f"no se tocó: depende de {', '.join(caidos)}, que no quedó probado"
            continue
        if not _destino_en_marcha(paso, n, d, r, commit):
            if decl["politica"] == "cortar":
                corte = True
    if not corte:
        sin_probar = [n for n in plan["orden"] if registro["destinos"][n]["estado"] != "probado"]
        if not sin_probar and decl["conjunto"]:
            _conjunto(registro, decl, raiz, commit, plan, correr, todos)
    _cerrar(registro, decl, raiz, plan, correr, todos, corte)
    _guardar(raiz, registro)
    return registro


def _ahora() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _id_nuevo(raiz: Path, cuando: str, commit: str) -> str:
    base = re.sub(r"[^0-9]", "", cuando)[:8] + "-" + re.sub(r"[^0-9]", "", cuando)[8:14] + "-" + commit[:7]
    candidato, n = base, 1
    while (raiz / DIR_REGISTROS / candidato).exists():
        n += 1
        candidato = f"{base}-{n}"
    return candidato


def _destino_en_marcha(paso: Callable, n: str, d: dict, r: dict, commit: str) -> bool:
    """Un destino por sus pasos; True si quedó probado (o desplegado si no tiene prueba). Anota el estado y el motivo en `r`."""
    if "alcanzable" in d:
        codigo, _ = paso(n, "alcanzable", d["alcanzable"])
        if codigo != 0:
            r.update(estado="inalcanzable", motivo="no se alcanza (el comando «alcanzable» falló); no se desplegó")
            return False
    if "version" in d:
        codigo, salida = paso(n, "version_antes", d["version"])
        r["version_antes"] = salida if codigo == 0 else None
    for nombre in ("construir", "desplegar"):
        if nombre in d:
            codigo, _ = paso(n, nombre, d[nombre])
            if codigo != 0:
                r.update(estado="fallido", motivo=f"falló «{nombre}» (código {codigo})")
                r["desplego"] = nombre == "desplegar" or r.get("desplego", False)
                return False
    r["desplego"] = True
    r["estado"] = "desplegado"
    if "version" in d:
        codigo, salida = paso(n, "version", d["version"])
        r["version_despues"] = salida if codigo == 0 else None
        if codigo != 0 or salida != commit:
            r.update(estado="fallido", motivo=f"corre otra versión que la del plan: devolvió «{salida[:60]}», se esperaba {commit[:12]}"
                     if codigo == 0 else "no se pudo leer la versión que corre (el comando «version» falló)")
            return False
    if "probar" not in d:
        r["motivo"] = "desplegado; sin prueba de humo declarada, no queda «probado»"
        return True
    codigo, _ = paso(n, "probar", d["probar"])
    r["ultima_prueba"] = {"cuando": _ahora(), "resultado": "ok" if codigo == 0 else "fallo"}
    if codigo != 0:
        r.update(estado="fallido", motivo=f"falló su prueba de humo (código {codigo})")
        return False
    r["estado"] = "probado"
    return True


def _conjunto(registro: dict, decl: dict, raiz: Path, commit: str, plan: dict, correr: Callable, secretos: dict) -> None:
    env = {**os.environ, "FACTORY_COMMIT": commit, "FACTORY_RAMA": plan["rama"]}
    codigo, salida, seg = correr(decl["conjunto"]["probar"], raiz, env, decl["conjunto"].get("tope_segundos", TOPE))
    registro["conjunto"] = {"resultado": "ok" if codigo == 0 else "fallo", "comando": _tapar(decl["conjunto"]["probar"], secretos), "codigo": codigo,
                            "segundos": round(seg, 2), "salida": _tapar(salida, secretos)[-MAX_SALIDA:]}


def _cerrar(registro: dict, decl: dict, raiz: Path, plan: dict, correr: Callable, secretos: dict, corte: bool) -> None:
    """Vuelve atrás lo que corresponde y fija el resultado."""
    destinos = registro["destinos"]
    fallo = any(destinos[n]["estado"] in ("fallido", "inalcanzable") for n in plan["orden"])
    avisos = []
    if fallo:  # con «cortar» o con «seguir»: la corrida no se queda a medias, se vuelve atrás lo desplegado
        for n in reversed(plan["orden"]):  # lo ya desplegado en esta corrida (menos lo que falló), del último al primero
            r, d = destinos[n], decl["destinos"][n]
            if r["estado"] not in ("probado", "desplegado"):
                continue
            if "volver" not in d:
                r["sin_volver"] = True
                r.update(estado="desplegado", motivo="quedó desplegado: la corrida falló y no tiene comando «volver»")
                avisos.append(n)
                continue
            env = {**os.environ, "FACTORY_COMMIT": registro["commit"], "FACTORY_DESTINO": n, "FACTORY_RAMA": plan["rama"]}
            codigo, salida, seg = correr(d["volver"], raiz, env, d["tope_segundos"])
            r["pasos"]["volver"] = {"comando": _tapar(d["volver"], secretos), "codigo": codigo, "segundos": round(seg, 2), "salida": _tapar(salida, secretos)[-MAX_SALIDA:]}
            if codigo == 0:
                r.update(estado="revertido", motivo="vuelto atrás tras el fallo de otro destino")
            else:
                r.update(estado="fallido", motivo=f"hubo que volverlo atrás y «volver» falló (código {codigo}): revisalo a mano")
    if avisos:
        registro["aviso"] = "quedaron desplegados sin poder volver atrás: " + ", ".join(avisos)
    caidos = [n for n in plan["orden"] if destinos[n]["estado"] in ("fallido", "inalcanzable")]
    sin_probar = [n for n in plan["orden"] if destinos[n]["estado"] != "probado"]
    if registro["conjunto"]["resultado"] == "fallo":
        registro["resultado"], registro["motivo"] = "fallido", "falló la prueba de conjunto; los destinos conservan su estado"
    elif caidos:
        registro["resultado"], registro["motivo"] = "fallido", "; ".join(f"{n}: {destinos[n]['motivo']}" for n in caidos)
    elif sin_probar:
        registro["resultado"] = "incompleto"
        registro["motivo"] = "no quedaron probados: " + ", ".join(sin_probar)
    else:
        registro["resultado"], registro["motivo"] = "todo_funciona", "todo quedó funcionando"


def _guardar(raiz: Path, registro: dict) -> None:
    carpeta = raiz / DIR_REGISTROS / registro["id"]
    carpeta.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=carpeta, prefix=".registro-", delete=False) as f:
        json.dump(registro, f, ensure_ascii=False, indent=1)
        f.write("\n")
        temporal = Path(f.name)
    temporal.replace(carpeta / "registro.json")


def registros(raiz: Path) -> list[dict]:
    """Las corridas guardadas, de la más vieja a la más nueva."""
    salida = []
    for archivo in sorted((raiz / DIR_REGISTROS).glob("*/registro.json")) if (raiz / DIR_REGISTROS).is_dir() else []:
        try:
            salida.append((json.loads(archivo.read_text(encoding="utf-8")), archivo.stat().st_mtime_ns))
        except (ValueError, OSError):
            continue
    # «cuando» tiene precisión de segundos y el ID lleva el commit: dos corridas del mismo segundo se ordenan por cuándo se escribió su registro.
    return [r for r, _ in sorted(salida, key=lambda x: (x[0].get("cuando", ""), x[1], x[0].get("id", "")))]


def estados(raiz: Path, decl: dict, consultar: bool = True, correr: Callable | None = None) -> list[dict]:
    """Cada destino con su estado según la última corrida que lo tocó. «desactualizado» se calcula: si el destino responde con su versión,
    se compara con la punta de la rama; si no responde o no se consulta, es «desconocido»."""
    correr = correr or _correr
    historia = registros(raiz)
    punta = _git(raiz, "rev-parse", "--verify", "--quiet", f"{decl['rama']}^{{commit}}").stdout.strip() or None
    salida = []
    for n, d in decl["destinos"].items():
        ultimo = next(((r, r["destinos"][n]) for r in reversed(historia) if n in r.get("destinos", {}) and r["destinos"][n]["estado"] != "sin_desplegar"), None)
        desplegada, esperada, desactualizado = None, punta, "desconocido"
        if ultimo:
            desplegada = ultimo[1].get("version_despues")
        if consultar and "version" in d:
            env = {**os.environ, "FACTORY_DESTINO": n, "FACTORY_RAMA": decl["rama"]}
            codigo, texto, _ = correr(d["version"], raiz, env, d["tope_segundos"])
            if codigo == 0 and texto.strip():
                desplegada = texto.strip()
                desactualizado = bool(punta) and desplegada != punta
        salida.append({"nombre": n, "tipo": d["tipo"], "estado": ultimo[1]["estado"] if ultimo else "sin_desplegar", "version_desplegada": desplegada,
                       "version_esperada": esperada, "ultima_prueba": (ultimo[1].get("ultima_prueba") if ultimo else None), "desactualizado": desactualizado,
                       "depende_de": list(d["depende_de"]), "corrida": ultimo[0]["id"] if ultimo else None})
    return salida


def resumen_corrida(registro: dict | None) -> dict | None:
    if not registro:
        return None
    return {k: registro.get(k) for k in ("id", "commit", "cuando", "planeo", "autorizo", "resultado", "motivo", "aviso")}
