"""Preguntar al conocimiento: escenarios rag1–rag5, en proyectos temporales con la CLI en proceso y un proveedor de
embeddings de prueba (un servidor HTTP local y determinista)."""
import contextlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
from pathlib import Path
import subprocess
import sys
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_archivo as _archivo  # noqa: E402

f = _archivo.f
rag = f.rag_mod
# Un «modelo» de prueba: cada concepto es una dimensión, y sus sinónimos caen en la misma.
CONCEPTOS = [('azar', 'aleatori', 'suerte'), ('tortuga', 'quelonio'), ('integrar', 'merge', 'fusionar'), ('lluvia', 'paraguas', 'llue')]


def vector(texto):
    t = texto.casefold()
    return [float(sum(t.count(s) for s in sinonimos)) for sinonimos in CONCEPTOS]


class Servidor:
    """Un proveedor de embeddings de prueba: Ollama (/api/embed) u OpenAI (/embeddings). Anota cada pedido."""

    def __init__(self):
        self.pedidos = []
        servidor = self

        class Manejador(BaseHTTPRequestHandler):
            def do_POST(self):
                cuerpo = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                servidor.pedidos.append({'ruta': self.path, 'modelo': cuerpo['model'], 'textos': cuerpo['input'],
                                         'clave': self.headers.get('Authorization')})
                vectores = [vector(x) for x in cuerpo['input']]
                datos = {'embeddings': vectores} if self.path == '/api/embed' else {'data': [{'embedding': v} for v in vectores]}
                salida = json.dumps(datos).encode()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(salida)))
                self.end_headers()
                self.wfile.write(salida)

            def do_GET(self):  # nadie debería llegar acá: los embeddings se piden con POST
                servidor.pedidos.append({'ruta': self.path, 'metodo': 'GET'})
                self.send_response(404)
                self.end_headers()

            def log_message(self, *args):
                pass

        self.http = ThreadingHTTPServer(('127.0.0.1', 0), Manejador)
        self.url = f'http://127.0.0.1:{self.http.server_address[1]}'
        threading.Thread(target=self.http.serve_forever, daemon=True).start()

    def cerrar(self):
        self.http.shutdown()
        self.http.server_close()

    def textos(self):
        return [t for p in self.pedidos for t in p['textos']]


