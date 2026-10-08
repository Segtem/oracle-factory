"""Producir en la carpeta del candidato y preparar la revisión desde los revisores: escenarios p1–p4 de la spec."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_archivo as _archivo  # noqa: E402

f = _archivo.f
AYUDANTES = ('setUp', 'escribe', 'git', 'salida', 'archivos')


class Base(unittest.TestCase):
    pass


for _nombre in AYUDANTES:  # el fixture de archivo, sin heredar sus pruebas
    setattr(Base, _nombre, getattr(_archivo.Archivo, _nombre))


def informe_clue(head, hallazgos=(), proveedor='codex', modelo='gpt-x', estado='completo'):
    return {'schema_version': 'oracle-clue.review/v1', 'repo': '/no/existe', 'base': '0' * 40, 'head': head,
            'diff_sha256': 'd' * 64, 'context_sha256': 'c' * 64, 'provider': {'name': proveedor, 'model': modelo},
            'findings': [{'id': i, 'kind': 'bug', 'severity': 'baja', 'confidence': 0.8, 'title': f'Título {i}',
                          'explanation': 'Explicación.', 'location': {'file': 'examples/notas/notas.py', 'start_line': 3,
                                                                      'end_line': 3, 'side': 'head'},
                          'trigger': 't', 'evidence': f'Lo reproduje ({i}).', 'related_requirement': 'r', 'status': 'pendiente',
                          'verification': 'v'} for i in hallazgos],
            'review_status': estado, 'limitations': [f'Límite de {proveedor}.']}


class Autoproduccion(Base):
    def cambio_medido(self):
        ident = f.nuevo('Nota', con_ejemplo='notas')
        with self.escribe('1'):
            f.aprobar_spec(ident)
        f.importar(ident)
        rid = f.leer(ident)[1]['requisitos'][0]
        f.medir(ident, requisito_id=rid, medidas=['notas.casos_ejecutados', 'notas.resultados'], quitar_sin_medir=True)
        self.git('add', '.')
        self.git('commit', '-qm', 'producto')
        return ident

    def head(self):
        return self.git('rev-parse', 'HEAD')

    def carpeta(self, ident, sha=None):
        return self.root / '.factory/cambios' / ident / 'candidatos' / (sha or self.head()[:7])

    def producir_evidencia(self, ident):
        destino = self.carpeta(ident) / 'evidencia'
        subprocess.run([sys.executable, 'examples/notas/sensor.py', '--salida', destino / 'hechos.json'], cwd=self.root,
                       check=True, capture_output=True)
        (destino / 'resultado.json').write_text(json.dumps({'exitoso': True, 'tests': 3, 'casos_contrato': 3,
                                                            'limites': 'Sólo el ejemplo de notas.'}))
        return destino / 'hechos.json'

    def preparar(self):
        salida, errores = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(errores):
            informe, decisiones = f.preparar_revision(self.ident)
        return json.loads(informe.read_text()), json.loads(decisiones.read_text()), errores.getvalue()

    # --- p1: juzgar encuentra la evidencia del candidato ----------------------------------------------------------------
    def test_p1_evidencia_en_la_carpeta_del_candidato(self):
        ident = self.cambio_medido()
        candidato = self.head()[:7]
        self.producir_evidencia(ident)
        self.git('add', '.')
        self.git('commit', '-qm', 'evidencia')  # HEAD avanza, el producto no cambia
        hechos = f.hechos_del_candidato(ident)
        self.assertEqual(hechos, self.carpeta(ident, candidato) / 'evidencia' / 'hechos.json')
        with contextlib.redirect_stdout(io.StringIO()):
            f.juzgar(ident, hechos)
        self.assertEqual(f.leer(ident)[1]['oracle']['hechos'],
                         f'.factory/cambios/{ident}/candidatos/{candidato}/evidencia/hechos.json')

    def test_p1_sin_evidencia_falla_sin_registrar(self):
        ident = self.cambio_medido()
        antes = f.ruta_registro(f.leer(ident)[0]).read_bytes()
        with self.assertRaises(f.FactoryError) as error:
            f.hechos_del_candidato(ident)
        self.assertIn(f'.factory/cambios/{ident}/candidatos/{self.head()[:7]}/evidencia/hechos.json', str(error.exception))
        self.assertEqual(f.ruta_registro(f.leer(ident)[0]).read_bytes(), antes)

    def test_p1_un_cambio_de_producto_deja_viejo_al_candidato(self):
        ident = self.cambio_medido()
        self.producir_evidencia(ident)
        self.git('add', '.')
        self.git('commit', '-qm', 'evidencia')
        (self.root / 'examples/notas/notas.py').write_text('# otro producto\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'cambio de producto')
        self.assertIsNone(f.candidato_vigente(ident))
        with self.assertRaises(f.FactoryError):
            f.hechos_del_candidato(ident)

    def test_p1_un_cambio_local_sin_commit_deja_viejo_al_candidato(self):
        ident = self.cambio_medido()
        self.producir_evidencia(ident)
        self.git('add', '.')
        self.git('commit', '-qm', 'evidencia')
        self.assertIsNotNone(f.candidato_vigente(ident))
        notas = self.root / 'examples/notas/notas.py'
        notas.write_text(notas.read_text() + '# edición local\n')  # sin commit
        self.assertIsNone(f.candidato_vigente(ident))
        notas.write_text(notas.read_text().replace('# edición local\n', ''))
        (self.root / 'nuevo_modulo.py').write_text('x = 1\n')  # archivo nuevo del producto, sin commit
        self.assertIsNone(f.candidato_vigente(ident))

    def test_p1_muchos_commits_que_no_tocan_el_producto(self):
        ident = self.cambio_medido()
        candidato = self.head()[:7]
        self.producir_evidencia(ident)
        self.git('add', '.')
        self.git('commit', '-qm', 'evidencia')
        for i in range(205):
            self.git('commit', '-q', '--allow-empty', '-m', f'vacío {i}')
        self.assertEqual(f.candidato_vigente(ident), candidato)

    def test_p5_init_avisa_de_paquetes_de_clue_versionados(self):
        viejo = self.root / '.factory/cambios/20250101-000000-x/candidatos/abc1234/clue/paquete.json'
        viejo.parent.mkdir(parents=True)
        viejo.write_text('{}')
        self.git('add', '-f', str(viejo))
        errores = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(errores):
            f.inicializar()
        self.assertIn('git rm -r --cached .factory/cambios/20250101-000000-x/candidatos/abc1234/clue', errores.getvalue())
        self.assertIn(str(viejo.relative_to(self.root)), self.git('ls-files'))  # init no toca el índice

    # --- p2: revision-preparar arma el informe desde los revisores --------------------------------------------------------
    def test_p2_dos_informes_de_revisores(self):
        informe, _, _ = self._dos_informes()
        self.assertEqual([h['id'] for h in informe['hallazgos']], ['R-01', 'R-02'])
        self.assertEqual(informe['hallazgos'][0]['ubicacion'], 'examples/notas/notas.py:3')
        self.assertIn('codex (gpt-x)', informe['hallazgos'][0]['evidencia'])
        self.assertEqual(informe['comprobaciones'][0]['resultado'], 'cumple')  # la evidencia del candidato
        self.assertEqual(len(informe['comprobaciones']), 3)  # evidencia + un revisor + otro
        self.assertIn('codex (gpt-x): Límite de codex.', informe['limites'])
        self.assertEqual(informe['archivos_revisados'], ['examples/notas/notas.py', 'examples/notas/sensor.py'])
        self.assertIsNone(informe['revisor'])  # lo que es de la persona queda vacío
        self.assertIsNone(informe['completa'])

    def _dos_informes(self, clue=None):
        with contextlib.nullcontext() if clue == 'externo' else patch.object(f.shutil, 'which', return_value=None):
            # el head del candidato se conoce recién al hacer el commit del producto: se arma en dos pasos
            self.ident = self.cambio_medido()
            head = self.head()
            carpeta = self.carpeta(self.ident)
            self.producir_evidencia(self.ident)
            (carpeta / 'revision').mkdir(parents=True)
            (carpeta / 'revision' / 'a.json').write_text(json.dumps(informe_clue(head, ['R-01', 'R-02'])))
            (carpeta / 'revision' / 'b.json').write_text(json.dumps(informe_clue(head, [], 'agy', 'gemini')))
            (carpeta / 'clue').mkdir()
            (carpeta / 'clue' / 'paquete.json').write_text(json.dumps({
                'schema_version': 'oracle-clue.bundle/v1', 'repo': '/no/existe', 'diff_sha256': 'd' * 64, 'context_sha256': 'c' * 64,
                'files': [{'file': 'examples/notas/notas.py'}, {'file': 'examples/notas/sensor.py'}]}))
            self.git('add', '.')
            self.git('commit', '-qm', 'evidencia e informes')
            return self.preparar()

    # --- p3: el borrador de decisiones no decide ----------------------------------------------------------------------------
    def test_p3_registrar_sin_decidir_se_rechaza(self):
        informe, decisiones, _ = self._dos_informes()
        self.assertEqual([d['estado'] for d in decisiones['decisiones']], [None, None])
        carpeta = sorted((self.root / 'tareas' / self.ident / 'revisiones').glob('preparacion-*'))[-1]
        informe.update(revisor='Persona fixture', completa=True)
        (carpeta / 'informe.json').write_text(json.dumps(informe))
        import hashlib
        decisiones.update(informe_sha256=hashlib.sha256((carpeta / 'informe.json').read_bytes()).hexdigest(),
                          actor='Persona fixture', motivo='fixture')
        (carpeta / 'decisiones.json').write_text(json.dumps(decisiones))
        antes = f.ruta_registro(f.leer(self.ident)[0]).read_bytes()
        with self.escribe('1'), self.assertRaises(f.FactoryError), \
                contextlib.redirect_stdout(io.StringIO()):
            f.revisar_guiado(self.ident, carpeta / 'informe.json', carpeta / 'decisiones.json', 'Persona fixture', 'aprobar')
        self.assertEqual(f.ruta_registro(f.leer(self.ident)[0]).read_bytes(), antes)

    # --- p4: los informes se validan o se marcan ----------------------------------------------------------------------------
    def test_p4_informe_de_otro_candidato_no_se_usa(self):
        with patch.object(f.shutil, 'which', return_value=None):
            self.ident = self.cambio_medido()
            carpeta = self.carpeta(self.ident)
            self.producir_evidencia(self.ident)
            (carpeta / 'revision').mkdir(parents=True)
            (carpeta / 'revision' / 'viejo.json').write_text(json.dumps(informe_clue('f' * 40, ['V-01'])))
            informe, _, avisos = self.preparar()
        self.assertEqual(informe['hallazgos'], [])
        self.assertIn('es de otro candidato', avisos)

    def test_p4_sin_clue_se_usa_marcado(self):
        informe, _, _ = self._dos_informes()
        self.assertIn('sin validar: oracle-clue no está instalado', informe['hallazgos'][0]['evidencia'])

    def test_p4_con_clue_y_sin_checkout_no_se_usa(self):
        with patch.object(f.shutil, 'which', return_value='/usr/bin/oracle-clue'):
            informe, _, _ = self._dos_informes('externo')  # el repo del paquete (/no/existe) no está en esta máquina
        self.assertEqual(informe['hallazgos'], [])

    def test_p4_un_informe_que_no_pasa_clue_no_se_usa(self):
        real = f.ejecutar

        def clue(argv, *a, **k):
            if argv[1:2] == ['validar']:
                return subprocess.CompletedProcess(argv, 1, '', 'CLUE: ubicación fuera del diff')
            return real(argv, *a, **k)

        # el checkout del paquete existe (el propio proyecto) y Clue rechaza el informe
        self.ident = self.cambio_medido()
        head = self.head()
        carpeta = self.carpeta(self.ident)
        self.producir_evidencia(self.ident)
        (carpeta / 'revision').mkdir(parents=True)
        datos = informe_clue(head, ['X-01'])
        datos['repo'] = str(self.root)
        (carpeta / 'revision' / 'a.json').write_text(json.dumps(datos))
        (carpeta / 'clue').mkdir()
        (carpeta / 'clue' / 'paquete.json').write_text(json.dumps({'schema_version': 'oracle-clue.bundle/v1', 'repo': str(self.root),
                                                                 'diff_sha256': 'd' * 64, 'context_sha256': 'c' * 64, 'files': []}))
        with patch.object(f.shutil, 'which', return_value='/usr/bin/oracle-clue'), patch.object(f, 'ejecutar', clue):
            informe, _, avisos = self.preparar()
        self.assertEqual(informe['hallazgos'], [])
        self.assertIn('no pasa la validación de Clue', avisos)


if __name__ == '__main__':
    unittest.main()
