import Base

# Un modelo chico de la tabla «Las decisiones, según el modo de trabajo» de AGENTS.md de Oracle Factory.
# No es el código de Factory (que es Python): es la regla, escrita para poder probarla.

type Actor is Data:
  Persona{}
  Agente{}

type Modo is Data:
  Autonomo{}
  Funcional{}
  Confirmacion{}

type Tipo is Data:
  Func{}
  NoFunc{}

type Decision is Data:
  Spec{}
  Medidas{}
  Revision{}
  Cierre{}
  AprobarSensor{}

type Resultado is Data:
  Decide{}
  Propone{}
  NoPuede{}

# Qué pasa cuando un agente pide una decisión, según el modo y el tipo de requisito.
def del_agente(m: Modo, t: Tipo, d: Decision) -> Resultado:
  match m t d:
    case _ _ AprobarSensor{}:
      NoPuede{}
    case Autonomo{} _ _:
      Decide{}
    case Funcional{} _ Cierre{}:
      NoPuede{}
    case Funcional{} Func{} _:
      NoPuede{}
    case Funcional{} NoFunc{} _:
      Decide{}
    case Confirmacion{} _ Cierre{}:
      NoPuede{}
    case Confirmacion{} _ _:
      Propone{}

# Una persona, desde su terminal, siempre decide.
def puede(a: Actor, m: Modo, t: Tipo, d: Decision) -> Resultado:
  match a:
    case Persona{}:
      Decide{}
    case Agente{}:
      del_agente(m, t, d)

def es_decide(r: Resultado) -> Bool:
  match r:
    case Decide{}:
      True{}
    case Propone{}:
      False{}
    case NoPuede{}:
      False{}

def es_agente(a: Actor) -> Bool:
  match a:
    case Persona{}:
      False{}
    case Agente{}:
      True{}

# Un paso del registro: quién pidió qué decisión, sobre qué tipo de requisito.
type Paso is Data:
  Paso{a: Actor, t: Tipo, d: Decision}

def sumar(b: Bool, n: Nat) -> Nat:
  match b:
    case True{}:
      1n+n
    case False{}:
      n

# Cuántas decisiones quedan registradas como tomadas por un agente al reproducir los pasos en un modo.
def decididas_por_agente(+m: Modo, pasos: List<Paso>) -> Nat:
  match pasos:
    case Nil{}:
      0n
    case Con{p, resto}:
      match p:
        case Paso{+a, t, d}:
          sumar(es_agente(a) && es_decide(puede(a, m, t, d)), decididas_por_agente(m, resto))

# Una fila de la tabla de AGENTS.md: lo que pasa cuando un agente pide cada decisión, en un modo y para un tipo de requisito.
type Fila is Data:
  Fila{spec: Resultado, medidas: Resultado, revision: Resultado, cierre: Resultado, sensor: Resultado}

def fila(+m: Modo, +t: Tipo) -> Fila:
  Fila{del_agente(m, t, Spec{}), del_agente(m, t, Medidas{}), del_agente(m, t, Revision{}), del_agente(m, t, Cierre{}), del_agente(m, t, AprobarSensor{})}
