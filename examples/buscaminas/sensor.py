"""Observa seis reglas del Buscaminas y escribe hechos para Oracle."""

import argparse
import json
from pathlib import Path

from buscaminas import MINAS, Partida


def _numero():
    minas_esperadas = frozenset({(1, 1), (1, 5), (3, 3), (5, 1), (5, 5)})
    if MINAS != minas_esperadas:
        return False
    partida = Partida()
    for fila in range(1, 6):
        for columna in range(1, 6):
            if (fila, columna) in minas_esperadas:
                continue
            esperado = sum(abs(fila - f) <= 1 and abs(columna - c) <= 1
                           for f, c in minas_esperadas)
            if partida.numero(fila, columna) != esperado:
                return False
    return True


def _cero():
    regiones = {
        (1, 3): {(1, 2), (1, 3), (1, 4), (2, 2), (2, 3), (2, 4)},
        (3, 1): {(2, 1), (2, 2), (3, 1), (3, 2), (4, 1), (4, 2)},
        (3, 5): {(2, 4), (2, 5), (3, 4), (3, 5), (4, 4), (4, 5)},
        (5, 3): {(4, 2), (4, 3), (4, 4), (5, 2), (5, 3), (5, 4)},
    }
    for inicio, esperadas in regiones.items():
        partida = Partida()
        partida.destapar(*inicio)
        if partida.destapadas != esperadas or partida.estado != "jugando":
            return False
    return True


def _bandera():
    partida = Partida()
    partida.alternar_bandera(1, 1)
    try:
        partida.destapar(1, 1)
    except ValueError:
        bloqueada = (1, 1) in partida.banderas and (1, 1) not in partida.destapadas
    else:
        bloqueada = False
    partida.alternar_bandera(1, 1)
    return bloqueada and (1, 1) not in partida.banderas


def _mina():
    partida = Partida()
    partida.destapar(1, 1)
    return partida.estado == "perdida"


def _victoria():
    partida = Partida()
    for fila in range(1, 6):
        for columna in range(1, 6):
            if (fila, columna) not in MINAS and partida.estado == "jugando":
                partida.destapar(fila, columna)
    return partida.estado == "ganada"


def _invalidas():
    partida = Partida()
    try:
        partida.destapar(0, 1)
    except ValueError:
        intacta = partida.estado == "jugando" and not partida.destapadas
    else:
        intacta = False
    partida.destapar(1, 1)
    try:
        partida.alternar_bandera(2, 2)
    except ValueError:
        return intacta and partida.estado == "perdida" and not partida.banderas
    return False


def observar():
    pruebas = (("numero", _numero), ("cero", _cero), ("bandera", _bandera),
               ("mina", _mina), ("victoria", _victoria), ("invalidas", _invalidas))
    casos = []
    for nombre, prueba in pruebas:
        try:
            correcto = prueba()
        except Exception:
            correcto = False
        casos.append({"caso": nombre, "codigo": int(not correcto)})
    return {"casos": casos, "corrida": [{"completa": 1, "casos": len(casos)}]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, required=True)
    destino = parser.parse_args().salida
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(observar(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Hechos de Buscaminas escritos en {destino}")
