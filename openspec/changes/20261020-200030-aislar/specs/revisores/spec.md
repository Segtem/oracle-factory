# Capability: revisores

## ADDED Requirements

### Requirement: el checkout de un revisor no toca el repositorio
Tipo: funcional
`pedir-revision` SHALL darle a cada revisor un checkout del candidato que sea un repositorio aparte, sin copiar objetos: lo que el revisor haga con git en ese checkout (cambiar su configuración, crear ramas, hacer commits) SHALL NOT cambiar la configuración, las ramas ni el HEAD del repositorio del proyecto ni de sus worktrees, y su informe SHALL validarse como siempre.

#### Scenario: un revisor que juega con git en su checkout
- GIVEN un cambio con un candidato y un revisor que en su checkout cambia user.name, crea una rama y hace un commit
- WHEN se pide la revisión con pedir-revision
- THEN el repositorio sigue con su user.name, sin esa rama y en el mismo HEAD, y el informe del revisor queda validado
