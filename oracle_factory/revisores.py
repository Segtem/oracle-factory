"""Pedir una revisión independiente: configuración de revisores, pedido y validación de lo que devuelven.

Puro salvo `ejecutar_revisor`: la CLI prepara el checkout y el paquete, y registra el evento.
"""
from __future__ import annotations

from importlib import resources
import contextlib
import os
import re
from pathlib import Path
import signal
from string import Template
import subprocess

EJEMPLO = ('"revisores": {"codex": {"comando": ["ask-codex", "{pedido}", "{carpeta}", "{registro}"], '
           '"proveedor": "codex", "modelo": "gpt-6-luna", "tope_minutos": 90}}')
SEGUNDOS_POR_MINUTO = 60  # las pruebas lo achican para no esperar minutos
MARCADORES = ('{pedido}', '{pedido_archivo}', '{carpeta}', '{informe}', '{registro}', '{paquete}', '{checkout}')


class RevisorInvalido(ValueError):
    pass


def validar_config(revisores) -> dict:
    """La sección `revisores` de la configuración, comprobada; RevisorInvalido con el problema si no sirve."""
    if not isinstance(revisores, dict):
        raise RevisorInvalido('revisores debe ser un objeto nombre → revisor')
    for nombre, r in revisores.items():
        if not isinstance(r, dict) or set(r) != {'comando', 'proveedor', 'modelo', 'tope_minutos'}:
            raise RevisorInvalido(f'revisor {nombre}: se requieren exactamente comando, proveedor, modelo y tope_minutos')
        if not (isinstance(r['comando'], list) and r['comando'] and all(isinstance(a, str) and a for a in r['comando'])):
            raise RevisorInvalido(f'revisor {nombre}: comando debe ser una lista no vacía de argumentos')
        desconocidos = sorted({m for a in r['comando'] for m in re.findall(r'\{[a-z_]+\}', a)} - set(MARCADORES))
        if desconocidos:
            raise RevisorInvalido(f'revisor {nombre}: marcadores desconocidos {", ".join(desconocidos)}; '
                                  f'se pueden usar {", ".join(MARCADORES)}')
        if not all(isinstance(r[k], str) and r[k] for k in ('proveedor', 'modelo')):
            raise RevisorInvalido(f'revisor {nombre}: proveedor y modelo son textos')
        if type(r['tope_minutos']) is not int or not 0 < r['tope_minutos'] <= 24 * 60:
            raise RevisorInvalido(f'revisor {nombre}: tope_minutos es un entero entre 1 y 1440')
    return revisores


def plantilla(raiz: Path) -> str:
    propia = raiz / '.factory' / 'pedido-revision.md'
    if propia.is_file() and not propia.is_symlink():
        return propia.read_text(encoding='utf-8')
    return resources.files('oracle_factory').joinpath('data/pedido_revision.md').read_text(encoding='utf-8')


def pedido(texto_plantilla: str, valores: dict, extra: str | None) -> str:
    texto = Template(texto_plantilla).safe_substitute(valores)
    return texto + (f'\nIndicaciones de quien pide la revisión:\n{extra}\n' if extra else '')


def argumentos(comando: list[str], valores: dict) -> list[str]:
    """El comando con los marcadores reemplazados; sin shell, cada argumento es uno solo."""
    salida = []
    for arg in comando:
        for marca in MARCADORES:
            arg = arg.replace(marca, str(valores[marca.strip('{}')]))
        salida.append(arg)
    return salida


def ejecutar_revisor(argv: list[str], cwd: Path, registro: Path, tope_minutos: int) -> str:
    """'ok' o 'tope'. La salida del revisor va a `registro`; al vencer el tope se detiene todo su grupo de procesos."""
    with open(registro, 'wb') as salida:
        proceso = subprocess.Popen(argv, cwd=cwd, stdin=subprocess.DEVNULL, stdout=salida, stderr=subprocess.STDOUT,
                                   start_new_session=True)
        try:
            proceso.wait(timeout=tope_minutos * SEGUNDOS_POR_MINUTO)
            return 'ok'
        except subprocess.TimeoutExpired:
            os.killpg(proceso.pid, signal.SIGTERM)
            try:
                proceso.wait(timeout=10)
            except subprocess.TimeoutExpired:
                pass
            with contextlib.suppress(ProcessLookupError):  # el líder puede haber salido dejando hijos que ignoran SIGTERM
                os.killpg(proceso.pid, signal.SIGKILL)
            proceso.wait()
            return 'tope'
