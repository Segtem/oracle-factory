# Verificar los cambios en CI

`oracle-factory verificar` comprueba, de sólo lectura, que los cambios del proyecto estén consistentes. Sirve para un CI y para un clon en otra máquina: no pide terminal, no necesita `--agente`, no usa la red y no escribe nada. Informa; confirmar, cerrar o corregir sigue siendo de una persona.

```bash
oracle-factory verificar          # una línea por problema; sale con 0 o con 1
oracle-factory verificar --json   # el mismo resultado en un objeto con esquema oracle-factory.verificar/1
```

## Qué comprueba

- **Un cambio abierto**: que la spec aprobada, las medidas, la revisión y el juicio de Oracle sigan siendo los del producto actual, y que las huellas de los informes y de los hechos coincidan.
- **Un cambio cerrado**: que sus informes y decisiones conserven su huella y que el cierre lo haya decidido una persona (en modo autónomo vale el de un agente). No lo compara con el producto actual: integrarlo lo deja distinto por diseño.
- **Lo que falta por hacer no es una inconsistencia**: una spec sin aprobar o una revisión pendiente no hacen fallar a `verificar`.
- **Hechos ausentes**: los hechos de la evidencia que no están en este clon (una carpeta ignorada, un clon limpio) se avisan sin fallar; si están y no coinciden con su huella, falla.

## El código de salida

0 si todo está consistente; 1 si algún cambio no lo está (con el cambio y lo que falta). Los avisos no cambian el código.

## En GitHub Actions

La plantilla `docs/plantillas/verificar.yml` corre `oracle-factory verificar` en cada push y pull request, con permisos de sólo lectura y sin secretos. Copiala a `.github/workflows/verificar.yml`.

**La política: falla en `main`, avisa en las demás.** Si `verificar` encuentra un cambio inconsistente, el workflow falla cuando corre en `main` y, en cualquier otra rama o pull request, avisa con una anotación `::warning::` y sale con 0: una revisión desactualizada es normal en una rama de trabajo mientras se sigue editando. El detalle de qué cambio falla queda en el registro del job (`oracle-factory verificar` lo imprime). Para que un fallo en `main` impida integrar, marcá el check como obligatorio en las reglas de ramas de GitHub (eso es configuración del repositorio, no del workflow).

Este repositorio usa el mismo workflow en `.github/workflows/verificar.yml`, con dos diferencias: instala Factory desde el checkout (`uv tool install .`) en vez de PyPI, para probar el código que se está integrando, y suma un trabajo `pruebas` que corre la suite (`.venv/bin/python -m unittest discover -s tests`). La suite pasa en un clon limpio, sin la configuración de quien la corre: las pruebas que leen los registros del propio repositorio se omiten diciendo por qué si no están a mano.

## Con los registros en un almacén aparte

Un producto marcado con `.oracle-factory-almacen` (ver `docs/estructura.md`) no tiene sus registros en el checkout del CI: ahí `verificar` se negaría. Por eso el paso de verificación de la plantilla, si ve la marca, avisa con `::notice::` que los registros se verifican en el CI del almacén y sale con 0.

Los registros se verifican en el repo del almacén, con la plantilla `docs/plantillas/verificar-almacen.yml`: copiala a `.github/workflows/verificar.yml` del almacén y poné en `PRODUCTO` el repo del producto (`dueño/nombre`). Clona el almacén y el producto, este con toda su historia para ver los candidatos, instala Factory desde el producto y corre `oracle-factory --proyecto producto --registros almacen verificar`, con la misma política: falla en `main` y avisa en las demás ramas. Sólo lee y no usa secretos mientras el producto sea público; si es privado, el almacén necesita una clave de lectura del producto (una deploy key guardada como secreto, pasada a `actions/checkout` con `ssh-key`). Los minutos de Actions de un repo privado cuentan contra el cupo de la cuenta. El almacén de Factory usa esta plantilla con `Segtem/oracle-factory`.

## En un hook pre-push

Para correrlo antes de empujar, agregá `oracle-factory verificar || exit 1` al hook `pre-push` de tu proyecto: la puerta local de `oracle-factory hooks` ya corre `verificar`, pero sólo avisa; con esta línea, un cambio inconsistente bloquea el push. Como cualquier hook, se saltea con `git push --no-verify`: revisá antes lo que publicás.
