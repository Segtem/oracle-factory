# Tres ejemplos cortos para entender qué aporta Factory

Estos ejercicios usan Factory 0.1.0a20, Python 3.11 o posterior y Git. Cada carpeta es un proyecto de práctica independiente: una regla, dos pruebas y un sensor con un caso observable. Podés ejecutarlos en unos minutos sin clonar Factory. El [tutorial de Buscaminas](tutorial-buscaminas.md) muestra cada menú y decisión de un cambio completo.

| Ejercicio | Regla que importa | Qué conserva Factory |
| --- | --- | --- |
| [Precio](#precio-un-limite-de-negocio) | El descuento máximo es 50 %. | La spec aceptada fija el límite; la medida y el sensor muestran si un commit lo respeta. |
| [CSV](#csv-una-entrada-defectuosa) | Una fila negativa o incompleta se rechaza. | La revisión puede preguntar si rechazar era la decisión correcta, no sólo si el test pasa. |
| [Ayuda](#ayuda-un-enlace-roto) | El primer paso enlazado existe. | El cambio de documentación también deja hechos, revisión y procedencia. |

Las pruebas ejecutan los casos. Factory registra quién acordó la regla, qué sensor se aprobó, qué medida se eligió, qué commit se observó y quién decidió la revisión. No escribe el producto ni garantiza que un sensor haya elegido todos los riesgos.

## Prepará uno de los ejercicios

Instalá Factory con la [guía de instalación](instalacion.md). Elegí una fila; son proyectos distintos, así que empezá en una carpeta vacía por cada uno:

| `caso` | `archivos` que se descargan |
| --- | --- |
| `precio` | `total.py test_total.py sensor.py spec.md` |
| `csv` | `lector.py test_lector.py sensor.py spec.md` |
| `ayuda` | `uso.md pasos.md test_ayuda.py sensor.py spec.md` |

Para Precio, copiá este bloque tal cual. Para CSV o Ayuda, cambiá sólo las dos primeras líneas por la fila correspondiente:

```bash
caso=precio
archivos="total.py test_total.py sensor.py spec.md"
mkdir "mi-$caso"
cd "mi-$caso"
git init
oracle-factory init
base="https://raw.githubusercontent.com/Segtem/oracle-factory/main/examples/cortos"
for archivo in $archivos; do curl --fail --location --silent --show-error "$base/$caso/$archivo" --output "$archivo"; done
curl --fail --location --silent --show-error "$base/comun/config.json" --output .factory/config.json
mkdir -p catalogos
for archivo in cortos.caso.oracle cortos.corrida.oracle; do curl --fail --location --silent --show-error "$base/comun/catalogos/$archivo" --output "catalogos/$archivo"; done
python3 -m unittest discover -s . -p "test_*.py"
python3 sensor.py --salida hechos-locales.json
python3 -m json.tool hechos-locales.json
```

La suite debe pasar dos pruebas y `hechos-locales.json` debe tener un `caso` con `codigo: 0` y `corrida` con `completa: 1` y `casos: 1`. Es un ensayo local; Factory volverá a ejecutar el sensor en un checkout limpio después de que apruebes su comando y guardes un commit. Si no tenés `curl`, abrí los archivos de [Precio](https://github.com/Segtem/oracle-factory/tree/main/examples/cortos/precio), [CSV](https://github.com/Segtem/oracle-factory/tree/main/examples/cortos/csv) o [Ayuda](https://github.com/Segtem/oracle-factory/tree/main/examples/cortos/ayuda) y copiá su contenido.

El archivo compartido que colocaste en `.factory/config.json` declara exactamente el comando que Factory pedirá aprobar:

```json archivo=comun/config.json
{
  "modo_por_defecto": "confirmacion",
  "tipos_obligatorios": false,
  "sensor": {
    "comando": ["{python}", "sensor.py", "--salida", "{salida}"],
    "tope_minutos": 5,
    "hechos": "exigir"
  }
}
```

Los dos catálogos sirven para cualquiera de los tres proyectos, **de a uno por carpeta**. Uno exige el caso correcto y el otro que se declaró una corrida completa:

```oracle archivo=comun/catalogos/cortos.caso.oracle
medida cortos.caso:
    de casos c
    donde c.codigo == 0
    resumen contar(1)
    umbral == 1 segun contrato porque "el caso declarado debe cumplir"
    requiere casos
    ambito universal
    alcance "un caso por ejercicio; depende de lo que observe su sensor"
```

```oracle archivo=comun/catalogos/cortos.corrida.oracle
medida cortos.corrida:
    de corrida c
    donde c.completa == 1 y c.casos == 1
    resumen contar(1)
    umbral == 1 segun contrato porque "el sensor declara un caso completo"
    requiere corrida
    ambito universal
    alcance "integridad declarada por el sensor; no autentica sus hechos"
```

## Precio: un límite de negocio

La regla es `calcular(1001, 50) == 501`: la rebaja se trunca en centavos. Un descuento de `51` se rechaza. La implementación de referencia es:

```python archivo=precio/total.py
"""Precio en centavos con descuento entero de 0 a 50 por ciento."""


def calcular(centavos, descuento):
    if type(centavos) is not int or type(descuento) is not int:
        raise ValueError("centavos y descuento deben ser enteros")
    if centavos < 0 or not 0 <= descuento <= 50:
        raise ValueError("importe negativo o descuento fuera de 0..50")
    return centavos - centavos * descuento // 100
```

Las dos pruebas de `examples/cortos/precio/test_total.py` verifican límite y redondeo; `examples/cortos/precio/sensor.py` emite el hecho `limite`. Para ver un rojo, cambiá temporalmente `<= 50` por `<= 51` en `total.py` y repetí los dos últimos comandos de prueba y sensor. Aceptar `51` produce `codigo: 1`. Volvé a `<= 50` antes del commit. Factory permite que una persona decida explícitamente si el límite 50 pertenece al contrato; el test por sí solo no registra esa aprobación.

## CSV: una entrada defectuosa

`A,3` y `B,4` suman 7. Una fila `B,-4` o `B` sin cantidad debe producir `ValueError`:

```python archivo=csv/lector.py
"""Suma cantidades positivas de filas CSV codigo,cantidad sin encabezado."""

import csv
from io import StringIO


def sumar(texto):
    total = 0
    for fila in csv.reader(StringIO(texto)):
        if len(fila) != 2 or not fila[0].strip():
            raise ValueError("cada fila necesita código y cantidad")
        try:
            cantidad = int(fila[1])
        except ValueError as error:
            raise ValueError("la cantidad debe ser entera") from error
        if cantidad <= 0:
            raise ValueError("la cantidad debe ser positiva")
        total += cantidad
    return total
```

Las pruebas de `examples/cortos/csv/test_lector.py` y el sensor comprueban el caso. Para reproducir el error, cambiá temporalmente `cantidad <= 0` por `cantidad == 0`: la fila negativa pasa y el hecho `fila` queda en `codigo: 1`. Restaurá la condición. La decisión de **rechazar** filas malas, en lugar de omitirlas, queda escrita en la spec y puede revisarse con el contexto del cambio.

## Ayuda: un enlace roto

El producto aquí es texto, no Python. `uso.md` debe llevar a `pasos.md`:

```markdown archivo=ayuda/uso.md
# Uso

Empezá por el [primer paso](pasos.md).
```

`examples/cortos/ayuda/sensor.py` busca ese enlace y comprueba que el archivo exista. Cambiá temporalmente `pasos.md` por `faltante.md` en `uso.md`: el hecho `enlace` queda en `codigo: 1`. La medida sólo comprueba **este enlace declarado**; leer si la ayuda sirve a una persona sigue siendo trabajo de revisión.

## Convertí la práctica en un cambio de Factory

Cada carpeta trae una `spec.md` breve. Cuando quieras desarrollar una variante propia, hacé el acuerdo **antes de editar el producto**. Los comandos siguientes los ejecuta una persona; un agente agrega `--agente NOMBRE` después de `oracle-factory` y sólo propone las decisiones reservadas a la persona en modo `confirmacion`:

```bash
oracle-factory nuevo --capacidad "$caso" --sufijo primer-ejercicio "Comprobar la regla de $caso"
oracle-factory listar
oracle-factory estado ID_DEL_CAMBIO
```

Copiá `spec.md` a `openspec/changes/ID_DEL_CAMBIO/specs/CASO/spec.md` y completá `proposal.md` en esa carpeta con el motivo, el cambio y lo que queda fuera. Sustituí `CASO` por `precio`, `csv` o `ayuda`. Revisá la spec y usá el orden de decisiones del [tutorial completo](tutorial-buscaminas.md#2-abrí-el-cambio-y-escribí-el-acuerdo):

```bash
oracle-factory aprobar-spec ID_DEL_CAMBIO
oracle-factory importar ID_DEL_CAMBIO
oracle-factory medir ID_DEL_CAMBIO --listar
oracle-factory medir ID_DEL_CAMBIO --requisito ID_DEL_REQUISITO --medida cortos.caso --medida cortos.corrida --quitar-sin-medir
oracle-factory aprobar-sensor
rm hechos-locales.json
git add .
git commit -m "Comprobar la regla del ejercicio"
oracle-factory evidencia ID_DEL_CAMBIO
oracle-factory revisar ID_DEL_CAMBIO
oracle-factory juzgar ID_DEL_CAMBIO
oracle-factory cerrar ID_DEL_CAMBIO
oracle-factory por-que ARCHIVO:1
```

`ID_DEL_REQUISITO` sale de `medir --listar` y `ARCHIVO` es `total.py`, `lector.py` o `uso.md`. Al aprobar el sensor, inspeccioná el comando; ejecutar código de un proyecto con tu usuario requiere tu decisión. En `revisar`, leé el producto, el sensor, la evidencia y los límites antes de aprobar: el menú registra una decisión humana, no una prueba automática. Si corregís el candidato después de producir hechos, repetí commit, `evidencia` y revisión antes de `juzgar`. El tutorial de Buscaminas detalla cómo preparar un informe real y resolver hallazgos.

`por-que` liga la línea versionada con el cambio cerrado y sus decisiones. Ese rastro y la posibilidad de preguntar **por qué se eligió la regla** son la diferencia visible cuando un ejemplo pequeño empieza a crecer con otras personas.
