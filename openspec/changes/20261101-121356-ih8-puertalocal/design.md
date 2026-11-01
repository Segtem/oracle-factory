# Diseño

- Un módulo nuevo, `oracle_factory/puerta.py`, con una lista de comprobaciones `(nombre, función)`; cada una devuelve problemas con texto. Las dos de esta entrega son `secretos` y `verificaciones`; las futuras (analizadores, `verificar` de CI) se agregan a la lista.
- Los commits del rango salen de `git log -p -U0 --no-color --format=commit:%H` (sin merges, que no agregan contenido propio), de modo que un secreto agregado y quitado después se ve. Las líneas y sus números salen de los encabezados `@@`.
- Los patrones buscan valores con forma de credencial; la asignación genérica pide un valor entre comillas de 16 o más caracteres sin espacios. El valor se tapa dejando los primeros caracteres.
- Las verificaciones se llaman en el proceso (`main(['agentes', '--verificar'])`, etc.) con la salida capturada.
- El hook pre-push sigue el patrón de `instalar_hook`: lleva la misma marca, no pisa uno ajeno, vive en la carpeta de hooks compartida por los worktrees. Lee de la entrada estándar las líneas que Git le pasa («ref local, sha local, ref remoto, sha remoto»): un borrado no se mira, una rama nueva se mira desde lo que ningún remoto tiene (`sha --not --remotes`), y una existente desde el sha remoto.
- A diferencia del hook de commits, que nunca impide nada, éste puede bloquear; pero si no encuentra el intérprete avisa y sale con éxito.
