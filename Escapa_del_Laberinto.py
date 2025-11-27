#Desarrollo del juego principal
#
#
import random
import time
import os
import json
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
    
    def permiteTrampa(self):
        return False

#hijos de Terrenos (Todas las casillas que van a existir)

class Camino(Terreno):
    def __init__(self, fila, columna):
        super().__init__(fila, columna) #se llama super para que las clases hijos llamen al del padre automáticamente y porque nos habia dado problemas mas adelante con ImprimirMapa.

    def permiteJugador(self):
        return True
    
    def permiteCazador(self):
        return True
    
    def permiteTrampa(self):
        return True
    
class Muro(Terreno):
    pass

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
        self.salida=(filas-1,columnas-1)
    #hacer que siempre alla un camino y sea de forma aleatoria con dfs
    def generarAleatorio(self):
        for f in range(self.filas):
            for c in range(self.columnas):
                self.matriz[f][c]=Muro(f,c)

        self.matriz[0][0]=Camino(0,0)
        self.matriz[self.filas-1][self.columnas-1]=Camino(self.filas-1,self.columnas-1)

        def crearLab(f_act,c_act,visitados):
            visitados.append((f_act,c_act))
            self.matriz[f_act][c_act]=Camino(f_act,c_act)

            dirs=[(-2,0),(0,2),(2,0),(0,-2)]
            random.shuffle(dirs)

            for df,dc in dirs:
                nf=f_act+df
                nc=c_act+dc
                if 0<=nf<self.filas and 0<=nc<self.columnas:
                    visitado=(nf,nc) in visitados
                    es_muro=self.matriz[nf][nc].permiteJugador()==False and self.matriz[nf][nc].permiteCazador()==False
                    if not visitado and es_muro:
                        pf=f_act+df//2
                        pc=c_act+dc//2
                        if 0<=pf<self.filas and 0<=pc<self.columnas:
                            self.matriz[pf][pc]=Camino(pf,pc)
                        crearLab(nf,nc,visitados)

        visitados=[]
        crearLab(0,0,visitados)

        while not self.verificarConexion():
            self.__init__(self.filas,self.columnas)
            self.generarAleatorio()
            return

        self.conectarSalida()
    
        self.agregarTuneles()
        self.agregarLianas()

        if not self.verificarConexion():
            self.conectarSalida()

    def conectarSalida(self):
        fs,cs=self.salida
        
        if not self.salidaConectada():
            punto_cercano=None
            for dist in range(1,6):
                for dc in range(-dist,dist+1):
                    for df in range(-dist,dist+1):
                        if abs(dc)+abs(df)==dist:
                            fv=fs+df
                            cv=cs+dc
                            if (0<=fv<self.filas and 0<=cv<self.columnas and
                                (self.matriz[fv][cv].permiteJugador() or self.matriz[fv][cv].permiteCazador())):
                                punto_cercano=(fv,cv)
                                break
                    if punto_cercano:
                        break
                if punto_cercano:
                    break
            
            if punto_cercano:
                self.crearCamino(punto_cercano,self.salida)

    def salidaConectada(self):
        fs,cs=self.salida
        for df,dc in [(0,1),(1,0),(0,-1),(-1,0)]:
            fv=fs+df
            cv=cs+dc
            if (0<=fv<self.filas and 0<=cv<self.columnas and
                (self.matriz[fv][cv].permiteJugador() or self.matriz[fv][cv].permiteCazador())):
                return True
        return False

    def crearCamino(self,inicio,fin):
        fa,ca=inicio
        while (fa,ca)!=fin:
            if fa<fin[0]:
                fa+=1
            elif fa>fin[0]:
                fa-=1
            elif ca<fin[1]:
                ca+=1
            elif ca>fin[1]:
                ca-=1
            
            es_muro=self.matriz[fa][ca].permiteJugador()==False and self.matriz[fa][ca].permiteCazador()==False
            if es_muro:
                self.matriz[fa][ca]=Camino(fa,ca)

    def agregarTuneles(self):
        cont=0
        for f in range(1,self.filas-1):
            for c in range(1,self.columnas-1):
                es_camino=self.matriz[f][c].permiteJugador() and self.matriz[f][c].permiteCazador()
                if cont<5 and es_camino:
                    if random.random()<0.05:
                        no_inicio=(f,c)!=(0,0)
                        no_salida=(f,c)!=(self.filas-1,self.columnas-1)
                        if no_inicio and no_salida:
                            self.matriz[f][c]=Tunel(f,c)
                            cont+=1

    def agregarLianas(self):
        cont=0
        for f in range(1,self.filas-1):
            for c in range(1,self.columnas-1):
                es_muro=self.matriz[f][c].permiteJugador()==False and self.matriz[f][c].permiteCazador()==False
                if cont<8 and es_muro:
                    if random.random()<0.04:
                        tiene_vecino=False
                        for df,dc in [(0,1),(1,0),(0,-1),(-1,0)]:
                            fv=f+df
                            cv=c+dc
                            if 0<=fv<self.filas and 0<=cv<self.columnas:
                                vecino_transitable=self.matriz[fv][cv].permiteJugador() or self.matriz[fv][cv].permiteCazador()
                                if vecino_transitable:
                                    tiene_vecino=True
                                    break
                    
                        if tiene_vecino:
                            self.matriz[f][c]=Liana(f,c)
                            cont+=1

    def verificarConexion(self):
        inicio_transitable=self.matriz[0][0].permiteJugador()

        if not inicio_transitable:
            return False
        
        visitados=[[False]*self.columnas for _ in range(self.filas)]
        cola=[]
        cola.append((0,0))
        visitados[0][0]=True
        
        while cola:
            fa,ca=cola.pop(0)
            if (fa,ca)==(self.filas-1,self.columnas-1):
                return True
            
            for df,dc in [(0,1),(1,0),(0,-1),(-1,0)]:
                fv=fa+df
                cv=ca+dc

                if (0<=fv<self.filas and 0<=cv<self.columnas and not visitados[fv][cv] and self.matriz[fv][cv].permiteJugador()):
                    visitados[fv][cv]=True
                    cola.append((fv,cv))
        
        return False

    def enLimites(self,f,c):
        return 0<=f<self.filas and 0<=c<self.columnas

    def obtenerTerreno(self,f,c):
        if self.enLimites(f,c):
            return self.matriz[f][c]
        return None

    def imprimir(self):
        for fila in self.matriz:
            linea=""
            for casilla in fila:
                letra=casilla.__class__.__name__[0] #con esta variable se agarra la primera letra de las clases, Camino, entonces toma C
                linea+=letra+" "
            print(linea)

