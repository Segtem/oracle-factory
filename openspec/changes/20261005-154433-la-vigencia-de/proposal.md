# La vigencia de una revisión depende del contenido del producto

## Why

Factory vincula la revisión y el veredicto de Oracle al **commit exacto** (`HEAD`) y a una huella de los archivos del producto. Alcanza con que cambie cualquiera de las dos para que quede «desactualizada respecto del producto». El efecto práctico, observado tres veces el 2026-10-05 (hallazgo G-02 de la revisión guiada):

- Registrar una revisión y commitear su propio registro cambia el `HEAD` y la deja vieja, aunque ningún archivo del producto haya cambiado.
- Para cerrar los modos hubo que preparar una revisión nueva, con el mismo contenido y las mismas 20 decisiones, y pedirle a Brian que la registrara otra vez. Colaboración y revisión guiada están en la misma situación.
- El informe guiado exige `informe.contexto == contexto` actual, **incluido el HEAD**: no se puede commitear un informe completo antes de registrarlo, ni mergear con `main` entre preparar y registrar.

El producto no cambió; lo que cambió es el historial. Obligar a una persona a renovar una revisión por eso la lleva a firmar sin releer, que es lo contrario de lo que busca el flujo.

La huella de archivos ya existe y ya excluye lo que no es producto (`tareas/` y los registros de Factory). Es lo que realmente dice si lo revisado sigue siendo lo que hay.

## What changes

1. **Vigencia por contenido.** Una revisión o un veredicto siguen vigentes mientras la huella de archivos del producto coincida con la que tenían al registrarse, aunque el `HEAD` sea otro. Si cambia un archivo del producto, quedan desactualizados, como hoy.
2. **El commit se conserva como dato, no como condición.** Cada registro sigue guardando el `HEAD` observado. `estado` y el cierre lo muestran, y avisan cuando el `HEAD` actual es otro con el producto idéntico: «revisado en `c0e7c3c`; producto idéntico en `608c0fa`».
3. **El informe guiado se vincula al contenido.** `revision` acepta un informe preparado en otro `HEAD` si la huella coincide, y lo rechaza si la huella difiere.
4. **Sin migración.** Los registros existentes ya traen la huella: pasan a valer con la regla nueva si el producto no cambió.

## Out of scope

- Cambiar qué archivos cuentan como producto: se mantienen las exclusiones actuales.
- Firmar commits o vincular la revisión a objetos de Git.
- Detectar que dos commits distintos con el mismo contenido son «la misma versión» a efectos de auditoría: el historial sigue registrado, sólo deja de ser condición.
- Colaboración, revisión guiada y los demás cambios abiertos: éste sólo quita un obstáculo para cerrarlos.

## Human decisions

Pendiente de aceptación de proposal.md y spec.md. Preguntas abiertas para Brian:

1. **Mostrar el aviso de HEAD distinto:** ¿sólo en `estado` y en el cierre (lo propuesto), o también como advertencia al juzgar y revisar?
2. **¿El veredicto de Oracle (`juzgar`) sigue la misma regla?** Se propone que sí: usa los mismos hechos y el mismo producto. Los hechos, en cambio, no se vinculan a un commit hoy; no cambia nada ahí.
3. **Antes de aplicarlo:** este cambio modifica el producto, así que **vuelve a dejar desactualizadas las revisiones** de colaboración y de revisión guiada (que ya lo están por otros motivos). Se propone cerrarlas cuando se cubra lo que cada una declara, con la regla nueva ya vigente. ¿De acuerdo?

La persona conserva alcance, aprobación de spec, pertinencia de medidas, resolución de hallazgos y cierre. Preparar esto no acepta el cambio.
