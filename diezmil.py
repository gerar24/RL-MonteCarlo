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
    AgenteQLearning,
    ElBatoQueSoloCalculaPromediosPicados,
    ElBatoQueSoloCalculaPromediosMasPicados,
    ElBatoQueSoloCalculaPromediosPicadosPlus,
    ElBatoQueSoloCalculaPromediosMasPicados_Upgraded,
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
                    elif isinstance(self.jugador, ElBatoQueSoloCalculaPromediosPicados):
                        self.jugador.actualizar_tabla(len(dados_a_tirar), puntaje_turno, puntaje_total)
                    elif isinstance(self.jugador, ElBatoQueSoloCalculaPromediosMasPicados):
                        self.jugador.actualizar_tabla(len(dados_a_tirar), puntaje_turno, puntaje_total)
                    elif isinstance(self.jugador, ElBatoQueSoloCalculaPromediosPicadosPlus):
                        self.jugador.actualizar_tabla(len(dados_a_tirar), puntaje_turno, puntaje_total)
                    elif isinstance(self.jugador, ElBatoQueSoloCalculaPromediosMasPicados_Upgraded):
                        self.jugador.actualizar_tabla(len(dados_a_tirar), puntaje_turno, puntaje_total)
                    elif isinstance(self.jugador, AgenteQLearning):
                        self.jugador.actualizar_tabla(len(dados_a_tirar), puntaje_turno)
                        # print("PERDIO", dados_a_tirar, puntaje_turno)


                else:
                    # Bien, suma puntos. Preguntamos al jugador qué quiere hacer.
                    jugada, dados_a_tirar = self.jugador.jugar(
                        puntaje_total, puntaje_turno, dados # puntaje turno cambiado por puntajeturno + puntaje tirada
                    ) #PORQUE ACA PUNTAJE TURNO NO TIENE LA TIRADA ??????????

                    if jugada == JUGADA_PLANTARSE:
                        msg += "P"
                        fin_de_turno = True
                        puntaje_turno += puntaje_tirada
                        if isinstance(self.jugador, ElBatoQueSoloCalculaPromedios):
                            self.jugador.actualizar_tabla(
                                len(dados_a_tirar), puntaje_turno
                            )
                        elif isinstance(self.jugador, ElBatoQueSoloCalculaPromediosPicados):
                            self.jugador.actualizar_tabla(
                                len(dados_a_tirar), puntaje_turno, puntaje_total
                            )
                        elif isinstance(self.jugador, ElBatoQueSoloCalculaPromediosMasPicados):
                            self.jugador.actualizar_tabla(
                                len(dados_a_tirar), puntaje_turno, puntaje_total
                            )
                        elif isinstance(self.jugador, ElBatoQueSoloCalculaPromediosPicadosPlus):
                            self.jugador.actualizar_tabla(
                                len(dados_a_tirar), puntaje_turno, puntaje_total
                            )
                        elif isinstance(self.jugador, ElBatoQueSoloCalculaPromediosMasPicados_Upgraded):
                            self.jugador.actualizar_tabla(
                                len(dados_a_tirar), puntaje_turno, puntaje_total
                            )
                        elif isinstance(self.jugador, AgenteQLearning):
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
#
#
# def main():
#     # jugador = JugadorAleatorio("random")
#     # juego = JuegoDiezMil(jugador)
#     # (cantidad_turnos, puntaje_final) = juego.jugar(verbose=True)
#     # print(jugador.nombre, cantidad_turnos, puntaje_final)
#
#     # jugador = JugadorSiempreSePlanta("plantón")
#     # juego = JuegoDiezMil(jugador)
#     # (cantidad_turnos, puntaje_final) = juego.jugar(verbose=True)
#     # print(jugador.nombre, cantidad_turnos, puntaje_final)
#
#     # jugador = ElBatoQueSoloCalculaPromedios(0.05)
#     # jugador_random = JugadorAleatorio("random")
#
#     play_amounts = []
#     for j in tqdm(range(5)):
#         player_amounts = []
#         jugador = ElBatoQueSoloCalculaPromedios(0.05, "politica_chill.csv")
#         #jugador = ElBatoQueSoloCalculaPromediosPicados(0.05, "politica_picada.csv")
#         #jugador = ElBatoQueSoloCalculaPromediosMasPicados(0.05, "politica_maspicada.csv")
#         #jugador = ElBatoQueSoloCalculaPromediosPicados(0.05, "politica_picadaplus.csv")
#         # jugador = AgenteQLearning(0.05, 0.99, 0.05, 0.05)
#
#         for i in tqdm(range(20000)):
#             juego = JuegoDiezMil(jugador)
#             # juego_aleatorio = JuegoDiezMil(jugador_random)
#             (cantidad_turnos, puntaje_final) = juego.jugar(verbose=False)
#             # (cantidad_turnos_random, puntaje_final_random) = juego_aleatorio.jugar(
#             #     verbose=False
#             # )
#             player_amounts.append(cantidad_turnos)
#             # play_amounts_random.append((i, cantidad_turnos_random))
#             # print(jugador.nombre, cantidad_turnos, puntaje_final)
#         # jugador.print_table()
#         play_amounts.append(player_amounts)
#         if isinstance(jugador, ElBatoQueSoloCalculaPromediosPicados):
#             jugador.guardar_estados_en_csv()
#         if isinstance(jugador, ElBatoQueSoloCalculaPromediosMasPicados):
#             jugador.guardar_estados_en_csv()
#         if isinstance(jugador, ElBatoQueSoloCalculaPromedios):
#             jugador.guardar_estados_en_csv()
#         if isinstance(jugador, ElBatoQueSoloCalculaPromediosPicadosPlus):
#             jugador.guardar_estados_en_csv()
#
#
#     # Convert play_amounts to a numpy array for easier manipulation
#     play_amounts = np.array(play_amounts)
#
#     # Calculate the average play amount across all agents for each iteration
#     average_play_amounts = np.mean(play_amounts, axis=0)
#
#     # ultimas mil
#     # Select the last 1000 iterations
#     last_1000 = play_amounts[:, -1000:]
#     # Calculate the average for each agent over the last 1000 iterations
#     average_last_1000_per_agent = np.mean(last_1000, axis=1)
#     # Calculate the overall average across the agents
#     overall_average = np.mean(average_last_1000_per_agent)
#     print("OVERALL AVERAGE in last 1000 its", overall_average)
#
#     # Plot the average play amounts
#     plt.figure(figsize=(10, 6))
#     plt.plot(
#         range(len(average_play_amounts)),
#         average_play_amounts,
#         label="Average Play Amounts",
#     )
#     plt.xlabel("Iteration")
#     plt.ylabel("Average Play Amount")
#     plt.title("Average Play Amounts Across 30 Agents Over 1000 Iterations")
#     plt.legend()
#     plt.savefig("MontecarloPicado.png")
#     plt.show()

