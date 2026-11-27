"""ee1–ee3: el tutorial de Buscaminas y los tres ejemplos cortos llegan, con la CLI, a producir evidencia y juicio (A4-02 de la cuarta
auditoría). Cada prueba arma un proyecto nuevo como dice su guía —los archivos del ejemplo, su config.json y sus catálogos, sin
adaptarlos—, abre el cambio con la spec del ejemplo, aprueba spec y sensor, elige las medidas de la guía, commitea y corre `evidencia`
y `juzgar`."""
import json
from pathlib import Path
import re
import shutil
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_sensor_de_factory as _sensor  # noqa: E402
from oracle_factory import sensor  # noqa: E402

f = _sensor.f
SOURCE = _sensor.SOURCE
BUSCAMINAS = SOURCE / 'examples/buscaminas'
CORTOS = SOURCE / 'examples/cortos'
# Los archivos que copia cada guía (docs/tutorial-buscaminas.md y la tabla de docs/ejemplos-cortos.md).
ARCHIVOS = {'precio': ('total.py', 'test_total.py', 'sensor.py'), 'csv': ('lector.py', 'test_lector.py', 'sensor.py'),
            'ayuda': ('uso.md', 'pasos.md', 'test_ayuda.py', 'sensor.py')}
# La regresión que propone cada guía para ver un rojo.
ROTURAS = {'precio': ('total.py', '<= 50', '<= 51'), 'csv': ('lector.py', 'cantidad <= 0', 'cantidad == 0'),
           'ayuda': ('uso.md', 'pasos.md)', 'faltante.md)')}


class Recorrido(_sensor.Base):
    def guia(self, capacidad, carpeta, archivos, comun, medidas, rotura=None):
        """Lo que hace la persona con la guía, en un proyecto recién inicializado. Devuelve el identificador del cambio."""
        for nombre in archivos:
            shutil.copy(carpeta / nombre, self.root / nombre)
        shutil.copy(comun / 'config.json', self.root / '.factory/config.json')
        shutil.copy(comun / 'oracle.json', self.root / 'oracle.json')
        (self.root / 'catalogos').mkdir(exist_ok=True)
        for catalogo in (comun / 'catalogos').glob('*.oracle'):
            shutil.copy(catalogo, self.root / 'catalogos' / catalogo.name)
        ident = f.nuevo(f'Comprobar {capacidad}', capacidad=capacidad, sufijo='primer-ejercicio')
        cambio = self.root / 'openspec/changes' / ident
        (cambio / 'proposal.md').write_text(f'# Comprobar {capacidad}\n\n## Por qué\n\nPráctica.\n\n## Qué cambia\n\nLa regla del ejemplo.\n\n'
                                            '## Fuera de alcance\n\nOtras reglas.\n\n## Decisiones humanas\n\nNinguna.\n', encoding='utf-8')
        for vieja in (cambio / 'specs').iterdir():
            shutil.rmtree(vieja)
        (cambio / 'specs' / capacidad).mkdir(parents=True)
        shutil.copy(carpeta / 'spec.md', cambio / 'specs' / capacidad / 'spec.md')
        with self.escribe('1'):
            f.aprobar_spec(ident)
        f.importar(ident)
        rid = f.leer(ident)[1]['requisitos'][0]
        f.medir(ident, requisito_id=rid, medidas=medidas, quitar_sin_medir=True)
        with self.escribe('1'):
            sensor.aprobar()
        if rotura:
            archivo, antes, despues = rotura
            texto = (self.root / archivo).read_text(encoding='utf-8')
            self.assertIn(antes, texto)
            (self.root / archivo).write_text(texto.replace(antes, despues, 1), encoding='utf-8')
        self.git('add', '.')
        self.git('commit', '-qm', 'Comprobar la regla del ejercicio')
        return ident

    def evidencia_y_juicio(self, ident):
        """`evidencia` y `juzgar` como en la guía: los hechos tienen que quedar en la carpeta de evidencia del commit."""
        sensor.producir(ident, [])
        hechos = self.evidencia(ident) / 'hechos.json'
        self.assertTrue(hechos.is_file(), f'evidencia no dejó {hechos}: {self.salida()}')
        json.loads(hechos.read_text(encoding='utf-8'))
        try:  # juzgar registra el juicio y además se niega a seguir si no es verde
            f.juzgar(ident, f.hechos_del_candidato(ident))
        except f.FactoryError:
            pass
        self.salida()
        oracle = f.leer(ident)[1]['oracle']
        self.informe = (self.root / oracle['informe']).read_text(encoding='utf-8')
        return oracle['codigo']

    def buscaminas(self, rotura=None):
        ident = self.guia('buscaminas', BUSCAMINAS, ('buscaminas.py', 'test_buscaminas.py', 'sensor.py'),
                          BUSCAMINAS,
                          ['buscaminas.casos_correctos', 'buscaminas.corrida_completa'], rotura)
        return self.evidencia_y_juicio(ident)

    def corto(self, caso, rotura=None):
        ident = self.guia(caso, CORTOS / caso, ARCHIVOS[caso], CORTOS / 'comun', ['cortos.caso', 'cortos.corrida'], rotura)
        return self.evidencia_y_juicio(ident)


