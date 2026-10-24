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
    ('conteo_cero', 'oracle_factory/consultas.py', "'cantidad': len(elegidos)", "'cantidad': 0", 'pq3'),
    ('cita_ajena', 'oracle_factory/generacion.py', " or extracto not in fuente['texto']", '', 'pq2'),
    ('numero_inventado', 'oracle_factory/generacion.py', "if _numeros_afirmacion(a['texto'], referencias) - numeros:", 'if False:', 'pq2'),
    ('llamadas_sin_cota', 'oracle_factory/generacion.py', "if isinstance(calls, list) and disponibles and (len(calls) > conf['max_llamadas'] - llamadas or not cabe_lote):", 'if False:', 'pq2'),
    ('modelo_implicito', 'oracle_factory/generacion.py', 'if conf is None:\n        return None', 'if conf is None:\n        return {}', 'pq2'),
    ('respaldo_siempre', 'oracle_factory/rag.py', "'tipo': 'documentos' if respaldo else 'sin_respaldo'", "'tipo': 'documentos'", 'pq4'),
    ('esquema_viejo', 'oracle_factory/rag.py', 'oracle-factory.preguntar/2', 'oracle-factory.preguntar/1', 'pq5'),
    ('evaluacion_acepta_error', 'oracle_factory/rag.py', "and datos['valor'] == p['valor']", 'and True', 'pq6'),
    ('compuesta_como_filtro', 'oracle_factory/consultas.py', "if ' y ' in p:\n        return None", "if ' y ' in p:\n        p = p.split(' y ', 1)[0]", 'pq1'),
    ('url_sin_error_claro', 'oracle_factory/generacion.py', "raise cli.FactoryError('rag.generacion.url no es una URL HTTP(S) válida.') from exc", 'raise', 'pq2'),
    ('caso_sin_validar', 'oracle_factory/rag.py', "or (grupo == 'registro' and (type(p.get('valor')) is not int or p['valor'] < 0))", '', 'pq6'),
    ('detalle_sin_vigencia', 'oracle_factory/consultas.py', 'actual = cli.datos_estado(i)', "actual = {**cli.datos_estado(i), 'revision': {'vigente': True}}", 'pq1'),
    ('pagina_sin_cota', 'oracle_factory/consultas.py', "pagina = elegidos[desplazamiento:desplazamiento + limite] if op == 'listar' else elegidos if op == 'detalle' else []", "pagina = elegidos if op in ('listar', 'detalle') else []", 'pq1'),
    ('formato_sin_recuperacion', 'oracle_factory/generacion.py', 'mensaje_final = enviar(conf, finales, [], restante)', "raise ValueError('Mutación: sin corrección de formato')", 'pq2'),
    ('servidor_exige_clave', 'oracle_factory/generacion.py', "if conf.get('clave_env') and not clave:", 'if not clave:', 'pq2'),
    ('temperatura_azar', 'oracle_factory/generacion.py', "cuerpo['temperature'] = 0", "cuerpo['temperature'] = 1", 'pq2'),
    ('identificador_como_cantidad', 'oracle_factory/generacion.py', 'for patron in patrones:', 'for patron in ():', 'pq2'),
    ('sin_inventario_cero', 'oracle_factory/consultas.py', "'texto': '\\n'.join(lineas), 'archivos': archivos,", "'texto': '\\n'.join(lineas), 'archivos': [],", 'pq3'),
    ('variante_rechazada', 'oracle_factory/consultas.py', 'factory estan existe existen quedan actualmente', 'factory existe quedan actualmente', 'pq3'),
    ('sin_limites_json', 'oracle_factory/rag.py', "'limites': generacion.limites(),", "'limites': {},", 'pq5'),
    ('documental_ignora_abstencion', 'oracle_factory/rag.py', "'acierto': int(puesto > 0 and datos['tipo'] == 'documentos')", "'acierto': int(puesto > 0)", 'pq6'),
    ('mixta_sin_calculo', 'oracle_factory/rag.py', "acierto = acierto and _calculo_respaldado(datos, p.get('filtro_registro', 'todos'))", 'acierto = acierto', 'pq6'),
    ('listado_sin_ids', 'oracle_factory/rag.py', "if p.get('requiere_listado'):", 'if False:', 'pq6'),
    ('saltos_rompen_citas', 'oracle_factory/generacion.py', "fuente['texto'] = ' '.join(fuente['texto'].split())", "fuente['texto'] = fuente['texto']", 'pq1'),
    ('antecedente_como_norma', 'oracle_factory/generacion.py', 'fuente = procedencia(fuente)', 'fuente = dict(fuente)', 'pq1'),
    ('concepto_alternativo_ignorado', 'oracle_factory/rag.py', "and all(any(t.casefold() in datos['respuesta'].casefold() for t in g)\n                                   for g in p.get('contiene_alguno', []))", "and all(g[0].casefold() in datos['respuesta'].casefold() for g in p.get('contiene_alguno', []))", 'pq6'),
    ('procedimiento_obsoleto_aceptado', 'oracle_factory/rag.py', "and not any(t.casefold() in datos['respuesta'].casefold() for t in p.get('excluye', []))", 'and True', 'pq6'),
    ('sin_cierre_al_agotar_herramientas', 'oracle_factory/generacion.py', "disponibles = herramientas() if llamadas < conf['max_llamadas'] and not cerrar_contexto else []", 'disponibles = herramientas()', 'pq2'),
    ('sin_respaldo_llama_modelo', 'oracle_factory/rag.py', 'if not respaldo:', 'if False:', 'pq4'),
    ('antecedente_actual_aceptado', 'oracle_factory/generacion.py', "if alcance == 'actual' and all(procedencia(s)['clase'] in no_normativas for s in referencias):", 'if False:', 'pq1'),
    ('conteo_desde_ejemplo', 'oracle_factory/generacion.py', "not rag._calculo_respaldado({**final, 'herramientas': trazas}, intencion['estado'])", 'False', 'pq1'),
    ('resultado_desborda_contexto', 'oracle_factory/generacion.py', 'if len(json.dumps(mensajes + [respuesta_proyectada], ensure_ascii=False).encode()) > LIMITE_CONTEXTO - RESERVA_CIERRE:', 'if False:', 'pq2'),
    ('versiones_del_proyecto_rechazadas', 'oracle_factory/generacion.py', '|Qwen|SQLite|Ollama|HTTP|versión|version', '|versión|version', 'pq2'),
    ('ordinales_colon_rechazados', 'oracle_factory/generacion.py', "texto = re.sub(r'\\bpaso\\s+\\d+\\b', 'paso', texto, flags=re.I)", 'texto = texto', 'pq2'),
    ('metricas_sin_distincion', 'oracle_factory/rag.py', "'documental': 'recuperacion_con_respaldo'", "'documental': 'recuperacion_en_cinco'", 'pq6'),
    ('inventario_como_coincidencias', 'oracle_factory/rag.py', 'Registros inspeccionados para verificar el filtro (pueden no coincidir):', 'Registros coincidentes:', 'pq3'),
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
