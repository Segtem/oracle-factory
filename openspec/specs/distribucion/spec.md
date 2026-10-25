# Capability: distribucion

<!-- Generada por Oracle Factory al cerrar cada cambio: no se edita a mano. -->

## Requirements

### Requirement: la versión de entrega es coherente y declara su estado
Origen: 20261025-122552-ho0-entrega-a14 · distribucion_c477fe3fb3e543879.la_version_de_entrega_es_coherente_y_declara_su_estado
Tipo: funcional
La versión declarada en los metadatos del paquete, la CLI instalada y los textos de instalación,
notas y web que describen la entrega SHALL coincidir. La documentación SHALL distinguir un artefacto
en preparación de una publicación remota verificada, sin afirmar que un tag, release o paquete ya
existe antes de comprobarlo. La preparación SHALL conservar las versiones y artefactos publicados.

#### Scenario: preparar una entrega nueva
- GIVEN la versión 0.1.0a13 publicada y un checkout con mejoras posteriores aceptadas
- WHEN se prepara 0.1.0a14 y se construye e instala su wheel
- THEN los metadatos y la CLI informan 0.1.0a14, los textos son coherentes y la preparación no se presenta como publicación ya realizada

#### Scenario: una versión o un estado divergen
- GIVEN un candidato cuya instalación, web o instrucciones todavía nombran otra versión como la de esa entrega, o afirman una publicación no verificada
- WHEN se comprueba la entrega
- THEN se detecta la divergencia y no se declara exitosa la preparación

### Requirement: la distribución instalada ofrece las consultas del proyecto
Origen: 20261025-122552-ho0-entrega-a14 · distribucion_c477fe3fb3e543879.la_distribucion_instalada_ofrece_las_consultas_del_proyecto
Tipo: funcional
El wheel SHALL incluir las consultas de registro y elaboración de preguntar, con sus fuentes y límites.
Su comprobación SHALL ejecutarse en un entorno nuevo desde fuera del checkout, verificar versión y
origen de importación, y SHALL NOT resolver módulos desde el árbol fuente o desde otra instalación.
Los conteos SHALL corresponder al registro del proyecto fixture; sin modelo generativo configurado
SHALL conservar las consultas directas y la recuperación, sin elegir ni descargar un modelo generativo.
Un proveedor fixture explícito SHALL permitir comprobar elaboración, citas y herramientas de sólo lectura,
sin atribuir a esa simulación calidad de un modelo real.

#### Scenario: contar sin depender del checkout ni del modelo
- GIVEN un wheel instalado en un entorno nuevo y un proyecto temporal con dos cerrados archivados, un abierto y un abandonado
- WHEN desde otra carpeta se pregunta cuántos cambios cerrados hay, sin modelo generativo configurado
- THEN responde dos cerrados desde el registro con fuentes y la importación pertenece al entorno instalado, no al checkout

#### Scenario: elaborar con un proveedor fixture explícito
- GIVEN esa instalación y un servidor HTTP local fixture configurado como proveedor de generación
- WHEN se consulta una pregunta que combina documentación y conteo, y el proveedor intenta también una llamada de escritura
- THEN se conserva la respuesta con sus fuentes calculadas y documentales, la llamada de escritura se rechaza y la prueba se identifica como simulada

#### Scenario: una instalación anterior o una importación accidental
- GIVEN un entorno que carga otro paquete o resuelve oracle_factory desde el checkout
- WHEN se comprueba la entrega
- THEN se detecta el origen o la versión incorrecta y no se acepta como prueba del wheel nuevo

### Requirement: la entrega registra sus pruebas y sus límites
Origen: 20261025-122552-ho0-entrega-a14 · distribucion_c477fe3fb3e543879.la_entrega_registra_sus_pruebas_y_sus_limites
Tipo: funcional
La preparación SHALL ejecutar la suite y los arneses de instalación y guía aplicables, y registrar
resultados, versiones, configuración, hashes de fuentes y artefactos y límites del alcance en evidencia
reproducible. SHALL distinguir errores, omisiones y fixtures de observaciones reales, y SHALL detectar
una corrida incompleta, una fuente modificada durante la medición o una comprobación fallida. Generar
esa evidencia SHALL NOT crear una publicación ni decidir en nombre de Brian en un proyecto real.

#### Scenario: preparación completa
- GIVEN fuentes quietas, medidas confirmadas y los artefactos candidatos
- WHEN se ejecutan los verificadores y la suite
- THEN la evidencia identifica lo instalado, sus hashes y los casos ejecutados, con sus resultados y límites

#### Scenario: una prueba falla o cambia una fuente
- GIVEN una comprobación que falla, se omite indebidamente o cambia el contenido durante la corrida
- WHEN se produce el resultado de preparación
- THEN la falla o falta de estabilidad queda registrada y no se informa una corrida completa exitosa
