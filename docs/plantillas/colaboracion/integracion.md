# Integración de entregas

- Cambio(s), IDs completos: {{tareas}}
- Persona integradora y confirmación del equipo: {{integrador}}
- Rama / checkout de integración: {{ubicacion}}
- Base completa: {{base}}
- Entregas en orden (responsable, rama y commit completo): {{entregas}}
- Dependencias e interfaces verificadas: {{dependencias}}
- Paquetes, informes y triage (rutas y hashes por entrega): {{revisiones}}
- Conflictos y decisión humana (o ninguno): {{conflictos}}
- Commit del candidato resultante: {{candidato}}
- Pruebas/sensor del candidato (comandos, resultado, artefactos y hashes): {{pruebas}}
- Gates obsoletos y renovaciones necesarias: {{renovaciones}}
- Revisión del candidato y decisión humana: {{decision}}
- Oracle (requisitos, medidas, hechos, veredicto y límites): {{oracle}}
- Pendientes de cierre: {{pendientes}}
- Confirmación humana de cierre (o pendiente): {{cierre}}
- Commit que archiva el cierre (o pendiente): {{commit_cierre}}

Integrar una entrega por vez. Preservar estados divergentes antes de conciliarlos; nunca elegir el verde más avanzado. Un merge limpio requiere pruebas de compatibilidad. Distinguir el commit juzgado del commit posterior que archiva registros.