#clase Entidad para agregar jugador y cazadores

class Entidad:
    def __init__(self, fila, columna, mapa, semueve):
        self.fila=fila
        self.columna=columna
        self.mapa=mapa
        self.semueve=semueve
    
    def puedeMover(self, filanew, columnanew):
        if not self.mapa.enLimites(filanew, columnanew):
            return False
        
        terreno=self.mapa.obtenerTerreno(filanew, columnanew)
        if self.semueve=="juega":
            return terreno.permiteJugador()
        elif self.semueve=="caza":
            return terreno.permiteCazador()
        return False

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
        super().__init__(fila, columna, mapa, 'juega')

        self.energia=100
        self.energiamax=100
        self.trampas=[]
        self.ultimo=0
        self.recarga=5
        self.trampasmax=3
    
    def correr(self, nfilas, ncolumnas):
        if self.energia<=0:
            return False
        
        filasegui=self.fila+nfilas*2
        columnasegui=self.columna+ncolumnas*2

        if self.puedeMover(filasegui, columnasegui):
            self.fila=filasegui
            self.columna=columnasegui
            self.energia-=10
            return True
        return False

    def recuperarEnergia(self):
        if self.energia<self.energiamax:
            self.energia+=5

    def colocarTrampa(self, modo):
        if modo!="escape":
            return False

        ahora=time.time()
        if ahora-self.ultimo<self.recarga:
            return False
        
        if len(self.trampas)>=self.trampasmax:
            return False
        
        terreno=self.mapa.obtenerTerreno(self.fila, self.columna)
        if not terreno.permiteTrampa():
            return False
        
        trampa=Trampa(self.fila, self.columna, self.mapa)
        self.trampas.append(trampa)
        self.ultimo=ahora
        return True

    def limpiarTrampas(self):
        self.trampas=[i for i in self.trampas if i.activa]

    def mover(self, df, dc):
        nueva_fila=self.fila+df
        nueva_columna=self.columna+dc
        
        if self.puedeMover(nueva_fila, nueva_columna):
            self.fila=nueva_fila
            self.columna=nueva_columna
            return True
        return False

    def estaEnSalida(self):
        return (self.fila, self.columna)==self.mapa.salida

#clase Cazador (hijo)

