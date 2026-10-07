"""Resumen del estado actual: una vista corta, derivada de los registros y determinista.

Puro: recibe los datos ya leídos y devuelve el texto Markdown; quien llama lee y escribe. Las mismas entradas dan los
mismos bytes (sin fecha ni commit), así que verificar es regenerar y comparar.
"""
from __future__ import annotations

import hashlib
import re

PENDIENTE_DE_MEDIDA = re.compile(r'^medidas de (\S+)[ :]+(.+)$')


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
    if not isinstance(oracle, dict) or 'codigo' not in oracle:
        return f'sin veredicto registrado (cierre {fecha})'
    return f"{'verde' if oracle.get('codigo') == 0 else 'rojo'} al cerrar el {fecha}"


def _celda(texto) -> str:
    """Texto seguro dentro de una celda de tabla Markdown: ni `|` ni `\\` lo cortan."""
    return str(texto).replace('\\', '\\\\').replace('|', '\\|').replace('\n', ' ')


def _agrupar(pendientes: list[str]) -> list[str]:
    """Junta las líneas de medidas que dicen lo mismo de varios requisitos («7 requisitos: …»)."""
    grupos: dict[str, int] = {}
    resto = []
    for p in pendientes:
        m = PENDIENTE_DE_MEDIDA.match(p)
        if m:
            grupos[m[2]] = grupos.get(m[2], 0) + 1
        else:
            resto.append(p)
    return resto + [f'medidas de {n} requisito{"s" if n > 1 else ""}: {texto}' for texto, n in grupos.items()]


def generar(indices: list[dict], registros: dict[str, dict], medidas: dict[str, list[str]],
            abiertos: list[dict], revisiones: dict[str, dict], sin_registro: list[str] = (), raiz_relativa: str = '../') -> str:
    """El resumen completo, con la línea de huella al principio.

    - `indices`: los de `.factory/specs/`, en orden de capacidad.
    - `registros`: id de cambio → registro (`factory.json`).
    - `medidas`: requisito de Oracle → medidas que lo miden (`medido_por`).
    - `abiertos`: [{id, titulo, fase, modo, capacidad, pendientes}] en orden de id.
    - `revisiones`: id de cambio cerrado → {'decisiones', 'hallazgos', 'limites', 'problemas'}.
    - `sin_registro`: carpetas de `openspec/changes/` que no tienen registro de Factory.
    - `raiz_relativa`: cómo se llega a la raíz del proyecto desde donde se escribe el resumen (para los enlaces).
    """
    vigentes = {r['cambio'] for i in indices for r in i['requisitos'].values()}
    total = sum(len(i['requisitos']) for i in indices)
    cuerpo = ['# Estado actual', '',
              'Generado por `oracle-factory resumen` a partir de los registros; no se edita a mano. '
              '`oracle-factory resumen --verificar` dice si quedó viejo.', '',
              f'{len(indices)} capacidades · {total} requisitos vigentes · {len(abiertos)} cambios abiertos', '',
              '## Lo vigente', '',
              'El veredicto es el registrado al cerrar el cambio de origen, no una corrida nueva de Oracle sobre todo el sistema.']
    for indice in indices:
        cap = indice['capacidad']
        cuerpo += ['', f'### {cap}', '', f'Spec completa: [openspec/specs/{cap}/spec.md]({raiz_relativa}openspec/specs/{cap}/spec.md)', '',
                   '| Requisito | Tipo | Requisito de Oracle | Medidas | Veredicto al cerrar | Cambio de origen |',
                   '|---|---|---|---|---|---|']
        for nombre, req in indice['requisitos'].items():
            rid = req['requisito']
            cuerpo.append(f"| {_celda(nombre)} | {_tipo(req.get('cuerpo', []))} | `{_celda(rid)}` | "
                          f"{_celda(', '.join(medidas.get(rid, [])) or 'sin medir')} | {_veredicto(registros.get(req['cambio']))} | "
                          f"{_celda(req['cambio'])} |")
    cuerpo += ['', '## Cambios abiertos', '']
    cuerpo.append('Lo que falta se calculó al generar este resumen; un commit posterior puede cambiarlo.' if abiertos else 'Ninguno.')
    for a in abiertos:
        cuerpo += ['', f"### {a['id']} — {a['titulo']}", '',
                   f"Fase `{a['fase']}` · modo `{a['modo']}` · capacidad `{a['capacidad']}` · "
                   f"[propuesta]({raiz_relativa}openspec/changes/{a['id']}/proposal.md)", '']
        cuerpo += [f'- {_celda(p)}' for p in _agrupar(a['pendientes'])] or ['- Nada: listo para cerrar.']
    if sin_registro:
        cuerpo += ['', 'Carpetas de `openspec/changes/` sin registro de Factory (anteriores al flujo): '
                   + ', '.join(f'`{c}`' for c in sin_registro) + '.']
    for titulo, clave in (('Riesgos aceptados', 'decisiones'), ('Límites declarados', 'limites')):
        cuerpo += ['', f'## {titulo}']
        secciones = []
        for grupo, es_vigente in (('De cambios con requisitos vigentes', True), ('Históricos', False)):
            filas = []
            for ident in sorted(revisiones):
                if (ident in vigentes) != es_vigente:
                    continue
                rev = revisiones[ident]
                filas += [f'- ⚠ ({ident}) {_celda(p)}' for p in rev.get('problemas', [])]  # nunca se omite en silencio
                if clave == 'decisiones':
                    for d in rev.get('decisiones', []):
                        if d.get('estado') == 'riesgo_aceptado':
                            h = rev.get('hallazgos', {}).get(d.get('hallazgo_id'), {})
                            filas.append(f"- **{_celda(d.get('hallazgo_id'))}** ({ident}): "
                                         f"{_celda(h.get('descripcion', 'sin descripción')).rstrip('.')}. "
                                         f"Aceptado por {_celda(d.get('actor', '?'))}: {_celda(d.get('motivo', ''))}")
                else:
                    filas += [f'- ({ident}) {_celda(l)}' for l in rev.get('limites', [])]
            if filas:
                secciones += ['', f'### {grupo}', ''] + filas
        cuerpo += secciones or ['', 'Ninguno.']
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
    assert 'no funcional' in t and 'verde al cerrar el 2026-10-01' in t and 'A SHALL b.' not in t and '`x_c1.uno`' in t
    assert t.index('**H1**') < t.index('### Históricos') and t.index('(c0) viejo') > t.rindex('### Históricos')
    assert _celda('a\\|b') == 'a\\\\\\|b'
    assert _agrupar(['medidas de a: x', 'medidas de b: x', 'otra']) == ['otra', 'medidas de 2 requisitos: x']
    print('ok')
