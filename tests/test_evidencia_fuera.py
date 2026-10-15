"""buscar no recorre la evidencia ni los paquetes de Clue: escenario ef1, en un proyecto temporal."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_estructura as _estructura  # noqa: E402

f, estructura = _estructura.f, _estructura.estructura


class Base(unittest.TestCase):
    pass


for _nombre in ('setUp', 'escribe', 'git', 'salida'):
    setattr(Base, _nombre, getattr(_estructura.Estructura, _nombre))


class EvidenciaFuera(Base):

    # --- ef1: buscar en todo el proyecto (escenario nuevo del MODIFIED) -----------------------------------------------------
    def test_ef1_la_evidencia_no_aparece(self):
        ident = f.nuevo('Nota', con_ejemplo='notas')
        candidato = self.root / '.factory/cambios' / ident / 'candidatos' / 'abc1234'
        grande = 'x' * (estructura.LIMITE_ARCHIVO + 100) + '\n'  # aunque pese más que el límite, no cuenta como omitido
        for ruta, texto in (('evidencia/suite.txt', 'aguja-de-registro en la suite\n'),
                            ('evidencia/hechos.json', grande + '{"aguja-de-registro": 1}\n'),
                            ('evidencia/trazabilidad.json', '{"caso": "aguja-de-registro"}\n'),
                            ('clue/paquete-codex-1.json', grande + '{"texto": "aguja-de-registro"}\n'),
                            ('revision/codex-1.json', '{"title": "aguja-de-registro en un hallazgo"}\n'),
                            ('revision/codex-1.pedido.md', 'Revisá la aguja-de-registro.\n')):
            (candidato / ruta).parent.mkdir(parents=True, exist_ok=True)
            (candidato / ruta).write_text(texto)
        lineas, total, omitidos = estructura.buscar(self.root, 'aguja-de-registro')
        rel = f'.factory/cambios/{ident}/candidatos/abc1234'
        self.assertEqual(sorted(l.split(':', 1)[0] for l in lineas), [f'{rel}/revision/codex-1.json', f'{rel}/revision/codex-1.pedido.md'])
        self.assertEqual((total, omitidos), (2, 0))
        self.salida()
        f.comando_buscar('aguja-de-registro', 50)  # y la CLI dice lo mismo
        salida = self.salida()
        self.assertIn('2 coincidencia(s)', salida)
        self.assertNotIn('omitido', salida)
        self.assertNotIn('evidencia/', salida)


if __name__ == '__main__':
    unittest.main()
