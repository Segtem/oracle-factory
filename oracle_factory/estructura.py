"""Dónde está cada cosa: la carpeta .factory/, el descubrimiento de la raíz y los comandos de sólo lectura.

Nada de lo que hay acá escribe en el proyecto: ruta imprime una ruta y no crea la carpeta.
"""
from __future__ import annotations

import json
from pathlib import Path
import re

DIR = '.factory'
IGNORAR_LOCAL = '.factory/local/'
# Los paquetes de Clue son de cada máquina, como los checkouts: pesan (cientos de KB, más que lo que Clue acepta en un diff)
# y guardan la ruta absoluta del checkout que revisaron. Se versionan los informes de los revisores, no los paquetes.
IGNORAR_CLUE = '.factory/cambios/*/candidatos/*/clue/'
TIPOS = ('evidencia', 'clue', 'revision', 'checkout')
SUBCARPETAS = ('evidencia', 'clue', 'revision')
ID_RE = re.compile(r'^\d{8}-\d{6}-[a-z0-9_-]+$')
SUFIJOS_TEXTO = ('.md', '.json', '.requisito', '.txt')
LIMITE_ARCHIVO = 1_000_000


def es_proyecto_anterior(carpeta: Path) -> bool:
    """Un proyecto Factory de antes de .factory/: tiene la configuración de Oracle y los acuerdos."""
    return (carpeta / 'oracle.json').is_file() and (carpeta / 'openspec' / 'changes').is_dir()


def raiz_del_proyecto(desde: Path) -> Path | None:
    """La primera carpeta, subiendo desde `desde`, que tiene .factory/; None si ninguna.

    Un proyecto anterior sin .factory/ es una frontera: no hereda el proyecto de afuera. La carpeta
    personal del usuario nunca es la raíz (otras herramientas usan ~/.factory) y un enlace simbólico
    llamado .factory no cuenta como marcador.
    """
    casa = Path.home().resolve()
    for carpeta in (desde, *desde.parents):
        marcador = carpeta / DIR
        if carpeta.resolve() != casa and marcador.is_dir() and not marcador.is_symlink():
            return carpeta
        if es_proyecto_anterior(carpeta):
            return None
    return None


def registro_de(raiz: Path, ident: str) -> Path:
    """El registro de un cambio: .factory/cambios/<ID>/factory.json; si sólo está en el lugar anterior a la fase 2, ahí."""
    nuevo = raiz / DIR / 'cambios' / ident / 'factory.json'
    viejo = raiz / 'openspec' / 'changes' / ident / 'factory.json'
    return viejo if viejo.is_file() and not nuevo.is_file() else nuevo


def es_anterior(raiz: Path, ident: str) -> bool:
    return registro_de(raiz, ident).parent == raiz / 'openspec' / 'changes' / ident


def ruta_canonica(raiz: Path, ident: str, tipo: str, sha7: str) -> Path:
    if tipo not in TIPOS:
        raise ValueError(f'tipo desconocido «{tipo}»; los válidos son: {", ".join(TIPOS)}')
    if tipo == 'checkout':
        return raiz / DIR / 'local' / 'revisiones' / sha7
    return raiz / DIR / 'cambios' / ident / 'candidatos' / sha7 / tipo


def _texto(valor) -> str | None:
    return valor if isinstance(valor, str) and valor and '\x00' not in valor else None


def _dic(valor) -> dict:
    return valor if isinstance(valor, dict) else {}


def _entrada(gate: str, ruta, raiz: Path, nota: str = '') -> dict:
    if _texto(ruta) is None:
        return {'gate': gate, 'ruta': '(valor no válido en el registro)', 'existe': False,
                'nota': 'el registro no tiene una ruta de texto', 'invalida': True}
    try:
        existe = (raiz / ruta).exists()
    except (OSError, ValueError):
        existe = False
    if ruta.startswith('/') and not nota:
        nota = 'ruta absoluta de un registro anterior a la portabilidad; sólo vale en la máquina que la escribió'
    return {'gate': gate, 'ruta': ruta, 'existe': existe, 'nota': nota}


