from random import randint, uniform
import random
from abc import ABC, abstractmethod
from utils import puntaje_y_no_usados, JUGADA_PLANTARSE, JUGADA_TIRAR
import os
import csv
import numpy as np

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
    def __init__(self, epsilon: float, politica_csv_path):
        self.nombre = "Monte Carlo"
        self.politica_csv_path = politica_csv_path
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
        # Elimina el archivo si ya existe
        if os.path.exists(self.politica_csv_path):
            os.remove(self.politica_csv_path)

        self._crear_csv()
        self._cargar_estados()

    def _crear_csv(self):
        estados_base = {
            0: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            1: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            2: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            3: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            4: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            5: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
        }
        with open(self.politica_csv_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Escribe el encabezado
            writer.writerow(["estado", "tirar", "plantarse", "c_tirar", "c_plantarse"])

            for estado, valores in estados_base.items():
                fila = [estado] + list(valores.values())
                writer.writerow(fila)

    def _cargar_estados(self):
        with open(self.politica_csv_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                estado = int(row["estado"])
                self.estados[estado] = {
                    "tirar": int(row["tirar"]),
                    "plantarse": int(row["plantarse"]),
                    "c_tirar": int(row["c_tirar"]),
                    "c_plantarse": int(row["c_plantarse"])
                }

    def guardar_estados_en_csv(self):
        """Guarda el contenido de self.estados en el archivo CSV."""
        with open(self.politica_csv_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Escribe el encabezado
            writer.writerow(["estado", "tirar", "plantarse", "c_tirar", "c_plantarse"])

            for estado, valores in self.estados.items():
                fila = [estado, valores["tirar"], valores["plantarse"],
                        valores["c_tirar"], valores["c_plantarse"]]
                writer.writerow(fila)

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

class ElBatoQueSoloCalculaPromediosPicados(Jugador):
    def __init__(self, epsilon: float, politica_csv_path):
        self.nombre = "Monte Carlo"
        self.epsilon = epsilon  # e-greedy
        self.history = []
        
        self.politica_csv_path = politica_csv_path
        self.estados = {}

        # Elimina el archivo si ya existe
        if os.path.exists(self.politica_csv_path):
            os.remove(self.politica_csv_path)

        self._crear_csv()
        self._cargar_estados()

    def _crear_csv(self):
        estados_base = {
            0: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            1: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            2: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            3: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            4: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            5: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
        }

        with open(self.politica_csv_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Escribe el encabezado
            writer.writerow(["estado", "puntuacion", "tirar", "plantarse", "c_tirar", "c_plantarse"])
            
            for estado in estados_base.keys():
                for puntuacion in range(0, 10001, 50):
                    fila = [estado, puntuacion] + list(estados_base[estado].values())
                    writer.writerow(fila)

    def _cargar_estados(self):
        with open(self.politica_csv_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                estado = int(row["estado"])
                puntuacion = int(row["puntuacion"])
                if estado not in self.estados:
                    self.estados[estado] = {}
                self.estados[estado][puntuacion] = {
                    "tirar": int(row["tirar"]),
                    "plantarse": int(row["plantarse"]),
                    "c_tirar": int(row["c_tirar"]),
                    "c_plantarse": int(row["c_plantarse"])
                }

    def guardar_estados_en_csv(self):
        """Guarda el contenido de self.estados en el archivo CSV."""
        with open(self.politica_csv_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Escribe el encabezado
            writer.writerow(["estado", "puntuacion", "tirar", "plantarse", "c_tirar", "c_plantarse"])
            
            for estado, puntuaciones in self.estados.items():
                for puntuacion, valores in puntuaciones.items():
                    fila = [estado, puntuacion, valores["tirar"], valores["plantarse"], 
                            valores["c_tirar"], valores["c_plantarse"]]
                    writer.writerow(fila)


    # def print_table(self):
    #     for state, rewards in self.estados.items():
    #         reward_plantarse = rewards["plantarse"]
    #         reward_tirar = rewards["tirar"]
    #         avg_reward_plantarse = reward_plantarse / rewards["c_plantarse"]
    #         avg_reward_tirar = reward_tirar / rewards["c_tirar"]
    #         ct = rewards["c_tirar"]
    #         cp = rewards["c_plantarse"]

    #         print(f"State {state}:")
    #         print(f"  Cantidad plantarse: {cp:.2f}")
    #         print(f"  Cantidad tirar: {ct:.2f}")
    #         print(f"  Promedio reward_plantarse: {avg_reward_plantarse:.2f}")
    #         print(f"  Promedio reward_tirar: {avg_reward_tirar:.2f}")

    def jugar(self, puntaje_total: int, puntaje_turno: int, dados: list[int]):
        (puntaje, no_usados) = puntaje_y_no_usados(dados)
        cant_dados = len(no_usados)

        if uniform(0, 1) < self.epsilon: #BUGGG?? tenemos poca entrada no greedy y sube mas greedy 50%
            if uniform(0, 1) > 0.5:
                self.history.append((cant_dados, "plantarse"))
                return (JUGADA_PLANTARSE, [])
            else:
                self.history.append((cant_dados, "tirar"))
                return (JUGADA_TIRAR, no_usados)

        # if uniform(0, 1) < self.epsilon: #### TOMO DECISION NO GREEDY, CONTRARIA
        #     if (
        #         self.estados[cant_dados][puntaje_total]["tirar"] / self.estados[cant_dados][puntaje_total]["c_tirar"]
        #         > self.estados[cant_dados][puntaje_total]["plantarse"]
        #         / self.estados[cant_dados][puntaje_total]["c_plantarse"]
        #     ):
        #         self.history.append((cant_dados, "plantarse"))
        #         return (JUGADA_PLANTARSE, [])
        #     else:
        #         self.history.append((cant_dados, "tirar"))
        #         return (JUGADA_TIRAR, no_usados)
        else:
            if (
                self.estados[cant_dados][puntaje_total]["tirar"] / self.estados[cant_dados][puntaje_total]["c_tirar"]
                > self.estados[cant_dados][puntaje_total]["plantarse"]
                / self.estados[cant_dados][puntaje_total]["c_plantarse"]
            ):
                self.history.append((cant_dados, "tirar"))
                return (JUGADA_TIRAR, no_usados)
            elif (
                self.estados[cant_dados][puntaje_total]["tirar"] / self.estados[cant_dados][puntaje_total]["c_tirar"]
                < self.estados[cant_dados][puntaje_total]["plantarse"]
                / self.estados[cant_dados][puntaje_total]["c_plantarse"]
            ):
                self.history.append((cant_dados, "plantarse"))
                return (JUGADA_PLANTARSE, [])
            else:
                if uniform(0, 1) > 0.5: #si es igual random
                    self.history.append((cant_dados, "tirar"))
                    return (JUGADA_TIRAR, no_usados)
                else:
                    self.history.append((cant_dados, "plantarse"))
                    return (JUGADA_PLANTARSE, [])
            # elif self.estados[cant_dados][puntaje_total]["tirar"] == 0 and self.estados[cant_dados][puntaje_total]["plantarse"] == 0: # caso inicial random
            #     if uniform(0, 1) > 0.5:
            #         self.history.append((cant_dados, "tirar"))
            #         return (JUGADA_TIRAR, no_usados)
            #     else:
            #         self.history.append((cant_dados, "plantarse"))
            #         return (JUGADA_PLANTARSE, [])
            # else: # es igual? ok me planto mas safe (rebug final)
            #     self.history.append((cant_dados, "plantarse"))
            #     return (JUGADA_PLANTARSE, [])


    def actualizar_tabla(self, estado, puntaje_turno, puntaje_total):

        nuevo_puntaje_total = puntaje_total + puntaje_turno
        # Ajustar la recompensa si excede el puntaje máximo de 10,000
        if nuevo_puntaje_total > 10000:
            puntaje_turno = 10000 - puntaje_total

        for estado, accion in self.history:
            self.estados[estado][puntaje_total][accion] += puntaje_turno
            self.estados[estado][puntaje_total]["c_" + accion] += 1
        self.history.clear()

class ElBatoQueSoloCalculaPromediosMasPicados(Jugador):
    def __init__(self, epsilon: float, politica_csv_path):
        self.nombre = "Monte Carlo"
        self.epsilon = epsilon  # e-greedy
        self.history = []

        self.politica_csv_path = politica_csv_path
        self.estados = {}

        # Elimina el archivo si ya existe
        if os.path.exists(self.politica_csv_path):
            os.remove(self.politica_csv_path)

        self._crear_csv()
        self._cargar_estados()

    def _crear_csv(self):
        estados_base = {
            0: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            1: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            2: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            3: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            4: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            5: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
        }

        with open(self.politica_csv_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Escribe el encabezado
            writer.writerow(["estado", "puntuacion", "puntaje_acumulado", "tirar", "plantarse", "c_tirar", "c_plantarse"])
            
            for estado in estados_base.keys():
                for puntuacion in range(0, 10001, 50):
                    for puntaje_acumulado in range(0, 10001, 50):
                        fila = [estado, puntuacion, puntaje_acumulado] + list(estados_base[estado].values())
                        writer.writerow(fila)

    def _cargar_estados(self):
        with open(self.politica_csv_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                estado = int(row["estado"])
                puntuacion = int(row["puntuacion"])
                puntaje_acumulado = int(row["puntaje_acumulado"])
                if estado not in self.estados:
                    self.estados[estado] = {}
                if puntuacion not in self.estados[estado]:
                    self.estados[estado][puntuacion] = {}
                self.estados[estado][puntuacion][puntaje_acumulado] = {
                    "tirar": int(row["tirar"]),
                    "plantarse": int(row["plantarse"]),
                    "c_tirar": int(row["c_tirar"]),
                    "c_plantarse": int(row["c_plantarse"])
                }

    def guardar_estados_en_csv(self):
        """Guarda el contenido de self.estados en el archivo CSV."""
        with open(self.politica_csv_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Escribe el encabezado
            writer.writerow(["estado", "puntuacion", "puntaje_acumulado", "tirar", "plantarse", "c_tirar", "c_plantarse"])
            
            for estado, puntuaciones in self.estados.items():
                for puntuacion, acumulados in puntuaciones.items():
                    for puntaje_acumulado, valores in acumulados.items():
                        fila = [estado, puntuacion, puntaje_acumulado, valores["tirar"], valores["plantarse"], 
                                valores["c_tirar"], valores["c_plantarse"]]
                        writer.writerow(fila)

    def jugar(self, puntaje_total: int, puntaje_turno: int, dados: list[int]):
        (puntaje, no_usados) = puntaje_y_no_usados(dados)
        cant_dados = len(no_usados)
        puntaje_acumulado = puntaje_turno #no tiene lo de la tirada + puntaje???
        # hardcode para probar algo
        if puntaje_turno >= 10000:
        #if puntaje_acumulado + puntaje >= 10000:
            return (JUGADA_PLANTARSE, [])

        if uniform(0, 1) < self.epsilon:  # Acción no greedy
            if uniform(0, 1) > 0.5:
                self.history.append((cant_dados, puntaje_total, puntaje_acumulado, "plantarse"))
                return (JUGADA_PLANTARSE, [])
            else:
                self.history.append((cant_dados, puntaje_total, puntaje_acumulado, "tirar"))
                return (JUGADA_TIRAR, no_usados)
        else:  # Acción greedy
            if (
                self.estados[cant_dados][puntaje_total][puntaje_acumulado]["tirar"] / self.estados[cant_dados][puntaje_total][puntaje_acumulado]["c_tirar"]
                > self.estados[cant_dados][puntaje_total][puntaje_acumulado]["plantarse"]
                / self.estados[cant_dados][puntaje_total][puntaje_acumulado]["c_plantarse"]
            ):
                self.history.append((cant_dados, puntaje_total, puntaje_acumulado, "tirar"))
                return (JUGADA_TIRAR, no_usados)
            elif (
                self.estados[cant_dados][puntaje_total][puntaje_acumulado]["tirar"] / self.estados[cant_dados][puntaje_total][puntaje_acumulado]["c_tirar"]
                < self.estados[cant_dados][puntaje_total][puntaje_acumulado]["plantarse"]
                / self.estados[cant_dados][puntaje_total][puntaje_acumulado]["c_plantarse"]
            ):
                self.history.append((cant_dados, puntaje_total, puntaje_acumulado, "plantarse"))
                return (JUGADA_PLANTARSE, [])
            else:
                if uniform(0, 1) > 0.5:  # Si es igual, se elige aleatoriamente
                    self.history.append((cant_dados, puntaje_total, puntaje_acumulado, "tirar"))
                    return (JUGADA_TIRAR, no_usados)
                else:
                    self.history.append((cant_dados, puntaje_total, puntaje_acumulado, "plantarse"))
                    return (JUGADA_PLANTARSE, [])

    def actualizar_tabla(self, estado, puntaje_turno, puntaje_total):
        nuevo_puntaje_total = puntaje_total + puntaje_turno
        if nuevo_puntaje_total > 10000: 
            puntaje_turno = 10000 - puntaje_total

        for estado, _, puntaje_acum, accion in self.history: # puntaje total deberia ser igual a _, acum no porque es parte del estado
            if puntaje_acum + puntaje_total > 10000:
                puntaje_acum = 10000 - puntaje_total
            self.estados[estado][puntaje_total][puntaje_acum][accion] += puntaje_turno
            self.estados[estado][puntaje_total][puntaje_acum]["c_" + accion] += 1
        self.history.clear()


class ElBatoQueSoloCalculaPromediosPicadosPlus(Jugador):
    def __init__(self, epsilon: float, politica_csv_path):
        self.nombre = "Monte Carlo"
        self.epsilon = epsilon  # e-greedy
        self.history = []

        self.politica_csv_path = politica_csv_path
        self.estados = {}

        # Elimina el archivo si ya existe
        if os.path.exists(self.politica_csv_path):
            os.remove(self.politica_csv_path)

        self._crear_csv()
        self._cargar_estados()

    def _crear_csv(self):
        estados_base = {
            0: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            1: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            2: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            3: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            4: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            5: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
        }

        with open(self.politica_csv_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Escribe el encabezado
            writer.writerow(["estado", "puntuacion", "tirar", "plantarse", "c_tirar", "c_plantarse"])

            for estado in estados_base.keys():
                for puntuacion in range(0, 10001, 50):
                    fila = [estado, puntuacion] + list(estados_base[estado].values())
                    writer.writerow(fila)

    def _cargar_estados(self):
        with open(self.politica_csv_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                estado = int(row["estado"])
                puntuacion = int(row["puntuacion"])
                if estado not in self.estados:
                    self.estados[estado] = {}
                self.estados[estado][puntuacion] = {
                    "tirar": int(row["tirar"]),
                    "plantarse": int(row["plantarse"]),
                    "c_tirar": int(row["c_tirar"]),
                    "c_plantarse": int(row["c_plantarse"])
                }

    def guardar_estados_en_csv(self):
        """Guarda el contenido de self.estados en el archivo CSV."""
        with open(self.politica_csv_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Escribe el encabezado
            writer.writerow(["estado", "puntuacion", "tirar", "plantarse", "c_tirar", "c_plantarse"])

            for estado, puntuaciones in self.estados.items():
                for puntuacion, valores in puntuaciones.items():
                    fila = [estado, puntuacion, valores["tirar"], valores["plantarse"],
                            valores["c_tirar"], valores["c_plantarse"]]
                    writer.writerow(fila)

    # def print_table(self):
    #     for state, rewards in self.estados.items():
    #         reward_plantarse = rewards["plantarse"]
    #         reward_tirar = rewards["tirar"]
    #         avg_reward_plantarse = reward_plantarse / rewards["c_plantarse"]
    #         avg_reward_tirar = reward_tirar / rewards["c_tirar"]
    #         ct = rewards["c_tirar"]
    #         cp = rewards["c_plantarse"]

    #         print(f"State {state}:")
    #         print(f"  Cantidad plantarse: {cp:.2f}")
    #         print(f"  Cantidad tirar: {ct:.2f}")
    #         print(f"  Promedio reward_plantarse: {avg_reward_plantarse:.2f}")
    #         print(f"  Promedio reward_tirar: {avg_reward_tirar:.2f}")

    def jugar(self, puntaje_total: int, puntaje_turno: int, dados: list[int]):
        (puntaje, no_usados) = puntaje_y_no_usados(dados)
        cant_dados = len(no_usados)
        puntaje_acum = puntaje_turno + puntaje

        nuevo_puntaje_total = puntaje_total + puntaje_acum
        # Ajustar la recompensa si excede el puntaje máximo de 10,000
        if nuevo_puntaje_total > 10000:
            puntaje_acum = 10000 - puntaje_total

        if uniform(0, 1) < self.epsilon:  # BUGGG?? tenemos poca entrada no greedy y sube mas greedy 50%
            if uniform(0, 1) > 0.5:
                self.history.append((cant_dados, puntaje_acum,"plantarse"))
                return (JUGADA_PLANTARSE, [])
            else:
                self.history.append((cant_dados, puntaje_acum, "tirar"))
                return (JUGADA_TIRAR, no_usados)

        # if uniform(0, 1) < self.epsilon: #### TOMO DECISION NO GREEDY, CONTRARIA
        #     if (
        #         self.estados[cant_dados][puntaje_total]["tirar"] / self.estados[cant_dados][puntaje_total]["c_tirar"]
        #         > self.estados[cant_dados][puntaje_total]["plantarse"]
        #         / self.estados[cant_dados][puntaje_total]["c_plantarse"]
        #     ):
        #         self.history.append((cant_dados, "plantarse"))
        #         return (JUGADA_PLANTARSE, [])
        #     else:
        #         self.history.append((cant_dados, "tirar"))
        #         return (JUGADA_TIRAR, no_usados)
        else:
            if (
                    self.estados[cant_dados][puntaje_acum]["tirar"] / self.estados[cant_dados][puntaje_acum][
                "c_tirar"]
                    > self.estados[cant_dados][puntaje_acum]["plantarse"]
                    / self.estados[cant_dados][puntaje_acum]["c_plantarse"]
            ):
                self.history.append((cant_dados, puntaje_acum,"tirar"))
                return (JUGADA_TIRAR, no_usados)
            elif (
                    self.estados[cant_dados][puntaje_acum]["tirar"] / self.estados[cant_dados][puntaje_acum][
                "c_tirar"]
                    < self.estados[cant_dados][puntaje_acum]["plantarse"]
                    / self.estados[cant_dados][puntaje_acum]["c_plantarse"]
            ):
                self.history.append((cant_dados, puntaje_acum,"plantarse"))
                return (JUGADA_PLANTARSE, [])
            else:
                if uniform(0, 1) > 0.5:  # si es igual random
                    self.history.append((cant_dados, puntaje_acum,"tirar"))
                    return (JUGADA_TIRAR, no_usados)
                else:
                    self.history.append((cant_dados, puntaje_acum,"plantarse"))
                    return (JUGADA_PLANTARSE, [])
            # elif self.estados[cant_dados][puntaje_total]["tirar"] == 0 and self.estados[cant_dados][puntaje_total]["plantarse"] == 0: # caso inicial random
            #     if uniform(0, 1) > 0.5:
            #         self.history.append((cant_dados, "tirar"))
            #         return (JUGADA_TIRAR, no_usados)
            #     else:
            #         self.history.append((cant_dados, "plantarse"))
            #         return (JUGADA_PLANTARSE, [])
            # else: # es igual? ok me planto mas safe (rebug final)
            #     self.history.append((cant_dados, "plantarse"))
            #     return (JUGADA_PLANTARSE, [])

    def actualizar_tabla(self, estado, puntaje_turno, puntaje_total):

        #nuevo_puntaje_total = puntaje_total + puntaje_turno
        # Ajustar la recompensa si excede el puntaje máximo de 10,000
        #if nuevo_puntaje_total > 10000:
        #    puntaje_turno = 10000 - puntaje_total

        for estado, puntaje_acum,accion in self.history:
            self.estados[estado][puntaje_acum][accion] += puntaje_turno
            self.estados[estado][puntaje_acum]["c_" + accion] += 1
        self.history.clear()


class ElBatoQueSoloCalculaPromediosMasPicados_Upgraded(Jugador):
    def __init__(self, epsilon: float, politica_csv_path):
        self.nombre = "Monte Carlo"
        self.epsilon = epsilon  # e-greedy
        self.history = []

        self.politica_csv_path = politica_csv_path
        self.estados = {}

        # Elimina el archivo si ya existe
        if os.path.exists(self.politica_csv_path):
            os.remove(self.politica_csv_path)

        self._crear_csv()
        self._cargar_estados()

    def _crear_csv(self):
        estados_base = {
            0: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            1: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            2: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            3: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            4: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            5: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
        }

        with open(self.politica_csv_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Escribe el encabezado
            writer.writerow(
                ["estado", "puntuacion", "puntaje_acumulado", "tirar", "plantarse", "c_tirar", "c_plantarse"])

            for estado in estados_base.keys():
                for puntuacion in range(6750, 10001, 250):
                    for puntaje_acumulado in range(0, 10001, 50):
                        fila = [estado, puntuacion, puntaje_acumulado] + list(estados_base[estado].values())
                        writer.writerow(fila)

    def _cargar_estados(self):
        with open(self.politica_csv_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                estado = int(row["estado"])
                puntuacion = int(row["puntuacion"])
                puntaje_acumulado = int(row["puntaje_acumulado"])
                if estado not in self.estados:
                    self.estados[estado] = {}
                if puntuacion not in self.estados[estado]:
                    self.estados[estado][puntuacion] = {}
                self.estados[estado][puntuacion][puntaje_acumulado] = {
                    "tirar": int(row["tirar"]),
                    "plantarse": int(row["plantarse"]),
                    "c_tirar": int(row["c_tirar"]),
                    "c_plantarse": int(row["c_plantarse"])
                }

    def guardar_estados_en_csv(self):
        """Guarda el contenido de self.estados en el archivo CSV."""
        with open(self.politica_csv_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Escribe el encabezado
            writer.writerow(
                ["estado", "puntuacion", "puntaje_acumulado", "tirar", "plantarse", "c_tirar", "c_plantarse"])

            for estado, puntuaciones in self.estados.items():
                for puntuacion, acumulados in puntuaciones.items():
                    for puntaje_acumulado, valores in acumulados.items():
                        fila = [estado, puntuacion, puntaje_acumulado, valores["tirar"], valores["plantarse"],
                                valores["c_tirar"], valores["c_plantarse"]]
                        writer.writerow(fila)

    def _asignar_bin(self, numero):
        # Definir los límites
        bins = np.arange(6750, 10250, 250)  # Bins desde 6750 hasta 10000
        if numero < 6750:
            return 6750
        else:
            # Seleccionar el bin más cercano
            return bins[np.argmin(np.abs(bins - numero))]

    def jugar(self, puntaje_total: int, puntaje_turno: int, dados: list[int]):
        (puntaje, no_usados) = puntaje_y_no_usados(dados)
        cant_dados = len(no_usados)
        puntaje_acumulado = puntaje_turno  # no tiene lo de la tirada + puntaje???
        # hardcode para probar algo
        if puntaje_turno >= 10000:
            # if puntaje_acumulado + puntaje >= 10000:
            return (JUGADA_PLANTARSE, [])

        puntaje_total_binned = self._asignar_bin(puntaje_total)

        if uniform(0, 1) < self.epsilon:  # Acción no greedy
            if uniform(0, 1) > 0.5:
                self.history.append((cant_dados, puntaje_total_binned, puntaje_acumulado, "plantarse"))
                return (JUGADA_PLANTARSE, [])
            else:
                self.history.append((cant_dados, puntaje_total_binned, puntaje_acumulado, "tirar"))
                return (JUGADA_TIRAR, no_usados)
        else:  # Acción greedy
            if (
                    self.estados[cant_dados][puntaje_total_binned][puntaje_acumulado]["tirar"] /
                    self.estados[cant_dados][puntaje_total_binned][puntaje_acumulado]["c_tirar"]
                    > self.estados[cant_dados][puntaje_total_binned][puntaje_acumulado]["plantarse"]
                    / self.estados[cant_dados][puntaje_total_binned][puntaje_acumulado]["c_plantarse"]
            ):
                self.history.append((cant_dados, puntaje_total_binned, puntaje_acumulado, "tirar"))
                return (JUGADA_TIRAR, no_usados)
            elif (
                    self.estados[cant_dados][puntaje_total_binned][puntaje_acumulado]["tirar"] /
                    self.estados[cant_dados][puntaje_total_binned][puntaje_acumulado]["c_tirar"]
                    < self.estados[cant_dados][puntaje_total_binned][puntaje_acumulado]["plantarse"]
                    / self.estados[cant_dados][puntaje_total_binned][puntaje_acumulado]["c_plantarse"]
            ):
                self.history.append((cant_dados, puntaje_total_binned, puntaje_acumulado, "plantarse"))
                return (JUGADA_PLANTARSE, [])
            else:
                if uniform(0, 1) > 0.5:  # Si es igual, se elige aleatoriamente
                    self.history.append((cant_dados, puntaje_total_binned, puntaje_acumulado, "tirar"))
                    return (JUGADA_TIRAR, no_usados)
                else:
                    self.history.append((cant_dados, puntaje_total_binned, puntaje_acumulado, "plantarse"))
                    return (JUGADA_PLANTARSE, [])

    def actualizar_tabla(self, estado, puntaje_turno, puntaje_total):

        nuevo_puntaje_total = puntaje_total + puntaje_turno
        if nuevo_puntaje_total > 10000:
            puntaje_turno = 10000 - puntaje_total

        puntaje_total_binned = self._asignar_bin(puntaje_total)

        for estado, _, puntaje_acum, accion in self.history:  # puntaje total deberia ser igual a _, acum no porque es parte del estado
            if puntaje_acum + puntaje_total > 10000:
                puntaje_acum = 10000 - puntaje_total
            self.estados[estado][puntaje_total_binned][puntaje_acum][accion] += puntaje_turno
            self.estados[estado][puntaje_total_binned][puntaje_acum]["c_" + accion] += 1
        self.history.clear()


class ElBatoQueSoloCalculaPromediosMasPicados_UpgradedAll(Jugador):
    def __init__(self, epsilon: float, politica_csv_path):
        self.nombre = "Monte Carlo"
        self.epsilon = epsilon  # e-greedy
        self.history = []

        self.politica_csv_path = politica_csv_path
        self.estados = {}

        # Elimina el archivo si ya existe
        if os.path.exists(self.politica_csv_path):
            os.remove(self.politica_csv_path)

        self._crear_csv()
        self._cargar_estados()

    def _crear_csv(self):
        estados_base = {
            0: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            1: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            2: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            3: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            4: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
            5: {"tirar": 0, "plantarse": 0, "c_tirar": 1, "c_plantarse": 1},
        }

        with open(self.politica_csv_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Escribe el encabezado
            writer.writerow(
                ["estado", "puntuacion", "puntaje_acumulado", "tirar", "plantarse", "c_tirar", "c_plantarse"])

            for estado in estados_base.keys():
                for puntuacion in range(0, 10001, 1000):
                    for puntaje_acumulado in range(0, 10001, 50):
                        fila = [estado, puntuacion, puntaje_acumulado] + list(estados_base[estado].values())
                        writer.writerow(fila)

    def _cargar_estados(self):
        with open(self.politica_csv_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                estado = int(row["estado"])
                puntuacion = int(row["puntuacion"])
                puntaje_acumulado = int(row["puntaje_acumulado"])
                if estado not in self.estados:
                    self.estados[estado] = {}
                if puntuacion not in self.estados[estado]:
                    self.estados[estado][puntuacion] = {}
                self.estados[estado][puntuacion][puntaje_acumulado] = {
                    "tirar": int(row["tirar"]),
                    "plantarse": int(row["plantarse"]),
                    "c_tirar": int(row["c_tirar"]),
                    "c_plantarse": int(row["c_plantarse"])
                }

    def guardar_estados_en_csv(self):
        """Guarda el contenido de self.estados en el archivo CSV."""
        with open(self.politica_csv_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Escribe el encabezado
            writer.writerow(
                ["estado", "puntuacion", "puntaje_acumulado", "tirar", "plantarse", "c_tirar", "c_plantarse"])

            for estado, puntuaciones in self.estados.items():
                for puntuacion, acumulados in puntuaciones.items():
                    for puntaje_acumulado, valores in acumulados.items():
                        fila = [estado, puntuacion, puntaje_acumulado, valores["tirar"], valores["plantarse"],
                                valores["c_tirar"], valores["c_plantarse"]]
                        writer.writerow(fila)

    def _asignar_bin(self, numero):
        # Definir los límites
        bins = np.arange(0, 11000, 1000)  # Bins desde 6750 hasta 10000
        return bins[np.argmin(np.abs(bins - numero))]

    def jugar(self, puntaje_total: int, puntaje_turno: int, dados: list[int]):
        (puntaje, no_usados) = puntaje_y_no_usados(dados)
        cant_dados = len(no_usados)
        puntaje_acumulado = puntaje_turno  # no tiene lo de la tirada + puntaje???
        # hardcode para probar algo
        if puntaje_turno >= 10000:
            # if puntaje_acumulado + puntaje >= 10000:
            return (JUGADA_PLANTARSE, [])

        puntaje_total_binned = self._asignar_bin(puntaje_total)

        if uniform(0, 1) < self.epsilon:  # Acción no greedy
            if uniform(0, 1) > 0.5:
                self.history.append((cant_dados, puntaje_total_binned, puntaje_acumulado, "plantarse"))
                return (JUGADA_PLANTARSE, [])
            else:
                self.history.append((cant_dados, puntaje_total_binned, puntaje_acumulado, "tirar"))
                return (JUGADA_TIRAR, no_usados)
        else:  # Acción greedy
            if (
                    self.estados[cant_dados][puntaje_total_binned][puntaje_acumulado]["tirar"] /
                    self.estados[cant_dados][puntaje_total_binned][puntaje_acumulado]["c_tirar"]
                    > self.estados[cant_dados][puntaje_total_binned][puntaje_acumulado]["plantarse"]
                    / self.estados[cant_dados][puntaje_total_binned][puntaje_acumulado]["c_plantarse"]
            ):
                self.history.append((cant_dados, puntaje_total_binned, puntaje_acumulado, "tirar"))
                return (JUGADA_TIRAR, no_usados)
            elif (
                    self.estados[cant_dados][puntaje_total_binned][puntaje_acumulado]["tirar"] /
                    self.estados[cant_dados][puntaje_total_binned][puntaje_acumulado]["c_tirar"]
                    < self.estados[cant_dados][puntaje_total_binned][puntaje_acumulado]["plantarse"]
                    / self.estados[cant_dados][puntaje_total_binned][puntaje_acumulado]["c_plantarse"]
            ):
                self.history.append((cant_dados, puntaje_total_binned, puntaje_acumulado, "plantarse"))
                return (JUGADA_PLANTARSE, [])
            else:
                if uniform(0, 1) > 0.5:  # Si es igual, se elige aleatoriamente
                    self.history.append((cant_dados, puntaje_total_binned, puntaje_acumulado, "tirar"))
                    return (JUGADA_TIRAR, no_usados)
                else:
                    self.history.append((cant_dados, puntaje_total_binned, puntaje_acumulado, "plantarse"))
                    return (JUGADA_PLANTARSE, [])

    def actualizar_tabla(self, estado, puntaje_turno, puntaje_total):

        nuevo_puntaje_total = puntaje_total + puntaje_turno
        if nuevo_puntaje_total > 10000:
            puntaje_turno = 10000 - puntaje_total

        puntaje_total_binned = self._asignar_bin(puntaje_total)

        for estado, _, puntaje_acum, accion in self.history:  # puntaje total deberia ser igual a _, acum no porque es parte del estado
            if puntaje_acum + puntaje_total > 10000:
                puntaje_acum = 10000 - puntaje_total
            self.estados[estado][puntaje_total_binned][puntaje_acum][accion] += puntaje_turno
            self.estados[estado][puntaje_total_binned][puntaje_acum]["c_" + accion] += 1
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
