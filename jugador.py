from random import randint, uniform
import random
from abc import ABC, abstractmethod
from utils import puntaje_y_no_usados, JUGADA_PLANTARSE, JUGADA_TIRAR


class Jugador(ABC):
    @abstractmethod
    def jugar(
        self,
        puntaje_total: int,
        puntaje_turno: int,
        dados: list[int],
        verbose: bool = False,
    ) -> tuple[int, list[int]]:
        pass


class JugadorAleatorio(Jugador):
    def __init__(self, nombre: str):
        self.nombre = nombre

    def jugar(
        self,
        puntaje_total: int,
        puntaje_turno: int,
        dados: list[int],
        verbose: bool = False,
    ) -> tuple[int, list[int]]:
        (puntaje, no_usados) = puntaje_y_no_usados(dados)
        if randint(0, 1) == 0:
            return (JUGADA_PLANTARSE, [])
        else:
            return (JUGADA_TIRAR, no_usados)


class JugadorSiempreSePlanta(Jugador):
    def __init__(self, nombre: str):
        self.nombre = nombre

    def jugar(
        self,
        puntaje_total: int,
        puntaje_turno: int,
        dados: list[int],
        verbose: bool = False,
    ) -> tuple[int, list[int]]:
        return (JUGADA_PLANTARSE, [])


class ElBatoQueSoloCalculaPromedios(Jugador):
    def __init__(self, epsilon: float):
        self.nombre = "Monte Carlo"
        self.epsilon = epsilon  # e-greedy
        self.history = []
        self.estados = {
            0: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            1: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            2: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            3: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            4: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            5: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            6: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
        }

    def print_table(self):
        for state, rewards in self.estados.items():
            reward_plantarse = rewards["plantarse"]
            reward_tirar = rewards["tirar"]
            avg_reward_plantarse = reward_plantarse / rewards["c_plantarse"]
            avg_reward_tirar = reward_tirar / rewards["c_tirar"]
            ct = rewards["c_tirar"]
            cp = rewards["c_plantarse"]

            print(f"State {state}:")
            print(f"  Cantidad plantarse: {cp:.2f}")
            print(f"  Cantidad tirar: {ct:.2f}")
            print(f"  Promedio reward_plantarse: {avg_reward_plantarse:.2f}")
            print(f"  Promedio reward_tirar: {avg_reward_tirar:.2f}")

    def jugar(self, puntaje_total: int, puntaje_turno: int, dados: list[int]):
        (puntaje, no_usados) = puntaje_y_no_usados(dados)
        cant_dados = len(no_usados)

        if uniform(0, 1) < self.epsilon:
            if uniform(0, 1) > 0.5:
                self.history.append((cant_dados, "plantarse"))
                return (JUGADA_PLANTARSE, [])
            else:
                self.history.append((cant_dados, "tirar"))
                return (JUGADA_TIRAR, no_usados)
        else:
            if (
                self.estados[cant_dados]["tirar"] / self.estados[cant_dados]["c_tirar"]
                > self.estados[cant_dados]["plantarse"]
                / self.estados[cant_dados]["c_plantarse"]
            ):
                self.history.append((cant_dados, "tirar"))
                return (JUGADA_TIRAR, no_usados)
            elif (
                self.estados[cant_dados]["tirar"] / self.estados[cant_dados]["c_tirar"]
                < self.estados[cant_dados]["plantarse"]
                / self.estados[cant_dados]["c_plantarse"]
            ):
                self.history.append((cant_dados, "plantarse"))
                return (JUGADA_PLANTARSE, [])
            else:
                if uniform(0, 1) > 0.5:
                    return (JUGADA_TIRAR, no_usados)
                else:
                    return (JUGADA_PLANTARSE, [])

    def actualizar_tabla(self, estado, puntaje_turno):
        for estado, accion in self.history:
            self.estados[estado][accion] += puntaje_turno
            self.estados[estado]["c_" + accion] += 1
        self.history.clear()


