# Integración de entregas

- Cambio(s), IDs completos: 20261021-211916-mf1-notas
- Persona integradora y confirmación del equipo: A fixture; acuerdo simulado
- Rama / checkout de integración: main / /tmp/factory-colaboracion-40csidqk/C6/producto
- Base completa: ac441878872027df2e658734771b8916f50443fd
- Entregas en orden (responsable, rama y commit completo): base A ac441878872027df2e658734771b8916f50443fd; entrega B 9ba03686d4905450599b1d3924d57a6aa20562db
- Dependencias e interfaces verificadas: aporte-b.txt independiente del ejemplo
- Paquetes, informes y triage (rutas y hashes por entrega): estado-revisado.json y estado-renovado.json; hashes en resultado.json
- Conflictos y decisión humana (o ninguno): ninguno
- Commit del candidato resultante: 5bdce09aeb7ee102b6499c36b7b41895a933e4bb
- Pruebas/sensor del candidato (comandos, resultado, artefactos y hashes): unittest y sensor de notas; comandos en ejecucion.json
- Gates obsoletos y renovaciones necesarias: revisión y juicio renovados después del merge
- Revisión del candidato y decisión humana: fixture; sin decisión humana real
- Oracle (requisitos, medidas, hechos, veredicto y límites): fixture verde; hechos sha256=82f6828218451de26d61633fc2197fd8ad5aaac1b343ae0766777746b7001916
- Pendientes de cierre: confirmación humana de cierre; no se cierra en este caso
- Confirmación humana de cierre (o pendiente): pendiente
- Commit que archiva el cierre (o pendiente): pendiente

Integrar una entrega por vez. Preservar estados divergentes antes de conciliarlos; nunca elegir el verde más avanzado. Un merge limpio requiere pruebas de compatibilidad. Distinguir el commit juzgado del commit posterior que archiva registros.
