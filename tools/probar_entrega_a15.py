"""Comprobación real del wheel instalado en entorno nuevo fuera del checkout.

Verifica:
1. Construcción del wheel 0.1.0a15 y sus hashes.
2. Instalación en venv nuevo y aislado.
3. Origen de importación (site-packages del venv, NUNCA checkout) y versión reportada.
4. Consultas directas de registro (cerrados archivados, abiertos, abandonados) sin modelo generativo.
5. Elaboración documental y de conteo con servidor HTTP fixture simulado, citas y rechazo de escrituras.
6. Reutilización de verify_installed.py y verify_guide.py.
"""
from __future__ import annotations

import argparse
import hashlib
import http.server
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import threading
import time

ROOT = Path(__file__).resolve().parents[1]
VERSION_ESPERADA = "0.1.0a15"
COMANDOS = []


def ejecutar(argv, **kwargs):
    kwargs.setdefault('stdin', subprocess.DEVNULL)
    kwargs.setdefault('timeout', 180)
    r = subprocess.run(argv, **kwargs)
    COMANDOS.append({'comando': [str(a) for a in argv], 'cwd': str(kwargs.get('cwd', Path.cwd())),
                     'codigo': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr})
    return r


def entorno_fixture():
    env = {**os.environ, 'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_CONFIG_NOSYSTEM': '1',
           'GIT_CONFIG_COUNT': '2', 'GIT_CONFIG_KEY_0': 'user.name', 'GIT_CONFIG_VALUE_0': 'Fixture',
           'GIT_CONFIG_KEY_1': 'user.email', 'GIT_CONFIG_VALUE_1': 'fixture@example.invalid',
           'PYTHONDONTWRITEBYTECODE': '1'}
    env.pop('PYTHONPATH', None)
    return env



def sha256_archivo(ruta: Path) -> str:
    h = hashlib.sha256()
    with ruta.open("rb") as f:
        for bloque in iter(lambda: f.read(65536), b""):
            h.update(bloque)
    return h.hexdigest()


