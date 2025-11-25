#Desarrollo del juego principal
#
#
import pygame
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
    def permiteJugador(self):
        return True
    
    def permiteCazador(self):
        return True


class Muro(Terreno):
    def permiteJugador(self):
        return False
    
    def permiteCazador(self):
        return False


class Liana(Terreno):
    def permiteJugador(self):
        return False
    
    def permiteCazador(self):
        return True


class Tunel(Terreno):
    def permiteJugador(self):
        return True
    
    def permiteCazador(self):
        return False
