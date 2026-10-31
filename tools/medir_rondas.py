"""Mide las rondas de revisión de los cambios cerrados: cuántos hallazgos trae cada ronda y de qué clases. Sólo lectura.

Uso: python tools/medir_rondas.py [--desde AAAA-MM-DD] [--proyecto RUTA]

Una ronda es un candidato que se pidió revisar; su número sale del ORDEN CRONOLÓGICO de los eventos de revisión del cambio
(`revision_pedida` / `revision_lanzada`), nunca del nombre de la carpeta del candidato (es un SHA) ni de la fecha de los
archivos (en un clon o tras un merge reflejan cuándo se escribieron, no cuándo se hizo la revisión)."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime
import json
from pathlib import Path
import re
import statistics

CLASES = {
    "rutas, «..» y enlaces": r"symlink|enlace[s]? simb|traversal|\.\.|ruta_segura|sin_enlaces",
    "valores raros o corruptos que rompen": r"AttributeError|TypeError|ValueError|no[- ]texto|traceback|byte nulo|malformad|corrupt|no capturad",
    "paridad con otra herramienta": r"importador|openspec|exigir_spec|paridad|divergen",
    "pruebas débiles (mutantes, por construcción)": r"mutaci[oó]n|sobreviv|mutante|por construcci[oó]n|cobertura incompleta",
    "falsos avisos o silencios": r"falso|calla|silenci|no avisa|oculta",
    "verificador y evidencia": r"verify_|fuentes_estables|trazabilidad\.trazar|estabilidad",
    "documentos y mensajes contra el código": r"docs/|documentaci[oó]n|docstring|promete|afirma",
}
SEVERIDADES = ("alta", "media", "baja", "informativa")


def leer_json(ruta: Path):
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def rondas_de(eventos: list[dict]) -> dict[str, int]:
    """{candidato: número de ronda} por el primer evento de revisión de cada candidato, en orden cronológico."""
    primero: dict[str, datetime] = {}
    for e in eventos:
        if e.get("accion") in ("revision_pedida", "revision_lanzada") and e.get("candidato") and e.get("cuando"):
            cuando = datetime.fromisoformat(e["cuando"])
            primero[e["candidato"]] = min(primero.get(e["candidato"], cuando), cuando)
    return {candidato: i for i, candidato in enumerate(sorted(primero, key=lambda c: (primero[c], c)), 1)}


def analizar(proyecto: Path, desde: str = "2026-10-24") -> dict:
    por_ronda: dict[int, Counter] = defaultdict(Counter)
    clases: dict[str, Counter] = defaultdict(Counter)
    rondas_por_cambio: list[int] = []
    for registro in sorted((proyecto / ".factory" / "cambios").glob("*/factory.json")):
        datos = leer_json(registro)
        if not isinstance(datos, dict):
            continue
        eventos = [e for e in datos.get("eventos") or [] if isinstance(e, dict)]
        creado = [e for e in eventos if e.get("accion") == "cambio_creado"]
        if not creado or creado[0].get("cuando", "") < desde or not any(e.get("accion") == "cierre" for e in eventos):
            continue
        rondas = rondas_de(eventos)
        rondas_por_cambio.append(len(rondas))
        for informe in sorted(registro.parent.glob("candidatos/*/revision/*.json")):
            if informe.name.endswith(".pedido.json"):
                continue
            candidato = informe.parts[-3]
            contenido = leer_json(informe)
            if not isinstance(contenido, dict) or candidato not in rondas:
                continue
            ronda = min(rondas[candidato], 5)
            for hallazgo in contenido.get("findings") or []:
                severidad = hallazgo.get("severity")
                por_ronda[ronda][severidad] += 1
                if severidad in ("alta", "media"):
                    texto = f"{hallazgo.get('title', '')} {str(hallazgo.get('explanation', ''))[:600]}"
                    for nombre, patron in CLASES.items():
                        if re.search(patron, texto, re.IGNORECASE):
                            clases[nombre][ronda] += 1
    return {"cambios": len(rondas_por_cambio),
            "rondas_mediana": statistics.median(rondas_por_cambio) if rondas_por_cambio else 0,
            "rondas_maximo": max(rondas_por_cambio, default=0),
            "por_ronda": {r: dict(c) for r, c in sorted(por_ronda.items())},
            "clases": {n: dict(c) for n, c in sorted(clases.items(), key=lambda kv: -sum(kv[1].values()))}}


def texto(resultado: dict) -> str:
    lineas = [f"{resultado['cambios']} cambios cerrados; rondas por cambio: mediana {resultado['rondas_mediana']}, máximo {resultado['rondas_maximo']}",
              "ronda    alta  media   baja  info | total | alta+media"]
    for ronda, c in resultado["por_ronda"].items():
        n = lambda s: c.get(s, 0)  # noqa: E731
        lineas.append(f"  {ronda}{'+' if ronda == 5 else ' '}   {n('alta'):5} {n('media'):6} {n('baja'):6} {n('informativa'):5} | {sum(c.values()):5} | {n('alta') + n('media'):5}")
    lineas.append("clases de los hallazgos altos y medios (total y por ronda 1, 2, 3, 4, 5+):")
    for nombre, c in resultado["clases"].items():
        lineas.append(f"  {sum(c.values()):3}  {nombre:46} {[c.get(i, 0) for i in range(1, 6)]}")
    return "\n".join(lineas) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--desde", default="2026-10-24", help="sólo los cambios creados desde esta fecha")
    parser.add_argument("--proyecto", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    print(texto(analizar(args.proyecto, args.desde)), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
