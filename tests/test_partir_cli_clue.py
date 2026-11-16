"""cli.py baja a 100 KB o menos para que un cambio que lo toca entre en el paquete de Clue: escenarios pk1–pk2."""
import inspect
from pathlib import Path
import re
import sys
import unittest

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE))
sys.path.insert(0, str(SOURCE / 'tests'))
from oracle_factory import acciones, alarmas, cli, ganchos, lecturas, proyecto  # noqa: E402
import test_camino_ligero as _cl  # noqa: E402
import test_cli_modulos  # noqa: E402
import test_partir_cli  # noqa: E402

MODULOS = {'ganchos': ganchos, 'acciones': acciones, 'lecturas': lecturas, 'proyecto': proyecto}
FIRMAS = {  # las de antes de mudarlas (2026-11-15): la mudanza no cambia ninguna
    'ganchos': {
        'escribir_atributos': "(raiz: 'Path') -> 'bool'",
        'instalar_union': "() -> 'str'",
        'unir_registro': "(base: 'str', nuestro: 'str', suyo: 'str') -> 'int'",
        'rehacer_generado': "() -> 'None'",
        'hook_pre_push': "() -> 'str'",
        'lineas_para_encadenar': "(llamada: 'str') -> 'str'",
        'instalar_pre_push': "(carpeta: 'Path') -> 'str'",
        'instalar_hook': "() -> 'str'",
        'cambio_del_commit': "(mensaje: 'str') -> 'str | None'",
        'poner_trailer': "(archivo: 'str') -> 'None'",
        'commits_del_cambio': "(identificador: 'str', estado: 'dict') -> 'list[dict]'",
    },
    'acciones': {
        'decidir_union': "(identificador: 'str', campo: 'str', cual: 'str') -> 'None'",
        'aviso_union': "(identificador: 'str', estado: 'dict') -> 'list[str]'",
        'abandonar': "(identificador: 'str', motivo_agente: 'str | None' = None) -> 'None'",
        'cambiar_modo': "(identificador: 'str', nuevo_modo: 'str') -> 'None'",
    },
    'lecturas': {
        'quien_del_cambio': "(estado: 'dict') -> 'dict'",
        'linea_quien': "(q: 'dict') -> 'str'",
        'mostrar': "(identificador: 'str') -> 'None'",
        'archivos_faltantes': "(carpeta: 'Path', estado: 'dict') -> 'list[str]'",
        'proximo_paso': "(identificador: 'str') -> 'str | None'",
        'pasos': "(identificador: 'str') -> 'list[str]'",
        '_pasos': "(identificador: 'str') -> 'str | list[str] | None'",
        'siguiente': "(identificador: 'str', fase: 'str | None' = None) -> 'None'",
        'ofrecer_siguiente': "(identificador: 'str') -> 'int'",
    },
    'proyecto': {
        'comando_ruta': "(identificador: 'str', tipo: 'str') -> 'None'",
        'comando_buscar': "(texto: 'str', maximo: 'int') -> 'None'",
        'comando_skill': "(instalar: 'bool', forzar: 'bool') -> 'int'",
        'comando_agentes': "(verificar: 'bool', en_el_repo: 'bool' = False) -> 'None'",
        'comando_preguntar': "(args) -> 'None'",
        'listar': "(fase: 'str | None' = None, abiertos: 'bool' = False, cerrados: 'bool' = False) -> 'None'",
    },
}


class Tamano(unittest.TestCase):
    # --- pk1: cli.py mide 100 000 bytes o menos y lo mudado es lo mismo ---------------------------------------------------
    def test_pk1_el_tamano_y_las_mudanzas(self):
        self.assertLessEqual((SOURCE / 'oracle_factory/cli.py').stat().st_size, 100_000)
        en_cli = test_partir_cli.definidos(SOURCE / 'oracle_factory/cli.py')
        for nombre_modulo, firmas in FIRMAS.items():
            definidos = test_partir_cli.definidos(SOURCE / 'oracle_factory' / f'{nombre_modulo}.py')
            for nombre, firma in firmas.items():
                with self.subTest(modulo=nombre_modulo, nombre=nombre):
                    self.assertIs(getattr(cli, nombre), getattr(MODULOS[nombre_modulo], nombre))
                    self.assertEqual(re.sub(r' at 0x[0-9a-f]+', '', str(inspect.signature(getattr(cli, nombre)))), firma)
                    self.assertIn(nombre, definidos)
                    self.assertNotIn(nombre, en_cli)

    def test_pk1_los_modulos_nuevos_estan_vigilados(self):
        for nombre, modulo in (('ganchos', ganchos), ('acciones', acciones)):
            self.assertIs(test_cli_modulos.MODULOS.get(nombre), modulo)
            texto = (SOURCE / 'oracle_factory' / f'{nombre}.py').read_text(encoding='utf-8')
            self.assertTrue(texto.rstrip().endswith('from . import cli  # noqa: E402'), nombre)  # al final, como los otros
            self.assertNotIn('ROOT = ', texto)


class Reglas(unittest.TestCase):
    # --- pk2: los módulos mudados con decisiones son reglas de decisión -----------------------------------------------------
    def test_pk2_un_cambio_chico_en_acciones_py(self):
        self.assertIn('oracle_factory/acciones.py', alarmas.REGLAS_DE_DECISION)
        self.chico('oracle_factory/acciones.py')

    def test_pk2_un_cambio_chico_en_ganchos_py(self):
        self.assertIn('oracle_factory/ganchos.py', alarmas.REGLAS_DE_DECISION)
        self.chico('oracle_factory/ganchos.py')

    def chico(self, ruta):
        caso = _cl.Camino('test_cl1_un_cambio_chico_es_ligero_y_el_estado_y_el_json_lo_dicen')  # su proyecto temporal y sus ayudantes
        caso.setUp()
        self.addCleanup(caso.doCleanups)
        texto, _, camino = caso.camino(lambda: (caso.root / ruta).write_text(_cl.CUERPO + 'y = 2\n'), en_la_base={ruta: _cl.CUERPO})
        self.assertEqual((camino['tipo'], camino['reglas_tocadas']), ('completo', [ruta]))
        self.assertIn(ruta, next(l for l in texto.splitlines() if l.startswith('Camino de revisión:')))


if __name__ == '__main__':
    unittest.main()
