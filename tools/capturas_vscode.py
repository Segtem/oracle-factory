"""Regenera las capturas de VS Code y los ejemplos de la web sobre un proyecto de ejemplo, en una carpeta temporal.

Uso: python tools/capturas_vscode.py [--sin-capturas] [--aplicar]
  --sin-capturas  sólo arma el proyecto y registra las salidas de los comandos (no abre VS Code)
  --aplicar       reescribe los bloques <pre data-ejemplo> de site/*.html con lo registrado
Necesita oracle-factory en el PATH; las capturas, además, `code`, `xvfb-run`, `xdotool` y ImageMagick (`import`, `convert`).
VS Code corre en un monitor virtual, con un perfil y extensiones temporales: no toca el escritorio ni la cuenta de nadie.
El proyecto usa personas ficticias (Ana Ejemplo); nada de lo que se escribe nombra rutas, correos ni cuentas reales."""
from __future__ import annotations

import argparse
import html
import json
import os
import pty
from pathlib import Path
import re
import select
import shutil
import subprocess
import sys
import tempfile
import time

AQUI = Path(__file__).resolve().parents[1]
SITIO, DATOS = AQUI / "site", AQUI / "tests" / "datos" / "ejemplos-demo.json"
GIT = ["git", "-c", "user.name=Ana Ejemplo", "-c", "user.email=ana@ejemplo.org"]
ENTORNO = {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull, "GIT_AUTHOR_NAME": "Ana Ejemplo", "GIT_AUTHOR_EMAIL": "ana@ejemplo.org",
           "GIT_COMMITTER_NAME": "Ana Ejemplo", "GIT_COMMITTER_EMAIL": "ana@ejemplo.org"}
LISTA = '''"""Una lista de tareas mínima."""


def agregar(tareas: list[str], texto: str) -> list[str]:
    if not texto.strip():
        raise ValueError("la tarea necesita un texto")
    return [*tareas, texto.strip()]
'''
PROPUESTA = "## Por qué\n\nQuien usa la lista necesita anotar una tarea y que no se guarde una vacía.\n\n## Qué cambia\n\nSe puede agregar una tarea con texto.\n\n## Fuera de alcance\n\nGuardar en disco.\n\n## Decisiones humanas\n\nNinguna.\n"
SPEC = ("# Capability: lista\n\n## ADDED Requirements\n\n### Requirement: una_tarea_necesita_texto\nTipo: funcional\nEl sistema DEBE rechazar una tarea sin texto.\n\n"
        "#### Scenario: tarea vacía\n- DADA una lista\n- CUANDO se agrega una tarea vacía\n- ENTONCES se rechaza con un error\n")


def correr(args: list[str], cwd: Path, check: bool = True, persona: bool = False) -> str:
    """Corre un comando. Con `persona`, lo hace en una terminal (pty) y responde «1» a cada menú: así decide Ana, la persona del ejemplo."""
    print("$", *args[:4], file=sys.stderr)
    entorno = {**os.environ, **ENTORNO}
    if not persona:
        r = subprocess.run(args, cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True, text=True, env=entorno, timeout=60)
        salida, codigo = r.stdout + r.stderr, r.returncode
    else:
        maestro, esclavo = pty.openpty()
        proceso = subprocess.Popen(args, cwd=cwd, stdin=esclavo, stdout=esclavo, stderr=esclavo, env=entorno)
        os.close(esclavo)
        trozos, limite = [], time.time() + 60
        while time.time() < limite:
            if not select.select([maestro], [], [], 0.2)[0]:
                if proceso.poll() is not None:
                    break
                continue
            try:
                dato = os.read(maestro, 4096)
            except OSError:  # EIO: el hijo cerró su lado
                break
            trozos.append(dato.decode(errors="replace"))
            if re.search(r"Elegí 1-\d+: $", "".join(trozos)):
                os.write(maestro, b"1\n")
                trozos.append("1\n")
        os.close(maestro)
        codigo = proceso.wait(timeout=30)
        salida = "".join(trozos).replace("\r\n", "\n")
    if check and codigo:
        raise SystemExit(f"falló {' '.join(args)}:\n{salida}")
    return salida


