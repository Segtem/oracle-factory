"""Abandonar un cambio: escenarios ab1–ab4 de la spec (decisión de persona, sin abrir ni medir, resumen, carpeta sin registro)."""
import contextlib
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_archivo as _archivo  # noqa: E402

f = _archivo.f
MOTIVO = 'lo reemplazó otro cambio; queda en la historia de Git.'
OTRA = '''# Capability: otra

## ADDED Requirements

### Requirement: algo de otra capacidad
Tipo: funcional
El sistema SHALL hacer algo.

#### Scenario: hacerlo
- GIVEN un estado
- WHEN se hace
- THEN queda hecho
'''


class Abandonar(unittest.TestCase):
    def responde(self, *respuestas):
        return patch('builtins.input', side_effect=list(respuestas))

    def importado(self, modo=None):
        ident = self.cambio_importado('Otra', 'otra', OTRA)
        if modo:  # el modo no cambia nada de abandonar: se fija en el registro, sin el menú de cambiar_modo
            carpeta, estado = f.leer(ident)
            f.guardar(carpeta, {**estado, 'modo': modo})
        return ident

    def proponer(self, ident, motivo=MOTIVO):
        with patch.object(f, 'AGENTE', 'claude-code'):
            f.abandonar(ident, motivo)

    def requisito(self, rid):
        return self.root / 'requisitos' / f'{rid}.requisito'

    def tarea(self, ident):
        return (self.root / 'tareas' / ident / 'TAREA.md').read_text(encoding='utf-8')

    def resumen(self):
        f.comando_resumen(False, None)
        return (self.root / '.factory/resumen.md').read_text(encoding='utf-8')

    # --- ab1: abandonar es una decisión de persona con motivo -------------------------------------------------------
    def test_ab1_la_persona_abandona_con_el_motivo_propuesto(self):
        ident = self.importado()
        self.proponer(ident)
        with self.responde('1', '1'):  # Abandonar el cambio · Propuesto por el agente
            f.abandonar(ident)
        estado = f.leer(ident)[1]
        self.assertEqual(estado['fase'], 'abandonada')
        a = estado['abandono']
        self.assertEqual((a['tipo_actor'], a['forma'], a['motivo'], a['origen_motivo']), ('persona', 'confirmo', MOTIVO, 'agente'))
        self.assertTrue(a['cuando'])
        self.assertNotIn('abandono', estado.get('motivos_propuestos') or {})

    def test_ab1_un_agente_no_abandona(self):
        ident = self.importado(modo='autonomo')
        self.proponer(ident)
        estado = f.leer(ident)[1]
        self.assertNotEqual(estado['fase'], 'abandonada')
        self.assertEqual(estado['motivos_propuestos']['abandono']['motivo'], MOTIVO)
        self.assertNotIn('abandono', estado)
        with patch.object(f, 'AGENTE', 'claude-code'), self.assertRaisesRegex(f.FactoryError, '--motivo'):
            f.abandonar(ident)  # sin motivo tampoco abandona

    def test_ab1_la_persona_cancela(self):
        ident = self.importado()
        antes = self.archivos()
        with self.responde('2'), self.assertRaisesRegex(f.FactoryError, 'cancelado'):
            f.abandonar(ident)
        self.assertEqual(self.archivos(), antes)

    def test_ab1_sin_terminal_no_se_abandona(self):
        ident = self.importado()
        antes = self.archivos()
        with patch.object(f, 'terminal_interactiva', return_value=False), self.responde('1', '1'), \
                self.assertRaisesRegex(f.FactoryError, 'terminal interactiva'):
            f.abandonar(ident)
        self.assertEqual(self.archivos(), antes)

    def test_ab1_un_cambio_cerrado(self):
        ident = self.cambio_cerrado()
        antes = self.archivos()
        with self.responde('1', '1'), self.assertRaisesRegex(f.FactoryError, 'cerrado'):
            f.abandonar(ident)
        self.assertEqual(self.archivos(), antes)

    # --- ab2: lo abandonado no queda abierto ni medido ----------------------------------------------------------------
    def test_ab2_abandonar_un_cambio_con_requisitos_importados(self):
        cerrado = self.cambio_cerrado()  # con spec consolidada, que no tiene que cambiar
        ident = self.importado()
        requisitos = f.leer(ident)[1]['requisitos']
        self.assertTrue(requisitos and all(self.requisito(r).is_file() for r in requisitos))
        specs = {k: v for k, v in self.archivos().items() if k.startswith(('openspec/', '.factory/specs/'))}
        with self.responde('1', '1'):  # Abandonar · Armado con los datos del cambio
            f.abandonar(ident)
        self.assertFalse(any(self.requisito(r).exists() for r in requisitos))
        self.assertEqual(f.leer(ident)[1]['abandono']['requisitos_quitados'], requisitos)
        self.assertIn('ESTADO: CERRADA', self.tarea(ident))
        self.assertIn('Abandonado por una persona', self.tarea(ident))
        self.assertEqual({k: v for k, v in self.archivos().items() if k.startswith(('openspec/', '.factory/specs/'))}, specs)
        self.assertTrue(f.leer(cerrado)[1]['requisitos'] and self.requisito(f.leer(cerrado)[1]['requisitos'][0]).is_file())
        self.salida()
        f.listar(abiertos=True)
        self.assertNotIn(ident, self.salida())
        f.mostrar(ident)
        estado = self.salida()
        self.assertIn('Fase: abandonada', estado)
        self.assertIn('motivo: no se va a terminar', estado)
        self.assertIsNone(f.proximo_paso(ident))

    def test_ab2_un_comando_sobre_un_cambio_abandonado(self):
        ident = self.importado()
        with self.responde('1', '1'):
            f.abandonar(ident)
        antes = self.archivos()
        for comando in (lambda: f.medir(ident, listar_opciones=True), lambda: f.juzgar(ident, self.root / 'hechos.json'),
                        lambda: f.cerrar(ident), lambda: f.abandonar(ident)):
            with self.responde('1', '1'), self.assertRaisesRegex(f.FactoryError, 'abandonado'):
                comando()
        self.assertEqual(self.archivos(), antes)

    def test_ab2_si_el_tracker_no_cierra_no_cambia_nada(self):
        ident = self.importado()
        antes = self.archivos()
        real = f.ejecutar

        def no_cierra(argv, *a, **k):
            if list(argv[:2]) == ['tasks', 'close']:
                return f.subprocess.CompletedProcess(argv, 1, '', 'el tracker no pudo cerrar')
            return real(argv, *a, **k)
        with patch.object(f, 'ejecutar', side_effect=no_cierra), self.responde('1', '1'), \
                self.assertRaisesRegex(f.FactoryError, 'no pudo cerrar'):
            f.abandonar(ident)
        self.assertEqual(self.archivos(), antes)  # ni el registro, ni los requisitos, ni una nota en la tarea abierta

    def test_ab2_un_corte_despues_del_registro_se_completa(self):
        ident = self.importado()
        requisitos = f.leer(ident)[1]['requisitos']
        contenido = {r: self.requisito(r).read_bytes() for r in requisitos}
        with self.responde('1', '1'):
            f.abandonar(ident)
        for r, datos in contenido.items():  # como si el proceso se hubiera cortado antes de borrarlos
            self.requisito(r).write_bytes(datos)
        registro = f.leer(ident)[1]
        with patch('builtins.input', side_effect=AssertionError('no vuelve a preguntar')):
            f.abandonar(ident)
        self.assertFalse(any(self.requisito(r).exists() for r in requisitos))
        self.assertEqual(f.leer(ident)[1], registro)

    # --- ab3: el resumen muestra lo abandonado aparte -----------------------------------------------------------------
    def test_ab3_un_cambio_abandonado_en_el_resumen(self):
        f.nuevo('Abierto', 'tercera')
        ident = self.importado()
        self.proponer(ident)
        with self.responde('1', '1'):
            f.abandonar(ident)
        texto = self.resumen()
        self.assertIn('· 1 cambio abierto\n', texto)
        seccion = texto.split('## Cambios abandonados', 1)[1].split('\n## ', 1)[0]
        self.assertIn(ident, seccion)
        self.assertIn(MOTIVO, seccion)
        self.assertIn('Otra', seccion)  # el título
        abandono = f.leer(ident)[1]['abandono']
        self.assertIn(f"({abandono['actor']}, {abandono['cuando'][:10]})", seccion)  # quién y cuándo
        self.assertNotIn(f'### {ident}', texto.split('## Cambios abiertos', 1)[1].split('\n## ', 1)[0])

    # --- ab4: una carpeta sin registro también se abandona ---------------------------------------------------------
    def test_ab4_una_carpeta_anterior_al_flujo(self):
        ident = '20261002-224749-revision-poc'
        carpeta = self.root / 'openspec/changes' / ident
        carpeta.mkdir(parents=True)
        (carpeta / 'proposal.md').write_text('# Revisión de la POC\n\nAnterior al registro.\n', encoding='utf-8')
        self.assertIn(ident, self.resumen().split('sin registro de Factory', 1)[1])
        with self.assertRaisesRegex(f.FactoryError, 'sin registro'), patch.object(f, 'AGENTE', 'claude-code'):
            f.abandonar(ident, MOTIVO)  # no hay dónde guardar una propuesta
        errores = io.StringIO()
        with self.responde('1', '2', MOTIVO), contextlib.redirect_stderr(errores):  # Abandonar · Otro · el motivo escrito
            f.abandonar(ident)
        self.assertIn('no tiene tarea', errores.getvalue())
        estado = f.leer(ident)[1]
        self.assertEqual((estado['fase'], estado['titulo'], estado['abandono']['motivo'], estado['abandono']['origen_motivo']),
                         ('abandonada', 'Revisión de la POC', MOTIVO, 'persona'))
        texto = self.resumen()
        self.assertNotIn('sin registro de Factory', texto)
        self.assertIn(ident, texto.split('## Cambios abandonados', 1)[1])
        self.salida()
        f.mostrar(ident)
        self.assertIn('Fase: abandonada', self.salida())
        f.comando_donde(ident, None)  # los comandos de lectura aceptan el registro mínimo, sin spec
        donde = self.salida()
        self.assertIn('proposal.md', donde)
        self.assertNotIn('no válido', donde)
        f.listar()
        self.assertIn(f'{ident}  abandonada', self.salida())


for _nombre in ('setUp', 'escribe', 'git', 'salida', 'archivos', 'cambio_cerrado', 'cambio_importado'):
    setattr(Abandonar, _nombre, getattr(_archivo.Archivo, _nombre))  # el fixture de archivo, sin heredar sus pruebas


if __name__ == '__main__':
    unittest.main()
