"""Archivo: fusionar la spec delta de un cambio en la spec consolidada de su capacidad.

Puro: recibe textos y devuelve textos; quien llama lee y escribe los archivos. Un requisito se identifica por su
nombre (`### Requirement: <nombre>`), como en OpenSpec. La spec consolidada es una vista para leer; el índice
(`.factory/specs/<capacidad>.json`) guarda de qué cambio y requisito de Oracle viene cada uno y qué reemplazó.
"""
from __future__ import annotations

import re

from . import modos

OPERACIONES = ('ADDED', 'MODIFIED', 'REMOVED')
CABECERA_DELTA = re.compile(r'^##\s+(ADDED|MODIFIED|REMOVED|RENAMED)\s+Requirements\s*$')
CABECERA_REQ = re.compile(r'^###\s+Requirement:\s*(.+?)\s*$')
ORIGEN = re.compile(r'^Origen: (\S+) · (\S+)$')
AVISO = '<!-- Generada por Oracle Factory al cerrar cada cambio: no se edita a mano. -->'


class Conflicto(ValueError):
    pass


def bloques(texto: str) -> list[tuple[str, str, list[str]]]:
    """[(operación, nombre, líneas del cuerpo)]; sin encabezados de delta, todo es ADDED."""
    resultado, operacion, actual = [], 'ADDED', None
    for linea in texto.splitlines():
        delta = CABECERA_DELTA.match(linea)
        if delta:
            if delta[1] == 'RENAMED':
                raise Conflicto('RENAMED no está soportado: quitá el requisito y agregalo con el nombre nuevo')
            operacion, actual = delta[1], None
            continue
        cabecera = CABECERA_REQ.match(linea)
        if cabecera:
            actual = (operacion, cabecera[1], [])
            resultado.append(actual)
            continue
        if linea.startswith('## ') or linea.startswith('# '):
            actual = None
            continue
        if actual is not None:
            actual[2].append(linea)
    return [(op, nombre, _recortar(cuerpo)) for op, nombre, cuerpo in resultado]


def _recortar(lineas: list[str]) -> list[str]:
    while lineas and not lineas[0].strip():
        lineas = lineas[1:]
    while lineas and not lineas[-1].strip():
        lineas = lineas[:-1]
    return lineas


def indice_vacio(capacidad: str) -> dict:
    return {'capacidad': capacidad, 'archivados': [], 'requisitos': {}, 'reemplazados': []}


def fusionar(indice: dict, delta: str, ident: str, dominio_por_slug: dict[str, str]) -> dict:
    """El índice nuevo tras fusionar la spec `delta` del cambio `ident`. Lanza Conflicto sin modificar nada.

    `dominio_por_slug` lleva cada slug de requisito al id de Oracle importado por ese cambio.
    """
    if ident in indice['archivados']:
        return indice  # ya fusionado: archivar de nuevo no cambia nada
    nuevo = {'capacidad': indice['capacidad'], 'archivados': [*indice['archivados'], ident],
             'requisitos': dict(indice['requisitos']), 'reemplazados': list(indice['reemplazados'])}
    conflictos = []
    for operacion, nombre, cuerpo in bloques(delta):
        existe = nombre in nuevo['requisitos']
        if operacion == 'ADDED' and existe:
            conflictos.append(f'«{nombre}» ya existe en la capacidad {indice["capacidad"]}; para cambiarlo usá MODIFIED')
            continue
        if operacion in ('MODIFIED', 'REMOVED') and not existe:
            conflictos.append(f'«{nombre}» no existe en la capacidad {indice["capacidad"]}; no se puede {operacion}')
            continue
        if existe:  # MODIFIED conserva su lugar en la spec; REMOVED lo saca
            anterior = nuevo['requisitos'].pop(nombre) if operacion == 'REMOVED' else nuevo['requisitos'][nombre]
            nuevo['reemplazados'].append({'nombre': nombre, **anterior, 'por_cambio': ident, 'operacion': operacion})
        if operacion == 'REMOVED':
            continue
        requisito = dominio_por_slug.get(modos.slug(nombre))
        if requisito is None:
            conflictos.append(f'«{nombre}» no tiene requisito de Oracle importado en {ident}')
            continue
        nuevo['requisitos'][nombre] = {'cambio': ident, 'requisito': requisito, 'cuerpo': cuerpo}
    if conflictos:
        raise Conflicto('; '.join(conflictos))
    return nuevo


def texto_consolidado(indice: dict) -> str:
    """La spec consolidada, en el orden en que entró cada requisito."""
    lineas = [f'# Capability: {indice["capacidad"]}', '', AVISO, '', '## Requirements']
    for nombre, req in indice['requisitos'].items():
        lineas += ['', f'### Requirement: {nombre}', f'Origen: {req["cambio"]} · {req["requisito"]}', *req['cuerpo']]
    return '\n'.join(lineas) + '\n'


def situacion(indice: dict, requisito: str) -> tuple[str, str | None]:
    """('vigente', None), ('reemplazado', cambio que lo reemplazó) o ('ausente', None)."""
    if any(r['requisito'] == requisito for r in indice['requisitos'].values()):
        return 'vigente', None
    for r in indice['reemplazados']:
        if r['requisito'] == requisito:
            return 'reemplazado', r['por_cambio']
    return 'ausente', None


if __name__ == '__main__':
    base = '# Capability: x\n\n## ADDED Requirements\n\n### Requirement: uno\nTipo: funcional\nA SHALL b.\n'
    i = fusionar(indice_vacio('x'), base, 'c1', {'uno': 'x_c1.uno'})
    assert situacion(i, 'x_c1.uno') == ('vigente', None)
    i2 = fusionar(i, '## MODIFIED Requirements\n### Requirement: uno\nA SHALL c.\n', 'c2', {'uno': 'x_c2.uno'})
    assert situacion(i2, 'x_c1.uno') == ('reemplazado', 'c2') and 'A SHALL c.' in texto_consolidado(i2)
    assert fusionar(i2, '', 'c2', {}) is i2
    try:
        fusionar(i, base, 'c3', {'uno': 'x_c3.uno'})
        raise AssertionError('debía haber conflicto')
    except Conflicto as e:
        assert 'uno' in str(e)
    print('ok')
