import Base

# Un modelo de `oracle_factory.autopilot.decidir`: qué hace el conductor con el próximo paso de un cambio.
# El próximo paso llega ya clasificado (el subcomando que el parser real de Factory reconoce, o prosa, o algo ilegible).

type Sub is Data:
  SinPaso{}
  Prosa{}
  Ilegible{}
  AprobarSpec{}
  Revisar{}
  Cerrar{}
  Abandonar{}
  Modo{}
  Autonomia{}
  Soltar{}
  DecidirUnion{}
  Conectar{}
  Desconectar{}
  Importar{}
  Juzgar{}
  PedirRevision{}
  RevisionPreparar{}
  Tomar{}
  Mensaje{}
  Sincronizar{}
  MedirConfirmar{}
  MedirListar{}
  MedirOtro{}
  AprobarSensor{}
  Evidencia{}
  Otro{}

type Accion is Data:
  Terminado{}
  Frenar{}
  PedirAPersona{}
  DelegarAlAgente{}
  Actuar{}

# Lo que decide el conductor: la acción y el subcomando del comando que trae (SinPaso si no trae ninguno).
type Salida is Data:
  Salida{accion: Accion, sub: Sub}

def frena() -> Salida:
  Salida{Frenar{}, SinPaso{}}

def delega() -> Salida:
  Salida{DelegarAlAgente{}, SinPaso{}}

def con_revisar(segundo: Bool, candidato: Bool, propuesta: Bool) -> Salida:
  match segundo candidato propuesta:
    case True{} _ _:
      Salida{Actuar{}, PedirRevision{}}
    case False{} True{} True{}:
      Salida{PedirAPersona{}, Revisar{}}
    case False{} True{} False{}:
      delega()
    case False{} False{} _:
      Salida{PedirAPersona{}, Revisar{}}

def sin_candidato_construye(candidato: Bool, +s: Sub) -> Salida:
  match candidato:
    case True{}:
      Salida{Actuar{}, s}
    case False{}:
      delega()

def sin_frenos(s: Sub, cerrada: Bool, segundo: Bool, candidato: Bool, propuesta: Bool) -> Salida:
  match s:
    case SinPaso{}:
      match cerrada:
        case True{}:
          Salida{Terminado{}, SinPaso{}}
        case False{}:
          frena()
    case Prosa{}:
      delega()
    case Ilegible{}:
      frena()
    case AprobarSpec{}:
      Salida{PedirAPersona{}, AprobarSpec{}}
    case Revisar{}:
      con_revisar(segundo, candidato, propuesta)
    case Cerrar{}:
      Salida{PedirAPersona{}, Cerrar{}}
    case Abandonar{}:
      Salida{PedirAPersona{}, Abandonar{}}
    case Modo{}:
      Salida{PedirAPersona{}, Modo{}}
    case Autonomia{}:
      Salida{PedirAPersona{}, Autonomia{}}
    case Soltar{}:
      Salida{PedirAPersona{}, Soltar{}}
    case DecidirUnion{}:
      Salida{PedirAPersona{}, DecidirUnion{}}
    case Conectar{}:
      Salida{PedirAPersona{}, Conectar{}}
    case Desconectar{}:
      Salida{PedirAPersona{}, Desconectar{}}
    case Importar{}:
      Salida{Actuar{}, Importar{}}
    case Juzgar{}:
      Salida{Actuar{}, Juzgar{}}
    case PedirRevision{}:
      sin_candidato_construye(candidato, PedirRevision{})
    case RevisionPreparar{}:
      sin_candidato_construye(candidato, RevisionPreparar{})
    case Tomar{}:
      Salida{Actuar{}, Tomar{}}
    case Mensaje{}:
      Salida{Actuar{}, Mensaje{}}
    case Sincronizar{}:
      Salida{Actuar{}, Sincronizar{}}
    case MedirConfirmar{}:
      Salida{PedirAPersona{}, MedirConfirmar{}}
    case MedirListar{}:
      delega()
    case MedirOtro{}:
      frena()
    case AprobarSensor{}:
      frena()
    case Evidencia{}:
      frena()
    case Otro{}:
      frena()

def decidir(frenos: Bool, cerrada: Bool, s: Sub, segundo: Bool, candidato: Bool, propuesta: Bool) -> Salida:
  match frenos:
    case True{}:
      frena()
    case False{}:
      sin_frenos(s, cerrada, segundo, candidato, propuesta)

# Los comandos mecánicos de Factory (autopilot.MECANICO): un agente los corre con --agente.
def es_mecanico(s: Sub) -> Bool:
  match s:
    case Importar{}:
      True{}
    case Juzgar{}:
      True{}
    case PedirRevision{}:
      True{}
    case RevisionPreparar{}:
      True{}
    case Tomar{}:
      True{}
    case Mensaje{}:
      True{}
    case Sincronizar{}:
      True{}
    case _:
      False{}

def sin_comando(s: Sub) -> Bool:
  match s:
    case SinPaso{}:
      True{}
    case _:
      False{}

# Lo que puede hacer el conductor: si actúa, sólo un comando mecánico; si frena, delega o termina, sin comando.
def permitida(x: Salida) -> Bool:
  match x:
    case Salida{a, s}:
      match a:
        case Actuar{}:
          es_mecanico(s)
        case PedirAPersona{}:
          True{}
        case Frenar{}:
          sin_comando(s)
        case DelegarAlAgente{}:
          sin_comando(s)
        case Terminado{}:
          sin_comando(s)

def accion_de(x: Salida) -> Accion:
  match x:
    case Salida{a, _}:
      a