def donde(raiz: Path, ident: str, estado: dict, candidato: str | None = None) -> list[dict]:
    """Cada artefacto del cambio con su ruta, si existe y el gate que respalda."""
    cambio = f'openspec/changes/{ident}'
    prefijo = (candidato or '').lower()

    def del_candidato(head) -> bool:
        return not prefijo or (isinstance(head, str) and head.lower().startswith(prefijo))

    filas: list[dict] = []
    if not prefijo:
        for nombre, gate in (('proposal.md', 'acuerdo'), ('design.md', 'acuerdo'), ('tasks.md', 'acuerdo')):
            filas.append(_entrada(gate, f'{cambio}/{nombre}', raiz))
        filas.append(_entrada('spec', estado.get('spec'), raiz))
        requisitos = estado.get('requisitos')
        for rid in (requisitos if isinstance(requisitos, list) else []):
            filas.append(_entrada('medidas', f'requisitos/{rid}.requisito' if _texto(rid) else None, raiz))
        if _texto(_dic(estado.get('archivo')).get('spec')):
            filas.append(_entrada('archivo', estado['archivo']['spec'], raiz, 'spec consolidada de la capacidad'))
        filas.append(_entrada('estado', registro_de(raiz, ident).relative_to(raiz).as_posix(), raiz,
                              'anterior a la fase 2: `oracle-factory migrar` lo pasa a .factory/' if es_anterior(raiz, ident) else ''))
        filas.append(_entrada('tarea', f'tareas/{ident}/TAREA.md', raiz))
    rev = _dic(estado.get('revision'))
    if rev and del_candidato(_dic(rev.get('contexto')).get('head')):
        for clave in ('informe', 'decisiones'):
            if clave in rev and rev[clave] is not None:
                filas.append(_entrada('revisión', rev[clave], raiz))
    oracle = _dic(estado.get('oracle'))
    if oracle and del_candidato(_dic(oracle.get('contexto')).get('head')):
        for clave in ('informe', 'hechos'):
            if clave in oracle and oracle[clave] is not None:
                filas.append(_entrada('juicio', oracle[clave], raiz))
    candidatos = raiz / DIR / 'cambios' / ident / 'candidatos'
    if candidatos.is_dir() and not (raiz / DIR).is_symlink():  # un .factory enlazado no es nuestra carpeta
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


def _fragmento(linea: str, aguja: str) -> str:
    """Hasta 160 caracteres de la línea, empezando poco antes de la coincidencia para que se vea."""
    linea = linea.strip()
    posicion = linea.casefold().find(aguja)
    # casefold puede alargar el texto («ß» → «ss»): se pasa la posición de la forma plegada al índice de la línea.
    acumulado = 0
    for indice, letra in enumerate(linea):
        acumulado += len(letra.casefold())
        if acumulado > posicion:
            posicion = indice
            break
    inicio = max(0, posicion - 60) if posicion > 100 else 0
    return ('…' if inicio else '') + linea[inicio:inicio + 160]


def buscar(raiz: Path, texto: str, maximo: int = 200) -> tuple[list[str], int, int]:
    """Coincidencias (texto literal, sin distinguir mayúsculas ni formas equivalentes) en propuestas, specs,
    requisitos, tareas y registros. Devuelve las líneas, el total y los archivos omitidos por tamaño."""
    aguja = texto.casefold()
    por_requisito: dict[str, str] = {}
    cambios = raiz / 'openspec' / 'changes'
    if cambios.is_dir():
        for carpeta in cambios.iterdir():
            registro = registro_de(raiz, carpeta.name)
            if registro.is_file() and not ((raiz / DIR).is_symlink() and registro.is_relative_to(raiz / DIR)):
                try:
                    for rid in json.loads(registro.read_text(encoding='utf-8')).get('requisitos', []):
                        por_requisito[rid] = carpeta.name
                except (OSError, ValueError):
                    continue
    lugares = [raiz / 'openspec' / 'changes', raiz / 'openspec' / 'specs', raiz / 'requisitos', raiz / 'tareas']
    if not (raiz / DIR).is_symlink():  # un .factory enlazado no es nuestra carpeta: no se lee a través de él
        lugares.append(raiz / DIR / 'cambios')
    archivos = sorted(p for lugar in lugares if lugar.is_dir() and not lugar.is_symlink() for p in lugar.rglob('*')
                      if p.is_file() and p.suffix in SUFIJOS_TEXTO and not p.is_symlink())
    lineas, total, omitidos = [], 0, 0
    for archivo in archivos:
        # tareas/: sólo los textos de las tareas; la evidencia en JSON es enorme y está atada a hashes.
        if archivo.relative_to(raiz).parts[0] == 'tareas' and archivo.suffix != '.md':
            continue
        try:
            if archivo.stat().st_size > LIMITE_ARCHIVO:
                omitidos += 1
                continue
            contenido = archivo.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            continue
        for numero, linea in enumerate(contenido.splitlines(), 1):
            if aguja in linea.casefold():
                total += 1
                if len(lineas) < maximo:
                    relativa = archivo.relative_to(raiz).as_posix()
                    lineas.append(f'{relativa}:{numero}: {_fragmento(linea, aguja)}  [{_cambio_de(archivo, raiz, por_requisito)}]')
    return lineas, total, omitidos
