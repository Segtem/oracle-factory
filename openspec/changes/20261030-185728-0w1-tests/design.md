# Diseño

Un solo lugar manda: `oracle_factory/plantillas.py`, que ya guarda las tareas en español y en inglés. Se agrega una línea a cada lista, entre «acordar medidas y evidencia» e «implementar», porque los tests salen de los escenarios aprobados y se escriben antes del código.

La guía para agentes se genera en `oracle_factory/agentes.py` y se regenera con `oracle-factory agentes`; una comprobación existente exige que `AGENTS.md` coincida. Se agrega una viñeta corta a la sección de trabajo, y `AGENTS.md` de este repositorio se regenera.

`docs/tests.md` es texto, sin código. La comprobación de documentos del proyecto (`tools/docs_al_dia.py`) trata `x.y.z` como versión de Factory: el documento no nombra otras versiones, y las fuentes se citan por su identificador de arXiv.

Los cambios ya creados no se tocan: la plantilla sólo afecta a los cambios nuevos. Las medidas comprueban los textos de las dos plantillas, la guarda de tests existentes en la guía, y que `docs/tests.md` exista y cite las fuentes. Una mutación por cada una (sacar la línea de la plantilla, sacar la viñeta, sacar el documento) debe detectarse.
