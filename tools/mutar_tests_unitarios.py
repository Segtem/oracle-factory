"""Mutaciones controladas de los tests unitarios como práctica: el paso en las tareas, la guía para agentes y docs/tests.md.

Cada mutación cambia una cosa y el caso que la vigila debe fallar. Restauración en finally; no correr mientras se genera evidencia.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
P, G, D = 'PasoDeTests', 'GuiaDeTests', 'DocumentoDeTests'
PASO_ES = '- [ ] Agente: escribir primero los tests de cada escenario de la spec, cuando sea posible, y comprobar que fallan antes de implementar.\n'
PASO_EN = '- [ ] Agent: write the tests for each spec scenario first, when possible, and check that they fail before implementing.\n'
IMPL_ES = '- [ ] Agente: implementar y correr las pruebas del producto.\n'
GUARDA = 'Un test que ya existía no se edita para que pase sin dejarlo dicho a quien revisa'

MUTACIONES = [
    ("paso_es_sacado", "oracle_factory/plantillas.py", PASO_ES, "", P, "test_tu1_un_cambio_nuevo_en_espanol"),
    ("paso_en_sacado", "oracle_factory/plantillas.py", PASO_EN, "", P, "test_tu1_un_cambio_nuevo_en_ingles"),
    ("paso_es_despues_de_implementar", "oracle_factory/plantillas.py", PASO_ES + IMPL_ES, IMPL_ES + PASO_ES, P, "test_tu1_la_plantilla_de_cada_idioma_lo_trae"),
    ("paso_con_marca_de_pendiente", "oracle_factory/plantillas.py", "antes de implementar.\n- [ ] Agente: implementar", "antes de implementar. TODO: completar\n- [ ] Agente: implementar", P, "test_tu1_el_paso_no_bloquea"),
    ("guia_sin_la_practica", "oracle_factory/agentes.py", "Los tests unitarios son parte del desarrollo y no suplantan a Oracle", "Los tests son opcionales", G, "test_tu2_la_guia_generada_lo_dice"),
    ("guia_sin_la_guarda", "oracle_factory/agentes.py", GUARDA, "Un test que ya existía se edita sin avisar", G, "test_tu2_la_guia_generada_lo_dice"),
    ("doc_sin_fuente", "docs/tests.md", "arXiv 2402.13521", "arXiv sin número", D, "test_tu3_explica_las_tres_capas_y_cita_las_fuentes"),
    ("doc_sin_la_guarda", "docs/tests.md", "un test que ya existía no se edita para que pase sin dejarlo dicho a quien revisa", "los tests se editan", D, "test_tu3_explica_las_tres_capas_y_cita_las_fuentes"),
    ("doc_dice_que_bloquea", "docs/tests.md", "El paso no bloquea:", "El paso bloquea:", D, "test_tu3_dice_lo_mismo_que_la_plantilla"),
]


def fuentes():
    from tools.verify_tests_unitarios import fuentes as actuales
    return actuales()


def ejecutar(clase, caso):
    return subprocess.run([sys.executable, "-B", "-m", "unittest", f"tests.test_tests_unitarios.{clase}.{caso}"], cwd=ROOT,
                          stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=240,
                          env={**os.environ, "PYTHONPYCACHEPREFIX": "/tmp/factory-mutaciones-sin-cache", "PYTHONDONTWRITEBYTECODE": "1"})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--salida", type=Path, default=ROOT / ".factory/local/mutaciones_tests_unitarios.json")
    args = p.parse_args()
    sys.path.insert(0, str(ROOT))
    if args.salida.exists():
        p.error('usar una salida nueva; no se reemplazan resultados anteriores')
    origen = fuentes()
    base = [{'caso': f'{c}.{k}', 'codigo': (r := ejecutar(c, k)).returncode, 'salida': r.stdout + r.stderr}
            for c, k in sorted({(m[4], m[5]) for m in MUTACIONES})]
    if any(b['codigo'] for b in base):
        print('Línea base fallida; no se mutó nada.\n' + '\n'.join(b['salida'] for b in base if b['codigo']))
        return 1
    filas = []
    for ident, rel, antes, despues, clase, caso in MUTACIONES:
        archivo = ROOT / rel
        original = archivo.read_bytes()
        texto = original.decode("utf-8")
        if texto.count(antes) != 1:
            raise RuntimeError(f"{ident}: se esperaba una ocurrencia exacta, hay {texto.count(antes)} en {rel}")
        try:
            archivo.write_text(texto.replace(antes, despues, 1), encoding="utf-8")
            r = ejecutar(clase, caso)
        finally:
            archivo.write_bytes(original)
        detectada = (r.returncode == 1 and ("FAIL:" in r.stderr or "ERROR:" in r.stderr) and "Ran 1 test" in r.stderr
                     and not any(s in r.stderr for s in ("SyntaxError", "ImportError", "ModuleNotFoundError")))
        filas.append({"id": ident, "archivo": rel, "caso": f"{clase}.{caso}", "detectada": detectada, "codigo": r.returncode, "salida": r.stderr[-2000:]})
        print(f"{ident:35} {'DETECTADA' if detectada else 'NO DETECTADA'}")
    if fuentes() != origen:
        raise RuntimeError("Las fuentes no quedaron idénticas tras restaurar mutaciones.")
    todas = all(f["detectada"] for f in filas)
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    with args.salida.open('x', encoding='utf-8') as s:
        s.write(json.dumps({"fuentes": origen, "linea_base": base, "mutaciones": filas, "total": len(filas),
                            "detectadas": sum(f["detectada"] for f in filas), "todas_detectadas": todas}, indent=2, ensure_ascii=False) + "\n")
    print(f"\nResumen: {sum(f['detectada'] for f in filas)}/{len(filas)} mutaciones detectadas.")
    return 0 if todas else 1


if __name__ == "__main__":
    raise SystemExit(main())
