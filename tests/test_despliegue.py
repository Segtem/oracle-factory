"""Despliegue a varios destinos: escenarios dd1–dd6, con Git de verdad y destinos simulados por scripts locales (sin red ni dispositivos).

Cada destino «despliega» escribiendo el commit del plan en un archivo de `srv/`; su versión es ese archivo y su prueba de humo, que exista.
Ningún secreto está escrito entero en este archivo: la puerta lo bloquearía."""
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE))
from oracle_factory import cli, despliegue  # noqa: E402

PYTHON_CLI = [sys.executable, '-c', 'import sys; from oracle_factory.cli import main; sys.exit(main())']
GIT = {**os.environ, 'GIT_AUTHOR_NAME': 'Persona fixture', 'GIT_AUTHOR_EMAIL': 'p@example.invalid',
       'GIT_COMMITTER_NAME': 'Persona fixture', 'GIT_COMMITTER_EMAIL': 'p@example.invalid',
       'GIT_CEILING_DIRECTORIES': str(Path(tempfile.gettempdir()).resolve())}
AWS = 'AKIA' + 'IOSFODNN7EXAMPLE'


def git(raiz, *args):
    return subprocess.run(['git', *args], cwd=raiz, env=GIT, capture_output=True, text=True, check=True).stdout.strip()


def destino(nombre, **mas):
    """Un destino que anda: despliega escribiendo el commit, lo lee como versión, se prueba con que exista y se vuelve atrás borrándolo."""
    base = {'tipo': 'vps', 'desplegar': f'mkdir -p srv && printf %s "$FACTORY_COMMIT" > srv/{nombre}',
            'version': f'cat srv/{nombre}', 'probar': f'test -s srv/{nombre}', 'volver': f'rm -f srv/{nombre}'}
    base.update(mas)
    return base


def proyecto(tmp, destinos, **extra):
    """Un repositorio temporal con `.factory/destinos.json` y un commit en main; devuelve su raíz."""
    raiz = Path(tmp) / 'p'
    raiz.mkdir()
    git(raiz, 'init', '-q', '-b', 'main')
    (raiz / '.factory').mkdir()
    extra = {'conjunto': {'probar': 'true'}, **extra}  # el conjunto es obligatorio; conjunto=None lo omite
    (raiz / '.factory' / 'destinos.json').write_text(json.dumps({'destinos': destinos, **{k: v for k, v in extra.items() if v is not None}}), encoding='utf-8')
    git(raiz, 'add', '-A')
    git(raiz, 'commit', '-qm', 'inicio')
    return raiz


def correr(raiz, *args, agente='claude-code'):
    base = [*PYTHON_CLI, '--proyecto', str(raiz)] + (['--agente', agente] if agente else [])
    return subprocess.run([*base, *args], cwd=raiz, env={**GIT, 'PYTHONPATH': str(SOURCE)}, capture_output=True, text=True, stdin=subprocess.DEVNULL)


def desplegar(raiz, autorizo='Brian', **mas):
    """Arma el plan sobre la punta de main y lo ejecuta como lo haría una persona."""
    decl = despliegue.cargar(raiz)
    plan = despliegue.armar_plan(raiz, decl, puerta=lambda: (True, ''), **mas)
    return despliegue.ejecutar(raiz, decl, plan, autorizo=autorizo, planeo='claude-code')


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def estados(self, raiz, **mas):
        return {d['nombre']: d for d in despliegue.estados(raiz, despliegue.cargar(raiz), **mas)}


