# Frenos de construcción: avisos de estado que mandan parar

## Por qué

Factory ya avisa en `estado` de varias señales de que un cambio se está yendo de las manos (muchas rondas, cambio grande, tests existentes editados), pero cada una es un aviso suelto y ninguna dice «acá se para». Para que un agente construya solo de principio a fin (el modo autopilot que pidió Brian, cambio 2 de 3) necesita una lista corta, determinista y legible por máquina de las condiciones que lo obligan a parar y devolverle la decisión a una persona. Hoy esa lista no existe.

## Qué cambia

`estado` (y `estado --json`, la clave nueva `frenos`) lista los frenos del cambio, calculados solo con datos que ya registra: dos juicios de Oracle rojos seguidos, un hallazgo de severidad alta en un informe del candidato vigente sin revisión aprobada vigente, un test existente editado, un cambio grande y un bucle de revisión. Cada freno lleva su identificador y su motivo, y aparece también como un aviso que empieza con «FRENO:». Es información: no cambia el próximo paso ni bloquea ningún comando.

## Fuera de alcance

El conductor `autopilot` que obedece los frenos (cambio 3). Verificar que un rojo sea real antes de corregir y comparar catálogos contra pruebas antes de pedir medidas (herramientas de `tools/`, quedan para después). Un registro nuevo del porqué: los frenos se calculan, no se guardan, y el porqué de lo que haga el conductor lo deja con `mensaje` en el cambio 3. La autonomía de integración, publicación y producción: Brian dejó las tres en `confirmacion`.

## Decisiones humanas

Decidido por Brian: integración, publicación y producción quedan en `confirmacion`. Pendiente de él: los umbrales de los frenos son los que ya usa `estado` (4 rondas, 450 líneas) más «dos juicios rojos seguidos»; si prefiere otros, se cambian en `oracle_factory/alarmas.py`.
