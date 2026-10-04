# Integración de entregas

- Cambio(s), IDs completos: 20261004-123603-fixture
- Persona integradora y confirmación del equipo: A fixture; acuerdo simulado
- Rama / checkout de integración: main / /tmp/factory-colaboracion-xamug3em/C6/producto
- Base completa: 5e6d3d2e19ac50479548ed8676c494ec18f1c61e
- Entregas en orden (responsable, rama y commit completo): base A 5e6d3d2e19ac50479548ed8676c494ec18f1c61e; entrega B 7d0dc61f3374d84f44887aa06f3e88e128538a29
- Dependencias e interfaces verificadas: aporte-b.txt independiente del ejemplo
- Paquetes, informes y triage (rutas y hashes por entrega): estado-revisado.json y estado-renovado.json; hashes en resultado.json
- Conflictos y decisión humana (o ninguno): ninguno
- Commit del candidato resultante: ec0819963c3f2faeb53511419264fe1d3a82e188
- Pruebas/sensor del candidato (comandos, resultado, artefactos y hashes): unittest y sensor de notas; comandos en ejecucion.json
- Gates obsoletos y renovaciones necesarias: revisión y juicio renovados después del merge
- Revisión del candidato y decisión humana: fixture; sin decisión humana real
- Oracle (requisitos, medidas, hechos, veredicto y límites): fixture verde; hechos sha256=82f6828218451de26d61633fc2197fd8ad5aaac1b343ae0766777746b7001916
- Pendientes de cierre: confirmación humana de cierre; no se cierra en este caso
- Confirmación humana de cierre (o pendiente): pendiente
- Commit que archiva el cierre (o pendiente): pendiente

Integrar una entrega por vez. Preservar estados divergentes antes de conciliarlos; nunca elegir el verde más avanzado. Un merge limpio requiere pruebas de compatibilidad. Distinguir el commit juzgado del commit posterior que archiva registros.
