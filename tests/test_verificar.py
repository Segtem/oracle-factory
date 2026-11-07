"""Verificar para CI: escenarios ci1–ci5, en repositorios temporales con cambios reales (sin red ni terminal)."""
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_estructura as _estructura  # noqa: E402

f, estructura, SOURCE = _estructura.f, _estructura.estructura, _estructura.SOURCE


class Verificar(unittest.TestCase):
    # Los ayudantes de test_estructura sin heredar sus pruebas.
    setUp = _estructura.Estructura.setUp
    escribe, git, estado, salida = (_estructura.Estructura.escribe, _estructura.Estructura.git,
                                     _estructura.Estructura.estado, _estructura.Estructura.salida)
    cambio_medido, cambio_juzgado, sha7 = (_estructura.Estructura.cambio_medido, _estructura.Estructura.cambio_juzgado,
                                            _estructura.Estructura.sha7)
    correr, huellas = _estructura.Estructura.correr, _estructura.Estructura.huellas

    def verificar(self, *mas):
        return self.correr('verificar', *mas, proyecto=self.root)

    def tocar_producto(self):
        (self.root / 'nuevo.txt').write_text('cambió el producto\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'producto cambiado')

    def cerrado(self):
        ident = self.cambio_juzgado()
        with self.escribe('1'):
            f.cerrar(ident)
        self.git('add', '.')
        self.git('commit', '-qm', 'cierre')
        self.assertEqual(self.estado(ident)['fase'], 'cerrada')
        return ident

    def reescribir(self, ident, **cambios):
        """Edita el registro del cambio, como lo dejaría un clon con otra historia (fixture)."""
        ruta = f.ruta_registro(f.ruta_cambio(ident))
        datos = json.loads(ruta.read_text(encoding='utf-8'))
        for clave, valor in cambios.items():
            if isinstance(valor, dict) and isinstance(datos.get(clave), dict):
                datos[clave].update(valor)
            else:
                datos[clave] = valor
        ruta.write_text(json.dumps(datos), encoding='utf-8')

    # --- ci1: dice si los cambios están consistentes --------------------------------------------------------------
    def test_ci1_todo_consistente_sale_en_cero(self):
        ident = self.cambio_juzgado()
        codigo, salida, _ = self.verificar()
        self.assertEqual(codigo, 0, salida)
        self.assertIn('1 cambio', salida)
        codigo, salida, _ = self.verificar('--json')
        datos = json.loads(salida)
        self.assertEqual((codigo, datos['esquema'], datos['ok'], datos['cambios']), (0, 'oracle-factory.verificar/1', True, 1))
        self.assertEqual(datos['problemas'], [])

    def test_ci1_una_revision_que_ya_no_corresponde(self):
        ident = self.cambio_juzgado()
        self.tocar_producto()
        codigo, salida, _ = self.verificar()
        self.assertEqual(codigo, 1)
        self.assertIn(ident, salida)
        self.assertIn('revision desactualizado respecto del producto', salida)

    def test_ci1_un_informe_tocado_despues_de_aprobarse(self):
        ident = self.cambio_juzgado()
        (self.root / self.estado(ident)['revision']['informe']).write_text('otro texto, después de aprobarse\n')
        codigo, salida, _ = self.verificar('--json')
        datos = json.loads(salida)
        self.assertEqual((codigo, datos['ok']), (1, False))
        self.assertIn({'cambio': ident, 'problema': 'informe de revisión cambiado o sin huella'}, datos['problemas'])

    def test_ci1_un_cambio_recien_creado_no_es_una_inconsistencia(self):
        ident = f.nuevo('Nota', con_ejemplo='notas')
        codigo, salida, _ = self.verificar()
        self.assertEqual(codigo, 0, salida)
        self.assertEqual(self.estado(ident)['fase'], 'espera_aprobacion_spec')

    # --- ci2: sólo lee y no necesita a nadie -------------------------------------------------------------------------
    def test_ci2_el_arbol_queda_igual(self):
        ident = self.cambio_juzgado()
        antes, eventos, contexto = self.huellas(), self.estado(ident)['eventos'], f.contexto_producto
        with patch.object(f, 'terminal_interactiva', return_value=False), patch('builtins.input', side_effect=AssertionError('no pregunta')):
            self.verificar()
            self.verificar('--json')
        self.assertEqual(self.huellas(), antes)
        self.assertEqual(self.estado(ident)['eventos'], eventos)
        self.assertIs(f.contexto_producto, contexto)  # el reemplazo temporal se deshace siempre
        self.assertIn('verificar', f.SOLO_LECTURA)

    # --- ci3: el cierre lo decidió una persona -------------------------------------------------------------------------
    def test_ci3_un_cierre_sin_persona(self):
        ident = self.cerrado()
        self.reescribir(ident, cierre={'tipo_actor': 'agente', 'actor': 'claude-code'})
        codigo, salida, _ = self.verificar()
        self.assertEqual(codigo, 1)
        self.assertIn(ident, salida)
        self.assertIn('cierre no lo decidió una persona', salida)

    def test_ci3_un_agente_cerro_en_modo_autonomo(self):
        ident = self.cerrado()
        self.reescribir(ident, modo='autonomo', cierre={'tipo_actor': 'agente', 'actor': 'claude-code', 'modo': 'autonomo'})
        codigo, salida, _ = self.verificar()
        self.assertEqual(codigo, 0, salida)

    def test_ci3_un_cambio_integrado_hace_tiempo(self):
        self.cerrado()
        self.tocar_producto()
        codigo, salida, _ = self.verificar()
        self.assertEqual(codigo, 0, salida)
        self.assertNotIn('desactualizado', salida)

    # --- ci4: no exige lo que otra máquina no tiene -------------------------------------------------------------------
    def test_ci4_hechos_ausentes_en_un_clon_limpio(self):
        ident = self.cambio_juzgado()
        hechos = self.root / self.estado(ident)['oracle']['hechos']
        hechos.unlink()
        codigo, salida, _ = self.verificar('--json')
        datos = json.loads(salida)
        self.assertEqual((codigo, datos['ok'], datos['problemas']), (0, True, []))
        self.assertEqual([a['cambio'] for a in datos['avisos']], [ident])
        self.assertIn('hechos ausentes', datos['avisos'][0]['aviso'])

    def test_ci4_hechos_presentes_pero_cambiados(self):
        ident = self.cambio_juzgado()
        hechos = self.root / self.estado(ident)['oracle']['hechos']
        hechos.write_text(hechos.read_text() + ' ')
        codigo, salida, _ = self.verificar()
        self.assertEqual(codigo, 1)
        self.assertIn(ident, salida)
        self.assertIn('hechos cambiado o sin huella', salida)

    # --- ci5: la plantilla y la guía --------------------------------------------------------------------------------
    def test_ci5_la_plantilla_solo_lee_y_la_guia_la_explica(self):
        plantilla = (SOURCE / 'docs/plantillas/verificar.yml').read_text(encoding='utf-8')
        self.assertIn('oracle-factory verificar', plantilla)
        self.assertIn('contents: read', plantilla)
        for prohibido in ('secrets.', 'write', 'GITHUB_TOKEN'):
            self.assertNotIn(prohibido, plantilla)
        guia = (SOURCE / 'docs/ci.md').read_text(encoding='utf-8')
        for marca in ('docs/plantillas/verificar.yml', 'oracle-factory verificar', 'código de salida', 'pre-push', '--no-verify'):
            self.assertIn(marca, guia, marca)


if __name__ == '__main__':
    unittest.main()
