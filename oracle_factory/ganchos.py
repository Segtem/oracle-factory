"""Los hooks de Git del producto y los commits de un cambio (sacado de cli.py): el driver de unión de los registros, el
hook pre-push que corre la puerta, el trailer «Cambio:» y qué commits son de un cambio.

Lo que necesita de cli.py lo lee de `cli` en el momento de usarlo (`cli.NOMBRE`), no lo copia."""
from __future__ import annotations

from pathlib import Path
import datetime as dt
import json
import re
import shlex
import subprocess
import sys


def escribir_atributos(raiz: Path) -> bool:
    """Agrega al .gitattributes de `raiz` las líneas de ATRIBUTOS que falten; True si escribió algo."""
    atributos = raiz / ".gitattributes"
    actual = atributos.read_text(encoding="utf-8") if atributos.is_file() else ""
    presentes = {" ".join(linea.split()) for linea in actual.splitlines()}  # otro espaciado es la misma línea
    faltan = [linea for linea in cli.ATRIBUTOS if linea not in presentes]
    if faltan:
        bloque = ([cli.ATRIBUTOS_MARCA] if cli.ATRIBUTOS_MARCA not in actual else []) + faltan
        atributos.write_text(actual + ("\n" if actual and not actual.endswith("\n") else "") + "\n".join(bloque) + "\n",
                             encoding="utf-8")
    return bool(faltan)



def instalar_union() -> str:
    """Los drivers de merge (en la configuración del clon), sus atributos (en .gitattributes, versionado) y el post-merge
    que rehace lo generado. Un post-merge ajeno no se pisa."""
    py = shlex.quote(sys.executable)
    for clave, valor in cli.drivers_de_union():
        cli.ejecutar(["git", "config", clave, valor])
    cli.escribir_atributos(cli.ROOT)
    p = cli.ejecutar(["git", "rev-parse", "--git-path", "hooks"])
    avisos = []
    for nombre, llamada in (("post-merge", cli.LLAMADA_POST_MERGE), ("post-commit", cli.LLAMADA_POST_COMMIT)):
        hook = cli.ROOT / p.stdout.strip() / nombre
        if hook.exists() and cli.HOOK_MARCA not in hook.read_text(encoding="utf-8", errors="replace"):
            avisos.append(f"Aviso: ya hay un hook {hook} que no es de Factory; no lo toqué. Para que lo generado se rehaga al "
                          f"integrar, agregale esta línea antes de su final:\n{llamada.format(py=py)}")
            continue
        hook.parent.mkdir(parents=True, exist_ok=True)
        hook.write_text(f"#!/bin/sh\n{cli.HOOK_MARCA} (rehace lo generado después de integrar). Lo instaló oracle-factory hooks.\n"
                        f"{llamada.format(py=py)}\nexit 0\n", encoding="utf-8")
        hook.chmod(0o755)
    if avisos:
        return "\n".join(avisos)
    return ("Al integrar, el registro de un cambio editado en dos ramas se une con Factory (sin perder eventos) y lo generado "
            "se rehace después del merge (.gitattributes, post-merge y post-commit).")



