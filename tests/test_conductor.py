"""Autopilot que actúa: escenarios co1–co4 (el bucle con un ejecutor y un reloj falsos, y el comando con Git y un proceso de verdad)."""
import contextlib
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import test_tests_editados as _te  # noqa: E402
from oracle_factory import autopilot, conductor  # noqa: E402

f = _te.f
ID = '20261108-000000-abc-demo'
FRENO = {'id': 'cambio_grande', 'motivo': 'el candidato agrega 900 líneas'}


def datos(paso, frenos=(), candidato='abc1234', fase='requisitos_importados'):
    return {'fase': fase, 'proximo_paso': paso, 'frenos': list(frenos), 'candidato': candidato}


class Fabrica:
    """Un ejecutor falso: observa una lista de estados (el último se repite), anota cada comando y devuelve lo que se le dice."""

    def __init__(self, estados, falla=(), lanzar_falla=None, reloj_paso=0, mensaje_tarda=0):
        self.estados, self.llamadas, self.lanzadas, self.observadas, self.falla, self.lanzar_falla = list(estados), [], [], 0, set(falla), lanzar_falla
        self.t = 0.0
        self.reloj_paso, self.mensaje_tarda = reloj_paso, mensaje_tarda
        self.plazos = []  # (comando, plazo) de cada proceso

    def observar(self):
        self.observadas += 1
        e = self.estados[min(self.observadas - 1, len(self.estados) - 1)]
        if isinstance(e, Exception):
            raise e
        return e

    def correr(self, argv, plazo):
        self.llamadas.append(argv)
        self.plazos.append((argv[0], plazo))
        if argv[0] == 'mensaje':
            self.t += self.mensaje_tarda  # dejar el porqué gasta tiempo del tope
        return (1, 'falló') if argv[0] in self.falla else (0, 'ok')

    def lanzar(self, argv, plazo):
        self.lanzadas.append(argv)
        self.plazos.append(('lanzar', plazo))
        return self.lanzar_falla or (0, 'hecho')

    def ahora(self):
        self.t += self.reloj_paso
        return self.t

    def bucle(self, lanzar=None, max_pasos=10, max_minutos=120):
        return conductor.bucle(ID, self.observar, self.correr, self.lanzar, lanzar, max_pasos, max_minutos, self.ahora)

    def comandos(self):
        return [a[0] for a in self.llamadas]


def pasos_distintos(n):
    return [datos(f'oracle-factory pedir-revision {ID} --a r{i}') for i in range(n)]


