"""Vueltas proporcionales y riesgos aceptados que persisten: escenarios vs1–vs3, con revisores de prueba y Clue real."""
import contextlib
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_revisores as _revisores  # noqa: E402

f = _revisores.f
from oracle_factory import preparacion  # noqa: E402

# Deja los hallazgos que recibe como JSON [[severidad, título], ...] sobre la primera línea cambiada de notas.py.
REVISOR = r'''
import json, sys
hallazgos, paquete, informe = json.loads(sys.argv[1]), sys.argv[2], sys.argv[3]
p = json.load(open(paquete))
archivo = next(a for a in p["files"] if a["file"].endswith("notas.py"))
linea = archivo["ranges"]["head"][0][0]
json.dump({"schema_version": "oracle-clue.review/v1", "repo": p["repo"], "base": p["base"], "head": p["head"],
           "diff_sha256": p["diff_sha256"], "context_sha256": p["context_sha256"],
           "provider": {"name": "revisor de prueba", "model": "fixture"},
           "findings": [{"id": f"T-{i}", "kind": "bug", "severity": s, "confidence": 0.5, "title": t, "explanation": "Explicación.",
                         "location": {"file": archivo["file"], "start_line": linea, "end_line": linea, "side": "head"},
                         "trigger": "t", "evidence": "e", "related_requirement": "r", "status": "pendiente", "verification": "v"}
                        for i, (s, t) in enumerate(hallazgos, 1)],
           "review_status": "completo", "limitations": ["Revisor de prueba."]}, open(informe, "w"))
'''


class Base(unittest.TestCase):
    pass


for _nombre in (*_revisores.AYUDANTES, 'carpeta'):
    setattr(Base, _nombre, getattr(_revisores.Revisores, _nombre))