def unir_registro(base: str, nuestro: str, suyo: str) -> int:
    """El merge driver del registro: Git pasa la versión común (%O), la de la rama actual (%A, donde va el resultado) y
    la de la otra (%B). Un registro que no se puede leer queda como conflicto para una persona."""
    try:
        leidos = [json.loads(Path(x).read_text(encoding="utf-8") or "{}") for x in (base, nuestro, suyo)]
    except (OSError, ValueError):
        return 1
    unido = cli.unir_mod.unir(*leidos)
    Path(nuestro).write_text(json.dumps(unido, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0



def rehacer_generado() -> None:
    """Lo llama el post-merge: rehace resumen.md y kb/ y, si cambiaron, los commitea aparte."""
    if not (cli.ROOT / cli.estructura.DIR).is_dir():
        return
    cli.escribir_atomico(cli.ruta_resumen(), cli.texto_resumen().encode("utf-8"))
    if (cli.ROOT / cli.kb_mod.DIR).is_dir():
        notas = cli.kb_mod.armar(cli)
        cli.escribir_kb(notas)
        for rel in cli.generadas_en_disco() - set(notas):
            (cli.ROOT / rel).unlink()
    rutas = [str(cli.ruta_resumen().relative_to(cli.ROOT))] + [r for r in cli.GENERADO_KB if (cli.ROOT / r).exists()]
    if cli.ejecutar(["git", "status", "--porcelain", "--", *rutas]).stdout.strip():
        # Dentro del post-merge Git todavía tiene MERGE_HEAD y no deja commitear rutas sueltas: el commit se arma a mano,
        # con el índice que dejó el merge más lo rehecho, y con un solo padre.
        cli.ejecutar(["git", "add", "-A", "--", *rutas])
        arbol = cli.ejecutar(["git", "write-tree"]).stdout.strip()
        hecho = cli.ejecutar(["git", "commit-tree", arbol, "-p", "HEAD", "-m", "Rehacer lo generado después de integrar (oracle-factory)"])
        if hecho.returncode or cli.ejecutar(["git", "update-ref", "HEAD", hecho.stdout.strip()]).returncode:
            raise cli.FactoryError(f"no pude commitear lo rehecho después de integrar: {(hecho.stderr or '').strip()}")
        print("Rehice resumen.md y kb/ después de integrar, en un commit aparte.")



def hook_pre_push() -> str:
    """El pre-push de la puerta local: bloquea sólo con el código propio de la puerta; todo lo demás avisa y deja pasar."""
    py = shlex.quote(sys.executable)
    return (f"#!/bin/sh\n{cli.puerta_mod.HOOK_MARCA} (secretos y verificaciones antes de publicar). Lo instaló oracle-factory hooks; "
            "git push --no-verify la saltea.\n"
            f'if [ ! -x {py} ]; then\n  echo "Aviso: no encuentro el intérprete de oracle-factory ({sys.executable}); la puerta local de salida no corrió." >&2\n'
            "  exit 0\nfi\n"
            f"{cli.LLAMADA_PUERTA.format(py=py)}\nrc=$?\n"
            f'[ "$rc" -eq {cli.puerta_mod.CODIGO_BLOQUEO} ] && exit 1\n'
            '[ "$rc" -ne 0 ] && echo "Aviso: la puerta local de salida no pudo comprobar (código $rc); el push sigue." >&2\n'
            "exit 0\n")



def lineas_para_encadenar(llamada: str) -> str:
    """Las líneas para un hook ajeno: sólo el código de bloqueo frena el push, y valen con `set -e` y como última línea del script."""
    return f'rc=0\n{llamada} || rc=$?\nif [ "$rc" -eq {cli.puerta_mod.CODIGO_BLOQUEO} ]; then exit 1; fi'



def instalar_pre_push(carpeta: Path) -> str:
    """El hook pre-push de la puerta, aparte de los de commits; nunca pisa uno ajeno."""
    hook = carpeta / "pre-push"
    if hook.exists() and cli.puerta_mod.HOOK_MARCA not in hook.read_text(encoding="utf-8", errors="replace"):
        return ("Aviso: ya hay un hook pre-push que no es de Factory; no lo toqué. Para tener la puerta local de salida (secretos y "
                f"verificaciones antes de publicar), agregale estas líneas antes de su final (la puerta bloquea con el código {cli.puerta_mod.CODIGO_BLOQUEO}; "
                f"cualquier otro código es un aviso y el push sigue):\n{cli.lineas_para_encadenar(cli.LLAMADA_PUERTA.format(py=shlex.quote(sys.executable)))}")
    hook.parent.mkdir(parents=True, exist_ok=True)
    hook.write_text(cli.hook_pre_push(), encoding="utf-8")
    hook.chmod(0o755)
    return f"Puerta local de salida en {hook}: un push con un secreto o con la guía para agentes vencida se bloquea; un kb o un resumen vencidos, o un cambio inconsistente (`verificar`), sólo avisan (git push --no-verify la saltea)."



def instalar_hook() -> str:
    """Instala los hooks de Factory en la carpeta de hooks de Git (la comparten los worktrees); nunca pisa uno ajeno."""
    p = cli.ejecutar(["git", "rev-parse", "--git-path", "hooks"])
    if p.returncode:
        return ("Hook de commits: este proyecto todavía no usa Git; después de git init, instalalo con "
                "oracle-factory hooks.")
    carpeta = cli.ROOT / p.stdout.strip()
    llamada = cli.LLAMADA_HOOK.format(py=shlex.quote(sys.executable))
    # Con un hook ajeno, en cualquiera de los dos, Factory no pone ninguno (y saca el suyo): la persona decide si
    # encadena la línea en el suyo.
    ajenos = [carpeta / n for n in cli.HOOKS if (carpeta / n).exists()
              and cli.HOOK_MARCA not in (carpeta / n).read_text(encoding="utf-8", errors="replace")]
    if ajenos:
        for nombre in cli.HOOKS:
            if carpeta / nombre not in ajenos and (carpeta / nombre).exists():
                (carpeta / nombre).unlink()
        avisos = "\n".join(f"Aviso: ya hay un hook {hook} que no es de Factory; no lo toqué ni instalé los de Factory. Para "
                           f"que tus commits digan de qué cambio son, agregale esta línea antes de su final:\n{llamada}"
                           for hook in ajenos)
        return avisos + "\n" + cli.instalar_pre_push(carpeta)
    instalados = []
    for nombre in cli.HOOKS:
        hook = carpeta / nombre
        hook.parent.mkdir(parents=True, exist_ok=True)
        hook.write_text(f"#!/bin/sh\n{cli.HOOK_MARCA} (trailer «Cambio: ID»). Lo instaló oracle-factory hooks; nunca "
                        f"impide un commit.\n{llamada}\nexit 0\n", encoding="utf-8")
        hook.chmod(0o755)
        instalados.append(nombre)
    return (f"Hook de commits en {carpeta} ({', '.join(instalados)}): un commit hecho con un solo cambio abierto lleva "
            f"«Cambio: ID».\n{cli.instalar_pre_push(carpeta)}")



def cambio_del_commit(mensaje: str) -> str | None:
    """El cambio de un commit: el que nombra su mensaje (si nombra uno solo del proyecto); si no, el único abierto; con
    varios abiertos, el único que tiene como responsable a quien commitea (su user.name de Git). Si no, ninguno."""
    nombrados = {i for i in re.findall(r"\b\d{8}-\d{6}-[a-z0-9_]+(?:-[a-z0-9_]+)*", mensaje)
                 if (cli.CHANGES / i).is_dir() and cli.ruta_registro(cli.CHANGES / i).exists()}
    if nombrados:
        return nombrados.pop() if len(nombrados) == 1 else None
    abiertos = cli.cambios_abiertos()
    if len(abiertos) == 1:
        return abiertos[0]
    yo = subprocess.run(["git", "config", "user.name"], cwd=cli.ROOT, capture_output=True, text=True).stdout.strip()
    mios = [i for i in abiertos if yo and (cli.leer(i)[1].get("responsable") or {}).get("persona") == yo]
    return mios[0] if len(mios) == 1 else None



def poner_trailer(archivo: str) -> None:
    """Lo llama el hook: agrega «Cambio: ID» al mensaje si no lo tiene, con el cambio que elige cambio_del_commit."""
    # Un mensaje todavía vacío (sólo comentarios, con el carácter de comentario que use este Git): se deja así, para
    # que cerrar el editor sin escribir siga abortando el commit; commit-msg lo completa después.
    vacio = subprocess.run(["git", "stripspace", "--strip-comments"], cwd=cli.ROOT, input=Path(archivo).read_bytes(),
                           capture_output=True, check=False)
    if vacio.returncode or not vacio.stdout.strip():
        return
    # Sólo cuenta un Cambio: del bloque de trailers, no una línea del cuerpo que empiece igual.
    trailers = cli.ejecutar(["git", "interpret-trailers", "--parse", archivo]).stdout
    if re.search(r"^Cambio:", trailers, re.M | re.I):
        return
    cambio = cli.cambio_del_commit(vacio.stdout.decode("utf-8", errors="replace"))
    if cambio:
        cli.ejecutar(["git", "interpret-trailers", "--in-place", "--trailer", f"Cambio: {cambio}", archivo])



def commits_del_cambio(identificador: str, estado: dict) -> list[dict]:
    """Los commits del cambio, del más nuevo al más viejo: los que llevan su trailer y los deducidos de sus candidatos y
    del merge que los integró (para lo de antes del trailer)."""
    formato = "--format=%H%x1f%an%x1f%aI%x1f%cI%x1f%s"  # la fecha de autor y la de cuando se hizo el commit

    def git_log(*args: str) -> list[list[str]]:
        p = cli.git_producto(["git", "log", formato, *args])
        return [] if p.returncode else [linea.split("\x1f") for linea in p.stdout.splitlines() if linea.count("\x1f") == 4]

    def completo(ref: str) -> str | None:
        p = cli.git_producto(["git", "rev-parse", "--verify", "--quiet", ref + "^{commit}"])
        return p.stdout.strip() if p.returncode == 0 else None

    base = cli.ROOT / cli.estructura.DIR / "cambios" / identificador / "candidatos"
    carpetas = {c.name: c for c in base.iterdir() if c.is_dir() and not c.is_symlink()} if base.is_dir() else {}
    pedidos = {e.get("candidato") for e in estado.get("eventos") or [] if e.get("candidato")}  # pedidos, no informes
    candidatos = {}  # sha completo -> nombre corto
    for corto_ in sorted(set(carpetas) | pedidos):
        sha = completo(str(corto_))
        if sha:
            candidatos[sha] = str(corto_)
    # --grep encuentra la línea en cualquier parte del mensaje; cuenta sólo si está en el bloque de trailers.
    con_trailer = set(cli.git_producto(["git", "log", "--all", f"--grep=^Cambio: {identificador}$",
                                "--format=%H %(trailers:key=Cambio,valueonly,separator=%x20)"]).stdout.splitlines())
    propios = {linea.split()[0] for linea in con_trailer if identificador in linea.split()[1:]}
    unidos = {c[0]: (c, "trailer") for c in git_log(*propios, "--no-walk")} if propios else {}
    deducidos = git_log("--no-walk", *candidatos) if candidatos else []
    # El merge que integró la rama, en un cambio cerrado (uno abierto no se integró: no se busca): el primer commit de
    # la línea principal (primeros padres de main, master o HEAD) que contiene un candidato. Si lo trae por su segundo
    # padre, es el merge que integró la rama; si lo trae por el primero, el cambio ya estaba en main sin merge propio
    # (directo, fast-forward, squash) y quedan sólo los candidatos. Un merge de otras ramas nunca está en esa línea.
    principal = next((r for r in ("main", "master") if completo(r)), "HEAD")

    def contiene(ref: str, sha: str) -> bool:
        return cli.git_producto(["git", "merge-base", "--is-ancestor", sha, ref]).returncode == 0

    for sha in candidatos if estado.get("fase") == "cerrada" else ():
        if not contiene(principal, sha):
            continue  # un candidato de una vuelta descartada: no está en la historia
        merge = next((m for m in cli.git_producto(["git", "rev-list", "--first-parent", "--merges", "--reverse",
                                           f"{sha}..{principal}"]).stdout.split() if contiene(m, sha)), None)
        if merge and not contiene(merge + "^1", sha):
            deducidos += git_log(f"{merge}^1..{merge}^2")
        break
    for c in deducidos:
        unidos.setdefault(c[0], (c, "deducido"))
    salida = []
    for sha, ((_, autor, fecha, fecha_commit, asunto), union) in unidos.items():
        carpeta = carpetas.get(candidatos.get(sha, ""))
        revisado = bool(carpeta and any((carpeta / "revision").glob("*.json")))  # con un informe, no sólo pedido
        salida.append({"sha": sha, "corto": sha[:7], "autor": autor, "fecha": fecha, "fecha_commit": fecha_commit,
                       "asunto": asunto, "union": union,
                       "candidato": sha in candidatos, "revisado": revisado,
                       "evidencia": bool(carpeta and (carpeta / "evidencia").is_dir())})
    return sorted(salida, key=lambda c: dt.datetime.fromisoformat(c["fecha"]), reverse=True)


# Al final a propósito: `cli` importa este módulo y lo usa sólo al llamar a sus funciones.
from . import cli  # noqa: E402
