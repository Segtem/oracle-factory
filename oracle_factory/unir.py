"""Unir el registro de un cambio editado en dos ramas: lo usa el merge driver de Git que instala `oracle-factory hooks`.

Puro: recibe la versión común y las de las dos ramas, y devuelve la unión. Los eventos (y los riesgos aceptados) de las
dos ramas quedan todos, sin repetirse y en orden. Lo que cambió una sola rama se toma de esa rama. Lo que las dos ramas
cambiaron distinto no se elige (tampoco la fase): queda el valor de la rama que integra y el de la otra va a
`pendientes_de_union`, para que lo decida una persona.
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
}
# Lo que ninguna otra decisión resuelve (dos fases, dos cierres) lo elige una persona entre las dos versiones.
DECIDIR = "elegí cuál vale con oracle-factory decidir-union {id} {campo} nuestro (o suyo)"


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


def _sumar3(base, nuestro, suyo) -> list:
    """Lo de las dos ramas, salvo lo que estaba en la base y una de las dos sacó (un pendiente ya resuelto no vuelve)."""
    en = [{_clave(x) for x in lista or []} for lista in (nuestro, suyo)]
    sacado = {_clave(x) for x in base or []} - (en[0] & en[1])
    return [x for x in _sumar(nuestro, suyo) if _clave(x) not in sacado]


def _unir(base, nuestro, suyo, camino: tuple, pendientes: list):
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
            if k in LISTAS_QUE_SE_SUMAN and not camino:
                juntos = _sumar3(base.get(k), nuestro.get(k), suyo.get(k))
                if juntos:  # una lista que quedó vacía no se escribe
                    salida[k] = sorted(juntos, key=lambda e: (str(e.get("cuando", "")), _clave(e))) if k == "eventos" else juntos
                continue
            valor = _unir(base.get(k), nuestro.get(k), suyo.get(k), (*camino, k), pendientes)
            if valor is not None or k in nuestro:
                salida[k] = valor
        return salida
    pendientes.append({"campo": ".".join(camino), "camino": list(camino), "nuestro": nuestro, "suyo": suyo})
    return nuestro


def unir(base: dict, nuestro: dict, suyo: dict) -> dict:
    """La unión de los tres registros (base puede ser {} si el cambio se creó en las dos ramas a la vez)."""
    pendientes: list = []
    salida = _unir(base or {}, nuestro, suyo, (), pendientes)
    if pendientes:
        salida["pendientes_de_union"] = _sumar(salida.get("pendientes_de_union"), pendientes)
        salida.setdefault("eventos", []).append({"accion": "union_con_decisiones", "forma": "registro", "actor": "oracle-factory",
                                                 "tipo_actor": "agente",
                                                 "cuando": max((str(e.get("cuando", "")) for e in salida.get("eventos") or []), default=""),
                                                 "campos": [p["campo"] for p in pendientes]})
    return salida


def resueltos_por(accion: str, requisito: str | None = None) -> tuple[tuple, ...]:
    """Los caminos que una decisión resuelve: las medidas de un requisito resuelven sólo las de ese requisito."""
    return tuple((campo, requisito) if campo.startswith("medidas") and requisito else (campo,)
                 for campo, (acciones, _) in RESUELVE.items() if accion in acciones)


def resuelto(pendiente: dict, caminos: tuple[tuple, ...]) -> bool:
    camino = tuple(pendiente.get("camino") or pendiente.get("campo", "").split("."))
    return any(camino[:len(c)] == c for c in caminos)


def como_resolver(campo: str, ident: str) -> str:
    raiz = campo.split(".")[0]
    decidir = DECIDIR.format(id=ident, campo=campo)
    return f"{RESUELVE[raiz][1].format(id=ident)}, o {decidir}" if raiz in RESUELVE else decidir
