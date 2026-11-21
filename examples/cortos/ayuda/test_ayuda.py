import tempfile
from pathlib import Path
import unittest

from sensor import observar


class Ayuda(unittest.TestCase):
    def test_enlace_existente(self):
        self.assertEqual(observar(Path("."))["casos"][0]["codigo"], 0)

    def test_enlace_roto(self):
        with tempfile.TemporaryDirectory() as temporal:
            raiz = Path(temporal)
            (raiz / "uso.md").write_text("# Uso\n\n[Primer paso](faltante.md)\n", encoding="utf-8")
            (raiz / "pasos.md").write_text("# Primer paso\n", encoding="utf-8")
            self.assertEqual(observar(raiz)["casos"][0]["codigo"], 1)


if __name__ == "__main__":
    unittest.main()
