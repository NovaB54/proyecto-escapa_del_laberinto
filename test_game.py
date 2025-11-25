#Pruebas de commit, clases y librerias 

import pygame
import sys
import random

VENTANA_X = 600
VENTANA_Y = 600

BGC = (255, 255, 255)
COLOR_TEXTO = (20, 20, 20)

MAPA = [
    [0,0, 0, 0, 0, 0, 0, 0, 0,1],
    [0,1, 0, 1, 0, 1, 1, 1, 0,1],
    [0,0, 0, 0, 0, 0, 0, 0, 0,1],
    [1,0, 1, 1, 0, 1, 1, 1, 0,1],
    [1,0, 0, 0, 0, 0, 0, 1, 0,1],
    [1,1, 1, 1, 0, 1, 0, 1, 0,1],
    [1,0, 0, 0, 0, 1, 0, 0, 0,1],
    [1,0, 1, 0, 1, 1, 1, 1, 0,1],
    [1,0, 0, 0, 0, 'E', 0, 0, 0,1],
    [1,1, 1, 1, 1, 1, 1, 1, 1,1]
]

POSICION_INICIAL = [0, 0] 

cantidad_cazadores = 3

RUTAS_IMAGENES = {
    0: 'assets/path.png',
    1: 'assets/wall.png',
    2: 'assets/lianas.png',
    'E': 'assets/exit.png',
    'PLAYER': 'assets/player.png',
    'CAZADOR': 'assets/cazador.png'
}

### Clases de Terreno ###
class Terreno:
    def __init__(self, tipo, imagen):
        self.tipo = tipo
        self.imagen = imagen
    
    def es_transitable_jugador(self):
        return True
    
    def es_transitable_enemigo(self):
        return True
    
    def dibujar(self, superficie, x, y):
        if self.imagen:
            superficie.blit(self.imagen, (x, y))

class Camino(Terreno):
    def __init__(self, imagen):
        super().__init__(0, imagen)
    
    def es_transitable_jugador(self):
        return True
    
    def es_transitable_enemigo(self):
        return True

class Muro(Terreno):
    def __init__(self, imagen):
        super().__init__(1, imagen)
    
    def es_transitable_jugador(self):
        return False
    
    def es_transitable_enemigo(self):
        return False

class Lianas(Terreno):
    def __init__(self, imagen):
        super().__init__(2, imagen)
    
    def es_transitable_jugador(self):
        return False
    
    def es_transitable_enemigo(self):
        return True

class Salida(Terreno):
    def __init__(self, imagen):
        super().__init__('E', imagen)
    
    def es_transitable_jugador(self):
        return True
    
    def es_transitable_enemigo(self):
        return False

### Recursos ###
class GestorRecursos:
    def __init__(self, ancho_celda, alto_celda):
        self.recursos = {}
        self.dimensiones_celda = (ancho_celda, alto_celda)
        self.cargar_recursos()

    def cargar_recursos(self):
        for clave, ruta in RUTAS_IMAGENES.items():
            try:
                imagen = pygame.image.load(ruta).convert_alpha()
                self.recursos[clave] = pygame.transform.scale(imagen, self.dimensiones_celda)
            except:
                # Si no se puede cargar la imagen, crear una superficie de color
                color = self._obtener_color_por_defecto(clave)
                superficie = pygame.Surface(self.dimensiones_celda)
                superficie.fill(color)
                self.recursos[clave] = superficie

    def _obtener_color_por_defecto(self, clave):
        colores = {
            0: (200, 200, 200),
            1: (100, 100, 100),
            2: (150, 100, 50),
            'E': (0, 255, 0),
            'PLAYER': (255, 0, 0),
            'CAZADOR': (0, 0, 255)
        }
        return colores.get(clave, (255, 255, 255))

    def obtener_recurso(self, clave):
        return self.recursos.get(clave)

