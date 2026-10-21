# Integración de entregas

- Cambio(s), IDs completos: 20261021-214827-s01-notas
- Persona integradora y confirmación del equipo: A fixture; acuerdo simulado
- Rama / checkout de integración: main / /tmp/factory-colaboracion-577l9t1b/C6/producto
- Base completa: 6ec7884b447441f96e8787f25279c5a67d9d17c6
- Entregas en orden (responsable, rama y commit completo): base A 6ec7884b447441f96e8787f25279c5a67d9d17c6; entrega B 3d2c1b27bd008100ec805e8b5cef03b9f265c63b
- Dependencias e interfaces verificadas: aporte-b.txt independiente del ejemplo
- Paquetes, informes y triage (rutas y hashes por entrega): estado-revisado.json y estado-renovado.json; hashes en resultado.json
- Conflictos y decisión humana (o ninguno): ninguno
- Commit del candidato resultante: 9a92cc0e0df2ff646a2db6ea56d88994d537e369
- Pruebas/sensor del candidato (comandos, resultado, artefactos y hashes): unittest y sensor de notas; comandos en ejecucion.json
- Gates obsoletos y renovaciones necesarias: revisión y juicio renovados después del merge
- Revisión del candidato y decisión humana: fixture; sin decisión humana real
- Oracle (requisitos, medidas, hechos, veredicto y límites): fixture verde; hechos sha256=82f6828218451de26d61633fc2197fd8ad5aaac1b343ae0766777746b7001916
- Pendientes de cierre: confirmación humana de cierre; no se cierra en este caso
- Confirmación humana de cierre (o pendiente): pendiente
- Commit que archiva el cierre (o pendiente): pendiente

Integrar una entrega por vez. Preservar estados divergentes antes de conciliarlos; nunca elegir el verde más avanzado. Un merge limpio requiere pruebas de compatibilidad. Distinguir el commit juzgado del commit posterior que archiva registros.
