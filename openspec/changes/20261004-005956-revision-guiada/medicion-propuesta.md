# Mapeo aplicado con límites explícitos

Los siete requisitos se importaron mediante Factory y ahora tienen medidas asociadas, conservando `sin_medir` para los límites de cobertura. Se aplicó el mapeo propuesto con `fabrica.py medir`, tras la respuesta del usuario «Bien, sigamos entonces.» al paso pendiente de elegir medidas y revisar. Se interpreta como continuación con el mapeo presentado; no como aprobación de revisión ni confirmación de cierre.

Todas las reglas están bajo `factory_revision_guiada`. Cada requisito se asoció a la medida de su mismo sufijo y a `factory_revision_guiada.corrida_completa`.

| Requisito (sufijo del ID importado) | Casos del sensor | Cantidad |
| --- | --- | --- |
| preparar_documentos_pendientes_sin_aprobar | G1 | 4 |
| validar_informe_guiado_y_su_alcance_declarado | G2 y G3 | 4 |
| derivar_pendientes_de_decisiones_separadas | G4 | 2 |
| registrar_confirmacion_humana_informada | G5 | 3 |
| conservar_evidencia_y_comprobar_vigencia | G6 | 3 |
| mantener_formato_libre_con_declaracion_explicita | G7 | 1 |
| explicar_y_verificar_los_limites_del_recorrido | G8 | 1 |

`tools/verify_review_guided.py` enumera los 18 nombres exactos de pruebas, exige que ocurran una sola vez y pasen, y también requiere que la suite completa no falle y las fuentes permanezcan estables. El conteo de una regla no identifica los casos por sí mismo: esa comprobación corresponde al sensor, cuyo código y suficiencia debe evaluar quien revisa.

Los límites conservados con `--sin-medir` son: casos seleccionados en Linux, sin prueba de calidad del análisis ni autenticación/competencia de los actores. Para el recorrido se agrega claridad para principiantes pendiente de observación humana. No convertir la ejecución fixture en decisión humana ni en aprobación de cierre.

La cobertura debe reevaluarse con los hechos del sensor y estas asociaciones. Un resultado favorable de las medidas sólo cubre los casos declarados: los siete requisitos mantienen cobertura parcial y no habilitan por sí solos el cierre de Factory.
