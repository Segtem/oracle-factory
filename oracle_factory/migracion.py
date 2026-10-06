"""Fase 2 de la estructura: pasar el estado de cada cambio y la configuración a .factory/.

Mueve `factory.json`, `review.md` y `oracle-veredicto.txt` de `openspec/changes/<ID>/` a `.factory/cambios/<ID>/` y el
`factory.json` de la raíz a `.factory/config.json`. En el registro sólo reescribe las rutas que citan los archivos
movidos. Escribe lo nuevo antes de borrar lo viejo, y el registro al final: una interrupción se repara volviendo a correr.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from . import estructura

ESTADO = ('review.md', 'oracle-veredicto.txt', 'factory.json')  # el registro va último
ID_RE = estructura.ID_RE
CLAVES_CONFIG = {'modo_por_defecto', 'tipos_obligatorios'}


def _enlazado(raiz: Path, ruta: Path) -> Path | None:
    """El primer enlace simbólico en el camino de `ruta` bajo `raiz`, que no se debe seguir al escribir."""
    actual = raiz
    for parte in ruta.relative_to(raiz).parts:
        actual = actual / parte
        if actual.is_symlink():
            return actual
    return None


def _es_configuracion(ruta: Path) -> bool:
    try:
        datos = json.loads(ruta.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return False
    return isinstance(datos, dict) and set(datos) <= CLAVES_CONFIG


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
            registro_presente = (carpeta / 'factory.json').is_file() or (raiz / estructura.DIR / 'cambios' / carpeta.name / 'factory.json').is_file()
            if not registro_presente:  # sin registro no es un cambio de Factory: no se mueve nada de esa carpeta
                huerfanos = [n for n in ESTADO if (carpeta / n).exists()]
                if huerfanos:
                    problemas.append(f'{carpeta.relative_to(raiz)} tiene {", ".join(huerfanos)} pero ningún registro: no los toco')
                continue
            for nombre in ESTADO:
                origen = carpeta / nombre
                if origen.is_file() and not origen.is_symlink():
                    pares.append((carpeta.name, origen, raiz / estructura.DIR / 'cambios' / carpeta.name / nombre, nombre))
    config = raiz / 'factory.json'
    if config.is_file() and not config.is_symlink():
        if _es_configuracion(config):
            pares.append(('configuración', config, raiz / estructura.DIR / 'config.json', 'config'))
        else:
            problemas.append('factory.json de la raíz no es una configuración de Factory (sólo modo_por_defecto y '
                             'tipos_obligatorios): no lo toco')
    if (raiz / estructura.DIR).is_symlink():
        return [], [f'{estructura.DIR} es un enlace simbólico: no migro a través de él']
    malos: set[str] = set()
    for cambio, origen, destino, nombre in pares:
        esperado = _esperado(origen, nombre, cambio)
        enlace = _enlazado(raiz, destino)
        if enlace is not None:  # ni el archivo ni ninguna carpeta del camino: escribir a través de un enlace sale del proyecto
            problemas.append(f'{enlace.relative_to(raiz)} es un enlace simbólico: no escribo a través de él')
            malos.add(cambio)
            continue
        if destino.is_file():
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
