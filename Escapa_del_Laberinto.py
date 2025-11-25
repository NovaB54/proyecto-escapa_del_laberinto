#Desarrollo del juego principal
#
#
import pygame
import random
#
#
#Clase Terreno para hacer variedad de casillas

class Terreno:
    def __init__(self, fila, columna):

        self.fila = fila
        self.columna = columna

    def permiteJugador(self):
        return False

    def permiteCazador(self):
        return False

#hijos de Terrenos (Todas las casillas que van a existir)

class Camino(Terreno):
    def __init__(self, fila, columna):
        super().__init__(self, fila, columna) #se llama super para que las clases hijos llamen al del padre automáticamente y porque nos habia dado problemas mas adelante con ImprimirMapa.

    def permiteJugador(self):
        return True
    
    def permiteCazador(self):
        return True


class Muro(Terreno):
    def __init__(self, fila, columna):
        super().__init__(fila, columna)


class Liana(Terreno):
    def __init__(self, fila, columna):
        super().__init__(fila, columna)
    
    def permiteCazador(self):
        return True


class Tunel(Terreno):
    def __init__(self, fila, columna):
        super().__init__(fila, columna)
    
    def permiteJugador(self):
        return False

#Clase Mapa para generar la matriz laberinto

class Mapa:
    def __init__(self, filas=10, columnas=10):

        self.filas=filas
        self.columnas=columnas
        self.matriz=[[None for _ in range(columnas)] for _ in range(filas)]

    def obtenerTerreno(self, fila, columna):

        if self.dentroDeLimites(fila, columna):
            return self.matriz[fila][columna]
        return None

    def dentroDeLimites(self, fila, columna):
        return 0<=fila<self.filas and 0<=columna<self.columnas
    
    def generarAleatorio(self):
        casillas=[Camino,Muro,Liana,Tunel]
        for i in range(self.filas):
            for j in range(self.columnas):
                Es=random.choice(casillas)
                self.matriz[i][j]=Es(i,j)
    
    def imprimirMapa(self):
        for fila in self.matriz:
            linea=""
            for casilla in fila:
                letra=casilla.__class__.__name__[0]
                linea+=letra+""
            print(linea)

