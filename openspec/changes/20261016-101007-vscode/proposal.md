# Extensión de VS Code: la vista de Factory, sus artefactos y el próximo paso

## Why

Para seguir un cambio de Factory hoy hay que correr `estado`, `donde` y `resumen` en la terminal y abrir a mano cada archivo que nombran. Brian pidió (2026-10-15) trabajar en VS Code con un complemento que ayude a previsualizar la información de Factory. Es la primera versión de la tarea `20261007-123220-vscode`, dentro del plan de revisión en el IDE (`20261005-112955-revision-ide`): la CLI ya da todo en JSON (`estado`, `donde` y `resumen --json`, `trazabilidad --json`).

## What changes

- **Una vista «Factory» en la barra lateral** con los cambios abiertos del proyecto; bajo cada uno, sus requisitos (medidas, decisión y veredicto), su revisión y su próximo paso. Sale de `resumen --json` y `estado ID --json`.
- **Abrir cada artefacto con un clic**: propuesta, spec, informes de revisión, evidencia y veredicto, desde `donde ID --json`; un artefacto ausente se ve marcado.
- **El próximo paso, en la terminal integrada**: un botón escribe el comando en una terminal del proyecto **sin ejecutarlo**; la persona lo lee y aprieta Enter, y la decisión se toma en el menú de siempre. La extensión muestra y guía, no decide.
- **La extensión vive en `editores/vscode/`** y se arma con `empaquetar.py` en un `.vsix`, sin `npm` ni `vsce`, como la de Oracle. Usa el `oracle-factory` del proyecto (`.venv/bin/oracle-factory` si existe) o el del `PATH`, o el que diga la configuración `factory.comando`.

## Out of scope

- Líneas sin respaldo en el margen y CodeLens «respalda: <requisito>» (de `trazabilidad --json`): segunda versión.
- SARIF (tarea `sarif`).
- Publicar en el Marketplace.

## Human decisions

- Brian eligió el alcance el 2026-10-16: vista, artefactos y próximo paso.
