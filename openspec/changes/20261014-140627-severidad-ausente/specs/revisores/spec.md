# Capability: revisores

## MODIFIED Requirements

### Requirement: el corte de vueltas sigue la severidad
Tipo: funcional
Después de guardar un informe, `pedir-revision` SHALL mostrar cuántos hallazgos trae por severidad. Si entre los informes del candidato vigente no queda ningún hallazgo de severidad media o alta sin un riesgo aceptado que coincida, SHALL decir que no hace falta otra vuelta y que los bajos los decide una persona en `revisar`; si queda alguno, SHALL pedir corregirlo y pedir otra vuelta. `estado` SHALL sugerir el mismo próximo paso. Un informe con un hallazgo sin severidad o con una desconocida SHALL NOT guardarse; uno guardado que la pierde SHALL NOT usarse para decidir la vuelta, y `estado` SHALL avisar por qué.

#### Scenario: sólo quedan bajos
- GIVEN un candidato cuyos informes traen sólo hallazgos bajos
- WHEN termina pedir-revision
- THEN la salida cuenta los bajos y sugiere revisar en vez de otra vuelta, y estado sugiere revisar

#### Scenario: queda uno medio
- GIVEN un candidato con un informe que trae un hallazgo medio y otro con sólo bajos
- WHEN termina pedir-revision
- THEN la salida pide corregir el hallazgo medio y pedir otra vuelta, y estado sugiere lo mismo

#### Scenario: un informe sin severidad no se guarda
- GIVEN un revisor que deja un hallazgo sin severidad, o con una que no existe
- WHEN termina pedir-revision
- THEN falla diciendo que Clue rechazó el informe, y revision/ no cambia

#### Scenario: un informe guardado que pierde la severidad
- GIVEN un informe guardado con un hallazgo medio, editado después para quitarle la severidad
- WHEN la persona pide estado
- THEN ese informe no se usa para decidir la vuelta y el aviso dice que no pasa la validación de Clue
