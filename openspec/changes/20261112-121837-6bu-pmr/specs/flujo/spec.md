# Capability: flujo

## ADDED Requirements

### Requirement: las_pruebas_y_herramientas_leen_los_registros_del_almacen
Tipo: funcional
El sistema DEBE, con el producto conectado a un almacén, hacer que `tools/verificar_cambio.py` lea la spec y el registro del cambio del almacén, escriba ahí los catálogos y corra las pruebas del producto, y que las pruebas de Factory que leen sus propios requisitos y catálogos (`test_portabilidad` p6 y `test_verificador_generico` vg3) los lean del almacén; sin conexión, todo DEBE seguir leyendo y escribiendo en el repo del producto como antes.

#### Scenario: verificar un cambio con el producto conectado
- DADO un producto conectado a un almacén con un cambio, su spec y sus pruebas en el producto
- CUANDO se corre `tools/verificar_cambio.py ID --pruebas test_x --catalogos --salida CARPETA`
- ENTONCES lee el contrato del almacén, corre las pruebas del producto, escribe los catálogos en el almacén y no escribe registros en el producto

#### Scenario: sin conexión
- DADO un producto con sus registros adentro
- CUANDO se corre lo mismo
- ENTONCES lee y escribe en el repo del producto, como antes

### Requirement: migrar_limpia_lo_de_factory_del_producto
Tipo: funcional
El sistema DEBE, con `migrar --almacen`, sacar del `.gitignore` y del `.gitattributes` del producto exactamente las líneas que escribe Factory (y la marca de su bloque), dejando esos cambios en el índice sin commitear junto con la baja; llevar las líneas de `.gitattributes` al almacén en el mismo commit de la migración; y sacar los hooks `commit-msg`, `prepare-commit-msg`, `post-commit` y `post-merge` que tengan la marca de Factory, sin tocar un hook que no la tenga ni el `pre-push`. `--verificar` DEBE decir qué sacaría, sin escribir nada.

#### Scenario: un producto con las líneas y los hooks de Factory
- DADO un producto con registros adentro, las líneas de Factory en `.gitignore` y `.gitattributes` junto a líneas propias, los cuatro hooks de Factory y la puerta pre-push
- CUANDO una persona corre `migrar --almacen`
- ENTONCES las líneas de Factory ya no están (las propias sí), el cambio está en el índice sin commitear, el `.gitattributes` del almacén tiene las líneas de Factory, los cuatro hooks no están y el `pre-push` sigue

#### Scenario: un hook ajeno
- DADO un `post-merge` que no instaló Factory
- CUANDO se migra
- ENTONCES ese hook queda igual

### Requirement: la_puerta_funciona_con_el_producto_conectado
Tipo: funcional
El sistema DEBE, con el producto conectado a un almacén, hacer que la puerta local de salida (`oracle-factory puerta`, la que corre el hook pre-push) busque secretos en lo que se empuja del repo del producto y corra sus verificaciones sobre los registros del almacén, y bloquee el push si encuentra un secreto o una verificación vencida.

#### Scenario: un secreto en el producto
- DADO un producto conectado con un commit sin empujar que agrega un secreto
- CUANDO corre la puerta
- ENTONCES la puerta lo encuentra y bloquea

#### Scenario: los registros al día
- DADO un producto conectado, sin secretos y con los registros del almacén al día
- CUANDO corre la puerta
- ENTONCES deja pasar

### Requirement: agentes_en_el_repo_mantiene_una_guia_versionada
Tipo: funcional
El sistema DEBE, con el producto conectado a un almacén, hacer que `agentes --en-el-repo` (sólo una persona) escriba el bloque generado en el `AGENTS.md` del producto y deje un `CLAUDE.md` que lo incluya, aunque el producto ya los versione, sin agregarlos a las exclusiones de Git y sin tocar lo que el archivo tiene fuera del bloque; sin `--en-el-repo`, `agentes` DEBE seguir negándose a tocar una guía versionada; y `agentes --verificar` DEBE decir si la guía del producto, versionada o no, está al día.

#### Scenario: Factory con su guía versionada
- DADO un producto conectado cuyo `AGENTS.md` versionado tiene texto propio y un bloque generado viejo
- CUANDO una persona corre `agentes --en-el-repo`
- ENTONCES el bloque queda al día, el texto propio igual, y el archivo no se excluye de Git

#### Scenario: sin la opción
- DADO el mismo producto
- CUANDO se corre `agentes`
- ENTONCES se niega sin escribir nada
