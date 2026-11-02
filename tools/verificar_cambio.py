"""Produce la evidencia de un cambio sin un verificador escrito a mano.

Uso: python tools/verificar_cambio.py ID --pruebas test_x [--salida CARPETA] [--catalogos] [--raiz RUTA]

Una prueba `test_<letras><n>_…` del módulo prueba el requisito número `n` de la spec del cambio, en el orden en que la spec los lista.
La herramienta falla (y no declara éxito) si un requisito no tiene casos, si un caso nombra un número sin requisito o si no hay casos."""
from __future__ import annotations

import argparse
from collections import Counter
import ast
from importlib import metadata
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest

AQUI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AQUI))
from tools.verify_review_guided import Resultado, escribir, sha  # noqa: E402
from oracle_factory import archivo, modos, trazabilidad  # noqa: E402

CASO = re.compile(r"test_[a-z]{2,3}(\d+)_")
REQUISITO = archivo.CABECERA_REQ  # la misma cabecera que lee Factory al importar
DELTA = re.compile(r"^##\s+(ADDED|MODIFIED|REMOVED|RENAMED)\s+Requirements\s*$", re.IGNORECASE)  # la de modos.tipos_spec
SIN_FUENTES = (".factory/", "kb/", "tareas/")  # los registros generados no son producto


class ContratoInvalido(Exception):
    """Los nombres de las pruebas y la spec no coinciden: no se puede decir qué prueba qué."""


def casos_del_modulo(texto: str) -> dict[int, list[str]]:
    """{n: ['Clase.método', …]}: los métodos `test_<letras><n>_…` de las clases del módulo (leídas con `ast`, no con el texto)."""
    casos: dict[int, list[str]] = {}
    for clase in ast.parse(texto).body:
        # Sin base, o sólo con `object`, no puede ser un TestCase: unittest no la correría. Con cualquier otra base (también una importada o
        # una clase propia del módulo) se cuenta: si no corre, el hecho de ese caso queda con código 1 y la evidencia en rojo.
        if isinstance(clase, ast.ClassDef) and any(not (isinstance(b, ast.Name) and b.id == "object") for b in clase.bases):
            for metodo in clase.body:
                if isinstance(metodo, (ast.FunctionDef, ast.AsyncFunctionDef)) and (m := CASO.match(metodo.name)):
                    casos.setdefault(int(m[1]), []).append(f"{clase.name}.{metodo.name}")
    return {n: sorted(lista) for n, lista in sorted(casos.items())}


def requisitos_de_la_spec(texto: str) -> list[str]:
    """Los requisitos de la spec en el orden en que aparecen, como los importa Factory: el nombre del «### Requirement: …» pasado a
    slug (`modos.slug`). Los de una sección REMOVED no se importan ni se miden."""
    retirados, nombres = False, []
    for linea in texto.splitlines():
        if delta := DELTA.match(linea):
            retirados = delta[1].upper() == "REMOVED"
        elif (m := REQUISITO.match(linea)) and not retirados:
            nombres.append(modos.slug(m[1]))
    return nombres


def contrato(requisitos: list[str], casos: dict[int, list[str]]) -> dict[str, list[str]]:
    """{requisito: [casos]}; ContratoInvalido si algún requisito queda sin casos, si un caso nombra un requisito que no existe o si no hay casos."""
    if not casos:
        raise ContratoInvalido("el módulo no tiene ningún caso test_<letras><n>_…")
    repetidos = sorted({r for r in requisitos if requisitos.count(r) > 1})
    if repetidos:
        raise ContratoInvalido(f"requisitos repetidos en la spec (un caso no podría decir a cuál pertenece): {', '.join(repetidos)}")
    huerfanos = [c for n, lista in casos.items() if not 1 <= n <= len(requisitos) for c in lista]
    if huerfanos:
        raise ContratoInvalido(f"casos que nombran un requisito que la spec no tiene ({len(requisitos)} requisitos): {', '.join(huerfanos)}")
    sin_casos = [r for i, r in enumerate(requisitos, 1) if i not in casos]
    if sin_casos:
        raise ContratoInvalido(f"requisitos sin ningún caso: {', '.join(sin_casos)}")
    return {r: casos[i] for i, r in enumerate(requisitos, 1)}


