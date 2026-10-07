"""Resumen del estado actual: una vista corta, derivada de los registros y determinista.

Puro: recibe los datos ya leídos y devuelve el texto Markdown; quien llama lee y escribe. Las mismas entradas dan los
mismos bytes (sin fecha ni commit), así que verificar es regenerar y comparar.
"""
from __future__ import annotations

import hashlib
import re

CABECERA = re.compile(r'^<!-- oracle-factory resumen sha256:([0-9a-f]{64}) -->\n')


def _tipo(cuerpo: list[str]) -> str:
    for linea in cuerpo:
        m = re.match(r'^\s*(?:-\s*)?Tipo:\s*(.+?)\s*$', linea, re.IGNORECASE)
        if m:
            return m[1].lower()
    return 'funcional'


def _veredicto(registro: dict | None) -> str:
    """El veredicto con el que se cerró el cambio; nunca uno inventado."""
    if not registro:
        return 'sin registro del cambio'
    oracle, cierre = registro.get('oracle') or {}, registro.get('cierre') or {}
    fecha = (cierre.get('cuando') or '')[:10] or 'sin fecha'
    if not oracle:
        return f'sin veredicto registrado (cierre {fecha})'
    return f"{'verde' if oracle.get('codigo') == 0 else 'rojo'} al cerrar el {fecha}"


def _celda(texto) -> str:
    return str(texto).replace('|', '\\|').replace('\n', ' ')


def generar(indices: list[dict], registros: dict[str, dict], medidas: dict[str, list[str]],
            abiertos: list[dict], revisiones: dict[str, dict]) -> str:
    """El resumen completo, con la línea de huella al principio.

    - `indices`: los de `.factory/specs/`, en orden de capacidad.
    - `registros`: id de cambio → registro (`factory.json`).
    - `medidas`: requisito de Oracle → medidas que lo miden (`medido_por`).
    - `abiertos`: [{id, titulo, fase, modo, capacidad, pendientes}] en orden de id.
    - `revisiones`: id de cambio cerrado → {'decisiones': [...], 'hallazgos': {id: {...}}, 'limites': [...]}.
    """
    vigentes = {r['cambio'] for i in indices for r in i['requisitos'].values()}
    total = sum(len(i['requisitos']) for i in indices)
    cuerpo = ['# Estado actual', '',
              'Generado por `oracle-factory resumen` a partir de los registros; no se edita a mano. '
              '`oracle-factory resumen --verificar` dice si quedó viejo.', '',
              f'{len(indices)} capacidades · {total} requisitos vigentes · {len(abiertos)} cambios abiertos', '',
              '## Lo vigente', '',
              'El veredicto es el registrado al cerrar el cambio de origen, no una corrida nueva de Oracle.']
    for indice in indices:
        cap = indice['capacidad']
        cuerpo += ['', f'### {cap}', '', f'Spec completa: [openspec/specs/{cap}/spec.md](../openspec/specs/{cap}/spec.md)', '',
                   '| Requisito | Tipo | Medidas | Veredicto | Cambio de origen |', '|---|---|---|---|---|']
        for nombre, req in indice['requisitos'].items():
            rid = req['requisito']
            cuerpo.append(f"| {_celda(nombre)} | {_tipo(req.get('cuerpo', []))} | "
                          f"{_celda(', '.join(medidas.get(rid, [])) or 'sin medir')} | {_veredicto(registros.get(req['cambio']))} | "
                          f"{req['cambio']} |")
    cuerpo += ['', '## Cambios abiertos', '']
    if not abiertos:
        cuerpo.append('Ninguno.')
    else:
        cuerpo.append('Lo que falta se calculó al generar este resumen; un commit posterior puede cambiarlo.')
    for a in abiertos:
        cuerpo += ['', f"### {a['id']} — {a['titulo']}", '',
                   f"Fase `{a['fase']}` · modo `{a['modo']}` · capacidad `{a['capacidad']}`", '']
        cuerpo += [f'- {_celda(p)}' for p in a['pendientes']] or ['- Nada: listo para cerrar.']
    for titulo, clave in (('Riesgos aceptados', 'decisiones'), ('Límites declarados', 'limites')):
        cuerpo += ['', f'## {titulo}']
        for grupo, es_vigente in (('De cambios con requisitos vigentes', True), ('Históricos', False)):
            filas = []
            for ident in sorted(revisiones):
                if (ident in vigentes) != es_vigente:
                    continue
                rev = revisiones[ident]
                if clave == 'decisiones':
                    for d in rev.get('decisiones', []):
                        if d.get('estado') == 'riesgo_aceptado':
                            h = rev.get('hallazgos', {}).get(d.get('hallazgo_id'), {})
                            filas.append(f"- **{d.get('hallazgo_id')}** ({ident}): {_celda(h.get('descripcion', 'sin descripción')).rstrip('.')}. "
                                         f"Aceptado por {d.get('actor', '?')}: {_celda(d.get('motivo', ''))}")
                else:
                    filas += [f'- ({ident}) {_celda(l)}' for l in rev.get('limites', [])]
            cuerpo += ['', f'### {grupo}', ''] + (filas or ['Ninguno.'])
    texto = '\n'.join(cuerpo) + '\n'
    return f'<!-- oracle-factory resumen sha256:{hashlib.sha256(texto.encode()).hexdigest()} -->\n' + texto


if __name__ == '__main__':
    idx = [{'capacidad': 'x', 'requisitos': {'uno': {'cambio': 'c1', 'requisito': 'x_c1.uno', 'cuerpo': ['Tipo: no funcional', 'A SHALL b.']}}}]
    reg = {'c1': {'oracle': {'codigo': 0}, 'cierre': {'cuando': '2026-10-01T00:00:00+00:00'}}}
    rev = {'c1': {'decisiones': [{'hallazgo_id': 'H1', 'estado': 'riesgo_aceptado', 'actor': 'P', 'motivo': 'm'}],
                  'hallazgos': {'H1': {'descripcion': 'd'}}, 'limites': ['l']},
           'c0': {'decisiones': [], 'hallazgos': {}, 'limites': ['viejo']}}
    t = generar(idx, reg, {'x_c1.uno': ['m.a']}, [], rev)
    assert t == generar(idx, reg, {'x_c1.uno': ['m.a']}, [], rev)
    assert 'no funcional' in t and 'verde al cerrar el 2026-10-01' in t and 'A SHALL b.' not in t
    assert t.index('**H1**') < t.index('### Históricos') and t.index('(c0) viejo') > t.rindex('### Históricos')
    print('ok')
