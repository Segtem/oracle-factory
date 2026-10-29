"""La consulta de avisos a OSV: escenarios ao1–ao3, contra un servidor local de mentira (ninguna prueba toca la red)."""
import json
import os
import shutil
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
import threading
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_archivo as _archivo  # noqa: E402
from oracle_factory import osv  # noqa: E402

f = _archivo.f


def aviso(ident='GHSA-aaaa', paquete='alfa', versiones=('1.2.3',), arreglo=None):
    afectado = {'package': {'name': paquete, 'ecosystem': 'PyPI'}, 'versions': list(versiones)}
    if arreglo:
        afectado['ranges'] = [{'type': 'ECOSYSTEM', 'events': [{'introduced': '0'}, {'fixed': arreglo}]}]
    return {'id': ident, 'summary': f'aviso {ident}', 'affected': [afectado]}


class Servicio:
    """OSV de mentira: anota cada pedido y responde lo que se le configure."""

    def __init__(self, avisos=None, por_dependencia=None, batch=None, vulns=None):
        self.avisos = {a['id']: a for a in avisos or []}
        self.por_dependencia = por_dependencia or {}  # (nombre, versión) -> [ids]
        self.batch, self.vulns = batch, vulns  # (código, bytes) o None para cortar la conexión; None: respuesta normal
        self.pedidos = []
        servicio = self

        class Manejador(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def responder(self, codigo, cuerpo, cabeceras=None):
                self.send_response(codigo)
                for k, v in (cabeceras or {}).items():
                    self.send_header(k, v)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(cuerpo)))
                self.end_headers()
                self.wfile.write(cuerpo)

            def atender(self, cuerpo):
                servicio.pedidos.append((self.command, self.path, cuerpo))
                if self.path == '/v1/querybatch':
                    if servicio.batch is not None:
                        return servicio.batch
                    consultas = cuerpo['queries']
                    return 200, json.dumps({'results': [
                        {'vulns': [{'id': i, 'modified': '2026-01-01T00:00:00Z'}
                                   for i in servicio.por_dependencia.get((q['package']['name'], q['version']), [])]} for q in consultas]}).encode()
                if self.path.startswith('/v1/vulns/'):
                    if servicio.vulns is not None:
                        return servicio.vulns
                    ident = self.path.rsplit('/', 1)[1]
                    return (200, json.dumps(servicio.avisos[ident]).encode()) if ident in servicio.avisos else (404, b'{}')
                return 404, b'{}'

            def hacer(self):
                largo = int(self.headers.get('Content-Length') or 0)
                cuerpo = json.loads(self.rfile.read(largo)) if largo else None
                respuesta = self.atender(cuerpo)
                if respuesta is None:
                    self.close_connection = True
                    return
                self.responder(*respuesta)

            do_GET = do_POST = hacer

        self.servidor = ThreadingHTTPServer(('127.0.0.1', 0), Manejador)
        threading.Thread(target=self.servidor.serve_forever, daemon=True).start()
        self.url = f'http://127.0.0.1:{self.servidor.server_port}'

    def cerrar(self):
        self.servidor.shutdown()
        self.servidor.server_close()

    def consultas(self):
        """Los pares (nombre, versión) pedidos a querybatch, en orden."""
        return [(q['package']['name'], q['version']) for c, p, cuerpo in self.pedidos if p == '/v1/querybatch' for q in cuerpo['queries']]


class Osv(unittest.TestCase):
    setUp, escribe, git, salida = (_archivo.Archivo.setUp, _archivo.Archivo.escribe, _archivo.Archivo.git, _archivo.Archivo.salida)

    def guarda(self, cambio='20260101-000000-aaa-uno', candidato='abc1234', componentes=(('alfa', '1.2.3'),)):
        """Un inventario de procedencia guardado, como lo deja «procedencia ID»."""
        ruta = self.root / '.factory/cambios' / cambio / 'candidatos' / candidato / 'procedencia/cyclonedx.json'
        ruta.parent.mkdir(parents=True)
        ruta.write_text(json.dumps({'bomFormat': 'CycloneDX', 'components': [
            {'type': 'library', 'name': n, 'version': v} for n, v in componentes]}))

    def servicio(self, **kw):
        s = Servicio(**kw)
        self.addCleanup(s.cerrar)
        return s

    def correr(self, s, **kw):
        args = dict(id=None, python=None, json=False, buscar=None, auditar=False, avisos=None,
                    consultar_osv=True, red=True, salida=None, osv_url=s.url)
        args.update(kw)
        import argparse
        self.salida()
        f.comando_procedencia(argparse.Namespace(**args))
        return self.salida()

    def local(self):
        base = self.root / '.factory/local'
        return sorted(p.name for p in base.iterdir()) if base.exists() else []

    def falla(self, s, texto=None, **kw):
        with self.assertRaises(f.FactoryError) as cm:
            self.correr(s, **kw)
        self.assertEqual(self.salida(), '')
        if texto:
            self.assertIn(texto, str(cm.exception))
        return str(cm.exception)


