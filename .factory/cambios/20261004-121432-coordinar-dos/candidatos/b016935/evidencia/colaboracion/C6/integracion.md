# Integración de entregas

- Cambio(s), IDs completos: 20261021-215948-oa9-notas
- Persona integradora y confirmación del equipo: A fixture; acuerdo simulado
- Rama / checkout de integración: main / /tmp/factory-colaboracion-odcpve1j/C6/producto
- Base completa: 1d204d4bbc115bef98162123855913a96e8e09e9
- Entregas en orden (responsable, rama y commit completo): base A 1d204d4bbc115bef98162123855913a96e8e09e9; entrega B c13dd1c3858b90652816742e5200819c0b305d54
- Dependencias e interfaces verificadas: aporte-b.txt independiente del ejemplo
- Paquetes, informes y triage (rutas y hashes por entrega): estado-revisado.json y estado-renovado.json; hashes en resultado.json
- Conflictos y decisión humana (o ninguno): ninguno
- Commit del candidato resultante: b6b9d9a8cbd7991f4ae4e7e28cd9053d43846f45
- Pruebas/sensor del candidato (comandos, resultado, artefactos y hashes): unittest y sensor de notas; comandos en ejecucion.json
- Gates obsoletos y renovaciones necesarias: revisión y juicio renovados después del merge
- Revisión del candidato y decisión humana: fixture; sin decisión humana real
- Oracle (requisitos, medidas, hechos, veredicto y límites): fixture verde; hechos sha256=82f6828218451de26d61633fc2197fd8ad5aaac1b343ae0766777746b7001916
- Pendientes de cierre: confirmación humana de cierre; no se cierra en este caso
- Confirmación humana de cierre (o pendiente): pendiente
- Commit que archiva el cierre (o pendiente): pendiente

Integrar una entrega por vez. Preservar estados divergentes antes de conciliarlos; nunca elegir el verde más avanzado. Un merge limpio requiere pruebas de compatibilidad. Distinguir el commit juzgado del commit posterior que archiva registros.
