# Integración de entregas

- Cambio(s), IDs completos: 20261021-210148-9ge-notas
- Persona integradora y confirmación del equipo: A fixture; acuerdo simulado
- Rama / checkout de integración: main / /tmp/factory-colaboracion-5rtc31v8/C6/producto
- Base completa: 65e3df3c17008e2bf01aab9df9d231dcb3b2231c
- Entregas en orden (responsable, rama y commit completo): base A 65e3df3c17008e2bf01aab9df9d231dcb3b2231c; entrega B f278b0db4b27fc46c1b9fe56ac64e3687a05671c
- Dependencias e interfaces verificadas: aporte-b.txt independiente del ejemplo
- Paquetes, informes y triage (rutas y hashes por entrega): estado-revisado.json y estado-renovado.json; hashes en resultado.json
- Conflictos y decisión humana (o ninguno): ninguno
- Commit del candidato resultante: 8fef73df80b0bc1a4e45a603b249a15887f80d13
- Pruebas/sensor del candidato (comandos, resultado, artefactos y hashes): unittest y sensor de notas; comandos en ejecucion.json
- Gates obsoletos y renovaciones necesarias: revisión y juicio renovados después del merge
- Revisión del candidato y decisión humana: fixture; sin decisión humana real
- Oracle (requisitos, medidas, hechos, veredicto y límites): fixture verde; hechos sha256=82f6828218451de26d61633fc2197fd8ad5aaac1b343ae0766777746b7001916
- Pendientes de cierre: confirmación humana de cierre; no se cierra en este caso
- Confirmación humana de cierre (o pendiente): pendiente
- Commit que archiva el cierre (o pendiente): pendiente

Integrar una entrega por vez. Preservar estados divergentes antes de conciliarlos; nunca elegir el verde más avanzado. Un merge limpio requiere pruebas de compatibilidad. Distinguir el commit juzgado del commit posterior que archiva registros.
