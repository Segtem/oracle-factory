"""La lista de firmantes del producto autoriza la llave pública aprobada de Brian."""
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
FIRMANTES = ROOT / ".factory-firmantes"
HUELLA_BRIAN = "SHA256:DEhKOtpM5hKDvpaqTXyfjnDMcrnvCUfsntAtNHuZiPU"


class FirmanteBrian(unittest.TestCase):
    def test_fb1_la_lista_autoriza_solo_a_brian_con_su_llave(self):
        self.assertTrue(FIRMANTES.is_file())
        lineas = FIRMANTES.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lineas), 1)
        self.assertEqual(lineas[0].split()[:2], ["brian", "ssh-ed25519"])
        huella = subprocess.run(["ssh-keygen", "-lf", str(FIRMANTES)],
                                capture_output=True, text=True, check=True).stdout.split()[1]
        self.assertEqual(huella, HUELLA_BRIAN)

    def test_fb1_no_se_publica_una_llave_privada(self):
        archivos = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True,
                                  text=True, check=True).stdout.splitlines()
        self.assertNotIn(".ssh/oracle-factory", archivos)
        self.assertNotIn("oracle-factory", archivos)
        if FIRMANTES.is_file():
            self.assertNotIn("BEGIN OPENSSH PRIVATE KEY", FIRMANTES.read_text(encoding="utf-8"))
