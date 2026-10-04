"""Documentos de revisión propios de Factory: consistencia, nunca calidad del análisis."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import PurePosixPath, PureWindowsPath
import re

INFORME = 'oracle-factory.revision/v1'
DECISIONES = 'oracle-factory.decisiones-revision/v1'


class RevisionInvalida(ValueError):
    pass


def cargar(datos: bytes, nombre: str) -> dict:
    def objeto(pares):
        resultado = {}
        for clave, valor in pares:
            if clave in resultado:
                raise RevisionInvalida(f'{nombre}: clave duplicada: {clave}')
            resultado[clave] = valor
        return resultado

    def constante(valor):
        raise RevisionInvalida(f'{nombre}: constante JSON inválida: {valor}')

    try:
        resultado = json.loads(datos.decode('utf-8'), object_pairs_hook=objeto, parse_constant=constante)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as e:
        raise RevisionInvalida(f'{nombre}: se requiere JSON UTF-8 válido: {e}') from e
    if not isinstance(resultado, dict):
        raise RevisionInvalida(f'{nombre}: se requiere un objeto JSON')
    return resultado


def campos(valor, esperados: str, nombre: str) -> None:
    if not isinstance(valor, dict):
        raise RevisionInvalida(f'{nombre}: se requiere un objeto')
    faltan, sobran = set(esperados.split()) - valor.keys(), valor.keys() - set(esperados.split())
    if faltan or sobran:
        raise RevisionInvalida(f'{nombre}: campos faltantes {sorted(faltan)}; desconocidos {sorted(sobran)}')


def texto(valor, nombre: str) -> str:
    if not isinstance(valor, str) or not valor.strip() or valor.strip().upper() == 'PENDIENTE':
        raise RevisionInvalida(f'{nombre}: texto requerido, todavía pendiente o vacío')
    return valor


def lista(valor, nombre: str, *, no_vacia=False) -> list:
    if not isinstance(valor, list) or (no_vacia and not valor):
        raise RevisionInvalida(f'{nombre}: lista explícita requerida' + (' y no vacía' if no_vacia else ' (null es pendiente)'))
    return valor


def plantillas(identificador: str, contexto: dict, documentos: dict) -> tuple[dict, dict]:
    informe = dict(schema_version=INFORME, cambio=identificador, contexto=contexto, documentos=documentos,
                   revisor=None, completa=None, archivos_revisados=None, comprobaciones=None,
                   limites=None, hallazgos=None, sin_hallazgos_motivo=None)
    decisiones = dict(schema_version=DECISIONES, informe_sha256=None, actor=None, motivo=None, decisiones=None)
    return informe, decisiones


def validar(informe_bytes: bytes, decisiones_bytes: bytes, *, identificador: str,
            contexto: dict, documentos: dict, revisor: str) -> tuple[dict, dict, list[str]]:
    informe, decisiones = cargar(informe_bytes, 'informe'), cargar(decisiones_bytes, 'decisiones')
    campos(informe, 'schema_version cambio contexto documentos revisor completa archivos_revisados '
           'comprobaciones limites hallazgos sin_hallazgos_motivo', 'informe')
    campos(decisiones, 'schema_version informe_sha256 actor motivo decisiones', 'decisiones')
    if informe['schema_version'] != INFORME or decisiones['schema_version'] != DECISIONES:
        raise RevisionInvalida('versión de documento desconocida; usá las plantillas de revision-preparar')
    if informe['cambio'] != identificador or informe['contexto'] != contexto or informe['documentos'] != documentos:
        raise RevisionInvalida('informe de otro cambio o contexto/propuesta/spec desactualizados; prepará una nueva revisión')
    if texto(informe['revisor'], 'informe.revisor') != revisor:
        raise RevisionInvalida('informe.revisor debe coincidir con --revisor')
    if type(informe['completa']) is not bool:
        raise RevisionInvalida('informe.completa: booleano explícito requerido, null es pendiente')
    archivos = lista(informe['archivos_revisados'], 'archivos_revisados', no_vacia=True)
    vistos = set()
    for archivo in archivos:
        texto(archivo, 'archivo revisado')
        ruta = PurePosixPath(archivo)
        if (ruta.is_absolute() or PureWindowsPath(archivo).drive or '\\' in archivo
                or any(p in ('', '.', '..') for p in archivo.split('/')) or archivo in vistos):
            raise RevisionInvalida(f'archivo revisado: ruta relativa inválida o repetida: {archivo}')
        vistos.add(archivo)
    for i, comprobacion in enumerate(lista(informe['comprobaciones'], 'comprobaciones', no_vacia=True)):
        nombre = f'comprobaciones[{i}]'
        campos(comprobacion, 'descripcion resultado evidencia', nombre)
        texto(comprobacion['descripcion'], nombre + '.descripcion')
        texto(comprobacion['evidencia'], nombre + '.evidencia')
        if texto(comprobacion['resultado'], nombre + '.resultado') not in ('cumple', 'falla', 'no_ejecutada'):
            raise RevisionInvalida(nombre + ': resultado desconocido')
    for limite in lista(informe['limites'], 'limites'):
        texto(limite, 'limite')
    if not informe['completa'] and not informe['limites']:
        raise RevisionInvalida('revisión incompleta requiere límites explícitos')
    hallazgos = lista(informe['hallazgos'], 'hallazgos')
    ids = set()
    for hallazgo in hallazgos:
        campos(hallazgo, 'id descripcion ubicacion evidencia', 'hallazgo')
        for campo, valor in hallazgo.items():
            texto(valor, 'hallazgo.' + campo)
        if hallazgo['id'] in ids:
            raise RevisionInvalida('id de hallazgo duplicado: ' + hallazgo['id'])
        ids.add(hallazgo['id'])
    if not hallazgos:
        texto(informe['sin_hallazgos_motivo'], 'sin_hallazgos_motivo')
    elif informe['sin_hallazgos_motivo'] is not None:
        raise RevisionInvalida('sin_hallazgos_motivo debe ser null cuando hay hallazgos')
    if decisiones['informe_sha256'] != hashlib.sha256(informe_bytes).hexdigest():
        raise RevisionInvalida('decisiones.informe_sha256 no corresponde a los bytes del informe; completá o renová el hash')
    texto(decisiones['actor'], 'decisiones.actor')
    texto(decisiones['motivo'], 'decisiones.motivo')
    resueltos = set()
    for resolucion in lista(decisiones['decisiones'], 'decisiones.decisiones'):
        campos(resolucion, 'hallazgo_id estado motivo actor fecha', 'resolución')
        for campo, valor in resolucion.items():
            texto(valor, 'resolución.' + campo)
        fid = resolucion['hallazgo_id']
        if fid not in ids or fid in resueltos:
            raise RevisionInvalida('decisión duplicada o hallazgo inexistente: ' + fid)
        if resolucion['estado'] not in ('corregido', 'descartado', 'riesgo_aceptado'):
            raise RevisionInvalida('estado de resolución desconocido: ' + resolucion['estado'])
        fecha = resolucion['fecha']
        try:
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})', fecha):
                raise ValueError('formato')
            dt.datetime.fromisoformat(fecha.replace('Z', '+00:00'))
        except ValueError as e:
            raise RevisionInvalida('fecha de resolución: se requiere ISO 8601 válido con zona horaria') from e
        resueltos.add(fid)
    return informe, decisiones, sorted(ids - resueltos)
