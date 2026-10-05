def listar_notas(notas):
    # mutante: ordena alfabéticamente en vez de conservar el orden de entrada
    return "\n".join(f"- {n['titulo']}" for n in sorted(notas, key=lambda n: n["titulo"]))
