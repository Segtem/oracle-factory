"""Comprueba la explicación de Clue y conserva evidencia de documentación y navegación.

Las comprobaciones textuales son acotadas: la revisión independiente debe juzgar la prosa.
"""
import argparse
import ast
from collections import Counter
import html
from importlib import metadata
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.verify_review_guided import Resultado, escribir, sha  # noqa: E402
from oracle_factory import trazabilidad  # noqa: E402

CAMBIO = '20261025-201245-erb-docs-clue'
CONTRACTS = {'la_portada_explica_el_papel_real_de_clue': ['Docs.test_dc1_alguien_llega_al_proyecto']}
PREFIX = 'test_docs.'
LIMITES = ('Comprobación de fragmentos concretos de la portada y la guía frente a las llamadas '
           'preparar/validar de la CLI, con cuatro alteraciones documentales en memoria. '
           'Suite existente y navegador en Linux. No analiza prosa arbitraria ni demuestra comprensión '
           'de una persona; la valoración del texto corresponde a la revisión independiente.')
CONTROLES = ('sin_negacion', 'contexto_y_validacion', 'analisis_externo', 'limite_ia',
             'decision_persona', 'guia_consistente', 'cli_consistente')


def legible(texto):
    return ' '.join(html.unescape(re.sub(r'<[^>]*>', ' ', texto)).split())


def comprobar(portada, guia, codigo):
    tarjeta = next((a for a in re.findall(r'<article\b.*?</article>', portada, re.S)
                    if 'data-sprite="clue"' in a), '')
    tarjeta = legible(tarjeta)
    texto = legible(portada)
    llamadas = set()
    for nodo in ast.walk(ast.parse(codigo)):
        if (isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Name)
                and nodo.func.id == 'ejecutar' and nodo.args and isinstance(nodo.args[0], ast.List)):
            valores = nodo.args[0].elts
            if (len(valores) >= 2 and all(isinstance(v, ast.Constant) for v in valores[:2])
                    and valores[0].value == 'oracle-clue'):
                llamadas.add(valores[1].value)
    return {
        'sin_negacion': 'Factory no invoca Clue' not in texto,
        'contexto_y_validacion': all(t in tarjeta for t in
                                    ('Factory usa Oracle Clue', 'preparar el contexto', 'validar informes externos'))
                                and all(t in texto for t in ('pedir-revision', 'valida su informe con Oracle Clue')),
        'analisis_externo': 'El análisis lo hace el revisor configurado' in tarjeta,
        'limite_ia': 'el alpha de Clue todavía no busca defectos con IA' in tarjeta,
        'decision_persona': all(t in tarjeta for t in
                               ('En el modo de confirmación', 'vos decidís', 'revisar')),
        'guia_consistente': all(t in guia for t in
                               ('su paquete de Oracle Clue', 'lanza al revisor', 'valida su informe con Clue')),
        'cli_consistente': {'preparar', 'validar'} <= llamadas,
    }


def observar():
    return ((ROOT / 'site/index.html').read_text(), (ROOT / 'docs/agentes.md').read_text(),
            (ROOT / 'oracle_factory/cli.py').read_text())


def alteraciones(portada, guia, codigo):
    cambios = (
        ('negacion_original', 'Factory usa Oracle Clue', 'Factory no invoca Clue'),
        ('sin_validacion', 'validar informes externos', 'guardar informes externos'),
        ('analisis_atribuido_a_clue', 'El análisis lo hace el revisor configurado', 'El análisis lo hace Oracle Clue'),
        ('limite_ia_invertido', 'el alpha de Clue todavía no busca defectos con IA',
         'el alpha de Clue ya busca defectos con IA'),
    )
    filas = []
    for nombre, antes, despues in cambios:
        if portada.count(antes) != 1:
            raise ValueError(f'{nombre}: no se encontró un único fragmento a alterar')
        controles = comprobar(portada.replace(antes, despues, 1), guia, codigo)
        filas.append({'id': nombre, 'detectada': not all(controles.values()), 'controles': controles})
    return filas


