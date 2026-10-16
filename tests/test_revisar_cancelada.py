"""Un intento de revisión que no se registró queda a la vista: escenarios rc1–rc3, con revisores de prueba y Clue real."""
import contextlib
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_vueltas as _vueltas  # noqa: E402

f = _vueltas.f


class RevisarCancelada(_vueltas.Base):
    preparar, candidato_nuevo = _vueltas.Vueltas.preparar, _vueltas.Vueltas.candidato_nuevo
    pedir, revisar = _vueltas.Vueltas.pedir, _vueltas.Vueltas.revisar

    def estado_texto(self):
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(f.main(['--proyecto', str(self.root), 'estado', self.ident]), 0)
        return salida.getvalue()

    def avisos(self):
        """Los avisos de estado --json, que deben ser también líneas «Aviso: …» de estado en texto."""
        avisos = f.datos_estado(self.ident)['avisos']
        texto = self.estado_texto()
        for aviso in avisos:
            self.assertIn(f'Aviso: {aviso}.', texto)
        return [a for a in avisos if 'intento de revisión' in a]

    def cancelada(self):
        eventos = f.leer(self.ident)[1]['eventos']
        return [e for e in eventos if e['accion'] == 'revision_cancelada']

    def test_rc1_se_elige_un_aprobar_no_disponible(self):
        self.preparar()
        self.pedir('codex', ['media', 'Falta validar el título'])
        sha = f.candidato_vigente(self.ident)
        self.assertEqual(self.avisos(), [])
        with self.assertRaisesRegex(f.FactoryError, 'no se puede aprobar: 1 hallazgo'):
            self.revisar('3', '1', '1')  # dejar abierto; completa; Aprobar, que no está disponible
        self.assertIsNone(f.leer(self.ident)[1].get('revision'))  # no registró ninguna decisión
        [evento] = self.cancelada()
        self.assertEqual((evento['candidato'], evento['forma']), (sha, 'intento'))
        self.assertTrue(evento['causa'].startswith('no se puede aprobar: 1 hallazgo(s) abiertos'), evento)
        self.assertTrue(evento['actor'])
        [aviso] = self.avisos()
        self.assertIn(f"el último intento de revisión ({evento['cuando'][:16].replace('T', ' ')}, {evento['actor']}) "
                      f"no se registró: {evento['causa']}", aviso)
        self.assertTrue(aviso.endswith(f'volvé a correr oracle-factory revisar {self.ident}'), aviso)

    def test_rc2_se_cancela_o_se_cierra_la_entrada(self):
        self.preparar()
        self.pedir('codex', ['baja', 'Un nombre poco claro'])
        with self.assertRaisesRegex(f.FactoryError, 'revisión cancelada'):
            self.revisar('2', '1', '1', '3')  # descartar; motivo; completa; Cancelar
        self.assertEqual([e['causa'] for e in self.cancelada()], ['revisión cancelada; no registré nada'])
        [aviso] = self.avisos()
        self.assertIn('no se registró: revisión cancelada; no registré nada', aviso)
        with self.assertRaises(EOFError):
            self.revisar('2', EOFError())  # la entrada se cierra en medio del menú
        self.assertEqual(self.cancelada()[-1]['causa'], 'se cerró la entrada antes de registrar la revisión')
        [aviso] = self.avisos()
        self.assertIn('no se registró: se cerró la entrada antes de registrar la revisión', aviso)
        with self.assertRaises(KeyboardInterrupt):
            self.revisar('2', KeyboardInterrupt())  # Ctrl-C en medio del menú
        self.assertEqual(self.cancelada()[-1]['causa'], 'se interrumpió antes de registrar la revisión')
        self.assertIsNone(f.leer(self.ident)[1].get('revision'))

    def test_rc3_una_revision_registrada_despues(self):
        self.preparar()
        self.pedir('codex', ['baja', 'Un nombre poco claro'])
        with self.assertRaises(f.FactoryError):
            self.revisar('2', '1', '1', '3')
        self.assertEqual(len(self.avisos()), 1)
        # Un fallo después de registrarla (la nota del tracker) no es un intento cortado.
        with patch.object(f, 'nota_tarea', side_effect=f.FactoryError('tracker caído')), \
                self.assertRaisesRegex(f.FactoryError, 'La revisión quedó registrada'):
            self.revisar('2', '1', '1', '1', '1')  # descartar; motivo; completa; Aprobar; motivo
        self.assertEqual(f.leer(self.ident)[1]['revision']['decision'], 'aprobar')
        self.assertEqual(f.leer(self.ident)[1]['eventos'][-1]['accion'], 'revision_registrada')
        self.assertEqual(self.avisos(), [])  # la registrada es la última: no avisa
        # Un intento cortado después de una revisión registrada: ésa sigue valiendo.
        with self.assertRaises(f.FactoryError):
            self.revisar('2', '1', '1', '3')
        [aviso] = self.avisos()
        self.assertTrue(aviso.endswith('sigue valiendo la revisión anterior'), aviso)
        self.assertEqual(f.leer(self.ident)[1]['revision']['decision'], 'aprobar')
        # Si la revisión registrada ya no vale para el producto actual (otro candidato), no dice que sigue valiendo.
        self.candidato_nuevo()
        self.pedir('codex', ['baja', 'Otro nombre poco claro'])
        with self.assertRaises(f.FactoryError):
            self.revisar('2', '1', '1', '3')
        [aviso] = self.avisos()
        self.assertTrue(aviso.endswith(f'volvé a correr oracle-factory revisar {self.ident}'), aviso)

    def test_rc_anotar_no_pisa_ni_tapa(self):
        self.preparar()
        self.pedir('codex', ['baja', 'Un nombre poco claro'])
        registro = f.ruta_registro(f.leer(self.ident)[0])
        # Otro proceso escribe el registro entre que se lee y se anota el intento: no se pisa.
        evento = f.evento
        def otro_escribe_antes(estado, accion, *args, **kwargs):
            if accion == 'revision_cancelada':
                datos = json.loads(registro.read_text())
                datos['eventos'].append({'accion': 'de_otro_proceso'})
                registro.write_text(json.dumps(datos))
            return evento(estado, accion, *args, **kwargs)
        errores = io.StringIO()
        with patch.object(f, 'evento', side_effect=otro_escribe_antes), contextlib.redirect_stderr(errores), \
                patch('builtins.input', side_effect=['2', '1', '1', '3']), contextlib.redirect_stdout(io.StringIO()), \
                self.assertRaisesRegex(f.FactoryError, 'revisión cancelada'):
            f.revisar_paso_a_paso(self.ident)
        self.assertIn('no pude anotar el intento de revisión', errores.getvalue())
        eventos = [e['accion'] for e in f.leer(self.ident)[1]['eventos']]
        self.assertIn('de_otro_proceso', eventos)
        self.assertNotIn('revision_cancelada', eventos)
        # Un registro roto o de sólo lectura: el error de la revisión sigue siendo el que se ve, y se dice que no se anotó.
        for romper in ('corrupto', 'solo_lectura'):
            original = registro.read_bytes()
            errores = io.StringIO()
            respuestas = iter(['2', '1', '1'])
            def cancelar_y_romper(*_):  # descartar; motivo; completa; y al final rompe el registro y cancela
                siguiente = next(respuestas, None)
                if siguiente is not None:
                    return siguiente
                if romper == 'corrupto':
                    registro.write_text('{roto')
                else:
                    registro.chmod(0o444)
                return '3'
            with self.subTest(romper=romper), contextlib.redirect_stderr(errores), \
                    patch('builtins.input', side_effect=cancelar_y_romper), \
                    contextlib.redirect_stdout(io.StringIO()), self.assertRaisesRegex(f.FactoryError, 'revisión cancelada'):
                f.revisar_paso_a_paso(self.ident)
            self.assertIn('no pude anotar el intento de revisión', errores.getvalue())
            registro.chmod(0o644)
            registro.write_bytes(original)

    def test_rc_antes_de_mostrar_no_queda_intento(self):
        # Sin candidato con informes no hubo intento: el corte ya dice qué hacer y no se anota.
        self.preparar()
        with self.assertRaises(f.FactoryError):
            self.revisar()
        self.assertEqual(self.cancelada(), [])


if __name__ == '__main__':
    unittest.main()