### Clases de Personajes ###
class Personaje:
    def __init__(self, posicion, ancho_celda, alto_celda, imagen):
        self.posicion = list(posicion)
        self.ancho_celda = ancho_celda
        self.alto_celda = alto_celda
        self.imagen = imagen
    
    def dibujar(self, superficie):
        fila, columna = self.posicion
        x = columna * self.ancho_celda
        y = fila * self.alto_celda
        
        if self.imagen:
            superficie.blit(self.imagen, (x, y))
        else:
            centro_x = x + self.ancho_celda // 2
            centro_y = y + self.alto_celda // 2
            pygame.draw.circle(superficie, (255, 0, 0), (centro_x, centro_y), self.ancho_celda // 3)

class Jugador(Personaje):
    def __init__(self, posicion_inicio, ancho_celda, alto_celda, recursos):
        super().__init__(posicion_inicio, ancho_celda, alto_celda, recursos.obtener_recurso('PLAYER'))
        self.posicion_inicio = list(posicion_inicio)
        self.contador_movimientos = 0
        
    def reiniciar(self):
        self.posicion = list(self.posicion_inicio)
        self.contador_movimientos = 0
        
    def hay_cazador_en_posicion(self, fila, columna, cazadores):
        """Verifica si hay un cazador en la posición especificada"""
        for cazador in cazadores:
            if cazador.posicion == [fila, columna]:
                return True
        return False
        
    def intentar_mover(self, direccion, laberinto, cazadores):
        fila_actual, columna_actual = self.posicion
        nueva_fila, nueva_columna = fila_actual, columna_actual
        
        if direccion == 'ARRIBA': nueva_fila -= 1
        elif direccion == 'ABAJO': nueva_fila += 1
        elif direccion == 'IZQUIERDA': nueva_columna -= 1
        elif direccion == 'DERECHA': nueva_columna += 1
            
        contenido_destino = laberinto.contenido_de_celda(nueva_fila, nueva_columna)
        
        if self.hay_cazador_en_posicion(nueva_fila, nueva_columna, cazadores):
            return 'MUERTE'
        
        if contenido_destino is not None:
            terreno_destino = laberinto.obtener_terreno(contenido_destino)
            if terreno_destino and terreno_destino.es_transitable_jugador():
                self.posicion[0] = nueva_fila
                self.posicion[1] = nueva_columna
                self.contador_movimientos += 1 
                
                if contenido_destino == 'E':
                    return 'VICTORIA' 
        
        return False

class Cazador(Personaje):
    def __init__(self, posicion, ancho_celda, alto_celda, recursos):
        super().__init__(posicion, ancho_celda, alto_celda, recursos.obtener_recurso('CAZADOR'))
    
    #Utiliza BFS para encontrar el camino más corto hacia el jugador
    def encontrar_camino_mas_corto(self, jugador_pos, laberinto):
        inicio = tuple(self.posicion)
        objetivo = tuple(jugador_pos)
        
        if inicio == objetivo:
            return None
            
        cola = [(inicio, [])]
        visitados = set([inicio])
        direcciones = [('ARRIBA', -1, 0), ('ABAJO', 1, 0), ('IZQUIERDA', 0, -1), ('DERECHA', 0, 1)]
        
        while cola:
            (fila_actual, columna_actual), camino = cola.pop(0)
            
            for nombre_dir, df, dc in direcciones:
                nueva_fila, nueva_columna = fila_actual + df, columna_actual + dc
                
                if (nueva_fila, nueva_columna) == objetivo:
                    return camino + [nombre_dir]
                
                if (0 <= nueva_fila < laberinto.tamano_cuadricula and 
                    0 <= nueva_columna < laberinto.tamano_cuadricula and 
                    (nueva_fila, nueva_columna) not in visitados):
                    
                    contenido = laberinto.contenido_de_celda(nueva_fila, nueva_columna)
                    if contenido is not None:
                        terreno = laberinto.obtener_terreno(contenido)
                        if terreno and terreno.es_transitable_enemigo():
                            visitados.add((nueva_fila, nueva_columna))
                            cola.append(((nueva_fila, nueva_columna), camino + [nombre_dir]))
        
        return None
    
    def mover_hacia_jugador(self, jugador_pos, laberinto, otros_cazadores):
        camino = self.encontrar_camino_mas_corto(jugador_pos, laberinto)
        
        if camino and len(camino) > 0:
            direccion = camino[0]
            fila_actual, columna_actual = self.posicion
            nueva_fila, nueva_columna = fila_actual, columna_actual
            
            if direccion == 'ARRIBA': nueva_fila -= 1
            elif direccion == 'ABAJO': nueva_fila += 1
            elif direccion == 'IZQUIERDA': nueva_columna -= 1
            elif direccion == 'DERECHA': nueva_columna += 1
            
            contenido_destino = laberinto.contenido_de_celda(nueva_fila, nueva_columna)
            
            posicion_ocupada = False
            for cazador in otros_cazadores:
                if cazador != self and cazador.posicion == [nueva_fila, nueva_columna]:
                    posicion_ocupada = True
                    break
            
            if (not posicion_ocupada and contenido_destino is not None):
                terreno_destino = laberinto.obtener_terreno(contenido_destino)
                if terreno_destino and terreno_destino.es_transitable_enemigo():
                    self.posicion[0] = nueva_fila
                    self.posicion[1] = nueva_columna
                    return True
        
        return self.mover_aleatoriamente(laberinto, otros_cazadores)
    
    def mover_aleatoriamente(self, laberinto, otros_cazadores):
        fila_actual, columna_actual = self.posicion
        direcciones = ['ARRIBA', 'ABAJO', 'IZQUIERDA', 'DERECHA']
        random.shuffle(direcciones)
        
        for direccion in direcciones:
            nueva_fila, nueva_columna = fila_actual, columna_actual
            
            if direccion == 'ARRIBA': nueva_fila -= 1
            elif direccion == 'ABAJO': nueva_fila += 1
            elif direccion == 'IZQUIERDA': nueva_columna -= 1
            elif direccion == 'DERECHA': nueva_columna += 1
            
            contenido_destino = laberinto.contenido_de_celda(nueva_fila, nueva_columna)
            
            posicion_ocupada = False
            for cazador in otros_cazadores:
                if cazador != self and cazador.posicion == [nueva_fila, nueva_columna]:
                    posicion_ocupada = True
                    break
            
            if (not posicion_ocupada and contenido_destino is not None):
                terreno_destino = laberinto.obtener_terreno(contenido_destino)
                if terreno_destino and terreno_destino.es_transitable_enemigo():
                    self.posicion[0] = nueva_fila
                    self.posicion[1] = nueva_columna
                    return True
        
        return False

### Mapa del Laberinto ###
class Laberinto:
    def __init__(self, mapa_matriz, ancho_total, alto_total, recursos, ancho_celda, alto_celda):
        self.datos = mapa_matriz
        self.tamano_cuadricula = len(mapa_matriz)
        self.ancho_total = ancho_total
        self.alto_total = alto_total
        self.ancho_celda = ancho_celda
        self.alto_celda = alto_celda
        self.recursos = recursos 
        self.color_linea_cuadricula = (0, 0, 0)
        self.terrenos = self._crear_terrenos()
    
    def _crear_terrenos(self):
        terrenos = {}
        # Crear instancias de cada tipo de terreno
        terrenos[0] = Camino(self.recursos.obtener_recurso(0))
        terrenos[1] = Muro(self.recursos.obtener_recurso(1))
        terrenos[2] = Lianas(self.recursos.obtener_recurso(2))
        terrenos['E'] = Salida(self.recursos.obtener_recurso('E'))
        return terrenos
    
    def contenido_de_celda(self, fila, columna):
        if 0 <= fila < self.tamano_cuadricula and 0 <= columna < self.tamano_cuadricula:
            return self.datos[fila][columna]
        return None 
    
    def obtener_terreno(self, tipo):
        return self.terrenos.get(tipo)
    
    def encontrar_posiciones_validas(self, cantidad, excluir_posiciones=[]):
        posiciones = []
        intentos = 0
        max_intentos = 100
        
        while len(posiciones) < cantidad and intentos < max_intentos:
            fila = random.randint(0, self.tamano_cuadricula - 1)
            columna = random.randint(0, self.tamano_cuadricula - 1)
            
            contenido = self.datos[fila][columna]
            terreno = self.obtener_terreno(contenido)
            
            if (terreno and terreno.es_transitable_enemigo() and 
                [fila, columna] not in excluir_posiciones and 
                [fila, columna] not in posiciones):
                posiciones.append([fila, columna])
            
            intentos += 1
        
        return posiciones
    
    def dibujar(self, superficie):
        for fila in range(self.tamano_cuadricula):
            for columna in range(self.tamano_cuadricula):
                x = columna * self.ancho_celda
                y = fila * self.alto_celda
                
                # Dibujar camino de fondo
                terreno_camino = self.obtener_terreno(0)
                if terreno_camino:
                    terreno_camino.dibujar(superficie, x, y)

                # Dibujar terreno específico
                contenido = self.datos[fila][columna]
                if contenido != 0:
                    terreno = self.obtener_terreno(contenido)
                    if terreno:
                        terreno.dibujar(superficie, x, y)
                        
        # Dibujar cuadrícula
        for x in range(0, self.ancho_total + 1, self.ancho_celda):
            pygame.draw.line(superficie, self.color_linea_cuadricula, (x, 0), (x, self.alto_total))
        for y in range(0, self.alto_total + 1, self.alto_celda):
            pygame.draw.line(superficie, self.color_linea_cuadricula, (0, y), (self.ancho_total, y))

### Juego Principal ###
class Juego:
    def __init__(self, datos_mapa, inicio, ancho, alto):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ancho, alto))
        pygame.display.set_caption("Escapa del Laberinto")
        self.reloj = pygame.time.Clock()
        self.ejecutandose = True
        self.juego_terminado = False
        self.victoria = False
        
        tamano_matriz = len(datos_mapa) 
        ancho_celda = ancho // tamano_matriz
        alto_celda = alto // tamano_matriz
        
        self.gestor_recursos = GestorRecursos(ancho_celda, alto_celda)
        self.laberinto = Laberinto(datos_mapa, ancho, alto, self.gestor_recursos, ancho_celda, alto_celda)
        self.jugador = Jugador(inicio, ancho_celda, alto_celda, self.gestor_recursos)
        self.cazadores = []
        
        self.inicializar_cazadores(cantidad_cazadores)
        
        self.fuente_pequena = pygame.font.Font(None, 24)
        self.fuente_grande = pygame.font.Font(None, 74)
    
    def inicializar_cazadores(self, cantidad):
        excluir = [self.jugador.posicion]
        posiciones_cazadores = self.laberinto.encontrar_posiciones_validas(cantidad, excluir)
        
        self.cazadores = []
        for pos in posiciones_cazadores:
            cazador = Cazador(pos, self.laberinto.ancho_celda, self.laberinto.alto_celda, self.gestor_recursos)
            self.cazadores.append(cazador)
    
    def mover_cazadores(self):
        for cazador in self.cazadores:
            otros_cazadores = [c for c in self.cazadores if c != cazador]
            cazador.mover_hacia_jugador(self.jugador.posicion, self.laberinto, otros_cazadores)
    
    def verificar_colisiones(self):
        for cazador in self.cazadores:
            if cazador.posicion == self.jugador.posicion:
                return True
        return False
        
    def manejar_inputs(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.ejecutandose = False
            
            if evento.type == pygame.KEYDOWN:
                if self.juego_terminado and evento.key == pygame.K_r:
                    self.reiniciar_juego()
                    return
                    
                if not self.juego_terminado:
                    direccion = None
                    if evento.key == pygame.K_UP: direccion = 'ARRIBA'
                    elif evento.key == pygame.K_DOWN: direccion = 'ABAJO'
                    elif evento.key == pygame.K_LEFT: direccion = 'IZQUIERDA'
                    elif evento.key == pygame.K_RIGHT: direccion = 'DERECHA'
                    
                    if direccion:
                        resultado = self.jugador.intentar_mover(direccion, self.laberinto, self.cazadores)
                        
                        if resultado == 'VICTORIA':
                            self.juego_terminado = True
                            self.victoria = True
                        elif resultado == 'MUERTE' or self.verificar_colisiones():
                            self.juego_terminado = True
                            self.victoria = False
                        else:
                            self.mover_cazadores()
                            if self.verificar_colisiones():
                                self.juego_terminado = True
                                self.victoria = False
    
    def reiniciar_juego(self):
        self.juego_terminado = False
        self.victoria = False
        self.jugador.reiniciar()
        self.inicializar_cazadores(cantidad_cazadores)
            
    def dibujar_texto(self, superficie, texto, fuente, color, centro_x, centro_y):
        texto_superficie = fuente.render(texto, True, color)
        rect_texto = texto_superficie.get_rect(center=(centro_x, centro_y))
        superficie.blit(texto_superficie, rect_texto)
        
    def dibujar_escena(self):
        self.pantalla.fill(BGC)
        
        self.laberinto.dibujar(self.pantalla)
        for cazador in self.cazadores:
            cazador.dibujar(self.pantalla)
            
        self.jugador.dibujar(self.pantalla)
        
        texto_movimientos = f"Movimientos: {self.jugador.contador_movimientos}"
        self.dibujar_texto(self.pantalla, texto_movimientos, self.fuente_pequena, COLOR_TEXTO, 90, 20)
        
        texto_cazadores = f"Cazadores: {len(self.cazadores)}"
        self.dibujar_texto(self.pantalla, texto_cazadores, self.fuente_pequena, COLOR_TEXTO, VENTANA_X - 80, 20)
        
        if self.juego_terminado:
            capa_oscura = pygame.Surface((VENTANA_X, VENTANA_Y))
            capa_oscura.set_alpha(180) 
            capa_oscura.fill((0, 0, 0))
            self.pantalla.blit(capa_oscura, (0, 0))
            
            if self.victoria:
                self.dibujar_texto(self.pantalla, "¡GANASTE!", self.fuente_grande, (0, 255, 0), VENTANA_X // 2, VENTANA_Y // 2 - 50)
            else:
                self.dibujar_texto(self.pantalla, "¡PERDISTE!", self.fuente_grande, (255, 0, 0), VENTANA_X // 2, VENTANA_Y // 2 - 50)
            
            texto_final_mov = f"Movimientos totales: {self.jugador.contador_movimientos}"
            self.dibujar_texto(self.pantalla, texto_final_mov, self.fuente_pequena, (255, 255, 255), VENTANA_X // 2, VENTANA_Y // 2 + 20)
            self.dibujar_texto(self.pantalla, "Presiona R para reiniciar", self.fuente_pequena, (255, 255, 255), VENTANA_X // 2, VENTANA_Y // 2 + 50)
        
        pygame.display.flip()
        
    def ejecutar(self):
        while self.ejecutandose:
            self.manejar_inputs()
            self.dibujar_escena()
            self.reloj.tick(30)
            
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    juego = Juego(MAPA, POSICION_INICIAL, VENTANA_X, VENTANA_Y)
    juego.ejecutar()