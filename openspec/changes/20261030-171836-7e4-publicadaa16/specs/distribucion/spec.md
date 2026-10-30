# Capability: distribucion

## ADDED Requirements

### Requirement: los_textos_declaran_publicada_la_version_a16_publicada
Tipo: funcional
El sistema DEBE presentar como publicada la versión 0.1.0a16, con su publicación en PyPI, su tag y su release, en las notas de versión, el README, la documentación, la guía y la web, y NO DEBE describirla como candidata, en preparación ni como instalable a futuro.

#### Scenario: una versión ya publicada
- DADO la versión 0.1.0a16 publicada en PyPI, con su tag y su release de GitHub
- CUANDO se leen las notas, el README, la documentación, la guía y la web
- ENTONCES las notas la declaran publicada con su tag y su release, y ningún otro texto la llama candidata ni en preparación ni dice que sus instrucciones de instalación se podrán usar cuando se publique

#### Scenario: la historia anterior se conserva
- DADO las notas de las versiones 0.1.0a15, 0.1.0a14 y anteriores
- CUANDO se declara publicada la 0.1.0a16
- ENTONCES esas secciones no cambian

### Requirement: un_texto_en_preparacion_de_la_version_a16_publicada_se_detecta
Tipo: funcional
El sistema DEBE detectar, cuando las notas declaran publicada la versión actual, cualquier texto del README, la documentación o la web que la describa como candidata, en preparación o instalable cuando se publique.

#### Scenario: una divergencia al revés
- DADO unas notas que declaran publicada la versión actual y un README que aún la llama candidata en preparación
- CUANDO se comprueba la documentación
- ENTONCES se señala ese texto como divergente y no se declara al día

#### Scenario: una versión todavía en preparación
- DADO unas notas que declaran la versión actual en preparación
- CUANDO un texto la llama candidata en preparación
- ENTONCES no es una divergencia
