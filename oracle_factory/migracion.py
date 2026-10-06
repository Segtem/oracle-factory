"""Fase 2 de la estructura: pasar el estado de cada cambio y la configuración a .factory/.

Mueve `factory.json`, `review.md` y `oracle-veredicto.txt` de `openspec/changes/<ID>/` a `.factory/cambios/<ID>/` y el
`factory.json` de la raíz a `.factory/config.json`. En el registro sólo reescribe las rutas que citan los archivos
movidos. Escribe lo nuevo antes de borrar lo viejo, y el registro al final: una interrupción se repara volviendo a correr.
"""
from __future__ import annotations

import os
from pathlib import Path

from . import estructura

ESTADO = ('review.md', 'oracle-veredicto.txt', 'factory.json')  # el registro va último
ID_RE = estructura.ID_RE


def _reescrito(contenido: bytes, ident: str) -> bytes:
    """El registro con las rutas citadas de los archivos movidos; el resto, byte a byte (el reemplazo es de texto)."""
    texto = contenido.decode('utf-8')
    for nombre in ('review.md', 'oracle-veredicto.txt'):
        texto = texto.replace(f'"openspec/changes/{ident}/{nombre}"', f'"{estructura.DIR}/cambios/{ident}/{nombre}"')
    return texto.encode('utf-8')


def _esperado(origen: Path, nombre: str, ident: str) -> bytes:
    datos = origen.read_bytes()
    return _reescrito(datos, ident) if nombre == 'factory.json' else datos


def planear(raiz: Path) -> tuple[list[dict], list[str]]:
    """(movimientos, problemas). Un movimiento: {'cambio', 'origen', 'destino', 'bytes', 'estado'} con estado
    'escribir' (el destino no existe) o 'borrar_viejo' (el destino ya es el esperado). No escribe nada."""
    movimientos: list[dict] = []
    problemas: list[str] = []
    cambios = raiz / 'openspec' / 'changes'
    pares: list[tuple[str, Path, Path, str]] = []  # (cambio, origen, destino, nombre)
    if cambios.is_dir():
        for carpeta in sorted(cambios.iterdir()):
            if not ID_RE.fullmatch(carpeta.name) or carpeta.is_symlink():
                continue
            for nombre in ESTADO:
                origen = carpeta / nombre
                if origen.is_file() and not origen.is_symlink():
                    pares.append((carpeta.name, origen, raiz / estructura.DIR / 'cambios' / carpeta.name / nombre, nombre))
    config = raiz / 'factory.json'
    if config.is_file() and not config.is_symlink():
        pares.append(('configuración', config, raiz / estructura.DIR / 'config.json', 'config'))
    if (raiz / estructura.DIR).is_symlink():
        return [], [f'{estructura.DIR} es un enlace simbólico: no migro a través de él']
    malos: set[str] = set()
    for cambio, origen, destino, nombre in pares:
        esperado = _esperado(origen, nombre, cambio)
        if destino.is_symlink():
            problemas.append(f'{destino.relative_to(raiz)} es un enlace simbólico')
            malos.add(cambio)
        elif destino.is_file():
            if destino.read_bytes() == esperado:
                estado = 'borrar_viejo'
            else:
                problemas.append(f'{cambio}: {destino.relative_to(raiz)} existe y difiere de {origen.relative_to(raiz)}; no toco ninguno')
                malos.add(cambio)
                continue
        elif destino.exists():
            problemas.append(f'{destino.relative_to(raiz)} existe y no es un archivo')
            malos.add(cambio)
            continue
        else:
            estado = 'escribir'
        movimientos.append({'cambio': cambio, 'origen': origen, 'destino': destino, 'bytes': esperado, 'estado': estado})
    # un cambio con un problema no se mueve a medias
    return [m for m in movimientos if m['cambio'] not in malos], problemas


def _escribir_atomico(destino: Path, datos: bytes) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = destino.with_name(destino.name + '.migracion')
    temporal.write_bytes(datos)
    os.replace(temporal, destino)


def aplicar(movimientos: list[dict]) -> int:
    """Escribe los destinos que faltan, comprueba cada uno leyéndolo de nuevo y recién entonces borra los viejos."""
    for m in movimientos:
        if m['estado'] == 'escribir':
            _escribir_atomico(m['destino'], m['bytes'])
    for m in movimientos:
        if m['destino'].read_bytes() != m['bytes']:
            raise RuntimeError(f'{m["destino"]}: lo escrito no es lo esperado; no borré nada')
    for m in movimientos:
        m['origen'].unlink()
    return len(movimientos)
