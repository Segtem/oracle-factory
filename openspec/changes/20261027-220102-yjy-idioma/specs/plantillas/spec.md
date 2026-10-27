# Capability: plantillas

## ADDED Requirements

### Requirement: idioma_de_la_plantilla
Tipo: funcional
El sistema DEBE crear la propuesta, la spec, el diseño y las tareas de un cambio nuevo enteros en el idioma elegido, español o inglés, sin mezclarlos, y dejar en su forma original lo que el formato exige.

#### Scenario: un proyecto sin idioma declarado
- DADO un proyecto sin `idioma` en `.factory/config.json`
- CUANDO se crea un cambio con `oracle-factory nuevo`
- ENTONCES la propuesta, la spec, el diseño y las tareas salen en español

#### Scenario: el proyecto declara inglés
- DADO un proyecto con `"idioma": "en"`
- CUANDO se crea un cambio con `oracle-factory nuevo`
- ENTONCES los cuatro archivos salen en inglés, sin frases en español salvo la marca TODO y `Tipo:`

#### Scenario: el cambio elige otro idioma
- DADO un proyecto en español
- CUANDO se crea un cambio con `nuevo --idioma en`
- ENTONCES ese cambio sale en inglés y el proyecto no cambia

#### Scenario: lo que exige el formato no se traduce
- DADO un cambio creado en cualquiera de los dos idiomas
- CUANDO se lee su spec
- ENTONCES conserva `# Capability:`, `## ADDED Requirements`, `### Requirement:`, `#### Scenario:` y `Tipo:`

### Requirement: idioma_no_admitido
Tipo: funcional
El sistema DEBE rechazar un idioma que no sea `es` o `en`, tanto en la configuración como en `--idioma`, diciendo cuáles hay y sin crear nada.

#### Scenario: un idioma desconocido en la configuración
- DADO un proyecto con `"idioma": "fr"`
- CUANDO se corre cualquier comando que lee la configuración
- ENTONCES falla diciendo que los idiomas son `es` y `en`

#### Scenario: un idioma desconocido en la línea de comandos
- DADO un proyecto válido
- CUANDO se corre `nuevo --idioma fr`
- ENTONCES se rechaza sin crear tarea ni archivos

### Requirement: la_plantilla_en_cualquier_idioma_se_aprueba_e_importa
Tipo: funcional
El sistema DEBE aceptar y poder importar una spec completada a partir de la plantilla de cualquiera de los dos idiomas, y seguir negando la aprobación mientras queden marcas TODO.

#### Scenario: una spec en español completa
- DADO un cambio en español cuyas marcas TODO se completaron
- CUANDO una persona aprueba la spec y un agente importa los requisitos
- ENTONCES se importa el requisito con el texto en español

#### Scenario: una plantilla sin completar
- DADO un cambio recién creado, en cualquiera de los dos idiomas
- CUANDO se intenta aprobar la spec
- ENTONCES se rechaza porque quedan marcas TODO
