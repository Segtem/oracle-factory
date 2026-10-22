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

            def log_message(self, *args):
                pass

        self.http = ThreadingHTTPServer(('127.0.0.1', 0), Manejador)
        self.url = f'http://127.0.0.1:{self.http.server_address[1]}'
        threading.Thread(target=self.http.serve_forever, daemon=True).start()

    def textos(self):
        return [t for p in self.pedidos for t in p['textos']]


class Rag(unittest.TestCase):
    setUp, escribe, git = _archivo.Archivo.setUp, _archivo.Archivo.escribe, _archivo.Archivo.git

    def servidor(self, **conf):
        s = Servidor()
        self.addCleanup(s.http.shutdown)
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
        self.configurar({'proveedor': 'ninguno'})
        vivo, muerto = self.nuevo('La tortuga', 'vivo'), self.nuevo('La tortuga vieja', 'muerto')
        self.escribir(f'openspec/changes/{vivo}/proposal.md', '# La tortuga\n\n## Why\n\nLa tortuga cruza el camino despacio.\n')
        self.escribir(f'openspec/changes/{muerto}/proposal.md', '# Vieja\n\n## Why\n\nLa tortuga ya no cruza el camino.\n')
        with self.escribe('1'), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            f.abandonar(muerto)
        self.escribir('kb/notas/tortugas.md', '---\nfuentes: [README.md]\n---\n# Tortugas\n\nTodo sobre la tortuga y el camino.\n')
        self.escribir('README.md', 'proyecto\n')
        self.git('add', '-A')
        self.git('commit', '-qm', 'base')
        datos = self.preguntar('¿Cómo cruza el camino la tortuga?')
        citas = [r['cita'] for r in datos['resultados']]
        self.assertEqual(citas[0], f'openspec/changes/{vivo}/proposal.md#Why')
        self.assertEqual(datos['resultados'][0]['cambio'], vivo)
        self.assertFalse([c for c in citas if muerto in c or 'tortugas.md' in c], citas)
        self.assertEqual(datos['por_revisar'], ['kb/notas/tortugas.md'])
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
        with patch.object(rag.urllib.request, 'urlopen', anotar):
            datos = self.preguntar('tortuga')
        self.assertEqual(rag.configuracion(f)['modelo'], 'qwen3-embedding:0.6b')
        self.assertTrue(rag.configuracion(f)['prefijo_pregunta'].startswith('Instruct:'))
        self.assertEqual(urls, ['http://localhost:11434/api/embed'])
        self.assertEqual(datos['modo'], 'lexico')
        # Una URL que no es local sólo si el proyecto la configuró: la de por defecto no puede ser externa.
        urls.clear()
        with patch.dict(rag.POR_DEFECTO, {'url': 'https://embeddings.example.com'}), patch.object(rag.urllib.request, 'urlopen', anotar):
            self.assertIn('no es local', self.preguntar('tortuga')['aviso'])
        self.assertEqual(urls, [])
        # Un proveedor OpenAI configurado: sólo a su URL, con la clave de su variable.
        s = Servidor()
        self.addCleanup(s.http.shutdown)
        self.configurar({'proveedor': 'openai', 'url': s.url, 'modelo': 'otro', 'clave_env': 'CLAVE_DE_PRUEBA'})
        with patch.dict('os.environ', {'CLAVE_DE_PRUEBA': 'secreta'}):
            self.assertEqual(self.preguntar('tortuga')['modo'], 'hibrido')
        self.assertEqual({(p['ruta'], p['modelo'], p['clave']) for p in s.pedidos}, {('/embeddings', 'otro', 'Bearer secreta')})
        self.assertEqual(s.pedidos[-1]['textos'], ['tortuga'])  # otro modelo no hereda el prefijo del de por defecto
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
        # Otro modelo: los embeddings viejos no sirven.
        s.pedidos.clear()
        self.configurar({'proveedor': 'ollama', 'url': s.url, 'modelo': 'otro-modelo'})
        self.preguntar('tortuga')
        self.assertEqual(len(s.textos()), primera)

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
        # Una pregunta no se responde con el archivo que la contiene (la lista de preguntas de un diseño, por ejemplo).
        self.escribir('docs/lista.md', '# Lista\n\n¿Qué llevo si llueve? es una de las preguntas.\n')
        with contextlib.redirect_stdout(io.StringIO()):
            rag.evaluar(f, self.root.parent / 'otra')
        detalle = {x['id']: x for x in json.loads((self.root.parent / 'otra/detalle.json').read_text())}
        self.assertNotIn('docs/lista.md', detalle['lluvia']['primeros'])


if __name__ == '__main__':
    unittest.main()