class Persona(unittest.TestCase):
    # --- co1: ejecutar solo actúa como agente y nunca decide por una persona ----------------------------------------------------
    def test_co1_una_decision_de_persona_detiene_el_bucle_sin_ejecutar_y_muestra_el_comando(self):
        for paso in (f'oracle-factory cerrar {ID}', f'oracle-factory --agente a revisar {ID}', f'oracle-factory medir {ID} --confirmar'):
            with self.subTest(paso=paso):
                fab = Fabrica([datos(paso)])
                r = fab.bucle()
                self.assertEqual(fab.comandos(), ['mensaje'])  # sólo el mensaje final
                self.assertEqual((r['pasos'], r['decision']['accion'], r['decision']['comando']), ([], 'pedir_a_persona', paso))
                self.assertIn(paso, [a for a in fab.llamadas if a[0] == 'mensaje'][-1][2])  # el mensaje final deja el comando para la persona
                self.assertFalse(fab.lanzadas)

    def test_co1_terminado_y_frenar_detienen_el_bucle_sin_ejecutar_nada(self):
        for estado, accion in ((datos(None, fase='cerrada'), 'terminado'), (datos(f'oracle-factory juzgar {ID}', frenos=[FRENO]), 'frenar'),
                               (datos('hacé lo que quieras'), 'frenar')):
            with self.subTest(accion=accion):
                fab = Fabrica([estado])
                r = fab.bucle(lanzar=['claude', '-p'])
                self.assertEqual((fab.comandos(), fab.lanzadas, r['pasos'], r['decision']['accion']), (['mensaje'], [], [], accion))
                self.assertTrue(r['motivo'])

    def test_co1_una_decision_de_persona_mal_clasificada_no_se_corre(self):
        for comando in (f'oracle-factory cerrar {ID}', f'oracle-factory --agente a aprobar-spec {ID}', f'oracle-factory medir {ID} --confirmar',
                        'oracle-factory autonomia produccion autonomo', 'oracle-factory comando-que-no-existe', 'cerrar', '',
                        f'oracle-factory juzgar {ID} --con RUTA_DE_HECHOS'):
            with self.subTest(comando=comando):
                fab = Fabrica([datos('x')])
                mala = {'accion': 'actuar', 'quien': 'agente', 'comando': comando, 'instruccion': None, 'motivo': 'm', 'frenos': []}
                with patch.object(conductor.autopilot, 'decidir', return_value=mala):
                    r = fab.bucle()
                self.assertEqual((fab.comandos(), r['pasos']), (['mensaje'], []))
                self.assertIn('persona', r['motivo'])

    def test_co1_sin_agente_el_comando_falla_y_no_corre_ni_escribe_nada(self):
        with patch.object(f, 'AGENTE', None), patch.object(conductor, 'bucle', side_effect=AssertionError('no debe correr')):
            with self.assertRaises(f.FactoryError) as e:
                f.comando_autopilot(ID, False, ejecutar=True)
        self.assertIn('--agente', str(e.exception))
        with patch.object(f, 'AGENTE', 'a'), patch.object(conductor, 'bucle', side_effect=AssertionError('no debe correr')):
            with self.assertRaises(f.FactoryError) as e:  # un cambio que no existe falla nombrándolo antes de escribir nada
                f.comando_autopilot('20261108-000000-zzz-nada', False, ejecutar=True)
            self.assertIn('20261108-000000-zzz-nada', str(e.exception))