def factory(cwd: Path, *args: str, agente: str | None = None) -> str:
    return correr(["oracle-factory", *(["--agente", agente] if agente else []), *args], cwd, persona=agente is None and args[0] in ("tomar", "aprobar-spec"))


def armar_demo(destino: Path) -> tuple[Path, str, str]:
    """El proyecto de ejemplo: dos cambios, uno con la spec aprobada y sus requisitos importados, otro esperando aprobación."""
    d = destino / "lista-de-tareas"
    d.mkdir(parents=True)
    correr(["git", "init", "-q", "-b", "main"], d)
    correr(["git", "config", "user.name", "Ana Ejemplo"], d)
    correr(["git", "config", "user.email", "ana@ejemplo.org"], d)
    (d / "lista.py").write_text(LISTA, encoding="utf-8")
    correr(["git", "add", "-A"], d)
    correr([*GIT, "commit", "-q", "-m", "base"], d)
    factory(d, "init")
    factory(d, "hooks")
    a = re.search(r"Cambio creado: (\S+)", factory(d, "nuevo", "--capacidad", "lista", "--sufijo", "agregar", "Agregar una tarea a la lista", agente="claude-code"))[1]
    cambio = d / "openspec" / "changes" / a
    (cambio / "proposal.md").write_text("# Agregar una tarea a la lista\n\n" + PROPUESTA, encoding="utf-8")
    (cambio / "specs" / "lista" / "spec.md").write_text(SPEC, encoding="utf-8")
    factory(d, "tomar", a, "--con", "claude-code")
    factory(d, "aprobar-spec", a)
    factory(d, "importar", a, agente="claude-code")
    (d / "lista.py").write_text(LISTA + "\n\ndef quitar(tareas: list[str], i: int) -> list[str]:\n    return [t for n, t in enumerate(tareas) if n != i]\n", encoding="utf-8")
    correr(["git", "add", "-A"], d)
    correr([*GIT, "commit", "-q", "-m", f"Quitar una tarea\n\nCambio: {a}"], d)
    b = re.search(r"Cambio creado: (\S+)", factory(d, "nuevo", "--capacidad", "lista", "--sufijo", "hecha", "Marcar una tarea como hecha", agente="claude-code"))[1]
    return d, a, b


def limpio(texto: str, d: Path) -> str:
    """Sin la ruta de la carpeta temporal (la línea «Acuerdos: …» y cualquier otra mención)."""
    texto = "\n".join(l for l in texto.splitlines() if not l.startswith("Acuerdos:"))
    return texto.replace(str(d), "lista-de-tareas").strip("\n")


def ejemplos(d: Path, a: str, b: str) -> dict[str, str]:
    comandos = {"listar": ["listar"], "estado-spec-aprobada": ["estado", a], "estado-sin-aprobar": ["estado", b], "por-que": ["por-que", "lista.py:9"]}
    salida = {}
    for ident, args in comandos.items():
        salida[ident] = f"$ oracle-factory {' '.join(args)}\n{limpio(correr(['oracle-factory', *args], d, check=False), d)}"
    return salida


def aplicar(registro: dict[str, str]) -> None:
    for p in SITIO.glob("*.html"):
        t = p.read_text(encoding="utf-8")
        nuevo = re.sub(r'(<pre\b[^>]*\bdata-ejemplo="([^"]+)"[^>]*>)(.*?)(</pre>)',
                       lambda m: m[1] + html.escape(registro[m[2]], quote=False) + m[4] if m[2] in registro else m[0], t, flags=re.S)
        if nuevo != t:
            p.write_text(nuevo, encoding="utf-8")


