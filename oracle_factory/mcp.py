"""Servidor MCP de sólo lectura sobre un proyecto de Factory: `oracle-factory --proyecto RUTA mcp`.

JSON-RPC por stdio, un mensaje por línea (el transporte stdio de MCP, sin cabeceras), sin dependencias. Cada herramienta
corre una consulta de la CLI en un proceso aparte y devuelve su salida tal cual: lo mismo que ve una persona, y nada que
pueda cambiar el proyecto (sólo comandos de lectura, con los argumentos validados y después de «--», para que un texto
nunca se tome como una opción). stdout es del protocolo; los avisos van a stderr.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys

PROTOCOLO = "2025-11-25"
ID_RE = re.compile(r"^\d{8}-\d{6}-[a-z0-9_-]+$")
TEXTO = {"type": "string", "minLength": 1, "maxLength": 2000}
MAXIMO = {"type": "integer", "minimum": 1, "maximum": 50}
ID = {"type": "string", "pattern": ID_RE.pattern}


def _herramienta(nombre: str, descripcion: str, propiedades: dict, requeridas: list) -> dict:
    return {"name": nombre, "description": descripcion,
            "inputSchema": {"type": "object", "properties": propiedades, "required": requeridas, "additionalProperties": False},
            "annotations": {"readOnlyHint": True}}


HERRAMIENTAS = [
    _herramienta("preguntar", "Responde sobre el proyecto con fuentes: consulta el registro y, si hay modelo configurado, "
                 "elabora respuestas. Avisa si falta respaldo (oracle-factory preguntar --json, esquema /2).",
                 {"texto": TEXTO, "max": MAXIMO}, ["texto"]),
    _herramienta("estado", "El estado de un cambio: fase, requisitos, decisiones, revisión, juicio, avisos y próximo paso "
                 "(oracle-factory estado ID --json).", {"id": ID}, ["id"]),
    _herramienta("buscar", "Un texto literal en propuestas, specs, requisitos, tareas y registros (oracle-factory buscar).",
                 {"texto": TEXTO, "max": MAXIMO}, ["texto"]),
    _herramienta("por_que", "Por qué existe una línea: su commit, su cambio, sus requisitos y decisiones "
                 "(oracle-factory por-que ARCHIVO:LÍNEA --json).",
                 {"archivo": TEXTO, "linea": {"type": "integer", "minimum": 1}}, ["archivo", "linea"]),
    _herramienta("resumen", "El resumen del estado vigente del proyecto (oracle-factory resumen --json).", {}, []),
    _herramienta("log", "Los commits de un cambio (oracle-factory log ID --json).", {"id": ID}, ["id"]),
    _herramienta("listar", "Los cambios del proyecto con su fase (oracle-factory listar).", {}, []),
]


def _valido(valor, esquema: dict) -> bool:
    if esquema["type"] == "string":
        return (isinstance(valor, str) and "\0" not in valor  # un byte nulo no se puede pasar a un proceso
                and esquema.get("minLength", 0) <= len(valor) <= esquema.get("maxLength", 10**9)
                and ("pattern" not in esquema or re.fullmatch(esquema["pattern"], valor) is not None))
    return (type(valor) is int and esquema.get("minimum", -10**18) <= valor <= esquema.get("maximum", 10**18))


def orden(nombre: str, argumentos) -> list[str]:
    """Los argumentos de la CLI para una herramienta; ValueError si los argumentos no son los esperados."""
    esquema = next(h["inputSchema"] for h in HERRAMIENTAS if h["name"] == nombre)
    if not isinstance(argumentos, dict) or set(argumentos) - set(esquema["properties"]) \
            or set(esquema["required"]) - set(argumentos) \
            or not all(_valido(v, esquema["properties"][k]) for k, v in argumentos.items()):
        raise ValueError(f"argumentos inválidos para {nombre}: se esperaba {json.dumps(esquema, ensure_ascii=False)}")
    a, maximo = argumentos, [*(["--max", str(argumentos["max"])] if "max" in argumentos else [])]
    return {"preguntar": lambda: ["preguntar", *maximo, "--json", "--", a.get("texto", "")],
            "estado": lambda: ["estado", "--json", "--", a.get("id", "")],
            "buscar": lambda: ["buscar", *maximo, "--", a.get("texto", "")],
            "por_que": lambda: ["por-que", "--json", "--", f"{a.get('archivo')}:{a.get('linea')}"],
            "resumen": lambda: ["resumen", "--json"],
            "log": lambda: ["log", "--json", "--", a.get("id", "")],
            "listar": lambda: ["listar"]}[nombre]()


def llamar(raiz: Path, nombre: str, argumentos) -> dict:
    try:
        args = orden(nombre, argumentos)
    except ValueError as e:
        return {"content": [{"type": "text", "text": str(e)}], "isError": True}
    try:
        p = subprocess.run([sys.executable, "-c", "import sys; from oracle_factory.cli import main; sys.exit(main())",
                            "--proyecto", str(raiz), *args], cwd=raiz, capture_output=True, text=True,
                           stdin=subprocess.DEVNULL, timeout=600)
    except (OSError, ValueError, subprocess.SubprocessError) as e:  # un plazo vencido, un proceso que no arranca
        return {"content": [{"type": "text", "text": f"{nombre} no se pudo correr: {e}"}], "isError": True}
    texto = p.stdout if p.returncode == 0 else (p.stderr or p.stdout).strip()
    return {"content": [{"type": "text", "text": texto}], "isError": p.returncode != 0}


def responder(raiz: Path, mensaje, version: str) -> dict | None:
    """La respuesta a un mensaje JSON-RPC, o None si es una notificación."""
    if not isinstance(mensaje, dict) or mensaje.get("jsonrpc") != "2.0" or not isinstance(mensaje.get("method"), str):
        return {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "pedido JSON-RPC inválido"}}
    if "id" not in mensaje:
        return None  # notifications/initialized y otras: no se contestan
    metodo, params = mensaje["method"], mensaje.get("params") or {}
    if metodo == "initialize":
        resultado = {"protocolVersion": PROTOCOLO, "capabilities": {"tools": {}},
                     "serverInfo": {"name": "oracle-factory", "version": version}}
    elif metodo == "ping":
        resultado = {}
    elif metodo == "tools/list":
        resultado = {"tools": HERRAMIENTAS}
    elif metodo == "tools/call" and isinstance(params, dict) and isinstance(params.get("name"), str) \
            and params["name"] in {h["name"] for h in HERRAMIENTAS}:
        resultado = llamar(raiz, params["name"], params.get("arguments", {}))
    elif metodo == "tools/call":
        return {"jsonrpc": "2.0", "id": mensaje["id"], "error": {"code": -32602, "message": f"herramienta desconocida: {params.get('name') if isinstance(params, dict) else params}"}}
    else:
        return {"jsonrpc": "2.0", "id": mensaje["id"], "error": {"code": -32601, "message": f"método no soportado: {metodo}"}}
    return {"jsonrpc": "2.0", "id": mensaje["id"], "result": resultado}


def servir(raiz: Path, entrada, salida, version: str) -> int:
    for linea in entrada:
        try:
            mensaje = json.loads(linea)
        except ValueError as e:
            respuesta = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": f"JSON inválido: {e}"}}
        else:
            try:
                respuesta = responder(raiz, mensaje, version)
            except Exception as e:  # noqa: BLE001 — un pedido raro no corta el servidor: se contesta con un error
                pedido = mensaje.get("id") if isinstance(mensaje, dict) else None
                respuesta = {"jsonrpc": "2.0", "id": pedido, "error": {"code": -32603, "message": f"error interno: {e}"}}
        if respuesta is not None:
            salida.write(json.dumps(respuesta, ensure_ascii=False, separators=(",", ":")) + "\n")
            salida.flush()
    return 0