class AgenteQLearning(Jugador):
    def __init__(self, alpha: float, gamma: float, epsilon: float):
        self.nombre = "Q-Learning"
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        # initialize the values at random
        # self.q_table = {
        #     0: {"tirar": randint(0, 10), "plantarse": randint(0, 10)},
        #     1: {"tirar": randint(0, 10), "plantarse": randint(0, 10)},
        #     2: {"tirar": randint(0, 10), "plantarse": randint(0, 10)},
        #     3: {"tirar": randint(0, 10), "plantarse": randint(0, 10)},
        #     4: {"tirar": randint(0, 10), "plantarse": randint(0, 10)},
        #     5: {"tirar": randint(0, 10), "plantarse": randint(0, 10)},
        #     6: {"tirar": randint(0, 10), "plantarse": randint(0, 10)},
        # }

        self.q_table = {
            0: {"tirar": 0, "plantarse": 0},
            1: {"tirar": 0, "plantarse": 0},
            2: {"tirar": 0, "plantarse": 0},
            3: {"tirar": 0, "plantarse": 0},
            4: {"tirar": 0, "plantarse": 0},
            5: {"tirar": 0, "plantarse": 0},
            6: {"tirar": 0, "plantarse": 0},
        }
        self.last_state = None
        self.last_action = None

    def print_table(self):
        for state, rewards in self.q_table.items():
            reward_plantarse = rewards["plantarse"]
            reward_tirar = rewards["tirar"]

            print(f"State {state}:")
            print(f"  Reward plantarse: {reward_plantarse:.2f}")
            print(f"  Reward tirar: {reward_tirar:.2f}")

    def jugar(self, puntaje_total: int, puntaje_turno: int, dados: list[int]):
        (puntaje, no_usados) = puntaje_y_no_usados(dados)
        cant_dados = len(no_usados)
        self.last_state = cant_dados

        if uniform(0, 1) < self.epsilon:
            if uniform(0, 1) > 0.5:
                self.last_action = "plantarse"
                return (JUGADA_PLANTARSE, [])
            else:
                self.last_action = "tirar"
                return (JUGADA_TIRAR, no_usados)
        else:
            if (
                self.q_table[cant_dados]["tirar"]
                > self.q_table[cant_dados]["plantarse"]
            ):
                self.last_action = "tirar"
                return (JUGADA_TIRAR, no_usados)
            else:
                self.last_action = "plantarse"
                return (JUGADA_PLANTARSE, [])

    def actualizar_tabla(self, estado, puntaje_tirada):
        if self.last_state is not None and self.last_action is not None:
            q_value = self.q_table[self.last_state][self.last_action]
            max_q_value = max(self.q_table[estado].values())
            self.q_table[self.last_state][self.last_action] = q_value + self.alpha * (
                puntaje_tirada + self.gamma * max_q_value - q_value
            )
        self.last_state = None
        self.last_action = None


class AgenteQLearning(Jugador):
    def __init__(
        self, alpha: float, gamma: float, epsilon: float, epsilon_decay: float
    ):
        self.nombre = "Q-Learning"
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay

        # Initialize Q-table to zero or equal values to avoid biasing towards any action
        self.q_table = {i: {"tirar": 0, "plantarse": 0} for i in range(7)}

        self.last_state = None
        self.last_action = None

    def jugar(self, puntaje_total: int, puntaje_turno: int, dados: list[int]):
        (puntaje, no_usados) = puntaje_y_no_usados(dados)
        cant_dados = len(no_usados)
        self.last_state = cant_dados

        # Epsilon-greedy action selection
        if uniform(0, 1) < self.epsilon:
            action = random.choice(["plantarse", "tirar"])
        else:
            action = (
                "tirar"
                if self.q_table[cant_dados]["tirar"]
                > self.q_table[cant_dados]["plantarse"]
                else "plantarse"
            )

        self.last_action = action

        if action == "tirar":
            return JUGADA_TIRAR, no_usados
        else:
            return JUGADA_PLANTARSE, []

    def actualizar_tabla(self, estado, puntaje_tirada):
        if self.last_state is not None and self.last_action is not None:
            q_value = self.q_table[self.last_state][self.last_action]
            max_q_value = max(self.q_table[estado].values())
            self.q_table[self.last_state][self.last_action] = q_value + self.alpha * (
                puntaje_tirada + self.gamma * max_q_value - q_value
            )

        # Decay epsilon
        self.epsilon *= self.epsilon_decay

        self.last_state = None
        self.last_action = None
