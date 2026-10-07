"""Preparar la revisión guiada desde lo que produjeron los revisores sobre un candidato.

Puro: recibe el informe y las decisiones vacíos de `revision.plantillas`, los informes de los revisores ya leídos (formato
de Oracle Clue) y la evidencia del candidato, y devuelve el informe completado y un borrador de decisiones sin decidir.
Lo que es de la persona (revisor, si la revisión está completa y el estado de cada hallazgo) queda vacío.
"""
from __future__ import annotations

ESQUEMA_CLUE = 'oracle-clue.review/v1'


def _ubicacion(hallazgo: dict) -> str:
    loc = hallazgo.get('location') if isinstance(hallazgo.get('location'), dict) else {}
    archivo, linea = loc.get('file') or '?', loc.get('start_line')
    return f'{archivo}:{linea}' if linea is not None else archivo


def _proveedor(informe: dict) -> str:
    p = informe.get('provider') if isinstance(informe.get('provider'), dict) else {}
    nombre, modelo = p.get('name') or 'revisor sin nombre', p.get('model')
    return f'{nombre} ({modelo})' if modelo else nombre


def completar(informe: dict, decisiones: dict, revisores: list[dict], evidencia: dict | None,
              archivos: list[str]) -> tuple[dict, dict]:
    """`revisores`: [{'ruta', 'datos', 'validacion'}] ya filtrados (los inválidos o de otro candidato no llegan acá).

    `evidencia`: {'ruta', 'resultado'} con el `resultado.json` del verificador, o None. `archivos`: los del paquete de Clue.
    """
    hallazgos, comprobaciones, limites, vistos = [], [], [], set()
    for rev in revisores:
        datos, origen = rev['datos'], f"{_proveedor(rev['datos'])}, {rev['ruta']}, {rev['validacion']}"
        for h in datos.get('findings') or []:
            if not isinstance(h, dict):
                continue
            hid = str(h.get('id') or f'H{len(hallazgos) + 1:02d}')
            if hid in vistos:  # dos revisores con el mismo id: se distingue, no se pisa
                hid = f'{hid}-{len(hallazgos) + 1}'
            vistos.add(hid)
            explicacion = (h.get('explanation') or '').strip()
            hallazgos.append({'id': hid, 'descripcion': str(h.get('title') or explicacion or 'sin título'),
                              'ubicacion': _ubicacion(h),
                              'evidencia': f"{origen}; severidad {h.get('severity', '?')}. {h.get('evidence') or explicacion}".strip()})
        n = len(datos.get('findings') or [])
        comprobaciones.append({'descripcion': f"Revisión de {_proveedor(datos)}: {n} hallazgo{'s' if n != 1 else ''}"
                                              f" ({datos.get('review_status', 'estado sin declarar')})",
                               'resultado': 'cumple' if datos.get('review_status') == 'completo' else 'no_ejecutada',
                               'evidencia': f"{rev['ruta']} ({rev['validacion']})"})
        limites += [f'{_proveedor(datos)}: {l}' for l in datos.get('limitations') or [] if isinstance(l, str)]
    if evidencia:
        r = evidencia['resultado']
        comprobaciones.insert(0, {'descripcion': f"Evidencia del candidato: {r.get('tests', '?')} pruebas, "
                                                 f"{r.get('casos_contrato', '?')} casos de contrato",
                                  'resultado': 'cumple' if r.get('exitoso') is True else 'falla',
                                  'evidencia': evidencia['ruta']})
        if isinstance(r.get('limites'), str):
            limites.insert(0, f"Evidencia: {r['limites']}")
    informe = {**informe, 'archivos_revisados': archivos or None, 'comprobaciones': comprobaciones or None,
               'limites': limites, 'hallazgos': hallazgos,
               'sin_hallazgos_motivo': None if hallazgos else (
                   'Los revisores no reportaron hallazgos.' if revisores else None)}
    borrador = [{'hallazgo_id': h['id'], 'estado': None, 'motivo': None, 'actor': None, 'fecha': None} for h in hallazgos]
    return informe, {**decisiones, 'decisiones': borrador}


def vueltas_anteriores(vueltas: list[dict]) -> list[dict]:
    """Una comprobación por vuelta anterior: [{'candidato', 'ruta', 'datos', 'validacion'}] → comprobaciones, sin hallazgos que decidir."""
    comprobaciones = []
    for v in vueltas:
        nota = '' if v.get('validacion', 'validado').startswith('validado') else f" ({v['validacion']})"
        hallazgos = [h for h in v['datos'].get('findings') or [] if isinstance(h, dict)]
        ids = ', '.join(f"{h.get('id')} ({h.get('severity', '?')})" for h in hallazgos) or 'sin hallazgos'
        comprobaciones.append({'descripcion': f"Vuelta anterior en el candidato {v['candidato']}: {_proveedor(v['datos'])}, "
                                              f"{len(hallazgos)} hallazgo{'s' if len(hallazgos) != 1 else ''}: {ids}"
                                              f"{nota}",
                               'resultado': 'falla' if hallazgos else 'cumple', 'evidencia': v['ruta']})
    return comprobaciones


if __name__ == '__main__':
    base = {'revisor': None, 'completa': None, 'archivos_revisados': None, 'comprobaciones': None, 'limites': None,
            'hallazgos': None, 'sin_hallazgos_motivo': None}
    rev = {'ruta': 'r.json', 'validacion': 'validado', 'datos': {'provider': {'name': 'codex', 'model': 'm'}, 'review_status': 'completo',
           'findings': [{'id': 'A', 'title': 't', 'location': {'file': 'x.py', 'start_line': 3}, 'severity': 'baja', 'evidence': 'e'}],
           'limitations': ['l']}}
    i, d = completar(base, {'decisiones': None}, [rev, rev], {'ruta': 'ev/resultado.json', 'resultado': {'exitoso': True, 'tests': 9}}, ['x.py'])
    assert [h['id'] for h in i['hallazgos']] == ['A', 'A-2'] and i['hallazgos'][0]['ubicacion'] == 'x.py:3'
    assert i['revisor'] is None and i['completa'] is None and all(x['estado'] is None for x in d['decisiones'])
    assert i['comprobaciones'][0]['resultado'] == 'cumple' and 'codex (m): l' in i['limites']
    print('ok')
