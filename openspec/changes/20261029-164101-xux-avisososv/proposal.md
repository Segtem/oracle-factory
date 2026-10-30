# Bajar avisos OSV de las dependencias de Factory y marcar qué candidatos quedan expuestos

## Por qué

Factory ya guarda el inventario de dependencias de cada candidato y sabe cruzarlo con un archivo de avisos OSV, pero ese archivo lo
tiene que traer la persona. Sin ese paso la auditoría se queda en el papel: nadie se entera de que una dependencia que un candidato
usó hoy tiene una vulnerabilidad publicada. Es la primera parte de tener, sin depender de un servicio comercial, el aviso continuo
que da Lightwell: saber cuándo una dependencia ya usada se vuelve vulnerable, para poder corregirla después.

## Qué cambia

Un modo nuevo de `oracle-factory procedencia` consulta la base pública OSV.dev, sólo cuando la persona lo autoriza con una bandera
explícita de red, por cada dependencia (nombre y versión) de los inventarios guardados. Guarda los avisos encontrados en un archivo
OSV local y enseguida corre la auditoría existente sobre él, de modo que el resultado dice qué cambios y candidatos usaron una
versión afectada. Sin la bandera no se abre ninguna conexión. Un fallo de red o una respuesta inválida termina con error y no guarda
nada: nunca se lee como «sin afectados».

## Fuera de alcance

- Corregir o actualizar dependencias (es la etapa siguiente: la remediación).
- Ejecutarlo solo, en un horario o en CI.
- Proyectos que no sean Factory; otros ecosistemas distintos de PyPI.
- Parchear o publicar versiones propias.

## Decisiones humanas

- Que la red sea opt-in por bandera, y que sólo salgan hacia OSV.dev el nombre, la versión y el ecosistema de cada dependencia,
  nunca rutas, identificadores de cambio ni contenido del repositorio.
- Dónde se guarda el archivo de avisos: en `.factory/local/`, que no viaja con el repositorio.
