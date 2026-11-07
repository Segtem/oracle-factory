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

## En un hook pre-push

Para correrlo antes de empujar, agregá `oracle-factory verificar || exit 1` al hook `pre-push` de tu proyecto (el de la puerta local, `oracle-factory hooks`, no lo incluye). Como cualquier hook, se saltea con `git push --no-verify`: revisá antes lo que publicás.
