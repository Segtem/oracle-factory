---
generado: oracle-factory kb
id: "estructura_cd7e5b6c4f15e5d8b.descubrir_la_raiz_del_proyecto"
vigente: true
---

# descubrir la raiz del proyecto

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `estructura_cd7e5b6c4f15e5d8b.descubrir_la_raiz_del_proyecto`
- Vigente: sí
- Cambio: [[cambios/20261005-132144-jerarquia-de]]
- Veredicto: cumple
- Medidas: `factory_estructura.descubrir_la_raiz_del_proyecto`, `factory_estructura.corrida_completa`
- Fuente: openspec/changes/20261005-132144-jerarquia-de/specs/estructura/spec.md#descubrir la raíz del proyecto

Tipo: funcional Los comandos SHALL buscar `.factory/` subiendo desde la carpeta actual hasta la raíz del sistema de archivos y usar la primera que encuentren; `--proyecto` SHALL tener prioridad y, sin `.factory/` en ningún ancestro, SHALL conservarse el comportamiento actual de usar la carpeta actual. Un proyecto Factory anterior sin `.factory/` (con `oracle.json` y `openspec/changes/`) SHALL ser una frontera: no hereda el proyecto de afuera. La carpeta personal del usuario y un enlace simbólico llamado `.factory` SHALL NOT contar como raíz. Cuando la raíz usada no es la carpeta actual, SHALL informarlo.
