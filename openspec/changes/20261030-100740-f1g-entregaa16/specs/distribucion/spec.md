# Capability: distribucion

## ADDED Requirements

### Requirement: la_version_a16_es_coherente_y_declara_su_estado
Tipo: funcional
El sistema DEBE declarar la misma versión 0.1.0a16 en los metadatos del paquete, en la CLI instalada, en el uv.lock y en los textos de instalación, notas y web de esa entrega, DEBE presentar la 0.1.0a15 como publicada y la 0.1.0a16 como preparada sin afirmar su publicación antes de comprobarla, y DEBE conservar las versiones y artefactos ya publicados.

#### Scenario: preparar la entrega nueva
- DADO la versión 0.1.0a15 publicada en PyPI y un checkout con mejoras posteriores aceptadas
- CUANDO se prepara la 0.1.0a16 y se construye e instala su wheel
- ENTONCES los metadatos, el uv.lock y la CLI informan 0.1.0a16, los textos son coherentes, las notas de la 0.1.0a15 no la dicen en preparación y la 0.1.0a16 no se presenta como ya publicada

#### Scenario: una versión o un estado divergen
- DADO un candidato cuya web, README, uv.lock o instrucciones nombran otra versión como la de esta entrega, o afirman una publicación no verificada
- CUANDO se comprueba la entrega
- ENTONCES se detecta la divergencia y no se declara exitosa la preparación

### Requirement: el_wheel_a16_instalado_ofrece_lo_nuevo
Tipo: funcional
El sistema DEBE comprobar, con el wheel instalado en un entorno nuevo y desde fuera del checkout, la versión y el origen de importación, y que el paquete instalado ofrece las novedades de esta entrega: el inventario de procedencia de un proyecto con uv.lock, la búsqueda de una dependencia entre los inventarios guardados, la auditoría contra un archivo de avisos OSV, y la consulta a OSV que se niega sin la bandera de red y, con ella, trae y audita los avisos de un servidor local.

#### Scenario: las novedades en el wheel instalado
- DADO el wheel instalado en un entorno nuevo, un proyecto temporal con uv.lock y un servidor OSV local de mentira
- CUANDO desde otra carpeta se pide la procedencia con su cambio, se busca una dependencia, se audita con un archivo de avisos y se consulta OSV con y sin la bandera de red
- ENTONCES el inventario CycloneDX se guarda en el candidato, la búsqueda y la auditoría nombran el cambio, la consulta sin bandera falla sin conectarse y con ella guarda los avisos y nombra al candidato expuesto

#### Scenario: una instalación anterior o una importación accidental
- DADO un entorno que carga otro paquete o resuelve oracle_factory desde el checkout
- CUANDO se comprueba la entrega
- ENTONCES se detecta el origen o la versión incorrecta y no se acepta como prueba del wheel nuevo

### Requirement: la_entrega_a16_registra_sus_pruebas_y_sus_limites
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
