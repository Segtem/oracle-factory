"""Unir el registro de un cambio editado en dos ramas: lo usa el merge driver de Git que instala `oracle-factory hooks`.

Puro: recibe la versión común y las de las dos ramas, y devuelve la unión. Los eventos (y los riesgos aceptados) de las
dos ramas quedan todos, sin repetirse y en orden. Cada decisión del registro (responsable, aprobación, revisión, juicio,
cierre, fase; las medidas, una por requisito) se une entera: lo que cambió una sola rama se toma de esa rama, y lo que
las dos cambiaron distinto no se elige ni se mezcla: queda el valor de la rama que integra y el de la otra va a
`pendientes_de_union`, para que lo decida una persona.
"""
from __future__ import annotations

import datetime as dt
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


def hora(evento: dict) -> tuple:
    """La clave para ordenar por la hora de un evento: con o sin microsegundos, con «Z» o con «+00:00». Una que no se
    entiende como fecha va primero, ordenada por su texto (como antes de este cambio)."""
    texto = str(evento.get("cuando") or "")
    try:
        h = dt.datetime.fromisoformat(texto.replace("Z", "+00:00"))
    except ValueError:
        return (dt.datetime.min.replace(tzinfo=dt.timezone.utc), texto)
    return (h if h.tzinfo else h.replace(tzinfo=dt.timezone.utc), texto)


def _clave(x) -> str:
    return "\0falta" if x is _FALTA else json.dumps(x, sort_keys=True, ensure_ascii=False)


def _sumar(base, nuestro, suyo, en_orden: bool) -> list:
    """Lo de las dos ramas sin repetir, salvo lo que estaba en la base y una de las dos sacó (un pendiente ya resuelto
    no vuelve). Con en_orden (los eventos, que nunca se borran), se intercalan por `cuando` conservando el orden de cada rama."""
    claves = [{_clave(x) for x in lista or []} for lista in (nuestro, suyo)]
    # Los eventos son el historial: no se borran aunque una rama los haya perdido. Lo demás (un pendiente resuelto) sí.
    sacado = set() if en_orden else {_clave(x) for x in base or []} - (claves[0] & claves[1])
    # El historial común primero, en su orden (aunque una rama haya perdido alguno), y después lo nuevo de cada rama.
    comun, propios, ajenos, vistos = [], [], [], set(sacado)
    for destino, lista in ((comun, base if en_orden else []), (propios, nuestro), (ajenos, suyo)):
        for x in lista or []:
            if _clave(x) not in vistos:
                vistos.add(_clave(x))
                destino.append(x)
    if not en_orden:
        return propios + ajenos
    # Lo común va antes que lo nuevo de cada rama, que lo vio (causalidad, como en un reloj lógico), aunque su hora empate.
    return comun + _intercalar(propios, ajenos)


def _desempate(e: dict) -> tuple:
    """Entre dos eventos de ramas distintas con la misma hora no hay un orden real que saber (dos máquinas en el mismo
    microsegundo): se elige uno determinista, el mismo en todos los clones y sin importar quién integra. Como en los
    relojes lógicos con id de nodo (Lamport, HLC, Automerge): la hora y, ante empate, quién y qué."""
    return (*hora(e), str(e.get("actor", "")), _clave(e))


def _intercalar(propios: list, ajenos: list) -> list:
    """Las dos listas por hora, cada una en su orden (el de su registro, que es el verdadero); ante la misma hora, el
    desempate determinista."""
    salida, i, j = [], 0, 0
    while i < len(propios) and j < len(ajenos):
        if _desempate(ajenos[j]) < _desempate(propios[i]):
            salida.append(ajenos[j])
            j += 1
        else:
            salida.append(propios[i])
            i += 1
    return salida + propios[i:] + ajenos[j:]


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
        # Su propia hora, con microsegundos: un microsegundo después del último evento. No la del reloj, para que la misma
        # unión hecha en dos clones dé el mismo evento (y al juntarlos después no se repita).
        ultimo = max((hora(e)[0] for e in salida.get("eventos") or []), default=dt.datetime.min.replace(tzinfo=dt.timezone.utc))
        cuando = ultimo + dt.timedelta(microseconds=1)
        salida.setdefault("eventos", []).append({"accion": "union_con_decisiones", "forma": "registro", "actor": "oracle-factory",
                                                 "tipo_actor": "agente", "cuando": cuando.isoformat(timespec="microseconds"),
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
