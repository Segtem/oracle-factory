import Base
import ./autopilot.bend as Q

# Las revisa una persona (al aprobar la spec de leyes-autopilot); el agente no las toca. Las pruebas, en PROOF.bend, las escribe generar.py.

# Si el conductor actúa, corre sólo un comando mecánico; si frena, delega o termina, no trae comando.
law el_conductor_solo_corre_lo_mecanico:
  for s: Q.Sub
  for frenos: Bool
  for terminada: Bool
  for segundo: Bool
  for candidato: Bool
  for propuesta: Bool
  {Q.permitida(Q.decidir(frenos, terminada, s, segundo, candidato, propuesta)) == True{} : Bool}

# Con frenos, el conductor frena, sea cual sea el próximo paso.
law con_frenos_siempre_frena:
  for s: Q.Sub
  for terminada: Bool
  for segundo: Bool
  for candidato: Bool
  for propuesta: Bool
  {Q.accion_de(Q.decidir(True{}, terminada, s, segundo, candidato, propuesta)) == Q.Frenar{} : Q.Accion}

# Confirmar las medidas es de una persona: el conductor se lo pide.
law confirmar_las_medidas_es_de_una_persona:
  for terminada: Bool
  for segundo: Bool
  for candidato: Bool
  for propuesta: Bool
  {Q.decidir(False{}, terminada, Q.MedirConfirmar{}, segundo, candidato, propuesta) == Q.Salida{Q.PedirAPersona{}, Q.MedirConfirmar{}} : Q.Salida}

# «aprobar_spec» es una decisión de una persona: el conductor se la pide, con su comando.
law aprobar_spec_se_le_pide_a_una_persona:
  for terminada: Bool
  for segundo: Bool
  for candidato: Bool
  for propuesta: Bool
  {Q.decidir(False{}, terminada, Q.AprobarSpec{}, segundo, candidato, propuesta) == Q.Salida{Q.PedirAPersona{}, Q.AprobarSpec{}} : Q.Salida}

# «cerrar» es una decisión de una persona: el conductor se la pide, con su comando.
law cerrar_se_le_pide_a_una_persona:
  for terminada: Bool
  for segundo: Bool
  for candidato: Bool
  for propuesta: Bool
  {Q.decidir(False{}, terminada, Q.Cerrar{}, segundo, candidato, propuesta) == Q.Salida{Q.PedirAPersona{}, Q.Cerrar{}} : Q.Salida}

# «abandonar» es una decisión de una persona: el conductor se la pide, con su comando.
law abandonar_se_le_pide_a_una_persona:
  for terminada: Bool
  for segundo: Bool
  for candidato: Bool
  for propuesta: Bool
  {Q.decidir(False{}, terminada, Q.Abandonar{}, segundo, candidato, propuesta) == Q.Salida{Q.PedirAPersona{}, Q.Abandonar{}} : Q.Salida}

# «modo» es una decisión de una persona: el conductor se la pide, con su comando.
law modo_se_le_pide_a_una_persona:
  for terminada: Bool
  for segundo: Bool
  for candidato: Bool
  for propuesta: Bool
  {Q.decidir(False{}, terminada, Q.Modo{}, segundo, candidato, propuesta) == Q.Salida{Q.PedirAPersona{}, Q.Modo{}} : Q.Salida}

# «autonomia» es una decisión de una persona: el conductor se la pide, con su comando.
law autonomia_se_le_pide_a_una_persona:
  for terminada: Bool
  for segundo: Bool
  for candidato: Bool
  for propuesta: Bool
  {Q.decidir(False{}, terminada, Q.Autonomia{}, segundo, candidato, propuesta) == Q.Salida{Q.PedirAPersona{}, Q.Autonomia{}} : Q.Salida}

# «soltar» es una decisión de una persona: el conductor se la pide, con su comando.
law soltar_se_le_pide_a_una_persona:
  for terminada: Bool
  for segundo: Bool
  for candidato: Bool
  for propuesta: Bool
  {Q.decidir(False{}, terminada, Q.Soltar{}, segundo, candidato, propuesta) == Q.Salida{Q.PedirAPersona{}, Q.Soltar{}} : Q.Salida}

# «decidir_union» es una decisión de una persona: el conductor se la pide, con su comando.
law decidir_union_se_le_pide_a_una_persona:
  for terminada: Bool
  for segundo: Bool
  for candidato: Bool
  for propuesta: Bool
  {Q.decidir(False{}, terminada, Q.DecidirUnion{}, segundo, candidato, propuesta) == Q.Salida{Q.PedirAPersona{}, Q.DecidirUnion{}} : Q.Salida}

# «conectar» es una decisión de una persona: el conductor se la pide, con su comando.
law conectar_se_le_pide_a_una_persona:
  for terminada: Bool
  for segundo: Bool
  for candidato: Bool
  for propuesta: Bool
  {Q.decidir(False{}, terminada, Q.Conectar{}, segundo, candidato, propuesta) == Q.Salida{Q.PedirAPersona{}, Q.Conectar{}} : Q.Salida}

