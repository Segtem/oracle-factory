"""Evidencia del banco de concurrencia, para medir los tres requisitos del banco (a la vez, de a turnos, el informe): los 13
escenarios dos veces en el orden de la misma semilla (tienen que dar lo mismo, traza incluida) y una vez en procesos
simultáneos de verdad; y la corrida con agentes reales que quedó registrada en la tarea del cambio.

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
CAMBIO = '20261004-121432-coordinar-dos'
REAL = ROOT / 'tareas' / CAMBIO / 'piloto-real' / 'banco-real.json'
NUMEROS = ('conflicto', 'decisiones_perdidas', 'mal_atribuidas', 'evidencia_vieja_aceptada', 'rehecho')
CAMPOS = ('escenario', 'resultado', *NUMEROS, 'detalle', 'segundos')
LIMITES = ('Agentes de prueba deterministas, no LLM; Linux, git real, repositorios temporales. La corrida con agentes reales '
           '(tools/piloto_real.py) se mide sólo por su formato y por estar aparte; la usabilidad humana sigue pendiente.')


def grupo(nombre: str) -> str:
    """s0 (un clon recién hecho) es previo: no es uno de los escenarios a la vez de la spec."""
    return 'previo' if nombre.startswith('s0') else 'a_la_vez' if nombre.startswith('s') else 'de_a_turnos'


def limpio(fila: dict) -> bool:
    """Sin defectos ni decisiones perdidas o mal atribuidas, sin evidencia vieja vigente y con el conflicto (si lo hubo)
    detectado a más tardar al integrar."""
    return (fila['resultado'] == 'ok' and fila['conflicto'] in ('ninguno', 'antes', 'al_integrar')
            and fila['decisiones_perdidas'] == fila['mal_atribuidas'] == fila['evidencia_vieja_aceptada'] == 0)


def fuentes() -> dict:
    files = [ROOT / 'pyproject.toml', Path(__file__), ROOT / 'tools/banco.py', ROOT / 'tools/terminal.py', REAL,
             *ROOT.glob('oracle_factory/*.py'), *ROOT.glob('catalogos/factory_banco.*.oracle')]
    head = subprocess.run(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True, capture_output=True, check=True).stdout.strip()
    return {'head': head, 'sha256': {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(files))}}


def informe_completo(datos: dict) -> bool:
    return (datos.get('esquema') == 'oracle-factory.banco/1' and isinstance(datos.get('semilla'), int)
            and datos.get('modo') in ('ordenado', 'simultaneo', 'real')
            and {'oracle-factory', 'oracle-metalenguaje', 'oracle-task', 'oracle-clue', 'python', 'git'} <= set(datos.get('versiones') or {})
            and all(set(CAMPOS) <= set(f) for f in datos['escenarios']))


def texto_concuerda(datos: dict, texto: str) -> bool:
    """El informe de texto dice, por escenario, lo mismo que el JSON: resultado, conflicto y los cuatro números."""
    lineas = texto.splitlines()
    return all(any(linea.split()[:2] == [f['resultado'], f['escenario']] and f"conflicto: {f['conflicto']}" in linea
                   and f"perdidas {f['decisiones_perdidas']} · mal atribuidas {f['mal_atribuidas']} · evidencia vieja "
                       f"{f['evidencia_vieja_aceptada']} · rehecho {f['rehecho']} " in linea for linea in lineas)
               for f in datos['escenarios']) and str(datos['semilla']) in lineas[0]


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
    banco.main(['--salida', str(salida / 'simultanea'), '--semilla', str(SEMILLA), '--simultaneo'])
    simultanea = json.loads((salida / 'simultanea/banco-simultaneo.json').read_text(encoding='utf-8'))
    # La corrida con agentes reales registrada en la tarea: aparte, no reproducible y con el mismo formato; y registrarla
    # otra vez con --real no toca el informe del banco.
    real = json.loads(REAL.read_text(encoding='utf-8')) if REAL.is_file() else {'escenarios': []}
    escribir(salida / 'filas-real.json', real['escenarios'])
    banco.main(['--salida', str(salida / 'primera'), '--real', str(salida / 'filas-real.json'), '--semilla', '0'])
    real_otra = (salida / 'primera/banco-real.txt').read_text(encoding='utf-8')
    real_aparte = (bool(real['escenarios']) and real.get('reproducible') is False and real.get('modo') == 'real'
                   and informe_completo(real) and all(f['escenario'].startswith('r') for f in real['escenarios'])
                   and 'no reproducible' in real_otra and texto_concuerda(real, real_otra)
                   and json.loads((salida / 'primera/banco.json').read_text(encoding='utf-8')) == corridas[0])
    por_nombre = [{f['escenario']: f for f in c['escenarios']} for c in (*corridas, simultanea)]
    filas = []
    for nombre in banco.ESCENARIOS:
        uno, dos, tres = (c.get(nombre) for c in por_nombre)
        igual = bool(uno and dos) and all(uno[k] == dos[k] for k in ('resultado', *NUMEROS, 'traza'))
        filas.append({'escenario': nombre, 'grupo': grupo(nombre),
                      'limpio': int(bool(uno and tres) and limpio(uno) and limpio(tres)), 'reproducible': int(igual)})
    completa = (all(list(p) == list(banco.ESCENARIOS) for p in por_nombre) and fuentes() == origen
                and all(c['semilla'] == SEMILLA and c['reproducible'] is True and c['modo'] == 'ordenado' for c in corridas)
                and simultanea['modo'] == 'simultaneo' and simultanea['reproducible'] is False)
    corrida = {'completa': int(completa), 'escenarios': len(filas),
               'informe': int(all(informe_completo(c) for c in (*corridas, simultanea)) and all(
                   texto_concuerda(c, (salida / d / n).read_text(encoding='utf-8'))
                   for c, d, n in ((corridas[0], 'primera', 'banco.txt'), (corridas[1], 'segunda', 'banco.txt'),
                                   (simultanea, 'simultanea', 'banco-simultaneo.txt')))),
               'real_aparte': int(real_aparte)}
    escribir(salida / 'hechos.json', {'banco_escenario': filas, 'banco_corrida': [corrida]})
    ok = completa and corrida['informe'] == corrida['real_aparte'] == 1 and all(f['limpio'] and f['reproducible'] for f in filas)
    escribir(salida / 'resultado.json', {'exitoso': ok, 'semilla': SEMILLA, 'origen': origen, 'fuentes_estables': fuentes() == origen,
             'limites': LIMITES, 'filas': filas, 'corrida': corrida,
             'artefactos_sha256': {str(p.relative_to(salida)): sha(p) for p in sorted(salida.rglob('*')) if p.is_file()}})
    print(f'Evidencia: {salida}; {len(filas)} escenarios, dos corridas ordenadas con la semilla {SEMILLA} y una simultánea; éxito: {ok}.')
    print(LIMITES)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
