"""La skill de agente: el procedimiento para trabajar un cambio con Factory, como texto que viaja con el paquete.

`oracle-factory skill` lo muestra y `oracle-factory skill --instalar` lo escribe en el proyecto (nunca fuera de él). Una prueba lo contrasta con el
código —comandos, umbrales y documentos— para que no se desactualice (`problemas`)."""
from __future__ import annotations

from importlib import resources
from pathlib import Path
import re

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


def comandos_nombrados(contenido: str) -> set[str]:
    """Los verbos de los fragmentos de código que empiezan con `oracle-factory` (`--agente NOMBRE nuevo …` → nuevo). Un fragmento sin verbo
    (un marcador como `…` o un nombre en mayúsculas) se ignora."""
    verbos = set()
    for fragmento in re.findall(r"`(oracle-factory[^`]*)`", contenido):
        palabras = fragmento.split()[1:]
        while palabras and palabras[0].startswith("--"):
            opcion = palabras.pop(0)
            if opcion in OPCIONES_CON_VALOR and palabras:
                palabras.pop(0)
        if palabras and re.fullmatch(r"[a-z][a-z-]*", palabras[0]):
            verbos.add(palabras[0])
    return verbos


def numeros_antes_de(contenido: str, palabra: str) -> set[int]:
    return {int(n) for n in re.findall(rf"(\d+) {palabra}\b", contenido)}


def documentos_enlazados(contenido: str) -> set[str]:
    return set(re.findall(r"`(docs/[\w.-]+\.md)`", contenido))


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
    existe = destino.exists()
    if existe and destino.read_text(encoding="utf-8") == nuevo:
        return "igual", destino
    if existe and not forzar:
        raise SkillError(f"ya hay un {RUTA_EN_EL_PROYECTO} distinto; --forzar lo reemplaza")
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(nuevo, encoding="utf-8")
    return ("reemplazada" if existe else "instalada"), destino
