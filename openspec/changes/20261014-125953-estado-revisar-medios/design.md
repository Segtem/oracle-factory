# Design

- `pasos(ID)` devuelve el próximo paso seguido de sus alternativas; `proximo_paso` es el primero, así sus usos no cambian. Sólo la rama de hallazgos medios devuelve una alternativa (`oracle-factory revisar ID`), con las mismas condiciones que ya decidían ese paso.
- `estado` en texto imprime «También: …» debajo del próximo paso; `ofrecer_siguiente` ofrece ejecutar cada paso que sea un comando completo, y «Salir». `estado --json` (esquema `oracle-factory.estado/1`) suma la clave `alternativas`: agregar una clave no rompe a quien lee el esquema.
