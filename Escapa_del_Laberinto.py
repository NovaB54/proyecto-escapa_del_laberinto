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
    def __init__(self,fila,columna):
        self.fila=fila
        self.columna=columna

    def permiteJugador(self):
        return False

    def permiteCazador(self):
        return False
    
    def permiteTrampa(self):
        return False

#hijos de Terrenos todas las casillas que van a existir

class Camino(Terreno):
    def __init__(self,fila,columna):
        super().__init__(fila,columna)

    def permiteJugador(self):
        return True
    
    def permiteCazador(self):
        return True
    
    def permiteTrampa(self):
        return True

class Muro(Terreno):
    pass

class Liana(Terreno):
    def __init__(self,fila,columna):
        super().__init__(fila,columna)
    
    def permiteCazador(self):
        return True

class Tunel(Terreno):
    def __init__(self,fila,columna):
        super().__init__(fila,columna)
    
    def permiteJugador(self):
        return True

class Salida(Terreno):
    def __init__(self,fila,columna):
        super().__init__(fila,columna)
    
    def permiteJugador(self):
        return True

#clase Mapa para generar la matriz del laberinto

class Mapa:
    def __init__(self,ancho,alto):
        self.ancho=ancho
        self.alto=alto
        self.filas=alto
        self.columnas=ancho
        self.matriz=[]
        self.salida=(alto-2,ancho-2)
        self.generar_mapa()

    def generar_mapa(self):
        self.matriz=[[Muro(y,x) for x in range(self.ancho)] for y in range(self.alto)]

        def crear_laberinto(y,x,visitados):
            visitados.add((y,x))
            self.matriz[y][x]=Camino(y,x)

            direcciones=[(-2,0),(0,2),(2,0),(0,-2)]
            random.shuffle(direcciones)

            for dy,dx in direcciones:
                ny,nx=y+dy,x+dx
                if 1<=ny<self.alto-1 and 1<=nx<self.ancho-1:
                    if(ny,nx)not in visitados:
                        pared_y=y+dy//2
                        pared_x=x+dx//2
                        self.matriz[pared_y][pared_x]=Camino(pared_y,pared_x)
                        crear_laberinto(ny,nx,visitados)

        visitados=set()
        crear_laberinto(1,1,visitados)

        for i in range(1,self.alto-1):
            if isinstance(self.matriz[i][self.ancho-3],Camino):
                self.matriz[i][self.ancho-2]=Camino(i,self.ancho-2)

        for i in range(1,self.ancho-1):
            if isinstance(self.matriz[self.alto-3][i],Camino):
                self.matriz[self.alto-2][i]=Camino(self.alto-2,i)

        for intento in range(40):
            y=random.randint(2,self.alto-3)
            x=random.randint(2,self.ancho-3)

            if isinstance(self.matriz[y][x],Muro):
                vecinos_camino=0
                for dy,dx in[(0,1),(1,0),(0,-1),(-1,0)]:
                    ny,nx=y+dy,x+dx
                    if 0<=ny<self.alto and 0<=nx<self.ancho:
                        if isinstance(self.matriz[ny][nx],Camino):
                            vecinos_camino+=1
                if vecinos_camino==2:
                    self.matriz[y][x]=Camino(y,x)

        tuneles_creados=0
        for y in range(2,self.alto-2):
            for x in range(2,self.ancho-2):
                if tuneles_creados<4 and isinstance(self.matriz[y][x],Camino):
                    if random.random()<0.015:
                        if not((y<4 and x<4)or(y>self.alto-5 and x>self.ancho-5)):
                            self.matriz[y][x]=Tunel(y,x)
                            tuneles_creados+=1

        lianas_creadas=0
        for y in range(2,self.alto-2):
            for x in range(2,self.ancho-2):
                if lianas_creadas<8 and isinstance(self.matriz[y][x],Muro):
                    if random.random()<0.02:
                        tiene_vecino=False
                        for dy,dx in[(0,1),(1,0),(0,-1),(-1,0)]:
                            ny,nx=y+dy,x+dx
                            if 0<=ny<self.alto and 0<=nx<self.ancho:
                                if(isinstance(self.matriz[ny][nx],Camino)or 
                                    isinstance(self.matriz[ny][nx],Liana)):
                                    tiene_vecino=True
                                    break
                        if tiene_vecino:
                            self.matriz[y][x]=Liana(y,x)
                            lianas_creadas+=1

        self.matriz[self.alto-2][self.ancho-2]=Salida(self.alto-2,self.ancho-2)

    def enLimites(self,fila,columna):
        return 0<=fila<self.alto and 0<=columna<self.ancho

    def obtenerTerreno(self,fila,columna):
        if self.enLimites(fila,columna):
            return self.matriz[fila][columna]
        return Muro(fila,columna)
    
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
        self.mapa=Mapa(columnas,filas)

        self.nombre_jugador=nombre_jugador

        self.jugador=Jugador(2, 1, self.mapa)
        
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