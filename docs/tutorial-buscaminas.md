# Buscaminas desde cero con Factory 0.1.0a20

Vas a construir un Buscaminas de terminal de 5 × 5 desde una carpeta vacía, sin clonar Factory. El tablero tiene cinco minas fijas: así podés conocer el resultado esperado antes de escribir código. Al terminar tendrás un juego ejecutable, pruebas, hechos del sensor, una revisión y un cambio cerrado por Factory. No hace falta contratar un revisor de IA.

Este recorrido se comprobó en Linux con Python 3.13 y Factory 0.1.0a20. Usá una terminal con Git y Python 3.11 o posterior. Los comandos `oracle-factory` de este tutorial los ejecuta **una persona**; si trabaja un agente, debe poner `--agente NOMBRE` después de `oracle-factory`. Un agente puede preparar y proponer, pero en el modo `confirmacion` la persona aprueba spec, medidas y revisión, y cierra.

| Momento | Qué aporta Factory |
| --- | --- |
| Antes del código | Conserva la propuesta y la spec que la persona aceptó. |
| Al probar | Liga requisitos con medidas y ejecuta un sensor aprobado sobre un commit limpio. |
| Al revisar | Guarda quién revisó, qué encontró y la decisión de la persona. |
| Al cerrar | Exige revisión vigente y juicio Oracle verde; fusiona la spec aceptada. |

## 1. Instalá Factory y prepará el proyecto

Seguí la [guía de instalación](instalacion.md) si necesitás instalar `uv` o resolver nombres de ejecutables. Para este tutorial alcanza la CLI, sin el complemento de VS Code:

```bash
uv python install 3.13
uv tool install --python 3.13 oracle-factory==0.1.0a20
uv tool update-shell
oracle-factory --version
```

Abrí otra terminal si `oracle-factory` aún no está en el `PATH`. En una carpeta nueva:

```bash
mkdir mi-buscaminas
cd mi-buscaminas
git init
oracle-factory init
```

