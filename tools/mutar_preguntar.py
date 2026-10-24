"""Mutaciones controladas de preguntar. Restauración en finally; no correr mientras se genera evidencia."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MUTACIONES = [
    ('fase_cerrada', 'oracle_factory/consultas.py', "fase == 'cerrada'", "fase == 'abandonada'", 'pq3'),
    ('conteo_cero', 'oracle_factory/consultas.py', "'cantidad': len(filas)", "'cantidad': 0", 'pq3'),
    ('cita_ajena', 'oracle_factory/generacion.py', " or extracto not in fuente['texto']", '', 'pq2'),
    ('numero_inventado', 'oracle_factory/generacion.py', "if set(re.findall(r'\\b\\d+(?:[.,]\\d+)?\\b', a['texto'])) - numeros:", 'if False:', 'pq2'),
    ('llamadas_sin_cota', 'oracle_factory/generacion.py', " or len(calls) > conf['max_llamadas'] - llamadas", '', 'pq2'),
    ('modelo_implicito', 'oracle_factory/generacion.py', "if conf is None:\n        return None", "if conf is None:\n        return {}", 'pq2'),
    ('respaldo_siempre', 'oracle_factory/rag.py', "'tipo': 'documentos' if respaldo else 'sin_respaldo'", "'tipo': 'documentos'", 'pq4'),
    ('esquema_viejo', 'oracle_factory/rag.py', 'oracle-factory.preguntar/2', 'oracle-factory.preguntar/1', 'pq5'),
    ('evaluacion_acepta_error', 'oracle_factory/rag.py', "and datos['valor'] == p['valor']", 'and True', 'pq6'),
    ('compuesta_como_filtro', 'oracle_factory/consultas.py', "if re.search(r'\\by (?:como|por que|que implica|que significa)\\b', p):", 'if False:', 'pq1'),
    ('url_sin_error_claro', 'oracle_factory/generacion.py', "raise cli.FactoryError('rag.generacion.url no es una URL HTTP(S) válida.') from exc", 'raise', 'pq2'),
    ('caso_sin_validar', 'oracle_factory/rag.py', "or (grupo == 'registro' and (type(p.get('valor')) is not int or p['valor'] < 0))", '', 'pq6'),
]
CASOS = {
    'pq1': 'test_pq1_respuesta_abierta_con_fuentes_y_herramientas',
    'pq2': 'test_pq2_herramientas_configuracion_fallos_y_limites',
    'pq3': 'test_pq3_cuenta_lista_cero_y_actualiza_registro',
    'pq4': 'test_pq4_sin_respaldo_ambiguedad_y_filtros',
    'pq5': 'test_pq5_cli_mcp_y_editor_conservan_respuesta',
    'pq6': 'test_pq6_evaluacion_por_grupos_detecta_errores',
}


def fuentes():
    archivos = [*(ROOT / 'oracle_factory').glob('*.py'), ROOT / 'tests/test_preguntar.py', Path(__file__)]
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(archivos)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida', type=Path, required=True)
    args = parser.parse_args()
    origen, filas = fuentes(), []
    for ident, rel, antes, despues, caso in MUTACIONES:
        archivo = ROOT / rel
        original = archivo.read_bytes()
        texto = original.decode()
        if texto.count(antes) != 1:
            raise RuntimeError(f'{ident}: se esperaba una ocurrencia exacta, hay {texto.count(antes)}')
        try:
            archivo.write_text(texto.replace(antes, despues, 1))
            # -B y caché fuera del árbol evitan reutilizar bytecode de una mutación anterior.
            corrida = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'tests.test_preguntar.Preguntar.' + CASOS[caso]],
                                     cwd=ROOT, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=120,
                                     env={**__import__('os').environ, 'PYTHONPYCACHEPREFIX': '/tmp/factory-mutaciones-sin-cache'})
            detectada = (corrida.returncode == 1 and 'FAILED (' in corrida.stderr and 'Ran 1 test' in corrida.stderr
                         and not any(s in corrida.stderr for s in ('SyntaxError', 'ImportError', 'ModuleNotFoundError', 'Failed to import test module')))
            filas.append({'id': ident, 'archivo': rel, 'caso': CASOS[caso], 'detectada': detectada,
                          'codigo': corrida.returncode, 'salida': corrida.stderr[-2500:]})
            print(ident, 'DETECTADA' if detectada else 'NO DETECTADA')
        finally:
            archivo.write_bytes(original)
        if fuentes() != origen:
            raise RuntimeError('Las fuentes no quedaron restauradas.')
    datos = {'fuentes': origen, 'mutaciones': filas, 'completas': len(filas) == len(MUTACIONES),
             'todas_detectadas': all(f['detectada'] for f in filas)}
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    with args.salida.open('x', encoding='utf-8') as out:
        json.dump(datos, out, ensure_ascii=False, indent=2)
    return 0 if datos['todas_detectadas'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
