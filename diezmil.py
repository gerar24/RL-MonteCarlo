from random import randint
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
from utils import puntaje_y_no_usados, separar, JUGADA_PLANTARSE, JUGADA_TIRAR
from jugador import (
    Jugador,
    JugadorAleatorio,
    JugadorSiempreSePlanta,
    ElBatoQueSoloCalculaPromedios,
)


class JuegoDiezMil:
    def __init__(self, jugador: Jugador):
        self.jugador: Jugador = jugador

    def jugar(self, verbose: bool = False, tope_turnos: int = 1000) -> tuple[int, int]:
        """Juega un juego de 10mil para un jugador, hasta terminar o hasta
        llegar a tope_turnos turnos. Devuelve la cantidad de turnos que
        necesitó y el puntaje final.
        """
        turno: int = 0
        puntaje_total: int = 0
        while puntaje_total < 10000 and turno < tope_turnos:
            # Nuevo turno
            turno += 1
            puntaje_turno: int = 0
            msg: str = "turno " + str(turno) + ":"

            # Un turno siempre empieza tirando los 6 dados.
            jugada: int = JUGADA_TIRAR
            dados_a_tirar: list[int] = [1, 2, 3, 4, 5, 6]
            fin_de_turno: bool = False

            while not fin_de_turno:
                # Tira los dados que correspondan y calcula su puntaje.
                dados: list[int] = [randint(1, 6) for _ in range(len(dados_a_tirar))]
                (puntaje_tirada, _) = puntaje_y_no_usados(dados)
                msg += " " + "".join(map(str, dados)) + " "
                # print(dados, _)

                if puntaje_tirada == 0:
                    # Mala suerte, no suma nada. Pierde el turno.
                    fin_de_turno = True
                    puntaje_turno = 0
                    if isinstance(self.jugador, ElBatoQueSoloCalculaPromedios):
                        self.jugador.actualizar_tabla(len(dados_a_tirar), puntaje_turno)

                else:
                    # Bien, suma puntos. Preguntamos al jugador qué quiere hacer.
                    jugada, dados_a_tirar = self.jugador.jugar(
                        puntaje_total, puntaje_turno, dados
                    )

                    if jugada == JUGADA_PLANTARSE:
                        msg += "P"
                        fin_de_turno = True
                        puntaje_turno += puntaje_tirada
                        if isinstance(self.jugador, ElBatoQueSoloCalculaPromedios):
                            self.jugador.actualizar_tabla(
                                len(dados_a_tirar), puntaje_turno
                            )

                    elif jugada == JUGADA_TIRAR:
                        dados_a_separar = separar(dados, dados_a_tirar)
                        assert len(dados_a_separar) + len(dados_a_tirar) == len(dados)
                        puntaje_tirada, dados_no_usados = puntaje_y_no_usados(
                            dados_a_separar
                        )
                        assert puntaje_tirada > 0 and len(dados_no_usados) == 0
                        puntaje_turno += puntaje_tirada
                        # Cuando usó todos los dados, vuelve a tirar todo.
                        if len(dados_a_tirar) == 0:
                            dados_a_tirar = [1, 2, 3, 4, 5, 6]
                        msg += "T(" + "".join(map(str, dados_a_tirar)) + ") "

            puntaje_total += puntaje_turno
            msg += (
                " --> " + str(puntaje_turno) + " puntos. TOTAL: " + str(puntaje_total)
            )
            if verbose:
                print(msg)
        return (turno, puntaje_total)


def main():
    # jugador = JugadorAleatorio("random")
    # juego = JuegoDiezMil(jugador)
    # (cantidad_turnos, puntaje_final) = juego.jugar(verbose=True)
    # print(jugador.nombre, cantidad_turnos, puntaje_final)

    # jugador = JugadorSiempreSePlanta("plantón")
    # juego = JuegoDiezMil(jugador)
    # (cantidad_turnos, puntaje_final) = juego.jugar(verbose=True)
    # print(jugador.nombre, cantidad_turnos, puntaje_final)

    # jugador = ElBatoQueSoloCalculaPromedios(0.05)
    # jugador_random = JugadorAleatorio("random")

    play_amounts = []
    for j in tqdm(range(100)):
        player_amounts = []
        jugador = ElBatoQueSoloCalculaPromedios(0.01)

        for i in tqdm(range(1000)):
            juego = JuegoDiezMil(jugador)
            # juego_aleatorio = JuegoDiezMil(jugador_random)
            (cantidad_turnos, puntaje_final) = juego.jugar(verbose=False)
            # (cantidad_turnos_random, puntaje_final_random) = juego_aleatorio.jugar(
            #     verbose=False
            # )
            player_amounts.append(cantidad_turnos)
            # play_amounts_random.append((i, cantidad_turnos_random))
            # print(jugador.nombre, cantidad_turnos, puntaje_final)
        jugador.print_table()
        play_amounts.append(player_amounts)

    # Convert play_amounts to a numpy array for easier manipulation
    play_amounts = np.array(play_amounts)

    # Calculate the average play amount across all agents for each iteration
    average_play_amounts = np.mean(play_amounts, axis=0)

    # Plot the average play amounts
    plt.figure(figsize=(10, 6))
    plt.plot(
        range(len(average_play_amounts)),
        average_play_amounts,
        label="Average Play Amounts",
    )
    plt.xlabel("Iteration")
    plt.ylabel("Average Play Amount")
    plt.title("Average Play Amounts Across 30 Agents Over 1000 Iterations")
    plt.legend()
    plt.show()
    plt.savefig("Montecarlo.png")


if __name__ == "__main__":
    main()