class DeclaracionDd1(Base):
    def test_dd1_los_destinos_declarados_se_ven_con_su_tipo_sus_dependencias_y_sin_desplegar(self):
        raiz = proyecto(self.tmp, {'api': destino('api'), 'app': destino('app', tipo='app', depende_de=['api']),
                                   'nodo': destino('nodo', tipo='esp32', depende_de=['api'])})
        est = self.estados(raiz, consultar=False)
        self.assertEqual(sorted(est), ['api', 'app', 'nodo'])
        self.assertEqual([est[n]['tipo'] for n in ('api', 'app', 'nodo')], ['vps', 'app', 'esp32'])
        self.assertEqual(est['app']['depende_de'], ['api'])
        self.assertTrue(all(e['estado'] == 'sin_desplegar' for e in est.values()))
        salida = correr(raiz, 'destinos')
        self.assertEqual(salida.returncode, 0, salida.stderr)
        self.assertIn('esp32', salida.stdout)

    def test_dd1_una_declaracion_que_no_sirve_falla_nombrando_el_destino_y_no_ejecuta_nada(self):
        casos = {
            'sin desplegar': ({'api': {'tipo': 'vps'}}, ('api', 'desplegar')),
            'dependencia que no existe': ({'api': destino('api', depende_de=['fantasma'])}, ('api', 'fantasma')),
            'ciclo': ({'a': destino('a', depende_de=['b']), 'b': destino('b', depende_de=['a'])}, ('ciclo',)),
            'secreto con valor': ({'api': destino('api', secretos=['TOKEN=' + AWS])}, ('api', 'secretos')),
            'campo desconocido': ({'api': destino('api', desplgar='x')}, ('api', 'desplgar')),
            'sin version': ({'api': {k: v for k, v in destino('api').items() if k != 'version'}}, ('api', 'version')),
            'comando que no es texto': ({'api': destino('api', probar=['test'])}, ('api', 'probar')),
        }
        casos['sin conjunto'] = ({'api': destino('api')}, ('conjunto',))
        for i, (nombre, (destinos, palabras)) in enumerate(casos.items()):
            with self.subTest(nombre):
                sub = Path(self.tmp) / str(i)
                sub.mkdir()
                raiz = proyecto(sub, destinos, conjunto=None if nombre == 'sin conjunto' else {'probar': 'true'})
                with self.assertRaises(despliegue.DeclaracionInvalida) as c:
                    despliegue.cargar(raiz)
                for p in palabras:
                    self.assertIn(p, str(c.exception))
                self.assertFalse((raiz / 'srv').exists())
                salida = correr(raiz, 'desplegar', '--simular')
                self.assertNotEqual(salida.returncode, 0)
                self.assertIn(palabras[0], salida.stderr + salida.stdout)

        for i, tope in enumerate((0, -1, 'diez', True)):  # el tope de la prueba de conjunto también se valida al leer
            sub = Path(self.tmp) / f'tope{i}'
            sub.mkdir()
            raiz = proyecto(sub, {'api': destino('api')}, conjunto={'probar': 'true', 'tope_segundos': tope})
            with self.assertRaises(despliegue.DeclaracionInvalida, msg=repr(tope)) as c:
                despliegue.cargar(raiz)
            self.assertIn('tope_segundos', str(c.exception))

    def test_dd1_sin_declaracion_lo_dice(self):
        raiz = proyecto(self.tmp, {'api': destino('api')})
        (raiz / '.factory' / 'destinos.json').unlink()
        self.assertIn('destinos.json', correr(raiz, 'destinos').stderr)


