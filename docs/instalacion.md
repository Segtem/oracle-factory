# Instalar Oracle Factory 0.1.0a20 y su extensión de VS Code

Necesitás [Git](https://git-scm.com/install/) y [uv](https://docs.astral.sh/uv/getting-started/installation/). `uv` puede instalar Python 3.13 por vos; Factory requiere Python 3.11 o posterior. La CLI funciona sola desde la terminal. El complemento de VS Code es opcional y muestra el tablero del proyecto.

## Elegí los comandos que querés en tu terminal

**Sólo Factory.** Es el camino más simple si ya tenés `oracle`, `tasks` u `oracle-clue` instalados. Factory conserva Oracle 0.39.0, Oracle Task 0.2.0 y Oracle Clue 0.1.0a2 dentro del entorno aislado que crea `uv`, pero no expone sus comandos en tu `PATH`:

```bash
uv python install 3.13
uv tool install --python 3.13 oracle-factory==0.1.0a20
uv tool update-shell
oracle-factory --version
```

**Kit completo.** Además de `oracle-factory`, expone `oracle`, `tasks` (alias de `oracle-task`) y `oracle-clue` desde el *mismo* entorno aislado:

```bash
uv python install 3.13
uv tool install --python 3.13 --with-executables-from oracle-metalenguaje,oracle-task,oracle-clue oracle-factory==0.1.0a20
uv tool update-shell
oracle-factory --version
oracle --version
tasks --version
oracle-clue --version
```

En una instalación nueva, las versiones esperadas son Factory **0.1.0a20**, Oracle **0.39.0**, Oracle Task **0.2.0** y Oracle Clue **0.1.0a2**. Cerrá y reabrí la terminal después de `uv tool update-shell` si todavía no encuentra los comandos. Podés comprobar qué herramientas expone uv con `uv tool list`.

Si `uv` avisa un **conflicto** porque ya existe alguno de esos ejecutables, usá el camino **Sólo Factory**: instalás la CLI sin sobrescribir `oracle`, `tasks` ni `oracle-clue` de otra herramienta. Para ejecutar esos programas por separado desde la terminal, conservá las instalaciones que ya tenías; la CLI de Factory usa sus propias dependencias internas. No uses `--force` para tapar el conflicto sin identificar su origen.

### Cambiar de versión

`uv tool upgrade oracle-factory` respeta la restricción `==0.1.0a20` usada al instalar y por sí solo no pasa a una entrega posterior. Cuando exista y elijas una versión nueva, reemplazá `VERSION_NUEVA` por su número real y volvé a instalar:

```bash
uv tool install --python 3.13 oracle-factory==VERSION_NUEVA
oracle-factory --version
```

Si querés seguir exponiendo los tres comandos del kit, repetí la variante con `--with-executables-from` y la versión nueva. Consultá las versiones y dependencias de esa entrega antes de actualizar. [uv documenta cómo sustituir una restricción de versión](https://docs.astral.sh/uv/guides/tools/#upgrading-tools).

## Instalar el tablero de VS Code

Descargá [oracle-factory-0.5.0.vsix](https://github.com/Segtem/oracle-factory/releases/download/v0.1.0a20/oracle-factory-0.5.0.vsix) de la [release v0.1.0a20](https://github.com/Segtem/oracle-factory/releases/tag/v0.1.0a20). No hace falta clonar el repositorio ni tener `npm`. El SHA-256 del archivo publicado es:

```text
17e4450e5518eba721a52a14e04faee21164c488dfac1846972184659dfe8cbd  oracle-factory-0.5.0.vsix
```

En Linux, comparalo con `sha256sum oracle-factory-0.5.0.vsix`; en macOS, con `shasum -a 256 oracle-factory-0.5.0.vsix`; en PowerShell, con `(Get-FileHash .\oracle-factory-0.5.0.vsix -Algorithm SHA256).Hash`. Si no coincide, descargá el archivo otra vez antes de instalarlo.

En VS Code abrí **Extensiones**, el menú `…` de esa vista y **Instalar desde VSIX…**; elegí el archivo descargado. O desde la terminal, en la carpeta de descarga:

```bash
code --install-extension oracle-factory-0.5.0.vsix
code --list-extensions --show-versions
```

La lista debe contener `cs50-taller.oracle-factory@0.5.0`. Abrí tu proyecto en VS Code; la vista **Factory** aparece en el Explorador y el comando **Factory: Abrir el tablero** está en la paleta. [La guía del tablero](tablero.md) explica qué muestra. VS Code debe confiar en el espacio de trabajo para ejecutar la extensión.

La extensión busca primero `.venv/bin/oracle-factory` en el proyecto; si no existe, usa `oracle-factory` del `PATH`. Si VS Code no lo encuentra, reabrilo después de `uv tool update-shell`, o configurá `factory.comando` en la **configuración de usuario** con la ruta absoluta del ejecutable. Es una configuración de máquina: el `.vscode/settings.json` del proyecto no puede fijarla. Para ver dónde lo instaló uv, usá `uv tool dir --bin`.

El VSIX se instala manualmente y VS Code no lo actualiza automáticamente como una extensión del Marketplace. Cuando haya una nueva entrega, descargá e instalá su VSIX. Podés usar todos los comandos de Factory sin instalar el complemento.
