# Capability: revisores

## ADDED Requirements

### Requirement: estado ofrece revisar cuando quedan hallazgos medios
Tipo: funcional
Con hallazgos medios o más sin aceptar en el candidato vigente, `estado` SHALL mostrar, además de corregir y pedir otra vuelta, que se pueden aceptar como riesgo o descartar con motivo con `oracle-factory revisar ID`; en una terminal, su menú SHALL ofrecer ejecutar ese comando; `estado --json` SHALL listarlo en `alternativas`, y `pedir-revision` SHALL decirlo al guardar un informe que deja medios sin aceptar. Sin medios pendientes no SHALL haber alternativa.

#### Scenario: quedan hallazgos medios sin aceptar
- GIVEN un candidato con un informe guardado que trae un hallazgo medio sin aceptar
- WHEN la persona pide estado, en texto y en JSON
- THEN el próximo paso sigue siendo corregir y pedir otra vuelta, y la alternativa es oracle-factory revisar ID

#### Scenario: el menú de estado ofrece revisar
- GIVEN ese mismo candidato, en una terminal
- WHEN la persona elige ejecutar la alternativa en el menú de estado
- THEN se abre revisar

#### Scenario: pedir-revision lo dice
- GIVEN un candidato
- WHEN pedir-revision guarda un informe con un hallazgo medio
- THEN dice que se puede corregir y pedir otra vuelta, o aceptar o descartar con oracle-factory revisar ID

#### Scenario: sin hallazgos medios no hay alternativa
- GIVEN un candidato cuyos informes sólo traen hallazgos bajos
- WHEN la persona pide estado
- THEN el próximo paso es oracle-factory revisar ID y no hay alternativas
