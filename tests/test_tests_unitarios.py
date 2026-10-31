"""Los tests unitarios como práctica del desarrollo: escenarios tu1–tu3, con la CLI y la plantilla de verdad."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_agentes as _agentes  # noqa: E402
import test_archivo as _archivo  # noqa: E402
from oracle_factory import agentes, plantillas  # noqa: E402

f = _archivo.f
SOURCE = Path(__file__).resolve().parents[1]
PASO = {'es': 'Agente: escribir primero los tests de cada escenario de la spec, cuando sea posible, y comprobar que fallan antes de implementar.',
        'en': 'Agent: write the tests for each spec scenario first, when possible, and check that they fail before implementing.'}
IMPLEMENTAR = {'es': 'Agente: implementar', 'en': 'Agent: implement'}
GUIA = ('Los tests unitarios son parte del desarrollo y no suplantan a Oracle',
        'Un test que ya existía no se edita para que pase sin dejarlo dicho a quien revisa')
FUENTES = ('2402.13521', '2608.17177', '2501.12862', '2510.09907', 'ImpossibleBench', 'EvilGenie')


def tareas(root, ident):
    return (root / 'openspec/changes' / ident / 'tasks.md').read_text(encoding='utf-8')


class PasoDeTests(unittest.TestCase):
    setUp, git, salida, escribe, cambio_cerrado = (_archivo.Archivo.setUp, _archivo.Archivo.git, _archivo.Archivo.salida,
                                                   _archivo.Archivo.escribe, _archivo.Archivo.cambio_cerrado)

    def declarar(self, idioma):
        ruta = self.root / '.factory/config.json'
        ruta.write_text(json.dumps({**json.loads(ruta.read_text()), 'idioma': idioma}))

    def comprobar(self, texto, idioma):
        self.assertIn(PASO[idioma], texto)
        self.assertLess(texto.index(PASO[idioma]), texto.index(IMPLEMENTAR[idioma]))
        self.assertIn('- [ ] ' + PASO[idioma], texto)

    # --- tu1: el paso en las tareas de un cambio nuevo ---------------------------------------------------------------
    def test_tu1_un_cambio_nuevo_en_espanol(self):
        self.comprobar(tareas(self.root, f.nuevo('Algo nuevo', 'algo')), 'es')

    def test_tu1_un_cambio_nuevo_en_ingles(self):
        self.declarar('en')
        texto = tareas(self.root, f.nuevo('Algo nuevo', 'algo'))
        self.comprobar(texto, 'en')
        self.assertNotIn('escribir primero', texto)

    def test_tu1_la_plantilla_de_cada_idioma_lo_trae(self):
        for idioma in plantillas.IDIOMAS:
            self.comprobar(plantillas.TEXTOS[idioma]['tareas'], idioma)

    def test_tu1_el_paso_no_bloquea(self):
        # El recorrido completo (aprobar, importar, medir, revisar, juzgar y cerrar) con el paso sin marcar en tasks.md.
        ident = self.cambio_cerrado()
        texto = tareas(self.root, ident)
        self.assertIn('- [ ] ' + PASO['es'], texto)  # el paso quedó sin marcar...
        self.assertEqual(f.leer(ident)[1]['fase'], 'cerrada')  # ...y ningún comando se negó por él

    def test_tu1_la_aprobacion_solo_se_niega_por_la_marca_de_pendiente_no_por_el_paso(self):
        ident = f.nuevo('Algo nuevo', 'algo')
        carpeta = self.root / 'openspec/changes' / ident
        self.assertNotIn('TODO:', tareas(self.root, ident))
        f.exigir_plantilla_completa([carpeta / 'tasks.md'])
        (carpeta / 'tasks.md').write_text(tareas(self.root, ident) + '- [ ] Agente: TODO: algo\n', encoding='utf-8')
        with self.assertRaises(f.FactoryError):
            f.exigir_plantilla_completa([carpeta / 'tasks.md'])


class GuiaDeTests(unittest.TestCase):
    setUp, git, correr = _agentes.Agentes.setUp, _agentes.Agentes.git, _agentes.Agentes.correr

    # --- tu2: la guía para agentes -------------------------------------------------------------------------------------
    def test_tu2_la_guia_generada_lo_dice(self):
        # La guía que escribe `oracle-factory agentes` de verdad en AGENTS.md, no sólo el bloque en memoria.
        self.correr('init')
        self.assertEqual(self.correr('agentes').returncode, 0)
        texto = (self.root / 'AGENTS.md').read_text(encoding='utf-8')
        for frase in (*GUIA, 'escribilos primero, cuando sea posible'):
            self.assertIn(frase, texto)
        self.assertIn(GUIA[0], agentes.bloque('confirmacion'))

    def test_tu2_una_guia_vieja_se_detecta(self):
        self.correr('init')
        self.assertEqual(self.correr('agentes', '--verificar').returncode, 0)
        vieja = '\n'.join(l for l in agentes.bloque('confirmacion').splitlines() if 'tests unitarios' not in l.lower())
        (self.root / 'AGENTS.md').write_text(vieja + '\n')
        r = self.correr('agentes', '--verificar')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('oracle-factory agentes', r.stdout + r.stderr)
        self.assertEqual(self.correr('agentes').returncode, 0)
        self.assertIn(GUIA[0], (self.root / 'AGENTS.md').read_text())


class DocumentoDeTests(unittest.TestCase):
    texto = (SOURCE / 'docs/tests.md').read_text(encoding='utf-8') if (SOURCE / 'docs/tests.md').is_file() else ''

    # --- tu3: el documento de la práctica --------------------------------------------------------------------------------
    def test_tu3_explica_las_tres_capas_y_cita_las_fuentes(self):
        self.assertTrue(self.texto, 'falta docs/tests.md')
        for palabra in ('Oracle', 'mutaciones', 'tests unitarios'):
            self.assertIn(palabra, self.texto)
        for fuente in FUENTES:
            self.assertIn(fuente, self.texto)
        self.assertIn(GUIA[1].lower(), self.texto.lower())

    def test_tu3_dice_lo_mismo_que_la_plantilla(self):
        # Lo que dice la plantilla de verdad, en los dos idiomas, y lo que dice el documento
        self.assertIn('cuando sea posible', plantillas.TEXTOS['es']['tareas'])
        self.assertIn('when possible', plantillas.TEXTOS['en']['tareas'])
        self.assertIn('cuando sea posible', self.texto)
        self.assertIn('no bloquea', self.texto)
        self.assertIn('`importar`, `medir`, `revisar`, `juzgar` y `cerrar` no lo miran', self.texto)

    def test_tu3_dice_que_hacer_cuando_no_se_puede_y_nombra_la_excepcion_de_la_spec(self):
        self.assertIn('Pruebas: no aplica — motivo', self.texto)
        self.assertIn('estado', self.texto)

    def test_tu3_no_dice_que_falta_lo_que_ya_existe(self):
        # El aviso de requisitos sin casos y la excepción de la spec ya existen: no figuran como pendientes.
        pendiente = self.texto[self.texto.index('## Qué falta'):]
        self.assertNotIn('avisar cuando un requisito no tiene caso asociado', pendiente)
        self.assertNotIn('excepción «sin tests»', pendiente)
        self.assertIn('ningún caso ejecuta', pendiente)


if __name__ == '__main__':
    unittest.main()
