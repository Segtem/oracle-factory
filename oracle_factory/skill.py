"""La skill de agente: el procedimiento para trabajar un cambio con Factory, como texto que viaja con el paquete.

`oracle-factory skill` lo muestra y `oracle-factory skill --instalar` lo escribe en el proyecto (nunca fuera de él). Una prueba lo contrasta con el
código —comandos, umbrales y documentos— para que no se desactualice (`problemas`)."""
from __future__ import annotations

from importlib import resources
import os
from pathlib import Path
import re
import tempfile

from . import alarmas

RUTA_EN_EL_PROYECTO = Path(".claude") / "skills" / "oracle-factory" / "SKILL.md"
OPCIONES_CON_VALOR = {"--agente", "--proyecto"}  # las únicas globales que llevan un valor y van antes del subcomando
UMBRAL_DE_PASO = 50  # la condición de parada «un paso de más de 50 líneas» es de la skill, no del código


class SkillError(Exception):
    """No se pudo instalar la skill (un archivo ajeno en el camino, un enlace simbólico)."""


def texto() -> str:
    return (resources.files("oracle_factory") / "data" / "skill" / "SKILL.md").read_text(encoding="utf-8")


def encabezado(contenido: str) -> dict[str, str]:
    """Las claves `clave: valor` del encabezado entre «---» (sin YAML: una por línea)."""
    m = re.match(r"^---\n(.*?)\n---\n", contenido, re.DOTALL)
    return {k: v.strip() for k, v in (l.split(":", 1) for l in (m[1].splitlines() if m else []) if ":" in l)}


def _regiones_de_codigo(contenido: str) -> list[str]:
    """Los bloques cercados (``` o ~~~) y los fragmentos entre backticks, donde la skill escribe comandos."""
    cercados = re.findall(r"^[ \t]*(?:```|~~~)[^\n]*\n(.*?)^[ \t]*(?:```|~~~)[ \t]*$", contenido, re.DOTALL | re.MULTILINE)
    sin_cercados = re.sub(r"^[ \t]*(?:```|~~~)[^\n]*\n.*?^[ \t]*(?:```|~~~)[ \t]*$", "", contenido, flags=re.DOTALL | re.MULTILINE)
    return cercados + re.findall(r"`([^`\n]+)`", sin_cercados)


def comandos_nombrados(contenido: str) -> set[str]:
    """Los verbos de cada `oracle-factory …` dentro de un fragmento o bloque de código, también encadenado con `&&`, `;`, `|` o `$(…)`
    (`--agente NOMBRE nuevo …` → nuevo). Un comando sin verbo (un marcador como `…` o un nombre en mayúsculas) se ignora."""
    verbos = set()
    for region in _regiones_de_codigo(contenido):
        for trozo in re.split(r"&&|\|\||[;&|\n]|\$\(|\)", region):
            palabras = trozo.split()
            if not palabras or palabras[0].rsplit("/", 1)[-1] != "oracle-factory":  # también `.venv/bin/oracle-factory`
                continue
            palabras = palabras[1:]
            while palabras and palabras[0].startswith("--"):
                opcion = palabras.pop(0)
                if opcion in OPCIONES_CON_VALOR and palabras:
                    palabras.pop(0)
            if palabras and re.fullmatch(r"[a-z][a-z0-9_-]*", palabras[0]):  # un verbo mal escrito (`pedir_revision`) se reporta, no se ignora
                verbos.add(palabras[0])
    return verbos


def numeros_antes_de(contenido: str, palabra: str) -> set[int]:
    return {int(n) for n in re.findall(rf"(\d+)\s+{palabra}\b", contenido)}


def documentos_enlazados(contenido: str) -> set[str]:
    """`docs/x.md` entre backticks o como destino de un enlace Markdown."""
    return set(re.findall(r"(?<![\w/.-])(docs/[\w.-]+\.md)", contenido))


def subcomandos() -> set[str]:
    import argparse
    from .parser import construir_parser
    return {nombre for a in construir_parser()._actions if isinstance(a, argparse._SubParsersAction) for nombre in a.choices}


