"""Las guías dicen lo que pasa (fc1), `estado` muestra en texto los mismos avisos que en JSON (fc2) y el camino de entrada —el
ejemplo de notas y la guía desde cero— produce los hechos con Factory (fc3).

Las frases vienen de las reauditorías de Astra (H4, H9, D5) y de Fable (R8, R10); se cuidan con el patrón de
tests/test_frases_honestas.py: la frase vieja que no tiene que volver y la que la reemplaza, en su archivo."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import test_archivo as _archivo  # noqa: E402
from test_frases_honestas import plano, problemas  # noqa: E402  (funciones sueltas: no se heredan pruebas)
from oracle_factory import sensor  # noqa: E402
from tools.verify_guide import Blocks  # noqa: E402

f = _archivo.f
SOURCE = Path(__file__).resolve().parents[1]
DE_CI = ('docs/ci.md', 'docs/plantillas/verificar.yml', 'docs/plantillas/verificar-almacen.yml', '.github/workflows/verificar.yml')

AFIRMACIONES = [  # (archivo, frase vieja, frase que la reemplaza)
    ('docs/ci.md', 'Para que un fallo en `main` impida integrar, marcá el check como obligatorio',
     'Este chequeo es informativo: muestra el estado de los cambios y no impide integrar.'),
    *[(archivo, 'marcá el check como obligatorio', 'Es un chequeo informativo: muestra el estado y no impide integrar') for archivo in DE_CI[1:]],
    ('site/index.html', 'Cada candidato guarda un inventario CycloneDX',
     '<code>oracle-factory procedencia ID</code> guarda en el candidato un inventario CycloneDX'),
    ('README.md', 'el inventario CycloneDX de cada candidato', 'el inventario CycloneDX que `procedencia ID` guarda en el candidato'),
    ('docs/estructura.md', 'Lo que la migración no hace: limpiar las líneas de Factory del `.gitignore` y el `.gitattributes` del producto',
     'Lo que la migración no hace: sacar el bloque generado de un `AGENTS.md` versionado.'),
    ('README.md', 'Si cambia el código, la spec, las medidas o la evidencia, hay que repetir la revisión y el juicio.',
     'Si cambia el código, la spec o las medidas, hay que repetir la revisión y el juicio; si cambia sólo la evidencia, vence el '
     'juicio y la revisión sigue vigente.'),
]


class Base(unittest.TestCase):
    A = _archivo.Archivo  # sus ayudantes, no sus pruebas
    setUp, escribe, git, salida = A.setUp, A.escribe, A.git, A.salida

    def config(self):
        return self.root / '.factory/config.json'

    def medido(self, ident):
        """La spec aprobada, las medidas decididas y el producto commiteado."""
        with self.escribe('1'):
            f.aprobar_spec(ident)
        f.importar(ident)
        rid = f.leer(ident)[1]['requisitos'][0]
        f.medir(ident, requisito_id=rid, medidas=['notas.casos_ejecutados', 'notas.resultados'], quitar_sin_medir=True)
        self.git('add', '.')
        self.git('commit', '-qm', 'producto fixture')

    def revisado(self, ident):
        informe = self.root / 'tareas' / ident / 'revision.md'
        informe.write_text('Fixture de revisión; no es una revisión real.\n')
        with self.escribe('1'):
            f.revisar(ident, informe, 'Persona fixture', 'aprobar', 0)


# --- fc1: las guías no prometen más de lo que pasa ------------------------------------------------------------------------
class FrasesFc1(unittest.TestCase):
    def test_fc1_ninguna_frase_vieja_esta_y_cada_reemplazo_si(self):
        self.assertEqual(problemas(SOURCE, AFIRMACIONES), [])

    def test_fc1_nada_de_ci_recomienda_hacer_obligatorio_el_chequeo(self):  # la clase, no sólo la frase de la lista
        patron = re.compile(r'(?:marc[aáo]\w*|hac[eé]\w*|pon[eé]\w*|configur[aáo]\w*)[^.]{0,60}\bobligatori|para que[^.]{0,60}impida integrar', re.I)
        hallados = [f'{archivo}: {m.group(0)}' for archivo in DE_CI
                    for m in patron.finditer(plano((SOURCE / archivo).read_text(encoding='utf-8')))]
        self.assertEqual(hallados, [])

    def test_fc1_la_guia_y_las_plantillas_dicen_que_el_chequeo_es_informativo(self):
        for archivo in DE_CI:
            with self.subTest(archivo=archivo):
                texto = plano((SOURCE / archivo).read_text(encoding='utf-8'))
                self.assertIn('informativo', texto)
                self.assertIn('no impide integrar', texto)

    def test_fc1_la_guia_de_ci_dice_por_que_marcarlo_obligatorio_no_frena_nada(self):
        guia = plano((SOURCE / 'docs/ci.md').read_text(encoding='utf-8'))
        self.assertIn('en el pull request el paso sale con 0', guia)
        self.assertIn('integrar lo decide una persona', guia)

    def test_fc1_las_plantillas_siguen_siendo_yaml_y_no_cambian_lo_que_hacen(self):
        for archivo in DE_CI[1:]:
            with self.subTest(archivo=archivo):
                texto = (SOURCE / archivo).read_text(encoding='utf-8')
                datos = yaml.safe_load(texto)
                self.assertEqual(datos['permissions'], {'contents': 'read'})
                self.assertIn('if [ "$GITHUB_REF" = refs/heads/main ]; then exit "$rc"; fi', texto)  # sigue fallando en main
                self.assertIn('::warning title=verificar::', texto)  # y avisando en las demás

    def test_fc1_ninguna_pagina_dice_que_cada_candidato_guarda_su_inventario(self):
        patron = re.compile(r'cada candidato[^.]{0,40}inventario|inventario[^.]{0,40}de cada candidato', re.I)
        archivos = sorted([*(SOURCE / 'site').glob('*.html'), *(SOURCE / 'site').glob('*.js'), SOURCE / 'README.md',
                           *(SOURCE / 'docs').rglob('*.md')])
        hallados = [f'{p.relative_to(SOURCE)}: {m.group(0)}' for p in archivos for m in patron.finditer(plano(p.read_text(encoding='utf-8')))]
        self.assertEqual(hallados, [])

    def test_fc1_estructura_dice_una_sola_cosa_de_las_lineas_de_gitignore_en_la_migracion(self):
        texto = plano((SOURCE / 'docs/estructura.md').read_text(encoding='utf-8'))
        self.assertIn('También saca del producto lo de Factory que ya no sirve: sus líneas de `.gitignore` y `.gitattributes`', texto)
        niega = [frase.strip()[:140] for frase in re.findall(r'[^.]*migración no hace[^.]*\.[^.]*\.', texto) if '.gitignore' in frase or '.gitattributes' in frase]
        self.assertEqual(niega, [])


class VigenciaFc1(Base):
    def test_fc1_cambiar_solo_la_evidencia_vence_el_juicio_y_no_la_revision(self):  # lo que ahora dice el README
        ident = f.nuevo('Nota', con_ejemplo='notas')
        self.medido(ident)
        self.revisado(ident)
        hechos = self.root / 'tareas' / ident / 'hechos.json'
        hechos.write_text(json.dumps({'comprobacion': [{'caso': c, 'codigo': 0} for c in ('vacío', 'espacios', 'válido')]}))
        f.juzgar(ident, hechos)
        carpeta, estado = f.leer(ident)
        self.assertEqual(f.pendientes_actuales(carpeta, estado), [])
        hechos.write_text(hechos.read_text() + '\n')
        pendientes = f.pendientes_actuales(carpeta, estado)
        self.assertEqual(pendientes, ['hechos cambiado o sin huella'])
        datos = f.datos_estado(ident)
        self.assertTrue(datos['revision']['vigente'])
        self.assertFalse(datos['oracle']['vigente'])


# --- fc2: estado muestra los mismos avisos en texto y en JSON -------------------------------------------------------------
class AvisosFc2(Base):
    def texto(self, ident):
        self.salida()
        f.mostrar(ident)
        return self.salida()

    def ignorar_un_modulo(self):
        (self.root / 'paquete').mkdir()
        (self.root / 'paquete' / 'secreto.py').write_text('X = 1\n')
        (self.root / '.git' / 'info').mkdir(parents=True, exist_ok=True)
        (self.root / '.git' / 'info' / 'exclude').write_text('secreto.py\n')

    def test_fc2_un_archivo_de_codigo_ignorado_sale_en_el_texto_y_en_el_json(self):
        ident = f.nuevo('Ignorados', 'uno')
        self.ignorar_un_modulo()
        [aviso] = [a for a in f.datos_estado(ident)['avisos'] if 'paquete/secreto.py' in a]
        self.assertIn('Git ignora 1 archivo de código dentro del producto', aviso)
        self.assertIn(f'Aviso: {aviso}.', self.texto(ident))

    def test_fc2_cada_aviso_del_json_esta_en_el_texto(self):
        ident = f.nuevo('Varios', 'uno')
        self.ignorar_un_modulo()
        fuentes = ('avisos_head', 'aviso_revision', 'aviso_lanzamientos', 'aviso_sin_autor', 'aviso_sin_medir', 'aviso_notas', 'aviso_union')
        for nombre in fuentes:  # cada fuente de avisos de estado dice algo, y la de ignorados dice lo suyo de verdad
            p = patch.object(f, nombre, return_value=[f'centinela de {nombre}']); p.start(); self.addCleanup(p.stop)
        avisos = f.datos_estado(ident)['avisos']
        self.assertEqual([a for a in avisos if a.startswith('centinela')], [f'centinela de {n}' for n in fuentes])
        self.assertGreater(len(avisos), len(fuentes))
        self.assertEqual([linea.removeprefix('Aviso: ').removesuffix('.') for linea in self.texto(ident).splitlines() if linea.startswith('Aviso: ')],
                         avisos)  # los mismos, en el mismo orden

    def test_fc2_un_cambio_abandonado_tambien_muestra_los_mismos(self):
        ident = f.nuevo('Abandonado', 'uno')
        self.ignorar_un_modulo()
        with self.escribe('1'):
            f.abandonar(ident)  # confirmar; motivo armado
        p = patch.object(f, 'aviso_union', return_value=['centinela de la unión']); p.start(); self.addCleanup(p.stop)
        avisos = f.datos_estado(ident)['avisos']
        self.assertEqual(avisos, ['centinela de la unión'])  # un cambio abandonado no avisa de lo demás
        self.assertEqual([linea for linea in self.texto(ident).splitlines() if linea.startswith('Aviso: ')], ['Aviso: centinela de la unión.'])


# --- fc3: el camino de entrada usa la evidencia de Factory ----------------------------------------------------------------
class EjemploFc3(Base):
    def test_fc3_el_ejemplo_declara_su_sensor_y_los_hechos_quedan_producidos_por_factory(self):
        ident = f.nuevo('Nota', con_ejemplo='notas')
        self.assertIn('oracle-factory aprobar-sensor', self.salida())  # dice lo que sigue
        declarado = json.loads(self.config().read_text(encoding='utf-8'))['sensor']
        self.assertEqual(declarado, {'comando': ['{python}', 'examples/notas/sensor.py', '--salida', '{salida}/hechos.json'],
                                     'tope_minutos': 5, 'hechos': 'avisar'})
        self.assertEqual(f.config_proyecto()['sensor'], declarado)
        self.assertFalse(sensor.aprobado(declarado))  # declararlo no lo aprueba: eso es de una persona
        self.medido(ident)
        with self.assertRaises(f.FactoryError):
            sensor.producir(ident, [])
        with self.escribe('1'):
            sensor.aprobar()
        sensor.producir(ident, [])
        self.revisado(ident)
        self.salida()
        f.juzgar(ident, f.hechos_del_candidato(ident))
        corto = self.git('rev-parse', '--short=7', 'HEAD')
        self.assertIn(f'Hechos: producidos por Factory (oracle-factory evidencia, commit {corto})', self.salida())
        self.assertEqual(f.pendientes_actuales(*f.leer(ident)), [])

    def test_fc3_un_sensor_ya_declarado_no_cambia(self):
        propio = {'comando': ['sh', 'tools/mi-sensor.sh', '{salida}'], 'tope_minutos': 7, 'hechos': 'exigir'}
        self.config().write_text(json.dumps({**json.loads(self.config().read_text(encoding='utf-8')), 'sensor': propio}), encoding='utf-8')
        antes = self.config().read_bytes()
        f.nuevo('Nota', con_ejemplo='notas')
        self.assertEqual(self.config().read_bytes(), antes)
        self.assertNotIn('aprobar-sensor', self.salida())

    def test_fc3_el_resto_de_la_configuracion_se_conserva(self):
        antes = {**json.loads(self.config().read_text(encoding='utf-8')), 'capacidades': {'apuntes': 'notas'}, 'idioma': 'en',
                 'rag': {'nota': 'sólo en español'}}
        self.config().write_text(json.dumps(antes), encoding='utf-8')
        f.nuevo('Nota', con_ejemplo='notas')
        despues = json.loads(self.config().read_text(encoding='utf-8'))
        self.assertEqual({k: v for k, v in despues.items() if k != 'sensor'}, antes)
        self.assertIn('sensor', despues)
        # legible, como la escribe init: con sangría de 2 y sin escapar lo que no es ASCII
        self.assertEqual(self.config().read_text(encoding='utf-8'), json.dumps(despues, indent=2, ensure_ascii=False) + '\n')

    def test_fc3_un_cambio_sin_el_ejemplo_no_declara_nada(self):
        antes = self.config().read_bytes()
        f.nuevo('Otro', 'uno')
        self.assertEqual(self.config().read_bytes(), antes)

    def test_fc3_con_la_configuracion_anterior_en_la_raiz_no_la_tapa(self):
        self.config().unlink()
        (self.root / 'factory.json').write_text(json.dumps({'tipos_obligatorios': True}))
        f.nuevo('Nota', con_ejemplo='notas')
        self.assertFalse(self.config().exists())  # crearla dejaría sin efecto la de la raíz
        self.assertTrue(f.config_proyecto()['tipos_obligatorios'])
        self.assertNotIn('aprobar-sensor', self.salida())

    def test_fc3_con_los_registros_en_un_almacen_aparte_no_declara_un_sensor_que_no_esta_en_el_producto(self):
        antes = self.config().read_bytes()
        p = patch.object(f, 'PRODUCTO', self.root); p.start(); self.addCleanup(p.stop)
        f.declarar_sensor_del_ejemplo()
        self.assertEqual(self.config().read_bytes(), antes)


class GuiaFc3(unittest.TestCase):
    def bloques(self):
        return Blocks((SOURCE / 'site/desde-cero.html').read_text(encoding='utf-8')).blocks

    def test_fc3_la_guia_desde_cero_produce_los_hechos_con_factory(self):
        probar = [linea for bloque in self.bloques()['probar'] for linea in bloque.splitlines()]
        orden = [next(i for i, linea in enumerate(probar) if linea.startswith(inicio))
                 for inicio in ('git commit', 'oracle-factory aprobar-sensor', 'oracle-factory evidencia ID_DEL_CAMBIO')]
        self.assertEqual(orden, sorted(orden))  # la evidencia sale del commit, con el sensor que aprobó una persona
        self.assertIn('oracle-factory juzgar ID_DEL_CAMBIO', self.bloques()['cerrar'])  # sin --con: los hechos del candidato

    def test_fc3_ni_la_guia_ni_el_ejemplo_ensenan_a_escribir_los_hechos_a_mano(self):
        for archivo in ('site/desde-cero.html', 'oracle_factory/data/notas/README.md'):
            with self.subTest(archivo=archivo):
                texto = (SOURCE / archivo).read_text(encoding='utf-8')
                for a_mano in ('sensor.py --salida', '.factory/local/hechos.json', 'juzgar ID_DEL_CAMBIO --con'):
                    self.assertNotIn(a_mano, texto)
                for comando in ('oracle-factory aprobar-sensor', 'oracle-factory evidencia'):
                    self.assertIn(comando, texto)

    def test_fc3_la_guia_dice_de_donde_salen_los_hechos(self):
        texto = plano((SOURCE / 'site/desde-cero.html').read_text(encoding='utf-8'))
        self.assertIn('producidos por Factory', texto)
        self.assertNotIn('sin ejecutar por sí misma el sensor', texto)

    def test_fc3_el_arnes_de_la_guia_confirma_el_sensor_como_una_persona(self):
        arnes = (SOURCE / 'tools/verify_guide.py').read_text(encoding='utf-8')
        self.assertIn("'aprobar-sensor'", arnes)

    @unittest.skipUnless(all(shutil.which(h) for h in ('oracle', 'tasks', 'uv'))
                         and (Path(sys.executable).parent / 'oracle-factory').is_file(), 'requiere Oracle, Oracle Task, uv y oracle-factory')
    def test_fc3_quien_sigue_la_guia_termina_con_hechos_producidos_por_factory(self):
        with tempfile.TemporaryDirectory() as tmp:
            informe = Path(tmp) / 'guia.json'
            r = subprocess.run([sys.executable, 'tools/verify_guide.py', '--factory', str(Path(sys.executable).parent / 'oracle-factory'),
                                '--evidencia', str(informe)], cwd=SOURCE, capture_output=True, text=True, timeout=600, stdin=subprocess.DEVNULL)
            self.assertEqual(r.returncode, 0, (r.stdout + r.stderr)[-3000:])
            comandos = json.loads(informe.read_text(encoding='utf-8'))['comandos']
        [aprobar] = [c for c in comandos if c['command'] == 'oracle-factory aprobar-sensor']
        self.assertIn('Sensor aprobado por', aprobar['stdout'])  # lo confirmó el menú, como una persona
        [juicio] = [c for c in comandos if c['command'].startswith('oracle-factory juzgar ')]
        self.assertIn('Hechos: producidos por Factory (oracle-factory evidencia, commit ', juicio['stdout'])


if __name__ == '__main__':
    unittest.main()
