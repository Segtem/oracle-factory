"""Dónde está cada cosa: la carpeta .factory/, el descubrimiento de la raíz y los comandos de sólo lectura.

Nada de lo que hay acá escribe en el proyecto: ruta imprime una ruta y no crea la carpeta.
"""
from __future__ import annotations

import json
from pathlib import Path
import re

DIR = '.factory'
IGNORAR_LOCAL = '.factory/local/'
TIPOS = ('evidencia', 'clue', 'revision', 'checkout')
SUBCARPETAS = ('evidencia', 'clue', 'revision')
ID_RE = re.compile(r'^\d{8}-\d{6}-[a-z0-9_-]+$')
SUFIJOS_TEXTO = ('.md', '.json', '.requisito', '.txt')
LIMITE_ARCHIVO = 1_000_000


def raiz_del_proyecto(desde: Path) -> Path | None:
    """La primera carpeta, subiendo desde `desde`, que tiene .factory/; None si ninguna."""
    for carpeta in (desde, *desde.parents):
        if (carpeta / DIR).is_dir():
            return carpeta
    return None


def ruta_canonica(raiz: Path, ident: str, tipo: str, sha7: str) -> Path:
    if tipo not in TIPOS:
        raise ValueError(f'tipo desconocido «{tipo}»; los válidos son: {", ".join(TIPOS)}')
    if tipo == 'checkout':
        return raiz / DIR / 'local' / 'revisiones' / sha7
    return raiz / DIR / 'cambios' / ident / 'candidatos' / sha7 / tipo


def _entrada(gate: str, ruta: str, raiz: Path, nota: str = '') -> dict:
    existe = (raiz / ruta).exists()
    if ruta.startswith('/') and not nota:
        nota = 'ruta absoluta de un registro anterior a la portabilidad; sólo vale en la máquina que la escribió'
    return {'gate': gate, 'ruta': ruta, 'existe': existe, 'nota': nota}


def donde(raiz: Path, ident: str, estado: dict, candidato: str | None = None) -> list[dict]:
    """Cada artefacto del cambio con su ruta, si existe y el gate que respalda."""
    cambio = f'openspec/changes/{ident}'
    prefijo = (candidato or '').lower()

    def del_candidato(head: str | None) -> bool:
        return not prefijo or bool(head and head.lower().startswith(prefijo))

    filas: list[dict] = []
    if not prefijo:
        for nombre, gate in (('proposal.md', 'acuerdo'), ('design.md', 'acuerdo'), ('tasks.md', 'acuerdo')):
            filas.append(_entrada(gate, f'{cambio}/{nombre}', raiz))
        filas.append(_entrada('spec', estado.get('spec', f'{cambio}/specs/?/spec.md'), raiz))
        for rid in estado.get('requisitos', []):
            filas.append(_entrada('medidas', f'requisitos/{rid}.requisito', raiz))
        filas.append(_entrada('estado', f'{cambio}/factory.json', raiz))
        filas.append(_entrada('tarea', f'tareas/{ident}/TAREA.md', raiz))
    rev = estado.get('revision') or {}
    if rev and del_candidato((rev.get('contexto') or {}).get('head')):
        for clave in ('informe', 'decisiones'):
            if rev.get(clave):
                filas.append(_entrada('revisión', rev[clave], raiz))
    oracle = estado.get('oracle') or {}
    if oracle and del_candidato((oracle.get('contexto') or {}).get('head')):
        for clave in ('informe', 'hechos'):
            if oracle.get(clave):
                filas.append(_entrada('juicio', oracle[clave], raiz))
    candidatos = raiz / DIR / 'cambios' / ident / 'candidatos'
    if candidatos.is_dir():
        for carpeta in sorted(candidatos.iterdir()):
            if carpeta.is_dir() and (not prefijo or carpeta.name.lower().startswith(prefijo[:7])):
                for sub in SUBCARPETAS:
                    if (carpeta / sub).exists():
                        filas.append(_entrada('candidato', f'{DIR}/cambios/{ident}/candidatos/{carpeta.name}/{sub}', raiz))
    tarea = raiz / 'tareas' / ident
    if tarea.is_dir():
        for entrada in sorted(tarea.iterdir()):
            if entrada.name == 'TAREA.md' or (prefijo and prefijo not in entrada.name.lower()):
                continue
            filas.append(_entrada('histórico', f'tareas/{ident}/{entrada.name}', raiz,
                                  'nombre anterior a la estructura; no se mueve'))
    return filas


def _cambio_de(ruta: Path, raiz: Path, por_requisito: dict[str, str]) -> str:
    partes = ruta.relative_to(raiz).parts
    if partes[0] == 'requisitos':
        return por_requisito.get(ruta.name.removesuffix('.requisito'), '-')
    # openspec/changes/<ID>/…, tareas/<ID>/…, .factory/cambios/<ID>/…
    posicion = {'openspec': 2, 'tareas': 1, DIR: 2}.get(partes[0])
    if posicion is not None and len(partes) > posicion and ID_RE.fullmatch(partes[posicion]):
        return partes[posicion]
    return '-'


def buscar(raiz: Path, texto: str, maximo: int = 200) -> tuple[list[str], int]:
    """Coincidencias (texto literal, sin distinguir mayúsculas) en propuestas, specs, requisitos, tareas y registros."""
    aguja = texto.lower()
    por_requisito: dict[str, str] = {}
    cambios = raiz / 'openspec' / 'changes'
    if cambios.is_dir():
        for carpeta in cambios.iterdir():
            registro = carpeta / 'factory.json'
            if registro.is_file():
                try:
                    for rid in json.loads(registro.read_text(encoding='utf-8')).get('requisitos', []):
                        por_requisito[rid] = carpeta.name
                except (OSError, ValueError):
                    continue
    lugares = [raiz / 'openspec' / 'changes', raiz / 'requisitos', raiz / 'tareas', raiz / DIR / 'cambios']
    archivos = sorted(p for lugar in lugares if lugar.is_dir() for p in lugar.rglob('*')
                      if p.is_file() and p.suffix in SUFIJOS_TEXTO and not p.is_symlink())
    lineas, total = [], 0
    for archivo in archivos:
        # tareas/: sólo los textos de las tareas; la evidencia en JSON es enorme y está atada a hashes.
        if archivo.relative_to(raiz).parts[0] == 'tareas' and archivo.suffix != '.md':
            continue
        try:
            if archivo.stat().st_size > LIMITE_ARCHIVO:
                continue
            contenido = archivo.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            continue
        for numero, linea in enumerate(contenido.splitlines(), 1):
            if aguja in linea.lower():
                total += 1
                if len(lineas) < maximo:
                    relativa = archivo.relative_to(raiz).as_posix()
                    lineas.append(f'{relativa}:{numero}: {linea.strip()[:160]}  [{_cambio_de(archivo, raiz, por_requisito)}]')
    return lineas, total
