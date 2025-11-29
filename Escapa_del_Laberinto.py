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

    def permiteCazador(self):
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
    def __init__(self,fila,columna,mapa):
        super().__init__(fila,columna,mapa,'juega')
        self.corriendo=False
        self.energia=100
        self.energiamax=100
        self.trampas=[]
        self.ultimo=0
        self.recarga=5
        self.trampasmax=3
        self.tiempo_ultimo_mov=0
        self.cooldown_mov=0.5
        self.tiempo_ultima_recarga=time.time()

    def mover(self,df,dc,cazadores):
        ahora=time.time()
        if not self.corriendo:
            if ahora-self.tiempo_ultimo_mov<self.cooldown_mov:
                return False

        nueva_fila=self.fila+df
        nueva_columna=self.columna+dc

        if not self.puedeMover(nueva_fila,nueva_columna):
            return False

        for caz in cazadores:
            if caz.vivo and caz.fila==nueva_fila and caz.columna==nueva_columna:
                return False

        self.fila=nueva_fila
        self.columna=nueva_columna

        if not self.corriendo:
            self.tiempo_ultimo_mov=ahora
        else:
            if self.energia>=10:
                self.energia-=10
            else:
                self.corriendo=False

        return True

    def recuperarEnergia(self):
        if self.corriendo:
            return

        ahora=time.time()
        if ahora-self.tiempo_ultima_recarga>=1.5:
            if self.energia<self.energiamax:
                self.energia+=5
                if self.energia>self.energiamax:
                    self.energia=self.energiamax
            self.tiempo_ultima_recarga=ahora

    def colocarTrampa(self,modo):
        if modo!="escape":
            return False

        ahora=time.time()
        if ahora-self.ultimo<self.recarga:
            return False
        
        if len(self.trampas)>=self.trampasmax:
            return False
        
        terreno=self.mapa.obtenerTerreno(self.fila,self.columna)
        if not terreno.permiteTrampa():
            return False
        
        trampa=Trampa(self.fila,self.columna,self.mapa)
        self.trampas.append(trampa)
        self.ultimo=ahora
        return True

    def limpiarTrampas(self):
        self.trampas=[i for i in self.trampas if i.activa]

    def estaEnSalida(self):
        return (self.fila,self.columna)==self.mapa.salida
    #para el modo caza
    def colocar_en_salida(self):
        self.fila=self.mapa.salida[0]
        self.columna=self.mapa.salida[1]

#clase Cazador (hijo)

