"""La puerta local de salida: lo barato y determinista que se comprueba antes de publicar, en segundos.

Hoy son dos comprobaciones: **secretos** (credenciales con forma de credencial en las líneas agregadas por *todos* los commits que se
van a publicar, no sólo en el resultado: un secreto agregado y quitado después igual viaja en la historia) y las **verificaciones**
del proyecto (`agentes`, `kb` y `resumen` con `--verificar`). Es una lista: los analizadores estáticos y `verificar` de CI se suman acá.

El hook `pre-push` (ver `cli.instalar_hook`) la llama con lo que Git está por empujar. Sólo bloquea con `CODIGO_BLOQUEO`: cualquier otra
salida (un intérprete que falta, un proyecto mal configurado, un error interno) avisa y deja pasar, porque una herramienta rota no
tiene que impedir trabajar."""
from __future__ import annotations

import re
from typing import Callable

CODIGO_BLOQUEO = 3
HOOK_MARCA = "# oracle-factory: puerta local de salida"
EXENCION = "factory:secreto-ok"
# Cada verificación y el archivo que la hace aplicable: si el proyecto todavía no lo generó, no hay nada que verificar (se omite).
# El tercer valor: si vencida bloquea. La guía no se arregla sola y desorienta a los agentes; kb y resumen se rehacen al integrar (post-merge),
# así que vencidos son cotidianos (p. ej. tras agregar un mensaje a un cambio): se avisan.
VERIFICACIONES = (("agentes", "AGENTS.md", True), ("kb", "kb/README.md", False), ("resumen", ".factory/resumen.md", False))
LINEA_MAXIMA = 300_000  # una línea de un JSON gigante se mira entera; más que esto ya no es texto escrito por una persona

# Valores con forma de credencial, no palabras. Cada patrón captura el valor en el grupo 1 (o el 0 si no hay grupo).
PATRONES: tuple[tuple[str, re.Pattern], ...] = (
    ("clave privada", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP |ENCRYPTED )?PRIVATE KEY")),
    ("clave de AWS", re.compile(r"\b(AKIA[0-9A-Z]{16})\b")),
    ("token de GitHub", re.compile(r"\b(gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{22,})")),
    ("token de PyPI", re.compile(r"\b(pypi-[A-Za-z0-9_-]{50,})")),
    ("token de Slack", re.compile(r"\b(xox[baprs]-[A-Za-z0-9-]{10,})")),
    ("clave de Google", re.compile(r"\b(AIza[0-9A-Za-z_-]{35})\b")),
    ("clave sk-", re.compile(r"\b(sk-(?:ant-)?[A-Za-z0-9_-]{20,})")),
)
# Un nombre de credencial asignado a un valor entre comillas, largo, sin espacios y con letras y dígitos (descarta frases y constantes).
ASIGNACION = re.compile(r"""(?i)\b(?:api[_-]?key|secret|token|passw(?:or)?d|clave|credencial)\w*\s*[=:]\s*["']([^"'\s]{16,})["']""")
ENCABEZADO_HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


class PuertaRota(Exception):
    """La puerta no pudo mirar (Git falló): no se puede decir que está limpio."""


def _tapado(valor: str) -> str:
    return valor[:4] + "…" + "*" * 3 if len(valor) > 4 else "****"


def _en_linea(linea: str) -> list[tuple[str, str]]:
    """[(tipo, valor)] de lo que parece una credencial en una línea."""
    if EXENCION in linea:
        return []
    if len(linea) > LINEA_MAXIMA:
        linea = linea[:LINEA_MAXIMA]
    encontrados = []
    for tipo, patron in PATRONES:
        for m in patron.finditer(linea):
            encontrados.append((tipo, m.group(1) if patron.groups else m.group(0)))
    for m in ASIGNACION.finditer(linea):
        valor = m.group(1)
        if re.search(r"\d", valor) and re.search(r"[A-Za-z]", valor) and not any(v == valor for _, v in encontrados):
            encontrados.append(("asignación sospechosa", valor))
    return encontrados


def hallazgos(texto_del_log: str) -> list[dict]:
    """Las credenciales en las líneas agregadas del texto de `git log -p -U0 --format=commit:%H`: archivo, línea, commit, tipo, vista."""
    salida, commit, archivo, linea, en_hunk = [], "", "", 0, False
    for crudo in texto_del_log.splitlines():
        if re.fullmatch(r"commit:[0-9a-f]{7,64}", crudo):  # nuestra línea de formato; dentro de un hunk las líneas empiezan con + o -
            commit, archivo, en_hunk = crudo[7:], "", False
        elif crudo.startswith("diff --git"):
            en_hunk, archivo = False, ""
        elif not en_hunk and crudo.startswith("+++ "):
            archivo = "" if crudo == "+++ /dev/null" else crudo[4:].removeprefix("b/")
        elif crudo.startswith("@@"):
            m = ENCABEZADO_HUNK.match(crudo)
            en_hunk, linea = bool(m), int(m[1]) if m else 0
        elif en_hunk and crudo.startswith("+"):
            for tipo, valor in _en_linea(crudo[1:]):
                salida.append({"archivo": archivo, "linea": linea, "commit": commit, "tipo": tipo, "vista": _tapado(valor)})
            linea += 1
    return salida


