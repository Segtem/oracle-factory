---
generado: oracle-factory kb
id: "flujo_c5b6a893e70e9eba0.conectar_una_url_clona_el_almacen_en_una_carpeta_del_usuario"
vigente: true
---

# conectar una url clona el almacen en una carpeta del usuario

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `flujo_c5b6a893e70e9eba0.conectar_una_url_clona_el_almacen_en_una_carpeta_del_usuario`
- Vigente: sí
- Cambio: [[cambios/20261111-135546-t8q-almacen-sincronizar]]
- Veredicto: sin juicio
- Medidas: `factory_almacen_sincronizar.conectar_una_url_clona_el_almacen_en_una_carpeta_del_usuario`, `factory_almacen_sincronizar.corrida_completa`
- Fuente: openspec/changes/20261111-135546-t8q-almacen-sincronizar/specs/flujo/spec.md#conectar_una_url_clona_el_almacen_en_una_carpeta_del_usuario

Tipo: funcional El sistema DEBE, con `conectar URL` (una URL de Git, no una carpeta) desde un producto, clonar el almacén en `$XDG_DATA_HOME/oracle-factory/almacenes/NOMBRE` (o `~/.local/share/oracle-factory/almacenes/NOMBRE`), donde NOMBRE sale del último tramo de la URL sin `.git`, y conectarlo como hace `conectar RUTA`; si esa carpeta ya existe y es un clon de la misma URL, DEBE reusarla sin clonar de nuevo; si existe y es otra cosa, DEBE negarse sin tocar nada; un clon que falla DEBE dejar el producto sin conectar y sin carpetas a medias; y DEBE seguir siendo sólo de una persona.
