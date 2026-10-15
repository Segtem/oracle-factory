# Capability: modos

## ADDED Requirements

### Requirement: una decisión de medidas deja de valer si cambia el catálogo
Tipo: funcional
Una decisión de medidas SHALL guardar la huella del archivo de cada medida que el requisito nombra. Si alguno cambia o desaparece del catálogo efectivo, la decisión SHALL dejar de valer: `estado` SHALL mostrarla pendiente nombrando la medida y su archivo, y `juzgar` SHALL NOT usarla. Volver a decidir con las mismas medidas SHALL registrar una decisión nueva. Una decisión sin esa huella, tomada antes de este cambio, SHALL seguir valiendo.

#### Scenario: cambia el catálogo de una medida confirmada
- GIVEN un requisito con medidas confirmadas por una persona
- WHEN cambia el alcance en el archivo de una de sus medidas
- THEN estado muestra pendiente esa decisión con el nombre de la medida y su archivo, y juzgar la rechaza

#### Scenario: volver a decidir con las mismas medidas
- GIVEN esa decisión que dejó de valer
- WHEN una persona vuelve a elegir las mismas medidas con medir
- THEN queda registrada una decisión nueva y el pendiente desaparece

#### Scenario: una decisión anterior sin huella de catálogos
- GIVEN una decisión registrada sin la huella de los catálogos
- WHEN cambia el archivo de una de sus medidas
- THEN la decisión sigue valiendo

### Requirement: una propuesta de medidas no se confirma si cambió el catálogo
Tipo: funcional
Una propuesta de medidas de un agente SHALL guardar la misma huella. Si un catálogo cambia antes de que una persona la confirme, `medir ID --confirmar` SHALL NOT confirmarla tal cual y SHALL avisar que cambió.

#### Scenario: el catálogo cambia entre la propuesta y la confirmación
- GIVEN medidas propuestas por un agente en modo confirmacion
- WHEN cambia el archivo de una de esas medidas y una persona corre medir --confirmar
- THEN la propuesta no se confirma y el aviso dice que cambió
