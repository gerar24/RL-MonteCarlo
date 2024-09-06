from random import randint
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
from utils import puntaje_y_no_usados, separar, JUGADA_PLANTARSE, JUGADA_TIRAR
from jugador import (
    Jugador,
    JugadorAleatorio,
    JugadorSiempreSePlanta,
    MonteCarlo_Base_Ag1,
    MonteCarlo_Base_Ag2_PTotal,
    MonteCarlo_Base_Ag3_PTotalyAcum,
    MonteCarlo_Base_Ag4_PAcum,
    MonteCarlo_Base_Ag5_PTotalBinnedyAcum,
    MonteCarlo_Base_Ag6_PTotalBinned1000yAcum,
    AgenteQLearning
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

                    if isinstance(self.jugador, MonteCarlo_Base_Ag1) or isinstance(self.jugador, AgenteQLearning):
                            self.jugador.actualizar_tabla(len(dados_a_tirar), puntaje_turno)
                    else:
                        self.jugador.actualizar_tabla(len(dados_a_tirar), puntaje_turno, puntaje_total)

                else:
                    # Bien, suma puntos. Preguntamos al jugador qué quiere hacer.
                    jugada, dados_a_tirar = self.jugador.jugar(
                        puntaje_total, puntaje_turno, dados # puntaje turno cambiado por puntajeturno + puntaje tirada
                    )

                    if jugada == JUGADA_PLANTARSE:
                        msg += "P"
                        fin_de_turno = True
                        puntaje_turno += puntaje_tirada
                        if isinstance(self.jugador, MonteCarlo_Base_Ag1) or isinstance(self.jugador, AgenteQLearning):
                            self.jugador.actualizar_tabla(len(dados_a_tirar), puntaje_turno)
                        else:
                            self.jugador.actualizar_tabla(len(dados_a_tirar), puntaje_turno, puntaje_total)

                    elif jugada == JUGADA_TIRAR:
                        dados_a_separar = separar(dados, dados_a_tirar)
                        assert len(dados_a_separar) + len(dados_a_tirar) == len(dados)
                        puntaje_tirada, dados_no_usados = puntaje_y_no_usados(
                            dados_a_separar
                        )
                        assert puntaje_tirada > 0 and len(dados_no_usados) == 0
                        puntaje_turno += puntaje_tirada
                        if isinstance(self.jugador, AgenteQLearning):
                            self.jugador.actualizar_tabla(
                                len(dados_a_tirar), puntaje_tirada
                            )
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
    # Agentes a entrenar o jugar.
    agent_classes = [
        #("politica_chill.csv", MonteCarlo_Base_Ag1),
        #("politica_picada.csv", MonteCarlo_Base_Ag2_PTotal),
        #("politica_maspicada_10palos.csv", MonteCarlo_Base_Ag3_PTotalyAcum),
        #("politica_picadaplus_1palo_2.5%_nmalrecomp.csv", MonteCarlo_Base_Ag4_PAcum),
        #("politica_maspicadaupgraded_10palo_5%.csv", MonteCarlo_Base_Ag5_PTotalBinnedyAcum),
        #("politica_maspicadaupgradedall_5palo_5%.csv", MonteCarlo_Base_Ag6_PTotalBinned1000yAcum),
        #("", AgenteQLearning),  # Añadir parámetros según sea necesario

    ]
    # Cantidad de iteraciones a entrenar/jugar
    its = 100000
    for policy_file, AgentClass in agent_classes:
        play_amounts = []

        for j in tqdm(range(1), desc=f"Running {AgentClass.__name__}"):
            player_amounts = []
            jugador = AgentClass(0.025, policy_file, False) #Epsilon-Greedy Param, CSV Politica File, Training Bool.

            for i in tqdm(range(its), desc=f"Iteration {j + 1}/10"): 
                juego = JuegoDiezMil(jugador)
                (cantidad_turnos, puntaje_final) = juego.jugar(verbose=False)
                player_amounts.append(cantidad_turnos)

            play_amounts.append(player_amounts)
            jugador.guardar_estados_en_csv()

        # Convert play_amounts to a numpy array for easier manipulation
        play_amounts = np.array(play_amounts)

        # Calculate the average play amount across all runs
        average_play_amounts = np.mean(play_amounts, axis=0)

        # Últimas diez mil iteraciones
        last_10000 = play_amounts[:, -10000:]
        average_last_10000_per_agent = np.mean(last_10000, axis=1)
        overall_average = np.mean(average_last_10000_per_agent)
        print(f"OVERALL AVERAGE in last 100000 iterations for {AgentClass.__name__}: {overall_average}")

        # Plot the average play amounts
        plt.figure(figsize=(10, 6))
        plt.plot(
            range(len(average_play_amounts)),
            average_play_amounts,
            label=f"Average Play Amounts ({AgentClass.__name__})",
        )
        plt.xlabel("Iteration")
        plt.ylabel("Average Play Amount")
        plt.title(f"Average Play Amounts for {AgentClass.__name__} Over {its} Iterations")
        plt.text(len(average_play_amounts) * 0.75, np.min(average_play_amounts) * 0.98, f"Average in last 10000 iterations{overall_average}") #
        plt.savefig(f"{AgentClass.__name__}_10palo_ntjuego1palo.png")
        plt.close()


if __name__ == "__main__":
    main()
