from random import randint, uniform
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
