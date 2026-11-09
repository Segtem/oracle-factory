"""El registro tolera eventos que no son objetos: escenarios er1–er2, con repositorios Git temporales."""
import contextlib
import io
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import test_tests_editados as _te  # noqa: E402
from oracle_factory import kb as kb_mod  # noqa: E402

f = _te.f
RAROS = [3, 'texto', None, [1, 2], 1.5, True, ['x']]
VALIDO = {'accion': 'mensaje', 'actor': 'ana', 'tipo_actor': 'persona', 'cuando': '2026-11-01T10:00:00+00:00', 'texto': 'mensaje-valido-xyz', 'forma': 'mensaje'}


class Base(_te.Base):
    def con_eventos(self, raros):
        """Pone los `raros` al principio de `eventos` (con un mensaje válido al final, una sola vez) y devuelve los bytes del archivo."""
        carpeta, estado = f.leer(self.ident)
        validos = [e for e in estado['eventos'] if isinstance(e, dict)]
        f.guardar(carpeta, {**estado, 'eventos': list(raros) + validos + ([] if VALIDO in validos else [VALIDO])})
        return f.ruta_registro(carpeta).read_bytes()

    def leer_con_aviso(self):
        with contextlib.redirect_stderr(io.StringIO()) as err:
            carpeta, estado = f.leer(self.ident)
        return estado, err.getvalue()


class Leer(Base):
    # --- er1: leer ignora los eventos que no son objetos ---------------------------------------------------------------------
    def test_er1_los_eventos_que_no_son_objetos_se_ignoran_con_un_aviso_y_sin_tocar_el_archivo(self):
        self.preparar()
        self.con_eventos([])
        sanos = f.leer(self.ident)[1]['eventos']
        bytes_ = self.con_eventos(RAROS)
        f.AVISADOS.discard(('eventos', self.ident))
        estado, aviso = self.leer_con_aviso()
        self.assertEqual(estado['eventos'], sanos)  # sólo los objetos, en el mismo orden
        self.assertIn(f'trae {len(RAROS)} evento(s)', aviso)
        self.assertIn(self.ident, aviso)
        self.assertEqual(f.ruta_registro(f.leer(self.ident)[0]).read_bytes(), bytes_)  # leer no escribe
        # el aviso sale una sola vez por cambio, no en cada lectura
        self.assertEqual(self.leer_con_aviso()[1], '')

    def test_er1_un_registro_sano_no_cambia_ni_avisa_y_eventos_que_no_es_una_lista_es_vacio(self):
        self.preparar()
        f.AVISADOS.discard(('eventos', self.ident))  # preparar ya leyó el cambio: sin esto un aviso espurio quedaría escondido
        estado, aviso = self.leer_con_aviso()
        self.assertEqual(aviso, '')
        self.assertTrue(all(isinstance(e, dict) for e in estado['eventos']))
        antes = json.dumps(estado, sort_keys=True)
        self.assertEqual(json.dumps(self.leer_con_aviso()[0], sort_keys=True), antes)
        for malo in ('texto', 3, None, {'a': 1}):
            with self.subTest(malo=malo):
                f.AVISADOS.discard(('eventos', self.ident))
                carpeta, estado = f.leer(self.ident)
                estado['eventos'] = malo
                f.guardar(carpeta, estado)
                f.AVISADOS.discard(('eventos', self.ident))
                leido, aviso = self.leer_con_aviso()
                self.assertEqual(leido['eventos'], [])
                self.assertTrue(aviso)
        f.AVISADOS.discard(('eventos', self.ident))
        carpeta, estado = f.leer(self.ident)
        del estado['eventos']  # sin la clave no se inventa nada
        f.guardar(carpeta, estado)
        self.assertNotIn('eventos', self.leer_con_aviso()[0])


class Comandos(Base):
    # --- er2: los comandos de lectura siguen funcionando ---------------------------------------------------------------------
    def test_er2_estado_y_kb_funcionan_con_eventos_raros_y_muestran_los_validos(self):
        self.preparar()
        self.con_eventos([])
        sana = f.datos_estado(self.ident)
        self.con_eventos(RAROS)
        f.AVISADOS.discard(('eventos', self.ident))
        with contextlib.redirect_stderr(io.StringIO()):
            self.salida()
            f.mostrar(self.ident)
            texto = self.salida()
            datos = f.datos_estado(self.ident)
            notas = kb_mod.armar(f)
        self.assertIn(self.ident, texto)
        self.assertEqual(datos['id'], sana['id'])
        self.assertEqual((datos['fase'], datos['proximo_paso']), (sana['fase'], sana['proximo_paso']))  # lo mismo que con el registro sano
        self.assertEqual(datos['quien'], sana['quien'])
        self.assertEqual(len(datos['commits']), len(sana['commits']))
        nota = next(t for ruta, t in notas.items() if self.ident in ruta and 'cambios' in ruta)
        self.assertIn('mensaje-valido-xyz', nota)


if __name__ == '__main__':
    unittest.main()
