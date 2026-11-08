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
# Las etapas posteriores a la construcción (la construcción es el modo del cambio) y los modos que admiten: `funcional` no tiene sentido para operaciones.
ETAPAS = ('integracion', 'publicacion', 'produccion')
MODOS_ETAPA = ('confirmacion', 'autonomo')


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


def via_agente_etapa(modo: str) -> str:
    """'decide' si la etapa es autónoma; si no, 'rechaza': lo decide una persona (que decide siempre)."""
    if modo not in MODOS_ETAPA:
        raise ValueError(f'modo de etapa desconocido: {modo!r}')
    return 'decide' if modo == 'autonomo' else 'rechaza'


def autonomia(valor) -> dict[str, str]:
    """La clave `autonomia` de la configuración completa (lo no declarado pide a una persona); ValueError con lo que está mal."""
    if not isinstance(valor, dict):
        raise ValueError(f'autonomia es un objeto con las etapas {", ".join(ETAPAS)}; dice {valor!r}')
    for etapa, modo in valor.items():
        if etapa not in ETAPAS:
            raise ValueError(f'autonomia: la etapa {etapa!r} no existe; hay {", ".join(ETAPAS)}')
        if modo not in MODOS_ETAPA:
            raise ValueError(f'autonomia.{etapa}: el modo {modo!r} no existe para una etapa; hay {", ".join(MODOS_ETAPA)}')
    return {etapa: valor.get(etapa, 'confirmacion') for etapa in ETAPAS}


def baja_intervencion(actual: str, nuevo: str) -> bool:
    return INTERVENCION[nuevo] < INTERVENCION[actual]


def slug(texto: str) -> str:
    ascii_ = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '_', ascii_.lower()).strip('_')


def tipos_spec(texto: str, *, obligatorios: bool = False) -> dict[str, str]:
    """{slug del requisito: tipo}. Sin línea «Tipo:», funcional, salvo tipos obligatorios."""
    tipos, actual, sin_tipo, retirados = {}, None, [], False
    for linea in texto.splitlines():
        delta = re.match(r'^##\s+(ADDED|MODIFIED|REMOVED|RENAMED)\s+Requirements\s*$', linea, re.IGNORECASE)
        if delta:  # lo que la spec retira no se importa ni se mide: no lleva tipo
            retirados, actual = delta[1].upper() == 'REMOVED', None
            continue
        cabecera = re.match(r'^###\s+Requirement:\s*(.+?)\s*$', linea)
        if cabecera and retirados:
            actual = None
            continue
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
