"""La medición de las rondas de revisión: el orden sale de los eventos, no del nombre del candidato ni de la fecha de los archivos."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import medir_rondas  # noqa: E402


def hallazgo(severidad, titulo='Un hallazgo', explicacion='Explicación.'):
    return {'id': 'h', 'severity': severidad, 'title': titulo, 'explanation': explicacion}


class MedirRondas(unittest.TestCase):
    def registro(self, raiz, ident, candidatos):
        """candidatos: [(sha, momento de su primera revisión, [hallazgos])], en cualquier orden."""
        carpeta = raiz / '.factory/cambios' / ident
        carpeta.mkdir(parents=True)
        eventos = [{'accion': 'cambio_creado', 'cuando': '2026-10-25T00:00:00+00:00'}]
        for sha, cuando, hallazgos in candidatos:
            eventos.append({'accion': 'revision_pedida', 'candidato': sha, 'cuando': cuando})
            informe = carpeta / 'candidatos' / sha / 'revision' / 'agy-1.json'
            informe.parent.mkdir(parents=True)
            informe.write_text(json.dumps({'findings': hallazgos}))
        eventos.append({'accion': 'cierre', 'cuando': '2026-10-26T00:00:00+00:00'})
        (carpeta / 'factory.json').write_text(json.dumps({'id': ident, 'eventos': eventos}))
        return carpeta

    def test_la_ronda_la_dan_los_eventos_y_no_el_nombre_ni_la_fecha_de_los_archivos(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            # El nombre del candidato y la fecha de sus archivos dicen lo contrario de lo que pasó:
            # «zzz» se revisó primero (ronda 1) y «aaa» después (ronda 2).
            carpeta = self.registro(raiz, 'c1', [('zzz', '2026-10-25T01:00:00+00:00', [hallazgo('alta')] * 3),
                                                 ('aaa', '2026-10-25T05:00:00+00:00', [hallazgo('alta')])])
            os.utime(carpeta / 'candidatos/zzz/revision/agy-1.json', (2_000_000_000, 2_000_000_000))  # el más nuevo en disco
            os.utime(carpeta / 'candidatos/aaa/revision/agy-1.json', (1_000_000_000, 1_000_000_000))  # el más viejo en disco
            r = medir_rondas.analizar(raiz)
            self.assertEqual(r['por_ronda'], {1: {'alta': 3}, 2: {'alta': 1}})
            self.assertEqual((r['cambios'], r['rondas_mediana'], r['rondas_maximo']), (1, 2, 2))

    def test_la_ronda_de_un_candidato_es_la_de_su_primer_evento_aunque_tenga_varios(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            carpeta = self.registro(raiz, 'c1', [('aa', '2026-10-25T01:00:00+00:00', [hallazgo('alta')]),
                                                 ('bb', '2026-10-25T03:00:00+00:00', [hallazgo('baja')] * 2)])
            datos = json.loads((carpeta / 'factory.json').read_text())
            # «aa» tiene también un evento tardío (otro revisor, mucho después): sigue siendo la ronda 1
            datos['eventos'].insert(-1, {'accion': 'revision_lanzada', 'candidato': 'aa', 'cuando': '2026-10-25T09:00:00+00:00'})
            (carpeta / 'factory.json').write_text(json.dumps(datos))
            self.assertEqual(medir_rondas.analizar(raiz)['por_ronda'], {1: {'alta': 1}, 2: {'baja': 2}})

    def test_a_partir_de_la_quinta_ronda_se_agrupan_y_las_severidades_se_cuentan(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            candidatos = [(f'c{i}', f'2026-10-25T0{i}:00:00+00:00', [hallazgo('media'), hallazgo('baja')]) for i in range(1, 8)]
            self.registro(raiz, 'c1', candidatos)
            r = medir_rondas.analizar(raiz)
            self.assertEqual(sorted(r['por_ronda']), [1, 2, 3, 4, 5])
            self.assertEqual(r['por_ronda'][5], {'media': 3, 'baja': 3})  # las rondas 5, 6 y 7
            self.assertEqual(r['rondas_maximo'], 7)

    def test_solo_cuentan_los_cambios_cerrados_y_desde_la_fecha(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            self.registro(raiz, 'nuevo', [('a1', '2026-10-25T01:00:00+00:00', [hallazgo('alta')])])
            viejo = self.registro(raiz, 'viejo', [('b1', '2026-10-25T01:00:00+00:00', [hallazgo('alta')])])
            datos = json.loads((viejo / 'factory.json').read_text())
            datos['eventos'][0]['cuando'] = '2026-09-01T00:00:00+00:00'
            (viejo / 'factory.json').write_text(json.dumps(datos))
            abierto = self.registro(raiz, 'abierto', [('c1', '2026-10-25T01:00:00+00:00', [hallazgo('alta')])])
            datos = json.loads((abierto / 'factory.json').read_text())
            datos['eventos'] = [e for e in datos['eventos'] if e['accion'] != 'cierre']
            (abierto / 'factory.json').write_text(json.dumps(datos))
            self.assertEqual(medir_rondas.analizar(raiz)['cambios'], 1)
            self.assertEqual(medir_rondas.analizar(raiz, desde='2026-08-01')['cambios'], 2)

    def test_las_clases_se_cuentan_por_ronda_solo_para_altos_y_medios(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            self.registro(raiz, 'c1', [('a1', '2026-10-25T01:00:00+00:00', [
                hallazgo('alta', 'Sigue enlaces simbólicos', 'Un symlink escapa del proyecto.'),
                hallazgo('baja', 'Otro enlace simbólico', 'También un symlink, pero baja.'),
                hallazgo('media', 'Cae con un traceback', 'Lanza TypeError sin capturar.')])])
            r = medir_rondas.analizar(raiz)
            self.assertEqual(r['clases']['rutas, «..» y enlaces'], {1: 1})
            self.assertEqual(r['clases']['valores raros o corruptos que rompen'], {1: 1})

    def test_la_salida_en_texto_trae_la_tabla_y_un_registro_roto_no_la_rompe(self):
        with tempfile.TemporaryDirectory() as tmp:
            raiz = Path(tmp)
            self.registro(raiz, 'c1', [('a1', '2026-10-25T01:00:00+00:00', [hallazgo('alta')])])
            roto = raiz / '.factory/cambios/roto'
            roto.mkdir()
            (roto / 'factory.json').write_text('{no es json')
            texto = medir_rondas.texto(medir_rondas.analizar(raiz))
            self.assertIn('1 cambios cerrados', texto)
            self.assertIn('alta+media', texto)


if __name__ == '__main__':
    unittest.main()
