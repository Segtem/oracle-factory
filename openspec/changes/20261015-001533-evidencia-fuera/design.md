# Design

- En `estructura.buscar`, un archivo cuya ruta relativa es `.factory/cambios/<ID>/candidatos/<sha>/(evidencia|clue)/…` se saltea antes de mirar su tamaño, igual que hoy los JSON de `tareas/`: no cuenta como omitido por tamaño.
- El caso nuevo va en un archivo propio (`tests/test_evidencia_fuera.py`) para no alterar el conjunto de casos que cuenta el sensor de `estructura`.
