"""La puerta local de salida: escenarios pu1–pu3, con Git de verdad (un remoto temporal) y secretos armados al vuelo.

Ningún secreto está escrito entero en este archivo (la puerta lo bloquearía al empujarlo): se arman al ejecutar."""
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE))
from oracle_factory import cli, puerta  # noqa: E402

PYTHON_CLI = [sys.executable, '-c', 'import sys; from oracle_factory.cli import main; sys.exit(main())']
ENTORNO = {**os.environ, 'PYTHONPATH': str(SOURCE), 'GIT_AUTHOR_NAME': 'Persona fixture', 'GIT_AUTHOR_EMAIL': 'p@example.invalid',
           'GIT_COMMITTER_NAME': 'Persona fixture', 'GIT_COMMITTER_EMAIL': 'p@example.invalid',
           'GIT_CEILING_DIRECTORIES': str(Path(tempfile.gettempdir()).resolve())}
# Cada uno armado en dos pedazos: el texto del archivo nunca contiene la credencial entera.
GITHUB = 'ghp' + '_' + 'a1B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6q7R8'
AWS = 'AKIA' + 'IOSFODNN7EXAMPLE'
PYPI = 'pypi' + '-' + 'AgEIcHlwaS5vcmcC' + 'x9' * 30
SLACK = 'xoxb' + '-' + '1234567890-abcdefghij'
GOOGLE = 'AIza' + 'Sy' + 'A1b2C3d4' * 4 + 'e'  # AIza + exactamente 35 caracteres, como las reales
SK = 'sk' + '-' + 'A1b2' * 10
SK_ANT = 'sk' + '-ant-' + 'A1b2C3' * 5
CLAVE_PRIVADA = '-----BEGIN ' + 'RSA PRIVATE KEY-----'
ASIGNACION = 'token = "' + 'a1b2c3d4e5f6g7h8i9' + '"'
CASOS = {'clave privada': CLAVE_PRIVADA, 'clave de AWS': f'aws = "{AWS}"', 'token de GitHub': f'x = "{GITHUB}"',
         'token de PyPI': f'x = "{PYPI}"', 'token de Slack': f'x = "{SLACK}"', 'clave de Google': f'x = "{GOOGLE}"',
         'clave sk-': f'x = "{SK}"', 'asignación sospechosa': ASIGNACION}


def log(commit, archivo, *lineas, desde=1):
    """El texto de `git log -p -U0` de un commit que agrega esas líneas a un archivo."""
    return (f'commit:{commit}\n\ndiff --git a/{archivo} b/{archivo}\nindex 1..2 100644\n--- a/{archivo}\n+++ b/{archivo}\n'
            f'@@ -0,0 +{desde},{len(lineas)} @@\n' + ''.join(f'+{l}\n' for l in lineas))