class Cazador(Entidad):
    def __init__(self,fila,columna,mapa):
        super().__init__(fila,columna,mapa,'caza')
        self.vivo=True
        self.t_muerte=None

    def bfs(self,jugador):
        inicio=(self.fila,self.columna)
        objetivo=(jugador.fila,jugador.columna)
        if inicio==objetivo:
            return None
        cola=[inicio]
        visitado=[[False for _ in range(self.mapa.columnas)] for _ in range(self.mapa.filas)]
        padre=[[None for _ in range(self.mapa.columnas)] for _ in range(self.mapa.filas)]
        visitado[inicio[0]][inicio[1]]=True
        movs=[(1,0),(-1,0),(0,1),(0,-1)]
        while cola:
            f,c=cola.pop(0)
            if (f,c)==objetivo:
                break
            for df,dc in movs:
                nf=f+df
                nc=c+dc
                if self.mapa.enLimites(nf,nc) and not visitado[nf][nc]:
                    terreno=self.mapa.obtenerTerreno(nf,nc)
                    if terreno.permiteCazador():
                        visitado[nf][nc]=True
                        padre[nf][nc]=(f,c)
                        cola.append((nf,nc))
        if not visitado[objetivo[0]][objetivo[1]]:
            return None
        camino=[]
        paso=objetivo
        while paso!=inicio:
            camino.append(paso)
            paso=padre[paso[0]][paso[1]]
        camino.reverse()
        return camino

    def perseguir(self,jugador):
        camino=self.bfs(jugador)
        if camino is None or len(camino)==0:
            return
        nf,nc=camino[0]
        if self.puedeMover(nf,nc):
            self.fila=nf
            self.columna=nc

    def huir(self,jugador):
        opciones=[(0,0),(1,0),(-1,0),(0,1),(0,-1)]
        mejor=-1
        pos=(self.fila,self.columna)
        for df,dc in opciones:
            nf=self.fila+df
            nc=self.columna+dc
            if self.puedeMover(nf,nc):
                d=abs(nf-jugador.fila)+abs(nc-jugador.columna)
                if d>mejor:
                    mejor=d
                    pos=(nf,nc)
        self.fila,self.columna=pos

    def mover_hacia_meta(self,meta):
        mf,mc=meta
        mejor=None
        dist=999
        movs=[(1,0),(-1,0),(0,1),(0,-1)]
        for df,dc in movs:
            nf=self.fila+df
            nc=self.columna+dc
            if self.puedeMover(nf,nc):
                d=abs(nf-mf)+abs(nc-mc)
                if d<dist:
                    dist=d
                    mejor=(nf,nc)
        if mejor:
            self.fila,self.columna=mejor

    def verificarTrampa(self,jugador):
        for t in jugador.trampas:
            if t.activa and t.fila==self.fila and t.columna==self.columna:
                t.activa=False
                return True
        return False

    def resurgir(self,jugador):
        posiciones=[]
        for i in range(self.mapa.filas):
            for j in range(self.mapa.columnas):
                terreno=self.mapa.obtenerTerreno(i,j)
                if terreno.permiteCazador():
                    if abs(i-jugador.fila)+abs(j-jugador.columna)>5:
                        posiciones.append((i,j))
        if posiciones:
            self.fila,self.columna=random.choice(posiciones)

