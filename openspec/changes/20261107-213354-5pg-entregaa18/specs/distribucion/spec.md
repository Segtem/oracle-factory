# Capability: distribucion

## ADDED Requirements

### Requirement: la_version_a18_es_coherente_y_declara_su_estado
Tipo: funcional
El sistema DEBE declarar la misma versión 0.1.0a18 en los metadatos del paquete, en la CLI, en el uv.lock y en los textos de instalación, notas y web, DEBE presentar la 0.1.0a17 como publicada y la 0.1.0a18 como preparada sin afirmar que ya esté publicada, y NO DEBE dejar la versión anterior como actual en ningún texto.

#### Scenario: preparar la entrega nueva
- DADA la versión 0.1.0a17 publicada en PyPI y un checkout con mejoras posteriores aceptadas
- CUANDO se prepara la 0.1.0a18
- ENTONCES los metadatos, el uv.lock y la CLI informan 0.1.0a18, los textos son coherentes, las notas de la 0.1.0a17 la dan por publicada y la 0.1.0a18 no se presenta como ya publicada

#### Scenario: un texto que quedó con la versión vieja
- DADO un texto de instalación que todavía dice 0.1.0a17 como actual
- CUANDO se comprueba la coherencia
- ENTONCES la prueba falla nombrando el archivo

### Requirement: el_wheel_a18_instalado_ofrece_lo_nuevo
Tipo: funcional
El sistema DEBE construir el wheel y el sdist de la 0.1.0a18, instalar el wheel en un entorno nuevo y comprobar, desde fuera del checkout, la versión y el origen de la importación, que el wheel trae `oracle_factory/data/skill/SKILL.md` y que instalado funcionan `skill`, `skill --instalar`, `puerta`, `agentes`, `verificar` y `destinos` y la ayuda de los subcomandos nuevos.

#### Scenario: el wheel instalado en un entorno nuevo
- DADO el wheel recién construido y un entorno sin el checkout
- CUANDO se instala y se corren las comprobaciones desde otra carpeta
- ENTONCES la versión es 0.1.0a18, el módulo se importa del entorno y no del checkout, el wheel contiene la skill y cada comando nuevo responde como se espera

#### Scenario: el wheel sin la skill
- DADO un wheel que no trae el archivo de la skill
- CUANDO se juzga lo observado
- ENTONCES el juicio falla nombrando el archivo

#### Scenario: un comando instalado que falla
- DADO un entorno donde `skill --instalar` sale con error
- CUANDO se juzga lo observado
- ENTONCES el juicio falla nombrando el comando

### Requirement: la_entrega_a18_registra_sus_hashes_y_sus_limites
Tipo: funcional
El sistema DEBE dejar un registro de la entrega con los hashes del wheel y del sdist, las versiones de las herramientas y lo observado, y DEBE declarar sus límites: que no publica nada, que la construcción no es reproducible bit a bit y qué no se comprobó.

#### Scenario: el registro
- DADA una comprobación completa
- CUANDO se escribe el registro
- ENTONCES tiene los dos hashes, las versiones, las observaciones y los límites, y no declara la entrega como publicada

#### Scenario: un registro sin límites
- DADO un registro al que le faltan los límites
- CUANDO se valida
- ENTONCES la validación falla
