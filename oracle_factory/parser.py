"""Construcción del parser de argumentos de oracle-factory.

No usa nada de cli.py: lo importa cli.py y lo re-exporta."""
from __future__ import annotations

from pathlib import Path
import argparse
import os

from . import __version__
from . import modos
from . import rag as rag_mod


def construir_parser() -> argparse.ArgumentParser:
    """La interfaz de la CLI; también la usan las pruebas que comprueban que la web sólo nombra comandos que existen."""
    parser = argparse.ArgumentParser(prog="oracle-factory", description="Factory local con gates humanos, OpenSpec, oracle-task y Oracle")
    parser.add_argument("--version", action="version", version=f"oracle-factory {__version__}")
    parser.add_argument("--proyecto", type=Path, default=None, help="carpeta del proyecto; por defecto se busca .factory/ subiendo desde la carpeta actual y, si no hay, se usa la actual; colocar antes del subcomando")
    parser.add_argument("--agente", default=os.environ.get("FACTORY_AGENTE"), help="actuar como agente con este nombre (o FACTORY_AGENTE); queda registrado como agente, nunca como persona")
    sub = parser.add_subparsers(dest="comando", required=True)
    p = sub.add_parser("init", help="inicializar Oracle, tareas y acuerdos sin sobrescribir configuración")
    p.add_argument("--oracle", metavar="CARPETA", help="adoptar el proyecto Oracle que ya está en esa carpeta (por ejemplo medidas)")
    p = sub.add_parser("ejemplo", help="copiar el ejemplo incluido a una carpeta nueva")
    p.add_argument("nombre", choices=["notas"])
    p.add_argument("--destino", type=Path, default=Path("examples/notas"))
    p = sub.add_parser("nuevo", help="crear tarea y paquete OpenSpec")
    p.add_argument("--capacidad")
    p.add_argument("--con-ejemplo", choices=["notas"], help="preparar documentos y catálogos del ejemplo en destinos nuevos")
    p.add_argument("--modo", choices=modos.MODOS, help="modo de trabajo del cambio (por defecto, el del proyecto)")
    p.add_argument("--sufijo", help="cómo termina el ID del cambio (por defecto, la capacidad)")
    p.add_argument("--idioma", help="idioma de la propuesta y la spec: es o en (por defecto, el del proyecto)")
    p.add_argument("titulo")
    q = sub.add_parser('listar', help='recuperar IDs completos y fases de cambios Factory')
    q.add_argument('--fase', help='sólo los cambios en esta fase')
    grupo = q.add_mutually_exclusive_group()
    grupo.add_argument('--abiertos', action='store_true', help='sólo los cambios abiertos')
    grupo.add_argument('--cerrados', action='store_true', help='sólo los cambios cerrados')
    q = sub.add_parser('pedir-revision', help='pedir una revisión independiente del candidato actual a un revisor configurado')
    q.add_argument('id'); q.add_argument('--a', dest='revisor', required=True, help='nombre del revisor en .factory/config.json')
    q.add_argument('--pedir', help='indicaciones que se agregan al pedido'); q.add_argument('--base', help='base del paquete de Clue (un commit, o «vacio» para revisar todo el producto)')
    q = sub.add_parser('tomar', help='registrarte como responsable de un cambio (con --con AGENTE); un agente con --agente se suma')
    q.add_argument('id'); q.add_argument('--con', action='append', metavar='AGENTE', help='el agente con el que trabajás (repetible)')
    q.add_argument('--relevo', action='store_true', help='tomarlo aunque lo tenga otra persona, con quien ya lo acordaste')
    q = sub.add_parser('mensaje', help='dejar un mensaje en el registro del cambio (queda versionado: sin secretos)')
    q.add_argument('id'); q.add_argument('texto')
    q.add_argument('--de', metavar='NOMBRE', help='(la usa la extensión de VS Code) el autor de un mensaje que llegó por Live Share')
    q = sub.add_parser('soltar', help='dejar de ser responsable de un cambio')
    q.add_argument('id')
    for nombre, ayuda in (('unir-registro', '(lo llama Git al integrar) unir el registro de un cambio editado en dos ramas'),
                          ('unir-generado', '(lo llama Git al integrar) dejar lo generado para rehacerlo después del merge')):
        q = sub.add_parser(nombre, help=ayuda)
        q.add_argument('base'); q.add_argument('nuestro'); q.add_argument('suyo'); q.add_argument('ruta', nargs='?')
    sub.add_parser('rehacer-generado', help='(lo llama el post-merge) rehacer resumen.md y kb/ y commitearlos aparte')
    q = sub.add_parser('decidir-union', help='elegir cuál de las dos versiones vale de algo que dos ramas decidieron distinto')
    q.add_argument('id'); q.add_argument('campo'); q.add_argument('cual', choices=['nuestro', 'suyo'])
    q = sub.add_parser('kb', help='escribir kb/ desde el registro (o --verificar); kb revisada NOTA marca una nota de personas')
    q.add_argument('accion', nargs='?', choices=['revisada'], help='revisada: marcar revisada una nota de kb/notas/')
    q.add_argument('nota', nargs='?', help='la nota de kb/notas/ (con revisada)')
    q.add_argument('--verificar', action='store_true', help='no escribe; falla si kb/ no coincide con el registro o hay notas por revisar')
    q = sub.add_parser('por-que', help='por qué existe una línea: su commit, su cambio, sus requisitos, decisiones, riesgos y notas')
    q.add_argument('referencia', metavar='ARCHIVO:LÍNEA'); q.add_argument('--json', action='store_true', help='imprimir JSON con esquema versionado')
    q = sub.add_parser('log', help='los commits de un cambio: con su trailer «Cambio: ID» o deducidos de sus candidatos (sólo lectura)')
    q.add_argument('id'); q.add_argument('--json', action='store_true', help='imprimir un objeto JSON con esquema versionado')
    sub.add_parser('hooks', help='instalar el hook de Git que agrega «Cambio: ID» a cada commit con un solo cambio abierto')
    q = sub.add_parser('trailer', help='(lo llama el hook prepare-commit-msg) agregar «Cambio: ID» al mensaje de un commit')
    q.add_argument('archivo'); q.add_argument('fuente', nargs='*')
    p = sub.add_parser('tablero', help='el tablero de comando: cada cambio abierto con su línea de tiempo, hallazgos y métricas')
    p.add_argument('--json', action='store_true', required=True, help='el tablero en JSON (lo lee la extensión de VS Code)')
    q = sub.add_parser('resumen', help='escribir .factory/resumen.md: lo vigente, los cambios abiertos, riesgos aceptados y límites')
    q.add_argument('--verificar', action='store_true', help='no escribe; falla si el resumen falta o quedó viejo')
    q.add_argument('--salida', type=Path, help='otra ruta dentro del proyecto (fuera de .factory/ cuenta en la huella)')
    q.add_argument('--ver', action='store_true', help='además, mostrarlo: con glow si está instalado, si no como texto')
    q.add_argument('--json', action='store_true', help='imprimir un objeto JSON con esquema versionado sin escribir el resumen (para IDE, paneles y MCP)')
    sub.add_parser('archivar', help='fusionar en openspec/specs/ la spec de los cambios cerrados que todavía no lo están')
    q = sub.add_parser('migrar', help='pasar el estado de cada cambio y la configuración a .factory/ (fase 2 de la estructura)')
    q.add_argument('--verificar', action='store_true', help='listar lo que movería sin escribir; falla si hay algo por migrar')
    q = sub.add_parser('donde', help='listar los artefactos de un cambio, su ruta y el gate que respaldan (sólo lectura)')
    q.add_argument('id'); q.add_argument('--candidato', help='limitarse a los artefactos de este commit (prefijo del SHA)')
    q.add_argument('--json', action='store_true', help='imprimir un objeto JSON con esquema versionado (para IDE, paneles y MCP)')
    q = sub.add_parser('trazabilidad', help='por requisito, las líneas cambiadas del candidato que ejecutan sus casos, y las que '
                       'no ejecuta ninguno (sólo lectura)')
    q.add_argument('id'); q.add_argument('--json', action='store_true', help='imprimir un objeto JSON con esquema versionado')
    q.add_argument('--base', help='base del diff (por defecto, el merge-base del candidato con main)')
    q = sub.add_parser('ruta', help='imprimir la ruta canónica donde producir un artefacto sobre el HEAD actual (no crea nada)')
    q.add_argument('id'); q.add_argument('tipo', help='evidencia, clue, revision o checkout')
    q = sub.add_parser('procedencia', help='inventario CycloneDX de las dependencias de Python de un candidato, quién usó una y auditoría contra avisos OSV (local; con --consultar-osv --red los baja)')
    q.add_argument('id', nargs='?', help='el cambio cuyo candidato recibe el inventario (sin él, el inventario sólo se muestra)')
    q.add_argument('--python', help='el Python del que se leen las distribuciones instaladas (por defecto, el .venv del proyecto)')
    q.add_argument('--json', action='store_true', help='imprimir el CycloneDX (o el resultado de --buscar y --auditar) como JSON')
    q.add_argument('--buscar', metavar='PAQUETE[==VERSIÓN]', help='qué candidatos y cambios usaron esa dependencia')
    q.add_argument('--auditar', action='store_true', help='cruzar los inventarios guardados con avisos OSV locales (con --avisos)')
    q.add_argument('--avisos', metavar='ARCHIVO', help='archivo de avisos en formato OSV, para --auditar')
    q.add_argument('--consultar-osv', action='store_true', help='bajar de OSV.dev los avisos de las dependencias de los inventarios guardados y auditar (necesita --red)')
    q.add_argument('--red', action='store_true', help='autorizar la conexión a OSV.dev (sale sólo nombre, versión y ecosistema de cada dependencia)')
    q.add_argument('--salida', metavar='ARCHIVO', help='dónde guardar los avisos de --consultar-osv, dentro del proyecto, sin «..» (por defecto .factory/local/avisos-osv.json)')
    q.add_argument('--osv-url', metavar='URL', default='https://api.osv.dev', help=argparse.SUPPRESS)
    q = sub.add_parser('buscar', help='buscar un texto en propuestas, specs, requisitos, tareas y registros (sólo lectura)')
    q.add_argument('texto'); q.add_argument('--max', type=int, default=200, dest='maximo', help='máximo de líneas a mostrar')
    q = sub.add_parser('agentes', help='escribir en AGENTS.md la guía para agentes, armada desde la CLI (o --verificar)')
    q.add_argument('--verificar', action='store_true', help='no escribe; falla si la guía falta o quedó vieja')
    sub.add_parser('mcp', help='servir el proyecto por MCP (stdio), de sólo lectura, para un agente: claude mcp add factory -- '
                              'oracle-factory --proyecto RUTA mcp')
    q = sub.add_parser('preguntar', help='responder sobre el proyecto con fuentes, registro y un modelo configurado (sólo lectura)')
    q.add_argument('texto', nargs='?', default='')
    q.add_argument('--max', type=int, default=8, dest='maximo', help='cuántos pasajes mostrar')
    q.add_argument('--json', action='store_true', help=f'imprimir un objeto JSON ({rag_mod.ESQUEMA})')
    q.add_argument('--evaluar', action='store_true', help='correr las preguntas de oro de kb/preguntas-de-oro.json')
    q.add_argument('--casos', type=Path, help='con --evaluar: sumar casos de registro, generación o abstención sin reemplazar las preguntas existentes')
    q.add_argument('--salida', type=Path, help='con --evaluar: carpeta nueva para hechos.json y detalle.json')
    q = sub.add_parser('modo', help='cambiar el modo de trabajo de un cambio')
    q.add_argument('id'); q.add_argument('nuevo_modo', choices=modos.MODOS)
    q = sub.add_parser('medir', help='listar y asociar medidas explícitas sin editar requisitos a mano')
    q.add_argument('id')
    q.add_argument('--listar', action='store_true')
    q.add_argument('--requisito', help='id completo importado por este cambio')
    q.add_argument('--medida', action='append', help='id completo de una medida efectiva; repetible')
    limites = q.add_mutually_exclusive_group()
    limites.add_argument('--sin-medir', help='declarar el límite que permanece sin medir')
    limites.add_argument('--quitar-sin-medir', action='store_true', help='eliminar explícitamente ese límite; no prueba pertinencia ni cumplimiento')
    limites.add_argument('--confirmar', action='store_true', help='confirmar con un menú las medidas que propuso el agente')
    q = sub.add_parser('revisar', help='revisión guiada del candidato vigente: muestra, pregunta y registra (persona); '
                       'con --agente deja la decisión y el motivo que propone')
    q.add_argument('id')
    q.add_argument('--decision', choices=['aprobar', 'cambios'], help='sólo con --agente: la decisión que propone')
    q.add_argument('--motivo', help='sólo con --agente: el motivo que propone')
    q = sub.add_parser('abandonar', help='abandonar un cambio con motivo (persona, en cualquier modo); '
                       'con --agente deja el motivo que propone')
    q.add_argument('id')
    q.add_argument('--motivo', help='sólo con --agente: el motivo que propone')
    for nombre, ayuda in (("aprobar-spec", "aceptación humana explícita de la propuesta/spec"),
                          ("revision-preparar", "preparar informe guiado y decisiones pendientes sin aprobar"),
                          ("importar", "importar requisitos de la spec aceptada a Oracle"),
                          ("estado", "mostrar estado y gates pendientes"),
                          ("cerrar", "cierre humano si todos los gates pasaron")):
        q = sub.add_parser(nombre, help=ayuda)
        q.add_argument("id")
        if nombre == "estado":
            q.add_argument('--json', action='store_true', help='imprimir un objeto JSON con esquema versionado (para IDE, paneles y MCP)')
    p = sub.add_parser("revision", help="registrar un informe de CodeRabbit/revisor y decisión humana")
    p.add_argument("id"); p.add_argument("--informe", type=Path, required=True)
    p.add_argument("--revisor", required=True); p.add_argument("--decision", choices=("aprobar", "cambios"), required=True)
    p.add_argument('--formato', choices=('libre', 'guiado'), default='libre')
    p.add_argument('--decisiones', type=Path, help='documento de decisiones separado, sólo en modo guiado')
    p.add_argument("--hallazgos-abiertos", type=int, help='obligatorio en formato libre; se deriva en guiado')
    p = sub.add_parser("juzgar", help="correr Oracle sobre evidencia del sensor")
    p.add_argument("id"); p.add_argument("--con", type=Path, action="append", help="hechos de un sensor; repetible, uno por sensor; por defecto, los del candidato (oracle-factory ruta ID evidencia)")
    return parser
