"""El alcance opcional de los destinos y `desplegar --cambios`: escenarios da1–da4, con Git de verdad y destinos simulados por scripts locales."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_despliegue as _d  # noqa: E402

cli, despliegue, SOURCE = _d.cli, _d.despliegue, _d.SOURCE
destino, proyecto, correr, desplegar, git = _d.destino, _d.proyecto, _d.correr, _d.desplegar, _d.git


def cambiar(raiz, ruta, mensaje='cambio'):
    """Un commit nuevo en main que toca ese archivo."""
    archivo = raiz / ruta
    archivo.parent.mkdir(parents=True, exist_ok=True)
    archivo.write_text(archivo.read_text(encoding='utf-8') + 'x\n' if archivo.exists() else 'x\n', encoding='utf-8')
    git(raiz, 'add', '-A')
    git(raiz, 'commit', '-qm', mensaje)


def plan(raiz, **mas):
    return despliegue.armar_plan(raiz, despliegue.cargar(raiz), puerta=lambda: (True, ''), **mas)


class Base(_d.Base):
    def dos(self, **extra):
        return proyecto(self.tmp, {'a': destino('a', alcance=['a/']), 'b': destino('b', alcance=['b/'])}, **extra)


class Declaracion(Base):
    # --- da1: un destino declara su alcance opcional ---------------------------------------------------------------------
    def test_da1_un_alcance_valido_se_conserva(self):
        raiz = proyecto(self.tmp, {'api': destino('api', alcance=['api/', 'docs/*.md'])})
        self.assertEqual(despliegue.cargar(raiz)['destinos']['api']['alcance'], ['api/', 'docs/*.md'])

    def test_da1_un_alcance_invalido_se_rechaza_nombrando_el_destino_y_el_campo(self):
        for malo in ('api/', [], [''], ['api/', 3], [None], {'api': 1}):
            with self.subTest(alcance=malo):
                with tempfile.TemporaryDirectory() as t:
                    raiz = proyecto(t, {'api': destino('api', alcance=malo)})
                    with self.assertRaises(despliegue.DeclaracionInvalida) as c:
                        despliegue.cargar(raiz)
                    self.assertIn('api', str(c.exception))
                    self.assertIn('alcance', str(c.exception))

    def test_da1_sin_alcance_se_acepta_como_hasta_ahora(self):
        raiz = proyecto(self.tmp, {'api': destino('api')})
        self.assertFalse(despliegue.cargar(raiz)['destinos']['api'].get('alcance'))


class Eleccion(Base):
    # --- da2: --cambios elige los destinos afectados ----------------------------------------------------------------------
    def test_da2_se_cambia_solo_lo_de_un_destino(self):
        raiz = self.dos()
        desplegar(raiz)
        cambiar(raiz, 'a/codigo.txt')
        p = plan(raiz, cambios=True)
        self.assertEqual(p['orden'], ['a'])
        self.assertIn('a', p['motivos'])
        self.assertIn('b', p['omitidos'])

    def test_da2_el_alcance_se_compara_con_lo_ultimo_que_se_desplego_en_ese_destino(self):
        raiz = self.dos()
        desplegar(raiz)
        cambiar(raiz, 'a/codigo.txt')
        cambiar(raiz, 'b/otro.txt')
        desplegar(raiz, destinos=['a'])  # a quedó al día; b sigue en la versión vieja
        self.assertEqual(plan(raiz, cambios=True)['orden'], ['b'])

    def test_da2_lo_que_no_se_puede_descartar_entra_con_su_motivo(self):
        raiz = proyecto(self.tmp, {'sin': destino('sin'), 'nuevo': destino('nuevo', alcance=['nuevo/']),
                                   'viejo': destino('viejo', alcance=['viejo/']), 'quieto': destino('quieto', alcance=['quieto/'])})
        desplegar(raiz, destinos=['sin', 'viejo', 'quieto'])
        for registro in (raiz / '.factory' / 'despliegues').glob('*/registro.json'):
            datos = json.loads(registro.read_text(encoding='utf-8'))
            datos['destinos']['viejo']['version_despues'] = '0' * 40  # una versión que este repositorio no conoce
            registro.write_text(json.dumps(datos), encoding='utf-8')
        cambiar(raiz, 'otra/cosa.txt')
        p = plan(raiz, cambios=True)
        self.assertEqual(sorted(p['orden']), ['nuevo', 'sin', 'viejo'])
        self.assertEqual(sorted(p['omitidos']), ['quieto'])
        self.assertEqual(len({p['motivos'][n] for n in ('sin', 'nuevo', 'viejo')}), 3)  # tres motivos distintos

    def test_da2_un_elegido_arrastra_lo_que_necesita_antes_que_el_(self):
        raiz = proyecto(self.tmp, {'y': destino('y', alcance=['y/']), 'x': destino('x', alcance=['x/'], depende_de=['y'])})
        desplegar(raiz)
        cambiar(raiz, 'x/codigo.txt')
        p = plan(raiz, cambios=True)
        self.assertEqual(p['orden'], ['y', 'x'])
        self.assertIn('y', p['motivos'])

    def test_da2_un_patron_de_git_cuenta_como_alcance(self):
        raiz = proyecto(self.tmp, {'web': destino('web', alcance=['*.html']), 'api': destino('api', alcance=['api/'])})
        desplegar(raiz)
        cambiar(raiz, 'site/index.html')
        self.assertEqual(plan(raiz, cambios=True)['orden'], ['web'])


class Explicacion(Base):
    # --- da3: el plan explica la elección y no ejecuta si no hay nada --------------------------------------------------------
    def test_da3_el_plan_dice_por_que_entra_cada_destino_y_cuales_se_omiten(self):
        raiz = self.dos()
        desplegar(raiz)
        cambiar(raiz, 'a/codigo.txt')
        decl = despliegue.cargar(raiz)
        texto = despliegue.texto_plan(decl, despliegue.armar_plan(raiz, decl, cambios=True, puerta=lambda: (True, '')))
        self.assertIn('a/codigo.txt', texto)  # el motivo nombra lo que cambió
        self.assertRegex(texto, r'(?i)omit\w+.*\bb\b')

    def test_da3_nada_que_desplegar_no_ejecuta_ni_crea_registro(self):
        raiz = self.dos()
        desplegar(raiz)
        antes = sorted(p.name for p in (raiz / '.factory' / 'despliegues').iterdir())
        cambiar(raiz, 'docs/nota.txt')
        git(raiz, 'config', 'user.name', 'Brian Fixture')
        with mock.patch.object(cli, 'terminal_interactiva', return_value=True), \
                mock.patch.object(cli, 'verificar_en_proceso', return_value=(0, 'puerta ok')), \
                mock.patch.object(despliegue, 'ejecutar', side_effect=AssertionError('no se ejecuta nada')):
            salida = _capturar(lambda: cli.main(['--proyecto', str(raiz), 'desplegar', '--cambios', '--autorizar']))
        self.assertEqual(salida[0], 0)
        self.assertIn('nada que desplegar', salida[1].lower())
        self.assertEqual(sorted(p.name for p in (raiz / '.factory' / 'despliegues').iterdir()), antes)


def _capturar(f):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        codigo = f()
    return codigo, buf.getvalue()


class SinCambios(Base):
    # --- da4: sin --cambios nada cambia; la guía cuenta el alcance ---------------------------------------------------------------
    def test_da4_sin_la_opcion_el_plan_incluye_todos_los_destinos(self):
        raiz = self.dos()
        desplegar(raiz)
        cambiar(raiz, 'a/codigo.txt')
        p = plan(raiz)
        self.assertEqual(p['orden'], ['a', 'b'])
        self.assertFalse(p.get('omitidos'))

    def test_da4_cambios_y_destino_juntos_se_niegan(self):
        raiz = self.dos()
        salida = correr(raiz, 'desplegar', '--simular', '--cambios', '--destino', 'a')
        self.assertNotEqual(salida.returncode, 0)
        self.assertIn('no se combinan', salida.stderr)

    def test_da4_la_guia_y_la_plantilla_cuentan_el_alcance_y_sus_limites(self):
        guia = (SOURCE / 'docs/despliegue.md').read_text(encoding='utf-8')
        plantilla = (SOURCE / 'docs/plantillas/destinos.json').read_text(encoding='utf-8')
        for texto in (guia, plantilla):
            self.assertIn('alcance', texto)
        self.assertIn('--cambios', guia)
        self.assertIn('sólo se miran las rutas declaradas', guia)
        json.loads(plantilla)  # sigue siendo JSON válido, y cargable
        carpeta = SOURCE / 'docs/plantillas'
        with tempfile.TemporaryDirectory() as t:
            (Path(t) / '.factory').mkdir()
            shutil.copy(carpeta / 'destinos.json', Path(t) / '.factory' / 'destinos.json')
            despliegue.cargar(Path(t))


if __name__ == '__main__':
    unittest.main()
