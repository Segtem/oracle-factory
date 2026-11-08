# El verificador respeta «Pruebas: no aplica»

## Por qué

Una spec puede declarar, en la cabecera de un requisito, «Pruebas: no aplica — motivo» (la práctica de `docs/tests.md`): ese requisito no se puede probar con un test y la spec lo dice con su motivo. Pero `tools/verificar_cambio.py`, que deriva el contrato de la evidencia, ignora esa línea: exige casos para todos los requisitos y se niega a producir la evidencia. Quien declara la excepción con motivo queda sin la herramienta, o tiene que inventar una prueba que no prueba nada.

## Qué cambia

- El verificador lee las excepciones de la spec con el mismo lector que usan `aprobar-spec` e `importar` (`oracle_factory/pruebas.py`).
- Un requisito exceptuado no necesita casos, no entra en los hechos y no recibe catálogo de medida; la corrida completa cuenta sólo los casos de los demás. La numeración de los casos no cambia: `test_<letras><n>_…` sigue siendo el requisito `n` de la spec, exceptuado o no.
- Un caso que nombra un requisito exceptuado se rechaza: la spec y las pruebas se contradicen.
- Una línea «Pruebas:» mal escrita (sin motivo, repetida, otra cosa que «no aplica») se rechaza con el mismo mensaje que da `aprobar-spec`, en vez de ignorarla.
- `docs/tests.md` dice cómo se comporta el verificador con las excepciones.

## Fuera de alcance

- Medir el requisito exceptuado: queda sin medida de este verificador; la persona decide con qué otra medida lo cubre (o lo deja «sin medir», que `estado` avisa).
- Cambiar el lector de excepciones o lo que hacen `estado`, `aprobar-spec` e `importar`.

## Decisiones humanas

Ninguna abierta: aprobar la spec es la decisión de la persona. Anotado para quien revise: con todos los requisitos exceptuados el verificador sigue fallando («el módulo no tiene ningún caso»), porque no habría evidencia que producir.
