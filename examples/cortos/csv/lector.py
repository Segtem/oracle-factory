"""Suma cantidades positivas de filas CSV codigo,cantidad sin encabezado."""

import csv
from io import StringIO


def sumar(texto):
    total = 0
    for fila in csv.reader(StringIO(texto)):
        if len(fila) != 2 or not fila[0].strip():
            raise ValueError("cada fila necesita código y cantidad")
        try:
            cantidad = int(fila[1])
        except ValueError as error:
            raise ValueError("la cantidad debe ser entera") from error
        if cantidad <= 0:
            raise ValueError("la cantidad debe ser positiva")
        total += cantidad
    return total