class Vueltas(Base):
    def preparar(self):
        self.ident = f.nuevo('Nota', con_ejemplo='notas')
        with self.escribe('1'):
            f.aprobar_spec(self.ident)
        f.importar(self.ident)
        for rid in f.leer(self.ident)[1]['requisitos']:  # con medidas, estado llega a la revisión
            with self.escribe('1'):
                f.medir(self.ident, requisito_id=rid, medidas=['notas.casos_ejecutados', 'notas.resultados'])
        self.git('add', '.')
        self.git('commit', '-qm', 'base')
        self.base = self.git('rev-parse', 'HEAD')
        self.script = Path(self.tmp.name) / 'revisor.py'
        self.script.write_text(REVISOR)
        self.candidato_nuevo()

    def candidato_nuevo(self):
        """Guarda lo que haya en .factory/ y hace un commit de producto: un candidato nuevo."""
        self.git('add', '.')
        self.git('commit', '-qm', 'registro', '--allow-empty')
        notas = self.root / 'examples/notas/notas.py'
        notas.write_text(notas.read_text() + '\n# un cambio del producto\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'producto')

    def pedir(self, revisor, *hallazgos):
        """Pide la revisión a `revisor`, que deja estos hallazgos; devuelve la salida."""
        config = json.loads((self.root / '.factory/config.json').read_text())
        config['revisores'] = {revisor: {'comando': [sys.executable, str(self.script), json.dumps(hallazgos), '{paquete}', '{informe}'],
                                         'proveedor': 'revisor de prueba', 'modelo': 'fixture', 'tope_minutos': 1}}
        (self.root / '.factory/config.json').write_text(json.dumps(config))
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            f.pedir_revision(self.ident, revisor, base=self.base)
        return salida.getvalue()

    def revisar(self, *respuestas):
        salida = io.StringIO()
        with patch('builtins.input', side_effect=list(respuestas)), contextlib.redirect_stdout(salida), \
                contextlib.redirect_stderr(io.StringIO()):
            f.revisar_paso_a_paso(self.ident)
        return salida.getvalue()

    def paso(self):
        with contextlib.redirect_stderr(io.StringIO()):
            return f.proximo_paso(self.ident)

    def aceptados(self):
        return f.leer(self.ident)[1].get('aceptados') or []

    def aceptar_en_una_vuelta(self, decision='1'):
        """Una vuelta con un hallazgo medio que la persona acepta; queda un candidato nuevo listo para la siguiente."""
        self.preparar()
        self.pedir('codex', ['media', 'Falta validar el título'])
        # aceptar el riesgo; motivo armado; completa; la decisión; motivo armado
        self.revisar('1', '1', '1', decision, '1')
        self.candidato_nuevo()

    # --- vs1: el corte de vueltas sigue la severidad -----------------------------------------------------------------------
    def test_vs1_solo_quedan_bajos(self):
        self.preparar()
        salida = self.pedir('codex', ['baja', 'Un nombre poco claro'], ['informativa', 'Un comentario'])
        self.assertIn('(2 hallazgos: 1 baja, 1 informativa)', salida)
        self.assertIn('no hace falta otra vuelta', salida)
        self.assertIn(f'Próximo paso: oracle-factory revisar {self.ident} — los 2 bajos los decide una persona', salida)
        self.assertEqual(self.paso(), f'oracle-factory revisar {self.ident}')

    def test_vs1_queda_uno_medio(self):
        self.preparar()
        self.pedir('codex', ['media', 'Falta validar el título'])
        salida = self.pedir('agy', ['baja', 'Un nombre poco claro'])
        self.assertIn('(1 hallazgo: 1 baja)', salida)
        self.assertIn('Quedan 1 hallazgo medio o más sin aceptar', salida)  # el del otro revisor cuenta
        self.assertIn(f'pedir otra vuelta con oracle-factory pedir-revision {self.ident}', salida)
        self.assertTrue(self.paso().startswith('corregí los 1 hallazgos medios o más del candidato'))

    def test_vs1_severidad_desconocida(self):
        # Clue exige la severidad; si un informe guardado la pierde, Factory no lo da por bajo.
        sin = {'title': 'x', 'location': {'file': 'a.py'}}
        graves, bajos = preparacion.corte([{'datos': {'findings': [sin, {**sin, 'severity': 'rara'}]}}], [])
        self.assertEqual((len(graves), bajos), (2, []))
        self.assertEqual(preparacion.contar_severidades([sin]), '1 sin severidad')

    # --- vs2: un riesgo aceptado persiste entre vueltas ----------------------------------------------------------------------
    def test_vs2_aceptado_presente_en_el_pedido_siguiente(self):
        self.aceptar_en_una_vuelta()
        [aceptado] = self.aceptados()
        self.assertEqual((aceptado['archivo'], aceptado['titulo'], aceptado['actor']),
                         ('examples/notas/notas.py', 'Falta validar el título', f.actor()['actor']))
        self.assertTrue(aceptado['motivo'] and aceptado['candidato'] and aceptado['fecha'])
        self.pedir('codex')
        pedido = (self.carpeta() / 'revision' / 'codex-1.pedido.md').read_text()
        self.assertIn('Riesgos ya aceptados por una persona', pedido)
        self.assertIn(f"- examples/notas/notas.py: Falta validar el título (aceptado por {aceptado['actor']}: {aceptado['motivo']})", pedido)

    def test_vs2_se_guarda_aunque_pida_cambios(self):
        self.aceptar_en_una_vuelta(decision='2')
        self.assertEqual(f.leer(self.ident)[1]['revision']['decision'], 'cambios')
        self.assertEqual(len(self.aceptados()), 1)

    def test_vs2_un_medio_aceptado_no_pide_otra_vuelta(self):
        self.aceptar_en_una_vuelta()
        salida = self.pedir('codex', ['media', 'Falta validar el título.'], ['baja', 'Un nombre poco claro'])
        self.assertIn('No quedan hallazgos medios ni altos sin aceptar', salida)
        self.assertIn('los 1 bajos', salida)
        self.assertEqual(self.paso(), f'oracle-factory revisar {self.ident}')

    def test_vs2_cancelar_no_guarda(self):
        self.preparar()
        self.pedir('codex', ['media', 'Falta validar el título'])
        with self.assertRaises(f.FactoryError):
            self.revisar('1', '1', '1', '3')  # acepta, pero cancela al final
        self.assertEqual(self.aceptados(), [])

    # --- vs3: revisar reconoce un riesgo ya aceptado -------------------------------------------------------------------------
    def test_vs3_mantener_un_riesgo_aceptado(self):
        self.aceptar_en_una_vuelta()
        [antes] = self.aceptados()
        self.pedir('codex', ['media', 'Falta  validar el TÍTULO'])
        salida = self.revisar('1', '1', '1', '1')  # mantener; completa; aprobar; motivo armado
        self.assertIn(f"YA ACEPTADO por {antes['actor']}", salida)
        self.assertIn(f"«{antes['motivo']}»", salida)
        rev = f.leer(self.ident)[1]['revision']
        self.assertEqual((rev['decision'], rev['hallazgos_abiertos']), ('aprobar', 0))
        [decision] = json.loads((self.root / rev['decisiones']).read_text())['decisiones']
        self.assertEqual((decision['estado'], decision['motivo']), ('riesgo_aceptado', antes['motivo']))
        self.assertEqual(self.aceptados(), [antes])

    def test_vs3_revocar_un_riesgo_aceptado(self):
        self.aceptar_en_una_vuelta()
        self.pedir('codex', ['media', 'Falta validar el título'])
        self.revisar('2', '3', '1', '2', '1')  # revocar; dejar abierto; completa; pedir cambios; motivo armado
        self.assertEqual(self.aceptados(), [])
        self.assertEqual(f.leer(self.ident)[1]['revision']['hallazgos_abiertos'], 1)

    def test_vs3_un_titulo_distinto_no_coincide(self):
        self.aceptar_en_una_vuelta()
        salida = self.pedir('codex', ['media', 'Falta validar la fecha'])
        self.assertIn('Quedan 1 hallazgo medio o más', salida)
        salida = self.revisar('3', '1', '2', '1')  # dejar abierto; completa; pedir cambios; motivo armado
        self.assertNotIn('YA ACEPTADO', salida)
        self.assertIn('¿Qué hacés con T-1?', salida)


if __name__ == '__main__':
    unittest.main()
