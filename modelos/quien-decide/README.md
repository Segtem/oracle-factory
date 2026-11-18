# Quién decide, como leyes probadas

La regla de `AGENTS.md` («Las decisiones, según el modo de trabajo») escrita en [Bend 2](https://bend-lang.com/) como un modelo
chico con leyes que se prueban para todas las combinaciones y todas las secuencias de pasos. No es el código de Factory, que es
Python (`oracle_factory/modos.py`): es la regla, para poder probarla y compararla con el código.

- `quien.bend`: el modelo. `LAWS.bend`: siete leyes (en confirmación un agente nunca decide; aprobar el sensor es de una persona;
  el cierre no es del agente fuera de autónomo; ninguna secuencia de pasos en confirmación deja una decisión a nombre de un
  agente; el registro sí cuenta al agente en autónomo; en funcional el agente no decide lo funcional; una persona siempre decide).
  `PROOF.bend`: sus pruebas. `quien.mjs`: el modelo compilado a JavaScript, versionado.
- `bend PROOF.bend` dice ALL PROOFS CHECK. Si cambiás `quien.bend`, regenerá `quien.mjs` con `bend quien.bend -o quien.mjs`.
- `tests/test_leyes_bend.py` lo vigila: con `bend`, las pruebas valen, `quien.mjs` está al día y ocho mutantes del modelo hacen
  fallar alguna prueba (ninguna ley vacía); con `node`, el modelo compilado y `modos.via_agente` dicen lo mismo en las 24
  combinaciones de modo, decisión y tipo. Sin `bend` o sin `node`, esas pruebas se omiten y dicen qué falta.

Límites: no corre `--verdict`, el núcleo de Bend probado en Lean (pide Lean 4.34.0). El modelo toma un solo tipo de requisito por
decisión, y `via_agente` recibe una lista. Aprobar el sensor no está en `modos.DECISIONES` (es de `agentes.PERSONA`): esa ley no
tiene comparación con el código. Bend es joven y su verificador no tiene prueba propia; lo que vale acá son las leyes, los
mutantes y la comparación.