#clase juego principal para que funcionen las demas clases juntas
class Juego:
    def __init__(self, filas=10, columnas=10, cantidad_cazadores=2, modo="escape", nombre_jugador="Jugador", dificultad=None):
        if modo not in ["escape","cazador"]:
            modo="escape"
        self.mapa=Mapa(columnas, filas)
        self.nombre_jugador=nombre_jugador
        self.jugador=Jugador(1, 1, self.mapa)
        self.modo=modo
        self.jugador.modo=self.modo
        self.dificultad=dificultad
        
        if modo=="escape":
            self.configurar_dificultad_escape()
            cantidad_cazadores=self.cantidad_cazadores_inicial
        else:
            self.jugador.recarga=999999
            self.jugador.trampasmax=0
            self.jugador.colocar_en_salida()
            self.configurar_dificultad_cazador()
            cantidad_cazadores=self.cantidad_cazadores_inicial
        self.cazadores=[]
        for _ in range(cantidad_cazadores):
            if self.modo=="cazador":
                f, c=self.buscar_posicion_cazador_modo_caza()
            else:
                f, c=self.buscar_posicion_cazador()
            self.cazadores.append(Cazador(f, c, self.mapa))
        self.contador_movimiento_cazadores=0
        self.juego_terminado=False
        self.resultado=None
        self.tiempo_inicio=time.time()
        self.puntos=0
        self.cazadores_capturados=0
        self.ultima_dir=(0, 1)

    def configurar_dificultad_escape(self):
        if self.dificultad=="facil":
            self.cantidad_cazadores_inicial=2
            self.puntos_ganar=200
            self.puntos_trampa=60
            self.frecuencia_movimiento_cazadores=7
        elif self.dificultad=="medio":
            self.cantidad_cazadores_inicial=3
            self.puntos_ganar=400
            self.puntos_trampa=120
            self.frecuencia_movimiento_cazadores=6
        elif self.dificultad=="dificil":
            self.cantidad_cazadores_inicial=5
            self.puntos_ganar=600
            self.puntos_trampa=180
            self.frecuencia_movimiento_cazadores=5

    def configurar_dificultad_cazador(self):
        if self.dificultad=="facil":
            self.cantidad_cazadores_inicial=2
            self.puntos_ganancia_captura=100
            self.puntos_perdida_salida=200
            self.frecuencia_movimiento_cazadores=7
            self.meta_cazadores=5
        elif self.dificultad=="medio":
            self.cantidad_cazadores_inicial=3
            self.puntos_ganancia_captura=300
            self.puntos_perdida_salida=600
            self.frecuencia_movimiento_cazadores=6
            self.meta_cazadores=10
        elif self.dificultad=="dificil":
            self.cantidad_cazadores_inicial=5
            self.puntos_ganancia_captura=600
            self.puntos_perdida_salida=1200
            self.frecuencia_movimiento_cazadores=5
            self.meta_cazadores=15

    def buscar_posicion_cazador(self):
        dist_min=6
        intentos=0
        while intentos<200:
            f=random.randint(0,self.mapa.filas-1)
            c=random.randint(0,self.mapa.columnas-1)
            terreno=self.mapa.obtenerTerreno(f,c)
            if terreno.permiteCazador():
                if abs(f-self.jugador.fila)+abs(c-self.jugador.columna)>=dist_min:
                    return f,c
            intentos+=1
        for i in range(self.mapa.filas):
            for j in range(self.mapa.columnas):
                terreno=self.mapa.obtenerTerreno(i,j)
                if terreno.permiteCazador():
                    if abs(i-self.jugador.fila)+abs(j-self.jugador.columna)>=dist_min:
                        return i,j
        return self.mapa.filas-1,self.mapa.columnas-1

    def buscar_posicion_cazador_modo_caza(self):
        meta=self.mapa.salida
        while True:
            f=random.randint(0,self.mapa.filas-1)
            c=random.randint(0,self.mapa.columnas-1)
            terreno=self.mapa.obtenerTerreno(f,c)
            if terreno.permiteCazador():
                if abs(f-meta[0])+abs(c-meta[1])>=12:
                    return f,c

    def actualizar_cazadores_modo_caza(self):
        meta=self.mapa.salida
        for cazador in self.cazadores:
            dist=abs(cazador.fila-self.jugador.fila)+abs(cazador.columna-self.jugador.columna)
            if dist<=3:
                cazador.huir(self.jugador)
            else:
                cazador.mover_hacia_meta(meta)

    @staticmethod
    def obtener_top5(modo):
        puntajes=cargar_puntajes()
        if modo not in puntajes:
            return []
        return puntajes[modo]

    def registrar_puntaje(self):
        if not self.juego_terminado:
            return

        puntajes=cargar_puntajes()
        if self.modo not in puntajes:
            puntajes[self.modo] = []

        entrada ={
        "nombre": self.nombre_jugador,
        "puntos": self.puntos,
        "tiempo": int(self.obtener_tiempo_transcurrido()),
        "resultado": self.resultado
        }

        puntajes[self.modo].append(entrada)
        puntajes[self.modo].sort(key=lambda x: x["puntos"], reverse=True)
        puntajes[self.modo]=puntajes[self.modo][:5]

        guardar_puntajes(puntajes)


    def mover_jugador(self,df,dc):
        if self.juego_terminado:
            return False
        if self.modo=="cazador":
            nueva_fila=self.jugador.fila+df
            nueva_columna=self.jugador.columna+dc
            if not self.mapa.enLimites(nueva_fila,nueva_columna):
                return False
            terreno=self.mapa.obtenerTerreno(nueva_fila,nueva_columna)
            if not terreno.permiteJugador():
                return False
            objetivo=None
            for cazador in self.cazadores:
                if cazador.fila==nueva_fila and cazador.columna==nueva_columna:
                    objetivo=cazador
                    break
            if objetivo is not None:
                self.jugador.fila=nueva_fila
                self.jugador.columna=nueva_columna
                self.cazadores_capturados+=1
                self.puntos+=self.puntos_ganancia_captura
                pos=self.buscar_posicion_cazador_modo_caza()
                objetivo.fila, objetivo.columna=pos
                self.ultima_dir=(df,dc)
                self.verificar_estado()
                return True
            if self.jugador.mover(df,dc,self.cazadores):
                self.ultima_dir=(df,dc)
                self.verificar_estado()
                return True
            return False
        else:
            if self.jugador.mover(df,dc,self.cazadores):
                self.ultima_dir=(df,dc)
                self.verificar_estado()
                return True
            return False

    def correr_jugador(self):
        if self.juego_terminado:
            return False
        self.jugador.corriendo=True
        return True

    def colocar_trampa(self):
        if self.juego_terminado:
            return False
        x=self.jugador.colocarTrampa(self.modo)
        if not x:
            return False
        if self.modo=="escape":
            self.puntos+=self.puntos_trampa
        return True

    def actualizar_cazadores(self):
        if self.juego_terminado:
            return
        if self.frecuencia_movimiento_cazadores!=-1:
            self.contador_movimiento_cazadores+=1
            if self.contador_movimiento_cazadores<self.frecuencia_movimiento_cazadores:
                return
            self.contador_movimiento_cazadores=0
        if self.modo=="escape":
            ahora=time.time()
            for cazador in self.cazadores:
                if not cazador.vivo:
                    if cazador.t_muerte is not None and ahora-cazador.t_muerte>=10:
                        cazador.resurgir(self.jugador)
                        cazador.vivo=True
                        cazador.t_muerte=None
                    continue
                if cazador.verificarTrampa(self.jugador):
                    cazador.vivo=False
                    cazador.t_muerte=ahora
                    self.cazadores_capturados+=1
                    continue
                cazador.perseguir(self.jugador)
        else:
            self.actualizar_cazadores_modo_caza()
        self.verificar_estado()

    def _verificar_modo_escape(self):
        if self.jugador.estaEnSalida():
            self.juego_terminado=True
            self.resultado="ganaste"
            self.puntos=self.puntos_ganar+self.puntos_trampa*self.cazadores_capturados
            self.registrar_puntaje()
            return
        for caz in self.cazadores:
            if caz.vivo and caz.fila==self.jugador.fila and caz.columna==self.jugador.columna:
                self.juego_terminado=True
                self.resultado="perdiste"
                self.registrar_puntaje()
                return

    def _verificar_modo_cazador(self):
        for cazador in self.cazadores:
            if (cazador.fila,cazador.columna)==self.mapa.salida:
                self.puntos-=self.puntos_perdida_salida
                pos=self.buscar_posicion_cazador_modo_caza()
                cazador.fila, cazador.columna=pos
        for cazador in self.cazadores:
            if self.jugador.fila==cazador.fila and self.jugador.columna==cazador.columna:
                self.cazadores_capturados+=1
                self.puntos+=self.puntos_ganancia_captura
                pos=self.buscar_posicion_cazador_modo_caza()
                cazador.fila, cazador.columna=pos
                break
        if self.cazadores_capturados>=self.meta_cazadores:
            self.juego_terminado=True
            self.resultado="ganaste"
            self.registrar_puntaje()
            return

    def verificar_estado(self):
        if self.modo=="escape":
            self._verificar_modo_escape()
        else:
            self._verificar_modo_cazador()

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
            nombre_jugador=nombre_jugador,
            dificultad=self.dificultad
        )

archivo_puntos="puntajes.json"

def cargar_puntajes():
    if not os.path.exists(archivo_puntos):
        return {"escape": [], "cazador": []}

    archivo=open(archivo_puntos, "r")
    contenido=archivo.read()
    archivo.close()

    if contenido.strip()=="":
        return {"escape": [], "cazador": []}

    data=json.loads(contenido)
    limpio={"escape": [], "cazador": []}

    for modo in ["escape", "cazador"]:
        lista=data.get(modo, [])
        for item in lista:
            if isinstance(item, dict):
                limpio[modo].append(item)
            else:
                limpio[modo].append({
                    "nombre": "Jugador",
                    "puntos": int(item),
                    "tiempo": 0,
                    "resultado": "desconocido"
                })

    return limpio

def guardar_puntajes(puntajes):
    texto=json.dumps(puntajes, indent=4)
    archivo=open(archivo_puntos, "w")
    archivo.write(texto)
    archivo.close()
