# Registros fuera del repo del producto: preparar la migración real de Factory

## Por qué

La etapa 6 dejó `oracle-factory migrar --almacen` y un ensayo sobre una copia de Factory. El ensayo migró 6637 archivos y `listar` dio lo mismo antes y después, pero también mostró lo que todavía da por hecho que los registros están en el repo del producto. Mientras eso siga así, migrar `~/Dev/factory` rompería pruebas, herramientas y la guía de agentes. Además, el producto quedaría con restos de Factory: líneas en `.gitignore` y `.gitattributes` que ya no sirven y hooks que corren sobre registros que ya no están. Arreglarlo sirve a Factory mismo y a cualquier equipo que migre un proyecto que ya usa Factory.

## Qué cambia

- **Pruebas y herramientas que leen los registros.** Con el producto conectado, buscan los registros en el almacén:
  - `test_portabilidad` p6 y `test_verificador_generico` vg3 leen `requisitos/` y `catalogos/` del almacén. Sin conexión, los siguen leyendo del repo.
  - `tools/verificar_cambio.py` lee la spec y el registro del cambio del almacén, y escribe ahí los catálogos. Las pruebas las sigue corriendo en el producto. `--raiz` sigue siendo la raíz del producto.
- **`migrar --almacen` limpia lo de Factory del producto:**
  - Saca de `.gitignore` y `.gitattributes` las líneas que escribe Factory, y nada más. Esos dos cambios quedan en el índice sin commitear, junto con la baja.
  - Las líneas de `.gitattributes` van al almacén en el mismo commit de la migración.
  - Saca los cuatro hooks que instaló Factory para el trailer `Cambio: ID` y para rehacer lo generado: `commit-msg`, `prepare-commit-msg`, `post-commit` y `post-merge`. Los reconoce por su marca. Un hook que no tiene la marca de Factory no se toca.
  - `--verificar` dice qué sacaría.
- **La puerta pre-push sigue en el producto conectado:**
  - Busca secretos en lo que se empuja del producto.
  - Corre sus verificaciones (agentes, kb, resumen, verificar) sobre los registros del almacén.
- **`agentes --en-el-repo`.** Con el producto conectado, mantiene al día el bloque generado en un `AGENTS.md` y un `CLAUDE.md` que el producto ya versiona, sin excluirlos. Es para un producto cuya guía de agentes es parte del producto, como Factory. Sin la opción, `agentes` sigue negándose a tocar una guía versionada. `agentes --verificar` compara la guía que haya, versionada o no.
- Al terminar, el ensayo de la etapa 6 se repite sobre Factory. Con los registros afuera no tiene que fallar ninguna prueba nueva. El informe queda en este cambio.

## Fuera de alcance

- Migrar `~/Dev/factory` de verdad: crear el repo del almacén, correr `migrar --almacen` y commitear y empujar la baja. Empujarla borra miles de archivos en origin y respaldo, y es una decisión aparte de Brian.
- Los `tools/verify_*.py` de cambios ya cerrados, que no se vuelven a correr.
- Volver atrás una migración.

## Decisiones humanas

Tomadas por Brian el 2026-11-12:
- Para `AGENTS.md`: una opción explícita para mantener el bloque generado en una guía que el producto ya versiona.
- Para los hooks: `migrar --almacen` saca los cuatro del trailer y de rehacer lo generado, y la puerta pre-push sigue en el producto, adaptada al almacén.