def texto_de_hallazgos(encontrados: list[dict]) -> str:
    return "\n".join(f"      {h['archivo']}:{h['linea']} (commit {h['commit'][:7]}): {h['tipo']} {h['vista']}" for h in encontrados)


def secretos(ejecutar: Callable, rango: list[str]) -> list[dict]:
    """Busca credenciales en todos los commits del rango (argumentos de `git log`)."""
    p = ejecutar(["git", "log", "-p", "-U0", "--no-color", "--format=commit:%H", *rango])
    if p.returncode:
        raise PuertaRota(f"git no pudo leer los commits {' '.join(rango)}: {(getattr(p, 'stderr', '') or '').strip()[:200]}")
    return hallazgos(p.stdout)


def verificaciones(verificar: Callable, existe: Callable[[str], bool] | None = None) -> tuple[list[str], list[str], list[str]]:
    """(problemas, avisos, omitidas): corre agentes, kb y resumen con --verificar (todas, aunque una falle).

    Una guía vieja es un problema (bloquea); un kb o un resumen vencidos son un aviso; una verificación cuyo archivo todavía no existe se
    omite: no hay nada vencido que corregir, y bloquear el primer push de un proyecto nuevo sería hostil."""
    problemas, avisos, omitidas = [], [], []
    for nombre, archivo, bloquea in VERIFICACIONES:
        if existe is not None and not existe(archivo):
            omitidas.append(nombre)
            continue
        codigo, salida = verificar([nombre, "--verificar"])
        if codigo:
            primera = next((l.strip() for l in (salida or "").splitlines() if l.strip()), "falló sin mensaje")
            (problemas if bloquea else avisos).append(f"{nombre}: {primera[:200]}")
    return problemas, avisos, omitidas


def correr(ejecutar: Callable, rangos: list[list[str]], verificar: Callable, existe: Callable[[str], bool] | None = None) -> tuple[int, str]:
    """(código, texto): 0 si todo pasa, CODIGO_BLOQUEO si alguna comprobación encuentra algo."""
    encontrados = [h for rango in rangos for h in secretos(ejecutar, rango)]
    problemas, avisos, omitidas = verificaciones(verificar, existe)
    lineas = ["Puerta local de salida:"]
    if encontrados:
        lineas += [f"  ✗ secretos: {len(encontrados)} hallazgo(s) en los commits que se publican", texto_de_hallazgos(encontrados)]
    else:
        lineas.append("  ✓ secretos: ninguno en los commits que se publican")
    if problemas:
        lineas += ["  ✗ verificaciones:", *[f"      {p}" for p in problemas]]
    else:
        hechas = [n for n, _, _ in VERIFICACIONES if n not in omitidas and not any(a.startswith(n + ":") for a in avisos)]
        lineas.append("  ✓ verificaciones: " + (", ".join(hechas) + " al día" if hechas else "ninguna aplicable")
                      + (f" (se omiten {', '.join(omitidas)}: el proyecto todavía no los generó)" if omitidas else ""))
    if avisos:
        lineas += ["  ! vencidos, no bloquean (se rehacen al integrar):", *[f"      {a}" for a in avisos]]
    if encontrados or problemas:
        lineas.append("La puerta no deja pasar el push. Arreglalo; si sabés lo que hacés, salteala con git push --no-verify "
                      f"(para una línea de ejemplo conocida, agregale {EXENCION}).")
        return CODIGO_BLOQUEO, "\n".join(lineas) + "\n"
    return 0, "\n".join(lineas) + "\n"


def rangos_del_hook(entrada: str, ejecutar: Callable) -> list[list[str]]:
    """Los rangos a mirar a partir de lo que Git le pasa al pre-push: «ref_local sha_local ref_remota sha_remoto» por línea.

    Un borrado no se mira; una rama nueva (o un sha remoto que no tenemos) se mira desde lo que ningún remoto tiene."""
    cero, rangos = "0" * 40, []
    for linea in entrada.splitlines():
        partes = linea.split()
        if len(partes) != 4 or not re.fullmatch(r"[0-9a-f]{40}", partes[1]) or not re.fullmatch(r"[0-9a-f]{40}", partes[3]):
            continue
        local, remoto = partes[1], partes[3]
        if local == cero:
            continue  # borrar una rama remota: no hay nada nuevo que publicar
        if remoto != cero and ejecutar(["git", "cat-file", "-e", f"{remoto}^{{commit}}"]).returncode == 0:
            rangos.append([f"{remoto}..{local}"])
        else:
            rangos.append([local, "--not", "--remotes"])
    return rangos