def leer_contrato(raiz: Path, cambio: str, modulo: str) -> tuple[dict[str, list[str]], dict[str, str]]:
    """(contrato por nombre de requisito, {nombre: id completo del registro}) del cambio en `raiz`."""
    carpeta = raiz / "openspec" / "changes" / cambio
    specs = sorted((carpeta / "specs").glob("*/spec.md"))
    if not specs:
        raise ContratoInvalido(f"no encuentro la spec del cambio {cambio} en {carpeta}")
    try:
        requisitos = [r for spec in specs for r in requisitos_de_la_spec(spec.read_text(encoding="utf-8"))]
    except (OSError, ValueError) as e:  # ValueError incluye UnicodeDecodeError
        raise ContratoInvalido(f"no puedo leer la spec del cambio {cambio}: {e}") from e
    registro = raiz / ".factory" / "cambios" / cambio / "factory.json"
    try:
        ids = {i.rsplit(".", 1)[-1]: i for i in json.loads(registro.read_text(encoding="utf-8")).get("requisitos") or []}
    except (OSError, ValueError, AttributeError) as e:
        raise ContratoInvalido(f"no puedo leer el registro del cambio {cambio} ({registro}): {e}") from e
    faltan = [r for r in requisitos if r not in ids]
    if faltan:
        raise ContratoInvalido(f"requisitos de la spec que el registro no importó: {', '.join(faltan)}")
    archivo = raiz / "tests" / f"{modulo}.py"
    try:
        casos = casos_del_modulo(archivo.read_text(encoding="utf-8"))
    except (OSError, ValueError, SyntaxError) as e:
        raise ContratoInvalido(f"no puedo leer las pruebas {archivo}: {e}") from e
    return contrato(requisitos, casos), {r: ids[r] for r in requisitos}


def fuentes(raiz: Path, salida: Path | None = None) -> dict:
    """Todo lo versionado o nuevo del producto con su hash; sin los registros generados ni la carpeta de evidencia."""
    raiz, salida = raiz.resolve(), salida.resolve() if salida else None
    nombres = subprocess.run(["git", "-C", str(raiz), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                             text=True, capture_output=True, check=True).stdout.split("\0")  # -z: nombres no ASCII sin comillas
    elegidos = [raiz / n for n in nombres if n and not n.startswith(SIN_FUENTES) and (raiz / n).is_file()
                and not (salida and (raiz / n).is_relative_to(salida))]
    head = subprocess.run(["git", "-C", str(raiz), "rev-parse", "HEAD"], text=True, capture_output=True, check=True).stdout.strip()
    return {"head": head, "sha256": {p.relative_to(raiz).as_posix(): sha(p) for p in sorted(elegidos)}}


def producir(raiz: Path, cambio: str, modulo: str, salida: Path) -> bool:
    """Corre la suite y escribe suite.txt, hechos.json, trazabilidad.json y resultado.json en `salida`; True si hay éxito."""
    raiz, salida = raiz.resolve(), salida.resolve()
    por_nombre, ids = leer_contrato(raiz, cambio, modulo)  # antes de crear nada: un contrato roto no deja una carpeta a medias
    salida.mkdir(parents=True, exist_ok=False)
    x, prefijo = modulo.removeprefix("test_"), f"{modulo}."
    origen = fuentes(raiz, salida)
    sys.path.insert(0, str(raiz / "tests"))
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.discover(str(raiz / "tests"))
    resultado = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=Resultado).run(suite)
    esperados = [prefijo + c for lista in por_nombre.values() for c in lista]
    observados = {n: k for n, k in resultado.cantidad.items() if n.startswith(prefijo) and CASO.match(n.rsplit(".", 1)[-1])}
    completa = observados == Counter(esperados) and all(resultado.observados.get(n, 1) == 0 for n in esperados)
    filas = [{"requisito": r, "caso": c, "codigo": resultado.observados.get(prefijo + c, 1)} for r, lista in por_nombre.items() for c in lista]
    (salida / "suite.txt").write_text(stream.getvalue(), encoding="utf-8")
    try:
        traza = trazabilidad.trazar(raiz, {ids[r]: [prefijo + c for c in lista] for r, lista in por_nombre.items()})
        trazada = all(c.get("resultado") == "ok" for c in traza["casos"].values()) and len(traza["casos"]) == len(esperados)
    except Exception as e:  # un caso que no se puede cargar deja la evidencia en rojo y entera, no a medias
        traza, trazada = {"error": f"{type(e).__name__}: {e}"}, False
    escribir(salida / "trazabilidad.json", traza)
    estables = fuentes(raiz, salida) == origen  # después de la segunda corrida, la trazada: ahí también tienen que seguir quietas
    exito = resultado.wasSuccessful() and completa and estables and trazada
    escribir(salida / "hechos.json", {f"{x}_caso": filas, f"{x}_corrida": [{"completa": int(exito), "casos": len(esperados)}]})
    versiones = {p: metadata.version(p) for p in ("oracle-metalenguaje", "oracle-task", "oracle-clue") if _instalado(p)}
    escribir(salida / "resultado.json", {
        "exitoso": exito, "tests": resultado.testsRun, "casos_contrato": len(esperados),
        "casos_exactos_sin_omisiones_duplicados_ni_fallas": completa, "fuentes_estables": estables, "origen": origen,
        "versiones": {**versiones, "python": sys.version},
        "limites": "Casos derivados de los nombres de las pruebas; comprueban lo que ellos prueban, no que la spec esté completa.",
        "artefactos_sha256": {n: sha(salida / n) for n in ("suite.txt", "hechos.json", "trazabilidad.json")}})
    return exito


