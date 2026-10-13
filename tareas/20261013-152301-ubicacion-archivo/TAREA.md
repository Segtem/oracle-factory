# Informe guiado: archivo y línea por separado en la ubicación de un hallazgo

- ESTADO: ABIERTA
- PRIORIDAD: 10
- ETIQUETAS: 

### Nota (2026-10-13 15:23:01 UTC)

Hallazgo F-01 (codex, vuelta 3, bajo) de 20261013-115616-vueltas-severidad, aceptado como riesgo por Brian: preparacion.archivo_de_ubicacion parte «archivo:línea» por el último «:número», así que un archivo POSIX como «src/parte:12» sin start_line queda registrado como «src/parte» y el riesgo aceptado no se reconoce en la vuelta siguiente (vuelve a preguntar: lado seguro). Arreglo: que el hallazgo del informe guiado lleve archivo y línea en campos propios (toca el esquema de revision.py).
