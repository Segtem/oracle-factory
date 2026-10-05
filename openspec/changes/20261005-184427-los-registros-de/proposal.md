# Los registros de Factory funcionan en otra máquina

## Why

Una persona prepara un cambio en su máquina y otra lo continúa en la suya a través de Git: es el centro del protocolo de colaboración. El 2026-10-05 se probó con contenedores Docker, que no comparten ningún archivo: tres «máquinas» (un remoto y dos estaciones, con usuarios y rutas distintos) y un cambio del ejemplo `notas`.

Ana dejó el cambio con el veredicto de Oracle en verde y subió el repositorio. Bruno lo clonó en otra máquina y encontró:

- `estado` dice **«Pendiente: hechos ausente»**, y `cerrar` responde **«no se puede cerrar: hechos ausente»**. El cambio no se puede cerrar fuera de la máquina donde se juzgó.
- La causa: `juzgar` guarda en `factory.json` la **ruta absoluta** de los hechos (`/home/ana/producto/tareas/<ID>/hechos.json`) y después la usa para verificarlos. En otra máquina esa ruta no existe.
- Oracle escribe la `fuente` de cada requisito también como ruta absoluta (`/home/ana/producto/openspec/…`). No bloquea nada, pero deja en el repositorio la ruta privada de una persona y ya figuraba como hallazgo A-04.

Lo que sí funcionó entre máquinas y se conserva: la huella de archivos del producto es idéntica, los actores se leen bien («Ana (persona, decidio, modo confirmacion)») y la vigencia por contenido avisa que el HEAD cambió con el producto idéntico.

Además, el flujo que documenta el README guarda los hechos en `.factory-demo/`, una carpeta que Git ignora: esos hechos nunca llegarían a otra máquina.

## What changes

1. **Los hechos se guardan con ruta relativa a la raíz del proyecto**, y se verifican resolviéndola desde la raíz de cada clon.
2. **Advertencia cuando los hechos no viajan:** si están fuera del proyecto, o dentro pero ignorados por Git, `juzgar` lo advierte (otra máquina no podrá verificarlos) y sigue.
3. **`fuente` relativa:** `importar` deja la `fuente` de cada requisito relativa a la raíz del proyecto.
4. **Mensaje útil:** cuando faltan los hechos, el pendiente nombra la ruta y dice cómo recuperarlo.
5. **Un cambio juzgado en una máquina se cierra desde otra:** se comprueba con contenedores Docker (`tools/verify_maquinas.py`).
6. **Sin migración:** los registros anteriores siguen leyéndose; si su ruta absoluta no existe, se informa y se vuelve a juzgar.

## Out of scope

- Reescribir registros existentes.
- Rechazar los hechos que no viajan (sólo se advierte, por compatibilidad).
- Cambiar Oracle: la `fuente` se normaliza en Factory después de importar; que Oracle la escriba relativa queda como una tarea suya.
- Rutas de otras herramientas (Clue guarda la ruta del checkout revisado en su paquete; es un límite ya conocido).
- El trabajo en un mismo repositorio desde varias carpetas (worktrees).

## Human decisions

Brian respondió en la conversación del 2026-10-05, aceptando las tres recomendaciones:

1. **Hechos que no viajan:** se advierte y se sigue; no se rechazan, por compatibilidad con lo existente.
2. **Dónde se guardan los hechos:** en `tareas/<ID>/`, por ahora, sin esperar a la carpeta `.factory/` de la estructura, que todavía no está implementada.
3. **La prueba con Docker:** `tools/verify_maquinas.py` queda como herramienta de evidencia que se corre a pedido y no forma parte de la suite de pruebas.

Pendiente: aceptación de proposal.md y spec.md. Preparar esto no la acepta ni autoriza implementarlo.
