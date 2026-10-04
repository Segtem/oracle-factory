"""Hechos de los casos concretos del contrato; no sustituyen revisión humana.

Corre la suite real y vincula resultados a los requisitos importados. Los nombres
de cada caso son parte del sensor, que se debe revisar junto con las medidas.
No prueba otras plataformas ni evita carreras con editores externos.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

CONTRACTS = {
    '20261004-005956-inicio-guiado': {
        'preparar_ejemplo_sin_aprobacion': ('InicioGuiado', [
            'ejemplo_completo_pendiente_y_sin_aprobaciones',
            'capacidad_incompatible_o_padre_archivo_no_crea_tarea']),
        'preservar_archivos_existentes': ('InicioGuiado', [
            'conflictos_se_rechazan_antes_de_crear_tarea',
            'ejemplo_existente_no_crea_tarea_duplicada_al_reintentar',
            'copia_interrumpida_informa_destinos_y_no_crea_tarea',
            'fallo_despues_de_crear_tarea_reporta_id_real_para_recuperar',
            'enlaces_de_destino_no_escriben_fuera_del_proyecto']),
        'recuperar_cambios_y_siguiente_paso': ('InicioGuiado', [
            'init_idempotente_conserva_configuracion_y_muestra_pasos_factory',
            'listar_recupera_cambio_y_no_confunde_tareas_solas']),
    },
    '20261004-005956-elegir-medidas': {
        'asociacion_explicita_y_valida': ('EleccionMedidas', [
            'asociacion_preserva_prosa_fuente_comentarios_y_limite_parcial',
            'quitar_limite_es_explicito_y_nuevo_limite_permanece_parcial',
            'medida_inexistente_duplicada_o_requisito_ajeno_no_mutan',
            'listado_es_solo_lectura_y_muestra_limites_y_fuentes']),
        'preservar_requisito_ante_error': ('EleccionMedidas', [
            'sintaxis_invalida_no_se_repara_ni_sobrescribe',
            'spec_desactualizada_rechaza_asociacion',
            'enlace_en_requisito_rechazado',
            'edicion_concurrente_detectada_no_sobrescribe_al_editor',
            'escritura_fallida_conserva_requisito_y_no_deja_verde_viejo',
            'catalogo_eliminado_durante_asociacion_no_muta']),
        'invalidar_evidencia_anterior': ('EleccionMedidas', [
            'cambio_invalida_y_repeticion_identica_conserva_validaciones',
            'escritura_fallida_conserva_requisito_y_no_deja_verde_viejo']),
    },
}

class Result(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.observed = {}
    def startTest(self, test):
        if test.id() in self.observed:
            raise RuntimeError('caso duplicado: ' + test.id())
        self.observed[test.id()] = 1
        super().startTest(test)
    def addSuccess(self, test):
        self.observed[test.id()] = 0
        super().addSuccess(test)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida', type=Path, required=True)
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.discover(str(ROOT/'tests'))
    result = unittest.TextTestRunner(verbosity=2, resultclass=Result).run(suite)
    rows = []
    for change, mapping in CONTRACTS.items():
        state = json.loads((ROOT/'openspec/changes'/change/'factory.json').read_text())
        for suffix, (cls, cases) in mapping.items():
            ids = [rid for rid in state['requisitos'] if rid.rsplit('.', 1)[-1] == suffix]
            if len(ids) != 1:
                raise RuntimeError('no encuentro requisito importado inequívoco: ' + suffix)
            for case in cases:
                name = f'test_guided.{cls}.test_{case}'
                rows.append({'requisito': ids[0], 'caso': name,
                             'codigo': result.observed.get(name, 1)})
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_text(json.dumps({'verificacion_factory': rows}, ensure_ascii=False, indent=2)+'\n')
    manifest = {'python': sys.version, 'tests': result.testsRun, 'exitoso': result.wasSuccessful(),
                'limites': 'Casos enumerados en este sensor, Linux. No es aprobación humana ni prueba de propiedades no observadas.',
                'sha256': {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
                           for p in ('oracle_factory/cli.py', 'tests/test_guided.py', 'tools/verify_contracts.py')}}
    args.salida.with_suffix('.manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    return 0 if result.wasSuccessful() and all(row['codigo'] == 0 for row in rows) else 1

if __name__ == '__main__':
    raise SystemExit(main())