class Detectar(unittest.TestCase):
    # --- pu1: la puerta detecta secretos --------------------------------------------------------------------------------
    def test_pu1_cada_tipo_de_credencial_se_nombra_con_archivo_linea_y_commit(self):
        for tipo, linea in CASOS.items():
            with self.subTest(tipo=tipo):
                [h] = puerta.hallazgos(log('abc1234def', 'src/config.py', 'x = 1', linea))
                self.assertEqual((h['archivo'], h['linea'], h['commit'], h['tipo']), ('src/config.py', 2, 'abc1234def', tipo))

    def test_pu1_el_valor_sale_tapado_y_nunca_entero(self):
        for tipo, linea in CASOS.items():
            with self.subTest(tipo=tipo):
                [h] = puerta.hallazgos(log('abc1234', 'a.py', linea))
                secreto = linea.split('"')[1] if '"' in linea else linea
                self.assertNotIn(secreto, h['vista'])
                self.assertLessEqual(len(h['vista']), 12)
                self.assertNotIn(secreto, puerta.texto_de_hallazgos([h]))

    def test_pu1_un_token_de_otro_tipo_de_anthropic_tambien(self):
        [h] = puerta.hallazgos(log('abc1234', 'a.py', f'k = "{SK_ANT}"'))
        self.assertEqual(h['tipo'], 'clave sk-')

    def test_pu1_las_palabras_no_son_secretos(self):
        for linea in ('# el secreto está en el vault', 'la palabra token y password en un texto', 'def password(): pass',
                      'password = "pedir-una-contraseña-larga"', 'token = "x1"', 'api_key = os.environ["API_KEY"]',
                      'secret = "una_constante_larga_sin_digitos"', 'x = "ghp_corto"', 'AKIA no es una clave', 'sk-corto',
                      'la sección «Tokens» del informe', 'secreto = "abcdefghijklmnopqrstuvwxyz"'):
            with self.subTest(linea=linea):
                self.assertEqual(puerta.hallazgos(log('abc1234', 'a.md', linea)), [])

    def test_pu1_la_marca_de_exencion_salva_solo_esa_linea(self):
        marcada = f'x = "{GITHUB}"  # factory:secreto-ok'
        hs = puerta.hallazgos(log('abc1234', 'a.py', marcada, f'y = "{GITHUB}"'))
        self.assertEqual([h['linea'] for h in hs], [2])

    def test_pu1_solo_cuentan_las_lineas_agregadas_y_los_numeros_siguen_los_hunks(self):
        texto = ('commit:aaa1111\n\ndiff --git a/x.py b/x.py\nindex 1..2\n--- a/x.py\n+++ b/x.py\n@@ -3 +3,0 @@\n'
                 f'-quitada = "{GITHUB}"\n@@ -9,0 +20,2 @@\n+ok = 1\n+bad = "{GITHUB}"\n')
        [h] = puerta.hallazgos(texto)
        self.assertEqual((h['archivo'], h['linea']), ('x.py', 21))  # la línea quitada no cuenta; la agregada es la 21

    def test_pu1_cada_commit_se_atribuye_al_suyo_y_cada_archivo_al_suyo(self):
        texto = log('aaa1111', 'uno.py', 'a = 1') + log('bbb2222', 'dos.py', f'x = "{GITHUB}"') + log('ccc3333', 'tres.py', f'y = "{AWS}"')
        self.assertEqual([(h['commit'], h['archivo']) for h in puerta.hallazgos(texto)], [('bbb2222', 'dos.py'), ('ccc3333', 'tres.py')])

    def test_pu1_dos_archivos_en_el_mismo_commit_se_atribuyen_cada_uno_al_suyo(self):
        texto = ('commit:abc1234\n\ndiff --git a/uno.py b/uno.py\nindex 1..2 100644\n--- a/uno.py\n+++ b/uno.py\n@@ -0,0 +1,2 @@\n+a = 1\n+b = 2\n'
                 'diff --git a/dos.py b/dos.py\nindex 3..4 100644\n--- a/dos.py\n+++ b/dos.py\n@@ -0,0 +1,3 @@\n+c = 3\n+d = 4\n'
                 f'+e = "{GITHUB}"\n')
        [h] = puerta.hallazgos(texto)
        self.assertEqual((h['archivo'], h['linea']), ('dos.py', 3))  # el segundo archivo, con su propia numeración

    def test_pu1_una_cabecera_con_guiones_no_se_lee_como_linea_agregada(self):
        texto = f'commit:abc1234\n\ndiff --git a/x b/x\n--- a/x\n+++ b/x\n@@ -1 +1 @@\n-viejo\n+++ no es cabecera = "{GITHUB}"\n'
        self.assertEqual(len(puerta.hallazgos(texto)), 1)  # dentro del hunk, «+++ …» es una línea agregada que empieza con ++

    def test_pu1_un_archivo_borrado_o_binario_no_rompe(self):
        texto = ('commit:abc1234\n\ndiff --git a/x.bin b/x.bin\nindex 1..2\nBinary files a/x.bin and b/x.bin differ\n'
                 'diff --git a/y b/y\ndeleted file mode 100644\n--- a/y\n+++ /dev/null\n@@ -1 +0,0 @@\n-viejo\n')
        self.assertEqual(puerta.hallazgos(texto), [])

    def test_pu1_una_linea_enorme_se_mira_entera_y_no_cuelga(self):
        import time
        linea = 'x' * 400_000 + f' "{GITHUB}" ' + 'y' * 10  # el secreto queda después de los 300 000 caracteres
        t = time.monotonic()
        self.assertEqual(len(puerta.hallazgos(log('abc1234', 'a.json', linea))), 1)
        self.assertLess(time.monotonic() - t, 5)
        patologica = 'token' + '_' * 400_000 + ' ' * 1000 + 'a1' * 100  # nombre de credencial que no se asigna nunca: no puede ser cuadrático
        t = time.monotonic()
        puerta.hallazgos(log('abc1234', 'a.json', patologica))
        self.assertLess(time.monotonic() - t, 5)

    def test_pu1_las_claves_temporales_de_aws_tambien(self):
        [h] = puerta.hallazgos(log('abc1234', 'a.sh', 'export K=' + 'ASIA' + 'IOSFODNN7EXAMPLE'))
        self.assertEqual(h['tipo'], 'clave de AWS')

    def test_pu1_una_asignacion_con_triples_comillas_se_marca(self):
        for comillas in ('"""', "'''"):
            with self.subTest(comillas=comillas):
                [h] = puerta.hallazgos(log('abc1234', 'a.py', 'token = ' + comillas + 'a1b2c3d4e5f6g7h8i9' + comillas))
                self.assertEqual(h['tipo'], 'asignación sospechosa')

    def test_pu1_un_commit_de_merge_con_un_secreto_propio_se_marca_y_el_texto_del_otro_lado_no(self):
        # --cc: sólo lo que el merge agrega frente a todos sus padres, en el formato combinado («@@@», «++»)
        merge = (f'commit:abc1234\n\ndiff --cc config.py\nindex 1,2..3\n--- a/config.py\n+++ b/config.py\n@@@ -1,1 -1,1 +1,2 @@@\n'
                 f'++TOKEN = "{GITHUB}"\n +otra = "{GITHUB}"\n- viejo\n')
        encontrados = puerta.hallazgos(merge)
        self.assertEqual([(h['archivo'], h['linea'], h['commit']) for h in encontrados], [('config.py', 1, 'abc1234')])

    def test_pu1_un_merge_pulpo_de_tres_padres_tambien_se_mira(self):
        pulpo = (f'commit:abc1234\n\ndiff --cc config.py\nindex 1,2,3..4\n--- a/config.py\n+++ b/config.py\n@@@@ -1,1 -1,1 -1,1 +1,2 @@@@\n'
                 f'+++TOKEN = "{GITHUB}"\n++ otra = "{GITHUB}"\n')
        self.assertEqual([(h['archivo'], h['linea']) for h in puerta.hallazgos(pulpo)], [('config.py', 1)])

    def test_pu1_en_un_merge_la_linea_cuenta_tambien_las_que_conserva_de_los_padres(self):
        merge = ('commit:abc1234\n\ndiff --cc config.py\nindex 1,2..3\n--- a/config.py\n+++ b/config.py\n@@@ -1,1 -1,1 +1,4 @@@\n'
                 f' +uno\n+ dos\n- quitada del padre\n++tres\n++TOKEN = "{GITHUB}"\n')
        self.assertEqual([h['linea'] for h in puerta.hallazgos(merge)], [4])  # uno=1, dos=2, tres=3, el secreto=4 (la quitada no está)

    def test_pu1_una_clave_de_google_que_termina_en_guion_tambien(self):
        clave = 'AIza' + 'Sy' + 'A1b2C3d4' * 4 + '-'
        self.assertEqual(len(clave), 39)
        self.assertEqual([h['tipo'] for h in puerta.hallazgos(log('abc1234', 'a.py', f"K = '{clave}'"))], ['clave de Google'])

    def test_pu1_las_rutas_con_escapes_de_git_se_decodifican(self):
        for escapada, real in (('"b/test\\"quote.py"', 'test"quote.py'), ('"b/dise\\303\\261o.py"', 'diseño.py'), ('"b/a\\tb.py"', 'a\tb.py'),
                               ('"b/a\\\\b.py"', 'a\\b.py')):
            with self.subTest(real=real):
                texto = f'commit:abc1234\n\ndiff --git a/x b/x\n--- a/x\n+++ {escapada}\n@@ -0,0 +1 @@\n+x = "{GITHUB}"\n'
                self.assertEqual(puerta.hallazgos(texto)[0]['archivo'], real)

    def test_pu1_una_ruta_con_espacios_o_comillas_sale_con_su_nombre_real(self):
        texto = ('commit:abc1234\n\ndiff --git "a/con espacio.py" "b/con espacio.py"\n--- "a/con espacio.py"\t\n+++ "b/con espacio.py"\t\n'
                 f'@@ -0,0 +1 @@\n+x = "{GITHUB}"\n')
        self.assertEqual(puerta.hallazgos(texto)[0]['archivo'], 'con espacio.py')
        texto = texto.replace('"b/con espacio.py"', 'b/con espacio.py')
        self.assertEqual(puerta.hallazgos(texto)[0]['archivo'], 'con espacio.py')

    def test_pu1_el_documento_nombra_cada_tipo_de_credencial_el_codigo_de_salida_y_la_marca(self):
        documento = (SOURCE / 'docs/puerta.md').read_text(encoding='utf-8')
        for etiqueta in ('clave privada', 'clave de AWS', 'token de GitHub', 'PyPI', 'Slack', 'clave de Google', 'sk-', 'asignación sospechosa'):
            with self.subTest(etiqueta=etiqueta):
                self.assertIn(etiqueta.replace('token de ', '').replace('asignación sospechosa', 'asignación'), documento)
        tipos_del_codigo = {tipo for tipo, _ in puerta.PATRONES} | {'asignación sospechosa'}
        self.assertEqual(tipos_del_codigo, {tipo for tipo in CASOS})  # y los casos de esta prueba cubren todos los del código
        self.assertIn(puerta.EXENCION, documento)
        self.assertIn(f'código {puerta.CODIGO_BLOQUEO}', documento)
        self.assertIn('--no-verify', documento)
        self.assertIn('Sólo lectura', documento)
        for nombre, *_ in puerta.VERIFICACIONES:
            self.assertIn(f'`{nombre} --verificar`' if nombre not in puerta.SIN_FLAG else f'`{nombre}`', documento)  # verificar no tiene el flag

    def test_pu1_el_contrato_del_verificador_nombra_exactamente_los_casos_que_existen(self):
        """Un nombre de caso mal escrito en tools/verify_puerta_local.py deja la evidencia en rojo sin que el producto falle."""
        from tools import verify_puerta_local as verificador

        def ids(suite):
            for x in suite:
                yield from ids(x) if isinstance(x, unittest.TestSuite) else [x.id()]
        reales = {'.'.join(i.split('.')[-2:]) for i in ids(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))
                  if re.search(r'\.test_pu\d_', i)}
        contratados = [n for nombres in verificador.CONTRACTS.values() for n in nombres]
        self.assertEqual(len(contratados), len(set(contratados)))
        self.assertEqual(set(contratados), reales)
        numeros = {'la_puerta_detecta_secretos_en_todos_los_commits_que_se_publican': '1', 'la_puerta_corre_las_verificaciones_del_proyecto': '2',
                   'el_hook_pre_push_llama_a_la_puerta_con_lo_que_se_empuja': '3', 'la_puerta_no_modifica_el_arbol_de_trabajo': '4'}
        self.assertEqual(set(verificador.CONTRACTS), set(numeros))
        for requisito, nombres in verificador.CONTRACTS.items():
            for nombre in nombres:
                self.assertRegex(nombre, rf'\.test_pu{numeros[requisito]}_')

    def test_pu1_el_texto_nombra_cada_hallazgo(self):
        texto = puerta.texto_de_hallazgos(puerta.hallazgos(log('abc1234def', 'src/c.py', f'x = "{GITHUB}"')))
        self.assertIn('src/c.py:1', texto)
        self.assertIn('abc1234', texto)
        self.assertIn('token de GitHub', texto)


