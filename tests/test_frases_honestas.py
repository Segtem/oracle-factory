"""Los textos no prometen más de lo que hace Factory (fh1) y la mutación documental de docs/tests.md muere (fh2).

Las afirmaciones vienen de las auditorías de Astra (H9, H10) y de Fable (H2, H12, H14). Cada una es una lista explícita: la frase
vieja que no tiene que volver y la que la reemplaza, en su archivo. Los espacios y saltos de línea no cuentan (el README va cortado
en líneas de 120)."""
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1]

AFIRMACIONES = [  # (archivo, frase vieja, frase que la reemplaza)
    ('README.md', 'No hace push ni publica ramas por su cuenta.',
     'No empuja el producto ni publica ramas: sólo `sincronizar`, corrido por una persona, sube el almacén de registros.'),
    ('README.md', '- No hace push ni publica ramas.',
     '- No empuja el producto ni publica ramas; `sincronizar`, corrido por una persona, sube el almacén de registros.'),
    ('README.md', 'Una decisión de persona nunca la toma un agente.',
     'Con `--agente`, un agente nunca queda registrado como persona; sin él, Factory no puede saberlo.'),
    ('README.md', 'Esta ampliación aún no está en el paquete publicado.', '`preguntar` hace consultas al registro'),
    ('README.md', '`oracle-factory --proyecto RUTA mcp` sirve el proyecto por MCP, de sólo lectura.',
     'no cambia nada versionado, pero `preguntar` escribe su caché local y puede llamar al modelo configurado'),
    ('docs/agentes.md', 'sirve el proyecto por MCP (stdio), de sólo lectura.',
     'no cambia nada versionado, pero `preguntar` escribe su caché local y puede llamar al modelo configurado'),
    ('site/index.html', 'Factory no ejecuta agentes, pruebas ni revisores automáticamente.',
     'Factory no corre las pruebas del producto: lanza a los revisores que declara el proyecto y, si se lo piden, al agente.'),
    ('site/index.html', 'la coordinación automática de agentes es una capacidad prevista',
     'Factory lanza a los revisores y, con autopilot, al agente, con topes'),
    ('site/index.html', 'El alpha no elige, invoca ni coordina esos agentes.',
     'Factory no escribe ese código: lanza a los revisores que declara el proyecto y, si se lo piden, al agente, con topes de pasos y minutos.'),
    ('site/index.html', 'Coordinación automática prevista', 'pedir-revision · autopilot --ejecutar --lanzar'),
    ('site/factory.js', 'La coordinación automática de agentes y la revisión con IA de Clue son capacidades previstas.',
     'Factory lanza a los revisores con IA que declara el proyecto y, con autopilot, al agente; Clue valida sus informes.'),
    ('site/factory.js', 'La coordinación automática de agentes es una capacidad prevista. Hoy Factory no escribe ni ejecuta ese código.',
     'Factory no escribe ese código: lo escribe una persona, o el agente que lanza autopilot con topes.'),
    ('site/desde-cero.html', '<span>Windows · macOS · Linux</span>', '<span>Verificado en Linux · Windows y macOS sin prueba automatizada</span>'),
    ('oracle_factory/parser.py', '(sólo lectura: no corre nada)', '(sin --ejecutar sólo lee; con --ejecutar actúa, con topes)'),
    ('oracle_factory/parser.py', 'EXPERIMENTAL (etapa 1 de 6)', 'carpeta del almacén de registros'),
    ('docs/colaboracion.md', 'Factory tampoco valida automáticamente los schemas de Clue',
     'Factory valida con Clue los informes de los revisores: al pedirlos (`pedir-revision`) y al preparar la revisión'),
    ('site/colaboracion.html', 'Factory no llama a Clue:', 'Factory valida con Clue los informes de los revisores'),
    ('docs/ci.md', '(el de la puerta local, `oracle-factory hooks`, no lo incluye)',
     'la puerta local de `oracle-factory hooks` ya corre `verificar`, pero sólo avisa'),
    ('docs/despliegue.md', 'Nada se despliega solo: ni por CI, ni por un agente.',
     'un agente despliega sólo si una persona le dio autonomía en producción'),
]


def plano(texto: str) -> str:
    return re.sub(r'\s+', ' ', texto)


def problemas(raiz: Path, afirmaciones=AFIRMACIONES) -> list[str]:
    salida = []
    for archivo, vieja, nueva in afirmaciones:
        texto = plano((raiz / archivo).read_text(encoding='utf-8'))
        if plano(vieja) in texto:
            salida.append(f'{archivo}: todavía dice «{vieja}»')
        if plano(nueva) not in texto:
            salida.append(f'{archivo}: falta «{nueva}»')
    return salida


# --- fh1: los textos no prometen de más -----------------------------------------------------------------------------------
class Afirmaciones(unittest.TestCase):
    def test_fh1_ninguna_frase_vieja_esta_y_cada_reemplazo_si(self):
        self.assertEqual(problemas(SOURCE), [])

    def test_fh1_una_frase_vieja_que_vuelve_se_nombra_con_su_archivo(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'docs').mkdir()
            (Path(tmp) / 'docs/despliegue.md').write_text('Nada se despliega\nsolo: ni por CI, ni por un agente.\n', encoding='utf-8')
            [vieja, falta] = problemas(Path(tmp), [a for a in AFIRMACIONES if a[0] == 'docs/despliegue.md'])
        self.assertIn('docs/despliegue.md: todavía dice', vieja)
        self.assertIn('docs/despliegue.md: falta', falta)


    def test_fh1_ninguna_pagina_presenta_como_prevista_la_coordinacion_de_agentes(self):  # la clase, no sólo las frases de la lista
        patron = re.compile(r'(coordinaci[oó]n[^.<"]{0,40}previst|no (?:elige|invoca|coordina|lanza)[^.<"]{0,40}agentes|'
                            r'no ejecuta (?:agentes|revisores))', re.I)
        hallados = [f'{p.relative_to(SOURCE)}: {m.group(0)}' for p in sorted([*(SOURCE / 'site').glob('*.html'), *(SOURCE / 'site').glob('*.js'),
                                                                            SOURCE / 'README.md', *(SOURCE / 'docs').rglob('*.md')])
                    for m in patron.finditer(plano(p.read_text(encoding='utf-8')))]
        self.assertEqual(hallados, [])


# --- fh2: la mutación documental muere ------------------------------------------------------------------------------------
class Mutacion(unittest.TestCase):
    def test_fh2_la_mutacion_doc_dice_que_bloquea_hace_fallar_su_prueba(self):
        sys.path.insert(0, str(SOURCE))
        from tools import mutar_tests_unitarios as mt
        [(nombre, archivo, vieja, nueva, _, prueba)] = [m for m in mt.MUTACIONES if m[0] == 'doc_dice_que_bloquea']
        with tempfile.TemporaryDirectory() as tmp:
            copia = Path(tmp) / 'copia'
            subprocess.run(['cp', '-a', '--reflink=auto', str(SOURCE), str(copia)], check=True)
            ruta = copia / archivo
            ruta.write_text(ruta.read_text(encoding='utf-8').replace(vieja, nueva, 1), encoding='utf-8')
            r = subprocess.run([sys.executable, '-m', 'unittest', '-k', prueba, 'test_tests_unitarios'], cwd=copia / 'tests',
                               capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=300)
        self.assertNotEqual(r.returncode, 0, r.stderr[-1500:])
        self.assertIn('Ran 1 test', r.stderr)


if __name__ == '__main__':
    unittest.main()
