# Abandonar un cambio con motivo, decidido por una persona

## Why

Hay seis cambios abiertos desde antes de los modos de trabajo y tres carpetas de `openspec/changes/` sin registro de Factory. Algunos ya no se van a terminar: `validar-el-flujo` es una plantilla que nunca se completó, `explicar-oracle` lo reemplazó la capacidad `web`, y `dist-uv` se entregó fuera del flujo (de 0.1.0a1 a 0.1.0a9). Hoy Factory sólo sabe cerrar, y cerrar exige revisión y veredicto en verde. Por eso esos cambios quedan abiertos para siempre: el resumen dice «6 cambios abiertos», y sus requisitos sin medir ensucian la cobertura de cada `juzgar`.

Tarea de origen: `20261007-114731-cambios-viejos`. Brian eligió el alcance el 2026-10-12, con un menú: sumar `abandonar` y aplicar el plan a los cambios viejos.

## What changes

- **`oracle-factory abandonar ID`**: una persona lo decide desde su terminal, con un menú y un motivo, en cualquier modo de trabajo. Un agente no abandona nada: con `--agente` y `--motivo` deja propuesto el motivo, que la persona ve como opción.
- **Lo abandonado no queda abierto ni medido.** El cambio pasa a la fase `abandonada`, con quién, cuándo y por qué. Sus archivos `.requisito` salen de `requisitos/` (siguen en la historia de Git) y quedan listados en el registro. La tarea del tracker se cierra con una nota que da el motivo. La propuesta y la spec del cambio no se tocan, y nada se fusiona en `openspec/specs/`.
- **Los comandos lo distinguen.** `estado` muestra quién lo abandonó y por qué, sin próximo paso. Los comandos que modifican un cambio lo rechazan. `listar --abiertos` no lo muestra. El resumen lo pone en una sección propia, sin contarlo entre los abiertos.
- **Una carpeta sin registro también se abandona**, con un registro mínimo. Así deja de aparecer como «sin registro».

## Out of scope

- Decidir cada cambio viejo: eso lo hace Brian con el comando nuevo, después de integrarlo.
- Cerrar con evidencia `elegir-medidas` e `inicio-guiado`: es un paso aparte.
- Reabrir un cambio abandonado: se crea uno nuevo.

## Human decisions

- Brian decidió el alcance (2026-10-12).
- Que abandonar sea siempre de una persona, también en modo autónomo, es parte de esta propuesta: abandonar descarta promesas.
