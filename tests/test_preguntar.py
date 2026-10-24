"""Contratos pq1–pq6: respuestas con fuentes, herramientas y límites en proyectos aislados."""
import contextlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_archivo as base
from oracle_factory import rag

f = base.f


class Preguntar(unittest.TestCase):
    setUp, escribe, git = base.Archivo.setUp, base.Archivo.escribe, base.Archivo.git

    def configurar(self, generacion=None):
        ruta = self.root / '.factory/config.json'
        datos = json.loads(ruta.read_text())
        datos['rag'] = {'embeddings': {'proveedor': 'ninguno'}}
        if generacion is not None:
            datos['rag']['generacion'] = generacion
        ruta.write_text(json.dumps(datos))

    def nuevo(self, sufijo, fase):
        f.AGENTE = 'codex'
        try:
            ident = f.nuevo('Cambio ' + sufijo, capacidad='otra', sufijo=sufijo)
        finally:
            f.AGENTE = None
        carpeta, estado = f.leer(ident)
        estado['fase'] = fase
        if fase == 'cerrada':
            estado['archivo'] = {'spec': 'openspec/specs/otra/spec.md'}
        f.ruta_registro(carpeta).write_text(json.dumps(estado))
        return ident

    def docs(self):
        p = self.root / 'docs/decisiones.md'
        p.parent.mkdir(exist_ok=True)
        p.write_text('# Diseño\n\nSe eligió un clon aparte porque aísla la configuración y las ramas de Git.\n')

    def test_pq1_respuesta_abierta_con_fuentes_y_herramientas(self):
        from oracle_factory import generacion
        self.configurar({'proveedor': 'ollama', 'modelo': 'fixture'})
        self.docs()
        ident = self.nuevo('abierto', 'requisitos_importados')
        llamadas = []

        def modelo(conf, mensajes, herramientas, timeout):
            llamadas.append(mensajes)
            if not any(m['role'] == 'tool' for m in mensajes):
                return {'role': 'assistant', 'content': '', 'tool_calls': [
                    {'id': 'consulta1', 'type': 'function', 'function': {'name': 'registro',
                     'arguments': {'operacion': 'contar', 'estado': 'abiertos'}}}]}
            # El modelo simulado usa fuentes realmente recibidas, no inventa IDs de fuentes.
            contexto = json.loads(mensajes[1]['content'])
            extra = json.loads(mensajes[-1]['content'])
            fuente_doc = next(s for s in contexto['fuentes'] if s['ruta'] == 'docs/decisiones.md')
            fuente_registro = extra['fuentes'][0]
            return {'role': 'assistant', 'content': json.dumps({'estado': 'respondida', 'afirmaciones': [
                {'texto': 'Se usa un clon aparte para aislar Git.', 'inferencia': False,
                 'citas': [{'fuente': fuente_doc['id'], 'texto': 'aísla la configuración y las ramas de Git'}]},
                {'texto': 'Hay 1 cambio abierto.', 'inferencia': False,
                 'citas': [{'fuente': fuente_registro['id'], 'texto': '"cantidad": 1'}]}]})}

        with patch.object(generacion, 'enviar', side_effect=modelo):
            respuesta = rag.preguntar(f, '¿Por qué se eligió un clon aparte y cuánto trabajo queda abierto?')
            otra = rag.preguntar(f, '¿Cuántas tareas abiertas hay y por qué se eligió un clon aparte?')
        self.assertEqual(respuesta['tipo'], 'respuesta_elaborada')
        self.assertIn('aislar Git', respuesta['respuesta'])
        self.assertIn('1 cambio abierto', respuesta['respuesta'])
        self.assertEqual(respuesta['modelo_generativo'], 'fixture')
        self.assertEqual(len(respuesta['herramientas']), 1)
        self.assertIn(ident, json.dumps(respuesta['fuentes']))
        self.assertIn('Fuentes', rag.texto(respuesta))
        self.assertEqual(otra['tipo'], 'respuesta_elaborada')
        self.assertEqual(len(llamadas), 4)

    def test_pq2_herramientas_configuracion_fallos_y_limites(self):
        from oracle_factory import generacion, consultas
        self.configurar()
        self.assertIsNone(generacion.configuracion(f))
        self.docs()
        sin = rag.preguntar(f, '¿Por qué se usan clones aparte?')
        self.assertIsNone(sin['modelo_generativo'])
        self.assertIn('generativo', sin['aviso'])
        for args in ({'operacion': 'escribir', 'estado': 'todos'},
                     {'operacion': 'contar', 'estado': 'cerrados', 'shell': 'touch ajeno'},
                     {'operacion': 'contar', 'estado': 'no_cerrados'}):
            with self.subTest(args=args), self.assertRaises(ValueError):
                consultas.registro(f, args)
        self.assertEqual(consultas.registro(f, {'operacion': 'contar', 'estado': 'todos'})['datos']['cantidad'], 0)
        self.configurar({'proveedor': 'ollama', 'modelo': 'fixture', 'max_llamadas': 2})
        for mensaje in (
                {'role': 'assistant', 'content': '', 'tool_calls': [{'id': 'a', 'function': {'name': 'shell', 'arguments': {}}}]},
                {'role': 'assistant', 'content': 'No es un resultado estructurado'},
                {'role': 'assistant', 'content': json.dumps({'estado': 'respondida', 'afirmaciones': [
                    {'texto': 'Hay 999 abiertos.', 'inferencia': False, 'citas': [{'fuente': 'inventada', 'texto': '999'}]}]})}):
            with self.subTest(mensaje=mensaje), patch.object(generacion, 'enviar', return_value=mensaje):
                r = rag.preguntar(f, '¿Por qué se usan clones aparte?')
                self.assertNotEqual(r['tipo'], 'respuesta_elaborada')
                self.assertNotIn('999', r['respuesta'])
                self.assertTrue(r['aviso'])
        with patch.object(generacion, 'enviar', side_effect=OSError('proveedor caído')):
            self.assertIn('generación', rag.preguntar(f, 'clones aparte')['aviso'])
        self.assertFalse((self.root / 'ajeno').exists())
        contador = []
        def insistir(*args):
            contador.append(1)
            return {'role': 'assistant', 'content': '', 'tool_calls': [{'id': 'c' + str(len(contador)),
                    'function': {'name': 'registro', 'arguments': {'operacion': 'contar', 'estado': 'todos'}}}]}
        with patch.object(generacion, 'enviar', side_effect=insistir), patch.object(consultas, 'registro', wraps=consultas.registro) as ejecutar:
            self.assertNotEqual(rag.preguntar(f, '¿Por qué se usan clones aparte?')['tipo'], 'respuesta_elaborada')
            self.assertEqual(ejecutar.call_count, 2)
        for conf in ({'proveedor': 'ollama'}, {'proveedor': 'openai', 'modelo': 'fixture'},
                     {'proveedor': 'ollama', 'modelo': 'fixture', 'max_llamadas': True},
                     {'proveedor': 'ollama', 'modelo': 'fixture', 'url': 'http://usuario:clave@localhost'},
                     {'proveedor': 'ollama', 'modelo': 'fixture', 'url': 'http://['}):
            self.configurar(conf)
            with self.subTest(conf=conf), self.assertRaises(f.FactoryError):
                generacion.configuracion(f)
        # Citas inventadas o números añadidos tampoco se aceptan aunque el ID de fuente sea real.
        fuente = {'S1': {'texto': 'Hay 1 cambio abierto en el registro.', 'ruta': 'registro', 'cita': 'registro'}}
        for texto, cita in (('Hay 999 cambios.', 'Hay 1 cambio abierto'), ('Se eligió un clon.', 'Un fragmento inexistente')):
            mensaje = {'content': json.dumps({'estado': 'respondida', 'afirmaciones': [
                {'texto': texto, 'inferencia': False, 'citas': [{'fuente': 'S1', 'texto': cita}]}]})}
            with self.subTest(texto=texto), self.assertRaises(ValueError):
                generacion.validar_final(mensaje, fuente)
        self.configurar({'proveedor': 'ollama', 'modelo': 'fixture'})
        # Se prueba el transporte de ambos proveedores contra HTTP real local, sin claves ni modelos reales.
        pedidos = []
        class Manejador(BaseHTTPRequestHandler):
            def do_POST(handler):
                cuerpo = json.loads(handler.rfile.read(int(handler.headers['Content-Length'])))
                pedidos.append((handler.path, cuerpo, handler.headers.get('Authorization')))
                fuente = next(s for s in json.loads(cuerpo['messages'][1]['content'])['fuentes']
                              if s['ruta'] == 'docs/decisiones.md')
                mensaje = {'role': 'assistant', 'content': json.dumps({'estado': 'respondida', 'afirmaciones': [
                    {'texto': 'Se eligió un clon aparte.', 'inferencia': False,
                     'citas': [{'fuente': fuente['id'], 'texto': 'Se eligió un clon aparte'}]}]})}
                if not any(m['role'] == 'tool' for m in cuerpo['messages']):
                    args = {'operacion': 'contar', 'estado': 'todos'}
                    mensaje = {'role': 'assistant', 'content': '', 'tool_calls': [{'id': 'http1', 'type': 'function',
                        'function': {'name': 'registro', 'arguments': args if handler.path == '/api/chat' else json.dumps(args)}}]}
                datos = {'message': mensaje} if handler.path == '/api/chat' else {'choices': [{'message': mensaje}]}
                bruto = json.dumps(datos).encode()
                handler.send_response(200); handler.send_header('Content-Length', str(len(bruto))); handler.end_headers()
                handler.wfile.write(bruto)
            def log_message(self, *args):
                pass
        http = ThreadingHTTPServer(('127.0.0.1', 0), Manejador)
        threading.Thread(target=http.serve_forever, daemon=True).start()
        try:
            for proveedor, ruta in (('ollama', '/api/chat'), ('openai', '/chat/completions')):
                with self.subTest(proveedor=proveedor), patch.dict(os.environ, {'FACTORY_CLAVE_FIXTURE': 'clave-de-prueba'}):
                    self.configurar({'proveedor': proveedor, 'modelo': 'fixture',
                                     'url': f'http://127.0.0.1:{http.server_port}', 'clave_env': 'FACTORY_CLAVE_FIXTURE'})
                    r = rag.preguntar(f, '¿Por qué se eligió un clon aparte?')
                    self.assertEqual(r['tipo'], 'respuesta_elaborada')
                    self.assertEqual(len(r['herramientas']), 1)
                    self.assertEqual(pedidos[-1][0], ruta)
                    self.assertFalse(pedidos[-1][1]['stream'])
                    self.assertNotIn('clave-de-prueba', json.dumps(r))
        finally:
            http.shutdown(); http.server_close()

    def test_pq3_cuenta_lista_cero_y_actualiza_registro(self):
        self.configurar()
        a = self.nuevo('cerrado1', 'cerrada')
        b = self.nuevo('cerrado2', 'cerrada')
        abierto = self.nuevo('abierto', 'requisitos_importados')
        self.nuevo('abandonado', 'abandonada')
        with patch.object(rag, 'embeber', side_effect=AssertionError('no debe pedir embeddings')):
            for pregunta in ('Cuantas tareas cerradas hay?', '¿CUÁNTOS CAMBIOS CERRADOS HAY?'):
                r = rag.preguntar(f, pregunta)
                self.assertEqual((r['tipo'], r['valor'], r['filtro']), ('registro', 2, 'cerrados'))
                self.assertTrue({a, b}.issubset(set(r['ids'])))
                self.assertIn('2', rag.texto(r))
            self.assertEqual(rag.preguntar(f, '¿Cuántos cambios hay en total?')['valor'], 4)
            self.assertEqual(rag.preguntar(f, 'Listá las tareas abiertas')['ids'], [abierto])
            self.assertEqual(rag.preguntar(f, '¿Cuántos cambios abandonados hay?')['valor'], 1)
            carpeta, estado = f.leer(abierto)
            estado['fase'] = 'cerrada'
            f.ruta_registro(carpeta).write_text(json.dumps(estado))
            self.assertEqual(rag.preguntar(f, 'Cuantas tareas cerradas hay?')['valor'], 3)
        # La respuesta cero trae el criterio reproducible aunque no haya registros que citar.
        self.assertTrue(rag.preguntar(f, 'Listá tareas abiertas')['fuentes'])

    def test_pq4_sin_respaldo_ambiguedad_y_filtros(self):
        self.configurar()
        self.docs()
        self.assertEqual(rag.preguntar(f, '¿Cuántas tareas cerradas hay desde ayer?')['tipo'], 'consulta_no_admitida')
        self.assertNotEqual(rag.preguntar(f, '¿Cuántas tareas no cerradas hay?')['tipo'], 'registro')
        r = rag.preguntar(f, '¿Qué come el ornitorrinco de Marte?')
        self.assertEqual(r['tipo'], 'sin_respaldo')
        self.assertIn('respaldo suficiente', rag.texto(r))
        self.assertEqual(rag.preguntar(f, '¿Por qué se eligió un clon aparte?')['tipo'], 'documentos')

    def test_pq5_cli_mcp_y_editor_conservan_respuesta(self):
        from oracle_factory import mcp
        self.configurar()
        self.nuevo('cerrado', 'cerrada')
        pregunta = '¿Cuántas tareas cerradas hay?'
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            self.assertEqual(f.main(['--proyecto', str(self.root), 'preguntar', '--json', '--', pregunta]), 0)
        datos = json.loads(salida.getvalue())
        self.assertEqual(datos['esquema'], 'oracle-factory.preguntar/2')
        remoto = mcp.llamar(self.root, 'preguntar', {'texto': pregunta})
        self.assertFalse(remoto['isError'])
        self.assertEqual(json.loads(remoto['content'][0]['text']), datos)
        # El editor ejecuta la CLI real y muestra su respuesta; el arnés sólo reemplaza vscode.
        import test_tablero
        source = Path(__file__).resolve().parents[1]
        ejecutable = Path(self.tmp.name) / 'factory-fixture'
        ejecutable.write_text(f'#!{sys.executable}\nimport sys\nsys.path.insert(0, {str(source)!r})\n'
                              'from oracle_factory.cli import main\nsys.exit(main())\n')
        ejecutable.chmod(0o755)
        r = subprocess.run([test_tablero.NODE, str(source / 'tests/tablero_en_node.cjs'),
                            str(source / 'editores/vscode'), str(self.root), '[]', str(ejecutable)],
                           capture_output=True, text=True, timeout=120,
                           env={**os.environ, 'PREGUNTA': pregunta, 'COMANDO': 'factory.preguntar'})
        self.assertEqual(r.returncode, 0, r.stderr)
        documento = json.loads(r.stdout)['documentos'][0]
        self.assertIn(datos['respuesta'], documento)
        self.assertIn('Fuentes', documento)

    def test_pq6_evaluacion_por_grupos_detecta_errores(self):
        self.configurar()
        self.docs()
        self.nuevo('cerrado', 'cerrada')
        archivo = self.root / 'kb/preguntas-de-oro.json'
        archivo.parent.mkdir(exist_ok=True)
        archivo.write_text(json.dumps([
            {'id': 'doc', 'pregunta': '¿Por qué clones aparte?', 'esperadas': ['docs/decisiones.md']},
            {'id': 'registro', 'grupo': 'registro', 'pregunta': 'Cuantas tareas cerradas hay?', 'valor': 1},
            {'id': 'negativa', 'grupo': 'abstencion', 'pregunta': '¿Cuánto mide el ornitorrinco marciano?', 'tipo': 'sin_respaldo'}]))
        destino = self.root.parent / 'evaluacion'
        rag.evaluar(f, destino)
        hechos = json.loads((destino / 'hechos.json').read_text())
        self.assertEqual({g['grupo'] for g in hechos['preguntar_grupo']}, {'documental', 'registro', 'abstencion'})
        self.assertTrue(all(g['errores'] == 0 for g in hechos['preguntar_grupo']))
        with patch.object(rag, 'preguntar', return_value={**rag.preguntar(f, 'Cuantas tareas cerradas hay?'), 'valor': 999}):
            rag.evaluar(f, self.root.parent / 'errada')
        mal = json.loads((self.root.parent / 'errada/hechos.json').read_text())
        self.assertTrue(any(g['grupo'] == 'registro' and g['errores'] for g in mal['preguntar_grupo']))
        from oracle_factory import generacion
        self.configurar({'proveedor': 'ollama', 'modelo': 'fixture'})
        casos = self.root / 'casos-adicionales.json'
        casos.write_text(json.dumps([{'id': 'generada', 'grupo': 'generativa', 'pregunta': '¿Por qué se eligió un clon aparte?',
                                      'contiene': ['clon'], 'fuentes': ['docs/decisiones.md']}]))
        def modelo(conf, mensajes, herramientas, timeout):
            fuentes = json.loads(mensajes[1]['content'])['fuentes']
            fuente = next((s for s in fuentes if s['ruta'] == 'docs/decisiones.md'), None)
            if fuente is None:
                return {'content': '{"estado":"sin_respaldo"}'}
            return {'content': json.dumps({'estado': 'respondida', 'afirmaciones': [{'texto': 'Se eligió un clon aparte.',
                    'inferencia': False, 'citas': [{'fuente': fuente['id'], 'texto': 'Se eligió un clon aparte'}]}]})}
        with patch.object(generacion, 'enviar', side_effect=modelo):
            rag.evaluar(f, self.root.parent / 'simulada', simulado=True, casos=casos)
        simulada = json.loads((self.root.parent / 'simulada/hechos.json').read_text())
        grupo = next(g for g in simulada['preguntar_grupo'] if g['grupo'] == 'generativa')
        self.assertEqual((grupo['aciertos'], grupo['simulado']), (1, 1))
        with patch.object(generacion, 'enviar', return_value={'content': '{"estado":"sin_respaldo"}'}):
            rag.evaluar(f, self.root.parent / 'abstencion-errada', simulado=True, casos=casos)
        mala = json.loads((self.root.parent / 'abstencion-errada/hechos.json').read_text())
        grupo = next(g for g in mala['preguntar_grupo'] if g['grupo'] == 'generativa')
        self.assertEqual((grupo['errores'], grupo['abstenciones_incorrectas']), (1, 1))
        casos.write_text(json.dumps([{'id': 'incompleto', 'grupo': 'registro', 'pregunta': 'Cuantas tareas hay?'}]))
        with self.assertRaises(f.FactoryError):
            rag.evaluar(f, self.root.parent / 'incompleta', casos=casos)


if __name__ == '__main__':
    unittest.main()
