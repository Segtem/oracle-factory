# Design

- Una función por objeto (`datos_estado`, `datos_donde` y `datos_resumen`) arma un `dict` con lo mismo que hoy imprime el texto. Con `--json` se imprime con `json.dumps(..., ensure_ascii=False, indent=2, sort_keys=True)`, así el orden no depende de la implementación. El texto no se toca: sigue saliendo de `mostrar`, `comando_donde` y `resumen.generar`.
- El resumen en JSON reusa los mismos datos que `texto_resumen` ya junta (índices, registros, medidas, abiertos, revisiones, sin registro); se separa esa recolección en una función que usan los dos.
- La vigencia de la revisión y del juicio usa `mismo_producto` con el contexto registrado, igual que `pendientes_actuales`; el commit al que se refieren es el `head` de su contexto.
- El candidato vigente es `candidato_vigente(ID)`, el mismo que usan `ruta`, `pedir-revision` y `juzgar`.
- Con `--json`, `estado` no llama a `ofrecer_siguiente`. Los avisos que hoy van a stderr siguen yendo ahí.