class PlanDd2(Base):
    def test_dd2_simular_muestra_el_orden_por_dependencias_y_no_ejecuta_nada(self):
        raiz = proyecto(self.tmp, {'app': destino('app', depende_de=['api']), 'api': destino('api'), 'nodo': destino('nodo', depende_de=['api'])})
        salida = correr(raiz, 'desplegar', '--simular')
        self.assertEqual(salida.returncode, 0, salida.stderr)
        self.assertLess(salida.stdout.index('api'), salida.stdout.index('app'))
        self.assertLess(salida.stdout.index('api'), salida.stdout.index('nodo'))
        self.assertIn('printf', salida.stdout)  # los comandos de cada destino
        self.assertFalse((raiz / 'srv').exists())
        self.assertEqual(list((raiz / '.factory').glob('despliegues/*')), [])
        solo = correr(raiz, 'desplegar', '--simular', '--destino', 'app')  # elegir un consumidor arrastra su dependencia, antes
        self.assertEqual(solo.returncode, 0, solo.stderr)
        self.assertLess(solo.stdout.index('1. api'), solo.stdout.index('2. app'))
        self.assertNotIn('nodo [', solo.stdout)

    def test_dd2_un_agente_no_autoriza_y_no_cambia_nada(self):
        raiz = proyecto(self.tmp, {'api': destino('api')})
        salida = correr(raiz, 'desplegar', '--autorizar')
        self.assertNotEqual(salida.returncode, 0)
        self.assertIn('persona', salida.stderr)
        self.assertFalse((raiz / 'srv').exists())
        sin_nadie = correr(raiz, 'desplegar', '--autorizar', agente=None)  # ni agente ni terminal: no se atribuye a nadie
        self.assertNotEqual(sin_nadie.returncode, 0)
        self.assertFalse((raiz / 'srv').exists())

    def test_dd2_una_persona_en_su_terminal_autoriza_y_queda_quien(self):
        raiz = proyecto(self.tmp, {'api': destino('api')})
        git(raiz, 'config', 'user.name', 'Brian Fixture')  # config local del repositorio temporal
        with mock.patch.object(cli, 'terminal_interactiva', return_value=True), \
                mock.patch.object(cli, 'verificar_en_proceso', return_value=(0, 'puerta ok')):
            codigo = cli.main(['--proyecto', str(raiz), 'desplegar', '--autorizar'])
        self.assertEqual(codigo, 0)
        registro = json.loads(next((raiz / '.factory' / 'despliegues').glob('*/registro.json')).read_text(encoding='utf-8'))
        self.assertEqual(registro['autorizo'], 'Brian Fixture')
        self.assertEqual(registro['resultado'], 'todo_funciona')

    def test_dd2_la_puerta_en_rojo_o_un_commit_fuera_de_la_rama_niegan_el_plan(self):
        raiz = proyecto(self.tmp, {'api': destino('api')})
        decl = despliegue.cargar(raiz)
        with self.assertRaises(despliegue.DespliegueNegado) as c:
            despliegue.armar_plan(raiz, decl, puerta=lambda: (False, 'secretos: clave de AWS en x.py'))
        self.assertIn('clave de AWS', str(c.exception))
        git(raiz, 'checkout', '-qb', 'otra')
        (raiz / 'x.txt').write_text('x', encoding='utf-8')
        git(raiz, 'add', '-A')
        git(raiz, 'commit', '-qm', 'solo en otra')
        fuera = git(raiz, 'rev-parse', 'HEAD')
        git(raiz, 'checkout', '-q', 'main')
        with self.assertRaises(despliegue.DespliegueNegado) as c:
            despliegue.armar_plan(raiz, decl, commit=fuera, puerta=lambda: (True, ''))
        self.assertIn('main', str(c.exception))
        # y por la CLI, con la puerta de verdad: una credencial en un commit de main
        (raiz / 'clave.py').write_text(f'AWS = "{AWS}"\n', encoding='utf-8')
        git(raiz, 'add', '-A')
        git(raiz, 'commit', '-qm', 'una credencial')
        salida = correr(raiz, 'desplegar', '--simular')
        self.assertNotEqual(salida.returncode, 0)
        self.assertIn('puerta', salida.stderr.lower())


class PruebasDd3(Base):
    def test_dd3_todo_anda_y_el_resultado_es_todo_quedo_funcionando(self):
        raiz = proyecto(self.tmp, {'api': destino('api'), 'app': destino('app', depende_de=['api']), 'nodo': destino('nodo', depende_de=['api'])},
                        conjunto={'probar': 'test -s srv/api && test -s srv/app && test -s srv/nodo'})
        r = desplegar(raiz)
        self.assertEqual(r['resultado'], 'todo_funciona')
        self.assertEqual({n: d['estado'] for n, d in r['destinos'].items()}, {'api': 'probado', 'app': 'probado', 'nodo': 'probado'})
        self.assertEqual(r['conjunto']['resultado'], 'ok')
        self.assertEqual((raiz / 'srv' / 'api').read_text(), git(raiz, 'rev-parse', 'main'))
        self.assertEqual(r['orden'], ['api', 'app', 'nodo'])

    def test_dd3_un_destino_apagado_queda_inalcanzable_y_no_se_despliega(self):
        raiz = proyecto(self.tmp, {'nodo': destino('nodo', tipo='esp32', alcanzable='false')})
        r = desplegar(raiz)
        self.assertEqual(r['destinos']['nodo']['estado'], 'inalcanzable')
        self.assertNotEqual(r['resultado'], 'todo_funciona')
        self.assertFalse((raiz / 'srv').exists())

    def test_dd3_desplego_pero_corre_otra_version_queda_fallido_sin_probarlo(self):
        raiz = proyecto(self.tmp, {'api': destino('api', version='echo otra-version', probar='touch humo_corrio')})
        r = desplegar(raiz)
        self.assertEqual(r['destinos']['api']['estado'], 'fallido')
        self.assertIn('versión', r['destinos']['api']['motivo'])
        self.assertFalse((raiz / 'humo_corrio').exists())

    def test_dd3_si_el_conjunto_falla_los_destinos_siguen_probados_y_el_resultado_lo_dice(self):
        raiz = proyecto(self.tmp, {'api': destino('api')}, conjunto={'probar': 'false'})
        r = desplegar(raiz)
        self.assertEqual(r['resultado'], 'fallido')
        self.assertEqual(r['destinos']['api']['estado'], 'probado')
        self.assertEqual(r['conjunto']['resultado'], 'fallo')
        self.assertIn('conjunto', r['motivo'])

    def test_dd3_sin_prueba_de_humo_un_destino_no_queda_probado(self):
        raiz2 = proyecto(self.tmp, {'api': {k: v for k, v in destino('api').items() if k != 'probar'}})
        r = desplegar(raiz2)
        self.assertEqual(r['destinos']['api']['estado'], 'desplegado')
        self.assertNotEqual(r['resultado'], 'todo_funciona')


