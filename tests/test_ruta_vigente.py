"""ruta apunta al candidato vigente: escenarios r1 de la spec (registros, producto, los cuatro tipos, sin crear nada)."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_estructura as _e  # noqa: E402

f = _e.f


class RutaVigente(unittest.TestCase):
    def ruta(self, ident, tipo):
        self.salida()
        f.comando_ruta(ident, tipo)
        return self.salida().strip()

    def juzgado(self):
        """Un cambio juzgado y, después, un commit que sólo guarda sus registros; devuelve (id, sha7 del candidato)."""
        ident = self.cambio_juzgado()
        candidatos = [p.name for p in (self.root / '.factory/cambios' / ident / 'candidatos').iterdir()]
        self.assertEqual(len(candidatos), 1, candidatos)
        self.assertNotEqual(candidatos[0], self.sha7())  # HEAD es el commit de registros
        return ident, candidatos[0]

    def test_r1_un_commit_que_solo_guarda_registros(self):
        ident, sha = self.juzgado()
        antes = self.huellas()
        impresa = self.ruta(ident, 'evidencia')
        self.assertTrue(impresa.endswith(f'.factory/cambios/{ident}/candidatos/{sha}/evidencia'), impresa)
        self.assertEqual(self.huellas(), antes)
        self.assertFalse((self.root / '.factory/cambios' / ident / 'candidatos' / self.sha7()).exists())

    def test_r1_un_commit_que_cambia_el_producto(self):
        ident, sha = self.juzgado()
        with (self.root / 'examples/notas/notas.py').open('a', encoding='utf-8') as out:
            out.write('\n# cambio de producto\n')
        self.git('commit', '-qam', 'producto')
        impresa = self.ruta(ident, 'evidencia')
        self.assertTrue(impresa.endswith(f'.factory/cambios/{ident}/candidatos/{self.sha7()}/evidencia'), impresa)

    def test_r1_los_cuatro_tipos_del_mismo_candidato(self):
        ident, sha = self.juzgado()
        for tipo in ('evidencia', 'clue', 'revision'):
            self.assertTrue(self.ruta(ident, tipo).endswith(f'/candidatos/{sha}/{tipo}'), tipo)
        self.assertTrue(self.ruta(ident, 'checkout').endswith(f'.factory/local/revisiones/{sha}'))


for _nombre in ('setUp', 'escribe', 'git', 'estado', 'salida', 'cambio_medido', 'sha7', 'cambio_juzgado', 'huellas'):
    setattr(RutaVigente, _nombre, getattr(_e.Estructura, _nombre))  # el fixture de estructura, sin heredar sus pruebas


if __name__ == '__main__':
    unittest.main()