class Cazador(Entidad):
    def __init__(self, fila, columna, mapa):
        super().__init__(fila, columna, mapa, 'caza')
        self.vivo=True
        self.t_muerte=None

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

                if self.mapa.enLimites(ffs, ccs) and not visitado[ffs][ccs]:
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
        if self.puedeMover(siguiente[0], siguiente[1]):
            self.fila, self.columna=siguiente

    def huir(self, jugador):
        opciones=[(0,0),(1,0),(-1,0),(0,1),(0,-1)]
        mejor_dist=-1
        mejor_pos=(self.fila,self.columna)

        for df,dc in opciones:
            nf=self.fila+df
            nc=self.columna+dc
            if self.puedeMover(nf,nc):
                dist=abs(nf-jugador.fila)+abs(nc-jugador.columna)
                if dist>mejor_dist:
                    mejor_dist=dist
                    mejor_pos=(nf,nc)

        self.fila,self.columna=mejor_pos

    def verificarTrampa(self, jugador):
        for t in jugador.trampas:
            if t.activa and t.fila==self.fila and t.columna==self.columna:
                t.activa=False
                return True
        return False
    
    def resurgir(self, jugador):
        posiciones_validas=[]
        for i in range(self.mapa.filas):
            for j in range(self.mapa.columnas):
                terreno=self.mapa.obtenerTerreno(i,j)
                if (terreno.permiteCazador() and 
                    abs(i-jugador.fila)+abs(j-jugador.columna)>5):
                    posiciones_validas.append((i,j))

        if posiciones_validas:
            self.fila, self.columna=random.choice(posiciones_validas)