class Verificaciones(unittest.TestCase):
    @staticmethod
    def verificar(falla=()):
        llamadas = []

        def correr(argv):
            llamadas.append(argv[0])
            return (1, f'{argv[0]} está vieja\nlínea dos') if argv[0] in falla else (0, f'{argv[0]} al día')
        correr.llamadas = llamadas
        return correr

    # --- pu2: la puerta corre las verificaciones del proyecto ---------------------------------------------------------------
    def test_pu2_las_tres_verificaciones_pasan(self):
        v = self.verificar()
        self.assertEqual(puerta.verificaciones(v), ([], [], []))
        self.assertEqual(v.llamadas, ['agentes', 'kb', 'resumen', 'verificar'])

    def test_pu2_una_que_falla_se_nombra_y_las_demas_se_corren_igual(self):
        v = self.verificar(falla=('agentes',))
        problemas, avisos, omitidas = puerta.verificaciones(v)
        self.assertEqual((avisos, omitidas), ([], []))
        self.assertEqual(len(problemas), 1)
        self.assertIn('agentes', problemas[0])
        self.assertIn('vieja', problemas[0])
        self.assertEqual(v.llamadas, ['agentes', 'kb', 'resumen', 'verificar'])

    def test_pu2_un_kb_o_un_resumen_vencidos_avisan_y_no_bloquean(self):
        problemas, avisos, omitidas = puerta.verificaciones(self.verificar(falla=('kb', 'resumen')))
        self.assertEqual(problemas, [])
        self.assertEqual([a.split(':')[0] for a in avisos], ['kb', 'resumen'])
        self.assertEqual(omitidas, [])

    def test_pu2_la_guia_vieja_bloquea_y_las_otras_se_informan_como_aviso(self):
        problemas, avisos, _ = puerta.verificaciones(self.verificar(falla=('agentes', 'kb')))
        self.assertEqual([p.split(':')[0] for p in problemas], ['agentes'])
        self.assertEqual([a.split(':')[0] for a in avisos], ['kb'])

    def test_pu2_la_verificacion_pide_siempre_verificar_y_no_escribe(self):
        argumentos = []
        puerta.verificaciones(lambda argv: (argumentos.append(argv) or (0, '')))  # noqa: E501
        self.assertEqual(argumentos, [['agentes', '--verificar'], ['kb', '--verificar'], ['resumen', '--verificar'], ['verificar']])

    def test_pu2_una_verificacion_cuyo_archivo_no_existe_se_omite_y_no_bloquea(self):
        v = self.verificar(falla=('kb', 'resumen', 'agentes'))
        problemas, avisos, omitidas = puerta.verificaciones(v, existe=lambda archivo: archivo == 'AGENTS.md')
        self.assertEqual((omitidas, avisos), (['kb', 'resumen', 'verificar'], []))
        self.assertEqual([p.split(':')[0] for p in problemas], ['agentes'])  # la que existe y está vieja, sí
        self.assertEqual(v.llamadas, ['agentes'])  # y las omitidas ni se corren

    def test_pu2_la_puerta_con_un_kb_vencido_pasa_y_lo_dice_sin_decir_que_esta_al_dia(self):
        limpio = lambda argv: SimpleNamespace(returncode=0, stdout=log('abc1234', 'a.py', 'x = 1'))  # noqa: E731
        codigo, texto = puerta.correr(limpio, [['HEAD']], self.verificar(falla=('kb',)))
        self.assertEqual(codigo, 0)
        self.assertIn('! vencidos, no bloquean', texto)
        self.assertIn('kb: kb está vieja', texto)
        self.assertIn('✓ verificaciones: agentes, resumen, verificar al día', texto)  # kb no figura entre las que están al día
        self.assertNotIn('--no-verify', texto)
        codigo, texto = puerta.correr(limpio, [['HEAD']], self.verificar(falla=('agentes', 'kb')))
        self.assertEqual(codigo, puerta.CODIGO_BLOQUEO)
        self.assertIn('✗ verificaciones', texto)
        self.assertIn('! vencidos, no bloquean', texto)
        self.assertIn('✓ al día: resumen', texto)  # lo que sí está al día se informa igual cuando otra falla
        codigo, texto = puerta.correr(limpio, [['HEAD']], self.verificar(falla=('agentes',)), existe=lambda archivo: archivo != 'kb/README.md')
        self.assertEqual(codigo, puerta.CODIGO_BLOQUEO)
        self.assertIn('se omiten kb', texto)  # y lo omitido también

    def test_pu2_con_todas_omitidas_la_puerta_dice_que_ninguna_aplica_y_pasa(self):
        limpio = lambda argv: SimpleNamespace(returncode=0, stdout=log('abc1234', 'a.py', 'x = 1'))  # noqa: E731
        codigo, texto = puerta.correr(limpio, [['HEAD']], self.verificar(falla=('agentes',)), existe=lambda archivo: False)
        self.assertEqual(codigo, 0)
        self.assertIn('ninguna aplicable', texto)
        codigo, texto = puerta.correr(limpio, [['HEAD']], self.verificar(), existe=lambda archivo: archivo != 'kb/README.md')
        self.assertEqual(codigo, 0)
        self.assertIn('se omiten kb', texto)

    def test_pu2_la_puerta_junta_secretos_y_verificaciones_en_un_resultado(self):
        ejecutar = lambda argv: SimpleNamespace(returncode=0, stdout=log('abc1234', 'a.py', f'x = "{GITHUB}"'))  # noqa: E731
        codigo, texto = puerta.correr(ejecutar, [['HEAD']], self.verificar(falla=('agentes',)))
        self.assertEqual(codigo, puerta.CODIGO_BLOQUEO)
        self.assertIn('✗ secretos', texto)
        self.assertIn('✗ secretos', texto)
        self.assertIn('--no-verify', texto)
        limpio = lambda argv: SimpleNamespace(returncode=0, stdout=log('abc1234', 'a.py', 'x = 1'))  # noqa: E731
        codigo, texto = puerta.correr(limpio, [['HEAD']], self.verificar())
        self.assertEqual(codigo, 0)
        self.assertIn('✓ secretos', texto)
        self.assertIn('✓ verificaciones', texto)
        self.assertNotIn('--no-verify', texto)

    def test_pu2_si_git_falla_al_leer_los_commits_la_puerta_no_dice_que_esta_limpio(self):
        roto = lambda argv: SimpleNamespace(returncode=128, stdout='', stderr='fatal: mala revisión')  # noqa: E731
        with self.assertRaises(puerta.PuertaRota):
            puerta.secretos(roto, ['mala'])


