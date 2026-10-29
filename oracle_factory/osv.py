"""Consulta de avisos a OSV.dev para las dependencias de los inventarios guardados, sólo con autorización explícita de red.

Sale hacia el servicio únicamente el nombre, la versión y el ecosistema de cada dependencia distinta; nunca rutas, identificadores
de cambio ni contenido del repositorio. Cualquier fallo es un error: no se guarda nada y nunca se lee como «sin afectados»."""
from __future__ import annotations

import http.client
import json
import os
from pathlib import Path
import tempfile
import urllib.error
import urllib.request
from urllib.parse import quote

from . import procedencia as proc

URL = "https://api.osv.dev"
LOTE = 500  # consultas por pedido a /v1/querybatch
TIEMPO = 30  # segundos por pedido
TOPE = 50_000_000  # bytes que se aceptan de una respuesta
SALIDA = Path(".factory") / "local" / "avisos-osv.json"


def pares(inventarios: list[tuple[str, str, dict]]) -> list[tuple[str, str]]:
    """Los (nombre, versión) distintos de los inventarios; la versión sin el sufijo de corrección, que es la que OSV conoce."""
    vistos = {}
    for _, _, bom in inventarios:
        for c in bom.get("components", []):
            if isinstance(c, dict) and c.get("name") and c.get("version"):
                nombre, version = str(c["name"]), proc.sin_correccion(str(c["version"]))
                vistos.setdefault((proc.normal(nombre), version), (nombre, version))
    return sorted(vistos.values(), key=lambda p: (proc.normal(p[0]), p[1]))


def _pedir(url: str, cuerpo: dict | None = None) -> object:
    pedido = urllib.request.Request(url, data=None if cuerpo is None else json.dumps(cuerpo).encode(),
                                    headers={"Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(pedido, timeout=TIEMPO) as respuesta:
            datos = respuesta.read(TOPE + 1)
        if len(datos) > TOPE:
            raise proc.ProcedenciaError(f"la respuesta de {url} es demasiado grande")
        return json.loads(datos.decode("utf-8"))
    except proc.ProcedenciaError:
        raise
    except urllib.error.HTTPError as e:
        raise proc.ProcedenciaError(f"{url} respondió con el error HTTP {e.code}") from e
    except (OSError, ValueError, EOFError, http.client.HTTPException) as e:  # URLError, tiempo, conexión cortada, JSON o UTF-8 inválido
        raise proc.ProcedenciaError(f"no pude consultar {url} ({type(e).__name__}: {e})") from e


def consultar(base: str, lista: list[tuple[str, str]]) -> list[dict]:
    """Los avisos OSV de esas dependencias, completos y validados."""
    if not base.startswith(("http://", "https://")):
        raise proc.ProcedenciaError(f"la URL de OSV debe ser http o https: {base}")
    base = base.rstrip("/")
    ids = []
    for i in range(0, len(lista), LOTE):
        parte = lista[i:i + LOTE]
        respuesta = _pedir(f"{base}/v1/querybatch", {"queries": [
            {"package": {"name": nombre, "ecosystem": "PyPI"}, "version": version} for nombre, version in parte]})
        resultados = respuesta.get("results") if isinstance(respuesta, dict) else None
        if not isinstance(resultados, list) or len(resultados) != len(parte):
            raise proc.ProcedenciaError("OSV respondió con algo que no es el resultado esperado de querybatch")
        for r in resultados:
            vulns = r.get("vulns", []) if isinstance(r, dict) else None
            if not isinstance(vulns, list) or not all(isinstance(v, dict) and isinstance(v.get("id"), str) for v in vulns):
                raise proc.ProcedenciaError("OSV respondió con avisos sin identificador")
            ids += [v["id"] for v in vulns]
    completos = [_pedir(f"{base}/v1/vulns/{quote(i, safe='')}") for i in sorted(set(ids))]
    return proc.avisos(json.dumps(completos), f"{base}/v1/vulns") if completos else []


def guardar(ruta: Path, lista: list[dict]) -> None:
    """Escribe los avisos de una vez (archivo temporal y reemplazo), sin dejar nada parcial."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporal = tempfile.mkstemp(dir=ruta.parent, prefix=".avisos-osv-")
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as f:
            f.write(json.dumps(lista, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
        os.replace(temporal, ruta)
    except BaseException:
        Path(temporal).unlink(missing_ok=True)
        raise


def informe(raiz: Path, base: str, salida: str | None, como_json: bool) -> str:
    inventarios = proc.guardados(raiz)
    if not inventarios:
        raise proc.ProcedenciaError("no hay inventarios de procedencia guardados: nada que consultar (guardá uno con «procedencia ID»)")
    ruta = Path(salida) if salida else raiz / SALIDA
    absoluta = ruta.absolute()
    if absoluta.is_relative_to(raiz):
        proc.sin_enlaces(raiz, absoluta)  # dentro del proyecto, ningún directorio del camino es un enlace
    if ruta.is_symlink() or ruta.is_dir():
        raise proc.ProcedenciaError(f"no escribo los avisos en {ruta}")
    consultadas = pares(inventarios)
    lista = consultar(base, consultadas)
    if not lista:
        if como_json:
            return json.dumps({"avisos": 0, "inventarios": len(inventarios), "dependencias": len(consultadas), "afectados": [],
                               "corregidos": [], "sin_comparar": []}, ensure_ascii=False, indent=2) + "\n"
        return (f"Consulta a OSV: {len(consultadas)} dependencia(s) distinta(s) de {len(inventarios)} inventario(s); "
                "OSV no declara avisos para ellas: no hay candidatos expuestos.\n")
    guardar(ruta, lista)
    cabecera = f"Consulta a OSV: {len(consultadas)} dependencia(s) distinta(s); {len(lista)} aviso(s) guardado(s) en {ruta}.\n"
    return proc.informe_auditar(raiz, str(ruta), True) if como_json else cabecera + proc.informe_auditar(raiz, str(ruta), False)