class SinAutorizacion(Osv):
    def test_ao1_sin_la_bandera_de_red_no_se_abre_ninguna_conexion_ni_se_crea_archivo(self):
        self.guarda()
        s = self.servicio(avisos=[aviso()], por_dependencia={('alfa', '1.2.3'): ['GHSA-aaaa']})
        self.falla(s, '--red', red=False)
        self.assertEqual(s.pedidos, [])
        self.assertEqual(self.local(), [])

    def test_ao1_sin_la_bandera_tampoco_se_conecta_a_un_servidor_que_no_existe(self):
        self.guarda()
        s = self.servicio()
        self.falla(s, '--red', red=False, osv_url='http://127.0.0.1:9')

    def test_ao1_la_bandera_de_red_sola_no_consulta_nada(self):
        self.guarda()
        s = self.servicio()
        self.falla(s, '--consultar-osv', consultar_osv=False, red=True)
        self.assertEqual(s.pedidos, [])

    def test_ao1_salida_sin_consultar_es_un_error(self):
        self.guarda()
        s = self.servicio()
        self.falla(s, '--consultar-osv', consultar_osv=False, red=False, salida='x.json')
        self.assertEqual(s.pedidos, [])

    def test_ao1_no_se_combina_con_auditar_buscar_avisos_ni_un_cambio(self):
        self.guarda()
        s = self.servicio()
        for kw in ({'auditar': True}, {'buscar': 'alfa'}, {'avisos': 'a.json'}, {'id': '20260101-000000-aaa-uno'}):
            with self.subTest(kw=kw):
                self.falla(s, 'no se combina', **kw)
        self.assertEqual(s.pedidos, [])


