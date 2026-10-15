# CLI: plantilla de cambio, medir que avisa qué reemplaza y --listar separado

## Why

Tres fricciones del piloto con agentes (fricción 7, tarea `20261005-105254-cli-piloto`) siguen abiertas:

- La plantilla genérica de `nuevo` arma una spec sin `## ADDED Requirements` y una propuesta que pide «una decisión de Brian/equipo». Se vio en cada cambio de esta semana: hubo que reescribir la spec entera. Sólo el ejemplo `notas` se había corregido.
- `medir` reemplaza las medidas de un requisito sin decir cuáles tenía, y una medida que deja de usarse no se nombra: queda en el catálogo sin requisito.
- `medir --listar` muestra todas las medidas efectivas juntas. En un proyecto nuevo son 41, todas del catálogo base de Oracle (meta, proceso, simulación), y las del proyecto quedan mezcladas con ellas.

## What changes

- **La plantilla de `nuevo`** trae `## ADDED Requirements`, `Tipo: funcional` en el requisito, y una propuesta que habla de «una persona del equipo».
- **`medir` dice qué reemplaza**: si el requisito ya tenía otras medidas, las nombra junto a las nuevas, y señala las que quedan sin ningún requisito del proyecto que las use.
- **`medir --listar` separa** las medidas del proyecto, con su detalle, de las del catálogo base de Oracle, que van al final y en una línea cada una.

## Out of scope

- Que el ejemplo `notas` cumpla `meta.ningun_umbral_de_igualdad` y `meta.toda_medida_filtra_o_agrupa`: cambia el significado de sus medidas y de las pruebas que lo usan; queda como tarea aparte.

## Human decisions

- Ninguna nueva: las fricciones son del piloto y la tarea ya las lista.
