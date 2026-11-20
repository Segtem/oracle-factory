"""Buscaminas de terminal: tablero fijo y reglas separadas de la entrada de texto."""

from collections import deque


LADO = 5
MINAS = frozenset({(1, 1), (1, 5), (3, 3), (5, 1), (5, 5)})


class Partida:
    def __init__(self):
        self.destapadas = set()
        self.banderas = set()
        self.estado = "jugando"

    @staticmethod
    def _validar(fila, columna):
        if not (isinstance(fila, int) and isinstance(columna, int)
                and 1 <= fila <= LADO and 1 <= columna <= LADO):
            raise ValueError("fila y columna deben estar entre 1 y 5")

    @staticmethod
    def _vecinas(fila, columna):
        for f in range(max(1, fila - 1), min(LADO, fila + 1) + 1):
            for c in range(max(1, columna - 1), min(LADO, columna + 1) + 1):
                if (f, c) != (fila, columna):
                    yield f, c

    def numero(self, fila, columna):
        self._validar(fila, columna)
        return sum(vecina in MINAS for vecina in self._vecinas(fila, columna))

    def _jugando(self):
        if self.estado != "jugando":
            raise ValueError("la partida ya terminó")

    def alternar_bandera(self, fila, columna):
        self._jugando()
        self._validar(fila, columna)
        casilla = (fila, columna)
        if casilla in self.destapadas:
            raise ValueError("no se puede marcar una casilla destapada")
        if casilla in self.banderas:
            self.banderas.remove(casilla)
        else:
            self.banderas.add(casilla)

    def destapar(self, fila, columna):
        self._jugando()
        self._validar(fila, columna)
        casilla = (fila, columna)
        if casilla in self.banderas:
            raise ValueError("quitá la bandera antes de destapar")
        if casilla in self.destapadas:
            return
        if casilla in MINAS:
            self.destapadas.add(casilla)
            self.estado = "perdida"
            return

        pendientes = deque([casilla])
        while pendientes:
            actual = pendientes.popleft()
            if actual in self.destapadas or actual in self.banderas or actual in MINAS:
                continue
            self.destapadas.add(actual)
            if self.numero(*actual) == 0:
                pendientes.extend(self._vecinas(*actual))
        if len(self.destapadas) == LADO * LADO - len(MINAS):
            self.estado = "ganada"

    def vista(self):
        filas = ["    1 2 3 4 5"]
        for f in range(1, LADO + 1):
            casillas = []
            for c in range(1, LADO + 1):
                pos = (f, c)
                if pos in self.destapadas and pos in MINAS:
                    signo = "*"
                elif pos in self.destapadas:
                    n = self.numero(f, c)
                    signo = str(n) if n else "."
                elif pos in self.banderas:
                    signo = "F"
                elif self.estado != "jugando" and pos in MINAS:
                    signo = "*"
                else:
                    signo = "#"
                casillas.append(signo)
            filas.append(f"{f} | " + " ".join(casillas))
        return "\n".join(filas)


def jugar():
    partida = Partida()
    print("Buscaminas 5×5. d FILA COLUMNA destapa; b FILA COLUMNA marca; salir termina.")
    while True:
        print(partida.vista())
        if partida.estado != "jugando":
            print("Ganaste." if partida.estado == "ganada" else "Perdiste.")
            return
        try:
            orden = input("> ").strip().lower().split()
        except EOFError:
            return
        if orden == ["salir"]:
            return
        try:
            if len(orden) != 3 or orden[0] not in {"d", "b"}:
                raise ValueError("usá d FILA COLUMNA, b FILA COLUMNA o salir")
            fila, columna = int(orden[1]), int(orden[2])
            if orden[0] == "d":
                partida.destapar(fila, columna)
            else:
                partida.alternar_bandera(fila, columna)
        except ValueError as error:
            print(f"Comando inválido: {error}")


if __name__ == "__main__":
    jugar()
