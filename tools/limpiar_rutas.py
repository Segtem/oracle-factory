"""Quita la ruta absoluta de la máquina que escribió los registros de Factory.

Reescribe a relativas a la raíz del proyecto: la `fuente` de `requisitos/*.requisito` y de
`openspec/changes/*/requisitos-previos/*.txt`, y `oracle.hechos` de cada `factory.json`. Si el contenido de un
requisito cambia y su decisión de medidas guardó el hash, lo actualiza y deja el evento `rutas_limpiadas`.
Nunca toca `tareas/`: es evidencia atada a hashes. Idempotente; `--verificar` no escribe y falla si queda algo.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from oracle_factory import cli  # noqa: E402

# Una ruta absoluta de otra máquina: lo que importa empieza en openspec/ o tareas/.
ABSOLUTA = re.compile(r'^/.*?(?<=/)((?:openspec|tareas)/.+)$')
FUENTE = re.compile(r'^(\s+fuente ")(/[^"\\]*)(")$')


def relativa(ruta):
    """La ruta relativa al proyecto, o None si no es una ruta absoluta de las conocidas."""
    if not isinstance(ruta, str):
        return None
    m = ABSOLUTA.match(ruta)
    return m.group(1) if m else None


def requisito_limpio(texto: str) -> str:
    lineas = texto.split('\n')
    for i, linea in enumerate(lineas):
        m = FUENTE.match(linea)
        if m and relativa(m.group(2)):
            lineas[i] = m.group(1) + relativa(m.group(2)) + m.group(3)
    return '\n'.join(lineas)


def serializar(estado: dict) -> str:
    return json.dumps(estado, ensure_ascii=False, indent=2) + '\n'


def planear(raiz: Path) -> tuple[dict[Path, str], dict[str, dict], list[str]]:
    """(archivo → texto nuevo, rid → hashes, problemas). No escribe nada."""
    escribir: dict[Path, str] = {}
    hashes: dict[str, dict] = {}
    problemas: list[str] = []
    previos = sorted((raiz / 'openspec' / 'changes').glob('*/requisitos-previos/*.txt'))
    for archivo in sorted((raiz / 'requisitos').glob('*.requisito')) + previos:
        viejo = archivo.read_bytes()
        nuevo = requisito_limpio(viejo.decode('utf-8')).encode('utf-8')
        if nuevo != viejo:
            escribir[archivo] = nuevo.decode('utf-8')
            if archivo.parent.name == 'requisitos':
                hashes[archivo.name.removesuffix('.requisito')] = {
                    'anterior': hashlib.sha256(viejo).hexdigest(), 'nuevo': hashlib.sha256(nuevo).hexdigest()}
    for registro in sorted((raiz / 'openspec' / 'changes').glob('*/factory.json')):
        original = registro.read_text(encoding='utf-8')
        estado = json.loads(original)
        cambios = {}
        oracle = estado.get('oracle')
        if isinstance(oracle, dict) and relativa(oracle.get('hechos')):
            cambios['hechos'] = (oracle, 'hechos', relativa(oracle['hechos']))
        decididas = {}
        for rid, decision in (estado.get('medidas') or {}).items():
            if rid in hashes and isinstance(decision, dict) and decision.get('sha256') == hashes[rid]['anterior']:
                decididas[rid] = decision
        if not cambios and not decididas:
            continue
        if serializar(json.loads(original)) != original:
            problemas.append(f'{registro.relative_to(raiz)}: no se reserializa igual; no lo toco')
            continue
        for objeto, clave, valor in cambios.values():
            objeto[clave] = valor
        for rid, decision in decididas.items():
            decision['sha256'] = hashes[rid]['nuevo']
        if decididas:
            estado.setdefault('eventos', []).append({
                'accion': 'rutas_limpiadas', **cli.actor(), 'modo': cli.modo_de(estado), 'forma': 'decidio',
                'cuando': cli.ahora(), 'requisitos': {rid: hashes[rid] for rid in decididas}})
        escribir[registro] = serializar(estado)
    return escribir, hashes, problemas


def restos(raiz: Path) -> list[str]:
    """Registros que todavía llevan una ruta absoluta (fuera de tareas/ y de la prosa de los cambios)."""
    faltan = []
    for archivo in sorted((raiz / 'requisitos').glob('*.requisito')) + sorted(
            (raiz / 'openspec' / 'changes').glob('*/requisitos-previos/*.txt')):
        if any((m := FUENTE.match(l)) and relativa(m.group(2)) for l in archivo.read_text(encoding='utf-8').split('\n')):
            faltan.append(str(archivo.relative_to(raiz)))
    for registro in sorted((raiz / 'openspec' / 'changes').glob('*/factory.json')):
        oracle = json.loads(registro.read_text(encoding='utf-8')).get('oracle')
        if isinstance(oracle, dict) and relativa(oracle.get('hechos')):
            faltan.append(str(registro.relative_to(raiz)))
    return faltan


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--proyecto', type=Path, default=Path.cwd())
    parser.add_argument('--verificar', action='store_true', help='no escribe; falla si queda algo por limpiar')
    parser.add_argument('--agente', help='nombre del agente que ejecuta; sin él, quien tenga la terminal')
    args = parser.parse_args(argv)
    raiz = args.proyecto.resolve()
    cli.ROOT = raiz
    cli.AGENTE = args.agente
    escribir, hashes, problemas = planear(raiz)
    for p in problemas:
        print('Aviso:', p, file=sys.stderr)
    if args.verificar:
        print(f'Pendientes de limpiar: {len(escribir)} archivos.')
        return 1 if escribir or problemas else 0
    for archivo, texto in escribir.items():
        archivo.write_text(texto, encoding='utf-8')
    print(f'Limpiados {len(escribir)} archivos; {len(hashes)} requisitos con hash nuevo.')
    return 1 if problemas else 0


if __name__ == '__main__':
    sys.exit(main())
