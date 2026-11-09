"""Autopilot: no se ofrece como segundo revisor a uno que se lanzó sin dejar resultado: escenarios si1."""
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import test_segundo_revisor as _sr  # noqa: E402
import test_tests_editados as _te  # noqa: E402
from oracle_factory import estructura  # noqa: E402

f = _te.f
REVISORES = _sr.REVISORES
CON_OTRO = {**REVISORES, 'gemini': {'proveedor': 'google'}}


class SinInforme(_te.Base):
    def lanzar(self, revisor, candidato, lanzamiento='l1', cerrar=False):
        carpeta, estado = f.leer(self.ident)
        f.evento(estado, 'revision_lanzada', forma='registro', revisor=revisor, candidato=candidato, lanzamiento=lanzamiento)
        if cerrar:
            f.evento(estado, 'revision_pedida', forma='registro', revisor=revisor, candidato=candidato, lanzamiento=lanzamiento,
                     resultado='ok', hallazgos=0)
        f.guardar(carpeta, estado)

    def segundo(self, revisores):
        real = f.config_proyecto
        with patch.object(f, 'config_proyecto', side_effect=lambda: {**real(), 'revisores': revisores}):
            return f.datos_estado(self.ident)['segundo_revisor']

    def con_informe_de_agy(self):
        self.preparar()
        grande = ''.join(f'def f{i}():\n    return {i}\n\n\n' for i in range(60))
        sha = self.candidato(lambda: (self.root / 'src/grande.py').write_text(grande))
        carpeta = estructura.ruta_canonica(self.root, self.ident, 'revision', sha)
        carpeta.mkdir(parents=True, exist_ok=True)
        (carpeta / 'agy-1.json').write_text(json.dumps({'findings': []}))
        return sha

    def test_si1_el_revisor_que_fallo_sobre_el_candidato_vigente_no_se_ofrece(self):
        sha = self.con_informe_de_agy()
        self.assertEqual(self.segundo(REVISORES), 'codex')
        self.lanzar('codex', sha)
        self.assertIsNone(self.segundo(REVISORES))  # no hay otro de otro proveedor
        self.assertEqual(self.segundo(CON_OTRO), 'gemini')  # el primero que no falló
        largo = self.git('rev-parse', sha).upper()  # el mismo candidato escrito entero y en mayúsculas
        self.lanzar('gemini', largo, lanzamiento='l3')
        self.assertIsNone(self.segundo(CON_OTRO))
        real = f.config_proyecto
        with patch.object(f, 'config_proyecto', side_effect=lambda: {**real(), 'revisores': REVISORES}):
            _, estado = f.leer(self.ident)
            self.assertEqual(f.segundo_revisor_del_cambio(self.ident, _sr.COMPLETO), 'codex')  # sin estado ni candidato no se descarta a nadie, ni rompe
            self.assertEqual(f.segundo_revisor_del_cambio(self.ident, _sr.COMPLETO, estado, None), 'codex')
        self.lanzar('codex', 'abc1234', lanzamiento='l4')
        self.lanzar('gemini', 'abc1234', lanzamiento='l5')
        with patch.object(f, 'config_proyecto', side_effect=lambda: {**real(), 'revisores': CON_OTRO}):
            _, estado = f.leer(self.ident)
            self.assertIsNone(f.segundo_revisor_del_cambio(self.ident, _sr.COMPLETO, estado, 'ABC1234'))  # mayúsculas o minúsculas, es el mismo candidato
            self.assertEqual(f.segundo_revisor_del_cambio(self.ident, _sr.COMPLETO, estado, 'fff9999'), 'codex')
        mismo_proveedor = {**REVISORES, 'codex2': {'proveedor': 'codex'}}
        self.assertEqual(self.segundo(mismo_proveedor), 'codex2')  # se descarta al revisor que falló, no a todo su proveedor

    def test_si1_un_lanzamiento_de_otro_candidato_o_ya_cerrado_no_descarta_a_nadie(self):
        sha = self.con_informe_de_agy()
        self.lanzar('codex', 'deadbee')
        self.assertEqual(self.segundo(REVISORES), 'codex')
        self.lanzar('codex', sha, lanzamiento='l2', cerrar=True)
        self.assertEqual(self.segundo(REVISORES), 'codex')


class Conductor(unittest.TestCase):
    def test_si1_el_conductor_no_repite_el_pedido(self):
        d = _sr.decidir({'segundo_revisor': None})
        self.assertNotIn('pedir-revision', d.get('comando') or '')
        self.assertEqual(d['accion'], 'pedir_a_persona')


if __name__ == '__main__':
    unittest.main()