def construir_artefactos(salida_dir: Path | None = None) -> dict[str, object]:
    """Construye wheel y sdist mediante uv build en la carpeta indicada."""
    if salida_dir is None:
        salida_dir = ROOT / ".factory/local/dist"
    salida_dir.mkdir(parents=True, exist_ok=True)
    if any(salida_dir.iterdir()):
        raise ValueError(f'La construcción exige una carpeta vacía: {salida_dir}')
    env = entorno_fixture()
    r = ejecutar(
        ["uv", "build", "--wheel", "--sdist", "--out-dir", str(salida_dir)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        env=env,
    )
    if r.returncode != 0:
        raise RuntimeError(f"Fallo al construir artefactos: {r.stdout}\n{r.stderr}")
    wheels = list(salida_dir.glob(f"oracle_factory-{VERSION_ESPERADA}-*.whl"))
    sdists = list(salida_dir.glob(f"oracle_factory-{VERSION_ESPERADA}.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        raise FileNotFoundError(f"No se encontró el wheel de {VERSION_ESPERADA} en {salida_dir}")
    wheel_path = wheels[0]
    sdist_path = sdists[0]
    res = {
        "wheel": wheel_path,
        "wheel_sha256": sha256_archivo(wheel_path),
        "sdist": sdist_path,
        "sdist_sha256": sha256_archivo(sdist_path) if sdist_path else None,
        "stdout": r.stdout,
        "stderr": r.stderr,
    }
    return res


def crear_entorno_aislado(venv_dir: Path, wheel_path: Path) -> tuple[Path, Path]:
    """Crea un virtualenv nuevo e instala el wheel con sus dependencias."""
    env = {**os.environ, "UV_LINK_MODE": "copy", "PYTHONDONTWRITEBYTECODE": "1"}
    r1 = ejecutar(["uv", "venv", str(venv_dir), "--python", "3.13"], capture_output=True, text=True, env=env)
    if r1.returncode != 0:
        raise RuntimeError(f"Fallo al crear venv en {venv_dir}: {r1.stderr}")
    python_bin = venv_dir / "bin/python"
    factory_bin = venv_dir / "bin/oracle-factory"
    r2 = ejecutar(
        ["uv", "pip", "install", "--python", str(python_bin), str(wheel_path)],
        capture_output=True,
        text=True,
        env=env,
    )
    if r2.returncode != 0:
        raise RuntimeError(f"Fallo al instalar wheel en venv: {r2.stderr}")
    if not factory_bin.is_file():
        raise FileNotFoundError(f"No se encontró el ejecutable {factory_bin}")
    return factory_bin, python_bin


def verificar_origen_y_version(
    python_bin: Path,
    factory_bin: Path,
    esperado_dir: Path,
    version_esperada: str = VERSION_ESPERADA,
    prohibir_checkout: Path = ROOT,
) -> dict[str, str]:
    """Verifica que el módulo importado provenga del venv y no del checkout, y que la versión sea la esperada."""
    env = entorno_fixture()
    env.pop("PYTHONPATH", None)
    codigo = "import oracle_factory; print(oracle_factory.__file__); print(oracle_factory.__version__)"
    r = ejecutar(
        [str(python_bin), "-c", codigo],
        cwd=esperado_dir.parent,
        capture_output=True,
        text=True,
        env=env,
    )
    if r.returncode != 0:
        raise RuntimeError(f"Error al importar oracle_factory: {r.stderr}")
    lineas = r.stdout.strip().splitlines()
    if len(lineas) < 2:
        raise ValueError(f"Salida inesperada: {r.stdout}")
    archivo_mod, version_mod = lineas[0], lineas[1]

    # Comprobación de origen
    archivo_path = Path(archivo_mod).resolve()
    esperado_resolved = esperado_dir.resolve()
    prohibido_resolved = prohibir_checkout.resolve()

    if prohibido_resolved in archivo_path.parents or archivo_path == prohibido_resolved:
        raise AssertionError(f"Importación accidental desde el checkout: {archivo_path}")
    if esperado_resolved not in archivo_path.parents:
        raise AssertionError(f"El módulo {archivo_path} no está en el entorno esperado {esperado_resolved}")
    if version_mod != version_esperada:
        raise AssertionError(f"Versión incorrecta instalada: {version_mod} != {version_esperada}")

    # Comprobar la CLI directamente
    r_cli = ejecutar(
        [str(factory_bin), "--version"],
        cwd=esperado_dir.parent,
        capture_output=True,
        text=True,
        env=env,
    )
    if r_cli.returncode != 0:
        raise RuntimeError(f"Error al ejecutar oracle-factory --version: {r_cli.stderr}")
    salida_cli = r_cli.stdout.strip()
    esperada_cli = f"oracle-factory {version_esperada}"
    if salida_cli != esperada_cli:
        raise AssertionError(f"Salida CLI inesperada: '{salida_cli}' != '{esperada_cli}'")

    return {
        "archivo_modulo": str(archivo_path),
        "version_modulo": version_mod,
        "salida_cli": salida_cli,
        "ejecutable": str(factory_bin),
    }


def crear_proyecto_fixture_registro(destino: Path, factory_bin: Path) -> Path:
    """Crea un proyecto temporal con dos cerrados archivados, un abierto y un abandonado."""
    proyecto = destino / "proyecto_fixture"
    proyecto.mkdir(parents=True, exist_ok=True)
    env = {
        **os.environ,
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    env.pop("PYTHONPATH", None)

    # Git init
    ejecutar(["git", "init", "-q"], cwd=proyecto, check=True, env=env)

    # Factory init
    r = ejecutar([str(factory_bin), "--agente", "codex", "--proyecto", str(proyecto), "init"], capture_output=True, text=True, env=env)
    if r.returncode != 0:
        raise RuntimeError(f"Fallo en init: {r.stderr}")

    config_path = proyecto / '.factory/config.json'
    config = json.loads(config_path.read_text())
    config['rag'] = {'embeddings': {'proveedor': 'ninguno'}, 'generacion': {'proveedor': 'ninguno'}}
    config_path.write_text(json.dumps(config) + '\n')

    # Crear 4 cambios: 2 cerrados archivados, 1 abierto, 1 abandonado
    cambios_info = [
        ("20261020-100000-aaa-cerrado1", "cerrada", True, False),
        ("20261021-110000-bbb-cerrado2", "cerrada", True, False),
        ("20261022-120000-ccc-abierto", "abierta", False, False),
        ("20261023-130000-ddd-abandonado", "abandonada", False, True),
    ]

    for ident, fase, archivado, abandonado in cambios_info:
        dir_c = proyecto / ".factory/cambios" / ident
        dir_c.mkdir(parents=True, exist_ok=True)
        dir_open = proyecto / "openspec/changes" / ident
        dir_open.mkdir(parents=True, exist_ok=True)
        (dir_open / "proposal.md").write_text(f"# Propuesta {ident}\n")
        (dir_open / "design.md").write_text(f"# Diseño {ident}\n")
        dir_spec = dir_open / "specs/distribucion"
        dir_spec.mkdir(parents=True, exist_ok=True)
        (dir_spec / "spec.md").write_text(f"# Spec {ident}\n")

        dir_tarea = proyecto / "tareas" / ident
        dir_tarea.mkdir(parents=True, exist_ok=True)
        (dir_tarea / "TAREA.md").write_text(f"# Tarea {ident}\nESTADO: {fase.upper()}\n")

        data = {
            "id": ident,
            "titulo": f"Cambio {ident}",
            "fase": fase,
            "capacidad": "distribucion",
            "modo": "confirmacion",
            "eventos": [
                {"accion": "nuevo", "actor": "Brian", "cuando": "2026-10-20T10:00:00Z"},
            ],
            "requisitos": [],
        }
        if archivado:
            data["archivo"] = {
                "capacidad": "distribucion",
                "spec": "openspec/specs/distribucion/spec.md",
                "cuando": "2026-10-21T12:00:00Z",
                "modo": "migracion",
            }
            data["cierre"] = {"actor": "Brian", "cuando": "2026-10-21T12:00:00Z"}
            data["eventos"].append({"accion": "cierre", "actor": "Brian", "cuando": "2026-10-21T12:00:00Z"})
        if abandonado:
            data["abandono"] = {"actor": "Brian", "motivo": "Descartado", "cuando": "2026-10-23T13:00:00Z"}
            data["eventos"].append({"accion": "abandono", "actor": "Brian", "cuando": "2026-10-23T13:00:00Z"})

        (dir_c / "factory.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Openspec specs consolidada para notas/distribución
    specs_dir = proyecto / "openspec/specs/distribucion"
    specs_dir.mkdir(parents=True, exist_ok=True)
    (specs_dir / "spec.md").write_text("# Capacidad distribucion\n", encoding="utf-8")

    return proyecto


def probar_conteo_registro(factory_bin: Path, proyecto_dir: Path) -> dict[str, object]:
    """Prueba conteos de cambios desde el registro sin modelo generativo."""
    env = {
        **os.environ,
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    env.pop("PYTHONPATH", None)

    casos = [
        ("¿Cuántos cambios cerrados hay?", "cerrados", 2),
        ("¿Cuántos cambios abiertos hay?", "abiertos", 1),
        ("¿Cuántos cambios abandonados hay?", "abandonados", 1),
        ("¿Cuántos cambios hay en total?", "todos", 4),
    ]

    observaciones = []
    for pregunta, filtro, esperado in casos:
        r = ejecutar(
            [str(factory_bin), "--agente", "codex", "--proyecto", str(proyecto_dir), "preguntar", "--json", pregunta],
            cwd=proyecto_dir.parent,
            capture_output=True,
            text=True,
            env=env,
        )
        if r.returncode != 0:
            raise AssertionError(f"Error en preguntar '{pregunta}': {r.stderr}")
        try:
            datos = json.loads(r.stdout)
        except json.JSONDecodeError as exc:
            raise AssertionError(f"Salida no es JSON válido para '{pregunta}': {r.stdout}") from exc

        # Verificaciones del conteo y fuentes
        cantidad = datos.get("valor")
        if datos.get('tipo') != 'registro' or type(cantidad) is not int:
            raise AssertionError(f'Contrato de conteo inválido: {datos}')
        fuentes = datos.get("fuentes", [])
        citas = [f.get("cita", "") for f in fuentes]

        if cantidad != esperado:
            raise AssertionError(f"Conteo incorrecto para '{pregunta}': esperado {esperado}, observado {cantidad}")
        if not any(f"registro:" in c and f'"{filtro}"' in c for c in citas):
            raise AssertionError(f"Falta cita de registro con filtro {filtro} en: {citas}")
        if datos.get("modelo_generativo"):
            raise AssertionError(f"Se invocó modelo generativo indebidamente: {datos.get('modelo_generativo')}")

        observaciones.append({
            "pregunta": pregunta,
            "filtro": filtro,
            "esperado": esperado,
            "observado": cantidad,
            "fuentes": citas,
        })

    return {"casos": observaciones, "exitoso": True}


class ManejadorFixtureOpenAI(http.server.BaseHTTPRequestHandler):
    """Servidor local HTTP fixture que simula endpoint OpenAI Chat Completions.
    En el primer turno emite tool_calls con 'registro' y una llamada prohibida de 'escribir'.
    En el segundo turno verifica que 'escribir' haya sido rechazada y emite la respuesta estructurada final.
    """
    solicitudes = 0
    llamada_escritura_recibida = False
    rechazo_escritura_detectado = False

    def log_message(self, format, *args):
        pass  # silencioso

    def do_POST(self):
        longitud = int(self.headers.get("Content-Length", 0))
        cuerpo = self.rfile.read(longitud).decode("utf-8")
        solicitud = json.loads(cuerpo)
        ManejadorFixtureOpenAI.solicitudes += 1

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()

        if ManejadorFixtureOpenAI.solicitudes == 1:
            # Emitir tool_calls: una de consulta (registro) y una llamada ilegal de escritura (escribir)
            respuesta = {
                "id": "chatcmpl-fix-1",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": "fixture-model",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": "call_registro_1",
                                "type": "function",
                                "function": {
                                    "name": "registro",
                                    "arguments": json.dumps({"operacion": "contar", "estado": "cerrados"}),
                                },
                            },
                            {
                                "id": "call_escribir_1",
                                "type": "function",
                                "function": {
                                    "name": "escribir",
                                    "arguments": json.dumps({"ruta": "malicioso.txt", "contenido": "destruir"}),
                                },
                            },
                        ],
                    },
                    "finish_reason": "tool_calls",
                }],
            }
            ManejadorFixtureOpenAI.llamada_escritura_recibida = True
        else:
            # Inspeccionar respuestas de herramientas en los mensajes
            mensajes = solicitud.get("messages", [])
            fragmento_id = None
            for m in mensajes:
                if m.get("role") == "tool":
                    call_id = m.get("tool_call_id")
                    contenido = m.get("content", "")
                    if call_id == "call_escribir_1":
                        if "Sólo se admiten registro y recuperar" in contenido or "error" in contenido.lower():
                            ManejadorFixtureOpenAI.rechazo_escritura_detectado = True
                    elif call_id == "call_registro_1":
                        try:
                            datos_tool = json.loads(contenido)
                            for f in datos_tool.get("fuentes", []):
                                if f.get("fragmentos"):
                                    fragmento_id = f["fragmentos"][0]["id"]
                                    break
                        except Exception:
                            pass

            iniciales = json.loads(mensajes[1]['content'])['fuentes']
            documento = next(f for f in iniciales if f.get('ruta') == 'docs/reglas.md')
            if not fragmento_id:
                raise AssertionError('El fixture no recibió el fragmento calculado del registro')

            # Emitir respuesta final según FORMATO_FINAL
            contenido_final = json.dumps({
                "estado": "respondida",
                "afirmaciones": [
                    {
                        "texto": "Hay 2 cambios cerrados en el registro.",
                        "inferencia": False,
                        "alcance": "actual",
                        "citas": [{"fragmento": fragmento_id}],
                    },
                    {
                        "texto": "Las reglas establecen acuerdos y revisiones para cada entrega.",
                        "inferencia": False,
                        "alcance": "actual",
                        "citas": [{"fragmento": documento['fragmentos'][0]['id']}],
                    }
                ],
                "pregunta": "",
            }, ensure_ascii=False)

            respuesta = {
                "id": "chatcmpl-fix-2",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": "fixture-model",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": contenido_final,
                    },
                    "finish_reason": "stop",
                }],
            }

        self.wfile.write(json.dumps(respuesta).encode("utf-8"))