def _instalado(paquete: str) -> bool:
    try:
        metadata.version(paquete)
        return True
    except metadata.PackageNotFoundError:
        return False


def catalogo_de_requisito(x: str, requisito: str, casos: int, alcance: str) -> str:
    return (f"medida factory_{x}.{requisito}:\n    de {x}_caso c\n    donde c.requisito == \"{requisito}\" y c.codigo == 0\n"
            f"    resumen contar(1)\n    umbral == {casos} segun contrato porque \"deben pasar los {casos} casos enumerados para este "
            f"requisito en tests/test_{x}.py; asociar junto a corrida_completa\"\n    requiere {x}_caso\n    ambito universal\n"
            f"    alcance \"{alcance}\"\n")


def catalogo_de_corrida(x: str, casos: int) -> str:
    return (f"medida factory_{x}.corrida_completa:\n    de {x}_corrida c\n    donde c.completa == 1 y c.casos == {casos}\n"
            f"    resumen contar(1)\n    umbral == 1 segun contrato porque \"el sensor exige los casos exactos sin omisiones, duplicados ni "
            f"fallas y fuentes estables\"\n    requiere {x}_corrida\n    ambito universal\n"
            f"    alcance \"integridad local declarada por el sensor; no autentica hechos ni reemplaza revision humana\"\n")


def escribir_catalogos(raiz: Path, cambio: str, modulo: str, alcance: str) -> list[str]:
    """Escribe los catálogos del cambio en `raiz/catalogos`; devuelve los nombres de los que cambiaron (los que ya estaban igual no se tocan)."""
    if any(c in '"\\' or ord(c) < 32 for c in alcance):  # el catálogo lo escribe entre comillas dobles, con la sintaxis de cadenas de JSON
        raise ContratoInvalido("el alcance no puede llevar comillas dobles, barras invertidas ni caracteres de control (tabulaciones, saltos de línea)")
    por_nombre, _ = leer_contrato(raiz, cambio, modulo)
    x = modulo.removeprefix("test_")
    destino = raiz / "catalogos"
    textos = {f"factory_{x}.corrida_completa.oracle": catalogo_de_corrida(x, sum(len(v) for v in por_nombre.values())),
              **{f"factory_{x}.{r}.oracle": catalogo_de_requisito(x, r, len(c), alcance) for r, c in por_nombre.items()}}
    cambiados = []
    for nombre, texto in textos.items():
        ruta = destino / nombre
        if ruta.is_file() and ruta.read_text(encoding="utf-8") == texto:
            continue
        destino.mkdir(exist_ok=True)
        ruta.write_text(texto, encoding="utf-8")
        cambiados.append(nombre)
    return cambiados


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cambio", help="id del cambio")
    parser.add_argument("--pruebas", required=True, help="módulo de pruebas del cambio, por ejemplo test_alarmas_flujo")
    parser.add_argument("--salida", type=Path, help="carpeta nueva de evidencia")
    parser.add_argument("--catalogos", action="store_true", help="escribir los catálogos Oracle del cambio en catalogos/")
    parser.add_argument("--alcance", default="escenarios del cambio con Git de verdad y repositorios temporales, Linux",
                        help="el texto de «alcance» de los catálogos")
    parser.add_argument("--raiz", type=Path, default=AQUI, help="raíz del proyecto (por omisión, este repositorio)")
    args = parser.parse_args(argv)
    if not args.salida and not args.catalogos:
        parser.error("indicá --salida, --catalogos o los dos")
    raiz = args.raiz.expanduser().resolve()
    try:
        if args.catalogos:
            cambiados = escribir_catalogos(raiz, args.cambio, args.pruebas, args.alcance)
            print(("Catálogos escritos: " + ", ".join(cambiados)) if cambiados else "Catálogos sin cambios.")
        if args.salida:
            salida = args.salida.expanduser().resolve()
            exito = producir(raiz, args.cambio, args.pruebas, salida)
            resumen = json.loads((salida / "resultado.json").read_text(encoding="utf-8"))
            print(f"Evidencia: {salida}; {resumen['tests']} pruebas, {resumen['casos_contrato']} casos de contrato; éxito: {exito}.")
            return 0 if exito else 1
    except ContratoInvalido as e:
        print(f"Contrato inválido: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
