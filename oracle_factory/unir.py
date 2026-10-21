"""Unir el registro de un cambio editado en dos ramas: lo usa el merge driver de Git que instala `oracle-factory hooks`.

Puro: recibe la versión común y las de las dos ramas, y devuelve la unión. Los eventos (y los riesgos aceptados) de las
dos ramas quedan todos, sin repetirse y en orden. Lo que cambió una sola rama se toma de esa rama. Lo que las dos ramas
cambiaron distinto no se elige: queda el valor de la rama que integra y el de la otra va a `pendientes_de_union`, para que
lo decida una persona.
"""
from __future__ import annotations

import json

LISTAS_QUE_SE_SUMAN = ("eventos", "aceptados", "pendientes_de_union")
# Qué decisión resuelve cada pendiente (por el primer tramo de su campo) y cómo se le dice a la persona.
RESUELVE = {
    "responsable": (("tomado", "soltado"), "acuérdenlo y que una persona lo tome con oracle-factory tomar {id} --relevo (o lo suelte)"),
    "spec_aprobada": (("spec_aprobada",), "que una persona apruebe la spec otra vez con oracle-factory aprobar-spec {id}"),
    "medidas": (("medidas_confirmadas", "medidas_elegidas"), "que una persona vuelva a decidir las medidas con oracle-factory medir {id}"),
    "medidas_pendientes": (("medidas_propuestas", "medidas_confirmadas", "medidas_elegidas"), "volvé a proponer o decidir las medidas con oracle-factory medir {id}"),
    "revision": (("revision_registrada",), "que una persona registre la revisión otra vez con oracle-factory revisar {id}"),
    "oracle": (("oracle_ejecutado",), "juzgá otra vez con oracle-factory juzgar {id}"),
    "cierre": (("cierre",), "decidan si el cambio está cerrado; cerralo otra vez con oracle-factory cerrar {id}"),
}
# Campos que se derivan de las decisiones: se toma el de la rama que integra, sin pedir nada.
DERIVADOS = ("fase",)


def _clave(x) -> str:
    return json.dumps(x, sort_keys=True, ensure_ascii=False)


def _sumar(*listas) -> list:
    vistos, salida = set(), []
    for lista in listas:
        for x in lista or []:
            if _clave(x) not in vistos:
                vistos.add(_clave(x))
                salida.append(x)
    return salida


def _unir(base, nuestro, suyo, camino: str, pendientes: list):
    if nuestro == suyo:
        return nuestro
    if nuestro == base:
        return suyo
    if suyo == base:
        return nuestro
    if isinstance(nuestro, dict) and isinstance(suyo, dict):
        base = base if isinstance(base, dict) else {}
        salida = {}
        for k in list(dict.fromkeys([*nuestro, *suyo])):
            sub = f"{camino}.{k}" if camino else k
            if k in LISTAS_QUE_SE_SUMAN and not camino:
                juntos = _sumar(base.get(k), nuestro.get(k), suyo.get(k))
                salida[k] = sorted(juntos, key=lambda e: (str(e.get("cuando", "")), _clave(e))) if k == "eventos" else juntos
                continue
            valor = _unir(base.get(k), nuestro.get(k), suyo.get(k), sub, pendientes)
            if valor is not None or k in nuestro:
                salida[k] = valor
        return salida
    if camino.split(".")[0] in DERIVADOS:
        return nuestro
    pendientes.append({"campo": camino, "nuestro": nuestro, "suyo": suyo})
    return nuestro


def unir(base: dict, nuestro: dict, suyo: dict) -> dict:
    """La unión de los tres registros (base puede ser {} si el cambio se creó en las dos ramas a la vez)."""
    pendientes: list = []
    salida = _unir(base or {}, nuestro, suyo, "", pendientes)
    if pendientes:
        salida["pendientes_de_union"] = _sumar(salida.get("pendientes_de_union"), pendientes)
        salida.setdefault("eventos", []).append({"accion": "union_con_decisiones", "forma": "registro", "actor": "oracle-factory",
                                                 "tipo_actor": "agente",
                                                 "cuando": max((str(e.get("cuando", "")) for e in salida.get("eventos") or []), default=""),
                                                 "campos": [p["campo"] for p in pendientes]})
    return salida


def resueltos_por(accion: str) -> tuple[str, ...]:
    """Los primeros tramos de campo que una decisión resuelve."""
    return tuple(campo for campo, (acciones, _) in RESUELVE.items() if accion in acciones)


def como_resolver(campo: str, ident: str) -> str:
    raiz = campo.split(".")[0]
    return RESUELVE.get(raiz, ((), "decidan cuál vale y registrenlo con la decisión que corresponde"))[1].format(id=ident)
