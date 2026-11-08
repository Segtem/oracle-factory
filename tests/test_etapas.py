"""Autonomía por etapa: escenarios et1–et5, con proyectos temporales con Git de verdad."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from oracle_factory import cli, modos  # noqa: E402
from test_despliegue import AWS, Base, correr, destino, git, proyecto  # noqa: E402

TODAS = ('integracion', 'publicacion', 'produccion')


class Etapas(Base):
    def raiz(self, autonomia=None, **extra):
        """Un proyecto con destinos y su `.factory/config.json` (commiteado, para que el árbol quede limpio)."""
        raiz = proyecto(tempfile.mkdtemp(dir=self.tmp), {'api': destino('api')})  # una carpeta propia: un subTest crea varios
        config = {'modo_por_defecto': 'confirmacion', **extra}
        if autonomia is not None:
            config['autonomia'] = autonomia
        (raiz / '.factory' / 'config.json').write_text(json.dumps(config), encoding='utf-8')
        git(raiz, 'add', '-A')
        git(raiz, 'commit', '-qm', 'config')
        return raiz

    def config(self, raiz):
        with mock.patch.object(cli, 'ROOT', raiz), contextlib.redirect_stderr(io.StringIO()):
            return cli.config_proyecto()

    def texto_config(self, raiz):
        return (raiz / '.factory' / 'config.json').read_text(encoding='utf-8')

    def como_persona(self, raiz, *args, respuestas=('1',)):
        salida = io.StringIO()
        with mock.patch.object(cli, 'terminal_interactiva', return_value=True), mock.patch('builtins.input', side_effect=list(respuestas)), \
                contextlib.redirect_stdout(salida), contextlib.redirect_stderr(salida):
            codigo = cli.main(['--proyecto', str(raiz), *args])
        return codigo, salida.getvalue()

    # --- et1: la configuración ----------------------------------------------------------------------------------------------
    def test_et1_sin_la_clave_las_tres_etapas_piden_a_una_persona(self):
        self.assertEqual(self.config(self.raiz())['autonomia'], {e: 'confirmacion' for e in TODAS})

    def test_et1_una_etapa_declarada_no_cambia_las_otras(self):
        self.assertEqual(self.config(self.raiz({'produccion': 'autonomo'}))['autonomia'],
                         {'integracion': 'confirmacion', 'publicacion': 'confirmacion', 'produccion': 'autonomo'})

    def test_et1_una_etapa_o_un_modo_desconocidos_fallan_nombrando_el_archivo_y_el_valor(self):
        for malo, valor in (({'despliegue': 'autonomo'}, 'despliegue'), ({'produccion': 'funcional'}, 'funcional'),
                            ({'produccion': 1}, '1'), ('produccion', 'produccion')):
            with self.subTest(malo=malo), self.assertRaises(cli.FactoryError) as e:
                self.config(self.raiz(malo))
            self.assertIn('config.json', str(e.exception))
            self.assertIn(valor, str(e.exception))

    # --- et2: quién decide por la vía de agente --------------------------------------------------------------------------
    def test_et2_un_agente_decide_solo_si_la_etapa_es_autonoma(self):
        self.assertEqual(modos.via_agente_etapa('autonomo'), 'decide')
        self.assertEqual(modos.via_agente_etapa('confirmacion'), 'rechaza')
        for raro in ('funcional', '', None):
            with self.subTest(raro=raro), self.assertRaises(ValueError):
                modos.via_agente_etapa(raro)

    # --- et3: la consulta ----------------------------------------------------------------------------------------------------
    def test_et3_por_defecto_muestra_las_cuatro_etapas_con_una_persona_donde_corresponde(self):
        raiz = self.raiz()
        salida = correr(raiz, 'autonomia')
        self.assertEqual(salida.returncode, 0, salida.stderr)
        for etapa in ('construccion', *TODAS):
            self.assertIn(etapa, salida.stdout)
        filas = json.loads(correr(raiz, 'autonomia', '--json').stdout)
        self.assertEqual([f['etapa'] for f in filas], ['construccion', *TODAS])
        self.assertEqual(filas[0]['modo'], 'confirmacion')  # el modo por defecto del proyecto
        self.assertEqual([f['modo'] for f in filas[1:]], ['confirmacion'] * 3)
        self.assertEqual([f['decide'] for f in filas[1:]], ['persona'] * 3)
        self.assertEqual({f['etapa']: f['aplica_hoy'] for f in filas}, {'construccion': True, 'integracion': False, 'publicacion': False, 'produccion': True})

    def test_et3_la_salida_estructurada_refleja_la_etapa_autonoma_y_no_modifica_nada(self):
        raiz = self.raiz({'produccion': 'autonomo'}, modo_por_defecto='autonomo')
        antes = self.texto_config(raiz)
        filas = {f['etapa']: f for f in json.loads(correr(raiz, 'autonomia', '--json').stdout)}
        self.assertEqual((filas['produccion']['modo'], filas['produccion']['decide']), ('autonomo', 'agente'))
        self.assertEqual((filas['construccion']['modo'], filas['construccion']['decide']), ('autonomo', 'agente'))
        self.assertEqual(self.texto_config(raiz), antes)
        self.assertEqual(git(raiz, 'status', '--porcelain'), '')

    # --- et4: quién la cambia ------------------------------------------------------------------------------------------------
    def test_et4_un_agente_no_cambia_la_autonomia_y_la_configuracion_no_se_toca(self):
        raiz = self.raiz()
        antes = self.texto_config(raiz)
        salida = correr(raiz, 'autonomia', 'produccion', 'autonomo')
        self.assertNotEqual(salida.returncode, 0)
        self.assertIn('persona', salida.stderr)
        self.assertEqual(self.texto_config(raiz), antes)

    def test_et4_una_persona_que_confirma_la_cambia_y_se_conserva_el_resto(self):
        raiz = self.raiz(None, tipos_obligatorios=True, capacidades={'alias': 'estructura'})
        antes = json.loads(self.texto_config(raiz))
        codigo, texto = self.como_persona(raiz, 'autonomia', 'produccion', 'autonomo')
        self.assertEqual(codigo, 0, texto)
        despues = json.loads(self.texto_config(raiz))
        self.assertEqual(despues.pop('autonomia'), {'produccion': 'autonomo'})
        self.assertEqual(despues, antes)
        self.assertEqual(self.config(raiz)['autonomia']['produccion'], 'autonomo')

    def test_et4_cambiar_una_etapa_conserva_las_otras_etapas_declaradas(self):
        raiz = self.raiz({'integracion': 'autonomo'})
        codigo, texto = self.como_persona(raiz, 'autonomia', 'produccion', 'autonomo')
        self.assertEqual(codigo, 0, texto)
        self.assertEqual(json.loads(self.texto_config(raiz))['autonomia'], {'integracion': 'autonomo', 'produccion': 'autonomo'})

    def test_et4_poner_la_etapa_en_el_modo_que_ya_tiene_no_pregunta_ni_escribe(self):
        raiz = self.raiz({'produccion': 'autonomo'})
        antes = self.texto_config(raiz)
        codigo, texto = self.como_persona(raiz, 'autonomia', 'produccion', 'autonomo', respuestas=())  # si preguntara, input fallaría
        self.assertEqual(codigo, 0, texto)
        self.assertIn('ya está', texto)
        self.assertEqual(self.texto_config(raiz), antes)

    def test_et4_una_persona_que_cancela_no_cambia_nada(self):
        raiz = self.raiz()
        antes = self.texto_config(raiz)
        codigo, _ = self.como_persona(raiz, 'autonomia', 'produccion', 'autonomo', respuestas=('2',))
        self.assertNotEqual(codigo, 0)
        self.assertEqual(self.texto_config(raiz), antes)

    def test_et4_sin_modo_o_con_un_modo_que_no_existe_es_un_error_de_uso(self):
        raiz = self.raiz()
        antes = self.texto_config(raiz)
        codigo, texto = self.como_persona(raiz, 'autonomia', 'produccion', respuestas=())  # una persona sin modo: ni pregunta ni escribe
        self.assertNotEqual(codigo, 0)
        self.assertIn('modo', texto)
        self.assertEqual(self.texto_config(raiz), antes)
        self.assertNotEqual(correr(raiz, 'autonomia', 'produccion').returncode, 0)
        self.assertNotEqual(correr(raiz, 'autonomia', 'produccion', 'funcional').returncode, 0)

    # --- et5: la producción ----------------------------------------------------------------------------------------------
    def test_et5_con_confirmacion_un_agente_sigue_sin_poder_autorizar(self):
        raiz = self.raiz({'produccion': 'confirmacion'})
        salida = correr(raiz, 'desplegar', '--autorizar')
        self.assertNotEqual(salida.returncode, 0)
        self.assertIn('persona', salida.stderr)
        self.assertFalse((raiz / 'srv').exists())

    def test_et5_con_produccion_autonoma_un_agente_despliega_y_queda_registrado(self):
        raiz = self.raiz({'produccion': 'autonomo'})
        salida = correr(raiz, 'desplegar', '--autorizar')
        self.assertEqual(salida.returncode, 0, salida.stdout + salida.stderr)
        registro = json.loads(next((raiz / '.factory' / 'despliegues').glob('*/registro.json')).read_text(encoding='utf-8'))
        self.assertEqual(registro['autorizo'], 'claude-code')
        self.assertEqual(registro['resultado'], 'todo_funciona')
        self.assertTrue((raiz / 'srv' / 'api').is_file())

    def test_et5_con_produccion_autonoma_quien_no_es_ni_persona_ni_agente_tampoco_autoriza(self):
        raiz = self.raiz({'produccion': 'autonomo'})
        salida = correr(raiz, 'desplegar', '--autorizar', agente=None)  # sin --agente ni terminal: no se atribuye a nadie
        self.assertNotEqual(salida.returncode, 0)
        self.assertFalse((raiz / 'srv').exists())

    def test_et5_con_produccion_autonoma_un_plan_negado_no_ejecuta_nada(self):
        raiz = self.raiz({'produccion': 'autonomo'})
        (raiz / 'clave.py').write_text(f'AWS = "{AWS}"\n', encoding='utf-8')
        git(raiz, 'add', '-A')
        git(raiz, 'commit', '-qm', 'una credencial')
        salida = correr(raiz, 'desplegar', '--autorizar')
        self.assertNotEqual(salida.returncode, 0)
        self.assertIn('puerta', salida.stderr.lower())
        self.assertFalse((raiz / 'srv').exists())
        self.assertEqual(list((raiz / '.factory').glob('despliegues/*')), [])


if __name__ == '__main__':
    unittest.main()
