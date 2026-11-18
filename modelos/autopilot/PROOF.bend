import Base
import ./autopilot.bend as Q
import ./LAWS.bend as Laws

# Generado por generar.py (no se edita a mano): análisis por casos sobre el próximo paso y las banderas.

def Laws.el_conductor_solo_corre_lo_mecanico(s, frenos, cerrada, segundo, candidato, propuesta):
  match s:
    case Q.SinPaso{}:
      match frenos:
        case True{}:
          {==}
        case False{}:
          match cerrada:
            case True{}:
              {==}
            case False{}:
              {==}
    case Q.Prosa{}:
      match frenos:
        case True{}:
          {==}
        case False{}:
          {==}
    case Q.Ilegible{}:
      match frenos:
        case True{}:
          {==}
        case False{}:
          {==}
    case Q.AprobarSpec{}:
      match frenos:
        case True{}:
          {==}
        case False{}:
          {==}
    case Q.Revisar{}:
      match frenos:
        case True{}:
          {==}
        case False{}:
          match segundo candidato propuesta:
            case True{} True{} True{}:
              {==}
            case True{} True{} False{}:
              {==}
            case True{} False{} True{}:
              {==}
            case True{} False{} False{}:
              {==}
            case False{} True{} True{}:
              {==}
            case False{} True{} False{}:
              {==}
            case False{} False{} True{}:
              {==}
            case False{} False{} False{}:
              {==}
    case Q.Cerrar{}:
      match frenos:
        case True{}:
          {==}
        case False{}:
          {==}
    case Q.Abandonar{}:
      match frenos:
        case True{}:
          {==}
        case False{}:
          {==}
    case Q.Modo{}:
      match frenos:
        case True{}:
          {==}
        case False{}:
          {==}
    case Q.Autonomia{}:
      match frenos:
        case True{}:
          {==}
        case False{}:
          {==}
    case Q.Soltar{}:
      match frenos:
        case True{}:
          {==}
        case False{}:
          {==}
    case Q.DecidirUnion{}:
      match frenos:
        case True{}:
          {==}
        case False{}:
          {==}
    case Q.Conectar{}:
      match frenos:
        case True{}:
          {==}
        case False{}:
          {==}
    case Q.Desconectar{}:
      match frenos:
        case True{}:
          {==}
        case False{}:
          {==}
    case Q.Importar{}:
      match frenos:
        case True{}:
          {==}
        case False{}:
          {==}
    case Q.Juzgar{}:
      match frenos:
        case True{}:
          {==}
        case False{}:
          {==}
    case Q.PedirRevision{}:
      match frenos:
        case True{}:
          {==}
        case False{}:
          match candidato:
            case True{}:
              {==}
            case False{}:
              {==}
    case Q.RevisionPreparar{}:
      match frenos:
        case True{}:
          {==}
        case False{}:
          match candidato:
            case True{}:
              {==}
            case False{}:
              {==}
    case Q.Tomar{}:
      match frenos:
        case True{}:
          {==}
        case False{}:
          {==}
    case Q.Mensaje{}:
      match frenos:
        case True{}:
          {==}
        case False{}:
          {==}
    case Q.Sincronizar{}:
      match frenos:
        case True{}:
          {==}
        case False{}:
          {==}
    case Q.MedirConfirmar{}:
      match frenos:
        case True{}:
          {==}
        case False{}:
          {==}
    case Q.MedirListar{}:
      match frenos:
        case True{}:
          {==}
        case False{}:
          {==}
    case Q.MedirOtro{}:
      match frenos:
        case True{}:
          {==}
        case False{}:
          {==}
    case Q.AprobarSensor{}:
      match frenos:
        case True{}:
          {==}
        case False{}:
          {==}
    case Q.Evidencia{}:
      match frenos:
        case True{}:
          {==}
        case False{}:
          {==}
    case Q.Otro{}:
      match frenos:
        case True{}:
          {==}
        case False{}:
          {==}

def Laws.con_frenos_siempre_frena(s, cerrada, segundo, candidato, propuesta):
  {==}

def Laws.confirmar_las_medidas_es_de_una_persona(cerrada, segundo, candidato, propuesta):
  {==}

def Laws.aprobar_spec_se_le_pide_a_una_persona(cerrada, segundo, candidato, propuesta):
  {==}

def Laws.cerrar_se_le_pide_a_una_persona(cerrada, segundo, candidato, propuesta):
  {==}

def Laws.abandonar_se_le_pide_a_una_persona(cerrada, segundo, candidato, propuesta):
  {==}

def Laws.modo_se_le_pide_a_una_persona(cerrada, segundo, candidato, propuesta):
  {==}

def Laws.autonomia_se_le_pide_a_una_persona(cerrada, segundo, candidato, propuesta):
  {==}

def Laws.soltar_se_le_pide_a_una_persona(cerrada, segundo, candidato, propuesta):
  {==}

def Laws.decidir_union_se_le_pide_a_una_persona(cerrada, segundo, candidato, propuesta):
  {==}

def Laws.conectar_se_le_pide_a_una_persona(cerrada, segundo, candidato, propuesta):
  {==}

def Laws.desconectar_se_le_pide_a_una_persona(cerrada, segundo, candidato, propuesta):
  {==}

def Laws.revisar_se_le_pide_a_una_persona(cerrada):
  {==}

def Laws.revisar_sin_propuesta_la_prepara_el_agente(cerrada):
  {==}

def Laws.revisar_pide_antes_el_segundo_revisor(cerrada, candidato, propuesta):
  {==}

def Laws.la_prosa_se_delega(cerrada, segundo, candidato, propuesta):
  {==}

def Laws.importar_lo_corre_el_agente(cerrada, segundo, candidato, propuesta):
  {==}

def Laws.lo_que_no_conoce_lo_frena(cerrada, segundo, candidato, propuesta):
  {==}

def Laws.lo_de_persona_no_es_mecanico():
  {==}

def Laws.sin_paso_termina_solo_lo_cerrado(segundo, candidato, propuesta):
  {==}

def Laws.cerrado_y_sin_paso_termina(segundo, candidato, propuesta):
  {==}

def Laws.sin_candidato_primero_se_construye(cerrada, segundo, propuesta):
  {==}
