"""Unir el registro de un cambio editado en dos ramas: lo usa el merge driver de Git que instala `oracle-factory hooks`.

Puro: recibe la versión común y las de las dos ramas, y devuelve la unión. Los eventos (y los riesgos aceptados) de las
dos ramas quedan todos, sin repetirse y en orden. Cada decisión del registro (responsable, aprobación, revisión, juicio,
cierre, fase; las medidas, una por requisito) se une entera: lo que cambió una sola rama se toma de esa rama, y lo que
las dos cambiaron distinto no se elige ni se mezcla: queda el valor de la rama que integra y el de la otra va a
`pendientes_de_union`, para que lo decida una persona.
"""
from __future__ import annotations

import heapq
import json

LISTAS_QUE_SE_SUMAN = ("eventos", "aceptados", "pendientes_de_union")
# Mapas cuyas entradas son decisiones aparte: las medidas de un requisito no se mezclan con las de otro.
POR_ENTRADA = ("medidas", "medidas_pendientes")
_FALTA = object()  # la clave no está (distinto de estar con None)
# Qué decisiones resuelven cada pendiente (por su campo) y cómo se le dice a la persona.
_APROBAR = "que una persona apruebe la spec otra vez con oracle-factory aprobar-spec {id}"
RESUELVE = {
    "responsable": (("tomado", "soltado"), "acuérdenlo y que una persona lo tome con oracle-factory tomar {id} --relevo (o lo suelte)"),
    "spec_aprobada": (("spec_aprobada",), _APROBAR),
    "spec_sha256": (("spec_aprobada",), _APROBAR),
    "medidas": (("medidas_confirmadas", "medidas_elegidas"), "que una persona vuelva a decidir las medidas con oracle-factory medir {id}"),
    "medidas_pendientes": (("medidas_propuestas", "medidas_confirmadas", "medidas_elegidas"), "volvé a proponer o decidir las medidas con oracle-factory medir {id}"),
    "revision": (("revision_registrada",), "que una persona registre la revisión otra vez con oracle-factory revisar {id}"),
    "oracle": (("oracle_ejecutado",), "juzgá otra vez con oracle-factory juzgar {id}"),
    # La próxima decisión que fija la fase la resuelve; dos cierres o dos abandonos, sólo una persona eligiendo.
    "fase": (("spec_aprobada", "requisitos_importados", "revision_registrada", "oracle_ejecutado"),
             "la próxima decisión del cambio fija la fase"),
}
DECIDIR = "elegí cuál vale con oracle-factory decidir-union {id} {campo} nuestro (o suyo)"


def _clave(x) -> str:
    return "\0falta" if x is _FALTA else json.dumps(x, sort_keys=True, ensure_ascii=False)


def _sumar(base, nuestro, suyo, en_orden: bool) -> list:
    """Lo de las dos ramas sin repetir, salvo lo que estaba en la base y una de las dos sacó (un pendiente ya resuelto
    no vuelve). Con en_orden (los eventos, que nunca se borran), se intercalan por `cuando` conservando el orden de cada rama."""
    claves = [{_clave(x) for x in lista or []} for lista in (nuestro, suyo)]
    # Los eventos son el historial: no se borran aunque una rama los haya perdido. Lo demás (un pendiente resuelto) sí.
    sacado = set() if en_orden else {_clave(x) for x in base or []} - (claves[0] & claves[1])
    # El historial común primero, en su orden (aunque una rama haya perdido alguno), y después lo nuevo de cada rama.
    propios, ajenos, vistos = [], [], set(sacado)
    for destino, lista in ((propios, base if en_orden else []), (propios, nuestro), (ajenos, suyo)):
        for x in lista or []:
            if _clave(x) not in vistos:
                vistos.add(_clave(x))
                destino.append(x)
    if not en_orden:
        return propios + ajenos
    return list(heapq.merge(propios, ajenos, key=lambda e: str(e.get("cuando", ""))))  # estable: ante empate, los nuestros


def _valor(base, nuestro, suyo, camino: list, pendientes: list):
    """Una decisión entera: la de la rama que la cambió, o la nuestra con la otra anotada si las dos la cambiaron."""
    if _clave(nuestro) == _clave(suyo) or _clave(suyo) == _clave(base):
        return nuestro
    if _clave(nuestro) == _clave(base):
        return suyo
    pendientes.append({"campo": ".".join(camino), "camino": camino,
                       "nuestro": None if nuestro is _FALTA else nuestro, "suyo": None if suyo is _FALTA else suyo})
    return nuestro


def _mapa(base: dict, nuestro: dict, suyo: dict, camino: list, pendientes: list, entrar) -> dict:
    salida = {}
    for k in dict.fromkeys([*nuestro, *suyo]):
        valor = entrar(k, base.get(k, _FALTA), nuestro.get(k, _FALTA), suyo.get(k, _FALTA), [*camino, k], pendientes)
        if valor is not _FALTA:  # la rama que la sacó, la sacó
            salida[k] = valor
    return salida


def _campo(k, base, nuestro, suyo, camino, pendientes):
    if k in LISTAS_QUE_SE_SUMAN:
        juntos = _sumar(*(x if isinstance(x, list) else [] for x in (base, nuestro, suyo)), en_orden=k == "eventos")
        return juntos if juntos else _FALTA  # una lista que quedó vacía no se escribe
    if k in POR_ENTRADA and all(isinstance(x, dict) or x is _FALTA for x in (base, nuestro, suyo)):
        return _mapa(*({} if x is _FALTA else x for x in (base, nuestro, suyo)), camino, pendientes,
                     lambda _k, b, n, s, c, p: _valor(b, n, s, c, p))
    return _valor(base, nuestro, suyo, camino, pendientes)


def unir(base: dict, nuestro: dict, suyo: dict) -> dict:
    """La unión de los tres registros (base puede ser {} si el cambio se creó en las dos ramas a la vez)."""
    pendientes: list = []
    salida = _mapa(base or {}, nuestro, suyo, [], pendientes, _campo)
    if pendientes:
        salida["pendientes_de_union"] = _sumar([], salida.get("pendientes_de_union"), pendientes, en_orden=False)
        salida.setdefault("eventos", []).append({"accion": "union_con_decisiones", "forma": "registro", "actor": "oracle-factory",
                                                 "tipo_actor": "agente",
                                                 "cuando": max((str(e.get("cuando", "")) for e in salida.get("eventos") or []), default=""),
                                                 "campos": [p["campo"] for p in pendientes]})
    return salida


def resueltos_por(accion: str, requisito: str | None = None) -> tuple[tuple, ...]:
    """Los caminos que una decisión resuelve: las medidas de un requisito resuelven sólo las de ese requisito."""
    return tuple((campo, requisito) if campo in POR_ENTRADA and requisito else (campo,)
                 for campo, (acciones, _) in RESUELVE.items() if accion in acciones)


def resuelto(pendiente: dict, caminos: tuple[tuple, ...]) -> bool:
    camino = tuple(pendiente.get("camino") or pendiente.get("campo", "").split("."))
    return any(camino[:len(c)] == c for c in caminos)


def como_resolver(campo: str, ident: str) -> str:
    raiz = campo.split(".")[0]
    decidir = DECIDIR.format(id=ident, campo=campo)
    return f"{RESUELVE[raiz][1].format(id=ident)}, o {decidir}" if raiz in RESUELVE else decidir
