"""Escribe PROOF.bend: las pruebas de las leyes de LAWS.bend, por análisis de casos. LAWS.bend no se genera: lo revisa una persona.

    python3 modelos/autopilot/generar.py          (escribe PROOF.bend)
"""
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SUBS = ["SinPaso", "Prosa", "Ilegible", "AprobarSpec", "Revisar", "Cerrar", "Abandonar", "Modo", "Autonomia", "Soltar", "DecidirUnion",
        "Conectar", "Desconectar", "Importar", "Juzgar", "PedirRevision", "RevisionPreparar", "Tomar", "Mensaje", "Sincronizar",
        "MedirConfirmar", "MedirListar", "MedirOtro", "AprobarSensor", "Evidencia", "Otro"]
PERSONA = ["AprobarSpec", "Cerrar", "Abandonar", "Modo", "Autonomia", "Soltar", "DecidirUnion", "Conectar", "Desconectar"]
B = ["True", "False"]
RESTO = "(terminada, segundo, candidato, propuesta)"
# Las leyes que se prueban por reflexividad, con sus parámetros: el modelo reduce a un valor sin separar casos.
DIRECTAS = [("con_frenos_siempre_frena", "(s, terminada, segundo, candidato, propuesta)"),
            ("confirmar_las_medidas_es_de_una_persona", RESTO),
            *((f"{''.join('_' + c.lower() if c.isupper() else c for c in p).lstrip('_')}_se_le_pide_a_una_persona", RESTO) for p in PERSONA),
            ("revisar_se_le_pide_a_una_persona", "(terminada)"), ("revisar_sin_propuesta_la_prepara_el_agente", "(terminada)"),
            ("revisar_pide_antes_el_segundo_revisor", "(terminada, candidato, propuesta)"), ("la_prosa_se_delega", RESTO),
            ("importar_lo_corre_el_agente", RESTO), ("lo_que_no_conoce_lo_frena", RESTO), ("lo_de_persona_no_es_mecanico", "()"),
            ("sin_paso_termina_solo_lo_terminado", "(segundo, candidato, propuesta)"), ("terminado_y_sin_paso_termina", "(segundo, candidato, propuesta)"),
            ("sin_candidato_primero_se_construye", "(terminada, segundo, propuesta)")]


def casos(indent, scrutinee, ramas):
    out = [f"{indent}match {scrutinee}:"]
    for patron, cuerpo in ramas:
        out += [f"{indent}  case {patron}:", *cuerpo]
    return out


def segun_sub(i, s):
    """Lo que hay que separar para que decidir(False, terminada, s, …) reduzca a un valor."""
    if s == "SinPaso":
        return casos(i, "terminada", [(f"{b}{{}}", [f"{i}    {{==}}"]) for b in B])
    if s == "Revisar":
        return casos(i, "segundo candidato propuesta", [(f"{a}{{}} {b}{{}} {c}{{}}", [f"{i}    {{==}}"]) for a in B for b in B for c in B])
    if s in ("PedirRevision", "RevisionPreparar"):
        return casos(i, "candidato", [(f"{b}{{}}", [f"{i}    {{==}}"]) for b in B])
    return [f"{i}{{==}}"]


def pruebas() -> str:
    lineas = ["import Base", "import ./autopilot.bend as Q", "import ./LAWS.bend as Laws", "",
              "# Generado por generar.py (no se edita a mano): análisis por casos sobre el próximo paso y las banderas.", "",
              "def Laws.el_conductor_solo_corre_lo_mecanico(s, frenos, terminada, segundo, candidato, propuesta):", "  match s:"]
    for s in SUBS:
        lineas += [f"    case Q.{s}{{}}:", *casos("      ", "frenos", [("True{}", ["          {==}"]), ("False{}", segun_sub("          ", s))])]
    for nombre, params in DIRECTAS:
        lineas += ["", f"def Laws.{nombre}{params}:", "  {==}"]
    return "\n".join(lineas) + "\n"


if __name__ == "__main__":
    (AQUI / "PROOF.bend").write_text(pruebas(), encoding="utf-8")
