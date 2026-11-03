---
name: oracle-factory
description: Cómo un agente (Claude Code, Codex, agy) trabaja un cambio con Oracle Factory de punta a punta sin repetir los errores de procedimiento más comunes: qué mirar antes de abrir un cambio, el orden de los pasos, la evidencia, las rondas de revisión, el camino ligero y cuándo parar. Usala cuando el proyecto tenga `.factory/` o cuando te pidan un cambio, una spec, una revisión o una integración.
---

# Trabajar un cambio con Oracle Factory

Esta skill es el **procedimiento**. Quién decide cada paso y los comandos disponibles están en el bloque generado de `AGENTS.md` (`docs/agentes.md`); no los repitas de memoria, mirá ese bloque. Las decisiones son de una persona: vos trabajás, proponés y dejás todo registrado.

## 1. Antes de abrir un cambio

- `git worktree list`, `oracle-factory listar` y `oracle-factory buscar TEXTO`: si ya hay un cambio o una rama sobre lo mismo, no abras otro. Abrir un cambio duplicado costó una integración entera.
- Mirá `tareas/` del proyecto: puede haber una tarea abierta que lo cubra.
- Corré cada comando como agente: `oracle-factory --agente TU_NOMBRE …`. Sin `--agente` la acción se registra como de una persona.
- El próximo paso lo dice `oracle-factory estado ID`: seguilo en vez de adivinar.

## 2. El worktree (si el proyecto es Factory mismo)

- Un worktree por cambio: `git worktree add -b tarea/X ../factory-X main`, con su propio entorno (`uv venv .venv; uv pip install -e .`) y los `node_modules` copiados del proyecto principal.
- **Dentro del worktree usá `.venv/bin/oracle-factory`**, no el comando global: el global es la instalación editable del proyecto principal y corre el código de `main`, no el de tu rama. Regenerar `AGENTS.md` o `kb/` con el global deja lo generado viejo.
- No edites `.factory/`, `tareas/` ni `kb/` generado a mano.

## 3. Los pasos de un cambio

1. `oracle-factory nuevo --capacidad C --sufijo S "TÍTULO"` crea la propuesta y la spec; completalas (sin `TODO`). La spec la aprueba una persona (`aprobar-spec`); antes no implementes.
2. `oracle-factory importar ID` trae los requisitos de la spec aprobada.
3. Escribí las pruebas de cada escenario **antes** de implementar y comprobá que fallan (`docs/tests.md`). Un test que ya existía no se edita para que pase sin dejarlo dicho.
4. Implementá; corré mutaciones sobre lo que cambiaste: cada mutante que sobrevive es una prueba que falta o código equivalente que se puede simplificar.
5. Generá los catálogos y la evidencia con `tools/verificar_cambio.py ID --pruebas test_x --catalogos` y `--salida`. **Regenerá los catálogos antes de proponer medidas**; si no, Factory dice «sin cambios en la asociación».
6. `oracle-factory medir ID …` propone las medidas; las confirma una persona (`medir --confirmar`).
7. Pedí revisión (sección 5), `oracle-factory revision-preparar ID` y `oracle-factory revisar ID --decision aprobar|cambios --motivo M` propone la decisión; la registra una persona. Después `oracle-factory juzgar ID`, y una persona cierra con `cerrar`.
8. Integrar y empujar lo decide la persona (menú, comandos listos para pegar). Antes de integrar: `oracle-factory resumen --verificar`, `oracle-factory kb --verificar` y `oracle-factory agentes --verificar` en `main`, la suite completa en `main` y un escaneo de secretos del diff. La puerta local (`oracle-factory puerta`, `docs/puerta.md`) corre sola en el push.

Después de cada decisión de una persona («Listo»), comprobá en `oracle-factory estado ID` que quedó registrada como **persona** antes de seguir.

## 4. La evidencia: tres reglas

- Corré la **suite completa** antes de pedir una revisión. Una referencia de texto que cambió rompió una evidencia ya generada.
- El éxito de la evidencia se lee en la **última línea** de la salida (`éxito: True`), no en una línea suelta: las pruebas que corren la herramienta dentro del proceso pueden imprimir otras.
- Pedí las revisiones sólo si la evidencia dio éxito.

## 5. Las rondas de revisión

- Antes de pedir una revisión mirá la lista previa (`docs/lista-previa.md`) y arreglá la **clase** de problema, no sólo el caso que te señalaron.
- `oracle-factory estado ID` dice si el candidato califica para el **camino ligero**: hasta 150 líneas de producto, sin contar pruebas, y sin tocar las reglas de decisión (`docs/agentes.md`). Con el camino ligero alcanza un revisor y una ronda; si trae hallazgos medios o altos, el cambio sigue el camino completo. Es una orientación, no un gate.
- Con 4 rondas o más `estado` avisa de un bucle: parate, mirá la clase del problema y no pidas otra ronda sin arreglarla entera. Con más de 450 líneas de producto, considerá partir el cambio.
- Cada hallazgo se resuelve con una prueba y una mutación, y un hallazgo que no vas a arreglar se declara como límite en el documento y en el motivo de la decisión, sin esconderlo. Si arreglarlo toca lo que una persona aprobó (la spec, la propuesta), se lo decís: invalida su aprobación y hay que reaprobar.
- Si cambian los catálogos, hay que proponer de nuevo las medidas y una persona las confirma de nuevo.

## 6. Cuándo parar y preguntar

Parate y consultá a la persona si:

- hay una decisión de diseño que la spec no cubre;
- querés agregar algo que no se pidió;
- para que pase una prueba habría que cambiarla, saltearla o borrarla;
- el mismo intento falló dos veces;
- un paso supera las 50 líneas o toca más de tres archivos.

## 7. Lo que no se afirma sin haberlo medido

No escribas un número (pruebas, mutaciones, líneas, rondas) que no hayas leído del resultado o contado. Si no lo contaste, describí lo que hiciste sin la cifra. Si te equivocaste, decilo y corregilo en el motivo y en el documento.

Para consultar el proyecto sin suponer: `oracle-factory preguntar "PREGUNTA"`, `oracle-factory por-que ARCHIVO:LÍNEA`, `oracle-factory log ID`. Esta skill la muestra `oracle-factory skill` y la instala en el proyecto `oracle-factory skill --instalar`.
