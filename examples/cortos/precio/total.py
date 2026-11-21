"""Precio en centavos con descuento entero de 0 a 50 por ciento."""


def calcular(centavos, descuento):
    if type(centavos) is not int or type(descuento) is not int:
        raise ValueError("centavos y descuento deben ser enteros")
    if centavos < 0 or not 0 <= descuento <= 50:
        raise ValueError("importe negativo o descuento fuera de 0..50")
    return centavos - centavos * descuento // 100
