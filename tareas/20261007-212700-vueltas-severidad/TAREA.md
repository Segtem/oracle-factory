# Vueltas de revisión proporcionales: cortar por severidad y que los bajos los decida la persona

- ESTADO: ABIERTA
- PRIORIDAD: 17
- ETIQUETAS: revision, autoproduccion


## Objetivo

Hoy la regla para las vueltas de revisión es «hasta que no queden hallazgos». Proponer un criterio de corte proporcional: seguir mientras haya hallazgos medios o altos; los bajos se muestran y los decide la persona en la revisión guiada (aceptar, corregir o descartar con motivo), sin otra vuelta automática.

Origen: el video «Yo leo el código, ¿y tú?» (BettaTech, 2026-10-07) — «las cosas que decidimos no hacer también son una decisión de ingeniería» — y lo medido en el cambio 20261007-192608-revisores: 10 vueltas de codex, donde las últimas trajeron variantes bajas del mismo defecto (marcadores del comando), mientras que otras vueltas encontraron defectos reales de severidad media (el nombre del revisor usado en rutas, el candidato equivocado). El costo de cada vuelta es un candidato nuevo y unos 10 minutos.

## Notas

- Lo que corta es la persona, no el revisor: Factory puede mostrar «quedan N hallazgos bajos» y sugerir pasar a la revisión guiada.
- Puede ser una opción del revisor en la configuración (`corte: "media"`) o del proyecto.
- Medir: cuántas vueltas y cuántos hallazgos por severidad tuvo cada cambio (sale de los informes en `revision/`).
