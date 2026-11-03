# Capability: practicas

## ADDED Requirements

### Requirement: la_skill_describe_el_flujo_con_los_comandos_y_umbrales_del_codigo
Tipo: funcional
El sistema DEBE traer una skill de agente con el procedimiento para trabajar un cambio de punta a punta, con el encabezado que leen las herramientas de agentes, y DEBE fallar una prueba si la skill nombra un comando de Factory que no existe, cita un umbral que no es el del código o enlaza un documento que no existe.

#### Scenario: la skill coincide con el código
- DADA la skill y el código de Factory
- CUANDO se comprueba
- ENTONCES cada comando `oracle-factory VERBO` que nombra es un subcomando de la CLI, los umbrales de rondas, de líneas y del camino ligero son los de las constantes del código y cada documento enlazado existe

#### Scenario: la skill nombra un comando que no existe
- DADA una skill que nombra `oracle-factory inventado`
- CUANDO se comprueba
- ENTONCES la prueba falla nombrando el comando

#### Scenario: la skill cita un umbral viejo
- DADA una skill que dice 500 líneas donde el código dice 450
- CUANDO se comprueba
- ENTONCES la prueba falla nombrando el umbral

#### Scenario: el encabezado
- DADA la skill
- CUANDO se lee su encabezado
- ENTONCES tiene `name: oracle-factory` y una `description` no vacía

### Requirement: el_comando_skill_la_muestra_y_la_instala_sin_pisar_nada_ajeno
Tipo: funcional
El sistema DEBE mostrar la skill con `oracle-factory skill` y escribirla con `oracle-factory skill --instalar` en `.claude/skills/oracle-factory/SKILL.md` del proyecto, sin pisar un archivo distinto salvo con `--forzar`, y NO DEBE escribir fuera del proyecto ni modificar la configuración de ninguna herramienta.

#### Scenario: mostrarla
- DADO un proyecto
- CUANDO se corre `oracle-factory skill`
- ENTONCES se imprime el texto de la skill y no se escribe nada

#### Scenario: instalarla
- DADO un proyecto sin la skill instalada
- CUANDO se corre `oracle-factory skill --instalar`
- ENTONCES el archivo existe en `.claude/skills/oracle-factory/SKILL.md` con el mismo texto y la salida dice dónde

#### Scenario: instalarla otra vez
- DADA la skill ya instalada y sin cambios
- CUANDO se corre `--instalar` de nuevo
- ENTONCES no cambia nada y lo dice

#### Scenario: un archivo distinto
- DADO un archivo propio en esa ruta
- CUANDO se corre `--instalar`
- ENTONCES no lo pisa, sale con error y dice que `--forzar` lo reemplaza; con `--forzar` lo reemplaza

#### Scenario: nada fuera del proyecto
- DADO un directorio personal con su propia configuración de herramientas
- CUANDO se instala la skill
- ENTONCES esa configuración queda como estaba

### Requirement: la_guia_para_agentes_nombra_la_skill
Tipo: funcional
El sistema DEBE nombrar el comando `oracle-factory skill` en la guía para agentes que genera, y DEBE detectar con `agentes --verificar` que la guía quedó vieja si ese texto falta.

#### Scenario: la guía lo dice
- DADO la guía generada
- CUANDO se lee
- ENTONCES nombra `oracle-factory skill` y `oracle-factory skill --instalar`

#### Scenario: la guía quedó vieja
- DADA una guía sin esa mención
- CUANDO se verifica
- ENTONCES `agentes --verificar` falla
