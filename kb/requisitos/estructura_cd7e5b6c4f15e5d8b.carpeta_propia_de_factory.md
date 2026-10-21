---
generado: oracle-factory kb
id: "estructura_cd7e5b6c4f15e5d8b.carpeta_propia_de_factory"
vigente: true
---

# carpeta propia de factory

> Generado por `oracle-factory kb` desde el registro de Factory: no se edita a mano.

- Id: `estructura_cd7e5b6c4f15e5d8b.carpeta_propia_de_factory`
- Vigente: sí
- Cambio: [[cambios/20261005-132144-jerarquia-de]]
- Veredicto: cumple
- Medidas: `factory_estructura.carpeta_propia_de_factory`, `factory_estructura.corrida_completa`
- Fuente: openspec/changes/20261005-132144-jerarquia-de/specs/estructura/spec.md#carpeta propia de Factory

Tipo: funcional `init` SHALL crear `.factory/` en la raíz del proyecto con `cambios/` y `local/` y dejar en ella un archivo versionado que la explique (Git no versiona carpetas vacías), SHALL agregar `.factory/local/` al `.gitignore` sin sobrescribir lo existente, SHALL rechazar con un mensaje claro y antes de crear nada un `.factory` que no sea una carpeta, y SHALL avisar cuando la carpeta está dentro de otro proyecto Factory.
