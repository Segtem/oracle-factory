# Capability: distribucion

## ADDED Requirements

### Requirement: los_textos_declaran_publicada_la_version_a17
Tipo: funcional
El sistema DEBE declarar publicada la 0.1.0a17 en las notas de release (con su línea «Publicada», su tag y su release), en el README, en la guía de colaboración y en la web, sin llamarla candidata ni en preparación, y DEBE conservar las notas de las versiones anteriores en orden, la más nueva arriba.

#### Scenario: los textos de una versión publicada
- DADA la 0.1.0a17 publicada en PyPI, con tag y release en GitHub
- CUANDO se leen las notas, el README, la guía de colaboración y las páginas de la web
- ENTONCES las notas la dan por publicada con su línea «Publicada», el README y la guía dicen que está publicada, ningún texto la llama candidata o en preparación y las notas anteriores siguen en su orden

### Requirement: se_detecta_lo_que_siga_llamando_candidata_a_la_version_a17
Tipo: funcional
El sistema DEBE detectar y nombrar el archivo que siga presentando como candidata o en preparación a la 0.1.0a17 una vez que las notas la declaran publicada, y NO DEBE marcar como divergencia el candidato de una revisión ni los estados de preparación de un cambio.

#### Scenario: un texto que quedó con la a17 como candidata
- DADO un README o una guía que todavía dice que la 0.1.0a17 está en preparación o es candidata
- CUANDO se comprueba la coherencia con las notas que la declaran publicada
- ENTONCES la comprobación falla nombrando el archivo

#### Scenario: palabras parecidas que no son una divergencia
- DADO un texto que habla del candidato de una revisión o del estado de preparación de un cambio
- CUANDO se comprueba la coherencia
- ENTONCES no hay divergencias
