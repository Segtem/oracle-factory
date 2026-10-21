# Design

- `.gitattributes` versionado: `.factory/cambios/*/factory.json merge=oracle-factory-registro` y, para lo generado,
  `.factory/resumen.md` y `kb/README.md`, `kb/cambios/*.md`, `kb/requisitos/*.md` con `merge=oracle-factory-generado`.
  `hooks` (y `init`) escribe en `.git/config` del clon los dos drivers, con el intérprete de Factory; sin el driver
  configurado, Git une como texto, como hoy.
- `oracle-factory unir-registro BASE NUESTRO SUYO RUTA` (el driver): eventos = los de los dos lados sin repetir (un evento es
  igual a otro si su JSON es igual), ordenados por `cuando` y, a igual `cuando`, por su JSON. Para cada otro campo: si sólo
  un lado lo cambió respecto de la base, ese; si los dos lo cambiaron igual, ese; si lo cambiaron distinto, queda el de un
  lado y el otro va en `pendientes_de_union` (campo, valor de cada rama), con un evento `union_con_decisiones`. Siempre
  escribe JSON válido y sale con 0.
- `estado` avisa cada `pendiente_de_union` con qué decidir; la decisión que corresponde (tomar, aprobar-spec, medir,
  revisar, juzgar) lo limpia al registrarse.
- `oracle-factory unir-generado ...` (el driver de lo generado): se queda con la versión de la rama que se integra y avisa
  que corre `resumen` y `kb` después; un hook `post-merge` (instalado por `hooks`) los rehace y deja el resultado para el
  commit.