#clase juego principal para que funcionen las demas clases juntas
class Juego:
    def __init__(self, filas=10, columnas=10, cantidad_cazadores=2, modo="escape", nombre_jugador="Jugador"):
        self.mapa=Mapa(filas,columnas)
        self.mapa.generarAleatorio()

        self.nombre_jugador=nombre_jugador

        self.jugador=Jugador(0,0,self.mapa)
        
        if modo=="cazador":
            self.jugador.recarga=999999
            self.jugador.trampasmax=0
        
        self.cazadores=[]
        for _ in range(cantidad_cazadores):
            f,c=self.buscar_posicion_cazador()
            self.cazadores.append(Cazador(f,c,self.mapa))

        self.juego_terminado=False
        self.resultado=None
        self.modo=modo
        self.tiempo_inicio=time.time()
        self.puntos=0

        self.cazadores_capturados=0
        self.meta_cazadores=5
        self.puntos_perdida_salida=50
        self.puntos_ganancia_captura=self.puntos_perdida_salida*2
        self.bono_trampa=20

    def registrar_puntaje(self):
        if not self.juego_terminado:
            return

        puntajes=cargar_puntajes()

        if self.modo not in puntajes:
            puntajes[self.modo]=[]

        entrada={
            "nombre":self.nombre_jugador,
            "puntos":self.puntos,
            "tiempo":int(self.obtener_tiempo_transcurrido()),
            "resultado":self.resultado
        }
        puntajes[self.modo].append(entrada)

        puntajes[self.modo].sort(key=lambda x:x["puntos"],reverse=True)

        puntajes[self.modo]=puntajes[self.modo][:5]

        guardar_puntajes(puntajes)

    @staticmethod
    def obtener_top5(modo):
        puntajes=cargar_puntajes()
        if modo not in puntajes:
            return []
        return puntajes[modo]

    def buscar_posicion_cazador(self):
        intentos=0
        while intentos<50:
            fila=random.randint(0,self.mapa.filas-1)
            columna=random.randint(0,self.mapa.columnas-1)
            terreno=self.mapa.obtenerTerreno(fila,columna)
            
            if terreno.permiteCazador():
                return fila,columna
            intentos+=1
        
        for i in range(self.mapa.filas):
            for j in range(self.mapa.columnas):
                terreno=self.mapa.obtenerTerreno(i,j)
                if terreno.permiteCazador():
                    return i,j
        return self.mapa.filas-1,self.mapa.columnas-1

    def mover_jugador(self, df, dc):
        if self.juego_terminado:
            return False

        exito=self.jugador.mover(df,dc)
        if exito:
            self.verificar_estado()
        return exito

    def correr_jugador(self, df, dc):
        if self.juego_terminado:
            return False

        exito=self.jugador.correr(df,dc)
        if exito:
            self.verificar_estado()
        return exito

    def colocar_trampa(self):
        if self.juego_terminado:
            return False

        return self.jugador.colocarTrampa(self.modo)

    def actualizar_cazadores(self):
        if self.juego_terminado:
            return

        ahora=time.time()

        for cazador in self.cazadores:
            if self.modo=="escape":
                if not cazador.vivo:
                    if cazador.t_muerte is not None and ahora-cazador.t_muerte>=10:
                        cazador.resurgir(self.jugador)
                        cazador.vivo=True
                        cazador.t_muerte=None
                    continue

                if cazador.verificarTrampa(self.jugador):
                    cazador.vivo=False
                    cazador.t_muerte=ahora
                    self.puntos+=self.bono_trampa
                    continue

                cazador.perseguir(self.jugador)
            else:
                cazador.huir(self.jugador)

        self.verificar_estado()

    def verificar_estado(self):
        if self.modo=="escape":
            self._verificar_modo_escape()
        else:
            self._verificar_modo_cazador()

    def _verificar_modo_escape(self):
        if self.jugador.estaEnSalida():
            self.juego_terminado=True
            self.resultado="ganaste"
            self.puntos=self.calcular_puntos_escape()
            self.registrar_puntaje()
            return

        for cazador in self.cazadores:
            if (cazador.vivo and
                cazador.fila==self.jugador.fila and
                cazador.columna==self.jugador.columna):
                self.juego_terminado=True
                self.resultado="perdiste"
                self.registrar_puntaje()
                return

    def _verificar_modo_cazador(self):
        for cazador in self.cazadores:
            if (cazador.fila,cazador.columna)==self.mapa.salida:
                self.puntos-=self.puntos_perdida_salida
                if self.puntos<0:
                    self.puntos=0
                cazador.resurgir(self.jugador)

        for cazador in self.cazadores:
            if (self.jugador.fila==cazador.fila and
                self.jugador.columna==cazador.columna):
                self.cazadores_capturados+=1
                self.puntos+=self.puntos_ganancia_captura
                cazador.resurgir(self.jugador)
                break

        if self.cazadores_capturados>=self.meta_cazadores:
            self.juego_terminado=True
            self.resultado="ganaste"
            self.registrar_puntaje()
            return

        if self.jugador.energia<=0:
            self.juego_terminado=True
            self.resultado="perdiste"
            self.registrar_puntaje()
            return

    def calcular_puntos_escape(self):
        tiempo_transcurrido=time.time()-self.tiempo_inicio
        puntos_tiempo=max(0,1000-int(tiempo_transcurrido)*10)
        puntos_energia=self.jugador.energia*2
        factor_dificultad=1+(len(self.cazadores)-1)*0.5
        return int((puntos_tiempo+puntos_energia)*factor_dificultad)

    def obtener_estado_juego(self):
        return {
            "energia":self.jugador.energia,
            "trampas_activas":len([t for t in self.jugador.trampas if t.activa]),
            "trampas_max":self.jugador.trampasmax,
            "puntos":self.puntos,
            "cazadores_restantes":len(self.cazadores),
            "cazadores_capturados":self.cazadores_capturados,
            "tiempo":int(self.obtener_tiempo_transcurrido())
        }

    def obtener_tiempo_transcurrido(self):
        return time.time()-self.tiempo_inicio

    def tick(self):
        if not self.juego_terminado:
            self.jugador.recuperarEnergia()
            self.jugador.limpiarTrampas()
            self.actualizar_cazadores()
            
            if self.modo=="cazador" and not self.juego_terminado:
                self.puntos+=1

    def reiniciar(self, modo=None, nombre_jugador=None):
        if modo:
            self.modo=modo
        if nombre_jugador is None:
            nombre_jugador=self.nombre_jugador
            
        self.__init__(
            filas=self.mapa.filas,
            columnas=self.mapa.columnas,
            cantidad_cazadores=len(self.cazadores),
            modo=self.modo,
            nombre_jugador=nombre_jugador
        )

#funciones aparte para guardar los registros de puntajes en un archivo
archivo_puntos="puntajes.json"

def cargar_puntajes():
    if not os.path.exists(archivo_puntos):
        return {"escape": [], "cazador": []}

    archivo=open(archivo_puntos, "r")
    contenido=archivo.read()
    archivo.close()

    if contenido.strip()=="":
        return {"escape": [], "cazador": []}

    return json.loads(contenido)


def guardar_puntajes(puntajes):
    texto=json.dumps(puntajes, indent=4)
    archivo=open(archivo_puntos, "w")
    archivo.write(texto)
    archivo.close()