class FalloDd4(Base):
    def plan_tres(self, **mas):
        return proyecto(self.tmp, {'api': destino('api'), 'app': destino('app', depende_de=['api'], probar='false'),
                                   'nodo': destino('nodo', tipo='esp32', depende_de=['app'])}, **mas)

    def test_dd4_falla_el_segundo_se_corta_el_tercero_no_se_toca_y_el_primero_se_vuelve_atras(self):
        raiz = self.plan_tres()
        r = desplegar(raiz)
        self.assertEqual({n: d['estado'] for n, d in r['destinos'].items()}, {'api': 'revertido', 'app': 'fallido', 'nodo': 'sin_desplegar'})
        self.assertFalse((raiz / 'srv' / 'api').exists())  # lo volvió atrás
        self.assertFalse((raiz / 'srv' / 'nodo').exists())
        self.assertEqual(r['resultado'], 'fallido')

    def test_dd4_seguir_continua_solo_con_los_que_no_dependen_del_caido(self):
        raiz = proyecto(self.tmp, {'a': destino('a', probar='false'), 'b': destino('b', depende_de=['a']), 'c': destino('c')}, politica_ante_fallo='seguir')
        r = desplegar(raiz)
        estados = {n: d['estado'] for n, d in r['destinos'].items()}
        self.assertEqual(estados['c'], 'revertido')  # siguió con el independiente, pero la corrida no queda a medias
        self.assertFalse((raiz / 'srv' / 'c').exists())
        self.assertEqual(estados['b'], 'sin_desplegar')
        self.assertEqual(estados['a'], 'fallido')

    def test_dd4_sin_comando_de_volver_queda_desplegado_con_el_aviso(self):
        raiz = proyecto(self.tmp, {'api': {k: v for k, v in destino('api').items() if k != 'volver'},
                                   'app': destino('app', depende_de=['api'], probar='false')})
        r = desplegar(raiz)
        self.assertEqual(r['destinos']['api']['estado'], 'desplegado')
        self.assertTrue(r['destinos']['api']['sin_volver'])
        self.assertIn('sin poder volver atrás', r['aviso'])

    def test_dd4_un_volver_que_falla_deja_el_destino_fallido(self):
        raiz = proyecto(self.tmp, {'api': destino('api', volver='false'), 'app': destino('app', depende_de=['api'], probar='false')})
        r = desplegar(raiz)
        self.assertEqual(r['destinos']['api']['estado'], 'fallido')
        # un comando que se cuelga y deja un hijo vivo: se mata todo el grupo, no sólo el shell, y la corrida queda registrada
        sub = Path(self.tmp) / 'cuelga'
        sub.mkdir()
        colgado = proyecto(sub, {'api': destino('api', desplegar='sleep 60 & echo $! > hijo.pid; wait', tope_segundos=1)})
        inicio = time.monotonic()
        r = desplegar(colgado)
        self.assertLess(time.monotonic() - inicio, 20)  # no esperó al hijo de 60 s
        self.assertEqual(r['destinos']['api']['estado'], 'fallido')
        self.assertEqual(r['destinos']['api']['pasos']['desplegar']['codigo'], 124)
        self.assertIn('tope', r['destinos']['api']['pasos']['desplegar']['salida'])
        pid = int((colgado / 'hijo.pid').read_text())
        for _ in range(40):
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                break
            time.sleep(0.1)
        else:
            os.kill(pid, 9)
            self.fail('el hijo del comando siguió vivo tras el tope')
        self.assertTrue(list((colgado / '.factory' / 'despliegues').glob('*/registro.json')))

    def test_dd4_desactualizado_se_calcula_contra_la_punta_y_desconocido_si_no_se_alcanza(self):
        raiz = proyecto(self.tmp, {'api': destino('api')})
        desplegar(raiz)
        self.assertFalse(self.estados(raiz)['api']['desactualizado'])
        (raiz / 'nuevo.txt').write_text('n', encoding='utf-8')
        git(raiz, 'add', '-A')
        git(raiz, 'commit', '-qm', 'avanza main')
        self.assertTrue(self.estados(raiz)['api']['desactualizado'])
        (raiz / 'srv' / 'api').unlink()  # el destino ya no responde con una versión
        self.assertEqual(self.estados(raiz)['api']['desactualizado'], 'desconocido')
        self.assertEqual(self.estados(raiz, consultar=False)['api']['desactualizado'], 'desconocido')