# --- capturas -------------------------------------------------------------------------------------------------------------------
VENTANA = "1600x1000x24"
GUION = r'''
set -e
D="$1"; P="$2"; OUT="$3"; X="$4"
trap 'pkill -f "$P/user" 2>/dev/null || true' EXIT INT TERM   # VS Code se cierra aunque un paso falle
env -u WAYLAND_DISPLAY XDG_SESSION_TYPE=x11 code --ozone-platform=x11 --no-sandbox --disable-gpu --user-data-dir "$P/user" --extensions-dir "$P/ext" \
  --disable-workspace-trust --skip-welcome --skip-release-notes "$D" "$D/lista.py" >"$P/code.log" 2>&1 &
sleep 35
W=$(xdotool search --onlyvisible --name "lista-de-tareas" | tail -1)
[ -n "$W" ] || { echo "no apareció la ventana de VS Code" >&2; exit 1; }
paleta() { xdotool key ctrl+shift+p; sleep 2; xdotool type --delay 50 "$1"; sleep 2; xdotool key Return; sleep "${2:-4}"; }
xdotool key ctrl+alt+b; sleep 2                                   # cierra el panel de chat
paleta "View: Focus on Factory View"; sleep 3
xdotool key Home Right; sleep 1; xdotool key Down Down Right; sleep 1      # despliega los dos cambios de la vista
import -window "$W" "$OUT/vscode-explorador.png"
paleta "Factory: Abrir el tablero" 9
import -window "$W" "$OUT/vscode-tablero.png"
xdotool mousemove 800 450; for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do xdotool click 5; done; sleep 2   # baja hasta el segundo cambio
import -window "$W" "$OUT/vscode-pendientes.png"
xdotool mousemove 800 500 click 1; xdotool key ctrl+w; sleep 1
xdotool key ctrl+p; sleep 1; xdotool type --delay 50 "lista.py"; sleep 1; xdotool key Return; sleep 2
xdotool key ctrl+g; sleep 1; xdotool type "9"; xdotool key Return; sleep 1
paleta "Factory: ¿Por qué existe esta línea?" 6
import -window "$W" "$OUT/vscode-por-que.png"
pkill -f "$P/user" 2>/dev/null || true
'''


def capturar(d: Path, tmp: Path) -> None:
    perfil, salida = tmp / "vsc", SITIO / "img"
    (perfil / "user" / "User").mkdir(parents=True)
    # Sin avisos de recomendaciones ni de actualización en la captura.
    (perfil / "user" / "User" / "settings.json").write_text(json.dumps({"extensions.ignoreRecommendations": True, "update.mode": "none",
        "workbench.startupEditor": "none", "telemetry.telemetryLevel": "off", "chat.disableAIFeatures": True}), encoding="utf-8")
    salida.mkdir(exist_ok=True)
    vsix = tmp / "oracle-factory.vsix"  # el .vsix no se versiona: se arma de la carpeta de la extensión
    correr([sys.executable, str(AQUI / "editores" / "vscode" / "empaquetar.py"), "--salida", str(vsix)], AQUI)
    correr(["code", "--user-data-dir", str(perfil / "user"), "--extensions-dir", str(perfil / "ext"), "--install-extension", str(vsix)], d)
    guion = tmp / "capturar.sh"
    guion.write_text(GUION, encoding="utf-8")
    subprocess.run(["xvfb-run", "-a", "-s", f"-screen 0 {VENTANA}", "sh", str(guion), str(d), str(perfil), str(salida), ""], check=True, env={**os.environ, **ENTORNO})
    for png in sorted(salida.glob("vscode-*.png")):
        subprocess.run(["magick", str(png), "-strip", "-resize", "1280x", "-colors", "128", str(png)], check=True)
        print(f"{png.name}: {png.stat().st_size // 1024} KB")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sin-capturas", action="store_true")
    ap.add_argument("--aplicar", action="store_true")
    args = ap.parse_args(argv)
    if not shutil.which("oracle-factory"):
        raise SystemExit("falta oracle-factory en el PATH")
    with tempfile.TemporaryDirectory() as t:
        d, a, b = armar_demo(Path(t))
        registro = ejemplos(d, a, b)
        DATOS.write_text(json.dumps(registro, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        if args.aplicar:
            aplicar(registro)
        if not args.sin_capturas:
            capturar(d, Path(t))
    return 0


if __name__ == "__main__":
    sys.exit(main())