`init` crea `.factory/`, los lugares de Oracle y OpenSpec, y los hooks que agregan `Cambio: ID` a los commits. No aprueba nada. En VS Code podés abrir esta carpeta y usar el [tablero opcional](instalacion.md#instalar-el-tablero-de-vs-code); todos los pasos también funcionan desde la terminal.

## 2. Abrí el cambio y escribí el acuerdo

```bash
oracle-factory nuevo --capacidad buscaminas --sufijo primer-juego "Crear un Buscaminas de terminal"
oracle-factory listar
oracle-factory estado ID_DEL_CAMBIO
```

Copiá el **ID completo** que devolvió `nuevo` o `listar` y sustituilo por `ID_DEL_CAMBIO` en los comandos siguientes. `estado` te dirá siempre qué sigue. Antes de implementar, abrí `openspec/changes/ID_DEL_CAMBIO/proposal.md` y reemplazá la plantilla por este contenido:

```markdown archivo=proposal.md
# Construir un Buscaminas de terminal

## Por qué

Queremos practicar el desarrollo de una regla jugable y comprobarla con hechos, no sólo ejecutar comandos de Factory.

## Qué cambia

Un tablero fijo de 5 por 5 permite destapar casillas, poner banderas y distinguir victoria de derrota. Las pruebas y el sensor observan sus reglas.

## Fuera de alcance

No hay interfaz gráfica, niveles aleatorios ni partidas guardadas. El primer clic puede ser una mina.

## Decisiones humanas

La persona aprueba esta propuesta y la spec, acepta el sensor y las medidas, revisa el código y decide el cierre.
```

En `openspec/changes/ID_DEL_CAMBIO/specs/buscaminas/spec.md` guardá:

```markdown archivo=spec.md
# Capability: buscaminas

## ADDED Requirements

### Requirement: tablero jugable
Tipo: funcional
El juego DEBE usar un tablero fijo de 5 por 5, contar las minas vecinas, destapar casillas, expandir regiones vacías, alternar banderas, perder al destapar una mina y ganar al destapar todas las casillas seguras. DEBE rechazar coordenadas inválidas y acciones después del fin sin corromper el estado.

#### Scenario: número y región vacía
- DADO un tablero nuevo
- CUANDO se destapa una casilla segura
- ENTONCES muestra su número de minas vecinas y expande las casillas conectadas si es cero

#### Scenario: bandera y error
- DADO un tablero nuevo
- CUANDO se marca una casilla o se intenta destapar una coordenada inválida
- ENTONCES la bandera bloquea el destape y el error conserva el estado

#### Scenario: victoria y derrota
- DADO un tablero nuevo
- CUANDO se destapa una mina o todas las casillas seguras
- ENTONCES la partida termina como perdida o ganada respectivamente
```

La spec dice qué comportamiento se espera; el código todavía no existe. Leela y ajustá el alcance si no representa el juego que querés construir. Una persona acepta el acuerdo con:

```bash
oracle-factory aprobar-spec ID_DEL_CAMBIO
oracle-factory importar ID_DEL_CAMBIO
oracle-factory estado ID_DEL_CAMBIO
```

En el menú de `aprobar-spec`, elegir la opción de aprobación es una decisión humana. `importar` crea un requisito Oracle **sin medir**; todavía no afirma que el juego funcione. Si después cambiás la propuesta o la spec, repetí la aprobación y la importación antes de seguir.

## 3. Escribí las pruebas antes del juego

Creá `test_buscaminas.py` en la raíz de `mi-buscaminas` con estos cuatro casos:

```python archivo=test_buscaminas.py
"""Casos que se escriben antes de implementar buscaminas.py."""

import unittest

from buscaminas import MINAS, Partida


class Reglas(unittest.TestCase):
    def test_numero_y_minas_ocultas(self):
        partida = Partida()
        self.assertEqual(partida.numero(2, 2), 2)
        partida.destapar(2, 2)
        self.assertNotIn("*", partida.vista())

    def test_cero_y_bandera(self):
        partida = Partida()
        partida.alternar_bandera(1, 1)
        with self.assertRaises(ValueError):
            partida.destapar(1, 1)
        partida.destapar(3, 1)
        self.assertGreater(len(partida.destapadas), 1)
        self.assertFalse(partida.destapadas & MINAS)

    def test_derrota_y_victoria(self):
        derrota = Partida()
        derrota.destapar(1, 1)
        self.assertEqual(derrota.estado, "perdida")
        victoria = Partida()
        for fila in range(1, 6):
            for columna in range(1, 6):
                if (fila, columna) not in MINAS and victoria.estado == "jugando":
                    victoria.destapar(fila, columna)
        self.assertEqual(victoria.estado, "ganada")

    def test_errores_no_alteran_estado(self):
        partida = Partida()
        with self.assertRaises(ValueError):
            partida.destapar(0, 1)
        self.assertEqual(partida.destapadas, set())
        self.assertEqual(partida.estado, "jugando")


if __name__ == "__main__":
    unittest.main()
```

Ejecutalos **antes de implementar**:

```bash
python3 -m unittest discover -s . -p 'test_buscaminas.py'
```

Esperá un error de importación: todavía falta `buscaminas.py`. Esa falla inicial comprueba que los casos no eran verdes por accidente. Si falla por otra causa, corregí el test antes de avanzar.

Ahora creá `buscaminas.py` junto al test:

```python archivo=buscaminas.py
"""Buscaminas de terminal: tablero fijo y reglas separadas de la entrada de texto."""

from collections import deque


LADO = 5
MINAS = frozenset({(1, 1), (1, 5), (3, 3), (5, 1), (5, 5)})


class Partida:
    def __init__(self):
        self.destapadas = set()
        self.banderas = set()
        self.estado = "jugando"

    @staticmethod
    def _validar(fila, columna):
        if not (isinstance(fila, int) and isinstance(columna, int)
                and 1 <= fila <= LADO and 1 <= columna <= LADO):
            raise ValueError("fila y columna deben estar entre 1 y 5")

    @staticmethod
    def _vecinas(fila, columna):
        for f in range(max(1, fila - 1), min(LADO, fila + 1) + 1):
            for c in range(max(1, columna - 1), min(LADO, columna + 1) + 1):
                if (f, c) != (fila, columna):
                    yield f, c

    def numero(self, fila, columna):
        self._validar(fila, columna)
        return sum(vecina in MINAS for vecina in self._vecinas(fila, columna))

    def _jugando(self):
        if self.estado != "jugando":
            raise ValueError("la partida ya terminó")

    def alternar_bandera(self, fila, columna):
        self._jugando()
        self._validar(fila, columna)
        casilla = (fila, columna)
        if casilla in self.destapadas:
            raise ValueError("no se puede marcar una casilla destapada")
        if casilla in self.banderas:
            self.banderas.remove(casilla)
        else:
            self.banderas.add(casilla)

    def destapar(self, fila, columna):
        self._jugando()
        self._validar(fila, columna)
        casilla = (fila, columna)
        if casilla in self.banderas:
            raise ValueError("quitá la bandera antes de destapar")
        if casilla in self.destapadas:
            return
        if casilla in MINAS:
            self.destapadas.add(casilla)
            self.estado = "perdida"
            return

        pendientes = deque([casilla])
        while pendientes:
            actual = pendientes.popleft()
            if actual in self.destapadas or actual in self.banderas or actual in MINAS:
                continue
            self.destapadas.add(actual)
            if self.numero(*actual) == 0:
                pendientes.extend(self._vecinas(*actual))
        if len(self.destapadas) == LADO * LADO - len(MINAS):
            self.estado = "ganada"

    def vista(self):
        filas = ["    1 2 3 4 5"]
        for f in range(1, LADO + 1):
            casillas = []
            for c in range(1, LADO + 1):
                pos = (f, c)
                if pos in self.destapadas and pos in MINAS:
                    signo = "*"
                elif pos in self.destapadas:
                    n = self.numero(f, c)
                    signo = str(n) if n else "."
                elif pos in self.banderas:
                    signo = "F"
                elif self.estado != "jugando" and pos in MINAS:
                    signo = "*"
                else:
                    signo = "#"
                casillas.append(signo)
            filas.append(f"{f} | " + " ".join(casillas))
        return "\n".join(filas)


def jugar():
    partida = Partida()
    print("Buscaminas 5×5. d FILA COLUMNA destapa; b FILA COLUMNA marca; salir termina.")
    while True:
        print(partida.vista())
        if partida.estado != "jugando":
            print("Ganaste." if partida.estado == "ganada" else "Perdiste.")
            return
        try:
            orden = input("> ").strip().lower().split()
        except EOFError:
            return
        if orden == ["salir"]:
            return
        try:
            if len(orden) != 3 or orden[0] not in {"d", "b"}:
                raise ValueError("usá d FILA COLUMNA, b FILA COLUMNA o salir")
            fila, columna = int(orden[1]), int(orden[2])
            if orden[0] == "d":
                partida.destapar(fila, columna)
            else:
                partida.alternar_bandera(fila, columna)
        except ValueError as error:
            print(f"Comando inválido: {error}")


if __name__ == "__main__":
    jugar()
```

Repetí la suite y jugá:

```bash
python3 -m unittest discover -s . -p 'test_buscaminas.py'
python3 buscaminas.py
```

La suite debe pasar cuatro casos. En el juego, `d 2 2` destapa y muestra **2**; `b 1 1` marca o desmarca una bandera; `d 1 1` pierde si quitaste esa bandera; `salir` termina. Las coordenadas visibles empiezan en 1. El centro y las cuatro esquinas son minas. La región alrededor de `3 1` no tiene mina vecina y se expande. El primer clic **puede** ser una mina: no implementamos protección especial.

## 4. Hacé observable el comportamiento para Oracle

Los tests ayudan al desarrollo; Oracle necesita hechos del candidato. Creá `sensor.py` en la raíz del proyecto. Observa seis reglas; el caso de números comprueba las 20 casillas seguras contra las cinco minas fijas, así también detecta errores localizados. Escribe `codigo: 0` cuando una regla coincide con lo esperado y `codigo: 1` si falla:

```python archivo=sensor.py
"""Observa seis reglas del Buscaminas y escribe hechos para Oracle."""

import argparse
import json
from pathlib import Path

from buscaminas import MINAS, Partida


def _numero():
    minas_esperadas = frozenset({(1, 1), (1, 5), (3, 3), (5, 1), (5, 5)})
    if MINAS != minas_esperadas:
        return False
    partida = Partida()
    for fila in range(1, 6):
        for columna in range(1, 6):
            if (fila, columna) in minas_esperadas:
                continue
            esperado = sum(abs(fila - f) <= 1 and abs(columna - c) <= 1
                           for f, c in minas_esperadas)
            if partida.numero(fila, columna) != esperado:
                return False
    return True


def _cero():
    partida = Partida()
    partida.destapar(3, 1)
    return len(partida.destapadas) > 1 and not partida.destapadas & MINAS


def _bandera():
    partida = Partida()
    partida.alternar_bandera(1, 1)
    try:
        partida.destapar(1, 1)
    except ValueError:
        bloqueada = (1, 1) in partida.banderas and (1, 1) not in partida.destapadas
    else:
        bloqueada = False
    partida.alternar_bandera(1, 1)
    return bloqueada and (1, 1) not in partida.banderas


def _mina():
    partida = Partida()
    partida.destapar(1, 1)
    return partida.estado == "perdida"


def _victoria():
    partida = Partida()
    for fila in range(1, 6):
        for columna in range(1, 6):
            if (fila, columna) not in MINAS and partida.estado == "jugando":
                partida.destapar(fila, columna)
    return partida.estado == "ganada"


def _invalidas():
    partida = Partida()
    try:
        partida.destapar(0, 1)
    except ValueError:
        intacta = partida.estado == "jugando" and not partida.destapadas
    else:
        intacta = False
    partida.destapar(1, 1)
    try:
        partida.alternar_bandera(2, 2)
    except ValueError:
        return intacta and partida.estado == "perdida" and not partida.banderas
    return False


def observar():
    pruebas = (("numero", _numero), ("cero", _cero), ("bandera", _bandera),
               ("mina", _mina), ("victoria", _victoria), ("invalidas", _invalidas))
    casos = []
    for nombre, prueba in pruebas:
        try:
            correcto = prueba()
        except Exception:
            correcto = False
        casos.append({"caso": nombre, "codigo": int(not correcto)})
    return {"casos": casos, "corrida": [{"completa": 1, "casos": len(casos)}]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, required=True)
    destino = parser.parse_args().salida
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(observar(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Hechos de Buscaminas escritos en {destino}")
```

Probalo antes de declararlo:

```bash
python3 sensor.py --salida hechos-locales.json
python3 -m json.tool hechos-locales.json
```

El archivo debe contener seis filas en `casos` y una en `corrida`. Es sólo un ensayo local: `evidencia` volverá a correr el sensor en un checkout limpio. Podés borrar `hechos-locales.json` antes del commit.

Creá `catalogos/` y guardá las dos medidas siguientes. La primera exige seis resultados correctos; la segunda exige que el sensor declare seis casos. Ninguna demuestra que elegiste los casos adecuados: eso se revisa leyendo el sensor.

`catalogos/buscaminas.casos_correctos.oracle`:

```oracle archivo=catalogos/buscaminas.casos_correctos.oracle
medida buscaminas.casos_correctos:
    de casos c
    donde c.codigo == 0
    resumen contar(1)
    umbral == 6 segun contrato porque "las seis observaciones deben coincidir con lo esperado"
    requiere casos
    ambito universal
    alcance "seis reglas del tablero fijo; su pertinencia depende del sensor revisado"
```

`catalogos/buscaminas.corrida_completa.oracle`:

```oracle archivo=catalogos/buscaminas.corrida_completa.oracle
medida buscaminas.corrida_completa:
    de corrida c
    donde c.completa == 1 y c.casos == 6
    resumen contar(1)
    umbral == 1 segun contrato porque "el sensor debe declarar seis casos ejecutados"
    requiere corrida
    ambito universal
    alcance "integridad declarada por el sensor; no autentica hechos ni reemplaza revisión humana"
```

El sensor se declara en `.factory/config.json`. Como `init` acaba de crear este proyecto, reemplazá ese archivo por el contenido siguiente; conservá otros ajustes tuyos si ya los agregaste. `{python}` y `{salida}` son marcadores que Factory sustituye al ejecutarlo:

```json archivo=config.json
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

**Antes de usar la evidencia**, una persona inspecciona y aprueba el comando del sensor:

```bash
oracle-factory aprobar-sensor
```

El menú mostrará `python sensor.py --salida …` con el Python elegido por Factory. No apruebes un comando que no reconocés: el sensor es código del proyecto y podría hacer cualquier cosa que tu usuario pueda hacer. Cambiar su declaración exige una nueva aprobación.

Luego elegí las medidas del requisito importado:

```bash
oracle-factory medir ID_DEL_CAMBIO --listar
oracle-factory medir ID_DEL_CAMBIO --requisito ID_DEL_REQUISITO --medida buscaminas.casos_correctos --medida buscaminas.corrida_completa --quitar-sin-medir
```

Sustituí `ID_DEL_REQUISITO` por el identificador completo que muestra `medir --listar`. No uses el ID del cambio en su lugar. La persona revisa los umbrales y confirma la asociación. Si un agente propone esas medidas con `oracle-factory --agente NOMBRE medir …`, la persona las confirma con `oracle-factory medir ID_DEL_CAMBIO --confirmar`.

## 5. Guardá el candidato y producí la evidencia

Mirá qué vas a versionar, quitá el ensayo `hechos-locales.json` y creá un commit:

```bash
rm -f hechos-locales.json
git status --short
git add .
git commit -m "Construir el Buscaminas y sus pruebas"
git log -1 --format='%h %B'
```

El hook de Factory agrega `Cambio: ID_DEL_CAMBIO` al mensaje. Si Git pide nombre y correo, configurá tu identidad de Git antes de repetir el commit. El sensor requiere archivos guardados en un commit: Factory lo corre en otro checkout, no sobre el editor abierto.

```bash
oracle-factory evidencia ID_DEL_CAMBIO
oracle-factory estado ID_DEL_CAMBIO
```

Buscá `éxito` y la ruta de `hechos.json` en la última salida. El sensor observa este commit; modificar `buscaminas.py`, los tests o las medidas después hace vieja esa evidencia. Un hecho verde es una observación producida por el sensor aprobado, no una prueba de que el sensor eligió todos los riesgos.

## 6. Pedí una revisión real y registrá la decisión

Otra persona con criterio técnico debería revisar la spec, `buscaminas.py`, `test_buscaminas.py`, `sensor.py`, los catálogos y la salida de pruebas. Podés usar `oracle-factory pedir-revision ID_DEL_CAMBIO --a NOMBRE` si configuraste un revisor externo; **no hace falta un revisor de IA** para completar este recorrido. Si revisás tu propio código, dejá esa limitación explícita en el informe, sin llamarlo revisión independiente.

Creá el directorio local y luego `.factory/local/review.md` con tu editor:

```bash
mkdir -p .factory/local
```

Este texto es una **plantilla para completar con hechos reales**, no un informe ya aprobado:

```markdown
# Revisión del Buscaminas
Revisor: TU_NOMBRE_REAL
Commit revisado (git rev-parse HEAD): PEGAR_SHA_REAL
Archivos revisados: propuesta, spec, buscaminas.py, test_buscaminas.py, sensor.py, catalogos/ y .factory/config.json
Pruebas ejecutadas y resultado: COMPLETAR_CON_LA_SALIDA_REAL
Hechos del sensor y límites: COMPLETAR_TRAS_LEER_LA_EVIDENCIA
Hallazgos y resolución de cada uno: COMPLETAR; si no hubo, explicar por qué
Hallazgos abiertos: COMPLETAR
Límite de independencia: COMPLETAR
Conclusión motivada: COMPLETAR
```

Para recuperar el SHA:

```bash
git rev-parse HEAD
```

Si hay un defecto, corregilo antes de aprobar. Sólo cuando el informe está completo y no quedan hallazgos abiertos, la persona registra su revisión con un comando que le muestra qué decisión va a tomar:

```bash
oracle-factory revision ID_DEL_CAMBIO --informe .factory/local/review.md --revisor "TU_NOMBRE_REAL" --decision aprobar --hallazgos-abiertos 0
oracle-factory estado ID_DEL_CAMBIO
```

Si usaste un revisor externo, leé su informe y decidí cada hallazgo. `revision` registra tu decisión, no convierte automáticamente el informe en verdadero. Si quedan abiertos, registrá `--decision cambios` con el número real de hallazgos y seguí trabajando.

## 7. Juzgá y cerrá

```bash
oracle-factory juzgar ID_DEL_CAMBIO
oracle-factory estado ID_DEL_CAMBIO
```

Oracle debe informar que el requisito se cumple y `estado` debe decir que no quedan pendientes. El juicio sólo cubre los seis casos declarados, no todos los tableros posibles. Una persona decide el cierre en el menú:

```bash
oracle-factory cerrar ID_DEL_CAMBIO
oracle-factory estado ID_DEL_CAMBIO
oracle-factory resumen --verificar
```

Esperá `Fase: cerrada`. Factory fusiona la spec aceptada en `openspec/specs/buscaminas/spec.md` y conserva quién aprobó, qué commit se revisó y qué hechos juzgó. Para investigar luego:

```bash
oracle-factory log ID_DEL_CAMBIO
oracle-factory por-que buscaminas.py:1
```

`por-que` relaciona líneas versionadas con el cambio y sus decisiones. El ejemplo terminó localmente: no publicaste el juego ni diste a Factory permiso para enviar tu repositorio a ningún remoto.

## Si algo sale rojo

- **Test antes de implementar:** la falla de importación es esperada; después de crear `buscaminas.py`, las cuatro pruebas deben pasar. Una falla de comportamiento requiere corregir código o la expectativa de la spec, no borrar el test.
- **Regla rota:** si algún número es incorrecto o una bandera deja destapar, el sensor emite un caso con `codigo: 1`; las medidas no dan verde. Revisá `hechos.json`, corregí, repetí pruebas y creá un **nuevo commit**.
- **Cambió el candidato:** repetí `oracle-factory evidencia ID_DEL_CAMBIO`, pedí una nueva revisión o actualizá el informe sobre el nuevo commit, registrá la nueva decisión y repetí `oracle-factory juzgar ID_DEL_CAMBIO`. No reutilices un juicio viejo.
- **Cambió la propuesta o spec:** pedí otra aprobación humana, ejecutá `importar` de nuevo y revisá las medidas. Si cambia el comando del sensor, una persona repite `aprobar-sensor`.
- **No sabés qué falta:** `oracle-factory listar` recupera el ID y `oracle-factory estado ID_DEL_CAMBIO` indica el próximo paso. Un error de firma o una revisión pendiente no se arregla escribiendo hechos a mano.

El [ejemplo versionado](https://github.com/Segtem/oracle-factory/tree/main/examples/buscaminas) conserva exactamente los archivos copiables de esta página para comparar tu resultado. Los tests del repositorio comprueban que los bloques de esta guía y esos archivos no divergen.