def probar_elaboracion_servidor_fixture(factory_bin: Path, proyecto_dir: Path) -> dict[str, object]:
    """Prueba elaboración con servidor HTTP fixture simulado, citas y rechazo de escrituras."""
    ManejadorFixtureOpenAI.solicitudes = 0
    ManejadorFixtureOpenAI.llamada_escritura_recibida = False
    ManejadorFixtureOpenAI.rechazo_escritura_detectado = False

    # Agregar documentación para que haya respaldo documental suficiente
    docs_dir = proyecto_dir / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    (docs_dir / "reglas.md").write_text("# Reglas del proyecto\nLas reglas establecen acuerdos y revisiones para cada entrega.\n", encoding="utf-8")

    servidor = http.server.ThreadingHTTPServer(("127.0.0.1", 0), ManejadorFixtureOpenAI)
    puerto = servidor.server_address[1]
    hilo = threading.Thread(target=servidor.serve_forever, daemon=True)
    hilo.start()

    try:
        # Configurar rag.generacion en .factory/config.json
        config_path = proyecto_dir / ".factory/config.json"
        config = json.loads(config_path.read_text())
        config['rag'] = {
                "embeddings": {"proveedor": "ninguno"},
                "generacion": {
                    "proveedor": "openai",
                    "url": f"http://127.0.0.1:{puerto}/v1",
                    "modelo": "fixture-model",
                    "segundos": 15,
                }
        }
        config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

        env = {
            **os.environ,
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        env.pop("PYTHONPATH", None)

        registros_antes = {p.relative_to(proyecto_dir).as_posix(): sha256_archivo(p)
                           for p in (proyecto_dir / '.factory/cambios').rglob('*') if p.is_file()}
        pregunta = "¿Qué reglas establecen acuerdos y cuántos cambios cerrados hay?"
        r = ejecutar(
            [str(factory_bin), "--agente", "codex", "--proyecto", str(proyecto_dir), "preguntar", "--json", pregunta],
            cwd=proyecto_dir.parent,
            capture_output=True,
            text=True,
            env=env,
        )
        if r.returncode != 0:
            raise AssertionError(f"Fallo en elaboración fixture: {r.stderr}\nSTDOUT: {r.stdout}")
        datos = json.loads(r.stdout)

        # Verificaciones:
        # 1. Herramienta 'escribir' rechazada en trazas
        trazas = datos.get("herramientas", [])
        trazas_escribir = [t for t in trazas if t.get("herramienta") == "escribir"]
        if not trazas_escribir or trazas_escribir[0].get("exitoso") is not False:
            raise AssertionError(f"La herramienta de escritura no fue rechazada correctamente: {trazas}")
        if not ManejadorFixtureOpenAI.rechazo_escritura_detectado:
            raise AssertionError("El servidor no recibió el mensaje de rechazo de la llamada de escritura.")

        # 2. No se creó el archivo malicioso ni se alteraron registros
        if (proyecto_dir / "malicioso.txt").exists() or (proyecto_dir.parent / "malicioso.txt").exists():
            raise AssertionError("Se creó el archivo malicioso solicitado en la herramienta de escritura.")

        # 3. Respuesta conservada con citas
        afirmaciones = datos.get("afirmaciones", [])
        if not afirmaciones:
            raise AssertionError(f"Faltan afirmaciones en la respuesta: {datos}")
        if "2" not in afirmaciones[0]["texto"]:
            raise AssertionError(f"La respuesta no conservó el conteo calculado: {afirmaciones[0]['texto']}")

        if datos.get('tipo') != 'respuesta_elaborada' or len(afirmaciones) != 2:
            raise AssertionError(f'Elaboración mixta incompleta: {datos}')
        citas = [c for a in afirmaciones for c in a.get('citas', [])]
        if not any('Cantidad de cambios cerrados: 2' in c.get('texto', '') for c in citas):
            raise AssertionError('Falta respaldo calculado del conteo')
        if not any('Las reglas establecen acuerdos y revisiones' in c.get('texto', '') for c in citas):
            raise AssertionError('Falta respaldo documental')
        registros_despues = {p.relative_to(proyecto_dir).as_posix(): sha256_archivo(p)
                             for p in (proyecto_dir / '.factory/cambios').rglob('*') if p.is_file()}
        if registros_antes != registros_despues:
            raise AssertionError('La consulta modificó registros')
        return {
            "exitoso": True,
            "fuentes": datos.get('fuentes'),
            "registros_intactos": True,
            "simulado": True,
            "rechazo_escritura": True,
            "trazas": trazas,
            "respuesta": datos.get("respuesta", ""),
            "afirmaciones": afirmaciones,
        }
    finally:
        servidor.shutdown()
        servidor.server_close()


def probar_novedades(factory_bin: Path, tmp_path: Path) -> dict[str, object]:
    """Lo nuevo de 0.1.0a15 con el wheel instalado, desde otra carpeta y en un proyecto temporal propio."""
    proyecto = tmp_path / "proyecto_novedades"
    proyecto.mkdir(parents=True, exist_ok=True)
    env = entorno_fixture()
    env.pop("PYTHONPATH", None)
    env["PATH"] = str(factory_bin.parent) + os.pathsep + env.get("PATH", "")  # `tasks`, de Oracle Task, del entorno nuevo
    ejecutar(["git", "init", "-q"], cwd=proyecto, check=True, env=env)
    base = [str(factory_bin), "--agente", "codex", "--proyecto", str(proyecto)]

    def correr(*args, esperado=0):
        r = ejecutar([*base, *args], cwd=tmp_path, capture_output=True, text=True, env=env)
        if (r.returncode == 0) != (esperado == 0):
            raise AssertionError(f"{' '.join(args)}: código {r.returncode}, se esperaba {esperado}: {r.stdout} {r.stderr}")
        return r

    correr("init")
    config = proyecto / ".factory/config.json"
    datos = json.loads(config.read_text())
    datos["rag"] = {"embeddings": {"proveedor": "ninguno"}, "generacion": {"proveedor": "ninguno"}}
    config.write_text(json.dumps(datos) + "\n")

    # El idioma de la plantilla: un cambio en inglés, con la estructura que exige el formato.
    creado = correr("nuevo", "--capacidad", "novedad", "--idioma", "en", "Probar las novedades").stdout
    ident = next((l.split(": ", 1)[1].strip() for l in creado.splitlines() if l.startswith("Cambio creado: ")), "")
    if not ident:
        raise AssertionError(f"nuevo no dijo el cambio creado: {creado}")
    carpeta = proyecto / "openspec/changes" / ident
    spec = (carpeta / "specs/novedad/spec.md").read_text(encoding="utf-8")
    propuesta = (carpeta / "proposal.md").read_text(encoding="utf-8")
    if "The system SHALL" not in spec or "DEBE" in spec or "## ADDED Requirements" not in spec or "## Why" not in propuesta:
        raise AssertionError(f"la plantilla en inglés no salió entera en inglés: {spec} {propuesta}")

    # El bloqueo de aprobar-spec nombra la línea que falta completar.
    bloqueo = correr("aprobar-spec", ident, esperado=1)
    texto = bloqueo.stdout + bloqueo.stderr
    if "hay que completar y revisar primero" not in texto or "proposal.md (línea " not in texto or "quedan 3 más" not in texto:
        raise AssertionError(f"el bloqueo no nombró la línea pendiente: {texto}")

    # preguntar cuenta las specs y rechaza un filtro que no admite.
    cuenta = json.loads(correr("preguntar", "--json", "¿Cuántas specs hay?").stdout)
    if cuenta.get("valor") != {"vigentes": 0, "en_cambios_abiertos": 1} or cuenta.get("modelo_generativo"):
        raise AssertionError(f"el conteo de specs no es el esperado: {cuenta}")
    filtro = json.loads(correr("preguntar", "--json", "¿Cuántas specs hay desde ayer?").stdout)
    if filtro.get("tipo") != "consulta_no_admitida" or filtro.get("resultados"):
        raise AssertionError(f"un filtro no admitido debía rechazarse: {filtro}")

    # El tablero: quién mira, qué falta con quién lo hace, y la actividad reciente.
    tablero = json.loads(correr("tablero", "--json").stdout)
    [cambio] = [c for c in tablero["cambios"] if c["id"] == ident]
    if "yo" not in tablero or not cambio["faltan"] or not all({"texto", "humano", "quien"} <= set(x) for x in cambio["faltan"]):
        raise AssertionError(f"el tablero no trae yo y faltan: {list(tablero)} {cambio['faltan']}")
    if not any(e["cambio"] == ident and e["accion"] == "cambio_creado" for e in tablero["proyecto"]["actividad"]):
        raise AssertionError(f"la actividad no trae el cambio creado: {tablero['proyecto']['actividad']}")
    return {"exitoso": True, "cambio": ident, "especificaciones": cuenta["valor"], "filtro_rechazado": True,
            "faltan": [{"humano": x["humano"], "quien": x["quien"]} for x in cambio["faltan"]],
            "bloqueo": texto.strip().splitlines()[-1][:300]}


def probar_arneses(factory_bin: Path, python_bin: Path) -> dict[str, object]:
    """Reutiliza verify_installed.py y verify_guide.py usando el ejecutable y python del wheel."""
    env = entorno_fixture()
    env.pop("PYTHONPATH", None)

    # 1. verify_installed.py
    r1 = ejecutar(
        [sys.executable, str(ROOT / "tools/verify_installed.py"), "--factory", str(factory_bin), "--python", str(python_bin)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        env=env,
    )
    if r1.returncode != 0:
        raise AssertionError(f"verify_installed.py falló:\nSTDOUT: {r1.stdout}\nSTDERR: {r1.stderr}")

    # 2. verify_guide.py
    r2 = ejecutar(
        [sys.executable, str(ROOT / "tools/verify_guide.py"), "--factory", str(factory_bin)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        env=env,
    )
    if r2.returncode != 0:
        raise AssertionError(f"verify_guide.py falló:\nSTDOUT: {r2.stdout}\nSTDERR: {r2.stderr}")

    return {
        "verify_installed": {"returncode": r1.returncode, "stdout": r1.stdout.strip()},
        "verify_guide": {"returncode": r2.returncode, "stdout": r2.stdout.strip()},
        "exitoso": True,
    }


def ejecutar_comprobacion_completa(dist_dir: Path | None = None) -> dict[str, object]:
    """Ejecuta el flujo completo de distribución en directorios temporales aislados."""
    COMANDOS.clear()
    artefactos = construir_artefactos(dist_dir)
    wheel_path = artefactos["wheel"]

    with tempfile.TemporaryDirectory(prefix="factory-entrega-") as tmp:
        tmp_path = Path(tmp)
        venv_dir = tmp_path / "venv"
        factory_bin, python_bin = crear_entorno_aislado(venv_dir, wheel_path)

        verif_origen = verificar_origen_y_version(python_bin, factory_bin, venv_dir, VERSION_ESPERADA, ROOT)
        proyecto_dir = crear_proyecto_fixture_registro(tmp_path, factory_bin)
        res_conteo = probar_conteo_registro(factory_bin, proyecto_dir)
        res_elab = probar_elaboracion_servidor_fixture(factory_bin, proyecto_dir)
        res_novedades = probar_novedades(factory_bin, tmp_path)
        res_arneses = probar_arneses(factory_bin, python_bin)

    return {
        "version": VERSION_ESPERADA,
        "comandos": list(COMANDOS),
        "construccion": {k: artefactos[k] for k in ('stdout', 'stderr')},
        "configuracion": {'embeddings': 'ninguno', 'generacion': 'servidor HTTP fixture local'},
        "artefactos": {
            "wheel": str(artefactos["wheel"]),
            "wheel_sha256": artefactos["wheel_sha256"],
            "sdist": str(artefactos["sdist"]) if artefactos.get("sdist") else None,
            "sdist_sha256": artefactos.get("sdist_sha256"),
        },
        "origen": verif_origen,
        "conteo_registro": res_conteo,
        "elaboracion_fixture": res_elab,
        "novedades": res_novedades,
        "arneses": res_arneses,
        "exitoso": True,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--salida-log", type=Path, help="Archivo para guardar el log JSON")
    p.add_argument("--dist-dir", type=Path, default=ROOT / ".factory/local/dist")
    args = p.parse_args()

    inicio = time.monotonic()
    resultado = ejecutar_comprobacion_completa(args.dist_dir)
    duracion = time.monotonic() - inicio
    resultado["duracion_segundos"] = round(duracion, 2)

    if args.salida_log:
        args.salida_log.parent.mkdir(parents=True, exist_ok=True)
        args.salida_log.write_text(json.dumps(resultado, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"OK: Comprobación de entrega {VERSION_ESPERADA} exitosa en {duracion:.2f}s.")
    print(f"Wheel: {resultado['artefactos']['wheel']} ({resultado['artefactos']['wheel_sha256'][:16]}...)")
    print(f"Módulo verificado: {resultado['origen']['archivo_modulo']}")
    print(f"Conteos de registro: {len(resultado['conteo_registro']['casos'])} casos verificados sin modelo generativo.")
    print("Elaboración fixture: llamada de escritura rechazada, citas conservadas y simulación identificada.")
    print("Novedades: plantilla en inglés, bloqueo con su línea, conteo de specs, filtro rechazado y tablero con yo, faltan y actividad.")
    print("Arneses: verify_installed.py y verify_guide.py exitosos.")


if __name__ == "__main__":
    main()
