"""La evidencia no dice más de lo que prueba: la preparación no da por buena evidencia contradictoria (eh1), `estado` avisa del código
que Git ignora (eh2) y el inventario lista lo instalado fuera del lock (eh3)."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_archivo as _archivo  # noqa: E402
import test_procedencia as _proc  # noqa: E402
from oracle_factory import flujo_revision, preparacion  # noqa: E402

f = _archivo.f
SOURCE = Path(__file__).resolve().parents[1]
CANDIDATO = 'a' * 40
BASE = {'revisor': None, 'completa': None, 'archivos_revisados': None, 'comprobaciones': None, 'limites': None,
        'hallazgos': None, 'sin_hallazgos_motivo': None}


def evidencia_en(carpeta: Path, **cambios) -> dict:
    """Una carpeta de evidencia como la que escribe tools/verificar_cambio.py, con su resultado.json; `cambios` lo altera."""
    carpeta.mkdir(parents=True, exist_ok=True)
    for n in ('suite.txt', 'hechos.json', 'trazabilidad.json'):
        (carpeta / n).write_text(f'{n}\n', encoding='utf-8')
    resultado = {'exitoso': True, 'tests': 5, 'casos_contrato': 2, 'casos_exactos_sin_omisiones_duplicados_ni_fallas': True,
                 'fuentes_estables': True, 'origen': {'head': CANDIDATO, 'sha256': {}, 'mtime_ns': {}},
                 'limites': 'Casos derivados de los nombres de las pruebas.',
                 'artefactos_sha256': {n: hashlib.sha256((carpeta / n).read_bytes()).hexdigest() for n in ('suite.txt', 'hechos.json', 'trazabilidad.json')}}
    resultado.update(cambios)
    (carpeta / 'resultado.json').write_text(json.dumps(resultado), encoding='utf-8')
    return resultado


def preparar(carpeta: Path, resultado: dict, candidato: str = CANDIDATO[:7]) -> dict:
    evidencia = {'ruta': 'ev/resultado.json', 'resultado': resultado, 'candidato': candidato,
                 'artefactos': flujo_revision.artefactos_de(carpeta, resultado)}
    informe, _ = preparacion.completar(BASE, {'decisiones': None}, [], evidencia, [])
    [comprobacion] = [c for c in informe['comprobaciones'] if c['evidencia'] == 'ev/resultado.json']
    return {'comprobacion': comprobacion, 'limites': informe['limites']}


class EvidenciaEh1(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.carpeta = Path(self.tmp.name) / 'evidencia'

    def test_eh1_cero_pruebas_y_fuentes_inestables(self):
        r = preparar(self.carpeta, evidencia_en(self.carpeta, tests=0, fuentes_estables=False))
        self.assertEqual(r['comprobacion']['resultado'], 'falla')
        self.assertIn('tests', r['comprobacion']['descripcion'])
        self.assertIn('fuentes_estables', r['comprobacion']['descripcion'])
        for malo in ('5', True, -1, None):  # un número que no es entero positivo también se contradice con el éxito
            r = preparar(self.carpeta, evidencia_en(self.carpeta, tests=malo))
            self.assertEqual(r['comprobacion']['resultado'], 'falla', malo)
        r = preparar(self.carpeta, evidencia_en(self.carpeta, fuentes_estables='true'))  # sólo true es true
        self.assertEqual(r['comprobacion']['resultado'], 'falla')
        r = preparar(self.carpeta, evidencia_en(self.carpeta, casos_exactos_sin_omisiones_duplicados_ni_fallas=False))
        self.assertEqual(r['comprobacion']['resultado'], 'falla')
        self.assertIn('casos_exactos_sin_omisiones_duplicados_ni_fallas', r['comprobacion']['descripcion'])

    def test_eh1_un_artefacto_con_otro_hash(self):
        resultado = evidencia_en(self.carpeta)
        (self.carpeta / 'hechos.json').write_text('{"otros": "hechos"}\n', encoding='utf-8')
        r = preparar(self.carpeta, resultado)
        self.assertEqual(r['comprobacion']['resultado'], 'falla')
        self.assertIn('hechos.json', r['comprobacion']['descripcion'])
        (self.carpeta / 'hechos.json').unlink()  # un artefacto que falta, también
        r = preparar(self.carpeta, resultado)
        self.assertEqual(r['comprobacion']['resultado'], 'falla')
        self.assertIn('hechos.json no está', r['comprobacion']['descripcion'])
        fuera = self.carpeta.parent / 'fuera.txt'  # fuera de la carpeta, aunque el hash coincida, no cuenta
        fuera.write_text('x\n')
        r = preparar(self.carpeta, evidencia_en(self.carpeta, artefactos_sha256={'../fuera.txt': hashlib.sha256(b'x\n').hexdigest()}))
        self.assertEqual(r['comprobacion']['resultado'], 'falla')
        r = preparar(self.carpeta, evidencia_en(self.carpeta, artefactos_sha256={str(fuera): hashlib.sha256(b'x\n').hexdigest()}))  # ni absoluta
        self.assertEqual(r['comprobacion']['resultado'], 'falla')
        (self.carpeta / 'real').mkdir()  # un enlace en una carpeta intermedia tampoco se sigue, aunque apunte adentro
        (self.carpeta / 'real' / 'a.txt').write_text('x\n')
        (self.carpeta / 'alias').symlink_to(self.carpeta / 'real')
        r = preparar(self.carpeta, evidencia_en(self.carpeta, artefactos_sha256={'alias/a.txt': hashlib.sha256(b'x\n').hexdigest()}))
        self.assertEqual(r['comprobacion']['resultado'], 'falla')
        r = preparar(self.carpeta, evidencia_en(self.carpeta, artefactos_sha256={'real/a.txt': hashlib.sha256(b'x\n').hexdigest()}))
        self.assertEqual(r['comprobacion']['resultado'], 'cumple')  # la misma ruta sin enlace, sí
        r = preparar(self.carpeta, evidencia_en(self.carpeta, artefactos_sha256={}))  # declarar que no hay artefactos no es coherente
        self.assertEqual(r['comprobacion']['resultado'], 'falla')

    def test_eh1_otro_head(self):
        r = preparar(self.carpeta, evidencia_en(self.carpeta, origen={'head': 'b' * 40}))
        self.assertEqual(r['comprobacion']['resultado'], 'falla')
        self.assertIn('bbbbbbb', r['comprobacion']['descripcion'])
        self.assertIn('aaaaaaa', r['comprobacion']['descripcion'])

    def test_eh1_evidencia_coherente(self):
        r = preparar(self.carpeta, evidencia_en(self.carpeta))
        self.assertEqual(r['comprobacion']['resultado'], 'cumple')
        self.assertNotIn('contradic', r['comprobacion']['descripcion'])
        self.assertFalse([l for l in r['limites'] if 'declarado por el sensor' in l])
        r = preparar(self.carpeta, evidencia_en(self.carpeta, exitoso=False))  # un fracaso declarado sigue siendo «falla», como siempre
        self.assertEqual(r['comprobacion']['resultado'], 'falla')

    def test_eh1_solo_exitoso(self):
        self.carpeta.mkdir()
        r = preparar(self.carpeta, {'exitoso': True})
        self.assertEqual(r['comprobacion']['resultado'], 'cumple')
        self.assertTrue([l for l in r['limites'] if 'éxito declarado por el sensor; Factory no pudo comprobar su coherencia' in l], r['limites'])
        self.assertFalse((SOURCE / 'oracle_factory' / 'prep.py').exists())  # la copia vieja con la regla de antes no vuelve


class IgnoradosEh2(unittest.TestCase):
    setUp = _archivo.Archivo.setUp  # sólo el proyecto temporal, no sus pruebas

    def avisos(self, ident):
        return [a for a in f.datos_estado(ident)['avisos'] if 'ignora' in a]

    def test_eh2_un_modulo_excluido(self):
        ident = f.nuevo('Ignorados', 'uno')
        self.assertEqual(self.avisos(ident), [])
        (self.root / 'paquete').mkdir()
        (self.root / 'paquete' / 'secreto.py').write_text('X = 1\n')
        (self.root / '.git' / 'info').mkdir(parents=True, exist_ok=True)
        (self.root / '.git' / 'info' / 'exclude').write_text('secreto.py\n')
        [aviso] = self.avisos(ident)
        self.assertIn('paquete/secreto.py', aviso)
        self.assertIn('fuera de la huella', aviso)
        for i in range(12):  # con muchos, se nombran todos
            (self.root / 'paquete' / f'm{i:02d}.py').write_text('X = 1\n')
        (self.root / '.git' / 'info' / 'exclude').write_text('secreto.py\nm*.py\n')
        [aviso] = self.avisos(ident)
        for i in range(12):
            self.assertIn(f'paquete/m{i:02d}.py', aviso)

    def test_eh2_lo_ignorado_que_no_es_codigo(self):
        ident = f.nuevo('Ignorados', 'uno')
        (self.root / '.venv' / 'lib').mkdir(parents=True)
        (self.root / '.venv' / 'lib' / 'modulo.py').write_text('X = 1\n')
        (self.root / 'extension.vsix').write_bytes(b'PK')
        (self.root / 'datos.json').mkdir()  # una carpeta ignorada entera, aunque se llame como código
        (self.root / 'datos.json' / 'a.txt').write_text('a\n')
        (self.root / '.gitignore').write_text('.venv/\n*.vsix\ndatos.json/\n')
        self.assertEqual(self.avisos(ident), [])


class InventarioEh3(unittest.TestCase):
    python = None
    P = _proc.Procedencia  # sus ayudantes, no sus pruebas
    setUp, escribe, git, salida = P.setUp, P.escribe, P.git, P.salida
    proyecto, correr, bom, componente, prop = P.proyecto, P.correr, P.bom, P.componente, P.prop

    def test_eh3_un_paquete_extra(self):
        self.proyecto(instalado={'alfa': '1.2.3', 'beta': '2.0.1', 'Gama_Extra': '0.4'})
        bom = self.bom()
        gama = self.componente(bom, 'Gama_Extra')
        self.assertEqual((self.prop(gama, 'factory:fuente'), self.prop(gama, 'factory:fijada'), gama['version']), ('instalado', 'false', '0.4'))
        diferencias = [p['value'] for p in bom['metadata']['properties'] if p['name'] == 'factory:diferencia']
        self.assertTrue([d for d in diferencias if 'Gama_Extra' in d], diferencias)
        self.assertEqual(self.prop(bom['metadata'], 'factory:confiable'), 'false')

    def test_eh3_el_proyecto_mismo_no_cuenta(self):
        self.proyecto(instalado={'alfa': '1.2.3', 'beta': '2.0.1', 'demo': '1.0.0'})
        bom = self.bom()
        self.assertEqual([c for c in bom['components'] if c['name'] == 'demo'], [])
        self.assertEqual(self.prop(bom['metadata'], 'factory:confiable'), 'true')


if __name__ == '__main__':
    unittest.main()
