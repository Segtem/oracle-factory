---
generado: oracle-factory kb
id: "estructura_c01f2e6fb0af5aed6.el_proyecto_oracle_puede_estar_en_una_carpeta"
vigente: true
---

# el proyecto oracle puede estar en una carpeta

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `estructura_c01f2e6fb0af5aed6.el_proyecto_oracle_puede_estar_en_una_carpeta`
- Vigente: sí
- Cambio: [[cambios/20261015-155346-oracle-en-carpeta]]
- Veredicto: cumple
- Medidas: `factory_carpeta.el_proyecto_oracle_puede_estar_en_una_carpeta`, `factory_carpeta.corrida_completa`
- Fuente: openspec/changes/20261015-155346-oracle-en-carpeta/specs/estructura/spec.md#el proyecto Oracle puede estar en una carpeta

Tipo: funcional Con `\"oracle\": \"CARPETA\"` en `.factory/config.json`, Factory SHALL usar esa carpeta como proyecto Oracle: importar los requisitos en `CARPETA/requisitos/`, medirlos, juzgarlos y quitarlos al abandonar desde ahí, y correr Oracle con ese proyecto; `donde` y `buscar` SHALL nombrar los requisitos en esa carpeta. Sin la clave, el proyecto Oracle SHALL seguir siendo la raíz. Una carpeta absoluta, que sale del proyecto o sin `oracle.json` SHALL rechazarse con la causa.