class Rag(unittest.TestCase):
    setUp, escribe, git = _archivo.Archivo.setUp, _archivo.Archivo.escribe, _archivo.Archivo.git

    def servidor(self, **conf):
        s = Servidor()
        self.addCleanup(s.cerrar)
        self.configurar({'proveedor': 'ollama', 'url': s.url, 'modelo': 'prueba', **conf})
        return s

    def configurar(self, embeddings):
        ruta = self.root / '.factory/config.json'
        datos = json.loads(ruta.read_text()) if ruta.is_file() else {}
        datos['rag'] = {'embeddings': embeddings}
        ruta.write_text(json.dumps(datos))

    def escribir(self, rel, texto):
        ruta = self.root / rel
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(texto)

    def nuevo(self, titulo, sufijo):
        f.AGENTE = 'claude-code'
        try:
            return f.nuevo(titulo, capacidad='otra', sufijo=sufijo)
        finally:
            f.AGENTE = None

    def preguntar(self, texto, **kw):
        with contextlib.redirect_stdout(io.StringIO()):
            return rag.preguntar(f, texto, **kw)

    # --- rag1: pasajes vigentes con su cita ------------------------------------------------------------------------
    def test_rag1_una_pregunta_sobre_una_decision(self):
        with contextlib.redirect_stdout(io.StringIO()):
            f.main(['--proyecto', str(self.root), 'kb'])  # el proyecto usa el vault: el cierre deja su nota
            vivo = _archivo.Archivo.cambio_cerrado(self)
        self.assertEqual(f.leer(vivo)[1]['fase'], 'cerrada')
        self.configurar({'proveedor': 'ninguno'})
        muerto = self.nuevo('La tortuga vieja', 'muerto')
        self.escribir(f'openspec/changes/{vivo}/proposal.md', '# La tortuga\n\n## Why\n\nLa tortuga cruza el camino despacio.\n')
        self.escribir(f'openspec/changes/{muerto}/proposal.md', '# Vieja\n\n## Why\n\nLa tortuga ya no cruza el camino.\n')
        self.escribir('docs/historia.md', f'# Historia\n\nAntes hubo un intento con ranas, ver [[cambios/{muerto}]].\n')
        with self.escribe('1'), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            f.abandonar(muerto)
        self.escribir('kb/notas/tortugas.md', '---\nfuentes: [README.md]\n---\n# Tortugas\n\nTodo sobre la tortuga y el camino.\n')
        self.escribir('README.md', 'proyecto\n')
        # Un requisito que ya no está vigente, y el índice del vault que nombra todo: tampoco responden.
        self.escribir('kb/requisitos/viejo.md', '---\nvigente: false\n---\n# viejo\n\nLa tortuga cruza el camino por el puente.\n')
        (self.root / 'kb/README.md').write_text((self.root / 'kb/README.md').read_text() + '\n- La tortuga cruza el camino\n')
        self.git('add', '-A')
        self.git('commit', '-qm', 'base')
        datos = self.preguntar('¿Cómo cruza el camino la tortuga?')
        citas = [r['cita'] for r in datos['resultados']]
        self.assertEqual(citas[0], f'openspec/changes/{vivo}/proposal.md#Why')
        self.assertEqual(datos['resultados'][0]['cambio'], vivo)
        self.assertFalse([c for c in citas if muerto in c or 'tortugas.md' in c or 'viejo.md' in c or 'README' in c], citas)
        self.assertEqual(datos['por_revisar'], ['kb/notas/tortugas.md'])
        # La nota del cambio cerrado en el vault también responde; y una guía que enlaza al abandonado no es suya.
        self.assertIn(f'kb/cambios/{vivo}.md', [r['ruta'] for r in self.preguntar('Comprobar el título de una nota')['resultados']])
        self.assertEqual(self.preguntar('ranas')['resultados'][0]['ruta'], 'docs/historia.md')
        self.assertIn('Quedaron afuera por revisar', rag.texto(datos))
        # Sólo lectura: el proyecto sigue igual; lo único nuevo es el índice local (ignorado por Git).
        self.assertEqual(self.git('status', '--porcelain'), '')
        self.assertTrue(rag.ruta_indice(f).is_file())
        # Ni el vault: aunque haya quedado viejo respecto del registro, preguntar no lo rehace (eso es de kb).
        with contextlib.redirect_stdout(io.StringIO()):
            f.main(['--proyecto', str(self.root), 'kb'])
        carpeta, estado = f.leer(vivo)
        estado['titulo'] = 'Otro título'
        f.ruta_registro(carpeta).write_text(json.dumps(estado))
        self.git('add', '-A')
        self.git('commit', '-qm', 'vault y un registro que lo deja viejo')
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            self.assertEqual(f.main(['--proyecto', str(self.root), 'preguntar', 'tortuga', '--json']), 0)
        self.assertEqual(json.loads(salida.getvalue())['esquema'], 'oracle-factory.preguntar/1')
        self.assertEqual(self.git('status', '--porcelain'), '')

    # --- rag2: híbrida y dice qué usó ------------------------------------------------------------------------------
    def test_rag2_una_pregunta_con_otras_palabras(self):
        self.escribir('docs/ids.md', '# Identificadores\n\n## Cómo se eligen\n\nCada identificador se elige de forma aleatoria.\n')
        self.escribir('docs/otro.md', '# Otro\n\n## Clima\n\nCuando hay lluvia conviene llevar paraguas.\n')
        self.escribir('kb/notas/a.md', '# A\n\nEl clima y la lluvia, ver [[notas/b]] para más.\n')
        self.escribir('kb/notas/b.md', '# B\n\nUna nota sin palabras en común con nada de lo preguntado.\n')
        self.servidor()
        datos = self.preguntar('¿Por qué es al azar?')
        primero = datos['resultados'][0]
        self.assertEqual((datos['modo'], primero['ruta']), ('hibrido', 'docs/ids.md'))
        self.assertEqual(primero['aportes']['lexico'], 0)  # ninguna palabra en común: lo encontró lo semántico
        self.assertGreater(primero['aportes']['semantico'], 0)
        # El grafo trae la nota que enlaza la que responde.
        lluvia = {r['ruta']: r['aportes'] for r in self.preguntar('lluvia')['resultados']}
        self.assertGreater(lluvia['kb/notas/b.md']['grafo'], 0)
        self.assertEqual(lluvia['kb/notas/b.md']['lexico'], 0)
        # El título de un archivo es su #, aunque lo siga un ##; un # dentro de un bloque de código no parte la sección;
        # docs/ se recorre entero; un archivo enorme queda afuera.
        self.escribir('docs/guias/spec.md', '# Capability: jardín\n\n## Requirements\n\n### Requirement: regar\n'
                      'Las plantas se riegan al atardecer.\n\n```bash\n# un comentario de shell\nregar --todo\n```\n')
        [regar] = [r for r in self.preguntar('regar plantas atardecer')['resultados'] if r['ruta'] == 'docs/guias/spec.md']
        self.assertEqual(regar['seccion'], 'Requirement: regar')
        self.assertTrue(regar['texto'].startswith('Capability: jardín\nRequirement: regar'))
        self.assertIn('# un comentario de shell', regar['texto'])
        self.escribir('docs/script.md', '```bash\n# no es un título\n```\n\n# Script\n\n## Uso\n\nSe corre con cuidado y sin apuro.\n')
        [uso] = [r for r in self.preguntar('cuidado apuro')['resultados'] if r['ruta'] == 'docs/script.md']
        self.assertTrue(uso['texto'].startswith('Script\nUso'))
        self.escribir('docs/enorme.md', '# Enorme\n\n' + 'cometa ' * (f.estructura.LIMITE_ARCHIVO // 7 + 1))
        self.assertNotIn('docs/enorme.md', [r['ruta'] for r in self.preguntar('cometa')['resultados']])
        # Lo léxico no distingue tildes ni mayúsculas.
        self.escribir('docs/acentos.md', '# Acentos\n\nLA DECISION se tomo en la reunion de ayer.\n')
        self.assertEqual(self.preguntar('¿Qué decisión se tomó?')['resultados'][0]['ruta'], 'docs/acentos.md')
        # Sin proveedor: sigue y lo dice.
        self.configurar({'proveedor': 'ollama', 'url': 'http://127.0.0.1:9', 'modelo': 'prueba'})
        datos = self.preguntar('¿Por qué es al azar?')
        self.assertEqual(datos['modo'], 'lexico')
        self.assertIn('sólo léxica y por el grafo', rag.texto(datos))

    # --- rag3: configurables y locales por defecto -----------------------------------------------------------------
    def test_rag3_sin_configuracion_y_con_un_proveedor_externo(self):
        self.escribir('docs/a.md', '# A\n\nAlgo de la tortuga.\n')
        urls = []

        def anotar(pedido, timeout):
            urls.append(pedido.full_url)
            raise OSError('sin servidor en la prueba')
        with patch.object(rag, 'ABRIR', anotar):
            datos = self.preguntar('tortuga')
        self.assertEqual(rag.configuracion(f)['modelo'], 'qwen3-embedding:0.6b')
        self.assertTrue(rag.configuracion(f)['prefijo_pregunta'].startswith('Instruct:'))
        self.assertEqual(urls, ['http://localhost:11434/api/embed'])
        self.assertEqual(datos['modo'], 'lexico')
        # Una URL que no es local sólo si el proyecto la configuró: la de por defecto no puede ser externa.
        urls.clear()
        with patch.dict(rag.POR_DEFECTO, {'url': 'https://embeddings.example.com'}), patch.object(rag, 'ABRIR', anotar):
            self.assertIn('no es local', self.preguntar('tortuga')['aviso'])
        self.assertEqual(urls, [])
        self.configurar({'modelo': 'otro'})  # configurar el modelo no es configurar la URL
        with patch.dict(rag.POR_DEFECTO, {'url': 'https://embeddings.example.com'}), patch.object(rag, 'ABRIR', anotar):
            self.assertIn('no es local', self.preguntar('tortuga')['aviso'])
        self.assertEqual(urls, [])
        # Una redirección no se sigue: el otro servidor no recibe nada.
        otro = Servidor()
        self.addCleanup(otro.cerrar)

        class Redirige(BaseHTTPRequestHandler):
            def do_POST(self):
                self.send_response(302)
                self.send_header('Location', otro.url + '/api/embed')
                self.end_headers()

            def log_message(self, *args):
                pass
        redirige = ThreadingHTTPServer(('127.0.0.1', 0), Redirige)
        self.addCleanup(redirige.server_close)
        self.addCleanup(redirige.shutdown)
        threading.Thread(target=redirige.serve_forever, daemon=True).start()
        self.configurar({'proveedor': 'ollama', 'url': f'http://127.0.0.1:{redirige.server_address[1]}', 'modelo': 'prueba'})
        self.assertEqual(self.preguntar('tortuga')['modo'], 'lexico')
        self.assertEqual(otro.pedidos, [])
        # Un proveedor OpenAI configurado: sólo a su URL, con la clave de su variable.
        s = Servidor()
        self.addCleanup(s.cerrar)
        self.configurar({'proveedor': 'openai', 'url': s.url, 'modelo': 'otro', 'clave_env': 'CLAVE_DE_PRUEBA'})
        with patch.dict('os.environ', {'CLAVE_DE_PRUEBA': 'secreta'}):
            self.assertEqual(self.preguntar('tortuga')['modo'], 'hibrido')
        self.assertEqual({(p['ruta'], p['modelo'], p['clave']) for p in s.pedidos}, {('/embeddings', 'otro', 'Bearer secreta')})
        self.assertEqual(s.pedidos[-1]['textos'], ['tortuga'])  # otro modelo no hereda el prefijo del de por defecto
        self.configurar([])
        with self.assertRaisesRegex(f.FactoryError, 'tiene que ser un objeto'):
            self.preguntar('tortuga')
        self.configurar({'proveedor': 'magia'})
        with self.assertRaisesRegex(f.FactoryError, 'ollama, openai o ninguno'):
            self.preguntar('tortuga')

    # --- rag4: el índice se mantiene solo ----------------------------------------------------------------------------
    def test_rag4_el_vault_cambia_entre_dos_preguntas(self):
        self.escribir('docs/a.md', '# A\n\n## Uno\n\nLa tortuga va despacio.\n\n## Dos\n\nLa lluvia moja el camino.\n')
        s = self.servidor()
        self.preguntar('tortuga')
        primera = len(s.textos())
        self.assertGreaterEqual(primera, 3)  # los pasajes y la pregunta
        s.pedidos.clear()
        self.preguntar('tortuga')
        self.assertEqual(len(s.textos()), 1)  # sólo la pregunta: nada cambió
        s.pedidos.clear()
        self.escribir('docs/a.md', '# A\n\n## Uno\n\nLa tortuga va despacio.\n\n## Dos\n\nAhora hay que fusionar dos ramas.\n')
        datos = self.preguntar('¿cómo integrar?')
        self.assertEqual(len(s.textos()), 2)  # el pasaje que cambió y la pregunta
        self.assertIn('fusionar', datos['resultados'][0]['texto'])
        # Un cambio nuevo y una decisión regeneran el vault: sólo se piden los pasajes nuevos o cambiados.
        with contextlib.redirect_stdout(io.StringIO()):
            f.main(['--proyecto', str(self.root), 'kb'])
        antes = {p['huella'] for p in rag.corpus(f)[0]}
        ident = self.nuevo('Un cambio sobre quelonios', 'nuevo')
        nuevas = {p['huella'] for p in rag.corpus(f)[0]} - antes
        s.pedidos.clear()
        datos = self.preguntar('quelonios')
        self.assertEqual(len(s.textos()), len(nuevas) + 1)
        self.assertIn(f'kb/cambios/{ident}.md', [r['ruta'] for r in datos['resultados']])
        antes = {p['huella'] for p in rag.corpus(f)[0]}
        with contextlib.redirect_stdout(io.StringIO()):
            f.mensaje(ident, 'la tortuga es un quelonio')  # una decisión: la nota del cambio se regenera
        nuevas = {p['huella'] for p in rag.corpus(f)[0]} - antes
        self.assertTrue(nuevas)
        s.pedidos.clear()
        self.assertIn('la tortuga es un quelonio', ' '.join(r['texto'] for r in self.preguntar('quelonio')['resultados']))
        self.assertEqual(len(s.textos()), len(nuevas) + 1)
        # Otro modelo: los embeddings viejos no sirven.
        s.pedidos.clear()
        self.configurar({'proveedor': 'ollama', 'url': s.url, 'modelo': 'otro-modelo'})
        self.preguntar('tortuga')
        self.assertEqual(len(s.textos()), len(rag.corpus(f)[0]) + 1)
        # Si .factory/local/rag/ es un enlace a otra carpeta, no escribe ahí.
        afuera = self.root.parent / 'afuera'
        afuera.mkdir()
        import shutil
        shutil.rmtree(self.root / '.factory/local')
        (self.root / '.factory/local').symlink_to(afuera)
        with self.assertRaisesRegex(f.FactoryError, 'enlaces simbólicos'):
            self.preguntar('tortuga')
        self.assertEqual(list(afuera.iterdir()), [])
        # Un cambio cuya carpeta es un enlace a otro lado no entra al corpus.
        (self.root / '.factory/local').unlink()
        ajeno = self.root.parent / 'ajeno'
        (ajeno / 'specs').mkdir(parents=True)
        (ajeno / 'proposal.md').write_text('# Ajeno\n\nUn texto secreto de afuera del proyecto, sobre quelonios.\n')
        (self.root / 'openspec/changes/20990101-000000-ajeno').symlink_to(ajeno)
        self.assertNotIn('secreto', ' '.join(p['texto'] for p in rag.corpus(f)[0]))

    # --- rag5: la calidad se mide con preguntas de oro -------------------------------------------------------------
    def test_rag5_evaluar(self):
        self.escribir('docs/ids.md', '# Identificadores\n\nCada identificador se elige de forma aleatoria.\n')
        self.escribir('docs/clima.md', '# Clima\n\nCon lluvia, paraguas.\n')
        self.escribir('kb/preguntas-de-oro.json', json.dumps([
            {'id': 'azar', 'pregunta': '¿Por qué al azar?', 'esperadas': ['docs/ids.md']},
            {'id': 'lluvia', 'pregunta': '¿Qué llevo si llueve?', 'esperadas': ['docs/clima.md']},
            {'id': 'nada', 'pregunta': '¿Y la tortuga?', 'esperadas': ['docs/tortuga.md']}]))
        self.servidor()
        salida = self.root.parent / 'evaluacion'
        with contextlib.redirect_stdout(io.StringIO()):
            corrida = rag.evaluar(f, salida)
        hechos = json.loads((salida / 'hechos.json').read_text())
        filas = {x['id']: x for x in hechos['rag_pregunta']}
        self.assertEqual((filas['azar']['acierto'], filas['azar']['puesto']), (1, 1))
        self.assertEqual((filas['nada']['acierto'], filas['nada']['puesto']), (0, 0))
        self.assertEqual(corrida, hechos['rag_corrida'][0])
        self.assertEqual((corrida['preguntas'], corrida['aciertos'], corrida['modo'], corrida['modelo']), (3, 2, 'hibrido', 'prueba'))
        self.assertAlmostEqual(corrida['mrr'], 2 / 3, places=3)
        with self.assertRaises(FileExistsError):
            rag.evaluar(f, salida)  # la salida es una carpeta nueva
        # Una pregunta no se responde con la lista de las preguntas de oro (la de un diseño, por ejemplo).
        self.escribir('docs/lista.md', '# Lista\n\n¿Qué llevo si llueve? es una de las preguntas, y ¿Y la tortuga? otra.\n')
        self.escribir('docs/faq.md', '# FAQ\n\n## ¿Y la tortuga?\n\nLa tortuga vive en el jardín.\n')
        with contextlib.redirect_stdout(io.StringIO()):
            rag.evaluar(f, self.root.parent / 'tercera')
        detalle = {x['id']: x for x in json.loads((self.root.parent / 'tercera/detalle.json').read_text())}
        self.assertNotIn('docs/lista.md', detalle['nada']['primeros'])  # trae dos preguntas: es la lista
        self.assertNotIn('docs/lista.md', detalle['lluvia']['primeros'])
        # Y preguntar tampoco la devuelve: se evalúa lo mismo que ve quien pregunta.
        self.assertNotIn('docs/lista.md', [r['ruta'] for r in self.preguntar('¿Y la tortuga?', maximo=50)['resultados']])
        self.assertIn('docs/faq.md', detalle['nada']['primeros'])  # repite sólo su pregunta: es una respuesta
        # Se cuentan los cinco primeros pasajes, no los cinco primeros archivos: si seis secciones de otro archivo van
        # antes, el esperado no está entre lo que ve quien pregunta.
        self.escribir('docs/muchas.md', '# Muchas\n\n' + ''.join(f'## Parte {i}\n\nCuando llueve fuerte, llueve y llueve sin parar.\n\n'
                                                              for i in range(6)))
        oro = json.loads((self.root / 'kb/preguntas-de-oro.json').read_text())
        oro.append({'id': 'fuerte', 'pregunta': '¿Qué pasa si llueve fuerte?', 'esperadas': ['docs/clima.md']})
        self.escribir('kb/preguntas-de-oro.json', json.dumps(oro))
        with contextlib.redirect_stdout(io.StringIO()):
            rag.evaluar(f, self.root.parent / 'cuarta')
        fuerte = {x['id']: x for x in json.loads((self.root.parent / 'cuarta/detalle.json').read_text())}['fuerte']
        self.assertEqual((fuerte['acierto'], fuerte['primeros']), (0, ['docs/muchas.md'] * 5))


if __name__ == '__main__':
    unittest.main()