class ConsultaGuardaYAudita(Osv):
    def test_ao2_una_dependencia_afectada_se_guarda_como_aviso_valido_y_nombra_al_candidato(self):
        self.guarda()
        s = self.servicio(avisos=[aviso(arreglo='1.2.4')], por_dependencia={('alfa', '1.2.3'): ['GHSA-aaaa']})
        salida = self.correr(s)
        guardado = json.loads((self.root / '.factory/local/avisos-osv.json').read_text())
        self.assertEqual([a['id'] for a in guardado], ['GHSA-aaaa'])
        f.procedencia_mod.avisos(json.dumps(guardado), 'guardado')  # OSV válido para el auditor local
        self.assertIn('Afectados:', salida)
        self.assertIn('GHSA-aaaa: alfa 1.2.3 (corregida en: 1.2.4)', salida)
        self.assertIn('20260101-000000-aaa-uno · candidato abc1234', salida)
        self.assertEqual(self.local(), ['avisos-osv.json'])  # y ningún temporal

    def test_ao2_sale_solo_nombre_version_y_ecosistema_de_cada_dependencia_distinta_una_vez(self):
        self.guarda('20260101-000000-aaa-uno', 'abc1234', (('alfa', '1.2.3'), ('Beta_X', '2.0')))
        self.guarda('20260102-000000-bbb-dos', 'def5678', (('alfa', '1.2.3'), ('beta-x', '2.0'), ('gamma', '0.1')))
        s = self.servicio()
        self.correr(s)
        self.assertEqual(sorted(s.consultas()), [('Beta_X', '2.0'), ('alfa', '1.2.3'), ('gamma', '0.1')])
        cuerpos = [c for _, p, c in s.pedidos if p == '/v1/querybatch']
        self.assertEqual(len(cuerpos), 1)
        self.assertEqual(set(cuerpos[0]), {'queries'})
        for q in cuerpos[0]['queries']:
            self.assertEqual(set(q), {'package', 'version'})
            self.assertEqual(set(q['package']), {'name', 'ecosystem'})
            self.assertEqual(q['package']['ecosystem'], 'PyPI')
        self.assertEqual([m for m, _, _ in s.pedidos], ['POST'])

    def test_ao2_sin_avisos_dice_cuantas_consulto_y_no_guarda_archivo(self):
        self.guarda(componentes=(('alfa', '1.2.3'), ('beta', '2.0')))
        s = self.servicio()
        salida = self.correr(s)
        self.assertIn('2 dependencia(s) distinta(s)', salida)
        self.assertIn('no hay candidatos expuestos', salida)
        self.assertEqual(self.local(), [])
        self.assertEqual([p for _, p, _ in s.pedidos], ['/v1/querybatch'])

    def test_ao2_sin_avisos_en_json_es_una_auditoria_vacia(self):
        self.guarda()
        s = self.servicio()
        datos = json.loads(self.correr(s, json=True))
        self.assertEqual((datos['avisos'], datos['afectados'], datos['dependencias']), (0, [], 1))

    def test_ao2_un_aviso_de_otra_version_se_guarda_y_no_expone_a_nadie(self):
        self.guarda()
        s = self.servicio(avisos=[aviso(versiones=('9.9.9',))], por_dependencia={('alfa', '1.2.3'): ['GHSA-aaaa']})
        salida = self.correr(s)
        self.assertIn('No hay candidatos afectados.', salida)
        self.assertEqual(self.local(), ['avisos-osv.json'])

    def test_ao2_la_version_corregida_se_consulta_sin_su_sufijo(self):
        self.guarda(componentes=(('alfa', '1.2.3+rhlw1'),))
        s = self.servicio()
        self.correr(s)
        self.assertEqual(s.consultas(), [('alfa', '1.2.3')])

    def test_ao2_un_aviso_que_alcanza_a_dos_dependencias_se_baja_una_vez(self):
        self.guarda(componentes=(('alfa', '1.2.3'), ('beta', '2.0')))
        s = self.servicio(avisos=[aviso(versiones=('1.2.3', '2.0'))],
                          por_dependencia={('alfa', '1.2.3'): ['GHSA-aaaa'], ('beta', '2.0'): ['GHSA-aaaa']})
        self.correr(s)
        self.assertEqual([p for _, p, _ in s.pedidos if p.startswith('/v1/vulns/')], ['/v1/vulns/GHSA-aaaa'])

    def test_ao2_el_identificador_del_aviso_se_escapa_en_la_ruta(self):
        self.guarda()
        s = self.servicio(avisos=[aviso('A/../B')], por_dependencia={('alfa', '1.2.3'): ['A/../B']})
        s.avisos['A%2F..%2FB'] = s.avisos.pop('A/../B')
        self.correr(s)
        self.assertEqual([p for _, p, _ in s.pedidos if p.startswith('/v1/vulns/')], ['/v1/vulns/A%2F..%2FB'])

    def test_ao2_muchas_dependencias_se_consultan_en_lotes(self):
        self.guarda(componentes=[(f'p{i}', '1.0') for i in range(5)])
        s = self.servicio()
        with mock.patch.object(osv, 'LOTE', 2):
            self.correr(s)
        tamanos = [len(c['queries']) for _, p, c in s.pedidos if p == '/v1/querybatch']
        self.assertEqual(tamanos, [2, 2, 1])

    def test_ao2_la_salida_indicada_se_respeta_y_la_de_por_omision_no_se_crea(self):
        self.guarda()
        s = self.servicio(avisos=[aviso()], por_dependencia={('alfa', '1.2.3'): ['GHSA-aaaa']})
        self.correr(s, salida=str(self.root / 'otro/avisos.json'))
        self.assertTrue((self.root / 'otro/avisos.json').is_file())
        self.assertEqual(self.local(), [])

    def test_ao2_con_avisos_el_json_tambien_dice_cuantas_dependencias_se_consultaron(self):
        self.guarda(componentes=(('alfa', '1.2.3'), ('beta', '2.0')))
        s = self.servicio(avisos=[aviso()], por_dependencia={('alfa', '1.2.3'): ['GHSA-aaaa']})
        datos = json.loads(self.correr(s, json=True))
        self.assertEqual((datos['dependencias'], datos['avisos'], len(datos['afectados'])), (2, 1, 1))

    def test_ao2_el_archivo_guardado_se_audita_despues_con_auditar(self):
        self.guarda()
        s = self.servicio(avisos=[aviso()], por_dependencia={('alfa', '1.2.3'): ['GHSA-aaaa']})
        self.correr(s)
        despues = self.correr(s, consultar_osv=False, red=False, auditar=True, avisos=str(self.root / '.factory/local/avisos-osv.json'))
        self.assertIn('GHSA-aaaa: alfa 1.2.3', despues)


