#Desarrollo del juego principal
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