class EvidenciaDd5(Base):
    def test_dd5_la_salida_con_un_secreto_se_tapa_y_el_registro_marca_donde_estaba(self):
        valor = 'valor-secreto-' + 'x' * 12
        raiz = proyecto(self.tmp, {'api': destino('api', secretos=['TOKEN_API'], desplegar='echo "usando $TOKEN_API" && mkdir -p srv && printf %s "$FACTORY_COMMIT" > srv/api')})
        with mock.patch.dict(os.environ, {'TOKEN_API': valor}):
            r = desplegar(raiz)
        self.assertEqual(r['resultado'], 'todo_funciona')
        guardado = next((raiz / '.factory' / 'despliegues').glob('*/registro.json')).read_text(encoding='utf-8')
        self.assertNotIn(valor, guardado)
        self.assertIn('«secreto:TOKEN_API»', guardado)
        self.assertNotIn(valor, json.dumps(r))

    def test_dd5_un_secreto_que_falta_se_dice_antes_de_ejecutar_algo(self):
        raiz = proyecto(self.tmp, {'api': destino('api', secretos=['TOKEN_QUE_NO_ESTA'])})
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop('TOKEN_QUE_NO_ESTA', None)
            with self.assertRaises(despliegue.DespliegueNegado) as c:
                desplegar(raiz)
        self.assertIn('TOKEN_QUE_NO_ESTA', str(c.exception))
        self.assertFalse((raiz / 'srv').exists())

    def test_dd5_el_registro_dice_commit_quien_planeo_y_quien_autorizo_y_por_destino_lo_hecho(self):
        raiz = proyecto(self.tmp, {'api': destino('api')})
        r = desplegar(raiz, autorizo='Brian')
        guardado = json.loads(next((raiz / '.factory' / 'despliegues').glob('*/registro.json')).read_text(encoding='utf-8'))
        self.assertEqual(guardado['commit'], git(raiz, 'rev-parse', 'main'))
        self.assertEqual((guardado['planeo'], guardado['autorizo']), ('claude-code', 'Brian'))
        api = guardado['destinos']['api']
        self.assertEqual(api['estado'], 'probado')
        self.assertEqual(api['version_despues'], guardado['commit'])
        self.assertIn('desplegar', api['pasos'])
        self.assertIn('comando', api['pasos']['desplegar'])
        self.assertIn('segundos', api['pasos']['desplegar'])
        self.assertIn('salida', api['pasos']['desplegar'])
        self.assertEqual(r['id'], guardado['id'])

    def test_dd5_destinos_json_trae_lo_que_el_tablero_necesita(self):
        raiz = proyecto(self.tmp, {'api': destino('api'), 'app': destino('app', depende_de=['api'])})
        desplegar(raiz)
        salida = correr(raiz, 'destinos', '--json')
        self.assertEqual(salida.returncode, 0, salida.stderr)
        datos = json.loads(salida.stdout)
        api = {d['nombre']: d for d in datos['destinos']}['api']
        for clave in ('nombre', 'tipo', 'estado', 'version_desplegada', 'version_esperada', 'ultima_prueba', 'desactualizado', 'depende_de'):
            self.assertIn(clave, api)
        self.assertEqual(api['estado'], 'probado')
        self.assertEqual(api['version_desplegada'], api['version_esperada'])
        self.assertEqual(datos['ultima_corrida']['resultado'], 'todo_funciona')
        self.assertEqual(datos['ultima_corrida']['autorizo'], 'Brian')


