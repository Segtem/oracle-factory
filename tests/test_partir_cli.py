"""cli.py: los comandos del proyecto mudados a su módulo, con margen bajo el tope: escenarios pc1–pc2."""
import ast
import inspect
from pathlib import Path
import re
import sys
import unittest

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE))
sys.path.insert(0, str(SOURCE / 'tests'))
from oracle_factory import cli  # noqa: E402
from tools import tamanos  # noqa: E402

FIRMAS = {  # las de antes de mudarlas (2026-11-10): la mudanza no cambia ninguna
    'inicializar': "(oracle: 'str | None' = None) -> 'None'",
    'plan_ejemplo': "() -> 'dict[Path, bytes]'",
    'comando_migrar': "(verificar: 'bool') -> 'None'",
    'comando_procedencia': "(args) -> 'None'",
    'comando_autonomia': "(etapa: 'str | None', modo: 'str | None', como_json: 'bool') -> 'int'",
    'comando_desplegar': "(simular: 'bool', autorizar: 'bool', commit: 'str | None', destinos: 'list[str]', cambios: 'bool' = False) -> 'int'",
    'comando_autopilot': "(ident: 'str', como_json: 'bool', ejecutar: 'bool' = False, lanzar: 'str | None' = None, max_pasos: 'int' = 10, "
                         "max_minutos: 'float' = 120, entorno: 'list[str] | None' = None) -> 'int'",
}


def definidos(ruta: Path) -> set[str]:
    return {n.name for n in ast.parse(ruta.read_text(encoding='utf-8')).body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}


class Tamano(unittest.TestCase):
    def test_pc1_cli_py_mide_145000_bytes_o_menos_y_nada_pasa_su_tope(self):
        self.assertLessEqual((SOURCE / 'oracle_factory/cli.py').stat().st_size, 145_000)
        self.assertEqual(tamanos.problemas(SOURCE), [])


class Mudanza(unittest.TestCase):
    def test_pc2_cada_funcion_mudada_es_la_misma_en_cli_con_su_firma_y_cli_no_la_define(self):
        from oracle_factory import proyecto
        en_cli, en_proyecto = definidos(SOURCE / 'oracle_factory/cli.py'), definidos(SOURCE / 'oracle_factory/proyecto.py')
        for nombre, firma in FIRMAS.items():
            with self.subTest(nombre=nombre):
                self.assertIs(getattr(cli, nombre), getattr(proyecto, nombre))
                self.assertEqual(re.sub(r' at 0x[0-9a-f]+', '', str(inspect.signature(getattr(cli, nombre)))), firma)
                self.assertIn(nombre, en_proyecto)
                self.assertNotIn(nombre, en_cli)

    def test_pc2_la_prueba_de_modulos_vigila_proyecto_y_proyecto_lee_cli_al_usarlo(self):
        import test_cli_modulos
        from oracle_factory import proyecto
        self.assertIs(test_cli_modulos.MODULOS.get('proyecto'), proyecto)
        texto = (SOURCE / 'oracle_factory/proyecto.py').read_text(encoding='utf-8')
        self.assertTrue(texto.rstrip().endswith('from . import cli  # noqa: E402'))  # al final, como los otros módulos mudados
        self.assertNotIn('ROOT = ', texto)  # no copia la raíz: la lee de cli


if __name__ == '__main__':
    unittest.main()