class EjemplosProducenEvidencia(Recorrido):
    def test_ee1_buscaminas(self):
        self.assertEqual(self.buscaminas(), 0, self.__dict__.get('informe'))

    def test_ee1_precio(self):
        self.assertEqual(self.corto('precio'), 0, self.__dict__.get('informe'))

    def test_ee1_csv(self):
        self.assertEqual(self.corto('csv'), 0, self.__dict__.get('informe'))

    def test_ee1_ayuda(self):
        self.assertEqual(self.corto('ayuda'), 0, self.__dict__.get('informe'))


class RegresionEnRojo(Recorrido):
    def test_ee2_buscaminas_cuenta_mal(self):
        # Un número de minas vecinas de más: «número y región vacía» del sensor deja de coincidir.
        self.assertEqual(self.buscaminas(('buscaminas.py', 'return sum(', 'return 1 + sum(')), 1)

    def test_ee2_precio_acepta_51(self):
        self.assertEqual(self.corto('precio', ROTURAS['precio']), 1)

    def test_ee2_csv_acepta_negativa(self):
        self.assertEqual(self.corto('csv', ROTURAS['csv']), 1)

    def test_ee2_ayuda_enlaza_faltante(self):
        self.assertEqual(self.corto('ayuda', ROTURAS['ayuda']), 1)


def bloque(guia, archivo, lenguaje='json'):
    texto = (SOURCE / guia).read_text(encoding='utf-8')
    hallado = re.search(r'^```' + lenguaje + r' archivo=' + re.escape(archivo) + r'\n(.*?)^```', texto, re.M | re.S)
    return hallado.group(1) if hallado else None


class GuiasDeclaranElComando(unittest.TestCase):
    def coinciden(self, guia, carpeta, prefijo):
        config = (carpeta / 'config.json').read_text(encoding='utf-8')
        self.assertEqual(bloque(guia, prefijo + 'config.json'), config)
        self.assertIn('"{salida}/hechos.json"', config)
        oracle = (carpeta / 'oracle.json').read_text(encoding='utf-8')
        self.assertEqual(bloque(guia, prefijo + 'oracle.json'), oracle)
        self.assertIs(json.loads(oracle)['catalogo_base'], False)

    def test_ee3_buscaminas(self):
        self.coinciden('docs/tutorial-buscaminas.md', BUSCAMINAS, '')

    def test_ee3_cortos(self):
        self.coinciden('docs/ejemplos-cortos.md', CORTOS / 'comun', 'comun/')


if __name__ == '__main__':
    unittest.main()
