#Desarrollo del juego principal
#
#
import pygame
import random
import time
#
#
#Clase Terreno para hacer variedad de casillas

class Terreno:
    def __init__(self, fila, columna):
        self.fila=fila
        self.columna=columna

    def permiteJugador(self):
        return False

    def permiteCazador(self):
        return False

#hijos de Terrenos (Todas las casillas que van a existir)

class Camino(Terreno):
    def __init__(self, fila, columna):
        super().__init__(fila, columna) #se llama super para que las clases hijos llamen al del padre automáticamente y porque nos habia dado problemas mas adelante con ImprimirMapa.

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
        return True

#clase Mapa para generar la matriz del laberinto

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
                letra=casilla.__class__.__name__[0] #con esta variable se agarra la primera letra de las clases, Camino, entonces toma C
                linea+=letra+""
            print(linea)

#clase Entidad para agregar jugador y cazadores

class Entidad:
    def __init__(self, fila, columna, mapa):
        self.fila=fila
        self.columna=columna
        self.mapa=mapa
    
    def puedeMover(self, filanew, columnanew):
        if not self.mapa.dentroDeLimite(filanew, columnanew):
            return False
        return True
    
    def mover(self, nfilas, ncolumnas):
        filanew=self.fila+nfilas
        columnanew=self.columna+ncolumnas

        if self.puedeMoverA(filanew, columnanew):
            self.fila=filanew
            self.columna=columnanew

#clase Trampa para las trampas del jugador

class Trampa:
    def __init__(self, fila, columna, mapa):
        self.fila=fila
        self.columna=columna
        self.mapa=mapa
        self.activa=True

#clase Jugador(hijo de entidad)

class Jugador(Entidad):
    def __init__(self, fila, columna, mapa):
        super().__init__(fila, columna, mapa)

        self.energia=100
        self.energiamax=100
        self.trampas=[]
        self.ultimo=0
        self.recarga=5
        self.trampasmax=3
    
    def puedeMover(self, filanew, columnanew):
        if not self.mapa.dentroDeLimites(filanew, columnanew):
            return False
        
        terreno=self.mapa.obtenerTerreno(filanew, columnanew)
        if not terreno.permiteJugador():
            return False
        return True

    def correr(self, nfilas, ncolumnas):
        if self.energia<=0:
            return
        
        filasegui=self.fila+nfilas*2
        columnasegui=self.columna+ncolumnas*2
        self.energia-=1

        if self.puedeMover(filasegui, columnasegui):
            self.fila=filasegui
            self.columna=columnasegui

    def recuperarEnergia(self):
        if self.energia<self.energiamax:
            self.energia+=1

    def colocarTrampa(self):
        quieromitiempo=time.time()

        if quieromitiempo-self.ultimo<self.recarga:
            return
        
        if len(self.trampas)>=self.trampasmax:
            return
        
        trampa=Trampa(self.fila, self.columna, self.mapa)
        self.trampas.append(trampa)
        self.ultimo=quieromitiempo

    def limpiarTrampas(self):
        trampas=[]
        for t in self.trampas:
            if t.activa:
                trampas.append(t)
        self.trampas=trampas

#clase Cazador (hijo)

class Cazador(Entidad):
    def __init__(self, fila, columna, mapa):
        super().__init__(fila, columna, mapa)

    def puedeMoverA(self, nuevaFila, nuevaColumna):
        if not self.mapa.dentroDeLimites(nuevaFila, nuevaColumna):
            return False

        terreno=self.mapa.obtenerTerreno(nuevaFila, nuevaColumna)
        return terreno.permiteCazador()

    #se aplica bfs para encontrar al jugador de la forma mas rapida
    def bfs(self, jugador):
        inicio=(self.fila, self.columna)
        objetivo=(jugador.fila, jugador.columna)

        if inicio==objetivo:
            return None  

        cola=[inicio]
        visitado=[[False for _ in range(self.mapa.columnas)] for _ in range(self.mapa.filas)]

        padre=[[None for _ in range(self.mapa.columnas)] for _ in range(self.mapa.filas)]

        visitado[inicio[0]][inicio[1]]=True

        semueve=[(1,0), (-1,0), (0,1), (0,-1)]

        #bfs clasiquito
        while cola:

            f, c=cola.pop(0)
            if (f, c)==objetivo:
                break

            for fs, cs in semueve:
                ffs= f+fs
                ccs= c+cs
                if self.mapa.dentroDeLimites(ffs, ccs) and not visitado[ffs][ccs]:
                    terreno=self.mapa.obtenerTerreno(ffs, ccs)
                    if terreno.permiteCazador():
                        visitado[ffs][ccs]=True
                        padre[ffs][ccs]=(f, c)
                        cola.append((ffs, ccs))

        
        if not visitado[objetivo[0]][objetivo[1]]:
            return None

        camino=[]
        paso=objetivo

        while paso!=inicio:
            camino.append(paso)
            paso=padre[paso[0]][paso[1]]
        camino.reverse()

        return camino
    
    def perseguir(self, jugador):
        camino=self.bfs(jugador)

        if camino==None or len(camino)==0:
            return
        siguiente=camino[0]
        self.fila, self.columna=siguiente

    def verificarTrampa(self, jugador):
        for t in jugador.trampas:
            if t.activa and t.fila==self.fila and t.columna==self.columna:
                t.activa=False
                return True
        return False
    
#falta clase Juego