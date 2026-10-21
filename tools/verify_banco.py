"""Evidencia del banco de concurrencia: corre los 13 escenarios dos veces con la misma semilla y registra una corrida real
de prueba, para medir los tres requisitos del banco (a la vez, de a turnos, el informe).

    python tools/verify_banco.py --salida CARPETA_NUEVA
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import banco  # noqa: E402
from tools.verify_review_guided import escribir, sha  # noqa: E402

SEMILLA = 20261021
NUMEROS = ('conflicto', 'decisiones_perdidas', 'mal_atribuidas', 'evidencia_vieja_aceptada', 'rehecho')
CAMPOS = ('escenario', 'resultado', *NUMEROS, 'detalle', 'segundos')
LIMITES = ('Agentes de prueba deterministas, no LLM; Linux, git real, repositorios temporales. Una corrida con agentes '
           'reales se registra aparte (banco-real) y no se mide acá; la usabilidad humana sigue pendiente.')


def grupo(nombre: str) -> str:
    return 'a_la_vez' if nombre.startswith('s') else 'de_a_turnos'


def limpio(fila: dict) -> bool:
    """Sin defectos ni decisiones perdidas o mal atribuidas, sin evidencia vieja vigente y con el conflicto (si lo hubo)
    detectado a más tardar al integrar."""
    return (fila['resultado'] == 'ok' and fila['conflicto'] in ('ninguno', 'antes', 'al_integrar')
            and fila['decisiones_perdidas'] == fila['mal_atribuidas'] == fila['evidencia_vieja_aceptada'] == 0)


def fuentes() -> dict:
    files = [ROOT / 'pyproject.toml', Path(__file__), ROOT / 'tools/banco.py', ROOT / 'tools/terminal.py',
             *ROOT.glob('oracle_factory/*.py'), *ROOT.glob('catalogos/factory_banco.*.oracle')]
    head = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True, capture_output=True, check=True).stdout.strip()
    return {'head': head, 'sha256': {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(files))}}


def informe_completo(datos: dict) -> bool:
    return (datos.get('esquema') == 'oracle-factory.banco/1' and isinstance(datos.get('semilla'), int)
            and {'oracle-factory', 'oracle-metalenguaje', 'python', 'git'} <= set(datos.get('versiones') or {})
            and all(set(CAMPOS) <= set(f) for f in datos['escenarios']))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--salida', type=Path, required=True, help='carpeta nueva de evidencia')
    args = parser.parse_args(argv)
    salida = args.salida.expanduser().resolve()
    salida.mkdir(parents=True, exist_ok=False)
    origen = fuentes()
    corridas = []
    for vuelta in ('primera', 'segunda'):
        destino = salida / vuelta
        banco.main(['--salida', str(destino), '--semilla', str(SEMILLA)])
        corridas.append(json.loads((destino / 'banco.json').read_text(encoding='utf-8')))
    # Una corrida real de muestra (las filas de la primera, con un agente distinto): tiene que quedar aparte y marcada.
    muestra = salida / 'real-muestra.json'
    muestra.write_text(json.dumps(corridas[0]['escenarios'][:1], ensure_ascii=False) + '\n', encoding='utf-8')
    banco.main(['--salida', str(salida / 'primera'), '--real', str(muestra)])
    real = json.loads((salida / 'primera/banco-real.json').read_text(encoding='utf-8'))
    real_texto = (salida / 'primera/banco-real.txt').read_text(encoding='utf-8')
    real_aparte = (real['reproducible'] is False and 'no reproducible' in real_texto and informe_completo(real)
                   and json.loads((salida / 'primera/banco.json').read_text(encoding='utf-8')) == corridas[0])
    por_nombre = [{f['escenario']: f for f in c['escenarios']} for c in corridas]
    filas = []
    for nombre in banco.ESCENARIOS:
        uno, dos = (c.get(nombre) for c in por_nombre)
        igual = bool(uno and dos) and all(uno[k] == dos[k] for k in ('resultado', *NUMEROS))
        filas.append({'escenario': nombre, 'grupo': grupo(nombre), 'limpio': int(bool(uno) and limpio(uno)),
                      'reproducible': int(igual)})
    completa = (all(list(p) == list(banco.ESCENARIOS) for p in por_nombre) and fuentes() == origen
                and all(c['semilla'] == SEMILLA and c['reproducible'] is True for c in corridas))
    corrida = {'completa': int(completa), 'escenarios': len(filas),
               'informe': int(all(informe_completo(c) for c in corridas)), 'real_aparte': int(real_aparte)}
    escribir(salida / 'hechos.json', {'banco_escenario': filas, 'banco_corrida': [corrida]})
    ok = completa and corrida['informe'] == corrida['real_aparte'] == 1 and all(f['limpio'] and f['reproducible'] for f in filas)
    escribir(salida / 'resultado.json', {'exitoso': ok, 'semilla': SEMILLA, 'origen': origen, 'fuentes_estables': fuentes() == origen,
             'limites': LIMITES, 'filas': filas, 'corrida': corrida,
             'artefactos_sha256': {str(p.relative_to(salida)): sha(p) for p in sorted(salida.rglob('*')) if p.is_file()}})
    print(f'Evidencia: {salida}; {len(filas)} escenarios, dos corridas con la semilla {SEMILLA}; éxito: {ok}.')
    print(LIMITES)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
