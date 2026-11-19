# Firmas de las decisiones de una persona

Sin firmas, Factory considera persona a cualquier proceso con una terminal interactiva, con el nombre de `git config user.name`.
Un agente que corre con tu usuario puede abrirse una pseudo-terminal y decidir como vos. Con firmas, cada decisión de una persona
lleva la firma de tu llave, y una decisión sin una firma válida no cuenta.

Una firma sólo te distingue de un agente si la llave pide algo que el agente no tiene: por eso la llave es una sólo para Factory,
**con frase**, y Factory firma sin ssh-agent. Cada decisión te pide la frase en la terminal.

## Activarlas

1. Creá la llave, con una frase que sólo vos sepas:

   ```
   ssh-keygen -t ed25519 -C "tu-nombre, decisiones de Factory" -f ~/.ssh/oracle-factory
   ```

   Si la guardás en otro lugar, indicalo con `ORACLE_FACTORY_LLAVE=/ruta/a/la/llave`. Factory se niega a firmar con una llave sin frase.

2. Agregate a `.factory-firmantes`, en la raíz del producto (formato `allowed_signers` de OpenSSH: un nombre sin espacios y la llave
   pública), y commitealo. Cambiar esta lista es un commit del producto: pasa por revisión como cualquier otro.

   ```
   echo "tu-nombre $(cat ~/.ssh/oracle-factory.pub)" >> .factory-firmantes
   ```

3. En `.factory/config.json`, `"firmas": "exigir"`. Si el proyecto ya tiene cambios cerrados sin firma, tomá antes el SHA
   completo del commit actual del almacén de registros (`git rev-parse HEAD` allí) y ponelo también como `"firmas_base": "SHA"`.
   Esa base tiene que ser un ancestro del almacén. Sin base, «exigir» pide firma también a todas las decisiones anteriores.

## Qué se firma

Con «exigir», al tomarla se firma cada una de estas decisiones de una persona: aprobar la spec, confirmar las medidas, revisar,
cerrar, abandonar, cambiar el modo, soltar un cambio, decidir una unión y aprobar el sensor. Se firma el registro entero de la
decisión (el cambio, qué se decidió, cuándo y quién), en JSON canónico, con `ssh-keygen -Y sign -n oracle-factory-decision`. El
registro guarda la firma (`firma`) y la huella de la llave (`firma_llave`). Si no hay llave, si no tiene frase o si la firma no
sale (por ejemplo, una frase equivocada), la decisión no se registra.

Un agente con `--agente` sigue proponiendo, como siempre: no firma.

## Qué se comprueba

Con «exigir», `verificar`, `juzgar` y `cerrar` comprueban con `ssh-keygen -Y verify` la firma de cada decisión de persona del
cambio contra `.factory-firmantes`. Una decisión sin firma, con una firma que no corresponde a lo registrado (el registro cambió
después de firmarse) o de una llave que no está en la lista no cuenta: se nombra y hay que volver a tomarla. Una aprobación del
sensor sin firma válida no cuenta como aprobación: `aprobar-sensor` la pide de nuevo.

Con `firmas_base`, sólo se toleran sin firma las decisiones que ya estaban en cambios cerrados en ese commit y siguen idénticas.
Una decisión agregada o modificada después, o una decisión de un cambio que estaba abierto, necesita firma. La base no autentica
la historia anterior: la confianza en esas decisiones depende del commit del almacén elegido por la persona. Al activar «exigir»,
la aprobación anterior del sensor no se hereda y hay que aprobarlo otra vez con la llave.

Sin «exigir», Factory hace lo de siempre, y `estado` avisa que las decisiones de persona del cambio no están firmadas.

## Lo que no cubre

- **Otro proceso de tu usuario que lea la memoria de `ssh-keygen`** mientras firma. Lo impide `kernel.yama.ptrace_scope` en 1 o más
  (el valor por omisión de muchas distribuciones): comprobalo con `cat /proc/sys/kernel/yama/ptrace_scope`.
- **Un registrador de teclas** que capture la frase, o la frase guardada en algún lugar que el agente pueda leer.
- **La lista de firmantes** es tan confiable como el repo del producto: quien puede commitear en él puede agregarse.
- **La autonomía por etapa y marcar revisada una nota** todavía no se firman (quedan para otro cambio).
- **Las decisiones ya tomadas sin firma** no se firman después: sin `firmas_base`, hay que volver a tomarlas. Con esa base,
  sólo se conserva lo ya cerrado e idéntico; las decisiones de cambios abiertos hay que volver a tomarlas.
- Llaves físicas (`ed25519-sk`, FIDO): `ssh-keygen` las acepta igual, pero no están probadas.
