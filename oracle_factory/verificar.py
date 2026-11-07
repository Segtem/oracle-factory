"""`verificar`: de sólo lectura, dice si los cambios del proyecto están consistentes (lo que un CI o un hook pre-push necesitan).

No decide ni corrige nada: junta lo que `estado` ya sabe comprobar y lo que invalida un registro (una huella que no coincide, una
revisión o un juicio de otro producto, un cierre que no es de una persona). Lo que falta por hacer no es una inconsistencia."""
from __future__ import annotations

import json

ESQUEMA = "oracle-factory.verificar/1"
HECHOS_AUSENTES = "hechos ausentes"


def del_cambio(cli, ident: str) -> tuple[list[str], list[str]]:
    """(problemas, avisos) de un cambio."""
    try:
        carpeta, estado = cli.leer(ident)
    except (cli.FactoryError, OSError, ValueError) as e:
        return [f"registro ilegible: {e}"], []
    if estado.get("fase") == "abandonada":
        return [], []
    cerrado, cierre = estado.get("fase") == "cerrada", estado.get("cierre") or {}
    previstos = set(cli.pendientes(estado)) | {f"medidas de {rid}: {motivo}" for rid, motivo in cli.medidas_sin_decision(estado)}
    try:
        cli.exigir_spec(carpeta, estado)
    except cli.FactoryError as e:
        if not estado.get("spec_aprobada"):
            previstos.add(str(e))  # aún sin aprobar: falta hacerlo, no es una inconsistencia
    problemas, avisos = [], []
    try:
        pendientes = cli.pendientes_actuales(carpeta, estado)
    except (cli.FactoryError, OSError, ValueError) as e:
        return [f"no pude comprobarlo: {e}"], []
    for p in pendientes:
        if p in previstos or (cerrado and p.endswith(cli.DESACTUALIZADO)):  # integrar un cambio deja distinto el producto, por diseño
            continue
        (avisos if p.startswith(HECHOS_AUSENTES) else problemas).append(p)
    if cerrado and cierre.get("tipo_actor") == "agente" and (cierre.get("modo") or cli.modo_de(estado)) != "autonomo":
        problemas.append(f"su cierre no lo decidió una persona (lo registró el agente {cierre.get('actor')})")
    return problemas, avisos


def datos(cli) -> dict:
    ids = [c.name for c in sorted(cli.CHANGES.iterdir()) if cli.ID_RE.fullmatch(c.name) and cli.ruta_registro(c).is_file()] if cli.CHANGES.is_dir() else []
    problemas, avisos = [], []
    original = cli.contexto_producto
    try:
        actual = original()
        cli.contexto_producto = lambda: actual  # el producto es el mismo para todos: se hashea una vez, no una por cambio
    except (cli.FactoryError, OSError):
        pass  # sin Git o sin commits: sólo falla, con su motivo, el cambio que necesita compararse con el producto
    try:
        for ident in ids:
            malos, leves = del_cambio(cli, ident)
            problemas += [{"cambio": ident, "problema": p} for p in malos]
            avisos += [{"cambio": ident, "aviso": a} for a in leves]
    finally:
        cli.contexto_producto = original
    return {"esquema": ESQUEMA, "ok": not problemas, "cambios": len(ids), "problemas": problemas, "avisos": avisos}


def comando(cli, como_json: bool) -> int:
    d = datos(cli)
    if como_json:
        print(json.dumps(d, ensure_ascii=False, indent=1))
    else:
        n = d["cambios"]
        print(f"Miré {n} cambio{'s' if n != 1 else ''}: " + ("todo consistente." if d["ok"] else f"{len({p['cambio'] for p in d['problemas']})} con problemas."))
        for p in d["problemas"]:
            print(f"  ✗ {p['cambio']}: {p['problema']}")
        for a in d["avisos"]:
            print(f"  ! {a['cambio']}: {a['aviso']}")
    return 0 if d["ok"] else 1
