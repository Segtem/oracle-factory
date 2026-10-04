"""Evidencia del contrato de revisión guiada; casos reales y aprobaciones sólo fixture."""
from collections import Counter
import hashlib
from importlib import metadata
import io
import json
from pathlib import Path
import subprocess
import sys
import argparse
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

CONTRACTS = {
    'preparar_documentos_pendientes_sin_aprobar': [
        'g1_preparar_repetido_deja_pendientes_y_conserva_gates',
        'g1_error_parcial_y_enlace_no_modifican_gates',
        'g1_sin_aceptacion_o_cambio_cerrado_no_prepara',
        'g1_cambio_durante_preparacion_identifica_salida_obsoleta'],
    'validar_informe_guiado_y_su_alcance_declarado': [
        'g2_plantilla_y_entradas_invalidas_no_piden_confirmacion',
        'g2_schema_contexto_campos_y_rutas_se_validan',
        'g3_sin_hallazgos_exige_motivo_y_confirmacion',
        'g3_incompleta_falla_o_no_ejecutada_solo_permite_cambios'],
    'derivar_pendientes_de_decisiones_separadas': [
        'g4_resoluciones_derivan_abiertos_y_muestran_motivos',
        'g4_hash_ids_y_decisiones_invalidas_se_rechazan'],
    'registrar_confirmacion_humana_informada': [
        'g5_edicion_durante_confirmacion_preserva_revision',
        'g5_cancelar_preserva_y_nueva_revision_invalida_juicio',
        'g5_cambio_entre_lectura_y_snapshot_no_se_sobrescribe'],
    'conservar_evidencia_y_comprobar_vigencia': [
        'g6_archivos_archivados_y_contexto_se_verifican',
        'g6_fallas_de_archivo_y_estado_conservan_anterior',
        'g6_nota_fallida_no_finge_revertir_registro'],
    'mantener_formato_libre_con_declaracion_explicita': [
        'g7_libre_compatible_historico_y_opciones_explicitas'],
    'explicar_y_verificar_los_limites_del_recorrido': [
        'g8_cli_completo_y_oracle_real_en_fixture'],
}
PREFIX = 'test_review_guided.RevisionGuiada.test_'
LIMITES = ('Casos enumerados del contrato y regresiones existentes en Linux. Confirmaciones, '
           'hallazgos y resoluciones de pruebas son fixtures en repositorios temporales. '
           'No acredita calidad del análisis, competencia/identidad de actores ni claridad para principiantes.')


def escribir(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fuentes():
    files = [ROOT/'fabrica.py', ROOT/'pyproject.toml', ROOT/'docs/revision-guiada.md',
             Path(__file__), *ROOT.glob('oracle_factory/*.py'), *ROOT.glob('tests/*.py'),
             *ROOT.glob('catalogos/factory_revision_guiada.*.oracle')]
    files += [p for p in (ROOT/'oracle_factory/data/notas').rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    head = subprocess.run(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True,capture_output=True,check=True).stdout.strip()
    return {'head': head, 'sha256': {str(p.relative_to(ROOT)):sha(p) for p in sorted(set(files))}}


class Resultado(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.observados = {}
        self.cantidad = Counter()
        self.trazas = {}

    def startTest(self, test):
        self.cantidad[test.id()] += 1
        self.observados[test.id()] = 1
        super().startTest(test)

    def addSuccess(self, test):
        self.observados[test.id()] = 0
        super().addSuccess(test)

    def stopTest(self, test):
        if test.id().startswith(PREFIX):
            self.trazas[test.id()] = {'comandos': getattr(test, 'trace', []),
                                     'salida_factory': test.stdout.getvalue() if hasattr(test, 'stdout') else ''}
        super().stopTest(test)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida', type=Path, required=True, help='carpeta nueva de evidencia')
    args = parser.parse_args(argv)
    versions = {p:metadata.version(p) for p in ('oracle-metalenguaje','oracle-task')}
    if versions != {'oracle-metalenguaje':'0.38.1','oracle-task':'0.2.0'}:
        parser.error('usar las dependencias fijadas del proyecto: Oracle 0.38.1 y Task 0.2.0')
    output = args.salida.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=False)
    origen = fuentes()
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.discover(str(ROOT/'tests'))
    result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=Resultado).run(suite)
    expected = [PREFIX+name for names in CONTRACTS.values() for name in names]
    observed = {name:count for name,count in result.cantidad.items() if name.startswith(PREFIX)}
    complete = (observed == Counter(expected) and len(expected) == len(set(expected))
                and all(result.observados.get(name,1) == 0 for name in expected))
    stable = fuentes() == origen
    ok = result.wasSuccessful() and complete and stable
    rows = [{'requisito':suffix,'caso':PREFIX+name,'codigo':result.observados.get(PREFIX+name,1)}
            for suffix,names in CONTRACTS.items() for name in names]
    (output/'suite.txt').write_text(stream.getvalue(),encoding='utf-8')
    escribir(output/'trazas.json', result.trazas)
    escribir(output/'hechos.json', {'revision_guiada_caso':rows,
                                  'revision_guiada_corrida':[{'completa':int(ok),'casos':len(expected)}]})
    escribir(output/'resultado.json', {'exitoso':ok,'tests':result.testsRun,'casos_contrato':len(expected),
             'casos_exactos_sin_omisiones_duplicados_ni_fallas':complete,'fuentes_estables':stable,
             'origen':origen,'versiones':{**versions,'python':sys.version,'plataforma':sys.platform},
             'resultados':result.observados,'limites':LIMITES,
             'artefactos_sha256':{name:sha(output/name) for name in ('suite.txt','trazas.json','hechos.json')}})
    print(stream.getvalue())
    print(f'Evidencia: {output}; {result.testsRun} pruebas, {len(expected)} casos de contrato; éxito: {ok}.')
    print(LIMITES)
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
