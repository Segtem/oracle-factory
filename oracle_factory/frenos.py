"""Los frenos de construcción: las condiciones en las que quien construye (un agente solo, sobre todo) tiene que parar y devolverle la decisión
a una persona. Se calculan en cada consulta con datos que ya registra Factory; no se guardan ni bloquean nada: `estado` los muestra.

Un dato que no se puede leer no produce un freno: un falso freno detiene un trabajo sano, y los avisos de `alarmas` ya cubren lo ilegible."""
from __future__ import annotations


def _entero(x) -> bool:
    return isinstance(x, int) and not isinstance(x, bool)


def _dos_juicios_rojos(estado) -> bool:
    eventos = estado.get("eventos") if isinstance(estado, dict) else None
    if not isinstance(eventos, list):
        return False
    juicios = [e for e in eventos if isinstance(e, dict) and e.get("accion") == "oracle_ejecutado"][-2:]
    return len(juicios) == 2 and all(_entero(j.get("codigo")) and j["codigo"] != 0 for j in juicios)


def _hallazgo_alto(informes, candidato) -> bool:
    if not isinstance(candidato, str) or not candidato or not isinstance(informes, list):
        return False
    corto = candidato[:7].lower()
    return any(isinstance(i, dict) and isinstance(i.get("candidato"), str) and i["candidato"][:7].lower() == corto
               and isinstance(i.get("hallazgos"), list) and any(isinstance(h, dict) and h.get("severity") == "alta" for h in i["hallazgos"])
               for i in informes)


def _avisa(flujo, clave) -> bool:
    dato = flujo.get(clave) if isinstance(flujo, dict) else None
    return isinstance(dato, dict) and dato.get("avisa") is True


def calcular(estado: dict, informes: list[dict], candidato: str | None, revision_aprobada: bool, editados: list[dict] | None,
             flujo: dict) -> list[dict]:
    """[{id, motivo}] en un orden fijo; vacío si no hay ninguno.

    `informes` son los de `tablero.informes` (con `candidato` y `hallazgos`); `revision_aprobada` es una revisión aprobada y vigente
    (que ya vio el hallazgo y las pruebas editadas); `editados` y `flujo`, lo que ya calcula `alarmas` para `estado`."""
    salida = []
    if _dos_juicios_rojos(estado):
        salida.append(("juicios_rojos", "los dos últimos juicios de Oracle fueron rojos: no sigas probando, buscá la causa o pedí ayuda"))
    if not revision_aprobada and _hallazgo_alto(informes, candidato):
        salida.append(("hallazgo_alto_abierto", "un informe del candidato vigente trae un hallazgo de severidad alta y no hay una revisión aprobada vigente"))
    if editados and not revision_aprobada:  # una revisión aprobada y vigente ya vio las pruebas editadas (la registra una persona, salvo en los modos que dejan decidir al agente)
        salida.append(("prueba_existente_editada", "el candidato editó o borró tests que ya existían: decilo en la revisión (docs/tests.md)"))
    if _avisa(flujo, "cambio_grande"):
        salida.append(("cambio_grande", f"el candidato agrega {flujo['cambio_grande'].get('lineas')} líneas de producto: considerá partir el cambio"))
    if _avisa(flujo, "bucle_de_revision"):
        salida.append(("bucle_de_revision", f"{flujo['bucle_de_revision'].get('rondas')} rondas de revisión: arreglá la clase del problema entera antes de pedir otra"))
    return [{"id": i, "motivo": m} for i, m in salida]
