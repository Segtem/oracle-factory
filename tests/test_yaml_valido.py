"""Los workflows y las plantillas de CI son YAML válido (yv1) y PyYAML es sólo de desarrollo (yv2)."""
from pathlib import Path
import re
import tempfile
import tomllib
import unittest

import yaml

SOURCE = Path(__file__).resolve().parents[1]


def workflows() -> list[Path]:
    return sorted([*(SOURCE / '.github/workflows').glob('*.yml'), *(SOURCE / 'docs/plantillas').glob('*.yml')])


def problemas(ruta: Path) -> list[str]:
    """Lo que le falta a `ruta` para ser un workflow: que se parsee como YAML y tenga on, jobs, y runs-on y steps por trabajo."""
    try:
        datos = yaml.safe_load(ruta.read_text(encoding='utf-8'))
    except yaml.YAMLError as e:
        return [f'{ruta.name}: no es YAML válido ({str(e).splitlines()[0]})']
    if not isinstance(datos, dict):
        return [f'{ruta.name}: no es un workflow']
    falta = [f'{ruta.name}: falta {clave}' for clave in ('on', 'jobs') if clave not in datos and not (clave == 'on' and True in datos)]
    for nombre, trabajo in (datos.get('jobs') or {}).items():  # YAML 1.1 lee `on` como True: se acepta cualquiera de los dos
        for clave in ('runs-on', 'steps'):
            if not isinstance(trabajo, dict) or clave not in trabajo:
                falta.append(f'{ruta.name}: el trabajo {nombre} no tiene {clave}')
    return falta


# --- yv1: los workflows son YAML válido -----------------------------------------------------------------------------------
class Workflows(unittest.TestCase):
    def test_yv1_los_workflows_y_las_plantillas_del_repositorio_son_yaml_valido(self):
        self.assertGreaterEqual(len(workflows()), 4)  # verificar y pages, y las plantillas verificar y verificar-almacen
        self.assertEqual([p for r in workflows() for p in problemas(r)], [])

    def test_yv1_un_valor_con_dos_puntos_sin_comillas_se_rechaza(self):
        with tempfile.TemporaryDirectory() as tmp:
            roto = Path(tmp) / 'roto.yml'
            roto.write_text('on:\n  push:\njobs:\n  a:\n    runs-on: ubuntu-latest\n    steps:\n'
                            '      - name: La suite (con </dev/null: algunas pruebas)\n        run: echo\n', encoding='utf-8')
            self.assertEqual(len(problemas(roto)), 1)
            self.assertIn('roto.yml: no es YAML válido', problemas(roto)[0])
            sin_pasos = Path(tmp) / 'sin.yml'
            sin_pasos.write_text('on:\n  push:\njobs:\n  a:\n    runs-on: ubuntu-latest\n', encoding='utf-8')
            self.assertEqual(problemas(sin_pasos), ['sin.yml: el trabajo a no tiene steps'])


# --- yv2: PyYAML es sólo de desarrollo ------------------------------------------------------------------------------------
class Dependencia(unittest.TestCase):
    def test_yv2_pyyaml_esta_solo_en_el_extra_dev_y_el_lock_lo_fija_igual(self):
        proyecto = tomllib.loads((SOURCE / 'pyproject.toml').read_text(encoding='utf-8'))['project']
        self.assertFalse([d for d in proyecto['dependencies'] if d.lower().startswith('pyyaml')])
        [pedido] = [d for d in proyecto['optional-dependencies']['dev'] if d.lower().startswith('pyyaml')]
        self.assertRegex(pedido, r'^pyyaml==\d')
        lock = tomllib.loads((SOURCE / 'uv.lock').read_text(encoding='utf-8'))
        [paquete] = [p for p in lock['package'] if p['name'] == 'pyyaml']
        self.assertEqual(pedido, f"pyyaml=={paquete['version']}")

    def test_yv2_el_ci_instala_el_checkout_con_el_extra_dev(self):
        datos = yaml.safe_load((SOURCE / '.github/workflows/verificar.yml').read_text(encoding='utf-8'))
        pasos = ' '.join(str(p.get('run', '')) for p in datos['jobs']['pruebas']['steps'])
        self.assertTrue(re.search(r"-e '?\.\[dev\]'?", pasos), pasos)


if __name__ == '__main__':
    unittest.main()
