---
generado: oracle-factory kb
id: "flujo_c281f4f7154afdb2f.agentes_en_el_repo_mantiene_una_guia_versionada"
vigente: true
---

# agentes en el repo mantiene una guia versionada

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `flujo_c281f4f7154afdb2f.agentes_en_el_repo_mantiene_una_guia_versionada`
- Vigente: sí
- Cambio: [[cambios/20261112-121837-6bu-pmr]]
- Veredicto: cumple
- Medidas: `factory_preparar_migracion.agentes_en_el_repo_mantiene_una_guia_versionada`, `factory_preparar_migracion.corrida_completa`
- Fuente: openspec/changes/20261112-121837-6bu-pmr/specs/flujo/spec.md#agentes_en_el_repo_mantiene_una_guia_versionada

Tipo: funcional El sistema DEBE, con el producto conectado a un almacén, hacer que `agentes --en-el-repo` (sólo una persona) escriba el bloque generado en el `AGENTS.md` del producto y deje un `CLAUDE.md` que lo incluya, aunque el producto ya los versione, sin agregarlos a las exclusiones de Git y sin tocar lo que el archivo tiene fuera del bloque; sin `--en-el-repo`, `agentes` DEBE seguir negándose a tocar una guía versionada; y `agentes --verificar` DEBE decir si la guía del producto, versionada o no, está al día.