def fuentes():
    nombres = subprocess.run(['git', 'ls-files', '--cached', '--others', '--exclude-standard'],
                             cwd=ROOT, text=True, capture_output=True, check=True).stdout.splitlines()
    archivos = [n for n in nombres if not n.startswith(('.factory/', 'kb/', 'tareas/', 'openspec/'))
                and (ROOT / n).is_file()]
    head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                          text=True, capture_output=True, check=True).stdout.strip()
    return {'head': head, 'sha256': {n: sha(ROOT / n) for n in sorted(archivos)}}


def casos(suite):
    for caso in suite:
        if isinstance(caso, unittest.TestSuite):
            yield from casos(caso)
        else:
            yield caso.id()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--salida', type=Path, required=True)
    args = p.parse_args()
    output = args.salida.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=False)
    origen = fuentes()
    portada, guia, codigo = observar()
    controles = comprobar(portada, guia, codigo)
    mutaciones = alteraciones(portada, guia, codigo) if all(controles.values()) else []
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'))
    esperados = Counter(casos(suite))
    resultado = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=Resultado).run(suite)
    (output / 'suite.txt').write_text(stream.getvalue())
    completa = (bool(esperados) and resultado.cantidad == esperados
                and all(n == 1 for n in esperados.values())
                and all(resultado.observados.get(n, 1) == 0 for n in esperados)
                and not resultado.skipped and not resultado.expectedFailures
                and not resultado.unexpectedSuccesses and resultado.wasSuccessful())
    observacion = {'controles': controles, 'texto_tarjetas': [legible(a) for a in
                   re.findall(r'<article\b.*?</article>', portada, re.S) if 'data-sprite="clue"' in a],
                   'alteraciones': mutaciones, 'limites': LIMITES}
    escribir(output / 'observacion.json', observacion)
    estado = json.loads((ROOT / '.factory/cambios' / CAMBIO / 'factory.json').read_text())
    sufijo = next(iter(CONTRACTS))
    ids = estado.get('requisitos', [])
    contrato = [PREFIX + n for n in CONTRACTS[sufijo]]
    trazas = {r: contrato for r in ids if r.rsplit('.', 1)[-1] == sufijo}
    escribir(output / 'trazabilidad.json', trazabilidad.trazar(ROOT, trazas))
    estable = origen == fuentes()
    conforme = (set(controles) == set(CONTROLES) and all(controles.values())
                and len(mutaciones) == 4 and all(m['detectada'] for m in mutaciones))
    ok = (completa and estable and conforme and len(trazas) == 1 and len(ids) == 1
          and all(resultado.cantidad.get(n) == 1 and resultado.observados.get(n) == 0 for n in contrato))
    escribir(output / 'hechos.json', {
        'docs_clue_texto': [{'conforme': int(conforme), 'controles': len(controles),
                             'alteraciones_detectadas': sum(m['detectada'] for m in mutaciones)}],
        'docs_clue_corrida': [{'completa': int(ok), 'casos': len(contrato)}],
    })
    escribir(output / 'resultado.json', {
        'exitoso': bool(ok), 'tests': resultado.testsRun, 'tests_esperados': sum(esperados.values()),
        'suite_completa_sin_omisiones_duplicados_ni_fallas': completa,
        'fuentes_estables': estable, 'origen': origen, 'limites': LIMITES,
        'versiones': {n: metadata.version(n) for n in ('oracle-metalenguaje', 'oracle-task', 'oracle-clue')},
        'artefactos_sha256': {n: sha(output / n) for n in
                             ('suite.txt', 'observacion.json', 'trazabilidad.json', 'hechos.json')},
    })
    print(f'Evidencia: {output}; {resultado.testsRun} casos; éxito: {bool(ok)}')
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