class UnFalloNoEsLimpio(Osv):
    def verifica(self, s, texto=None):
        mensaje = self.falla(s, texto)
        self.assertNotIn('no hay candidatos', mensaje.lower())
        self.assertEqual(self.local(), [])

    def test_ao3_un_error_http_en_querybatch(self):
        self.guarda()
        self.verifica(self.servicio(batch=(500, b'{}')), 'HTTP 500')

    def test_ao3_un_error_http_al_bajar_un_aviso_no_deja_archivo(self):
        self.guarda()
        self.verifica(self.servicio(por_dependencia={('alfa', '1.2.3'): ['GHSA-aaaa']}, vulns=(503, b'{}')), 'HTTP 503')

    def test_ao3_una_conexion_cortada(self):
        self.guarda()
        self.verifica(self.cortado(), 'no pude consultar')

    def cortado(self):
        s = self.servicio()
        s.servidor.RequestHandlerClass.atender = lambda self, cuerpo: None
        return s

    def test_ao3_una_respuesta_que_no_es_json(self):
        self.guarda()
        self.verifica(self.servicio(batch=(200, b'<html>no soy json</html>')), 'no pude consultar')

    def test_ao3_una_respuesta_demasiado_grande(self):
        self.guarda()
        with mock.patch.object(osv, 'TOPE', 10):
            self.verifica(self.servicio(batch=(200, json.dumps({'results': [{}]}).encode())), 'demasiado grande')

    def test_ao3_una_respuesta_que_no_es_utf8(self):
        self.guarda()
        self.verifica(self.servicio(batch=(200, b'\xff\xfe\xfa')), 'no pude consultar')

    def test_ao3_querybatch_con_otra_cantidad_de_resultados(self):
        self.guarda(componentes=(('alfa', '1.2.3'), ('beta', '2.0')))
        self.verifica(self.servicio(batch=(200, json.dumps({'results': [{}]}).encode())), 'querybatch')

    def test_ao3_querybatch_con_avisos_sin_identificador(self):
        self.guarda()
        self.verifica(self.servicio(batch=(200, json.dumps({'results': [{'vulns': [{'modified': 'x'}]}]}).encode())), 'sin identificador')

    def test_ao3_un_aviso_que_no_es_osv_valido(self):
        self.guarda()
        self.verifica(self.servicio(por_dependencia={('alfa', '1.2.3'): ['MALO']}, avisos=[{'id': 'MALO', 'affected': []}]), 'OSV válido')

    def test_ao3_el_servicio_no_esta(self):
        self.guarda()
        s = self.servicio()
        self.falla(s, 'no pude consultar', osv_url='http://127.0.0.1:9')
        self.assertEqual(self.local(), [])

    def test_ao3_una_url_que_no_es_http_se_rechaza_sin_leer_archivos(self):
        self.guarda()
        s = self.servicio()
        self.falla(s, 'http o https', osv_url='file:///etc/passwd')
        self.assertEqual(s.pedidos, [])

    def test_ao3_inventarios_sin_dependencias_no_se_dan_por_limpios_ni_se_conecta(self):
        self.guarda(componentes=())
        s = self.servicio()
        mensaje = self.falla(s, 'nada que consultar')
        self.assertNotIn('no hay candidatos expuestos', mensaje)
        self.assertEqual(s.pedidos, [])
        self.assertEqual(self.local(), [])

    def test_ao3_una_redireccion_no_se_sigue_hacia_otro_servidor(self):
        self.guarda()
        otro = self.servicio()
        s = self.servicio(batch=(302, b'', {'Location': otro.url + '/v1/querybatch'}))
        self.falla(s, 'HTTP 302')
        self.assertEqual(otro.pedidos, [])
        self.assertEqual(self.local(), [])

    def test_ao3_un_identificador_de_aviso_vacio_se_rechaza_sin_pedir_la_raiz(self):
        self.guarda()
        s = self.servicio(batch=(200, json.dumps({'results': [{'vulns': [{'id': ''}]}]}).encode()))
        self.falla(s, 'sin identificador')
        self.assertEqual([p for _, p, _ in s.pedidos], ['/v1/querybatch'])

    def test_ao3_un_archivo_de_avisos_de_solo_lectura_no_se_reemplaza(self):
        self.guarda()
        previo = self.root / '.factory/local/avisos-osv.json'
        previo.parent.mkdir(parents=True, exist_ok=True)
        previo.write_text('[{"previo": true}]')
        previo.chmod(0o444)
        s = self.servicio(avisos=[aviso()], por_dependencia={('alfa', '1.2.3'): ['GHSA-aaaa']})
        if os.access(previo, os.W_OK):
            self.skipTest('el usuario escribe igual en archivos de sólo lectura')
        self.falla(s, 'sólo lectura')
        self.assertEqual(previo.read_text(), '[{"previo": true}]')
        self.assertEqual(s.pedidos, [])

    def test_ao3_una_salida_fuera_del_proyecto_se_rechaza_antes_de_conectar(self):
        self.guarda()
        s = self.servicio(avisos=[aviso()], por_dependencia={('alfa', '1.2.3'): ['GHSA-aaaa']})
        fuera = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, fuera, True)
        real = fuera / 'real'
        real.mkdir()
        (fuera / 'enlace').symlink_to(real)
        for salida in (fuera / 'avisos.json', fuera / 'enlace' / 'avisos.json', fuera / 'enlace' / 'sub' / 'avisos.json',
                       self.root / '..' / 'afuera.json', '/tmp/otro-avisos.json'):
            with self.subTest(salida=str(salida)):
                self.falla(s, 'dentro del proyecto', salida=str(salida))
        self.assertEqual(list(real.iterdir()), [])
        self.assertEqual(s.pedidos, [])

    def test_ao3_una_salida_dentro_del_proyecto_con_un_ancestro_enlazado_se_rechaza(self):
        self.guarda()
        s = self.servicio(avisos=[aviso()], por_dependencia={('alfa', '1.2.3'): ['GHSA-aaaa']})
        fuera = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, fuera, True)
        (self.root / 'enlace').symlink_to(fuera)
        self.falla(s, 'enlaces simbólicos', salida=str(self.root / 'enlace' / 'sub' / 'avisos.json'))
        self.assertEqual(list(fuera.iterdir()), [])
        self.assertEqual(s.pedidos, [])

    def test_ao3_la_url_invalida_se_rechaza_antes_de_leer_los_inventarios(self):
        s = self.servicio()  # sin inventarios guardados: si se leyeran primero, el error sería otro
        self.falla(s, 'http o https', osv_url='ftp://x')

    def test_ao3_si_no_se_puede_escribir_es_un_error_claro_y_no_queda_nada(self):
        self.guarda()
        s = self.servicio(avisos=[aviso()], por_dependencia={('alfa', '1.2.3'): ['GHSA-aaaa']})
        with mock.patch.object(osv.tempfile, 'mkstemp', side_effect=PermissionError('sin permiso')):
            self.falla(s, 'no pude guardar')
        self.assertEqual(self.local(), [])

    def test_ao3_el_guardado_es_atomico_un_fallo_al_reemplazar_deja_lo_anterior_y_ningun_temporal(self):
        self.guarda()
        previo = self.root / '.factory/local/avisos-osv.json'
        previo.parent.mkdir(parents=True, exist_ok=True)
        previo.write_text('[{"previo": true}]')
        s = self.servicio(avisos=[aviso()], por_dependencia={('alfa', '1.2.3'): ['GHSA-aaaa']})
        with mock.patch.object(osv.os, 'replace', side_effect=OSError('disco lleno')):
            self.falla(s, 'no pude guardar')
        self.assertEqual(previo.read_text(), '[{"previo": true}]')
        self.assertEqual(self.local(), ['avisos-osv.json'])

    def test_ao3_sin_inventarios_guardados_no_hay_nada_que_consultar_ni_conexion(self):
        s = self.servicio()
        self.falla(s, 'nada que consultar')
        self.assertEqual(s.pedidos, [])

    def test_ao3_un_fallo_no_toca_un_archivo_de_avisos_anterior(self):
        self.guarda()
        previo = self.root / '.factory/local/avisos-osv.json'
        previo.parent.mkdir(parents=True, exist_ok=True)
        previo.write_text('[{"previo": true}]')
        self.falla(self.servicio(batch=(500, b'{}')), 'HTTP 500')
        self.assertEqual(previo.read_text(), '[{"previo": true}]')
        self.assertEqual(self.local(), ['avisos-osv.json'])

    def test_ao3_no_se_escribe_a_traves_de_un_enlace_simbolico(self):
        self.guarda()
        s = self.servicio(avisos=[aviso()], por_dependencia={('alfa', '1.2.3'): ['GHSA-aaaa']})
        (self.root / '.factory/local').mkdir(parents=True, exist_ok=True)
        destino = self.root / 'afuera.json'
        (self.root / '.factory/local/avisos-osv.json').symlink_to(destino)
        self.falla(s, 'enlaces simbólicos')
        self.assertFalse(destino.exists())
        self.assertEqual(s.pedidos, [])

    def test_ao3_una_salida_que_es_una_carpeta_se_rechaza_antes_de_conectar(self):
        self.guarda()
        s = self.servicio()
        self.falla(s, 'no escribo', salida=str(self.root))
        self.assertEqual(s.pedidos, [])


if __name__ == '__main__':
    unittest.main()