class Bucle(unittest.TestCase):
    # --- co2: observa, decide, actúa y vuelve a observar --------------------------------------------------------------------------
    def test_co2_un_comando_mecanico_se_corre_y_se_vuelve_a_observar(self):
        fab = Fabrica([datos(f'oracle-factory juzgar {ID}'), datos(f'oracle-factory cerrar {ID}')])
        r = fab.bucle()
        self.assertEqual(fab.llamadas[1], ['juzgar', ID])  # sin el prefijo oracle-factory: el ejecutor pone --agente y --proyecto
        self.assertEqual(fab.comandos(), ['mensaje', 'juzgar', 'mensaje'])
        self.assertEqual(fab.observadas, 2)
        self.assertEqual([(p['accion'], p['codigo']) for p in r['pasos']], [('actuar', 0)])
        self.assertEqual(r['decision']['accion'], 'pedir_a_persona')

    def test_co2_el_comando_conserva_sus_argumentos_y_las_comillas(self):
        fab = Fabrica([datos(f'oracle-factory --agente x pedir-revision {ID} --a "codex vivo"'), datos(f'oracle-factory cerrar {ID}')])
        fab.bucle()
        self.assertEqual(fab.llamadas[1], ['pedir-revision', ID, '--a', 'codex vivo'])  # el --agente del paso se reemplaza por el del bucle

    def test_co2_el_trabajo_creativo_lanza_al_agente_con_la_instruccion_al_final(self):
        paso = 'corregí los hallazgos del candidato abc1234 y commitealo'
        fab = Fabrica([datos(paso), datos(f'oracle-factory cerrar {ID}')])
        r = fab.bucle(lanzar=['claude', '-p'])
        self.assertEqual(fab.lanzadas, [['claude', '-p', paso]])
        self.assertEqual([(p['accion'], p['codigo']) for p in r['pasos']], [('delegar_al_agente', 0)])
        self.assertEqual(fab.observadas, 2)
        # el ejecutor de verdad: el agente lanzado recibe FACTORY_AGENTE; un plazo vencido o un proceso que no arranca son un código distinto de cero
        _, lanzar = conductor.ejecutor(Path.cwd(), 'claude-code')
        self.assertEqual(lanzar([sys.executable, '-c', 'import os, sys; sys.exit(0 if os.environ.get("FACTORY_AGENTE") == "claude-code" else 3)'], 30)[0], 0)
        self.assertEqual(lanzar([sys.executable, '-c', 'import time; time.sleep(30)'], 0.01)[0], 124)
        self.assertEqual(lanzar(['no-existe-este-comando-xyz'], 5)[0], 127)
        self.assertEqual(lanzar([sys.executable, '-c', 'import sys; sys.exit(0)'], 0)[0], 124)  # sin tiempo no arranca, y el plazo no se estira a un segundo
        self.assertEqual(lanzar([sys.executable, '-c', 'import sys; sys.exit(0)'], -5)[0], 124)
        with patch.object(conductor.subprocess, 'run', side_effect=AssertionError('sin tiempo no arranca')):  # y sin tiempo ni siquiera arranca
            self.assertEqual(lanzar(['x'], 0)[0], 124)
        with patch.object(conductor.subprocess, 'run', side_effect=conductor.subprocess.TimeoutExpired('x', 0.2)) as run:  # el plazo llega exacto
            self.assertEqual(lanzar(['x'], 0.2)[0], 124)
            self.assertEqual(run.call_args.kwargs['timeout'], 0.2)

    def test_co2_sin_lanzar_el_trabajo_creativo_detiene_el_bucle_y_deja_la_instruccion(self):
        paso = 'corregí lo que pidió la revisión y commitealo'
        fab = Fabrica([datos(paso)])
        r = fab.bucle()
        self.assertEqual((fab.lanzadas, r['pasos'], fab.comandos()), ([], [], ['mensaje']))
        self.assertIn('--lanzar', r['motivo'])
        self.assertEqual(r['decision']['instruccion'], paso)

    # --- co3: topes y frenos propios ------------------------------------------------------------------------------------------------
    def test_co3_el_tope_de_pasos_detiene_el_bucle(self):
        fab = Fabrica(pasos_distintos(10))
        r = fab.bucle(max_pasos=3)
        self.assertEqual(len(r['pasos']), 3)
        self.assertIn('pasos', r['motivo'])
        self.assertEqual(fab.comandos().count('mensaje'), 4)  # uno por paso y el final

    def test_co3_el_tope_de_minutos_detiene_el_bucle_con_un_reloj_falso(self):
        fab = Fabrica(pasos_distintos(10), reloj_paso=60)  # cada lectura del reloj avanza un minuto
        r = fab.bucle(max_minutos=3)
        self.assertLessEqual(len(r['pasos']), 1)  # cada lectura del reloj gasta un minuto: con un tope de tres no caben más
        self.assertIn('minutos', r['motivo'])
        # el porqué gasta tiempo del tope: el paso toma su plazo del reloj de después, y si ya no queda, no se actúa
        fab = Fabrica([datos(f'oracle-factory juzgar {ID}'), datos(f'oracle-factory cerrar {ID}')], mensaje_tarda=45)
        r = fab.bucle(max_minutos=1)
        self.assertEqual([p for p in fab.plazos if p[0] == 'juzgar'], [('juzgar', 15)])  # 60 s menos los 45 del mensaje
        self.assertLessEqual([p for p in fab.plazos if p[0] == 'mensaje'][0][1], 60)
        fab = Fabrica([datos(f'oracle-factory juzgar {ID}')], mensaje_tarda=70)
        r = fab.bucle(max_minutos=1)
        self.assertEqual((r['pasos'], 'juzgar' in fab.comandos()), ([], False))
        self.assertIn('minutos', r['motivo'])
        fab = Fabrica([datos(f'oracle-factory juzgar {ID}')], mensaje_tarda=60)
        r = fab.bucle(max_minutos=1)
        self.assertEqual((r['pasos'], 'juzgar' in fab.comandos()), ([], False))  # justo en el tope tampoco
        # con el tiempo ya agotado no se deja ni el porqué: sólo el mensaje final
        for reloj, tope in ((1, 0.001), (0, 0)):
            fab = Fabrica(pasos_distintos(3), reloj_paso=reloj)
            r = fab.bucle(max_minutos=tope)
            self.assertEqual((r['pasos'], fab.comandos()), ([], ['mensaje']))
        fab = Fabrica([datos(f'oracle-factory juzgar {ID}'), datos(f'oracle-factory cerrar {ID}')])
        fab.bucle(max_minutos=0.5)
        self.assertEqual(fab.plazos[0], ('mensaje', 30))  # el plazo del porqué es lo que queda, hasta 60 s
        self.assertEqual(fab.plazos[-1], ('mensaje', 10))  # el mensaje final tiene su plazo propio
        # los plazos son exactos: menos de un segundo no se estira a un segundo
        fab = Fabrica([datos(f'oracle-factory juzgar {ID}'), datos(f'oracle-factory cerrar {ID}')], mensaje_tarda=59.5)
        fab.bucle(max_minutos=1)
        self.assertEqual([p for p in fab.plazos if p[0] == 'juzgar'], [('juzgar', 0.5)])
        fab = Fabrica([datos(f'oracle-factory juzgar {ID}'), datos(f'oracle-factory cerrar {ID}')])
        fab.bucle(max_minutos=0.01)
        self.assertAlmostEqual(fab.plazos[0][1], 0.6)
        # si al ir a dejar el porqué ya no queda tiempo, no se deja ni se actúa
        fab = Fabrica(pasos_distintos(3), reloj_paso=60)
        r = fab.bucle(max_minutos=1)
        self.assertEqual((r['pasos'], fab.comandos()), ([], ['mensaje']))
        self.assertIn('minutos', r['motivo'])

    def test_co3_la_misma_decision_dos_veces_seguidas_es_falta_de_progreso(self):
        fab = Fabrica([datos(f'oracle-factory juzgar {ID}')])  # el estado nunca cambia
        r = fab.bucle()
        self.assertEqual(len(r['pasos']), 1)
        self.assertIn('progreso', r['motivo'])
        self.assertEqual(fab.comandos().count('juzgar'), 1)

    def test_co3_un_comando_o_un_agente_que_fallan_detienen_el_bucle(self):
        fab = Fabrica(pasos_distintos(3) , falla={'mensaje'})  # el porqué es obligatorio: si no se puede dejar, no se actúa
        r = fab.bucle()
        self.assertEqual((r['pasos'], fab.comandos()[0]), ([], 'mensaje'))
        self.assertIn('mensaje final', r['aviso'])  # y como el final tampoco se pudo dejar, lo avisa
        fab = Fabrica([datos(f'oracle-factory juzgar {ID}'), datos(f'oracle-factory cerrar {ID}')], falla={'juzgar'})
        r = fab.bucle()
        self.assertEqual([p['codigo'] for p in r['pasos']], [1])
        self.assertIn('falló', r['motivo'])
        self.assertEqual(fab.observadas, 1)  # no sigue
        fab = Fabrica([datos('corregí algo'), datos(f'oracle-factory cerrar {ID}')], lanzar_falla=(127, 'no arranca'))
        r = fab.bucle(lanzar=['no-existe'])
        self.assertEqual([p['codigo'] for p in r['pasos']], [127])
        self.assertIn('falló', r['motivo'])
        self.assertEqual(fab.observadas, 1)

    def test_co3_un_estado_ilegible_detiene_el_bucle_sin_actuar(self):
        for estados in ([OSError('no se lee')], [None], [{'fase': 'x'}]):
            with self.subTest(estados=estados):
                fab = Fabrica(estados)
                r = fab.bucle()
                self.assertEqual((r['pasos'], fab.comandos()), ([], ['mensaje']))
                self.assertTrue(r['motivo'])

    # --- co4: el porqué en el registro ---------------------------------------------------------------------------------------------
    def test_co4_cada_paso_deja_un_mensaje_antes_y_otro_al_final(self):
        fab = Fabrica([datos(f'oracle-factory juzgar {ID}'), datos('corregí algo y commitealo'), datos(f'oracle-factory cerrar {ID}')])
        r = fab.bucle(lanzar=['claude', '-p'])
        mensajes = [a for a in fab.llamadas if a[0] == 'mensaje']
        self.assertEqual(len(mensajes), 3)
        self.assertTrue(all(m[1] == ID for m in mensajes))
        primero, segundo, final = (m[2] for m in mensajes)
        self.assertIn('actuar', primero)
        self.assertIn(f'oracle-factory juzgar {ID}', primero)
        self.assertIn('comando mecánico', primero)  # el motivo
        self.assertIn('delegar_al_agente', segundo)
        self.assertIn('corregí algo y commitealo', segundo)
        self.assertIn(r['motivo'], final)
        indices = [i for i, a in enumerate(fab.llamadas) if a[0] in ('mensaje', 'juzgar')]
        self.assertEqual([fab.llamadas[i][0] for i in indices], ['mensaje', 'juzgar', 'mensaje', 'mensaje'])  # el porqué va antes de actuar
        self.assertTrue(all(len(m[2]) <= 2000 for m in mensajes))

    def test_co4_un_mensaje_largo_se_recorta_y_no_hace_fallar_el_bucle(self):
        largo = 'corregí ' + 'x' * 5000
        fab = Fabrica([datos(largo), datos(f'oracle-factory cerrar {ID}')])
        fab.bucle(lanzar=['claude', '-p'])
        self.assertTrue(all(len(a[2]) <= 2000 for a in fab.llamadas if a[0] == 'mensaje'))
        self.assertEqual(fab.lanzadas, [['claude', '-p', largo]])  # al agente va la instrucción entera


