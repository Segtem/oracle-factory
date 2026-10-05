"""Sondas de R2 sobre 0234cc9. Cada prueba afirma el defecto observado."""
import sys, re
from unittest.mock import patch
sys.path.insert(0, 'tests')
from test_modos import Modos as Base, f, modos


class SondasD(Base):
    def _hasta_revision(self, ident):
        hechos, informe = self.producto_y_hechos(ident)
        with self.escribe(f'REGISTRAR REVISION {ident}'):
            f.revisar(ident, informe, 'Persona fixture', 'aprobar', 0)
        return hechos

    def test_r2d_01_registro_no_ata_el_contenido(self):
        # La persona elige una medida; el agente edita el .requisito a mano y agrega otra; el registro sigue valiendo.
        ident = self.crear()
        self.aceptar(ident); f.importar(ident)
        rid = self.estado(ident)['requisitos'][0]
        f.medir(ident, requisito_id=rid, medidas=['notas.casos_ejecutados'], quitar_sin_medir=True)
        ruta = self.root / 'requisitos' / f'{rid}.requisito'
        ruta.write_text(ruta.read_text().replace('medido_por notas.casos_ejecutados', 'medido_por notas.casos_ejecutados, notas.resultados'))
        print('\nR2D-01 archivo:', [l for l in ruta.read_text().splitlines() if 'medido_por' in l], file=sys.stderr)
        print('R2D-01 sin decisión:', f.medidas_sin_decision(self.estado(ident)), file=sys.stderr)
        self.assertEqual(f.medidas_sin_decision(self.estado(ident)), [])
        hechos = self._hasta_revision(ident)
        f.juzgar(ident, hechos)
        with self.escribe(f'CERRAR {ident}'):
            f.cerrar(ident)
        self.assertEqual(self.estado(ident)['fase'], 'cerrada')

    def test_r2d_02_indentacion_distinta_esquiva_la_regla(self):
        # Medidas escritas a mano con otra sangría: Oracle las lee, la regla no las ve.
        ident = self.crear()
        self.aceptar(ident); f.importar(ident)
        rid = self.estado(ident)['requisitos'][0]
        ruta = self.root / 'requisitos' / f'{rid}.requisito'
        texto = ruta.read_text()
        print('\nR2D-02 original:', texto, file=sys.stderr)
        texto = re.sub(r'\n\s*medido_por[^\n]*', '', texto)
        texto = re.sub(r'\n\s*sin_medir[^\n]*', '', texto)
        ruta.write_text(texto.rstrip('\n') + '\n  medido_por notas.casos_ejecutados, notas.resultados\n')
        print('R2D-02 editado:', ruta.read_text(), file=sys.stderr)
        self.assertEqual(f.medidas_sin_decision(self.estado(ident)), [])
        hechos = self._hasta_revision(ident)
        f.juzgar(ident, hechos)
        print('R2D-02 fase:', self.estado(ident)['fase'], file=sys.stderr)
        self.assertEqual(self.estado(ident)['fase'], 'oracle_verde')

    def test_r2d_03_persona_no_puede_registrar_medidas_ya_presentes(self):
        # Medidas en el archivo sin decisión: estado pide «elegilas con medir», pero medir con las mismas no registra.
        ident = self.crear()
        self.aceptar(ident); f.importar(ident)
        rid = self.estado(ident)['requisitos'][0]
        ruta = self.root / 'requisitos' / f'{rid}.requisito'
        f.medir(ident, requisito_id=rid, medidas=['notas.casos_ejecutados', 'notas.resultados'], quitar_sin_medir=True)
        estado = self.estado(ident); del estado['medidas'][rid]   # p. ej. edición a mano o registro perdido
        (self.root / 'openspec/changes' / ident / 'factory.json').write_text(__import__('json').dumps(estado, ensure_ascii=False, indent=2) + '\n')
        self.assertEqual(f.medidas_sin_decision(self.estado(ident)), [rid])
        f.medir(ident, requisito_id=rid, medidas=['notas.casos_ejecutados', 'notas.resultados'], quitar_sin_medir=True)
        print('\nR2D-03 salida:', self.stdout.getvalue().splitlines()[-1], file=sys.stderr)
        self.assertEqual(f.medidas_sin_decision(self.estado(ident)), [rid])