class Rangos(unittest.TestCase):
    CERO = '0' * 40

    @staticmethod
    def git(conocidos=()):
        return lambda argv: SimpleNamespace(returncode=0 if any(c in " ".join(argv) for c in conocidos) else 1, stdout='')

    # --- pu3: lo que Git le pasa al hook pre-push --------------------------------------------------------------------------
    def test_pu3_una_rama_nueva_mira_lo_que_ningun_remoto_tiene(self):
        entrada = f'refs/heads/x {"a" * 40} refs/heads/x {self.CERO}\n'
        self.assertEqual(puerta.rangos_del_hook(entrada, self.git()), [['a' * 40, '--not', '--remotes']])

    def test_pu3_una_rama_existente_mira_desde_el_sha_remoto(self):
        entrada = f'refs/heads/main {"a" * 40} refs/heads/main {"b" * 40}\n'
        self.assertEqual(puerta.rangos_del_hook(entrada, self.git(conocidos=('b' * 40,))), [[f'{"b" * 40}..{"a" * 40}']])

    def test_pu3_los_repositorios_con_hashes_de_64_caracteres_tambien_se_miran(self):
        local, remoto = 'a' * 64, 'b' * 64
        ejecutar = lambda argv: SimpleNamespace(returncode=0, stdout='')  # noqa: E731
        self.assertEqual(puerta.rangos_del_hook(f'refs/heads/m {local} refs/heads/m {remoto}\n', ejecutar), [[f'{remoto}..{local}']])
        self.assertEqual(puerta.rangos_del_hook(f'refs/heads/m {"0" * 64} refs/heads/m {remoto}\n', ejecutar), [])
        self.assertEqual(puerta.rangos_del_hook(f'refs/heads/m {local} refs/heads/m {"0" * 64}\n', ejecutar), [[local, '--not', '--remotes']])

    def test_pu3_borrar_una_rama_remota_no_se_mira(self):
        entrada = f'(delete) {self.CERO} refs/heads/vieja {"b" * 40}\n'
        self.assertEqual(puerta.rangos_del_hook(entrada, self.git()), [])

    def test_pu3_un_sha_remoto_que_no_tenemos_cae_al_modo_de_rama_nueva(self):
        entrada = f'refs/heads/main {"a" * 40} refs/heads/main {"c" * 40}\n'
        self.assertEqual(puerta.rangos_del_hook(entrada, self.git(conocidos=())), [['a' * 40, '--not', '--remotes']])

    def test_pu3_varias_ramas_en_un_push_dan_un_rango_cada_una_y_las_lineas_raras_se_ignoran(self):
        entrada = (f'refs/heads/a {"a" * 40} refs/heads/a {self.CERO}\n\n'
                   f'refs/heads/b {"b" * 40} refs/heads/b {"d" * 40}\nbasura\n(delete) {self.CERO} refs/heads/c {"e" * 40}\n')
        rangos = puerta.rangos_del_hook(entrada, self.git(conocidos=('d' * 40,)))
        self.assertEqual(rangos, [['a' * 40, '--not', '--remotes'], [f'{"d" * 40}..{"b" * 40}']])


