# El conocimiento del proyecto: un vault que se genera solo, notas humanas que vencen solas y ¿por qué existe esta línea?

## Why

Los vaults de conocimiento se pudren porque dependen de que alguien se acuerde de mantenerlos (pasó en Jam y en Oracle).
Factory ya registra lo que hace falta saber de cada cambio —propuesta, requisitos, medidas, decisiones con quién y
cuándo, hallazgos, riesgos aceptados, commits, mensajes—, así que el vault puede derivarse de ese registro y comprobarse
como se comprueban las specs. Y con los commits unidos a su cambio (B) se puede responder la pregunta del postmortem
del ajedrez: ¿qué decisión creó esta línea? Brian lo eligió el 2026-10-19: vault en `kb/` versionado, primero el vault y
C, después el RAG.

## What changes

- `oracle-factory kb` escribe `kb/` desde el registro: una nota por cambio, una por requisito y un índice, enlazadas
  con wikilinks de Obsidian. Nadie la edita a mano: `kb --verificar` falla si no coincide con el registro, y se
  regenera sola en cada decisión que cambia el estado de un cambio, como `resumen.md`.
- Notas humanas en `kb/notas/` (conceptos, guías, decisiones de arquitectura) con `fuentes:` en su frontmatter
  (archivos, requisitos o cambios que describen). Factory guarda la huella de esas fuentes: si una cambia, la nota queda
  «por revisar», `kb --verificar` lo dice y `estado` lo avisa en el cambio que la tocó. Una persona la marca revisada
  con `oracle-factory kb revisada NOTA` (después de editarla o de comprobar que sigue valiendo).
- `oracle-factory por-que ARCHIVO:LÍNEA` (y `--json`): del blame de esa línea al commit, del commit a su cambio
  (trailer o deducido), y de ahí sus requisitos con su veredicto, las decisiones con quién, cuándo y por qué, los
  riesgos aceptados y hallazgos sobre ese archivo, y las notas humanas que lo tienen como fuente. En VS Code, el comando
  «Factory: ¿Por qué existe esta línea?» lo muestra para la línea del cursor.

## Out of scope

- El RAG (búsqueda híbrida con embeddings y preguntas de oro): es el cambio siguiente, sobre este vault.
- Reescribir los vaults de Jam y Oracle.

## Human decisions

- Brian eligió el 2026-10-19: `kb/` en el repo, versionado; vault + C antes que el RAG.
- Marcar una nota humana como revisada es una decisión de una persona (como confirmar medidas).