class GeneralDd6(Base):
    def test_dd6_un_tipo_que_nadie_previo_se_trata_igual_que_cualquier_otro(self):
        raiz = proyecto(self.tmp, {'raro': destino('raro', tipo='telescopio-orbital')})
        r = desplegar(raiz)
        self.assertEqual(r['destinos']['raro']['estado'], 'probado')
        self.assertEqual(self.estados(raiz)['raro']['tipo'], 'telescopio-orbital')

    def test_dd6_las_plantillas_copiadas_a_un_proyecto_de_prueba_dan_todo_quedo_funcionando(self):
        plantilla = SOURCE / 'docs' / 'plantillas' / 'destinos.json'
        raiz = Path(self.tmp) / 'p'
        raiz.mkdir()
        git(raiz, 'init', '-q', '-b', 'main')
        (raiz / '.factory').mkdir()
        shutil.copy(plantilla, raiz / '.factory' / 'destinos.json')
        (raiz / 'tools').mkdir()  # la prueba de conjunto la escribe cada proyecto: acá, que los cuatro destinos hayan recibido el commit
        conjunto = raiz / 'tools' / 'prueba_de_conjunto.sh'
        conjunto.write_text('#!/bin/sh\nfor f in vps contenedor nodo app; do test -s "$FAKE/$f" || exit 1; done\n', encoding='utf-8')
        conjunto.chmod(0o755)
        git(raiz, 'add', '-A')
        git(raiz, 'commit', '-qm', 'plantillas')
        # Programas simulados en el PATH: cada uno guarda el commit que se le pide desplegar y lo devuelve cuando se le pregunta la versión.
        bin_ = Path(self.tmp) / 'bin'
        bin_.mkdir()
        estado = Path(self.tmp) / 'estado'
        estado.mkdir()
        guion = ('#!/bin/sh\nn=$(basename "$0"); a="$*"\n'
                 'case "$n" in ssh) f=vps;; docker) f=contenedor;; pio) f=nodo;; rsync) f=app;;\n'
                 '  curl) case "$a" in *nodo*) f=nodo;; *) f=app;; esac;; *) f=$n;; esac\n'
                 'case "$a" in *salud*|*health*) exit 0;; esac\n'
                 'case "$a" in *rev-parse*|*inspect*|*version*) cat "$FAKE/$f"; exit 0;; esac\n'
                 'case "$a" in *"@{-1}"*|*volver*) rm -f "$FAKE/$f"; exit 0;; esac\n'
                 'printf %s "$FACTORY_COMMIT" > "$FAKE/$f"\n')
        for programa in ('ssh', 'docker', 'pio', 'rsync', 'curl', 'ping'):
            p = bin_ / programa
            p.write_text(guion, encoding='utf-8')
            p.chmod(p.stat().st_mode | stat.S_IEXEC)
        entorno = {'PATH': f'{bin_}{os.pathsep}{os.environ["PATH"]}', 'FAKE': str(estado), 'VPS': 'vps.example.invalid',
                   'VPS_DOMINIO': 'vps.example.invalid', 'NODO': 'nodo.example.invalid', 'APP_URL': 'app.example.invalid',
                   'APP_DESTINO': 'usuario@app.example.invalid:/srv/app/'}
        with mock.patch.dict(os.environ, entorno):
            r = desplegar(raiz)
        self.assertEqual(r['resultado'], 'todo_funciona', json.dumps(r, ensure_ascii=False, indent=1)[:3000])
        self.assertEqual(sorted(r['destinos']), ['app', 'contenedor', 'nodo', 'vps'])


if __name__ == '__main__':
    unittest.main()