def main():
    agent_classes = [
        #("politica_chill.csv", ElBatoQueSoloCalculaPromedios),
        #("politica_picada.csv", ElBatoQueSoloCalculaPromediosPicados),
        #("politica_maspicada_10palos.csv", ElBatoQueSoloCalculaPromediosMasPicados),
        #("politica_picadaplus_1palo_2.5%_nmalrecomp.csv", ElBatoQueSoloCalculaPromediosPicadosPlus),
        ("politica_maspicadaupgraded_10palo_5%.csv", ElBatoQueSoloCalculaPromediosMasPicados_Upgraded),
        # ("", AgenteQLearning),  # Añadir parámetros según sea necesario
    ]

    for policy_file, AgentClass in agent_classes:
        play_amounts = []

        for j in tqdm(range(1), desc=f"Running {AgentClass.__name__}"):
            player_amounts = []
            jugador = AgentClass(0.05, policy_file)

            for i in tqdm(range(10000000), desc=f"Iteration {j + 1}/10"):
                juego = JuegoDiezMil(jugador)
                (cantidad_turnos, puntaje_final) = juego.jugar(verbose=False)
                player_amounts.append(cantidad_turnos)

            play_amounts.append(player_amounts)
            jugador.guardar_estados_en_csv()

        # Convert play_amounts to a numpy array for easier manipulation
        play_amounts = np.array(play_amounts)

        # Calculate the average play amount across all runs
        average_play_amounts = np.mean(play_amounts, axis=0)

        # Últimas mil iteraciones
        last_10000 = play_amounts[:, -10000:]
        average_last_10000_per_agent = np.mean(last_10000, axis=1)
        overall_average = np.mean(average_last_10000_per_agent)
        print(f"OVERALL AVERAGE in last 10000 iterations for {AgentClass.__name__}: {overall_average}")

        # Plot the average play amounts
        plt.figure(figsize=(10, 6))
        plt.plot(
            range(len(average_play_amounts)),
            average_play_amounts,
            label=f"Average Play Amounts ({AgentClass.__name__})",
        )
        plt.xlabel("Iteration")
        plt.ylabel("Average Play Amount")
        plt.title(f"Average Play Amounts for {AgentClass.__name__} Over 10,000,000 Iterations")
        plt.text(len(average_play_amounts) * 0.75, np.min(average_play_amounts) * 0.98, f"Average in last 10000 iterations{overall_average}")
        plt.savefig(f"Montecarlo_{AgentClass.__name__}_10palo_5%.png")
        plt.close()


if __name__ == "__main__":
    main()
