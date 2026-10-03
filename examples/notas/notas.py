"""Ejemplo mínimo: decidir si una nota se puede guardar."""

def puede_guardar(titulo: str) -> bool:
    """Un título válido contiene al menos un carácter que no sea espacio."""
    return bool(titulo.strip())
