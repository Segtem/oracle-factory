"""Mutación automática de las líneas de un cambio: ¿las pruebas del cambio vigilan lo que el cambio tocó?

Las líneas del cambio son las de archivos `.py` fuera de `tests/` que `git blame` atribuye, en HEAD, a commits con el trailer
`Cambio: ID` (en el checkout limpio de `oracle-factory evidencia` no hay `main` contra el que comparar). Sobre ellas genera mutantes con
operadores sobre el AST, hasta un tope elegido de forma determinista, y contra cada uno corre sólo el módulo de pruebas del cambio en una
copia del commit (`git archive HEAD`): el producto no se toca. Un mutante «muere» si alguna prueba falla.

Límites: un mutante equivalente (que no cambia el comportamiento) cuenta como sobreviviente; una línea commiteada sin el trailer no se
muta; el texto mutado sale de `ast.unparse`, sin los comentarios del original."""
from __future__ import annotations

import ast
import copy
import io
import os
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import tempfile
import time

AQUI = Path(__file__).resolve().parents[1]
if str(AQUI) not in sys.path:
    sys.path.insert(0, str(AQUI))
from oracle_factory import procesos  # noqa: E402

TOPE = 40
COMPARACIONES = {ast.Eq: (ast.NotEq, "==", "!="), ast.NotEq: (ast.Eq, "!=", "=="), ast.Lt: (ast.GtE, "<", ">="),
                 ast.GtE: (ast.Lt, ">=", "<"), ast.Gt: (ast.LtE, ">", "<="), ast.LtE: (ast.Gt, "<=", ">"),
                 ast.In: (ast.NotIn, "in", "not in"), ast.NotIn: (ast.In, "not in", "in"), ast.Is: (ast.IsNot, "is", "is not"),
                 ast.IsNot: (ast.Is, "is not", "is")}


def _git(raiz: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(raiz), *args], capture_output=True, text=True, check=True).stdout


def lineas_del_cambio(raiz: Path, cambio: str) -> dict[str, set[int]]:
    """{archivo: líneas} de los `.py` fuera de `tests/` que `git blame` atribuye en HEAD a commits del cambio."""
    commits = set(_git(raiz, "log", "--format=%H", "--no-merges", "--grep", f"^Cambio: {re.escape(cambio)}$").split())
    archivos = sorted({n for c in commits for n in _git(raiz, "show", "--name-only", "--format=", c).split()
                       if n.endswith(".py") and not n.startswith("tests/") and (raiz / n).is_file()})
    salida = {}
    for archivo in archivos:
        lineas = {int(m[2]) for m in re.finditer(r"^([0-9a-f]{40}) \d+ (\d+)", _git(raiz, "blame", "--porcelain", "HEAD", "--", archivo), re.M)
                  if m[1] in commits}
        if lineas:
            salida[archivo] = lineas
    return salida


def _mutaciones(arbol: ast.AST, lineas: set[int]) -> list[tuple[int, int, str]]:
    """(posición del nodo en ast.walk, variante, descripción) de cada mutante posible en esas líneas."""
    salida = []
    for i, nodo in enumerate(ast.walk(arbol)):
        if getattr(nodo, "lineno", None) not in lineas:
            continue
        if isinstance(nodo, ast.Compare):
            salida += [(i, k, f"{COMPARACIONES[type(op)][1]} → {COMPARACIONES[type(op)][2]}")
                       for k, op in enumerate(nodo.ops) if type(op) in COMPARACIONES]
        elif isinstance(nodo, ast.BoolOp):
            salida.append((i, 0, "and → or" if isinstance(nodo.op, ast.And) else "or → and"))
        elif isinstance(nodo, ast.UnaryOp) and isinstance(nodo.op, ast.Not):
            salida.append((i, 0, "quitar not"))
        elif isinstance(nodo, ast.Constant) and isinstance(nodo.value, bool):
            salida.append((i, 0, f"{nodo.value} → {not nodo.value}"))
        elif isinstance(nodo, ast.Constant) and type(nodo.value) is int:
            salida.append((i, 0, f"{nodo.value} → {nodo.value + 1}"))
    return salida


