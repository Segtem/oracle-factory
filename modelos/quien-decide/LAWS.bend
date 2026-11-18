import Base
import ./quien.bend as Q

# Las escribe una persona; el agente no las toca.

# En modo confirmación, un agente nunca decide: a lo sumo propone.
law confirmacion_el_agente_no_decide:
  for t: Q.Tipo
  for d: Q.Decision
  {Q.es_decide(Q.puede(Q.Agente{}, Q.Confirmacion{}, t, d)) == False{} : Bool}

# Aprobar el sensor es de una persona en cualquier modo.
law el_sensor_lo_aprueba_una_persona:
  for m: Q.Modo
  for t: Q.Tipo
  {Q.puede(Q.Agente{}, m, t, Q.AprobarSensor{}) == Q.NoPuede{} : Q.Resultado}

# Ningún cierre lo decide un agente, salvo en modo autónomo.
law el_cierre_no_es_del_agente_fuera_de_autonomo:
  for t: Q.Tipo
  {Q.puede(Q.Agente{}, Q.Confirmacion{}, t, Q.Cierre{}) == Q.NoPuede{} : Q.Resultado}

# Para toda secuencia de pasos, en confirmación no queda ninguna decisión a nombre de un agente.
law en_confirmacion_ningun_registro_lo_decide_un_agente:
  for pasos: List<Q.Paso>
  {Q.decididas_por_agente(Q.Confirmacion{}, pasos) == 0n : Nat}

# El contador cuenta: en autónomo, un agente que aprueba una spec queda registrado (sin esto, la ley anterior podría ser vacía).
law en_autonomo_el_registro_cuenta_al_agente:
  {Q.decididas_por_agente(Q.Autonomo{}, [Q.Paso{Q.Agente{}, Q.Func{}, Q.Spec{}}]) == 1n : Nat}

# En modo funcional, un agente no decide nada de un requisito funcional.
law en_funcional_el_agente_no_decide_lo_funcional:
  for d: Q.Decision
  {Q.es_decide(Q.puede(Q.Agente{}, Q.Funcional{}, Q.Func{}, d)) == False{} : Bool}

# Una persona, desde su terminal, siempre decide: en cualquier modo, tipo y decisión.
law una_persona_siempre_decide:
  for m: Q.Modo
  for t: Q.Tipo
  for d: Q.Decision
  {Q.puede(Q.Persona{}, m, t, d) == Q.Decide{} : Q.Resultado}
