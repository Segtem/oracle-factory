"""Una decisión en conflicto al unir dos ramas es un pendiente (ub1) y resolverla destraba (ub2).

Dos entornos: el de tests/test_cli_humana.py (un cambio listo para cerrar, con la CLI en el mismo proceso), al que se le pone
en el registro un conflicto con la forma exacta que deja el driver (`unir.unir`), y el de tests/test_unir.py (dos clones de
verdad que se integran con el driver de unión)."""
import contextlib
import io
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_cli_humana as _ch  # noqa: E402
import test_unir as _un  # noqa: E402
from oracle_factory import unir as unir_mod  # noqa: E402

f = _ch.f


class ListoConConflicto(_ch.CliHumana):
    def registro(self, ident):
        return self.root / '.factory/cambios' / ident / 'factory.json'

    def con_conflicto(self, ident, campo):
        """El registro con dos versiones de `campo`, como lo deja el driver al unir una rama que decidió otra cosa."""
        ruta = self.registro(ident)
        nuestro = json.loads(ruta.read_text())
        suyo = json.loads(json.dumps(nuestro))
        if campo == 'revision':
            suyo['revision'] = {**suyo['revision'], 'decision': 'cambios', 'actor': 'Beto'}
        else:
            suyo[campo] = {**suyo[campo], 'codigo': 1}
        base = {k: v for k, v in nuestro.items() if k != campo}  # antes de que cada rama decidiera
        unido = unir_mod.unir(base, nuestro, suyo)
        self.assertEqual([p['campo'] for p in unido['pendientes_de_union']], [campo])
        ruta.write_text(json.dumps(unido, ensure_ascii=False, indent=2) + '\n')
        return ruta

    def verificar(self):
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(salida):
            codigo = f.main(['--proyecto', str(self.root), 'verificar'])
        return codigo, salida.getvalue()

    def hechos(self, ident):
        return self.root / 'tareas' / ident / 'hechos.json'

    # --- ub1: un conflicto de unión es un pendiente ------------------------------------------------------------------
    def test_ub1_un_conflicto_en_la_revision_frena_juzgar_cerrar_y_verificar(self):
        ident = self.listo_para_cerrar()
        ruta = self.con_conflicto(ident, 'revision')
        antes = ruta.read_bytes()
        _, carpeta_estado = f.leer(ident)
        pendientes = f.pendientes_actuales(f.leer(ident)[0], carpeta_estado)
        self.assertTrue(any('revision' in p and 'decidir-union' in p for p in pendientes), pendientes)
        codigo, salida = self.verificar()
        self.assertEqual(codigo, 1, salida)
        self.assertIn(ident, salida)
        self.assertIn('revision', salida)
        with self.escribe('1'), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(f.FactoryError) as juicio:
                f.juzgar(ident, self.hechos(ident))
            with self.assertRaises(f.FactoryError) as cierre:
                f.cerrar(ident)
        self.assertIn('revision', str(juicio.exception))
        self.assertIn('revision', str(cierre.exception))
        self.assertEqual(ruta.read_bytes(), antes)

    def test_ub1_un_conflicto_que_resuelve_el_juicio_no_frena_juzgar(self):
        ident = self.listo_para_cerrar()
        self.con_conflicto(ident, 'oracle')
        with contextlib.redirect_stdout(io.StringIO()):
            f.juzgar(ident, self.hechos(ident))
        self.assertNotIn('pendientes_de_union', json.loads(self.registro(ident).read_text()))

    # --- ub2: resolver el conflicto destraba ------------------------------------------------------------------------
    def test_ub2_decidir_la_union_destraba_verificar_y_cerrar(self):
        ident = self.listo_para_cerrar()
        self.con_conflicto(ident, 'revision')
        with self.escribe('1'), contextlib.redirect_stdout(io.StringIO()):
            f.decidir_union(ident, 'revision', 'nuestro')
        self.assertNotIn('pendientes_de_union', json.loads(self.registro(ident).read_text()))
        codigo, salida = self.verificar()
        self.assertEqual(codigo, 0, salida)
        with self.escribe('1'), contextlib.redirect_stdout(io.StringIO()):
            f.cerrar(ident)
        self.assertEqual(json.loads(self.registro(ident).read_text())['fase'], 'cerrada')


class DosRamas(_un.Unir):
    def verificar_en(self, donde):
        r = _un.subprocess.run([*_un.CLI, 'verificar'], cwd=donde, env=self.env, capture_output=True, text=True,
                               stdin=_un.subprocess.DEVNULL)
        return r.returncode, r.stdout + r.stderr

    def test_ub1_dos_clones_que_toman_el_mismo_cambio_hacen_fallar_verificar(self):
        self.en_rama(self.ana, 'tarea/ana', 'tomar', self.ident, persona=True)
        self.en_rama(self.beto, 'tarea/beto', 'tomar', self.ident, persona=True)
        self.integrar_las_dos()
        codigo, salida = self.verificar_en(self.ana)
        self.assertEqual(codigo, 1, salida)
        self.assertIn('responsable', salida)

    def test_ub2_la_decision_que_corresponde_destraba(self):
        self.en_rama(self.ana, 'tarea/ana', 'tomar', self.ident, persona=True)
        self.en_rama(self.beto, 'tarea/beto', 'tomar', self.ident, persona=True)
        self.integrar_las_dos()
        self.persona(self.ana, 'tomar', self.ident, '--relevo')
        self.assertNotIn('pendientes_de_union', self.registro(self.ana))
        codigo, salida = self.verificar_en(self.ana)
        self.assertEqual(codigo, 0, salida)


for _clase, _base in ((ListoConConflicto, _ch.CliHumana), (DosRamas, _un.Unir)):  # su entorno, no sus pruebas
    for _nombre in dir(_base):
        if _nombre.startswith('test_') and _nombre not in vars(_clase):
            setattr(_clase, _nombre, None)
del _clase, _base, _nombre  # si quedaran, el cargador de unittest correría las pruebas de la base otra vez


if __name__ == '__main__':
    unittest.main()