class Comando(_te.Base):
    # --- co4 (de punta a punta): con Git y un proceso de verdad -------------------------------------------------------------
    def corrida(self, como_json=False, **opciones):
        self.salida()
        with patch.object(f, 'AGENTE', 'claude-code'):
            codigo = f.comando_autopilot(self.ident, como_json, ejecutar=True, **opciones)
        return codigo, self.salida()

    def mensajes(self):
        _, estado = f.leer(self.ident)
        return [e for e in estado['eventos'] if e.get('accion') == 'mensaje']

    def test_co4_el_registro_recibe_el_mensaje_del_agente_y_la_salida_trae_el_resumen(self):
        self.preparar()
        with patch.object(f, 'AGENTE', 'a'), patch.object(conductor, 'bucle', side_effect=AssertionError('no debe correr')):  # topes o --lanzar inválidos: nada corre
            for opciones in ({'max_pasos': 0}, {'max_minutos': 0}, {'max_minutos': -1}, {'lanzar': 'a "b'}):
                with self.subTest(opciones=opciones), self.assertRaises(f.FactoryError):
                    f.comando_autopilot(self.ident, False, ejecutar=True, **opciones)
        antes = len(self.mensajes())
        codigo, texto = self.corrida()
        self.assertEqual(codigo, 0)
        nuevos = self.mensajes()[antes:]
        self.assertEqual(len(nuevos), 1)
        self.assertEqual((nuevos[0]['actor'], nuevos[0]['tipo_actor']), ('claude-code', 'agente'))
        self.assertIn('--lanzar', nuevos[0]['texto'])
        self.assertIn('--lanzar', texto)
        codigo, crudo = self.corrida(como_json=True)
        datos_ = json.loads(crudo)
        self.assertTrue({'motivo', 'pasos', 'decision'} <= set(datos_))
        self.assertEqual(datos_['decision']['accion'], 'delegar_al_agente')
        resultado = {'motivo': 'm', 'pasos': [{'accion': 'actuar', 'comando': 'oracle-factory juzgar X', 'instruccion': None, 'motivo': 'm', 'codigo': 1, 'salida': ''}],
                     'decision': {'accion': 'pedir_a_persona', 'comando': 'oracle-factory cerrar X'}, 'aviso': 'un aviso'}
        with patch.object(f.conductor, 'bucle', return_value=resultado):
            codigo, texto = self.corrida()
        self.assertEqual(codigo, 1)  # un paso falló
        for linea in ('1. actuar: oracle-factory juzgar X → código 1', 'Se detuvo: m', 'Comando para una persona: oracle-factory cerrar X', 'Aviso: un aviso'):
            self.assertIn(linea, texto)
        resultado['pasos'][0]['codigo'] = 0
        with patch.object(f.conductor, 'bucle', return_value=resultado):
            self.assertEqual(self.corrida()[0], 0)


if __name__ == '__main__':
    unittest.main()
