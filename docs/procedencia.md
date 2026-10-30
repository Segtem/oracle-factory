# La procedencia de las dependencias

Factory registra qué se decidió y con qué evidencia. `oracle-factory procedencia` suma de dónde viene el software de terceros
sobre el que corre cada candidato, para que el día que se descubra una vulnerabilidad en una dependencia se pueda saber qué
cambios la usaron y decidir qué corregir. Todo es local: no usa la red.

Sigue las prácticas de servicios como [Lightwell](https://www.redhat.com/en/lightwell) (de IBM y Red Hat) sin depender de ellos:
un inventario de componentes, versiones fijadas, hashes de los archivos, origen declarado, y las versiones corregidas
reconocibles. Si algún día el proyecto instala paquetes desde un índice de correcciones, el inventario lo muestra sin cambios.

## El inventario

```bash
oracle-factory procedencia            # un resumen: cuántos componentes, si es confiable y por qué no
oracle-factory procedencia --json     # el inventario en CycloneDX 1.5 (JSON)
oracle-factory procedencia ID         # además lo guarda en el candidato del cambio ID y lo registra
```

Se arma con las dependencias de Python del proyecto: el lock (`uv.lock`), lo que pide `pyproject.toml` y lo que está instalado
(el `.venv` del proyecto, o el Python que indique `--python`; para leerlo se ejecuta ese Python con `-I -c`, sin importar el proyecto). De cada componente dice:

- su nombre, su versión y su enlace `pkg:pypi/…`;
- el índice de donde sale (`factory:origen`) y los hashes SHA-256 de sus archivos, tal como los registra el lock;
- si la versión está fijada (`factory:fijada`), si es una dependencia directa (`factory:directa`) y qué pide el proyecto
  (`factory:exigida`);
- de dónde sale cada dato (`factory:fuente`): `uv.lock`, o `instalado` cuando no hay lock y entonces no hay hashes ni origen
  que se puedan verificar;
- si el paquete está instalado en el entorno consultado y en esa versión (`factory:instalado`: `true`, `false`, o ausente si no se
  consultó el entorno);
- si es una versión corregida por Lightwell (`factory:corregida`): las que llevan el sufijo `+rhlw…` o `.rhlw-…`.

Un paquete que el lock fija en más de una versión aparece una vez por versión. Un paquete que está en el lock y no en el entorno (por ejemplo porque sólo se instala en otra versión de Python o en otro sistema) se marca
como no instalado, y no hace no confiable el inventario: un lock sirve a varios entornos. El archivo sale ordenado y sin marcas de tiempo:
dos corridas iguales dan el mismo archivo y la misma huella.

### Cuándo el inventario no es confiable

El inventario se declara **no confiable** (`factory:confiable: false`) y lista las diferencias (`factory:diferencia`) cuando:

- no hay `uv.lock`;
- el lock es de otra versión del proyecto que la de `pyproject.toml`;
- `pyproject.toml` exige una dependencia que el lock no tiene, o exige una versión fija distinta de la del lock;
- el entorno tiene instalada una versión que el lock no fija.

Si no se pudo consultar el entorno, el inventario lo dice (`factory:entorno: no consultado`) y se apoya en el lock y en
`pyproject.toml`. Una especificación no fijada (`>=2`) no es una diferencia: se registra como no fijada.

## El lock de Factory mismo

El `uv.lock` de Factory se versiona (ya no está en el `.gitignore`) y una prueba (`tests/test_uv_lock.py`) exige que coincida con su
`pyproject.toml`. En cada cambio de versión o de dependencias hay que regenerarlo, con `uv lock`, y commitearlo junto con el cambio:
si no, la prueba falla diciendo qué difiere.

## Guardarlo en el candidato

`oracle-factory procedencia ID` guarda el inventario en `.factory/cambios/ID/candidatos/<commit>/procedencia/cyclonedx.json` y
deja en el registro del cambio el evento `procedencia_registrada`, con la huella del archivo, la cantidad de componentes y si era
confiable. Un candidato nuevo tiene su propia carpeta: el inventario de uno anterior no se toca.

## Quién usó una dependencia

```bash
oracle-factory procedencia --buscar requests==2.31   # un paquete y una versión (exacta)
oracle-factory procedencia --buscar requests            # cualquier versión
```

Lista los cambios y candidatos cuyo inventario guardado la tiene. Los nombres se comparan como PyPI (`Foo_Bar` es `foo-bar`).
`--json` devuelve la lista como datos.

## Auditar contra avisos de seguridad

```bash
oracle-factory procedencia --auditar --avisos avisos.json
```

Cruza los inventarios guardados con un archivo de avisos en [formato OSV](https://ossf.github.io/osv-schema/) (un aviso, una
lista de avisos o un objeto con `vulns`), sin acceder a la red. El archivo lo traés vos, por ejemplo de OSV.dev o de la base de
avisos de tu proveedor. Para cada aviso del ecosistema PyPI lista los componentes afectados, las versiones en que se corrigió y
los cambios y candidatos que los usaron. Un archivo que no es OSV válido falla diciendo qué está mal, y nunca se lee como «sin
afectados».

Las versiones corregidas por Lightwell se listan aparte («afectados pero corregidos por Lightwell»): son las que un aviso
alcanzaría por su número base, pero que tienen la corrección aplicada. Verificá el aviso en cada caso. Una versión que no se puede
comparar con los rangos del aviso también se lista aparte, para que no se dé por limpia.

## Bajar los avisos de OSV.dev

```bash
oracle-factory procedencia --consultar-osv --red
oracle-factory procedencia --consultar-osv --red --salida avisos.json --json
```

Consulta la base pública OSV.dev por cada dependencia distinta (nombre y versión) de los inventarios guardados, guarda los avisos
que encuentra en `.factory/local/avisos-osv.json` (o en `--salida`) y corre enseguida la auditoría de arriba sobre ellos, de modo que
el resultado dice qué cambios y candidatos usaron una versión afectada. Es lo único de `procedencia` que usa la red, y sólo con
`--red`: sin esa bandera falla antes de conectarse.

- Hacia OSV.dev salen sólo el nombre, la versión y el ecosistema (PyPI) de cada dependencia, una vez cada una; la versión corregida
  por Lightwell se consulta sin su sufijo. Nunca salen rutas, identificadores de cambio ni contenido del repositorio.
- Un fallo (sin conexión, error HTTP, respuesta que no es JSON o un aviso que no es OSV válido) termina con error y no guarda nada:
  nunca se lee como «sin afectados». Un archivo de avisos anterior no se toca.
- `--salida` es una ruta del proyecto (una relativa se cuenta desde su raíz, no desde la carpeta donde estés), no admite `..` y ninguna carpeta de
  su camino puede ser un enlace simbólico; un archivo de sólo lectura no se reemplaza.
- Si OSV no declara avisos para ninguna dependencia, lo dice y no guarda archivo.
- Los avisos guardados se pueden volver a auditar sin red con `--auditar --avisos .factory/local/avisos-osv.json`.

## Qué no hace

- No corrige ni actualiza dependencias: decidir qué corrección aplicar es de una persona, y se registra como cualquier otro
  cambio de Factory.
- No firma archivos ni verifica firmas.
- No consulta la red salvo con `--consultar-osv --red`, y sólo a OSV.dev.
- Sólo Python: no mira npm, Go ni Maven.
