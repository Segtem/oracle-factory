"""Mutaciones controladas de la entrega 0.1.0a16.

Comprueba que el detector de divergencias, la comprobación de instalación aislada,
la detección de versiones viejas (0.1.0a15), la verificación de origen, el rechazo de
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
    ("version_pyproject_vieja_010a15", "pyproject.toml", 'version = "0.1.0a16"', 'version = "0.1.0a15"', "ea1"),
    ("version_init_vieja_010a15", "oracle_factory/__init__.py", '__version__ = "0.1.0a16"', '__version__ = "0.1.0a15"', "ea1"),
    ("lock_con_otra_version", "uv.lock", 'name = "oracle-factory"\nversion = "0.1.0a16"', 'name = "oracle-factory"\nversion = "0.1.0a15"', "ea1"),
    ("readme_version_divergente", "README.md", "Candidato en preparación `oracle-factory==0.1.0a16`", "Candidato en preparación `oracle-factory==0.2.0`", "ea1"),
    ("origen_checkout_no_rechazado", "tools/probar_entrega_a16.py", "if prohibido_resolved in archivo_path.parents or archivo_path == prohibido_resolved:", "if False:", "ea2_origen"),
    ("wheel_010a15_aceptado", "tools/probar_entrega_a16.py", "if version_mod != version_esperada:", "if False:", "ea2_origen"),
    ("mutaciones_identidades_ignoradas", "tools/verify_entrega_a16.py", "if Counter(m.get('id') for m in filas) != esperadas:", "if False:", "integridad_mutaciones"),
    ("mutaciones_fuentes_ignoradas", "tools/verify_entrega_a16.py", "datos.get('fuentes') != origen", "False", "integridad_mutaciones"),
    ("mutacion_viva_aceptada", "tools/verify_entrega_a16.py", "m.get('detectada') is True and", "True and", "integridad_mutaciones"),
    ("mutacion_codigo_cero_aceptado", "tools/verify_entrega_a16.py", "m['codigo'] == 1", "m['codigo'] == 0", "integridad_mutaciones"),
    ("suite_parcial_aceptada", "tools/verify_entrega_a16.py", "resultado.cantidad == esperado", "True", "integridad_suite"),
    ("suite_omitida_aceptada", "tools/verify_entrega_a16.py", "not resultado.skipped", "True", "integridad_suite"),
    ("fuentes_inestables_aceptadas", "tools/verify_entrega_a16.py", "origen == actual", "True", "integridad_resultado"),
    ("arnes_fallido_aceptado", "tools/verify_entrega_a16.py", "arneses.get(n, {}).get('returncode') == 0", "True", "integridad_resultado"),
    ("linea_base_fallida_aceptada", "tools/verify_entrega_a16.py", "b['codigo'] == 0", "True", "integridad_mutaciones"),
    ("simulacion_oculta", "tools/probar_entrega_a16.py", '"simulado": True', '"simulado": False', "ea2_consultas"),
    ("novedad_inventario_no_cyclonedx_aceptado", "tools/probar_entrega_a16.py", 'if inventario.get("bomFormat") != "CycloneDX" or ("alfa", "1.2.3") not in nombres:', 'if False:', "ea2_novedades"),
    ("novedad_inventario_sin_guardar_aceptado", "tools/probar_entrega_a16.py", 'if len(o["guardados"]) != 1 or not o["guardados"][0].startswith(f".factory/cambios/{ident}/candidatos/"):', 'if False:', "ea2_novedades"),
    ("novedad_busqueda_ignorada", "tools/probar_entrega_a16.py", 'if ident not in o["buscar"] or "alfa" not in o["buscar"]:', 'if False:', "ea2_novedades"),
    ("novedad_auditoria_ignorada", "tools/probar_entrega_a16.py", 'if "GHSA-prueba-0001" not in o["auditar"] or ident not in o["auditar"] or "Afectados" not in o["auditar"]:', 'if False:', "ea2_novedades"),
    ("novedad_consulta_sin_bandera_ignorada", "tools/probar_entrega_a16.py", 'if "--red" not in o["sin_red"] or o["pedidos_sin_red"] != 0:', 'if False:', "ea2_novedades"),
    ("novedad_consulta_con_red_ignorada", "tools/probar_entrega_a16.py", 'if "GHSA-prueba-0001" not in o["con_red"] or ident not in o["con_red"] or "Afectados" not in o["con_red"]:', 'if False:', "ea2_novedades"),
    ("novedad_avisos_guardados_ignorados", "tools/probar_entrega_a16.py", 'if [a.get("id") for a in o["avisos_guardados"]] != ["GHSA-prueba-0001"]:', 'if False:', "ea2_novedades"),
    ("novedad_consultas_de_mas_aceptadas", "tools/probar_entrega_a16.py", 'if o["consultas"] != [{"package": {"name": "alfa", "ecosystem": "PyPI"}, "version": "1.2.3"}]:', 'if False:', "ea2_novedades"),
    ("arnes_de_instalacion_fallido_ignorado", "tools/probar_entrega_a16.py", "    if r1.returncode != 0:", "    if False:", "ea3"),
    ("arnes_de_guia_fallido_ignorado", "tools/probar_entrega_a16.py", "    if r2.returncode != 0:", "    if False:", "ea3"),
    ("arbol_sucio_aceptado", "tools/verify_entrega_a16.py", "    return salida.strip() == ''", "    return True", "integridad_arbol"),
    ("rutas_del_checkout_en_la_evidencia", "tools/verify_entrega_a16.py", "((str(ROOT), '<repo>'), (str(Path.home()), '<home>'))", "((str(Path.home()), '<home>'),)", "integridad_rutas"),
    ("rutas_temporales_en_la_evidencia", "tools/verify_entrega_a16.py", "    texto = re.sub(r'/(?:tmp|var/tmp)/[^\"\\\\\\s]*', '<tmp>', texto)\n", "", "integridad_rutas"),
    ("publicacion_prematura_no_detectada", "tools/docs_al_dia.py", 'if not notas.is_file() or f"# Oracle Factory {version} (en preparación)" not in notas.read_text(encoding="utf-8"):', 'if True:', "ea1"),
    ("publicacion_prematura_sin_notas", "tools/docs_al_dia.py", 'la declara en preparación"\n            for nombre, texto in todo.items() if afirma.search(texto)]', 'la declara en preparación"\n            for nombre, texto in todo.items() if False]', "ea1"),
    ("preparacion_olvidada_no_detectada", "tools/docs_al_dia.py", 'if not notas.is_file() or f"\\n# Oracle Factory {version}\\n" not in "\\n" + notas.read_text(encoding="utf-8"):', 'if True:', "ea1"),
    ("preparacion_olvidada_sin_patron_cuando_se_publique", "tools/docs_al_dia.py", 'r"cuando se publique esta versi[oó]n", ', '', "ea1"),
]

CASOS = {
    "ea1": "test_ea1_version_coherente_y_estado_declarado",
    "ea2_origen": "test_ea2_el_origen_y_la_version_instalados_se_verifican",
    "ea2_novedades": "test_ea2_la_validacion_de_las_novedades_rechaza_cada_novedad_que_falta",
    "ea2_consultas": "test_ea2_las_consultas_de_la_entrega_anterior_siguen_en_el_wheel",
    "ea3": "test_ea3_un_arnes_fallido_no_se_registra_como_exitoso",
    "integridad_arbol": "test_el_arbol_debe_coincidir_con_head_para_atar_la_evidencia_al_commit",
    "integridad_rutas": "test_la_evidencia_de_instalacion_no_lleva_rutas_de_esta_maquina",
    "integridad_mutaciones": "test_mutaciones_exigen_identidades_y_fuentes_actuales",
    "integridad_suite": "test_suite_exige_todos_los_casos_sin_omisiones_ni_fallas",
    "integridad_resultado": "test_resultado_exige_arneses_y_fuentes_estables",
}


def fuentes():
    from tools.verify_entrega_a16 import fuentes as actuales
    return actuales()


def ejecutar_caso(caso):
    return subprocess.run(
        [
            sys.executable,
            "-B",
            "-m",
            "unittest",
            (f"tests.test_entrega_integridad_a16.IntegridadEntrega.{CASOS[caso]}" if caso.startswith('integridad_')
             else f"tests.test_entrega_a16.EntregaA16.{CASOS[caso]}"),
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
    p.add_argument("--salida", type=Path, default=ROOT / ".factory/local/mutaciones_entrega_a16.json")
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
