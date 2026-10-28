# Capability: distribucion

## ADDED Requirements

### Requirement: la_version_a15_es_coherente_y_declara_su_estado
Tipo: funcional
El sistema DEBE declarar la misma versión 0.1.0a15 en los metadatos del paquete, en la CLI instalada y en los textos de instalación, notas y web de esa entrega, DEBE presentar la 0.1.0a14 como publicada y la 0.1.0a15 como preparada sin afirmar su publicación antes de comprobarla, y DEBE conservar las versiones y artefactos ya publicados.

#### Scenario: preparar la entrega nueva
- DADO la versión 0.1.0a14 publicada en PyPI y un checkout con mejoras posteriores aceptadas
- CUANDO se prepara la 0.1.0a15 y se construye e instala su wheel
- ENTONCES los metadatos y la CLI informan 0.1.0a15, los textos son coherentes, las notas de la 0.1.0a14 no la dicen en preparación y la 0.1.0a15 no se presenta como ya publicada

#### Scenario: una versión o un estado divergen
- DADO un candidato cuya web, README o instrucciones nombran otra versión como la de esta entrega, o afirman una publicación no verificada
- CUANDO se comprueba la entrega
- ENTONCES se detecta la divergencia y no se declara exitosa la preparación

### Requirement: el_wheel_a15_instalado_ofrece_lo_nuevo
Tipo: funcional
El sistema DEBE comprobar, con el wheel instalado en un entorno nuevo y desde fuera del checkout, la versión y el origen de importación, y que el paquete instalado ofrece las novedades de esta entrega: contar y listar las specs con `preguntar`, crear un cambio en inglés con `nuevo --idioma`, el bloqueo de `aprobar-spec` que nombra la línea pendiente, y el tablero con `yo`, `faltan` y `actividad`.

#### Scenario: las novedades en el wheel instalado
- DADO el wheel instalado en un entorno nuevo y un proyecto temporal
- CUANDO desde otra carpeta se pregunta cuántas specs hay, se crea un cambio con `--idioma en`, se intenta aprobar su spec sin completar y se pide el JSON del tablero
- ENTONCES se responde con el conteo de specs, la plantilla sale en inglés, el bloqueo nombra la línea del archivo y el JSON trae `yo`, `faltan` y `actividad`

#### Scenario: una instalación anterior o una importación accidental
- DADO un entorno que carga otro paquete o resuelve oracle_factory desde el checkout
- CUANDO se comprueba la entrega
- ENTONCES se detecta el origen o la versión incorrecta y no se acepta como prueba del wheel nuevo

### Requirement: la_entrega_a15_registra_sus_pruebas_y_sus_limites
Tipo: funcional
El sistema DEBE ejecutar la suite y los arneses de instalación aplicables y registrar resultados, versiones, hashes de fuentes y artefactos y límites en evidencia reproducible, detectar una corrida incompleta, una fuente modificada durante la medición o una comprobación fallida, y no crear una publicación ni decidir en nombre de Brian.

#### Scenario: preparación completa
- DADO fuentes quietas, medidas confirmadas y los artefactos candidatos
- CUANDO se ejecutan los verificadores y la suite
- ENTONCES la evidencia identifica lo instalado, sus hashes y los casos ejecutados, con sus resultados y límites

#### Scenario: una prueba falla o cambia una fuente
- DADO una comprobación que falla, se omite indebidamente o cambia el contenido durante la corrida
- CUANDO se produce el resultado de preparación
- ENTONCES la falla o falta de estabilidad queda registrada y no se informa una corrida completa exitosa
