# Capability: flujo

## ADDED Requirements

### Requirement: una spec de otra capacidad no se pierde en silencio
Tipo: funcional
`aprobar-spec` SHALL negarse, sin registrar nada, si el cambio tiene en `specs/` una spec de otra capacidad que la suya, y SHALL nombrar esas specs y decir que Factory importa sólo la de su capacidad.

#### Scenario: un cambio con dos specs
- GIVEN un cambio de la capacidad uno con specs/uno/spec.md y specs/dos/spec.md
- WHEN una persona corre aprobar-spec, y después de quitar specs/dos lo corre otra vez
- THEN la primera vez se niega nombrando specs/dos/spec.md y el registro no cambia, y la segunda aprueba

### Requirement: reimportar no deja requisitos huérfanos
Tipo: funcional
`importar` SHALL quitar de `requisitos/` los requisitos que una importación anterior del mismo cambio escribió y la nueva ya no trae, y SHALL NOT tocar los requisitos de otros cambios.

#### Scenario: una spec aprobada otra vez
- GIVEN un cambio con sus requisitos importados y otro cambio con los suyos
- WHEN se edita la spec del primero, se aprueba de nuevo y se importa
- THEN requisitos/ tiene los nuevos del primero, no los de su importación anterior, y los del otro cambio siguen igual

### Requirement: un requisito que quedó sin medir se avisa a tiempo
Tipo: funcional
`estado` (y `--json`) SHALL avisar, en cuanto un requisito tiene sus medidas decididas y su `.requisito` todavía dice `sin_medir`, cuál es y qué hacer; y el error de cobertura de `juzgar` SHALL nombrar esos requisitos.

#### Scenario: medidas confirmadas con la marca todavía puesta
- GIVEN un cambio con un requisito cuyas medidas se decidieron sin quitar sin_medir
- WHEN se pide estado y después juzgar
- THEN estado lo avisa con el requisito y cómo seguir, y juzgar se niega nombrándolo