class HookReal(unittest.TestCase):
    """El hook instalado por `oracle-factory hooks`, empujando de verdad a un remoto local."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.root, self.remoto = base / 'producto', base / 'remoto.git'
        self.root.mkdir()
        self.git('init', '-q', '--bare', str(self.remoto), cwd=base)
        self.git('init', '-q', '-b', 'main')
        self.git('remote', 'add', 'origin', str(self.remoto))
        self.salida = self.cli('init')
        self.cli('kb')  # lo que un proyecto real ya tiene generado: sin esto, --verificar (con razón) bloquea
        self.cli('resumen')
        self.git('add', '-A')
        self.git('commit', '-qm', 'init')

    def git(self, *args, cwd=None, esperado=0):
        r = subprocess.run(['git', *args], cwd=cwd or self.root, env=ENTORNO, capture_output=True, text=True, stdin=subprocess.DEVNULL)
        if esperado is not None:
            self.assertEqual(r.returncode, esperado, r.stderr)
        return r

    def cli(self, *args):
        r = subprocess.run([*PYTHON_CLI, '--agente', 'claude-code', *args], cwd=self.root, env=ENTORNO, capture_output=True, text=True,
                           stdin=subprocess.DEVNULL)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout

    def commit(self, archivo, texto, mensaje='cambio'):
        (self.root / archivo).write_text(texto + '\n')
        self.git('add', '-A')
        self.git('commit', '-qm', mensaje)

    def empujar(self, *args):
        r = self.git('push', '-q', *args, esperado=None)
        return r.returncode, r.stdout + r.stderr

    def hook(self):
        return self.root / '.git/hooks/pre-push'

    # --- pu3: el hook pre-push --------------------------------------------------------------------------------------------
    def test_pu3_hooks_instala_el_pre_push_y_lo_dice(self):
        self.assertTrue(self.hook().is_file())
        self.assertTrue(os.access(self.hook(), os.X_OK))
        self.assertIn('pre-push', self.salida)
        self.assertIn('kb o un resumen vencidos, o un cambio inconsistente (`verificar`), sólo avisan', self.salida)  # el mensaje dice la política real
        self.assertNotIn('verificaciones vencidas se bloquea', self.salida)
        self.assertIn('puerta', self.hook().read_text())

    def test_pu3_un_push_limpio_pasa(self):
        self.commit('a.py', 'x = 1')
        codigo, salida = self.empujar('origin', 'main')
        self.assertEqual(codigo, 0, salida)
        self.assertTrue(self.git('--git-dir', str(self.remoto), 'rev-parse', 'main').stdout.strip())

    def test_pu3_un_push_con_un_secreto_se_bloquea_y_lo_nombra_sin_mostrarlo(self):
        self.commit('config.py', f'TOKEN = "{GITHUB}"')
        codigo, salida = self.empujar('origin', 'main')
        self.assertNotEqual(codigo, 0)
        self.assertIn('config.py', salida)
        self.assertIn('token de GitHub', salida)
        self.assertNotIn(GITHUB, salida)
        self.assertEqual(self.git('--git-dir', str(self.remoto), 'rev-parse', '--verify', '-q', 'main', esperado=None).returncode, 1)  # no llegó

    def test_pu3_un_secreto_quitado_en_el_commit_siguiente_igual_bloquea(self):
        self.commit('config.py', f'TOKEN = "{GITHUB}"', 'agrega')
        self.commit('config.py', 'TOKEN = ""', 'quita')
        codigo, salida = self.empujar('origin', 'main')
        self.assertNotEqual(codigo, 0)
        self.assertIn('config.py', salida)

    def test_pu3_un_secreto_escrito_al_resolver_un_merge_bloquea(self):
        self.commit('config.py', 'TOKEN = ""', 'base')
        self.git('checkout', '-q', '-b', 'otra')
        self.commit('otra.py', 'z = 3', 'lado de la otra rama')
        self.git('checkout', '-q', 'main')
        self.commit('b.py', 'y = 2', 'lado de main')
        self.git('merge', '-q', '--no-ff', '--no-commit', 'otra')
        (self.root / 'config.py').write_text(f'TOKEN = "{GITHUB}"\n')  # el secreto aparece sólo en el commit del merge
        self.git('add', '-A')
        self.git('commit', '-qm', 'merge con secreto')
        codigo, salida = self.empujar('origin', 'main')
        self.assertNotEqual(codigo, 0, salida)
        self.assertIn('token de GitHub', salida)
        self.assertNotIn(GITHUB, salida)

    def test_pu3_un_merge_limpio_con_el_contenido_de_la_otra_rama_pasa(self):
        self.commit('config.py', 'TOKEN = ""', 'base')
        self.git('checkout', '-q', '-b', 'otra')
        self.commit('otra.py', 'z = 3', 'lado de la otra rama')
        self.git('checkout', '-q', 'main')
        self.commit('b.py', 'y = 2', 'lado de main')
        self.git('merge', '-q', '--no-ff', '-m', 'merge limpio', 'otra')
        codigo, salida = self.empujar('origin', 'main')
        self.assertEqual(codigo, 0, salida)

    def test_pu3_solo_se_miran_los_commits_que_el_remoto_todavia_no_tiene(self):
        self.commit('config.py', f'TOKEN = "{GITHUB}"', 'ya publicado')
        self.assertEqual(self.empujar('--no-verify', 'origin', 'main')[0], 0)  # alguien lo publicó salteando la puerta
        self.commit('b.py', 'y = 2', 'limpio')
        codigo, salida = self.empujar('origin', 'main')
        self.assertEqual(codigo, 0, salida)

    def test_pu3_una_rama_nueva_se_mira_desde_lo_que_el_remoto_no_tiene(self):
        self.commit('a.py', 'x = 1')
        self.assertEqual(self.empujar('origin', 'main')[0], 0)
        self.git('checkout', '-qb', 'nueva')
        self.commit('n.py', 'z = 3', 'en la rama')
        self.assertEqual(self.empujar('origin', 'nueva')[0], 0)
        self.git('checkout', '-qb', 'mala')
        self.commit('m.py', f'k = "{AWS}"', 'con clave')
        codigo, salida = self.empujar('origin', 'mala')
        self.assertNotEqual(codigo, 0)
        self.assertIn('clave de AWS', salida)

    def test_pu3_borrar_una_rama_remota_pasa_aunque_tuviera_un_secreto(self):
        self.commit('a.py', 'x = 1')
        self.empujar('origin', 'main')
        self.git('checkout', '-qb', 'vieja')
        self.commit('c.py', f'k = "{AWS}"')
        self.assertEqual(self.empujar('--no-verify', 'origin', 'vieja')[0], 0)
        self.git('checkout', '-q', 'main')
        codigo, salida = self.empujar('origin', ':vieja')
        self.assertEqual(codigo, 0, salida)

    def test_pu3_una_puerta_que_no_puede_mirar_sale_con_el_codigo_2_y_nunca_con_el_de_bloqueo(self):
        r = subprocess.run([*PYTHON_CLI, 'puerta', 'una-revision-que-no-existe'], cwd=self.root, env=ENTORNO, capture_output=True,
                           text=True, stdin=subprocess.DEVNULL)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertNotEqual(r.returncode, puerta.CODIGO_BLOQUEO)
        self.assertIn('Aviso', r.stderr)
        self.assertIn('el push sigue', r.stderr)

    def test_pu3_la_puerta_a_mano_sin_argumentos_mira_lo_que_el_remoto_no_tiene(self):
        self.commit('config.py', f'TOKEN = "{GITHUB}"')
        r = subprocess.run([*PYTHON_CLI, 'puerta'], cwd=self.root, env=ENTORNO, capture_output=True, text=True, stdin=subprocess.DEVNULL)
        self.assertEqual(r.returncode, puerta.CODIGO_BLOQUEO, r.stdout + r.stderr)
        self.assertIn('config.py', r.stdout)
        self.assertEqual(self.empujar('--no-verify', 'origin', 'main')[0], 0)
        r = subprocess.run([*PYTHON_CLI, 'puerta'], cwd=self.root, env=ENTORNO, capture_output=True, text=True, stdin=subprocess.DEVNULL)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)  # ya publicado: tras el push, nada nuevo con rama de seguimiento

    def test_pu3_no_verify_saltea_la_puerta(self):
        self.commit('config.py', f'TOKEN = "{GITHUB}"')
        self.assertEqual(self.empujar('--no-verify', 'origin', 'main')[0], 0)

    def test_pu3_la_exencion_de_una_linea_deja_pasar(self):
        self.commit('ejemplo.py', f'TOKEN = "{GITHUB}"  # factory:secreto-ok')
        codigo, salida = self.empujar('origin', 'main')
        self.assertEqual(codigo, 0, salida)

    def test_pu3_un_hook_ajeno_no_se_pisa(self):
        self.hook().unlink()
        ajeno = '#!/bin/sh\n# mío, de otra herramienta\nexit 0\n'
        self.hook().write_text(ajeno)
        self.hook().chmod(0o755)
        salida = self.cli('hooks')
        self.assertEqual(self.hook().read_text(), ajeno)
        self.assertIn('pre-push', salida)
        self.assertIn('no es de Factory', salida)
        self.assertIn(f'-eq {puerta.CODIGO_BLOQUEO}', salida)  # la línea sugerida respeta el código de salida
        self.assertIn('exit 1', salida)
        for rc, esperado in ((0, 0), (2, 0), (puerta.CODIGO_BLOQUEO, 1)):  # con set -e, un push limpio o un aviso no frenan; sólo el bloqueo
            with self.subTest(rc=rc):
                script = 'set -e\n' + cli.lineas_para_encadenar(f'(exit {rc})') + '\nexit 0\n'
                self.assertEqual(subprocess.run(['sh', '-c', script], capture_output=True).returncode, esperado)
        self.assertNotIn('verificaciones vencidas se bloquea', salida)

    def test_pu3_instalar_dos_veces_no_duplica_ni_rompe(self):
        antes = self.hook().read_text()
        self.cli('hooks')
        self.assertEqual(self.hook().read_text(), antes)
        self.assertEqual(antes.count(puerta.HOOK_MARCA), 1)  # la marca de Factory una sola vez

    def test_pu3_con_el_interprete_borrado_el_push_pasa_con_un_aviso(self):
        self.hook().write_text(self.hook().read_text().replace(sys.executable, '/no/existe/python'))
        self.commit('config.py', f'TOKEN = "{GITHUB}"')
        codigo, salida = self.empujar('origin', 'main')
        self.assertEqual(codigo, 0, salida)
        self.assertIn('Aviso', salida)

    def test_pu3_si_la_puerta_se_rompe_por_dentro_el_push_pasa_con_un_aviso(self):
        (self.root / '.factory/config.json').write_text('{no es json')  # el proyecto mal configurado hace fallar cualquier comando
        self.commit('config.py', f'TOKEN = "{GITHUB}"')
        codigo, salida = self.empujar('origin', 'main')
        self.assertEqual(codigo, 0, salida)
        self.assertIn('Aviso', salida)

    def kb_vencido(self):
        """Deja kb/README.md distinto de lo que se generaría y commiteado: el conocimiento está vencido, el árbol limpio."""
        (self.root / 'kb/README.md').write_text('kb a mano, vencido\n')
        self.git('add', '-A')
        self.git('commit', '-qm', 'kb vencido')
        r = subprocess.run([*PYTHON_CLI, 'kb', '--verificar'], cwd=self.root, env=ENTORNO, capture_output=True, text=True, stdin=subprocess.DEVNULL)
        self.assertNotEqual(r.returncode, 0)  # es verdad que está vencido
        self.assertEqual(self.git('status', '--porcelain').stdout, '')

    def test_pu3_un_kb_vencido_no_frena_el_push_pero_se_avisa_y_no_se_toca(self):
        self.commit('a.py', 'x = 1')
        self.kb_vencido()
        codigo, salida = self.empujar('origin', 'main')
        self.assertEqual(codigo, 0, salida)
        self.assertIn('no bloquean', salida)
        self.assertIn('kb:', salida)

    # --- pu4: la puerta no modifica el árbol de trabajo ---------------------------------------------------------------------
    def test_pu4_correr_la_puerta_con_el_kb_vencido_no_cambia_nada(self):
        self.kb_vencido()
        antes = (self.git('status', '--porcelain').stdout, (self.root / 'kb/README.md').read_bytes())
        r = subprocess.run([*PYTHON_CLI, 'puerta'], cwd=self.root, env=ENTORNO, capture_output=True, text=True, stdin=subprocess.DEVNULL)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual((self.git('status', '--porcelain').stdout, (self.root / 'kb/README.md').read_bytes()), antes)

    def test_pu4_verificar_la_guia_tampoco_regenera_el_kb(self):
        self.kb_vencido()
        r = subprocess.run([*PYTHON_CLI, 'agentes', '--verificar'], cwd=self.root, env=ENTORNO, capture_output=True, text=True, stdin=subprocess.DEVNULL)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.git('status', '--porcelain').stdout, '')  # antes de este cambio, esto dejaba kb/README.md regenerado
        self.assertEqual((self.root / 'kb/README.md').read_text(), 'kb a mano, vencido\n')

    def test_pu4_un_push_con_el_kb_vencido_deja_el_arbol_como_estaba(self):
        self.commit('a.py', 'x = 1')
        self.kb_vencido()
        self.assertEqual(self.empujar('origin', 'main')[0], 0)
        self.assertEqual(self.git('status', '--porcelain').stdout, '')
        self.assertEqual((self.root / 'kb/README.md').read_text(), 'kb a mano, vencido\n')
        self.git('checkout', '-q', '-b', 'otra')  # y se puede cambiar de rama: nada quedó modificado

    def test_pu4_agentes_sin_verificar_sigue_escribiendo_la_guia_pero_no_el_kb(self):
        self.kb_vencido()
        (self.root / 'AGENTS.md').write_text('guía vieja\n')
        self.git('add', '-A')
        self.git('commit', '-qm', 'guía vieja')
        r = subprocess.run([*PYTHON_CLI, 'agentes'], cwd=self.root, env=ENTORNO, capture_output=True, text=True, stdin=subprocess.DEVNULL)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        cambios = self.git('status', '--porcelain').stdout.split()
        self.assertEqual([c for c in cambios if c != 'M'], ['AGENTS.md'])  # sólo la guía, y el kb vencido sigue como estaba

    def test_pu3_un_proyecto_que_todavia_no_genero_su_kb_ni_su_resumen_puede_empujar(self):
        shutil.rmtree(self.root / 'kb')
        (self.root / '.factory/resumen.md').unlink()
        self.commit('a.py', 'x = 1')
        codigo, salida = self.empujar('origin', 'main')
        self.assertEqual(codigo, 0, salida)

    def test_pu3_las_verificaciones_viejas_bloquean_el_push(self):
        (self.root / 'AGENTS.md').write_text('guía vieja a mano\n')
        self.commit('a.py', 'x = 1')
        codigo, salida = self.empujar('origin', 'main')
        self.assertNotEqual(codigo, 0)
        self.assertIn('agentes', salida)


if __name__ == '__main__':
    unittest.main()