def _aplicar(arbol: ast.AST, posicion: int, variante: int) -> str:
    """El texto del módulo con ese único mutante."""
    arbol = copy.deepcopy(arbol)
    nodos = list(ast.walk(arbol))
    nodo = nodos[posicion]
    if isinstance(nodo, ast.Compare):
        nodo.ops[variante] = COMPARACIONES[type(nodo.ops[variante])][0]()
    elif isinstance(nodo, ast.BoolOp):
        nodo.op = ast.Or() if isinstance(nodo.op, ast.And) else ast.And()
    elif isinstance(nodo, ast.Constant):
        nodo.value = (not nodo.value) if isinstance(nodo.value, bool) else nodo.value + 1
    elif isinstance(nodo, ast.UnaryOp):  # quitar el not: el padre apunta al operando
        for padre in nodos:
            for campo, valor in ast.iter_fields(padre):
                if valor is nodo:
                    setattr(padre, campo, nodo.operand)
                elif isinstance(valor, list):
                    valor[:] = [nodo.operand if v is nodo else v for v in valor]
    return ast.unparse(ast.fix_missing_locations(arbol)) + "\n"


def elegir(mutantes: list, tope: int) -> list:
    """Hasta `tope`, repartidos de forma determinista entre todos (no los primeros)."""
    return mutantes if len(mutantes) <= tope else [mutantes[i * len(mutantes) // tope] for i in range(tope)]


def _copia(raiz: Path, destino: Path) -> None:
    """El commit HEAD en `destino`, sin tocar `raiz`; con su `node_modules` enlazado si lo tiene (no se versiona)."""
    tar = subprocess.run(["git", "-C", str(raiz), "archive", "--format=tar", "HEAD"], capture_output=True, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(tar)) as t:
        t.extractall(destino, filter="data")
    if (raiz / "node_modules").is_dir():
        (destino / "node_modules").symlink_to((raiz / "node_modules").resolve())


def mutar(raiz: Path, cambio: str, modulo: str, tope: int = TOPE) -> dict:
    """{"mutantes": [{archivo, linea, operador, muerto}], "resumen": {generados, muertos, porcentaje, tope_alcanzado}}."""
    raiz = raiz.resolve()
    candidatos = []
    for archivo, lineas in sorted(lineas_del_cambio(raiz, cambio).items()):
        arbol = ast.parse((raiz / archivo).read_text(encoding="utf-8"))
        nodos = list(ast.walk(arbol))
        candidatos += [(archivo, nodos[p].lineno, p, v, d) for p, v, d in _mutaciones(arbol, lineas)]
    elegidos = elegir(candidatos, tope)
    resumen = {"generados": len(elegidos), "muertos": 0, "porcentaje": 100, "tope_alcanzado": int(len(candidatos) > tope)}
    if not elegidos:
        return {"mutantes": [], "resumen": resumen}
    with tempfile.TemporaryDirectory(prefix="oracle-factory-mutacion-") as tmp:
        copia = Path(tmp) / "producto"
        _copia(raiz, copia)
        entorno = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        orden = [sys.executable, "-B", "-m", "unittest", f"tests.{modulo}"]
        inicio = time.monotonic()
        base, _, _ = procesos.correr_en_grupo(orden, copia, 900, entorno)
        plazo = max(60.0, 5 * (time.monotonic() - inicio))
        filas = []
        for archivo, linea, posicion, variante, descripcion in elegidos:
            ruta = copia / archivo
            original = ruta.read_text(encoding="utf-8")
            muerto = 0
            if base == 0:  # si las pruebas ya fallan sin mutar, que fallen con el mutante no prueba nada
                try:
                    ruta.write_text(_aplicar(ast.parse(original), posicion, variante), encoding="utf-8")
                    codigo, _, _ = procesos.correr_en_grupo(orden, copia, plazo, entorno)
                    muerto = int(codigo != 0)
                finally:
                    ruta.write_text(original, encoding="utf-8")
            filas.append({"archivo": archivo, "linea": linea, "operador": descripcion, "muerto": muerto})
    muertos = sum(f["muerto"] for f in filas)
    resumen.update(muertos=muertos, porcentaje=muertos * 100 // len(filas))  # si la base falla, nadie corrió: muertos es 0
    return {"mutantes": filas, "resumen": resumen}
