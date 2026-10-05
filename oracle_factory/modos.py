"""Quién puede tomar cada decisión según el modo de trabajo del cambio.

Factory no autentica actores: distingue la vía de persona (terminal interactiva)
de la vía de agente (--agente) y registra cuál se usó.
"""
from __future__ import annotations

import re
import unicodedata

MODOS = ('autonomo', 'funcional', 'confirmacion')
POR_DEFECTO = 'confirmacion'
# Cuánto interviene la persona: bajar de nivel exige una persona.
INTERVENCION = {'autonomo': 0, 'funcional': 1, 'confirmacion': 2}
TIPOS = ('funcional', 'no funcional')
DECISIONES = ('spec', 'medidas', 'revision', 'cierre')


class TipoInvalido(ValueError):
    pass


def via_agente(modo: str, decision: str, tipos: list[str]) -> str:
    """Qué produce la vía de agente: 'decide', 'propone' o 'rechaza'.

    tipos son los de los requisitos afectados por la decisión. La vía de persona
    siempre decide: es la intervención más alta en cualquier modo.
    """
    if modo not in MODOS or decision not in DECISIONES:
        raise ValueError(f'modo o decisión desconocidos: {modo}, {decision}')
    if modo == 'autonomo':
        return 'decide'
    if decision == 'cierre':
        return 'rechaza'
    if modo == 'confirmacion':
        return 'propone'
    # funcional: la persona decide lo funcional; el agente, lo no funcional.
    return 'rechaza' if 'funcional' in tipos else 'decide'


def baja_intervencion(actual: str, nuevo: str) -> bool:
    return INTERVENCION[nuevo] < INTERVENCION[actual]


def slug(texto: str) -> str:
    ascii_ = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '_', ascii_.lower()).strip('_')


def tipos_spec(texto: str, *, obligatorios: bool = False) -> dict[str, str]:
    """{slug del requisito: tipo}. Sin línea «Tipo:», funcional, salvo tipos obligatorios."""
    tipos, actual, sin_tipo = {}, None, []
    for linea in texto.splitlines():
        cabecera = re.match(r'^###\s+Requirement:\s*(.+?)\s*$', linea)
        if cabecera:
            actual = slug(cabecera[1])
            tipos[actual] = None
            continue
        if linea.startswith('#'):
            if not linea.startswith('####'):
                actual = None
            continue
        declarado = re.match(r'^\s*(?:-\s*)?Tipo:\s*(.+?)\s*$', linea, re.IGNORECASE)
        if declarado and actual is not None:
            valor = declarado[1].lower()
            if valor not in TIPOS:
                raise TipoInvalido(f'requisito {actual}: tipo desconocido «{declarado[1]}»; usá funcional o no funcional')
            if tipos[actual] is not None:
                raise TipoInvalido(f'requisito {actual}: tipo declarado dos veces')
            tipos[actual] = valor
    for nombre, tipo in tipos.items():
        if tipo is None:
            sin_tipo.append(nombre)
            tipos[nombre] = 'funcional'
    if obligatorios and sin_tipo:
        raise TipoInvalido('el proyecto exige tipos (tipos_obligatorios) y no lo declaran: ' + ', '.join(sin_tipo))
    return tipos
