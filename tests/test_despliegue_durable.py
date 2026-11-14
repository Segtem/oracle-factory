"""Despliegue durable: se vuelve atrás todo lo que se desplegó (dv1), el registro sobrevive a una interrupción (dv2) y la guía dice lo que
hace el código (dv3). Con Git de verdad y los destinos simulados de `test_despliegue` (escriben el commit en `srv/<nombre>`)."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_despliegue as _dd  # noqa: E402
from test_despliegue import Base, correr, desplegar, destino, proyecto  # noqa: E402
from oracle_factory import despliegue  # noqa: E402

SOURCE = Path(__file__).resolve().parents[1]


def sin(d: dict, *campos: str) -> dict:
    return {k: v for k, v in d.items() if k not in campos}


def con_bitacora(nombre: str, **mas) -> dict:
    """Un destino que anota en `bitacora` cada `volver` que corre, para ver el orden."""
    return destino(nombre, volver=f'rm -f srv/{nombre}; echo {nombre} >> bitacora', **mas)


def registro_unico(raiz: Path) -> dict:
    archivos = list((raiz / '.factory' / 'despliegues').glob('*/registro.json'))
    assert len(archivos) == 1, archivos
    return json.loads(archivos[0].read_text(encoding='utf-8'))


class VuelveAtrasDv1(Base):
    def test_dv1_falla_la_prueba_de_humo_del_segundo_se_vuelven_atras_el_y_el_primero(self):
        raiz = proyecto(self.tmp, {'api': con_bitacora('api'), 'app': con_bitacora('app', depende_de=['api'], probar='false'),
                                   'nodo': con_bitacora('nodo', depende_de=['app'])})
        r = desplegar(raiz)
        self.assertEqual({n: d['estado'] for n, d in r['destinos'].items()}, {'api': 'revertido', 'app': 'revertido', 'nodo': 'sin_desplegar'})
        self.assertEqual((raiz / 'bitacora').read_text().split(), ['app', 'api'])  # del último al primero
        self.assertFalse((raiz / 'srv' / 'app').exists())
        self.assertEqual(r['resultado'], 'fallido')
        self.assertIn('app', r['motivo'])
        self.assertIn('prueba de humo', r['motivo'])
        self.assertIn('prueba de humo', r['destinos']['app']['motivo'])  # el estado dice dónde quedó; el motivo, por qué falló

    def test_dv1_falla_la_prueba_de_conjunto_se_vuelven_atras_todos_del_ultimo_al_primero(self):
        raiz = proyecto(self.tmp, {'api': con_bitacora('api'), 'app': con_bitacora('app', depende_de=['api'])}, conjunto={'probar': 'false'})
        r = desplegar(raiz)
        self.assertEqual({n: d['estado'] for n, d in r['destinos'].items()}, {'api': 'revertido', 'app': 'revertido'})
        self.assertEqual((raiz / 'bitacora').read_text().split(), ['app', 'api'])
        self.assertEqual(r['resultado'], 'fallido')
        self.assertIn('conjunto', r['motivo'])
        self.assertNotIn('conservan su estado', r['motivo'])

    def test_dv1_el_que_fallo_sin_volver_queda_fallido_y_el_aviso_lo_nombra(self):
        raiz = proyecto(self.tmp, {'api': sin(destino('api', probar='false'), 'volver')})
        r = desplegar(raiz)
        self.assertEqual(r['destinos']['api']['estado'], 'fallido')
        self.assertTrue(r['destinos']['api']['sin_volver'])
        self.assertIn('sin poder volver atrás', r['aviso'])
        self.assertIn('api', r['aviso'])
        self.assertTrue((raiz / 'srv' / 'api').exists())  # nadie lo tocó: no hay con qué

    def test_dv1_un_destino_que_no_llego_a_desplegar_no_corre_su_volver(self):
        raiz = proyecto(self.tmp, {'api': con_bitacora('api'), 'app': con_bitacora('app', depende_de=['api'], construir='false')})
        r = desplegar(raiz)
        self.assertNotIn('volver', r['destinos']['app']['pasos'])
        self.assertEqual(r['destinos']['app']['estado'], 'fallido')
        self.assertEqual((raiz / 'bitacora').read_text().split(), ['api'])  # sólo el que desplegó


class InterrupcionDv2(Base):
    def test_dv2_el_registro_existe_en_curso_mientras_corre(self):
        raiz = proyecto(self.tmp, {'api': destino('api', alcanzable='cat .factory/despliegues/*/registro.json > primero.json',
                                                  desplegar='cat .factory/despliegues/*/registro.json > visto.json && mkdir -p srv '
                                                            '&& printf %s "$FACTORY_COMMIT" > srv/api')})
        r = desplegar(raiz)
        primero = json.loads((raiz / 'primero.json').read_text(encoding='utf-8'))  # antes del primer comando ya estaba
        self.assertEqual((primero['resultado'], primero['destinos']['api']['pasos']), ('en_curso', {}))
        visto = json.loads((raiz / 'visto.json').read_text(encoding='utf-8'))
        self.assertEqual(visto['resultado'], 'en_curso')
        self.assertEqual(visto['id'], r['id'])
        self.assertIn('version_antes', visto['destinos']['api']['pasos'])  # se reescribió después del paso anterior
        self.assertEqual(r['resultado'], 'todo_funciona')
        self.assertEqual(registro_unico(raiz)['resultado'], 'todo_funciona')

    def test_dv2_una_interrupcion_en_medio_de_un_paso_queda_registrada(self):
        raiz = proyecto(self.tmp, {'api': destino('api'), 'app': destino('app', depende_de=['api'])})
        decl = despliegue.cargar(raiz)
        plan = despliegue.armar_plan(raiz, decl, puerta=lambda: (True, ''))

        def corta(comando, cwd, env, tope):
            if env.get('FACTORY_DESTINO') == 'app' and comando == decl['destinos']['app']['desplegar']:
                raise KeyboardInterrupt
            return despliegue._correr(comando, cwd, env, tope)

        with self.assertRaises(KeyboardInterrupt):  # la interrupción sigue su camino: quien la cortó decide
            despliegue.ejecutar(raiz, decl, plan, autorizo='Brian', planeo='claude-code', correr=corta)
        r = registro_unico(raiz)
        self.assertEqual(r['resultado'], 'interrumpido')
        self.assertIn('app', r['motivo'])
        self.assertIn('desplegar', r['motivo'])
        self.assertEqual(r['en_curso'], {'destino': 'app', 'paso': 'desplegar'})
        self.assertEqual(r['destinos']['api']['estado'], 'probado')
        self.assertEqual(r['destinos']['app']['estado'], 'interrumpido')
        self.assertTrue((raiz / 'srv' / 'api').exists())  # no se vuelve atrás nada por una interrupción
        self.assertEqual(self.estados(raiz, consultar=False)['app']['estado'], 'interrumpido')

    def test_dv2_la_siguiente_corrida_avisa_y_el_plan_se_arma_igual(self):
        raiz = proyecto(self.tmp, {'api': destino('api'), 'app': destino('app', depende_de=['api'])})
        decl = despliegue.cargar(raiz)
        plan = despliegue.armar_plan(raiz, decl, puerta=lambda: (True, ''))

        def corta(comando, cwd, env, tope):
            if env.get('FACTORY_DESTINO') == 'app':
                raise KeyboardInterrupt
            return despliegue._correr(comando, cwd, env, tope)

        with self.assertRaises(KeyboardInterrupt):
            despliegue.ejecutar(raiz, decl, plan, autorizo='Brian', planeo='claude-code', correr=corta)
        salida = correr(raiz, 'desplegar', '--simular')
        self.assertEqual(salida.returncode, 0, salida.stderr)
        self.assertIn('no terminó', salida.stdout)
        self.assertIn('interrumpido', salida.stdout)
        aviso = next(l for l in salida.stdout.splitlines() if 'no terminó' in l)
        self.assertIn('api', aviso)
        self.assertIn('app', aviso)
        self.assertIn('Plan de despliegue', salida.stdout)

    def test_dv2_una_corrida_matada_queda_en_curso_y_tambien_avisa(self):
        # El `desplegar` del segundo mata con SIGKILL al proceso de Python que corre el despliegue: no hay manejo posible.
        raiz = proyecto(self.tmp, {'api': destino('api'), 'app': destino('app', depende_de=['api'], desplegar='kill -9 $PPID; sleep 5')})
        guion = ('import sys; from pathlib import Path; from oracle_factory import despliegue as d; r = Path(sys.argv[1]); '
                 'decl = d.cargar(r); d.ejecutar(r, decl, d.armar_plan(r, decl), autorizo="Brian", planeo="claude-code")')
        p = subprocess.run([sys.executable, '-c', guion, str(raiz)], cwd=raiz, env={**os.environ, 'PYTHONPATH': str(SOURCE)},
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(p.returncode, -9, p.stderr)
        r = registro_unico(raiz)
        self.assertEqual(r['resultado'], 'en_curso')
        self.assertEqual(r['destinos']['api']['estado'], 'probado')
        salida = correr(raiz, 'desplegar', '--simular')
        self.assertEqual(salida.returncode, 0, salida.stderr)
        aviso = next(l for l in salida.stdout.splitlines() if 'no terminó' in l)
        self.assertIn('en_curso', aviso)
        self.assertIn('api', aviso)
        self.assertIn('app', aviso)

    def test_dv2_una_corrida_que_termino_no_deja_aviso(self):
        raiz = proyecto(self.tmp, {'api': destino('api', probar='false')})
        desplegar(raiz)  # falla, pero terminó: no es una interrupción
        salida = correr(raiz, 'desplegar', '--simular')
        self.assertNotIn('no terminó', salida.stdout)


class GuiaDv3(Base):
    def test_dv3_la_guia_nombra_los_estados_que_escribe_el_codigo(self):
        guia = (SOURCE / 'docs' / 'despliegue.md').read_text(encoding='utf-8')
        codigo = (SOURCE / 'oracle_factory' / 'despliegue.py').read_text(encoding='utf-8')
        self.assertTrue({'revertido', 'interrumpido', 'fallido'} <= set(despliegue.ESTADOS), despliegue.ESTADOS)
        self.assertTrue({'en_curso', 'interrumpido', 'fallido', 'todo_funciona', 'incompleto'} <= set(despliegue.RESULTADOS), despliegue.RESULTADOS)
        for estado in (*despliegue.ESTADOS, *despliegue.RESULTADOS):
            self.assertIn(f'`{estado}`', guia, estado)
        usados = set(re.findall(r'estado="([a-z_]+)"', codigo)) | set(re.findall(r'"estado": "([a-z_]+)"', codigo))
        self.assertLessEqual(usados, set(despliegue.ESTADOS))  # lo que el código escribe está en la lista
        self.assertNotIn('conservan su estado', guia)
        self.assertNotIn('conservan su estado', codigo)
        self.assertIn('también el que falló', guia)
        self.assertIn('interrumpido', (SOURCE / 'editores' / 'vscode' / 'tablero.js').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
