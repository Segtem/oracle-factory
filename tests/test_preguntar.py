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
        p.write_text('# Diseño\n\nSe eligió un clon aparte porque aísla la configuración\ny las ramas de Git.\n')

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
        # Una aprobación guardada puede estar vencida. El detalle debe reflejar lo mismo que estado, no el registro crudo.
        from oracle_factory import consultas
        carpeta, estado = f.leer(ident)
        estado['revision'] = {'decision': 'aprobar', 'hallazgos_abiertos': 0, 'revisor': 'Revisor fixture'}
        f.ruta_registro(carpeta).write_text(json.dumps(estado))
        esperado = f.datos_estado(ident)
        detalle = consultas.registro(f, {'operacion': 'detalle', 'id': ident})['datos']['cambios'][0]
        self.assertEqual(detalle['estado_actual']['pendientes'], esperado['pendientes'])
        self.assertFalse(detalle['estado_actual']['revision']['vigente'])
        self.assertEqual(detalle['estado_actual']['proximo_paso'], esperado['proximo_paso'])
        # Un listado grande pagina datos y fuentes; no envía todo el registro al modelo.
        for n in range(6):
            self.nuevo('pagina' + str(n), 'requisitos_importados')
        pagina = consultas.registro(f, {'operacion': 'listar', 'estado': 'abiertos'})
        self.assertLessEqual(len(pagina['datos']['cambios']), 5)
        self.assertTrue(pagina['datos']['siguiente'])
        siguiente = consultas.registro(f, pagina['datos']['siguiente'])
        self.assertFalse(set(pagina['datos']['ids']) & set(siguiente['datos']['ids']))
        # Una motivación histórica no debe presentarse al modelo como instrucciones actuales.
        fuentes = {'resultados': [
            {'ruta': 'openspec/changes/20261005-154433-vigencia/proposal.md', 'cita': 'antecedente#Why',
             'texto': 'Antes hubo que repetir una revisión idéntica sólo porque cambió HEAD.'},
            {'ruta': 'openspec/specs/vigencia/spec.md', 'cita': 'vigencia#Requirement',
             'texto': 'La revisión sigue vigente mientras coincida el contenido del producto.'}]}
        def con_antecedentes(conf, mensajes, herramientas, timeout):
            contexto = json.loads(mensajes[1]['content'])['fuentes']
            self.assertEqual(contexto[0]['clase'], 'antecedente')
            self.assertEqual(contexto[1]['clase'], 'spec_vigente')
            self.assertIn('no prescribe', contexto[0]['uso'])
            self.assertIn('no conviertas una falla histórica', mensajes[0]['content'])
            return {'content': json.dumps({'estado': 'respondida', 'afirmaciones': [
                {'texto': 'La revisión conserva vigencia si el producto coincide.', 'inferencia': False,
                 'citas': [{'fuente': contexto[1]['id'], 'texto': contexto[1]['texto']}]}]})}
        with patch.object(generacion, 'enviar', side_effect=con_antecedentes):
            vigente = generacion.elaborar(f, '¿Cuándo hay que repetir la revisión?', fuentes, generacion.configuracion(f))
        self.assertEqual(vigente['fuentes'][0]['clase'], 'spec_vigente')
        def antecedente_como_instruccion(conf, mensajes, herramientas, timeout):
            fuente = json.loads(mensajes[1]['content'])['fuentes'][0]
            return {'content': json.dumps({'estado': 'respondida', 'afirmaciones': [
                {'texto': 'Debés repetir una revisión idéntica sólo porque cambió HEAD.', 'inferencia': False,
                 'alcance': 'actual', 'citas': [{'fuente': fuente['id'], 'texto': fuente['texto']}]}]})}
        with patch.object(generacion, 'enviar', side_effect=antecedente_como_instruccion), self.assertRaises(ValueError):
            generacion.elaborar(f, '¿Qué debo repetir ahora?', fuentes, generacion.configuracion(f))
        def antecedente_explicito(*args):
            mensaje = antecedente_como_instruccion(*args)
            datos = json.loads(mensaje['content'])
            datos['afirmaciones'][0].update(texto='Antes hubo que repetir una revisión idéntica al cambiar HEAD.', alcance='antecedente')
            return {'content': json.dumps(datos)}
        with patch.object(generacion, 'enviar', side_effect=antecedente_explicito):
            historia = generacion.elaborar(f, '¿Qué problema existía antes?', fuentes, generacion.configuracion(f))
        self.assertTrue(historia['respuesta'].startswith('Antecedente histórico:'))
        ejemplo = {'resultados': [{'ruta': 'docs/ejemplos.md', 'cita': 'ejemplo',
                                  'texto': 'Ejemplo: Hay 2 cambios abiertos.'}]}
        def contar_desde_ejemplo(conf, mensajes, herramientas, timeout):
            s = json.loads(mensajes[1]['content'])['fuentes'][0]
            return {'content': json.dumps({'estado': 'respondida', 'afirmaciones': [
                {'texto': 'Hay 2 cambios abiertos.', 'inferencia': False,
                 'citas': [{'fuente': s['id'], 'texto': 'Hay 2 cambios abiertos.'}]}]})}
        with patch.object(generacion, 'enviar', side_effect=contar_desde_ejemplo), self.assertRaises(ValueError):
            generacion.elaborar(f, '¿Cuántas tareas abiertas hay y cómo se revisan?', ejemplo, generacion.configuracion(f))
        for pregunta in ('¿Qué cambios no tienen spec y cómo se aprueban?',
                         '¿Cuáles tareas cerradas hay sin hallazgos abiertos y cómo se revisa?'):
            self.assertIsNone(consultas.interpretar(pregunta))

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
        # Un JSON mal formado se vuelve a pedir con formato estructurado, sin aceptar texto sin validar.
        formatos = []
        def corregir_formato(conf, mensajes, herramientas, timeout):
            formatos.append(herramientas)
            if herramientas:
                return {'role': 'assistant', 'content': '{"estado":"respondida", roto'}
            fuente = next(s for s in json.loads(mensajes[1]['content'])['fuentes'] if s['ruta'] == 'docs/decisiones.md')
            return {'role': 'assistant', 'content': json.dumps({'estado': 'respondida', 'afirmaciones': [
                {'texto': 'Se eligió un clon aparte.', 'inferencia': False, 'alcance': 'actual',
                 'citas': [{'fuente': fuente['id'], 'texto': 'Se eligió un clon aparte'}]}]})}
        with patch.object(generacion, 'enviar', side_effect=corregir_formato):
            r = rag.preguntar(f, '¿Por qué se eligió un clon aparte?')
        self.assertEqual(r['tipo'], 'respuesta_elaborada')
        self.assertEqual(len(formatos), 2)
        self.assertEqual(formatos[-1], [])
        self.assertFalse((self.root / 'ajeno').exists())
        contador = []
        def insistir(*args):
            contador.append(1)
            return {'role': 'assistant', 'content': '', 'tool_calls': [{'id': 'c' + str(len(contador)),
                    'function': {'name': 'registro', 'arguments': {'operacion': 'contar', 'estado': 'todos'}}}]}
        with patch.object(generacion, 'enviar', side_effect=insistir), patch.object(consultas, 'registro', wraps=consultas.registro) as ejecutar:
            self.assertNotEqual(rag.preguntar(f, '¿Por qué se usan clones aparte?')['tipo'], 'respuesta_elaborada')
            self.assertEqual(ejecutar.call_count, 2)
        turnos = []
        def cerrar_con_datos(conf, mensajes, herramientas, timeout):
            turnos.append(bool(herramientas))
            if herramientas:
                return {'role': 'assistant', 'tool_calls': [{'id': 'consulta' + str(len(turnos)),
                        'function': {'name': 'registro', 'arguments': {'operacion': 'contar', 'estado': 'todos'}}}]}
            registro = json.loads(next(m['content'] for m in reversed(mensajes) if m['role'] == 'tool'))['fuentes'][0]
            return {'content': json.dumps({'estado': 'respondida', 'afirmaciones': [
                {'texto': 'Hay 0 cambios en total.', 'inferencia': False,
                 'citas': [{'fuente': registro['id'], 'texto': 'Cantidad de cambios todos: 0.'}]}]})}
        with patch.object(generacion, 'enviar', side_effect=cerrar_con_datos):
            final = rag.preguntar(f, '¿Por qué se eligió un clon aparte y cuántos cambios hay según el registro?')
        self.assertEqual(final['tipo'], 'respuesta_elaborada')
        self.assertEqual(turnos, [True, True, False])
        turnos.clear()
        def lote_excedido(conf, mensajes, herramientas, timeout):
            turnos.append(bool(herramientas))
            if herramientas:
                # Tras una consulta quedan una permitida; el modelo solicita dos juntas.
                cantidad = 1 if len(turnos) == 1 else 2
                return {'role': 'assistant', 'tool_calls': [
                    {'id': f'lote{len(turnos)}_{n}', 'function': {'name': 'registro',
                     'arguments': {'operacion': 'contar', 'estado': 'todos'}}} for n in range(cantidad)]}
            registro = json.loads(next(m['content'] for m in reversed(mensajes) if m['role'] == 'tool'))['fuentes'][0]
            return {'content': json.dumps({'estado': 'respondida', 'afirmaciones': [
                {'texto': 'Hay 0 cambios en total.', 'inferencia': False,
                 'citas': [{'fuente': registro['id'], 'texto': 'Cantidad de cambios todos: 0.'}]}]})}
        with patch.object(generacion, 'enviar', side_effect=lote_excedido), patch.object(consultas, 'registro', wraps=consultas.registro) as ejecutar:
            final = rag.preguntar(f, '¿Por qué se eligió un clon aparte y cuántos cambios hay según el registro?')
        self.assertEqual(final['tipo'], 'respuesta_elaborada')
        self.assertEqual(ejecutar.call_count, 1)  # el lote excedido se rechaza entero
        self.assertEqual(turnos, [True, True, False])
        self.assertEqual(final['llamadas_descartadas'], 2)
        self.assertIn('lote', rag.texto(final))
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
        fuente_id = {'S1': {'ruta': 'docs/decisiones.md', 'cita': 'Diseño',
                            'texto': 'El cambio 20261020-200030-aislar usa un clon de Git que no comparte configuración.'}}
        mensaje_id = {'content': json.dumps({'estado': 'respondida', 'afirmaciones': [
            {'texto': 'El cambio 20261020-200030-aislar usa un clon de Git.', 'inferencia': False,
             'citas': [{'fuente': 'S1', 'texto': 'usa un clon de Git que no comparte configuración'}]}]})}
        self.assertEqual(generacion.validar_final(mensaje_id, fuente_id)['tipo'], 'respuesta_elaborada')
        documento = {'S1': {'ruta': 'docs/guia.md', 'texto': 'Se usa Qwen 2.5, SQLite 3, Ollama 0.5 y HTTP 1.1. Se prepara el entorno.'}}
        for afirmacion in ('Se usa Qwen 2.5.', 'Se usa SQLite 3.', 'Se usa Ollama 0.5.', 'Se usa HTTP 1.1.',
                           'Paso 1: Se prepara el entorno.', '(1) Se prepara el entorno.',
                           'En el paso 1 se prepara el entorno.'):
            m = {'content': json.dumps({'estado': 'respondida', 'afirmaciones': [
                {'texto': afirmacion, 'inferencia': False, 'citas': [{'fuente': 'S1', 'texto': 'Se prepara el entorno.'}]}]})}
            self.assertEqual(generacion.validar_final(m, documento)['tipo'], 'respuesta_elaborada')
        self.configurar({'proveedor': 'ollama', 'modelo': 'fixture'})
        # Varias respuestas pequeñas individualmente no pueden desbordar juntas el contexto global.
        grandes = {'resultados': [{'ruta': f'docs/guia{n}.md', 'cita': f'guia{n}',
                    'texto': 'Respaldo vigente del proyecto. ' + 'x' * 5800} for n in range(5)]}
        extra = {'resultados': [{'ruta': f'docs/extra{n}.md', 'cita': f'extra{n}',
                  'texto': 'Respaldo adicional del proyecto. ' + 'y' * 5800} for n in range(3)]}
        tamanos = []
        def con_contexto_limitado(conf, mensajes, herramientas, timeout):
            tamanos.append(len(json.dumps(mensajes, ensure_ascii=False).encode()))
            self.assertLessEqual(tamanos[-1], generacion.LIMITE_CONTEXTO)
            if herramientas:
                return {'tool_calls': [{'id': 'contexto' + str(len(tamanos)), 'function': {
                    'name': 'recuperar', 'arguments': {'pregunta': 'respaldo del proyecto', 'maximo': 3}}}]}
            fuente = json.loads(mensajes[1]['content'])['fuentes'][0]
            return {'content': json.dumps({'estado': 'respondida', 'afirmaciones': [
                {'texto': 'Se conserva el respaldo vigente del proyecto.', 'inferencia': False,
                 'citas': [{'fuente': fuente['id'], 'texto': 'Respaldo vigente del proyecto.'}]}]})}
        with patch.object(generacion, 'enviar', side_effect=con_contexto_limitado), patch.object(rag, 'recuperar', return_value=extra):
            acotada = generacion.elaborar(f, '¿Cómo se conserva el respaldo?', grandes, generacion.configuracion(f))
        self.assertEqual(acotada['tipo'], 'respuesta_elaborada')
        self.assertTrue(acotada['cierre_por_contexto'])
        self.assertLessEqual(len(tamanos), 4)
        # Se prueba el transporte de ambos proveedores contra HTTP real local, sin claves ni modelos reales.
        pedidos = []
        class Manejador(BaseHTTPRequestHandler):
            def do_POST(handler):
                cuerpo = json.loads(handler.rfile.read(int(handler.headers['Content-Length'])))
                pedidos.append((handler.path, cuerpo, handler.headers.get('Authorization')))
                fuente = next(s for s in json.loads(cuerpo['messages'][1]['content'])['fuentes']
                              if s['ruta'] == 'docs/decisiones.md')
                mensaje = {'role': 'assistant', 'content': json.dumps({'estado': 'respondida', 'afirmaciones': [
                    {'texto': 'Se eligió un clon aparte.', 'inferencia': False, 'alcance': 'actual',
                     'citas': [{'fuente': fuente['id'], 'texto': 'Se eligió un clon aparte'}]}], 'pregunta': ''})}
                if cuerpo.get('tools') and not any(m['role'] == 'tool' for m in cuerpo['messages']):
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
            for proveedor, ruta, autenticar in (('ollama', '/api/chat', True), ('openai', '/chat/completions', True),
                                                ('openai', '/chat/completions', False)):
                with self.subTest(proveedor=proveedor), patch.dict(os.environ, {'FACTORY_CLAVE_FIXTURE': 'clave-de-prueba'}):
                    self.configurar({'proveedor': proveedor, 'modelo': 'fixture',
                                     'url': f'http://127.0.0.1:{http.server_port}',
                                     **({'clave_env': 'FACTORY_CLAVE_FIXTURE'} if autenticar else {})})
                    r = rag.preguntar(f, '¿Por qué se eligió un clon aparte?')
                    self.assertEqual(r['tipo'], 'respuesta_elaborada')
                    self.assertEqual(len(r['herramientas']), 1)
                    self.assertEqual(pedidos[-1][0], ruta)
                    self.assertFalse(pedidos[-1][1]['stream'])
                    self.assertNotIn('clave-de-prueba', json.dumps(r))
                    if proveedor == 'openai':
                        self.assertEqual(pedidos[-1][1]['temperature'], 0)
                        self.assertEqual(bool(pedidos[-1][2]), autenticar)
                    final = generacion.enviar(generacion.configuracion(f), pedidos[-1][1]['messages'], [], 10)
                    cuerpo_final = pedidos[-1][1]
                    esquema = cuerpo_final['format'] if proveedor == 'ollama' else cuerpo_final['response_format']['json_schema']['schema']
                    from jsonschema import validate, ValidationError
                    validate(json.loads(final['content']), esquema)
                    with self.assertRaises(ValidationError):
                        validate({'estado': 'inventado', 'afirmaciones': [], 'pregunta': ''}, esquema)
        finally:
            http.shutdown(); http.server_close()

    def test_pq3_cuenta_lista_cero_y_actualiza_registro(self):
        self.configurar()
        a = self.nuevo('cerrado1', 'cerrada')
        b = self.nuevo('cerrado2', 'cerrada')
        abierto = self.nuevo('abierto', 'requisitos_importados')
        self.nuevo('abandonado', 'abandonada')
        with patch.object(rag, 'embeber', side_effect=AssertionError('no debe pedir embeddings')):
            for pregunta in ('Cuantas tareas cerradas hay?', '¿CUÁNTOS CAMBIOS CERRADOS HAY?',
                             '¿Cuántas tareas están cerradas?', '¿Cuántos cambios cerrados existen actualmente?'):
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
        cero = rag.preguntar(f, 'Listá tareas abiertas')
        self.assertTrue(cero['fuentes'][0]['archivos'])  # hay registros consultados aunque ninguno coincida
        self.assertIn('pueden no coincidir', rag.texto(cero))
        self.assertIn('; archivado)', rag.preguntar(f, 'Listá tareas cerradas')['respuesta'])
        # El vault ordena por hora de creación; listar ordena por ID. La paginación debe seguir a listar.
        from oracle_factory import consultas
        registros = [(ident, f.leer(ident)[1]) for ident in (a, b)]
        with patch.object(consultas.kb, 'cambios_del_proyecto', return_value=sorted(registros, reverse=True)):
            self.assertEqual(rag.preguntar(f, 'Listá tareas cerradas')['ids'], sorted((a, b)))

    def test_pq4_sin_respaldo_ambiguedad_y_filtros(self):
        self.configurar()
        self.docs()
        self.assertEqual(rag.preguntar(f, '¿Cuántas tareas cerradas hay desde ayer?')['tipo'], 'consulta_no_admitida')
        self.assertNotEqual(rag.preguntar(f, '¿Cuántas tareas no cerradas hay?')['tipo'], 'registro')
        r = rag.preguntar(f, '¿Qué come el ornitorrinco de Marte?')
        self.assertEqual(r['tipo'], 'sin_respaldo')
        self.assertIn('respaldo suficiente', rag.texto(r))
        self.assertEqual(rag.preguntar(f, '¿Por qué se eligió un clon aparte?')['tipo'], 'documentos')
        self.configurar({'proveedor': 'ollama', 'modelo': 'fixture'})
        from oracle_factory import generacion
        with patch.object(generacion, 'elaborar', side_effect=AssertionError('No debe generar sin respaldo')):
            self.assertEqual(rag.preguntar(f, '¿Cuál es el número de serie de mi cafetera?')['tipo'], 'sin_respaldo')

    def test_pq5_cli_mcp_y_editor_conservan_respuesta(self):
        from oracle_factory import mcp
        self.docs()
        self.nuevo('cerrado', 'cerrada')
        class ServidorModelo(BaseHTTPRequestHandler):
            def do_POST(handler):
                body = json.loads(handler.rfile.read(int(handler.headers['Content-Length'])))
                contexto = json.loads(body['messages'][1]['content'])
                doc = next((s for s in contexto['fuentes'] if s['ruta'] == 'docs/decisiones.md'), None)
                tools = [m for m in body['messages'] if m['role'] == 'tool']
                if doc is None:
                    mensaje = {'role': 'assistant', 'content': '{"estado":"sin_respaldo"}'}
                elif not tools:
                    mensaje = {'role': 'assistant', 'content': '', 'tool_calls': [{'id': 'consultar1',
                               'function': {'name': 'registro', 'arguments': {'operacion': 'contar', 'estado': 'cerrados'}}}]}
                else:
                    registro = json.loads(tools[-1]['content'])['fuentes'][0]
                    n = registro['valor']
                    mensaje = {'role': 'assistant', 'content': json.dumps({'estado': 'respondida', 'afirmaciones': [
                        {'texto': f'Hay {n} cambios cerrados.', 'inferencia': False,
                         'citas': [{'fuente': registro['id'], 'texto': f'Cantidad de cambios cerrados: {n}.'}]},
                        {'texto': 'Se eligió un clon aparte para aislar Git.', 'inferencia': False,
                         'citas': [{'fuente': doc['id'], 'texto': 'aísla la configuración y las ramas de Git'}]}]})}
                raw = json.dumps({'message': mensaje}).encode()
                handler.send_response(200);handler.send_header('Content-Length', str(len(raw)));handler.end_headers()
                handler.wfile.write(raw)
            def log_message(self, *args):
                pass
        http = ThreadingHTTPServer(('127.0.0.1', 0), ServidorModelo)
        threading.Thread(target=http.serve_forever, daemon=True).start()
        self.addCleanup(http.server_close)
        self.addCleanup(http.shutdown)
        self.configurar({'proveedor': 'ollama', 'modelo': 'fixture', 'url': f'http://127.0.0.1:{http.server_port}'})
        import test_tablero
        source = Path(__file__).resolve().parents[1]
        ejecutable = Path(self.tmp.name) / 'factory-fixture'
        ejecutable.write_text(f'#!{sys.executable}\nimport sys\nsys.path.insert(0, {str(source)!r})\n'
                              'from oracle_factory.cli import main\nsys.exit(main())\n')
        ejecutable.chmod(0o755)
        for pregunta, tipo in [('¿Cuántas tareas cerradas hay?', 'registro'),
                               ('¿Cuántas tareas cerradas hay y por qué se eligió un clon aparte?', 'respuesta_elaborada'),
                               ('¿Qué come el ornitorrinco de Marte?', 'sin_respaldo')]:
            with self.subTest(tipo=tipo):
                salida = io.StringIO()
                with contextlib.redirect_stdout(salida):
                    self.assertEqual(f.main(['--proyecto', str(self.root), 'preguntar', '--json', '--', pregunta]), 0)
                datos = json.loads(salida.getvalue())
                self.assertEqual((datos['esquema'], datos['tipo']), ('oracle-factory.preguntar/2', tipo))
                self.assertEqual(datos['limites']['registro']['pagina_maxima'], 10)
                with patch.dict(os.environ, {'PYTHONPATH': str(source)}):
                    remoto = mcp.llamar(self.root, 'preguntar', {'texto': pregunta})
                self.assertFalse(remoto['isError'])
                self.assertEqual(json.loads(remoto['content'][0]['text']), datos)
                r = subprocess.run([test_tablero.NODE, str(source / 'tests/tablero_en_node.cjs'),
                                    str(source / 'editores/vscode'), str(self.root), '[]', str(ejecutable)],
                                   capture_output=True, text=True, timeout=120,
                                   env={**os.environ, 'PREGUNTA': pregunta, 'COMANDO': 'factory.preguntar'})
                self.assertEqual(r.returncode, 0, r.stderr)
                documento = json.loads(r.stdout)['documentos'][0]
                self.assertIn(rag.texto(datos), documento)

    def test_pq6_evaluacion_por_grupos_detecta_errores(self):
        self.configurar()
        self.docs()
        cerrado = self.nuevo('cerrado', 'cerrada')
        archivo = self.root / 'kb/preguntas-de-oro.json'
        archivo.parent.mkdir(exist_ok=True)
        archivo.write_text(json.dumps([
            {'id': 'doc', 'pregunta': '¿Por qué clones aparte?', 'esperadas': ['docs/decisiones.md']},
            {'id': 'registro', 'grupo': 'registro', 'pregunta': 'Cuantas tareas cerradas hay?', 'valor': 1},
            {'id': 'listado', 'grupo': 'registro', 'pregunta': 'Listá tareas cerradas', 'valor': 1,
             'requiere_listado': True, 'ids': [cerrado]},
            {'id': 'negativa', 'grupo': 'abstencion', 'pregunta': '¿Cuánto mide el ornitorrinco marciano?', 'tipo': 'sin_respaldo'}]))
        destino = self.root.parent / 'evaluacion'
        rag.evaluar(f, destino)
        hechos = json.loads((destino / 'hechos.json').read_text())
        self.assertEqual({g['grupo'] for g in hechos['preguntar_grupo']}, {'documental', 'registro', 'abstencion'})
        self.assertTrue(all(g['errores'] == 0 for g in hechos['preguntar_grupo']))
        with patch.object(rag, 'preguntar', return_value={**rag.preguntar(f, 'Cuantas tareas cerradas hay?'), 'valor': 999}):
            rag.evaluar(f, self.root.parent / 'errada')
        mal = json.loads((self.root.parent / 'errada/hechos.json').read_text())
        self.assertEqual(next(p['acierto'] for p in mal['preguntar_pregunta'] if p['id'] == 'registro'), 0)
        real = rag.preguntar
        def sin_ids(*args, **kwargs):
            datos = real(*args, **kwargs)
            if datos.get('pagina'):
                datos['ids'] = []
            return datos
        with patch.object(rag, 'preguntar', side_effect=sin_ids):
            rag.evaluar(f, self.root.parent / 'listado-vacio')
        listado = json.loads((self.root.parent / 'listado-vacio/hechos.json').read_text())
        self.assertEqual(next(p['acierto'] for p in listado['preguntar_pregunta'] if p['id'] == 'listado'), 0)
        sin = {**rag.preguntar(f, '¿Por qué se eligió un clon aparte?'), 'tipo': 'sin_respaldo'}
        with patch.object(rag, 'preguntar', return_value=sin):
            rag.evaluar(f, self.root.parent / 'guia-no-respondida')
        falsa = json.loads((self.root.parent / 'guia-no-respondida/hechos.json').read_text())
        grupo_doc = next(g for g in falsa['preguntar_grupo'] if g['grupo'] == 'documental')
        self.assertEqual((grupo_doc['errores'], grupo_doc['abstenciones_incorrectas']), (1, 1))
        # Ranking y respuesta con respaldo son medidas distintas, explícitas y no compensables.
        self.assertEqual(falsa['rag_corrida'][0]['aciertos'], 1)
        self.assertEqual(falsa['rag_corrida'][0]['criterio'], 'recuperacion_en_cinco')
        self.assertEqual(grupo_doc['criterio'], 'recuperacion_con_respaldo')
        from oracle_factory import generacion
        self.configurar({'proveedor': 'ollama', 'modelo': 'fixture'})
        casos = self.root / 'casos-adicionales.json'
        casos.write_text(json.dumps([{'id': 'generada', 'grupo': 'generativa', 'pregunta': '¿Por qué se eligió un clon aparte?',
                                      'contiene': ['clon'], 'contiene_alguno': [['aislamiento', 'clon']],
                                      'excluye': ['procedimiento obsoleto'], 'fuentes': ['docs/decisiones.md']}]))
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
        def obsoleto(*args, **kwargs):
            salida = modelo(*args, **kwargs)
            datos = json.loads(salida['content'])
            if datos.get('afirmaciones'):
                datos['afirmaciones'][0]['texto'] += ' Procedimiento obsoleto.'
            return {**salida, 'content': json.dumps(datos)}
        with patch.object(generacion, 'enviar', side_effect=obsoleto):
            rag.evaluar(f, self.root.parent / 'procedimiento-obsoleto', simulado=True, casos=casos)
        erronea = json.loads((self.root.parent / 'procedimiento-obsoleto/hechos.json').read_text())
        self.assertEqual(next(g['errores'] for g in erronea['preguntar_grupo'] if g['grupo'] == 'generativa'), 1)
        compuesta = json.loads(casos.read_text())
        compuesta[0].update(requiere_registro=True, filtro_registro='cerrados')
        casos.write_text(json.dumps(compuesta))
        with patch.object(generacion, 'enviar', side_effect=modelo):
            rag.evaluar(f, self.root.parent / 'sin-consultar-registro', simulado=True, casos=casos)
        sin_registro = json.loads((self.root.parent / 'sin-consultar-registro/hechos.json').read_text())
        grupo = next(g for g in sin_registro['preguntar_grupo'] if g['grupo'] == 'generativa')
        self.assertEqual(grupo['errores'], 1)  # citar sólo una guía no acredita el cálculo solicitado
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
