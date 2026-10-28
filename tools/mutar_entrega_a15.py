"""Mutaciones controladas de la entrega 0.1.0a15.

Comprueba que el detector de divergencias, la comprobación de instalación aislada,
la detección de versiones viejas (0.1.0a14), la verificación de origen, el rechazo de
escrituras y la estabilidad de fuentes detecten fallas significativas.
Restauración en finally; no correr mientras se genera evidencia.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

MUTACIONES = [
    ("version_pyproject_vieja_010a14", "pyproject.toml", 'version = "0.1.0a15"', 'version = "0.1.0a14"', "ea1"),
    ("version_init_vieja_010a14", "oracle_factory/__init__.py", '__version__ = "0.1.0a15"', '__version__ = "0.1.0a14"', "ea1"),
    ("readme_version_divergente", "README.md", "Versión publicada en PyPI: `oracle-factory==0.1.0a15`", "Versión publicada en PyPI: `oracle-factory==0.2.0`", "ea1"),
    ("origen_checkout_no_rechazado", "tools/probar_entrega_a15.py", "if prohibido_resolved in archivo_path.parents or archivo_path == prohibido_resolved:", "if False:", "ea2_origen"),
    ("wheel_010a14_aceptado", "tools/probar_entrega_a15.py", "if version_mod != version_esperada:", "if False:", "ea2_origen"),
    ("mutaciones_identidades_ignoradas", "tools/verify_entrega_a15.py", "if Counter(m.get('id') for m in filas) != esperadas:", "if False:", "integridad_mutaciones"),
    ("mutaciones_fuentes_ignoradas", "tools/verify_entrega_a15.py", "datos.get('fuentes') != origen", "False", "integridad_mutaciones"),
    ("mutacion_viva_aceptada", "tools/verify_entrega_a15.py", "m.get('detectada') is True and", "True and", "integridad_mutaciones"),
    ("mutacion_codigo_cero_aceptado", "tools/verify_entrega_a15.py", "m['codigo'] == 1", "m['codigo'] == 0", "integridad_mutaciones"),
    ("suite_parcial_aceptada", "tools/verify_entrega_a15.py", "resultado.cantidad == esperado", "True", "integridad_suite"),
    ("suite_omitida_aceptada", "tools/verify_entrega_a15.py", "not resultado.skipped", "True", "integridad_suite"),
    ("fuentes_inestables_aceptadas", "tools/verify_entrega_a15.py", "origen == actual", "True", "integridad_resultado"),
    ("arnes_fallido_aceptado", "tools/verify_entrega_a15.py", "arneses.get(n, {}).get('returncode') == 0", "True", "integridad_resultado"),
    ("linea_base_fallida_aceptada", "tools/verify_entrega_a15.py", "b['codigo'] == 0", "True", "integridad_mutaciones"),
    ("simulacion_oculta", "tools/probar_entrega_a15.py", '"simulado": True', '"simulado": False', "ea2_consultas"),
    ("novedad_plantilla_en_ingles_ignorada", "tools/probar_entrega_a15.py", 'if "The system SHALL" not in spec or "DEBE" in spec or', 'if False or', "ea2_novedades"),
    ("novedad_bloqueo_sin_linea_ignorado", "tools/probar_entrega_a15.py", '"proposal.md (línea " not in texto or ', '', "ea2_novedades"),
    ("novedad_conteo_de_specs_ignorado", "tools/probar_entrega_a15.py", 'if cuenta.get("valor") != {"vigentes": 0, "en_cambios_abiertos": 1} or cuenta.get("modelo_generativo"):', 'if False:', "ea2_novedades"),
    ("novedad_lista_de_specs_ignorada", "tools/probar_entrega_a15.py", 'if (not any(\'"operacion": "listar"\' in f.get("cita", "") for f in lista.get("fuentes") or [])', 'if (False', "ea2_novedades"),
    ("publicacion_prematura_no_detectada", "tools/docs_al_dia.py", 'if not notas.is_file() or f"# Oracle Factory {version} (en preparación)" not in notas.read_text(encoding="utf-8"):', 'if True:', "ea1"),
    ("publicacion_prematura_sin_notas", "tools/docs_al_dia.py", 'la declara en preparación"\n            for nombre, texto in todo.items() if afirma.search(texto)]', 'la declara en preparación"\n            for nombre, texto in todo.items() if False]', "ea1"),
    ("preparacion_olvidada_no_detectada", "tools/docs_al_dia.py", 'if not notas.is_file() or f"\\n# Oracle Factory {version}\\n" not in "\\n" + notas.read_text(encoding="utf-8"):', 'if True:', "ea1"),
    ("preparacion_olvidada_sin_patron_cuando_se_publique", "tools/docs_al_dia.py", 'r"cuando se publique esta versi[oó]n", ', '', "ea1"),
    ("novedad_filtro_aceptado", "tools/probar_entrega_a15.py", 'if filtro.get("tipo") != "consulta_no_admitida" or filtro.get("resultados"):', 'if False:', "ea2_novedades"),
    ("novedad_tablero_sin_faltan_ignorado", "tools/probar_entrega_a15.py", 'if "yo" not in tablero or not cambio["faltan"] or not all({"texto", "humano", "quien"} <= set(x) for x in cambio["faltan"]):', 'if False:', "ea2_novedades"),
    ("novedad_actividad_ignorada", "tools/probar_entrega_a15.py", 'if not any(e["cambio"] == ident and e["accion"] == "cambio_creado" for e in tablero["proyecto"]["actividad"]):', 'if False:', "ea2_novedades"),
]

CASOS = {
    "ea1": "test_ea1_version_coherente_y_estado_declarado",
    "ea2_origen": "test_ea2_el_origen_y_la_version_instalados_se_verifican",
    "ea2_novedades": "test_ea2_la_validacion_de_las_novedades_rechaza_cada_novedad_que_falta",
    "ea2_consultas": "test_ea2_las_consultas_de_la_entrega_anterior_siguen_en_el_wheel",
    "ea3": "test_ea3_entrega_registra_pruebas_y_limites",
    "integridad_mutaciones": "test_mutaciones_exigen_identidades_y_fuentes_actuales",
    "integridad_suite": "test_suite_exige_todos_los_casos_sin_omisiones_ni_fallas",
    "integridad_resultado": "test_resultado_exige_arneses_y_fuentes_estables",
}


def fuentes():
    from tools.verify_entrega_a15 import fuentes as actuales
    return actuales()


def ejecutar_caso(caso):
    return subprocess.run(
        [
            sys.executable,
            "-B",
            "-m",
            "unittest",
            (f"tests.test_entrega_integridad_a15.IntegridadEntrega.{CASOS[caso]}" if caso.startswith('integridad_')
             else f"tests.test_entrega_a15.EntregaA15.{CASOS[caso]}"),
        ],
        cwd=ROOT,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=240,
        env={**os.environ, "PYTHONPYCACHEPREFIX": "/tmp/factory-mutaciones-sin-cache", "PYTHONDONTWRITEBYTECODE": "1"},
    )


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--salida", type=Path, default=ROOT / ".factory/local/mutaciones_entrega_a15.json")
    args = p.parse_args()

    sys.path.insert(0, str(ROOT))
    if args.salida.exists():
        p.error('usar una salida nueva; no se reemplazan resultados anteriores')
    origen = fuentes()
    filas = []
    log_lineas = []
    linea_base = []
    for caso in sorted({m[4] for m in MUTACIONES}):
        corrida = ejecutar_caso(caso)
        linea_base.append({'caso': CASOS[caso], 'codigo': corrida.returncode,
                           'salida': corrida.stdout + corrida.stderr})
    if any(b['codigo'] != 0 for b in linea_base):
        args.salida.parent.mkdir(parents=True, exist_ok=True)
        with args.salida.open('x', encoding='utf-8') as salida:
            json.dump({'fuentes': origen, 'linea_base': linea_base, 'mutaciones': [],
                       'todas_detectadas': False, 'error': 'línea base fallida; no se mutaron fuentes'},
                      salida, ensure_ascii=False, indent=2)
        for b in linea_base:
            if b['codigo']:
                print(b['salida'])
        return 1

    try:
        for ident, rel, antes, despues, caso in MUTACIONES:
            archivo = ROOT / rel
            original = archivo.read_bytes()
            texto = original.decode("utf-8")
            if texto.count(antes) != 1:
                raise RuntimeError(f"{ident}: se esperaba una ocurrencia exacta de '{antes}', hay {texto.count(antes)} en {rel}")
            try:
                archivo.write_text(texto.replace(antes, despues, 1), encoding="utf-8")
                corrida = ejecutar_caso(caso)
                detectada = (
                    corrida.returncode == 1
                    and ("FAILED (" in corrida.stderr or "FAIL:" in corrida.stderr or "ERROR:" in corrida.stderr)
                    and "Ran 1 test" in corrida.stderr
                    and not any(s in corrida.stderr for s in ("SyntaxError", "ImportError", "ModuleNotFoundError"))
                )
                filas.append({
                    "id": ident,
                    "archivo": rel,
                    "caso": CASOS[caso],
                    "detectada": detectada,
                    "codigo": corrida.returncode,
                    "salida": corrida.stderr[-2000:],
                })
                estado_str = "DETECTADA" if detectada else "NO DETECTADA"
                log_lineas.append(f"{ident} ({CASOS[caso]}): {estado_str} (código {corrida.returncode})")
                print(f"{ident:35} {estado_str}")
            finally:
                archivo.write_bytes(original)
    finally:
        # Asegurar restauración completa
        restantes = fuentes()
        if restantes != origen:
            for k in origen:
                if restantes.get(k) != origen[k]:
                    print(f"ADVERTENCIA: Archivo {k} difiere tras mutaciones, restaurando...")

    actuales = fuentes()
    if actuales != origen:
        raise RuntimeError("Las fuentes no quedaron idénticas tras restaurar mutaciones.")

    todas_detectadas = len(filas) == len(MUTACIONES) and all(f["detectada"] for f in filas)
    resultado = {
        "fuentes": origen,
        "linea_base": linea_base,
        "mutaciones": filas,
        "total": len(filas),
        "detectadas": sum(f["detectada"] for f in filas),
        "todas_detectadas": todas_detectadas,
    }

    if args.salida:
        args.salida.parent.mkdir(parents=True, exist_ok=True)
        with args.salida.open('x', encoding='utf-8') as salida:
            salida.write(json.dumps(resultado, indent=2, ensure_ascii=False) + "\n")
        log_path = args.salida.with_suffix(".log")
        log_path.write_text("\n".join(log_lineas) + "\n", encoding="utf-8")

    print(f"\nResumen: {resultado['detectadas']}/{resultado['total']} mutaciones detectadas. Fuentes intactas: {actuales == origen}.")
    return 0 if todas_detectadas else 1


if __name__ == "__main__":
    raise SystemExit(main())
