import Base
import ./quien.bend as Q
import ./LAWS.bend as Laws

# Las escribe el agente; `bend PROOF.bend --verdict` dice si valen.

# Por casos: para cada tipo y cada decisión, el resultado de un agente en confirmación se calcula y no es Decide.
def Laws.confirmacion_el_agente_no_decide(t, d):
  match t d:
    case Q.Func{} Q.Spec{}:
      {==}
    case Q.Func{} Q.Medidas{}:
      {==}
    case Q.Func{} Q.Revision{}:
      {==}
    case Q.Func{} Q.Cierre{}:
      {==}
    case Q.Func{} Q.AprobarSensor{}:
      {==}
    case Q.NoFunc{} Q.Spec{}:
      {==}
    case Q.NoFunc{} Q.Medidas{}:
      {==}
    case Q.NoFunc{} Q.Revision{}:
      {==}
    case Q.NoFunc{} Q.Cierre{}:
      {==}
    case Q.NoFunc{} Q.AprobarSensor{}:
      {==}

def Laws.el_sensor_lo_aprueba_una_persona(m, t):
  match m t:
    case Q.Autonomo{} Q.Func{}:
      {==}
    case Q.Autonomo{} Q.NoFunc{}:
      {==}
    case Q.Funcional{} Q.Func{}:
      {==}
    case Q.Funcional{} Q.NoFunc{}:
      {==}
    case Q.Confirmacion{} Q.Func{}:
      {==}
    case Q.Confirmacion{} Q.NoFunc{}:
      {==}

def Laws.el_cierre_no_es_del_agente_fuera_de_autonomo(t):
  match t:
    case Q.Func{}:
      {==}
    case Q.NoFunc{}:
      {==}

# Por inducción sobre los pasos: el primero no suma (lo pidió una persona, o un agente que en confirmación no decide)
# y el resto es la hipótesis inductiva.
def Laws.en_confirmacion_ningun_registro_lo_decide_un_agente(pasos):
  match pasos:
    case Nil{}:
      {==}
    case Con{p, resto}:
      match p:
        case Q.Paso{a, t, d}:
          match a:
            case Q.Persona{}:
              Laws.en_confirmacion_ningun_registro_lo_decide_un_agente(resto)
            case Q.Agente{}:
              match t d:
                case Q.Func{} Q.Spec{}:
                  Laws.en_confirmacion_ningun_registro_lo_decide_un_agente(resto)
                case Q.Func{} Q.Medidas{}:
                  Laws.en_confirmacion_ningun_registro_lo_decide_un_agente(resto)
                case Q.Func{} Q.Revision{}:
                  Laws.en_confirmacion_ningun_registro_lo_decide_un_agente(resto)
                case Q.Func{} Q.Cierre{}:
                  Laws.en_confirmacion_ningun_registro_lo_decide_un_agente(resto)
                case Q.Func{} Q.AprobarSensor{}:
                  Laws.en_confirmacion_ningun_registro_lo_decide_un_agente(resto)
                case Q.NoFunc{} Q.Spec{}:
                  Laws.en_confirmacion_ningun_registro_lo_decide_un_agente(resto)
                case Q.NoFunc{} Q.Medidas{}:
                  Laws.en_confirmacion_ningun_registro_lo_decide_un_agente(resto)
                case Q.NoFunc{} Q.Revision{}:
                  Laws.en_confirmacion_ningun_registro_lo_decide_un_agente(resto)
                case Q.NoFunc{} Q.Cierre{}:
                  Laws.en_confirmacion_ningun_registro_lo_decide_un_agente(resto)
                case Q.NoFunc{} Q.AprobarSensor{}:
                  Laws.en_confirmacion_ningun_registro_lo_decide_un_agente(resto)

def Laws.en_autonomo_el_registro_cuenta_al_agente():
  {==}

def Laws.en_funcional_el_agente_no_decide_lo_funcional(d):
  match d:
    case Q.Spec{}:
      {==}
    case Q.Medidas{}:
      {==}
    case Q.Revision{}:
      {==}
    case Q.Cierre{}:
      {==}
    case Q.AprobarSensor{}:
      {==}

def Laws.una_persona_siempre_decide(m, t, d):
  {==}

def Laws.la_fila_de_autonomo(t):
  match t:
    case Q.Func{}:
      {==}
    case Q.NoFunc{}:
      {==}

def Laws.la_fila_de_funcional_para_lo_funcional():
  {==}

def Laws.la_fila_de_funcional_para_lo_no_funcional():
  {==}

def Laws.la_fila_de_confirmacion(t):
  match t:
    case Q.Func{}:
      {==}
    case Q.NoFunc{}:
      {==}