def problemas(contenido: str, raiz: Path, validos: set[str] | None = None) -> list[str]:
    """Lo que la skill dice y el código desmiente: encabezado, comandos que no existen, umbrales viejos, documentos que faltan."""
    salida = []
    cabecera = encabezado(contenido)
    if cabecera.get("name") != "oracle-factory" or not cabecera.get("description"):
        salida.append("el encabezado necesita name: oracle-factory y una description")
    validos = subcomandos() if validos is None else validos
    salida += [f"nombra el comando oracle-factory {c}, que no existe" for c in sorted(comandos_nombrados(contenido) - validos)]
    lineas, rondas = numeros_antes_de(contenido, "líneas"), numeros_antes_de(contenido, "rondas")
    permitidas = {alarmas.UMBRAL_LINEAS, alarmas.UMBRAL_LIGERO, UMBRAL_DE_PASO}
    salida += [f"cita {n} líneas y el código dice {alarmas.UMBRAL_LINEAS} (tamaño) y {alarmas.UMBRAL_LIGERO} (camino ligero)" for n in sorted(lineas - permitidas)]
    salida += [f"no cita el umbral de {n} líneas del código" for n in (alarmas.UMBRAL_LINEAS, alarmas.UMBRAL_LIGERO) if n not in lineas]
    salida += [f"cita {n} rondas y el código dice {alarmas.UMBRAL_RONDAS}" for n in sorted(rondas - {alarmas.UMBRAL_RONDAS})]
    if alarmas.UMBRAL_RONDAS not in rondas:
        salida.append(f"no cita el umbral de {alarmas.UMBRAL_RONDAS} rondas del código")
    salida += [f"enlaza {d}, que no existe" for d in sorted(documentos_enlazados(contenido)) if not (raiz / d).is_file()]
    return salida


def instalar(raiz: Path, forzar: bool = False) -> tuple[str, Path]:
    """Escribe la skill en `raiz/.claude/skills/oracle-factory/SKILL.md`: ('instalada'|'igual'|'reemplazada', ruta). Nunca sigue un enlace
    simbólico y nunca pisa un archivo distinto sin `forzar`."""
    destino = raiz / RUTA_EN_EL_PROYECTO
    cadena = [destino, *destino.parents]
    enlaces = [str(p.relative_to(raiz)) for p in cadena if p != raiz and raiz in p.parents and p.is_symlink()]
    if enlaces:
        raise SkillError(f"no escribo sobre enlaces simbólicos: {', '.join(enlaces)}")
    nuevo = texto()
    existe = destino.exists() or destino.is_symlink()
    temporal = None
    try:
        if existe and not destino.is_file():
            raise SkillError(f"{RUTA_EN_EL_PROYECTO} existe y no es un archivo")
        if existe and destino.read_bytes() == nuevo.encode("utf-8"):  # bytes: un archivo ajeno que no es UTF-8 es «distinto», no un error
            return "igual", destino
        if existe and not forzar:
            raise SkillError(f"ya hay un {RUTA_EN_EL_PROYECTO} distinto; --forzar lo reemplaza")
        destino.parent.mkdir(parents=True, exist_ok=True)
        descriptor, nombre = tempfile.mkstemp(dir=destino.parent, prefix=".SKILL.md.", suffix=".tmp")  # un nombre nuevo: nunca pisa un archivo ajeno
        temporal = Path(nombre)
        with os.fdopen(descriptor, "w", encoding="utf-8") as f:
            f.write(nuevo)
        temporal.chmod(0o644)
        os.replace(temporal, destino)  # atómico: una interrupción no deja el archivo del usuario a medio escribir
    except OSError as e:
        raise SkillError(f"no pude escribir {RUTA_EN_EL_PROYECTO}: {e}") from e
    finally:
        if temporal is not None:
            temporal.unlink(missing_ok=True)  # sólo el que creó esta invocación (si ya se movió, no hay nada que borrar)
    return ("reemplazada" if existe else "instalada"), destino
