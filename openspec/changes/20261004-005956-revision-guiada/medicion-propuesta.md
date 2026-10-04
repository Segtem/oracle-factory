# Mapeo propuesto, pendiente de elección humana

Los siete requisitos se importaron mediante Factory y conservan `sin_medir`. Las reglas siguientes están preparadas y comprobadas con Oracle 0.38.1; todavía no se asociaron a los requisitos. Se consultó en la conversación si se desea aplicar este mapeo conservando los límites.

Todas las reglas están bajo `factory_revision_guiada`. Cada requisito se asociaría a la medida de su mismo sufijo y a `factory_revision_guiada.corrida_completa`.

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

Los límites propuestos para conservar con `--sin-medir` son: casos seleccionados en Linux, sin prueba de calidad del análisis ni autenticación/competencia de los actores. Para el recorrido se agrega claridad para principiantes pendiente de observación humana. No convertir la ejecución fixture en decisión humana ni en aprobación de cierre.

Las reglas pueden evaluarse con los hechos del sensor sin asociar todavía requisitos. Ese verde de reglas no es cobertura del cambio; Factory debe continuar mostrando requisitos sin medir hasta elegir el mapeo.
