# Design

Notas para implementar después de la aceptación. No son parte del contrato.

- **Un solo punto de acceso.** Hoy `leer`, `guardar` y unas 15 llamadas escriben `carpeta / 'factory.json'`, `carpeta / 'review.md'` o `carpeta / 'oracle-veredicto.txt'`, donde `carpeta` es `openspec/changes/<ID>/`. Se agrega `estado_de(identificador)` que devuelve la carpeta del estado (`.factory/cambios/<ID>/` si existe su registro; la vieja si sólo existe ahí; la nueva para un cambio nuevo), y todas esas llamadas pasan por él. `carpeta` sigue siendo la del acuerdo.
- **Qué rutas se reescriben al migrar:** sólo valores de texto del registro que sean exactamente `openspec/changes/<ID>/review.md` u `.../oracle-veredicto.txt` (de ese mismo cambio), que pasan a `.factory/cambios/<ID>/…`. Los hashes de esos informes no cambian porque el contenido es el mismo. El resto del registro queda byte a byte.
- **Orden y recuperación:** por cada cambio se escribe primero el estado nuevo (reemplazo atómico), se comprueba que el contenido es el esperado y recién después se borra el viejo. Si al volver a correr existen los dos y son iguales (salvo las rutas reescritas), se borra el viejo; si difieren, se aborta ese cambio con un mensaje y no se pisa nada.
- **Huella del producto:** `contexto_producto()` ya omite `.factory/` y los tres archivos del estado en `openspec/changes/<ID>/`; la migración no cambia la huella. La configuración de la raíz sí es producto: si existe, moverla cambia la huella y `migrar` lo avisa antes.
- **Commit:** `migrar` no hace commit; deja los movimientos (borrado + alta) para que la persona los confirme.
- **Cuidado con `buscar` y `donde`:** `buscar` arma el mapa requisito → cambio leyendo los registros; debe leer los dos lugares. `donde` muestra la fila «estado» con la ruta real.
- **Verificación:** un arnés `tools/verify_estructura2.py` con catálogos propios; un verificador `--antes <ref>` que compara el `estado` de cada cambio contra un commit anterior a la migración (como en la limpieza de rutas).
