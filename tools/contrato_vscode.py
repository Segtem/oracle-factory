"""El contrato entre la CLI y la extensión de VS Code: qué claves de los JSON de la CLI lee la extensión, y con qué tipos.

`editores/vscode/contrato.json` es {comando: [{ruta, tipos, opcional?}]}. Una ruta son claves separadas por punto, «[]» por cada nivel de
arreglo y «.*» para un objeto que la extensión recorre (nombres variables). Los tipos: string, number, boolean, null, array, object.
Dos comprobaciones: lo que la extensión LEE tiene que estar declarado, y lo que está declarado tiene que ENTREGARLO la CLI. Una clave de más
en la salida de la CLI no es un problema."""
from __future__ import annotations

import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CONTRATO = RAIZ / "editores/vscode/contrato.json"
TIPOS = ("string", "number", "boolean", "null", "array", "object")


def tipo_de(valor) -> str:
    if valor is None:
        return "null"
    if isinstance(valor, bool):
        return "boolean"
    if isinstance(valor, (int, float)):
        return "number"
    return "string" if isinstance(valor, str) else "array" if isinstance(valor, list) else "object"


def cargar(ruta: Path = CONTRATO) -> dict[str, list[dict]]:
    return json.loads(ruta.read_text(encoding="utf-8"))


def _pasos(ruta: str) -> list[str]:
    """«a[].b.*» → ['a', '[]', 'b', '*']."""
    pasos = []
    for parte in ruta.split("."):
        niveles = 0
        while parte.endswith("[]"):
            parte, niveles = parte[:-2], niveles + 1
        if parte:
            pasos.append(parte)
        pasos.extend(["[]"] * niveles)
    return pasos


def _bajar(valores: list, paso: str) -> list:
    """Lo que hay un paso más abajo de cada valor: los elementos de un arreglo, los valores de un objeto o el de una clave."""
    salida = []
    for valor in valores:
        if paso == "[]":
            if isinstance(valor, list):
                salida.extend(valor)
        elif paso == "*":
            if isinstance(valor, dict):
                salida.extend(valor.values())
        elif isinstance(valor, dict) and paso in valor:
            salida.append(valor[paso])
    return salida


def muestras(dato, ruta: str) -> tuple[list, int]:
    """([valores hallados en la ruta], cuántos objetos había donde la clave podía estar). Un objeto sin la clave suma al segundo y no al primero.
    Para una ruta que termina en «[]» o «.*» el segundo es 0: un arreglo vacío es legítimo, y no se puede saber cuántos elementos se esperaban."""
    *previos, ultimo = _pasos(ruta)
    actuales = [dato]
    for paso in previos:
        actuales = _bajar(actuales, paso)
    if ultimo in ("[]", "*"):
        return _bajar(actuales, ultimo), 0
    padres = [v for v in actuales if isinstance(v, dict)]
    return [p[ultimo] for p in padres if ultimo in p], len(padres)


def comprobar_la_cli(contrato: dict, salidas: dict[str, list]) -> list[str]:
    """Problemas de lo declarado frente a lo que la CLI entregó. `salidas`: {comando: [JSON de cada estado]}."""
    problemas = []
    for comando, entradas in contrato.items():
        for entrada in entradas:
            ruta, tipos, opcional = entrada["ruta"], entrada["tipos"], entrada.get("opcional", False)
            hallados, padres = 0, 0
            for dato in salidas.get(comando, []):
                valores, p = muestras(dato, ruta)
                padres += p
                hallados += len(valores)
                for valor in valores:
                    if tipo_de(valor) not in tipos:
                        problemas.append(f"{comando}: «{ruta}» esperaba {'|'.join(tipos)} y la CLI dio {tipo_de(valor)}")
                        break
            if not opcional and padres and hallados < padres:
                problemas.append(f"{comando}: la CLI no da «{ruta}» (declarada, no opcional): faltó en {padres - hallados} de {padres} lugares")
            elif not opcional and not padres and not hallados:
                problemas.append(f"{comando}: «{ruta}» no se pudo comprobar con los estados de la prueba (sin muestra): marcala opcional o sumá un estado")
    return sorted(set(problemas))


def comprobar_la_extension(contrato: dict, leidas: dict[str, list[str]]) -> list[str]:
    """Las claves que la extensión leyó y el contrato no declara."""
    declaradas = {c: {e["ruta"] for e in entradas} for c, entradas in contrato.items()}
    return sorted(f"{comando}: la extensión lee «{ruta}» y el contrato no la declara"
                  for comando, rutas in leidas.items() for ruta in rutas if ruta not in declaradas.get(comando, set()))
