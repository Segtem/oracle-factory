"""La skill de agente: escenarios sk1–sk3, con la CLI de verdad en proyectos temporales."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE))
from oracle_factory import agentes, alarmas, skill  # noqa: E402
from tools.terminal import en_terminal  # noqa: E402

CLI = [sys.executable, '-c', 'import sys; from oracle_factory.cli import main; sys.exit(main())']
ENCABEZADO = '---\nname: oracle-factory\ndescription: algo\n---\n'


def cuerpo(*lineas):
    return ENCABEZADO + '\n'.join(lineas) + '\n'


class Contraste(unittest.TestCase):
    # --- sk1: la skill describe el flujo con los comandos y umbrales del código ---------------------------------------------
    def completo(self, extra=''):
        return cuerpo(f'Hasta {alarmas.UMBRAL_LIGERO} líneas es ligero; más de {alarmas.UMBRAL_LINEAS} líneas, partir.',
                      f'Con {alarmas.UMBRAL_RONDAS} rondas hay un bucle.', extra)

    def test_sk1_la_skill_del_repositorio_coincide_con_el_codigo(self):
        self.assertEqual(skill.problemas(skill.texto(), SOURCE), [])

    def test_sk1_un_texto_correcto_no_da_problemas(self):
        self.assertEqual(skill.problemas(self.completo('Corré `oracle-factory estado ID` y `docs/agentes.md`.'), SOURCE), [])

    def test_sk1_un_comando_inventado_se_nombra(self):
        [problema] = skill.problemas(self.completo('Corré `oracle-factory inventado ID`.'), SOURCE)
        self.assertIn('inventado', problema)
        self.assertIn('no existe', problema)

    def test_sk1_las_opciones_globales_con_valor_no_se_toman_por_el_comando(self):
        texto = self.completo('Corré `oracle-factory --agente TU_NOMBRE nuevo --capacidad C` y `oracle-factory --proyecto RUTA mcp` y `oracle-factory --agente NOMBRE …`.')
        self.assertEqual(skill.comandos_nombrados(texto), {'nuevo', 'mcp'})  # el marcador sin verbo se ignora

    def test_sk1_un_umbral_viejo_se_nombra(self):
        texto = cuerpo(f'Hasta {alarmas.UMBRAL_LIGERO} líneas es ligero; más de 500 líneas, partir.', f'Con {alarmas.UMBRAL_RONDAS} rondas hay un bucle.')
        problemas = skill.problemas(texto, SOURCE)
        self.assertTrue(any('500' in p and str(alarmas.UMBRAL_LINEAS) in p for p in problemas), problemas)
        self.assertTrue(any(f'no cita el umbral de {alarmas.UMBRAL_LINEAS}' in p for p in problemas), problemas)
        texto = cuerpo(f'Hasta {alarmas.UMBRAL_LIGERO} líneas; más de {alarmas.UMBRAL_LINEAS} líneas.', 'Con 5 rondas hay un bucle.')
        problemas = skill.problemas(texto, SOURCE)
        self.assertTrue(any('5 rondas' in p for p in problemas), problemas)
        self.assertTrue(any('no cita el umbral' in p and 'rondas' in p for p in problemas), problemas)

    def test_sk1_el_umbral_de_un_paso_de_50_lineas_es_de_la_skill_y_se_permite(self):
        self.assertEqual(skill.problemas(self.completo('Un paso de más de 50 líneas: parar.'), SOURCE), [])
        self.assertIn(alarmas.UMBRAL_LINEAS, skill.numeros_antes_de(self.completo(), 'líneas'))

    def test_sk1_un_documento_que_no_existe_se_nombra(self):
        [problema] = skill.problemas(self.completo('Mirá `docs/no-existe.md` y `docs/agentes.md`.'), SOURCE)
        self.assertIn('docs/no-existe.md', problema)
        self.assertNotIn('docs/agentes.md', problema)

    def test_sk1_el_encabezado_necesita_nombre_y_descripcion(self):
        sin_nombre = self.completo().replace('name: oracle-factory', 'name: otro')
        sin_descripcion = self.completo().replace('description: algo', 'description:')
        sin_encabezado = self.completo().split('---\n', 2)[2]
        for texto in (sin_nombre, sin_descripcion, sin_encabezado):
            self.assertTrue(any('encabezado' in p for p in skill.problemas(texto, SOURCE)), texto[:60])
        encabezado = skill.encabezado(skill.texto())
        self.assertEqual(encabezado['name'], 'oracle-factory')
        self.assertTrue(encabezado['description'])

    def test_sk1_los_subcomandos_salen_del_analizador_de_la_cli(self):
        validos = skill.subcomandos()
        self.assertLessEqual({'nuevo', 'estado', 'skill', 'agentes', 'puerta', 'medir'}, validos)
        self.assertNotIn('inventado', validos)

    def test_sk1_la_skill_viaja_en_el_paquete(self):
        self.assertIn('data/skill/*', (SOURCE / 'pyproject.toml').read_text(encoding='utf-8'))
        self.assertTrue((SOURCE / 'oracle_factory/data/skill/SKILL.md').is_file())


class Comando(unittest.TestCase):
    # --- sk2: el comando skill la muestra y la instala sin pisar nada ajeno -----------------------------------------------------
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'producto'
        self.root.mkdir()
        self.casa = Path(self.tmp.name) / 'casa'
        (self.casa / '.claude').mkdir(parents=True)
        (self.casa / '.claude/settings.json').write_text('{"mio": true}\n')
        self.env = {**os.environ, 'PYTHONPATH': str(SOURCE), 'GIT_CEILING_DIRECTORIES': self.tmp.name, 'HOME': str(self.casa),
                    'XDG_CONFIG_HOME': str(self.casa / '.config')}
        for args in (('init', '-q', '-b', 'main'), ('config', 'user.name', 'Ana'), ('config', 'user.email', 'ana@x.invalid')):
            subprocess.run(['git', *args], cwd=self.root, env=self.env, check=True, capture_output=True)
        self.assertEqual(en_terminal([*CLI, 'init'], cwd=self.root, env=self.env, entrada='1\n1\n1\n').returncode, 0)
        self.destino = self.root / skill.RUTA_EN_EL_PROYECTO

    def correr(self, *args):
        return subprocess.run([*CLI, 'skill', *args], cwd=self.root, env=self.env, capture_output=True, text=True, stdin=subprocess.DEVNULL)

    def arbol(self, carpeta):
        return {p.relative_to(carpeta).as_posix(): p.read_bytes() for p in sorted(carpeta.rglob('*')) if p.is_file() and '.git/' not in p.as_posix()}

    def test_sk2_mostrarla_imprime_el_texto_y_no_escribe_nada(self):
        antes = self.arbol(self.root)
        r = self.correr()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, skill.texto())
        self.assertEqual(self.arbol(self.root), antes)
        self.assertFalse((self.root / '.claude').exists())

    def test_sk2_instalarla_la_escribe_en_el_proyecto_y_dice_donde(self):
        r = self.correr('--instalar')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.destino.read_text(encoding='utf-8'), skill.texto())
        self.assertIn('.claude/skills/oracle-factory/SKILL.md', r.stdout)
        self.assertIn('instalada', r.stdout)

    def test_sk2_instalarla_otra_vez_no_cambia_nada_y_lo_dice(self):
        self.correr('--instalar')
        marca = self.destino.stat().st_mtime_ns
        r = self.correr('--instalar')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('sin cambios', r.stdout)
        self.assertEqual(self.destino.stat().st_mtime_ns, marca)

    def test_sk2_un_archivo_distinto_no_se_pisa_salvo_con_forzar(self):
        self.destino.parent.mkdir(parents=True)
        self.destino.write_text('el mío\n')
        r = self.correr('--instalar')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('--forzar', r.stderr)
        self.assertEqual(self.destino.read_text(), 'el mío\n')
        r = self.correr('--instalar', '--forzar')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('reemplazada', r.stdout)
        self.assertEqual(self.destino.read_text(encoding='utf-8'), skill.texto())

    def test_sk2_no_sigue_enlaces_simbolicos_ni_siquiera_con_forzar(self):
        fuera = Path(self.tmp.name) / 'fuera.md'
        fuera.write_text('no tocar\n')
        self.destino.parent.mkdir(parents=True)
        self.destino.symlink_to(fuera)
        for args in (('--instalar',), ('--instalar', '--forzar')):
            r = self.correr(*args)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn('enlaces simbólicos', r.stderr)
            self.assertEqual(fuera.read_text(), 'no tocar\n')
        self.destino.unlink()
        real = Path(self.tmp.name) / 'carpeta_real'
        real.mkdir()
        (self.root / '.claude/skills/oracle-factory').rmdir()
        (self.root / '.claude/skills/oracle-factory').symlink_to(real)
        r = self.correr('--instalar')
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(list(real.iterdir()), [])

    def test_sk2_nada_fuera_del_proyecto_ni_en_la_configuracion_personal(self):
        antes_casa = self.arbol(self.casa)
        antes_otros = {p for p in Path(self.tmp.name).iterdir()}
        self.correr('--instalar')
        self.correr('--instalar', '--forzar')
        self.assertEqual(self.arbol(self.casa), antes_casa)
        self.assertEqual({p for p in Path(self.tmp.name).iterdir()}, antes_otros)
        nuevos = set(self.arbol(self.root)) - {'.factory/' + n for n in ()}
        self.assertIn('.claude/skills/oracle-factory/SKILL.md', nuevos)

    def test_sk2_instalar_no_refresca_el_conocimiento_generado(self):
        antes = self.arbol(self.root / 'kb') if (self.root / 'kb').is_dir() else {}
        self.correr('--instalar')
        despues = self.arbol(self.root / 'kb') if (self.root / 'kb').is_dir() else {}
        self.assertEqual(antes, despues)
        self.assertIn('skill', __import__('oracle_factory.cli', fromlist=['x']).SOLO_LECTURA)


class Guia(unittest.TestCase):
    # --- sk3: la guía para agentes nombra la skill -------------------------------------------------------------------------------
    def test_sk3_la_guia_nombra_el_comando_y_la_ruta_de_instalacion(self):
        texto = agentes.bloque('confirmacion')
        self.assertIn('`oracle-factory skill`', texto)
        self.assertIn('`oracle-factory skill --instalar`', texto)
        self.assertIn('.claude/skills/oracle-factory/SKILL.md', texto)

    def test_sk3_si_la_guia_pierde_la_mencion_agentes_verificar_falla(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name) / 'producto'
        root.mkdir()
        env = {**os.environ, 'PYTHONPATH': str(SOURCE), 'GIT_CEILING_DIRECTORIES': tmp.name}
        for args in (('init', '-q', '-b', 'main'), ('config', 'user.name', 'Ana'), ('config', 'user.email', 'ana@x.invalid')):
            subprocess.run(['git', *args], cwd=root, env=env, check=True, capture_output=True)
        self.assertEqual(en_terminal([*CLI, 'init'], cwd=root, env=env, entrada='1\n1\n1\n').returncode, 0)
        self.assertEqual(en_terminal([*CLI, 'agentes'], cwd=root, env=env, entrada='').returncode, 0)
        self.assertEqual(en_terminal([*CLI, 'agentes', '--verificar'], cwd=root, env=env, entrada='').returncode, 0)
        guia = root / 'AGENTS.md'
        self.assertIn('oracle-factory skill', guia.read_text())
        guia.write_text(guia.read_text().replace('`oracle-factory skill --instalar`', '`otra cosa`'))
        self.assertNotEqual(en_terminal([*CLI, 'agentes', '--verificar'], cwd=root, env=env, entrada='').returncode, 0)


if __name__ == '__main__':
    unittest.main()