# «desconectar» es una decisión de una persona: el conductor se la pide, con su comando.
law desconectar_se_le_pide_a_una_persona:
  for terminada: Bool
  for segundo: Bool
  for candidato: Bool
  for propuesta: Bool
  {Q.decidir(False{}, terminada, Q.Desconectar{}, segundo, candidato, propuesta) == Q.Salida{Q.PedirAPersona{}, Q.Desconectar{}} : Q.Salida}

# Revisar es de una persona: sin un segundo revisor que falte y con la propuesta del agente lista, se le pide.
law revisar_se_le_pide_a_una_persona:
  for terminada: Bool
  {Q.decidir(False{}, terminada, Q.Revisar{}, False{}, True{}, True{}) == Q.Salida{Q.PedirAPersona{}, Q.Revisar{}} : Q.Salida}

# Sin la propuesta del agente sobre el candidato, antes de pedírsela a una persona el agente la prepara.
law revisar_sin_propuesta_la_prepara_el_agente:
  for terminada: Bool
  {Q.decidir(False{}, terminada, Q.Revisar{}, False{}, True{}, False{}) == Q.Salida{Q.DelegarAlAgente{}, Q.SinPaso{}} : Q.Salida}

# En el camino completo, si falta un segundo revisor, el conductor lo pide antes de la decisión de una persona.
law revisar_pide_antes_el_segundo_revisor:
  for terminada: Bool
  for candidato: Bool
  for propuesta: Bool
  {Q.decidir(False{}, terminada, Q.Revisar{}, True{}, candidato, propuesta) == Q.Salida{Q.Actuar{}, Q.PedirRevision{}} : Q.Salida}

# El trabajo creativo (corregir, commitear, resolver) se le delega al agente, sin comando.
law la_prosa_se_delega:
  for terminada: Bool
  for segundo: Bool
  for candidato: Bool
  for propuesta: Bool
  {Q.decidir(False{}, terminada, Q.Prosa{}, segundo, candidato, propuesta) == Q.Salida{Q.DelegarAlAgente{}, Q.SinPaso{}} : Q.Salida}

# Un comando mecánico con lo que necesita lo corre el agente.
law importar_lo_corre_el_agente:
  for terminada: Bool
  for segundo: Bool
  for candidato: Bool
  for propuesta: Bool
  {Q.decidir(False{}, terminada, Q.Importar{}, segundo, candidato, propuesta) == Q.Salida{Q.Actuar{}, Q.Importar{}} : Q.Salida}

# Lo que el conductor no conoce (aprobar el sensor, producir la evidencia, otro comando, algo ilegible) lo frena.
law lo_que_no_conoce_lo_frena:
  for terminada: Bool
  for segundo: Bool
  for candidato: Bool
  for propuesta: Bool
  {Q.accion_de(Q.decidir(False{}, terminada, Q.AprobarSensor{}, segundo, candidato, propuesta)) == Q.Frenar{} : Q.Accion}

# Ninguna decisión de una persona, ni producir la evidencia, es un comando mecánico (que el agente corre).
law lo_de_persona_no_es_mecanico:
  {(Q.es_mecanico(Q.AprobarSpec{}) || Q.es_mecanico(Q.Cerrar{}) || Q.es_mecanico(Q.Abandonar{}) || Q.es_mecanico(Q.Modo{}) || Q.es_mecanico(Q.Autonomia{}) || Q.es_mecanico(Q.Soltar{}) || Q.es_mecanico(Q.DecidirUnion{}) || Q.es_mecanico(Q.Conectar{}) || Q.es_mecanico(Q.Desconectar{}) || Q.es_mecanico(Q.Revisar{}) || Q.es_mecanico(Q.MedirConfirmar{}) || Q.es_mecanico(Q.AprobarSensor{}) || Q.es_mecanico(Q.Evidencia{})) == False{} : Bool}

# Sin próximo paso, sólo termina un cambio terminado (cerrado o abandonado); si no, frena.
law sin_paso_termina_solo_lo_terminado:
  for segundo: Bool
  for candidato: Bool
  for propuesta: Bool
  {Q.accion_de(Q.decidir(False{}, False{}, Q.SinPaso{}, segundo, candidato, propuesta)) == Q.Frenar{} : Q.Accion}

law terminado_y_sin_paso_termina:
  for segundo: Bool
  for candidato: Bool
  for propuesta: Bool
  {Q.accion_de(Q.decidir(False{}, True{}, Q.SinPaso{}, segundo, candidato, propuesta)) == Q.Terminado{} : Q.Accion}

# Sin candidato no se pide ni se prepara una revisión: primero se construye (lo delega al agente, sin comando).
law sin_candidato_primero_se_construye:
  for terminada: Bool
  for segundo: Bool
  for propuesta: Bool
  {Q.decidir(False{}, terminada, Q.PedirRevision{}, segundo, False{}, propuesta) == Q.Salida{Q.DelegarAlAgente{}, Q.SinPaso{}} : Q.Salida}
