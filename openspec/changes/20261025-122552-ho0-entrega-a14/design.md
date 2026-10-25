# Design

## Base y unidad de entrega

Partir de main 5a7013a, con docs y preguntar cerrados. La capacidad distribucion verifica la entrega
de lo ya implementado: las consultas de fuentes, generación y registro siguen en sus módulos actuales.
La configuración local de Brian en .factory/config.json no es un valor predeterminado del paquete.

## Instalación independiente

Construir los artefactos mediante el backend declarado en pyproject.toml. Registrar sus hashes e
instalar el wheel por ruta explícita en un entorno nuevo dentro del área local de pruebas. Ejecutar
sus comandos desde un directorio temporal fuera del repositorio, limpiando PYTHONPATH y cualquier
ruta que pueda resolver oracle_factory desde el checkout. Comprobar el origen del módulo, la versión
instalada y el ejecutable invocado; probar sólo __file__ desde la raíz del checkout no es suficiente.

Un proyecto fixture tendrá estados conocidos para contar abiertos, cerrados archivados y abandonados.
Un servidor HTTP local fixture permitirá comprobar la elaboración, las citas y el rechazo de una
consulta de escritura; no se usará ni descargará un modelo implícito ni se afirmará calidad real con
esa simulación. Los flujos con decisiones se ejecutan únicamente en proyectos temporales con una
identidad fixture explícita, sin registrar decisiones en este proyecto real ni modificar configuración
Git de Brian. Reutilizar tools/verify_installed.py y tools/verify_guide.py donde corresponda.

## Versión y publicación

Unificar metadatos, CLI, README, notas y web con el candidato 0.1.0a14. La redacción distinguirá el
artefacto preparado de un tag, release o paquete remoto cuya existencia todavía no fue verificada.
Construir y probar es anterior a cualquier publicación. Se conservará la 0.1.0a13 publicada y sus
artefactos: no se reescribe su tag ni su historia.

## Evidencia y límites

Proponer un sensor de distribución con CONTRACTS, PREFIX y LIMITES según el patrón del repositorio,
con medidas por requisito y de corrida completa. Generar evidencia sólo después de su confirmación,
con fuentes quietas. Registrar hashes de fuentes y artefactos, dependencias, intérprete, orígenes de
importación, comandos y resultados. Las verificaciones iniciales cubren Linux y el Python empleado;
no equivalen a una matriz de todos los sistemas ni a una nueva medición universal del modelo.
