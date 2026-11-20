# Capability: buscaminas

## ADDED Requirements

### Requirement: tablero jugable
Tipo: funcional
El juego DEBE usar un tablero fijo de 5 por 5, contar las minas vecinas, destapar casillas, expandir regiones vacías, alternar banderas, perder al destapar una mina y ganar al destapar todas las casillas seguras. DEBE rechazar coordenadas inválidas y acciones después del fin sin corromper el estado.

#### Scenario: número y región vacía
- DADO un tablero nuevo
- CUANDO se destapa una casilla segura
- ENTONCES muestra su número de minas vecinas y expande las casillas conectadas si es cero

#### Scenario: bandera y error
- DADO un tablero nuevo
- CUANDO se marca una casilla o se intenta destapar una coordenada inválida
- ENTONCES la bandera bloquea el destape y el error conserva el estado

#### Scenario: victoria y derrota
- DADO un tablero nuevo
- CUANDO se destapa una mina o todas las casillas seguras
- ENTONCES la partida termina como perdida o ganada respectivamente
