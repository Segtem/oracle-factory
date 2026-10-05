# Piloto de colaboración con agentes — 01

- Estado: **realizado con agentes. El piloto humano sigue pendiente.** Lo pidió Brian el 2026-10-05 («haz el piloto para saber si funciona»). Como sólo había una persona disponible, los participantes son sesiones de agente.
- Personas A y B: no hubo personas. El coordinador (agente principal) las representó en los pasos humanos: aceptar specs, confirmar el reparto y la recepción del relevo, decidir el triage y cerrar. Ninguna de esas decisiones es humana.
- Agentes y sesiones:
  - A1: frente A, propuesta e implementación.
  - A2: frente A después del relevo, medición, entrega y revisión de B.
  - B1: frente B completo y revisión de A.
  - R1: revisor neutral del candidato integrado.
  - Cada sesión partía sin contexto previo: sólo leía `brief-comun.md` y `docs/colaboracion.md`.
- Fecha, entorno y versiones: 2026-10-05, Linux, una sola máquina. Cada frente usó su propio clone de un remoto bare (`origen.git`). oracle-factory 0.1.0a3 (rama de colaboración, `7709b83`), oracle-task 0.2.0, oracle-clue 0.1.0a1 y oracle-metalenguaje 0.38.1. Unos 20 minutos de reloj en total.
- Producto y cambios: el ejemplo `notas`, con base `d704844560fe22eedde97ac0411193d144c02a35`.
  - A, `20261005-101725-crear-notas-con`: `crear_nota`.
  - B, `20261005-101733-listar-notas`: `listar_notas`, que consume la nota de A.
- Integrador y revisores: el coordinador integró. A2 revisó B, B1 revisó A y R1 revisó el candidato integrado.
- Reparto confirmado, interfaces y dependencias: los dos agentes, por separado, señalaron antes de implementar que sensor, pruebas y catálogos eran compartidos. Se decidió separar archivos con un prefijo por capacidad. B leyó la propuesta de A y encontró dos huecos del contrato «nota v1» (saltos de línea y espacios), que se resolvieron antes de aceptar.
- Entregas de A y B:
  - A: producto `1d39ca3f…`, evidencia `d276e305…`.
  - B: producto `fcc0abbe…`, corregido después en `ed3476ba…`, con evidencia `619baeaf…`.
- Relevo: A1 entregó a A2 en `09363acf…`. A2, sin contexto, verificó HEAD, padre, base, árbol, índice, locks, procesos, los 5 SHA-256 y las pruebas; la recepción se confirmó en `9f6d40a5…`. No hizo falta ninguna pregunta.
- Solapamiento observado y decisión:
  - Sobre archivos compartidos: se detectó en la fase de reparto y se resolvió separando archivos.
  - Sobre la interfaz de hechos: B detectó que dos sensores emitiendo la relación `comprobacion` pondrían rojo un requisito ajeno sin conflicto Git. Se avisó a A2 por el canal y se usaron relaciones propias.
- Integración, revisión y gates:
  - Merges en serie (`79efe14` y `bfce3ed`), sin conflicto textual. Prueba del contrato en `test_integracion.py`.
  - Candidato `f9b4b3866cc0e67b10f4100c2b7c4ae02e4b9216`, con 12 pruebas OK y 5 de 5 requisitos en `oracle cobertura` usando los hechos combinados de los tres sensores.
  - R1 reprodujo byte a byte los hechos y la cobertura del integrador.
  - `revision`, `juzgar` (código 0) y `cerrar` de los dos cambios. Archivo en `719c3bd`, que pasó a `main` del remoto.
- Artefactos: esta carpeta, con `bitacora-coordinador.md` (cronología completa), `brief-comun.md`, `revisiones/` (paquetes, informes, triage y evidencia propia de cada revisor) y `origen.bundle` (el remoto completo con sus 3 ramas; `git clone origen.bundle`).
- Alcance que sigue sin medir:
  - La experiencia de personas reales (claridad, esperas, desacuerdos).
  - Máquinas distintas.
  - Ediciones concurrentes reales sobre el mismo registro.
  - Desacuerdos entre personas, porque aquí decidía un solo coordinador.
  - La autenticación de actores.

## ¿Funciona?

**Sí, para agentes y en este producto.** El protocolo llevó dos frentes en paralelo, un relevo sin contexto, revisiones cruzadas, una corrección y la integración hasta el cierre en Factory, sin interferencias entre checkouts y sin conflictos textuales.

Las revisiones fueron útiles:
- A2 encontró un defecto real y lo demostró con un mutante: el orden no estaba probado.
- R1 encontró un efecto cruzado que el triage por frente no vio: un riesgo aceptado en A afecta a un requisito de B.

## Lo que falló o costó (candidatos a cambios)

1. **Hechos de varios sensores.** `juzgar --con` toma un solo JSON. No hay forma de combinar hechos, y ninguna herramienta detecta que dos sensores emitan la misma relación. Es un solapamiento de interfaz que Git no ve. Integrador y revisor escribieron cada uno su propio script.
2. **Archivos compartidos por diseño.** Sensor, pruebas, catálogos y la sección `sensores` de `oracle.json` son compartidos y la guía no da un patrón. Funcionó usar un prefijo por capacidad (`sensor_<cap>.py`, `<cap>.*`, relación `<cap>_comprobacion`).
3. **Commit de producto y commit de evidencia.** La guía no fija cuál se ofrece y cuál se revisa. Un relevo commiteado no puede contener su propio hash.
4. **Reparto y relevo se desincronizan.** El «escritor activo» y el estado del reparto quedan viejos (B1-A-03), y nadie tiene la responsabilidad de actualizarlos.
5. **Dónde va el registro de integración de dos cambios.** Task rechaza `tareas/integracion-<sha>/` como «nombre de carpeta inválido». Se guardó en la tarea de A, con una referencia desde la de B.
6. **Actores y gates de Factory.**
   - `factory.json` registra «workstation» en todos los eventos.
   - `aprobar-spec`, `revision` y `cerrar` aceptan la frase por pipe, así que un agente puede darlas sin una persona.
7. **CLI de Factory.**
   - `estado` sugiere `medir --listar` aunque ya se midió, y después de `juzgar` sugiere `estado` en bucle.
   - `medir` reemplaza las medidas sin avisarlo y no señala medidas huérfanas.
   - `medir --listar` mezcla unas 40 medidas meta.
   - La `fuente` de los requisitos guarda una ruta absoluta del checkout.
   - La spec que genera `nuevo` no trae `## ADDED Requirements` y la plantilla de proposal dice «Brian».
   - `revision` falla si el repositorio no tiene commits.
8. **Clue.**
   - El triage no tiene un estado para «pedir corrección».
   - No hay esqueleto del informe.
   - El paquete no muestra el diff.
   - `validar` confirma formato, no contenido.
9. **Triage por frente.** No mira la spec del otro frente: lo encontró R1 al integrar (R1-01). La guía debería pedir que los riesgos aceptados se revisen otra vez contra el candidato integrado.
10. **`oracle cobertura --con`.** Funcionó como un «juzgar sin registro» muy útil para verificarse. La guía no lo menciona.
11. **Medidas del ejemplo.** Violan `meta.ningun_umbral_de_igualdad` y `meta.toda_medida_filtra_o_agrupa`, y los agentes las copiaron.
