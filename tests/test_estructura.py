"""Estructura de carpetas: escenarios e1–e10 de la spec."""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from oracle_factory import cli as f
from oracle_factory import estructura

SOURCE = Path(__file__).resolve().parents[1]
GIT = ['git', '-c', 'user.name=Persona fixture', '-c', 'user.email=fixture@example.invalid', '-c', 'core.hooksPath=/dev/null', '-c', 'gc.auto=0', '-c', 'maintenance.auto=false']


class Estructura(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'producto'
        self.root.mkdir()
        for name, value in [('ROOT', self.root), ('CHANGES', self.root / 'openspec/changes'), ('AGENTE', None)]:
            p = patch.object(f, name, value); p.start(); self.addCleanup(p.stop)
        p = patch.object(f, 'terminal_interactiva', return_value=True); p.start(); self.addCleanup(p.stop)
        self.stdout = io.StringIO()
        p = contextlib.redirect_stdout(self.stdout); p.__enter__(); self.addCleanup(p.__exit__, None, None, None)
        self.cwd = os.getcwd()
        self.addCleanup(os.chdir, self.cwd)
        f.inicializar()

    # --- ayudantes -----------------------------------------------------------------
    def escribe(self, frase):
        return patch('builtins.input', return_value=frase)

    def git(self, *args, cwd=None):
        return subprocess.run([*GIT, *args], cwd=cwd or self.root, check=True, capture_output=True, text=True).stdout.strip()

    def estado(self, ident):
        return f.leer(ident)[1]

    def salida(self):
        texto = self.stdout.getvalue()
        self.stdout.truncate(0); self.stdout.seek(0)
        return texto

    def cambio_medido(self):
        ident = f.nuevo('Nota', con_ejemplo='notas')
        with self.escribe(f'APROBAR ESPECIFICACION {ident}'):
            f.aprobar_spec(ident)
        f.importar(ident)
        rid = self.estado(ident)['requisitos'][0]
        f.medir(ident, requisito_id=rid, medidas=['notas.casos_ejecutados', 'notas.resultados'], quitar_sin_medir=True)
        subprocess.run(['git', 'init', '-q', '-b', 'main'], cwd=self.root, check=True)
        self.git('add', '.')
        self.git('commit', '-qm', 'producto fixture')
        informe = self.root / 'tareas' / ident / 'revision.md'
        informe.write_text('Fixture de revisión; no es una revisión real.\n')
        with self.escribe(f'REGISTRAR REVISION {ident}'):
            f.revisar(ident, informe, 'Persona fixture', 'aprobar', 0)
        return ident

    def sha7(self):
        return self.git('rev-parse', 'HEAD')[:7]  # como ruta: los 7 primeros del hash completo

    def cambio_juzgado(self):
        ident = self.cambio_medido()
        destino = estructura.ruta_canonica(self.root, ident, 'evidencia', self.sha7()) / 'hechos.json'
        destino.parent.mkdir(parents=True)
        subprocess.run([sys.executable, 'examples/notas/sensor.py', '--salida', destino], cwd=self.root, check=True,
                       capture_output=True)
        f.juzgar(ident, destino)
        self.git('add', '.')
        self.git('commit', '-qm', 'registros')
        return ident

    def desactualizado(self, ident):
        carpeta, estado = f.leer(ident)
        return any('desactualizado' in p for p in f.pendientes_actuales(carpeta, estado))

    def correr(self, *argv, cwd=None, proyecto=None):
        """Corre main() como la CLI, desde una carpeta; devuelve (código, stdout, stderr)."""
        salida, errores = io.StringIO(), io.StringIO()
        if cwd:
            os.chdir(cwd)
        args = (['--proyecto', str(proyecto)] if proyecto else []) + list(argv)
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(errores):
            codigo = f.main(args)
        return codigo, salida.getvalue(), errores.getvalue()

    def huellas(self):
        resultado = {}
        for ruta in sorted(self.root.rglob('*')):
            if ruta.is_file() and '.git' not in ruta.relative_to(self.root).parts:
                try:
                    resultado[str(ruta.relative_to(self.root))] = hashlib.sha256(ruta.read_bytes()).hexdigest()
                except OSError as e:  # diagnóstico: qué archivo y por qué
                    raise AssertionError(f'huellas: no pude leer {ruta.relative_to(self.root)}: {e!r}') from e
        return resultado

    # --- e1: estructura documentada -------------------------------------------------------------
    def test_e1_la_guia_describe_cada_artefacto(self):
        guia = (SOURCE / 'docs/estructura.md').read_text(encoding='utf-8')
        for marca in ('.factory/cambios/<ID>/', 'candidatos/<sha7>/', '.factory/local/', 'revisiones/<sha7>/',
                      'openspec/changes/<ID>/', 'tareas/', 'oracle-factory donde', 'oracle-factory ruta', 'oracle-factory buscar'):
            self.assertIn(marca, guia, marca)
        self.assertIn('docs/estructura.md', (SOURCE / 'README.md').read_text(encoding='utf-8'))

    # --- e2: carpeta propia de Factory ---------------------------------------------------------------
    def test_e2_init_crea_factory_y_ignora_local(self):
        nuevo = Path(self.tmp.name) / 'nuevo'
        nuevo.mkdir()
        with patch.object(f, 'ROOT', nuevo), patch.object(f, 'CHANGES', nuevo / 'openspec/changes'):
            f.inicializar()
        self.assertTrue((nuevo / '.factory/cambios').is_dir() and (nuevo / '.factory/local').is_dir())
        subprocess.run(['git', 'init', '-q'], cwd=nuevo, check=True)
        ignorada = subprocess.run(['git', 'check-ignore', '-q', '.factory/local/x'], cwd=nuevo).returncode
        self.assertEqual(ignorada, 0)

    def test_e2_init_en_proyecto_existente_conserva_el_gitignore(self):
        existente = Path(self.tmp.name) / 'existente'
        existente.mkdir()
        (existente / '.gitignore').write_text('mis-salidas/\n')
        with patch.object(f, 'ROOT', existente), patch.object(f, 'CHANGES', existente / 'openspec/changes'):
            f.inicializar(); f.inicializar()
        lineas = (existente / '.gitignore').read_text().splitlines()
        self.assertEqual(lineas[0], 'mis-salidas/')
        self.assertEqual(lineas.count('.factory/local/'), 1)

    def test_e2_el_clon_de_un_proyecto_trae_la_carpeta_de_factory(self):
        subprocess.run(['git', 'init', '-q', '-b', 'main'], cwd=self.root, check=True)
        self.git('add', '-A')
        self.git('commit', '-qm', 'proyecto inicializado')
        clon = Path(self.tmp.name) / 'clon'
        subprocess.run(['git', 'clone', '-q', self.root, clon], check=True, capture_output=True)
        self.assertTrue((clon / '.factory' / 'LEEME.md').is_file())  # antes: Git no versiona carpetas vacías
        sub = clon / 'sub'
        sub.mkdir()
        codigo, _, errores = self.correr('listar', cwd=sub)
        self.assertEqual(codigo, 0)
        self.assertIn(str(clon), errores)  # descubrió la raíz del clon desde la subcarpeta

    def test_e2_factory_que_no_es_una_carpeta_se_rechaza_antes_de_crear_nada(self):
        raro = Path(self.tmp.name) / 'raro'
        raro.mkdir()
        (raro / '.factory').write_text('soy un archivo')
        with patch.object(f, 'ROOT', raro), patch.object(f, 'CHANGES', raro / 'openspec/changes'):
            with self.assertRaisesRegex(f.FactoryError, 'no es una carpeta'):
                f.inicializar()
        self.assertFalse((raro / 'tareas').exists() or (raro / 'openspec').exists() or (raro / 'oracle.json').exists())

    def test_e2_init_dentro_de_otro_proyecto_avisa(self):
        anidado = self.root / 'anidado'
        anidado.mkdir()
        avisos = io.StringIO()
        with patch.object(f, 'ROOT', anidado), patch.object(f, 'CHANGES', anidado / 'openspec/changes'), \
                contextlib.redirect_stderr(avisos):
            f.inicializar()
        self.assertIn('proyecto anidado', avisos.getvalue())
        self.assertTrue((anidado / '.factory').is_dir())

    # --- e3: descubrir la raíz del proyecto ---------------------------------------------------------------
    def test_e3_comando_desde_una_subcarpeta(self):
        ident = f.nuevo('Nota', con_ejemplo='notas')
        sub = self.root / 'examples' / 'notas'
        codigo, salida, errores = self.correr('listar', cwd=sub)
        self.assertEqual(codigo, 0)
        self.assertIn(ident, salida)
        self.assertIn('Proyecto:', errores)
        self.assertIn(str(self.root), errores)

    def test_e3_proyecto_explicito_manda(self):
        f.nuevo('Nota', con_ejemplo='notas')
        otro = Path(self.tmp.name) / 'otro'
        otro.mkdir()
        with patch.object(f, 'ROOT', otro), patch.object(f, 'CHANGES', otro / 'openspec/changes'):
            f.inicializar()
        codigo, salida, errores = self.correr('listar', cwd=self.root / 'examples', proyecto=otro)
        self.assertEqual(codigo, 0)
        self.assertIn('No hay cambios Factory', salida)
        self.assertNotIn('Proyecto:', errores)

    def test_e3_sin_factory_se_comporta_como_antes(self):
        vacio = Path(self.tmp.name) / 'sin-factory'
        vacio.mkdir()
        codigo, salida, errores = self.correr('listar', cwd=vacio)
        self.assertEqual(codigo, 0)
        self.assertIn('No hay cambios Factory', salida)
        self.assertNotIn('Proyecto:', errores)

    def test_e3_proyecto_anterior_dentro_de_otro_es_frontera(self):
        ident = f.nuevo('Nota', con_ejemplo='notas')  # un cambio en el proyecto de afuera
        anidado = self.root / 'anidado'
        (anidado / 'openspec' / 'changes').mkdir(parents=True)
        (anidado / 'oracle.json').write_text('{}')  # un proyecto de antes de .factory/
        codigo, salida, errores = self.correr('listar', cwd=anidado)
        self.assertEqual(codigo, 0)
        self.assertNotIn(ident, salida)  # no heredó el proyecto de afuera
        self.assertNotIn('Proyecto:', errores)

    def test_e3_la_carpeta_personal_no_cuenta(self):
        casa = Path(self.tmp.name) / 'casa'
        (casa / '.factory').mkdir(parents=True)  # lo que dejaría otra herramienta
        proyecto = casa / 'trabajo' / 'p'
        proyecto.mkdir(parents=True)
        with patch.object(Path, 'home', return_value=casa):
            codigo, salida, errores = self.correr('listar', cwd=proyecto)
        self.assertEqual(codigo, 0)
        self.assertNotIn('Proyecto:', errores)  # no usó la carpeta personal como raíz
        self.assertIn('No hay cambios Factory', salida)

    def test_e3_la_carpeta_personal_enlazada_tampoco_cuenta(self):
        real = Path(self.tmp.name) / 'casa-real'
        (real / '.factory').mkdir(parents=True)
        enlace = Path(self.tmp.name) / 'casa-enlace'
        enlace.symlink_to(real)
        proyecto = real / 'trabajo' / 'p'
        proyecto.mkdir(parents=True)
        with patch.object(Path, 'home', return_value=enlace):  # $HOME es un enlace a la carpeta real
            self.assertIsNone(estructura.raiz_del_proyecto(proyecto))

    def test_e3_un_enlace_simbolico_no_cuenta(self):
        enlace = Path(self.tmp.name) / 'con-enlace'
        enlace.mkdir()
        real = Path(self.tmp.name) / 'real'
        real.mkdir()
        (enlace / '.factory').symlink_to(real)
        sub = enlace / 'sub'
        sub.mkdir()
        self.assertIsNone(estructura.raiz_del_proyecto(sub))

    # --- e4: lo versionado y lo local ---------------------------------------------------------------------
    def test_e4_rutas_relativas_en_otra_ruta_absoluta(self):
        ident = self.cambio_juzgado()
        clon = Path(self.tmp.name) / 'otra' / 'maquina' / 'clon'
        clon.parent.mkdir(parents=True)
        subprocess.run(['git', 'clone', '-q', self.root, clon], check=True, capture_output=True)
        self.root.rename(self.root.with_name('producto-que-la-otra-maquina-no-tiene'))
        with patch.object(f, 'ROOT', clon), patch.object(f, 'CHANGES', clon / 'openspec/changes'):
            filas = estructura.donde(clon, ident, f.leer(ident)[1])
        candidatos = [x for x in filas if x['gate'] == 'candidato']
        self.assertTrue(candidatos and all(x['existe'] for x in candidatos))
        propios = clon / '.factory' / 'cambios'
        for archivo in propios.rglob('*'):
            if archivo.is_file():
                self.assertNotIn(str(self.root), archivo.read_text(encoding='utf-8'), archivo.name)
        self.assertTrue(all(not x['ruta'].startswith('/') for x in candidatos))
        # todo lo que el registro nombra es relativo y existe en la otra máquina
        registrados = [x for x in filas if x['gate'] in ('revisión', 'juicio', 'spec', 'medidas')]
        self.assertTrue(registrados)
        self.assertTrue(all(x['existe'] and not x['ruta'].startswith('/') for x in registrados),
                        [x for x in registrados if not x['existe'] or x['ruta'].startswith('/')])

    # --- e5: la huella excluye lo que Factory produce -----------------------------------------------------------
    def test_e5_nueva_evidencia_no_invalida_la_revision(self):
        ident = self.cambio_medido()
        carpeta = self.root / '.factory/cambios' / ident / 'candidatos' / 'abc1234' / 'evidencia'
        carpeta.mkdir(parents=True)
        (carpeta / 'hechos.json').write_text('{}')
        self.git('add', '.')
        self.git('commit', '-qm', 'evidencia nueva')
        self.assertFalse(self.desactualizado(ident))

    def test_e5_el_acuerdo_sigue_siendo_producto(self):
        ident = self.cambio_medido()
        spec = self.root / self.estado(ident)['spec']
        spec.write_text(spec.read_text() + '\n# cambia el acuerdo\n')
        self.assertTrue(self.desactualizado(ident))

    # --- e6: dónde está cada artefacto ---------------------------------------------------------------------------
    def test_e6_cambio_con_revision_registrada(self):
        ident = self.cambio_juzgado()
        self.salida()
        f.comando_donde(ident, None)
        salida = self.salida()
        for gate in ('acuerdo', 'spec', 'medidas', 'revisión', 'juicio', 'candidato'):
            self.assertRegex(salida, rf'(?m)^{gate}\s+existe\s+\S+', gate)

    def test_e6_artefacto_ausente(self):
        ident = self.cambio_juzgado()
        (self.root / 'openspec/changes' / ident / 'review.md').unlink()
        self.salida()
        f.comando_donde(ident, None)
        self.assertRegex(self.salida(), r'(?m)^revisión\s+AUSENTE\s+openspec/changes/\S+/review\.md')

    def test_e6_cambio_anterior_a_la_estructura(self):
        ident = self.cambio_juzgado()
        viejo = self.root / 'tareas' / ident / 'evidencia-mapeo'
        viejo.mkdir()
        (viejo / 'resultado.json').write_text('{}')
        (self.root / 'tareas' / ident / 'revision-pendiente.md').write_text('histórico\n')
        antes = self.huellas()
        self.salida()
        f.comando_donde(ident, None)
        salida = self.salida()
        self.assertRegex(salida, r'(?m)^histórico\s+histórico\s+tareas/\S+/evidencia-mapeo')
        self.assertRegex(salida, r'(?m)^histórico\s+histórico\s+tareas/\S+/revision-pendiente\.md')
        self.assertEqual(self.huellas(), antes)

    def test_e6_ruta_absoluta_de_un_registro_anterior(self):
        ident = self.cambio_juzgado()
        ruta = self.root / 'openspec/changes' / ident / 'factory.json'
        estado = json.loads(ruta.read_text())
        estado['oracle']['hechos'] = str(self.root / estado['oracle']['hechos'])  # como lo escribía la versión anterior
        ruta.write_text(json.dumps(estado, ensure_ascii=False, indent=2) + '\n')
        self.salida()
        f.comando_donde(ident, None)
        self.assertRegex(self.salida(), r'(?m)^juicio\s+existe\s+/\S+hechos\.json\s+— ruta absoluta de un registro anterior')

    def test_e6_valores_no_validos_en_el_registro(self):
        ident = self.cambio_juzgado()
        ruta = self.root / 'openspec/changes' / ident / 'factory.json'
        estado = json.loads(ruta.read_text())
        estado['spec'] = None
        estado['requisitos'] = 'texto'
        estado['revision'] = {'informe': 5, 'decisiones': [], 'contexto': {'head': 12}}
        estado['oracle'] = {'informe': None, 'hechos': {}, 'contexto': 'x'}
        ruta.write_text(json.dumps(estado, ensure_ascii=False, indent=2) + '\n')
        self.salida()
        f.comando_donde(ident, None)  # antes: TypeError o AttributeError
        salida = self.salida()
        self.assertRegex(salida, r'(?m)^spec\s+no válido')
        self.assertRegex(salida, r'(?m)^revisión\s+no válido')
        self.assertRegex(salida, r'(?m)^acuerdo\s+existe\s+openspec/changes/')  # los válidos se siguen listando

    def test_e6_candidato_limita_el_listado(self):
        ident = self.cambio_juzgado()
        for sha in ('abc1234', 'def5678'):
            carpeta = self.root / '.factory/cambios' / ident / 'candidatos' / sha / 'evidencia'
            carpeta.mkdir(parents=True)
        self.salida()
        f.comando_donde(ident, 'abc')
        salida = self.salida()
        self.assertIn('candidatos/abc1234/evidencia', salida)
        self.assertNotIn('def5678', salida)
        self.assertNotIn('proposal.md', salida)

    # --- e7: ruta canónica para producir artefactos -------------------------------------------------------------------
    def test_e7_evidencia_en_la_carpeta_del_candidato(self):
        ident = self.cambio_juzgado()
        self.salida()
        f.comando_ruta(ident, 'evidencia')
        impresa = self.salida().strip()
        self.assertTrue(impresa.endswith(f'.factory/cambios/{ident}/candidatos/{self.sha7()}/evidencia'), impresa)
        self.assertFalse(Path(impresa).exists())  # imprimir la ruta no crea la carpeta

    def test_e7_checkout_de_revision(self):
        ident = self.cambio_juzgado()
        antes = self.huellas()
        self.salida()
        f.comando_ruta(ident, 'checkout')
        impresa = self.salida().strip()
        self.assertTrue(impresa.endswith(f'.factory/local/revisiones/{self.sha7()}'), impresa)
        self.assertFalse(Path(impresa).exists())
        self.assertEqual(self.huellas(), antes)

    def test_e7_tipo_desconocido(self):
        ident = self.cambio_juzgado()
        with self.assertRaisesRegex(f.FactoryError, 'evidencia, clue, revision, checkout'):
            f.comando_ruta(ident, 'inventado')

    # --- e8: buscar en todo el proyecto ---------------------------------------------------------------------------------
    def test_e8_texto_en_varios_cambios(self):
        uno = f.nuevo('Nota', con_ejemplo='notas')
        dos = f.nuevo('Otra', 'otra')
        with (self.root / 'openspec/changes' / uno / 'proposal.md').open('a', encoding='utf-8') as out:
            out.write('\nfrase-unica-de-prueba en la propuesta\n')
        with (self.root / 'tareas' / dos / 'TAREA.md').open('a', encoding='utf-8') as out:
            out.write('\nfrase-unica-de-prueba en la tarea\n')
        self.salida()
        f.comando_buscar('FRASE-unica-DE-prueba', 200)
        salida = self.salida()
        self.assertRegex(salida, rf'openspec/changes/{uno}/proposal\.md:\d+: .*\[{uno}\]')
        self.assertRegex(salida, rf'tareas/{dos}/TAREA\.md:\d+: .*\[{dos}\]')
        self.assertIn('2 coincidencia(s)', salida)

    def test_e8_buscar_no_lee_a_traves_de_un_factory_enlazado(self):
        ajena = Path(self.tmp.name) / 'ajena'
        (ajena / 'cambios' / '20260101-000000-x').mkdir(parents=True)
        (ajena / 'cambios' / '20260101-000000-x' / 'nota.md').write_text('aguja-ajena\n')
        (self.root / '.factory').rename(self.root / 'factory-propia')
        (self.root / '.factory').symlink_to(ajena)
        self.salida()
        f.comando_buscar('aguja-ajena', 50)
        self.assertNotIn('nota.md', self.salida())

    def test_e6_donde_no_lista_a_traves_de_un_factory_enlazado(self):
        ident = self.cambio_juzgado()
        ajena = Path(self.tmp.name) / 'ajena'
        (ajena / 'cambios' / ident / 'candidatos' / 'abc1234' / 'evidencia').mkdir(parents=True)
        (self.root / '.factory').rename(self.root / 'factory-propia')
        (self.root / '.factory').symlink_to(ajena)
        filas = estructura.donde(self.root, ident, self.estado(ident))
        self.assertFalse([x for x in filas if x['gate'] == 'candidato'])

    def test_e8_fragmento_con_formas_que_se_alargan(self):
        linea = 'ß' * 150 + ' aguja-tardia final'  # casefold convierte cada «ß» en «ss»
        self.assertIn('aguja-tardia', estructura._fragmento(linea, 'aguja-tardia'))

    def test_e8_archivos_grandes_omitidos_y_formas_equivalentes(self):
        ident = f.nuevo('Nota', con_ejemplo='notas')
        carpeta = self.root / 'openspec/changes' / ident
        (carpeta / 'grande.md').write_text('x' * (estructura.LIMITE_ARCHIVO + 100) + '\naguja-grande\n')
        with (carpeta / 'proposal.md').open('a', encoding='utf-8') as out:
            out.write('\nLa Straße del proyecto\n' + 'a' * 300 + ' aguja-lejana\n')
        self.salida()
        f.comando_buscar('STRASSE', 50)  # «ß» y «ss» son formas equivalentes
        salida = self.salida()
        self.assertRegex(salida, r'proposal\.md:\d+: La Straße')
        self.assertIn('1 archivo(s) omitido(s)', salida)  # el grande no se leyó y se avisa
        f.comando_buscar('aguja-lejana', 50)
        self.assertIn('aguja-lejana', self.salida())  # el fragmento muestra donde está el texto

    # --- e9: listar con filtros -------------------------------------------------------------------------------------------
    def test_e9_filtro_de_abiertos(self):
        abierto = f.nuevo('Nota', con_ejemplo='notas')
        cerrado = f.nuevo('Otra', 'otra')
        carpeta, estado = f.leer(cerrado)
        estado['fase'] = 'cerrada'
        f.guardar(carpeta, estado)
        self.salida()
        f.listar(abiertos=True)
        salida = self.salida()
        self.assertIn(abierto, salida)
        self.assertNotIn(cerrado, salida)
        f.listar()
        sin_filtro = self.salida()
        self.assertTrue(abierto in sin_filtro and cerrado in sin_filtro)  # sin filtros, como siempre
        f.listar(cerrados=True)
        self.assertIn(cerrado, self.salida())

    # --- e10: respetar lo existente ---------------------------------------------------------------------------------------------
    def test_e10_los_comandos_de_lectura_no_cambian_nada(self):
        ident = self.cambio_juzgado()
        antes = self.huellas()
        f.comando_donde(ident, None)
        f.comando_ruta(ident, 'evidencia')
        f.comando_buscar('Nota', 50)
        f.listar(abiertos=True)
        self.assertEqual(self.huellas(), antes)


if __name__ == '__main__':
    unittest.main()
