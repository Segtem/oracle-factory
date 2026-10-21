"""La corrida piloto con agentes reales: el mismo proyecto del banco, con Ana trabajando con claude-code y Beto con codex.

    python tools/piloto_real.py --salida CARPETA

Las personas siguen siendo del banco (deciden en su terminal, de forma determinista); lo que hacen los agentes lo hacen
LLM de verdad: implementar, dejar mensajes, retomar el trabajo de la otra persona y resolver un conflicto. Por eso no es
reproducible: las filas se registran con `banco.py --real` (banco-real.json/.txt), aparte del banco.

r1 — a la vez: cada agente implementa una función en calc.py y su prueba, en su rama, al mismo tiempo; las dos ramas
tocan los mismos archivos, así que la segunda choca al integrar y la resuelve el agente de quien integra.
r2 — de a turnos: el agente de Ana deja el trabajo a medias con un mensaje de relevo; al día siguiente Beto toma el
cambio y su agente lo termina leyendo sólo lo que dice Factory.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import banco  # noqa: E402

PLAZO = 900
FACTORY = f"{sys.executable} -c 'import sys; from oracle_factory.cli import main; sys.exit(main())'"


def agente(persona: banco.Persona, cual: str, pedido: str) -> subprocess.CompletedProcess:
    """El agente real de la persona, en su clon, sin salir de él."""
    marco = (f'Trabajás en el repositorio de {persona.dir} (un proyecto de prueba). Para Factory usá exactamente '
             f'`{FACTORY} --agente {cual} <comando>`; nunca tomes decisiones de una persona (aprobar-spec, revisar, '
             'cerrar, tomar sin --agente). No hagas push ni cambies la configuración de git. Al terminar, commiteá con git '
             'en la rama en la que estás. ')
    if cual == 'claude-code':
        argv = ['claude', '-p', marco + pedido, '--permission-mode', 'acceptEdits',
                '--allowedTools', 'Bash(git:*)', f'Bash({sys.executable}:*)', 'Bash(python3:*)', 'Read', 'Edit', 'Write']
    else:
        argv = ['codex', 'exec', '-s', 'workspace-write', '--skip-git-repo-check', '-C', str(persona.dir), marco + pedido]
    return subprocess.run(argv, cwd=persona.dir, env=persona.env, capture_output=True, text=True, timeout=PLAZO,
                          stdin=subprocess.DEVNULL)


def actores(persona: banco.Persona, ident: str) -> set:
    return {e.get('actor') for e in persona.registro(ident)['eventos'] if e.get('tipo_actor') == 'agente'}


def r1(e: banco.Escenario) -> None:
    trabajos = ((e.ana, 'claude-code', 'restar', 'restar(a, b) que devuelve a - b'),
                (e.beto, 'codex', 'multiplicar', 'multiplicar(a, b) que devuelve a * b'))
    # El vault del proyecto, en main de los dos: así lo generado también se cruza al integrar (como en s7).
    e.ana.agente_hace('kb')
    e.ana.commit('el vault del proyecto')
    e.ana.git('push', '-q', 'origin', 'main')
    e.beto.git('pull', '-q', '--no-rebase', 'origin', 'main')
    ids = {}
    for p, cual, sufijo, que in trabajos:
        p.git('checkout', '-q', '-b', f'tarea/{sufijo}')
        ids[sufijo] = p.nuevo_cambio(sufijo, f'Agregar {sufijo}')
        p.decide('tomar', ids[sufijo], '--con', cual)
        p.commit(f'{sufijo}: el cambio')
    with ThreadPoolExecutor(2) as pool:
        hechos = [pool.submit(agente, p, cual, f'Agregá a calc.py la función {que} y una prueba en test_calc.py (con assert, '
                              f'como la de sumar). Corré `python3 test_calc.py`. Dejá un mensaje en el cambio {ids[sufijo]} '
                              f'con `mensaje {ids[sufijo]} "<qué hiciste>"`. Commiteá todo.')
                  for p, cual, sufijo, que in trabajos]
        for f in hechos:
            r = f.result()
            e.nota(f'agente: código {r.returncode}; {(r.stdout or r.stderr).strip()[-200:]}')
    for p, cual, sufijo, _ in trabajos:
        if p.git('status', '--porcelain').stdout.strip():
            e.fila['rehecho'] += 1
            e.nota(f'{cual} dejó cambios sin commitear (el sandbox de codex deja .git en sólo lectura): la persona los commitea')
            p.commit(f'{sufijo}: lo que dejó el agente')
        if cual not in actores(p, ids[sufijo]) or 'mensaje' not in {x['accion'] for x in p.registro(ids[sufijo])['eventos']}:
            e.fila['decisiones_perdidas'] += 1
            e.nota(f'el mensaje de {cual} no quedó en {ids[sufijo]}')
        p.git('push', '-q', 'origin', f'tarea/{sufijo}')
    e.integrar(e.ana, 'tarea/restar')
    if not e.integrar(e.ana, 'tarea/multiplicar'):
        r = agente(e.ana, 'claude-code', 'Estás en main en medio de un merge con conflictos de la rama tarea/multiplicar. '
                   'Resolvé los conflictos conservando lo de las dos ramas, corré `python3 test_calc.py`, hacé `git add` '
                   'de lo resuelto y terminá el merge con `git commit --no-edit`.')
        e.nota(f'claude-code resolvió el conflicto: código {r.returncode}')
        if e.ana.git('rev-parse', '-q', '--verify', 'MERGE_HEAD', ok=False).returncode == 0:
            e.defecto('el agente no terminó el merge')
            return
        e.ana.git('push', '-q', 'origin', 'main')
    if not e.pruebas_pasan(e.ana):
        e.defecto('después de integrar las dos ramas, las pruebas no pasan')
    for ident, cual in ((ids['restar'], 'claude-code'), (ids['multiplicar'], 'codex')):
        if cual not in actores(e.ana, ident):
            e.fila['mal_atribuidas'] += 1
            e.nota(f'{ident} no muestra a {cual} entre sus agentes en main')
    for orden in (('resumen', '--verificar'), ('kb', '--verificar')):
        r = e.ana.agente_hace(*orden, ok=False)
        if r.returncode:
            e.defecto(f'{" ".join(orden)} falla en main después de integrar: {(r.stderr or r.stdout).strip()[-300:]}')


def r2(e: banco.Escenario) -> None:
    e.ana.git('checkout', '-q', '-b', 'tarea/potencia')
    ident = e.ana.nuevo_cambio('potencia', 'Agregar potencia y raiz')
    e.ana.decide('tomar', ident, '--con', 'claude-code')
    agente(e.ana, 'claude-code', 'Agregá a calc.py la función potencia(a, b) que devuelve a ** b, con su prueba en '
           'test_calc.py. NO hagas raiz: la deja para mañana otra persona. Dejá un mensaje de relevo en el cambio '
           f'{ident} con `mensaje {ident} "<qué quedó hecho y qué falta>"`. Commiteá todo.')
    if e.ana.git('status', '--porcelain').stdout.strip():
        e.fila['rehecho'] += 1
        e.ana.commit('potencia: lo que dejó el agente')
    e.ana.git('push', '-q', 'origin', 'tarea/potencia')
    relevo = [x for x in e.ana.registro(ident)['eventos'] if x['accion'] == 'mensaje']
    if not relevo:
        e.fila['decisiones_perdidas'] += 1
        e.defecto('claude-code no dejó el mensaje de relevo')
        return
    # Al día siguiente: Beto trae la rama, toma el cambio con --relevo y su agente lo termina.
    e.beto.git('fetch', '-q', 'origin', 'tarea/potencia')
    e.beto.git('checkout', '-q', '-b', 'tarea/potencia', 'origin/tarea/potencia')
    e.beto.decide('tomar', ident, '--relevo', '--con', 'codex')
    e.beto.commit('potencia: Beto toma el relevo')
    r = agente(e.beto, 'codex', f'Retomás el cambio {ident} que dejó otra persona. Leé qué falta con `estado {ident}` y '
               f'`log {ident}` y con los mensajes de su registro (.factory/cambios/{ident}/factory.json), terminá lo que falta en '
               f'calc.py y test_calc.py, corré `python3 test_calc.py`, dejá un mensaje con `mensaje {ident} "<qué hiciste>"` '
               'y commiteá todo.')
    e.nota(f'codex retomó: código {r.returncode}')
    if e.beto.git('status', '--porcelain').stdout.strip():
        e.fila['rehecho'] += 1
        e.beto.commit('potencia: lo que dejó el agente')
    texto = (e.beto.dir / 'calc.py').read_text()
    if 'def raiz' not in texto and 'def raíz' not in texto:
        e.defecto('codex no terminó lo que el relevo decía que faltaba (raiz)')
    if not e.pruebas_pasan(e.beto):
        e.defecto('las pruebas no pasan después del relevo')
    eventos = e.beto.registro(ident)['eventos']
    if not any(x['accion'] == 'mensaje' and x.get('actor') == 'codex' for x in eventos):
        e.fila['decisiones_perdidas'] += 1
        e.nota('codex no dejó su mensaje')
    if any(x['accion'] == 'mensaje' and x.get('actor') not in ('claude-code', 'codex') for x in eventos):
        e.fila['mal_atribuidas'] += 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--salida', type=Path, required=True)
    args = parser.parse_args(argv)
    args.salida.mkdir(parents=True, exist_ok=True)
    filas = []
    for nombre, funcion in (('r1_dos_agentes_reales_a_la_vez', r1), ('r2_relevo_entre_agentes_reales', r2)):
        with tempfile.TemporaryDirectory(prefix=f'piloto-{nombre}-') as d:
            inicio = time.monotonic()
            try:
                esc = banco.Escenario(nombre, Path(d), 0)
                funcion(esc)
                fila = esc.fila
            except Exception as error:  # noqa: BLE001 — se registra, como en el banco
                fila = {'escenario': nombre, 'resultado': 'error', 'conflicto': 'nunca', 'decisiones_perdidas': 0,
                        'mal_atribuidas': 0, 'evidencia_vieja_aceptada': 0, 'rehecho': 0,
                        'detalle': [f'{type(error).__name__}: {error}'[:600]]}
            fila['segundos'] = round(time.monotonic() - inicio, 1)
            filas.append(fila)
            print(f"{fila['resultado']:<8} {nombre} ({fila['segundos']} s)", flush=True)
    (args.salida / 'filas-real.json').write_text(json.dumps(filas, ensure_ascii=False, indent=2) + '\n')
    return banco.main(['--salida', str(args.salida), '--real', str(args.salida / 'filas-real.json'), '--semilla', '0'])


if __name__ == '__main__':
    raise SystemExit(main())
