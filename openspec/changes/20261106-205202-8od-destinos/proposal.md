# Despliegue a varios destinos con prueba de que todo quedó funcionando

## Por qué

Factory acompaña un cambio hasta que se cierra y se integra, y ahí termina. Pero un producto real no es un repositorio: es un
VPS, una app, un ESP32, un contenedor, un sitio… varios **destinos** distintos, que hoy se despliegan a mano y cada uno a su
manera. Brian trabaja en una workstation en su casa y tiene exactamente ese caso: después de programar, lo que falta es llevar
el cambio a todos los destinos y **comprobar que todo quedó funcionando junto**, no sólo que cada pieza arrancó.

Hoy no queda registrado qué versión corre en cada destino, quién autorizó llevarla, ni si alguien probó que el conjunto anda;
y un destino que no se alcanzó (el ESP32 apagado) se confunde con uno que está bien. Factory tiene que poder hacerlo de forma
**general**: sin saber nada de VPS, de ESP32 ni de ninguna tecnología, sólo ejecutando los comandos que el proyecto declara.

## Qué cambia

- **Destinos declarados por el proyecto** en `.factory/destinos.json`: cada destino tiene un nombre, un tipo (una etiqueta
  libre: `vps`, `app`, `esp32`…), los comandos que lo construyen, despliegan, prueban y —si se puede— lo vuelven atrás, cómo leer
  qué versión corre, de qué otros destinos depende y qué nombres de secretos necesita (nunca el valor). Factory no trae
  conocimiento de ninguna tecnología; trae plantillas de ejemplo para copiar.
- **Un despliegue es un plan que una persona autoriza.** `oracle-factory desplegar` arma el plan (destinos en orden de
  dependencias, sobre un commit de la rama de despliegue con la puerta local en verde) y lo muestra; un agente puede proponerlo
  y simularlo, pero ejecutarlo lo autoriza una persona. Nada se despliega solo, ni por CI.
- **Se prueba cada destino y el conjunto.** Cada destino tiene su prueba de humo contra la versión recién desplegada, y el
  proyecto declara una prueba de conjunto («el ESP32 le habla a la API del VPS y la app lo muestra») que corre al final.
  «Todo quedó funcionando» sólo se dice si todo eso pasó contra la versión desplegada.
- **Un fallo deja un estado dicho.** Cada destino queda en uno de: sin desplegar, desplegado, probado, fallido, revertido,
  inalcanzable o desactualizado. Un destino que no se alcanzó **no es verde**. Si algo falla se corta (o se sigue, si el
  proyecto lo declara) y se vuelve atrás lo que se pueda, diciendo lo que no.
- **Cada ejecución deja evidencia**: por destino, la versión, los comandos, su salida (con los secretos tapados), los tiempos y
  el resultado. Oracle puede medir requisitos de despliegue sobre esa evidencia.
- **Para el tablero**: `oracle-factory destinos --json` expone la matriz destino × estado (versión desplegada, última prueba,
  si está desactualizado frente a la rama de despliegue). La vista en VS Code se construye sobre eso en el cambio siguiente.

## Fuera de alcance

- La vista «Destinos» del tablero de VS Code: es el cambio siguiente, sobre el contrato de `destinos --json` (el diseño está
  en `design.md`). Este cambio deja la CLI, el estado y la evidencia.
- Despliegue automático: ni por CI ni por un agente. El CD siempre pasa por una persona. Subir a PyPI sigue siendo de Brian
  (ver `release-flujo`).
- Gestor de secretos: Factory sólo lee los nombres declarados del entorno y nunca guarda un valor.
- Conocer tecnologías concretas (Docker, systemd, esptool, tiendas de apps): son comandos del proyecto.
- El CI remoto (`oracle-factory verificar`, tarea `ci-remoto`) y el análisis en cada commit (`shift-left`): son cambios aparte.

## Decisiones humanas

- ¿Aprobás el nombre «destino» para cada nodo de despliegue (VPS, app, ESP32…)?
- ¿Aceptás partir en dos cambios —este (motor, CLI, evidencia) y la vista del tablero—, o querés ambos en uno?
- ¿La rama de despliegue es siempre `main` o cada proyecto la declara? (Propuesto: la declara, `main` por defecto.)
- ¿Si un destino falla, el valor por defecto es cortar? (Propuesto: cortar y volver atrás lo que se pueda.)
