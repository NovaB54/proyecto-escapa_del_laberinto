import pygame
import sys
import os
import json
import time

#importaciones necesarias del juego principal
from Escapa_del_Laberinto import (
    Terreno, Camino, Muro, Liana, Tunel,Salida, Mapa, 
    Entidad, Trampa, Jugador, Cazador, Juego,
    cargar_puntajes, guardar_puntajes)

NEGRO =(0, 0, 0)
GRIS =(50, 50, 50)
BLANCO =(255, 255, 255)
VERDE =(0, 150, 0)
ROJO =(150, 0, 0)
AZUL_CLARO =(173, 216, 230)

def escalar(img):
    return pygame.transform.scale(img, (30, 30))

CAMINO=escalar(pygame.image.load(os.path.join("assets","textures","path.png")))
MURO =escalar(pygame.image.load(os.path.join("assets","textures","wall.png")))
LIANA =escalar(pygame.image.load(os.path.join("assets","textures","pit.png")))
TUNEL =escalar(pygame.image.load(os.path.join("assets","textures","duct.png")))
SALIDA =escalar(pygame.image.load(os.path.join("assets","textures","exit.png")))
TRAMPA =escalar(pygame.image.load(os.path.join("assets","textures","pit.png")))
CAZADOR =escalar(pygame.image.load(os.path.join("assets","textures","hunter.png")))
JUGADOR =escalar(pygame.image.load(os.path.join("assets","textures","player.png")))

### Sonidos ###
def reproducir_click():
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    ruta_sonido = os.path.join("assets", "sounds", "click.ogg")
    sonido_click = pygame.mixer.Sound(ruta_sonido)
    sonido_click.play()

def reproducir_start_game():
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    ruta_sonido = os.path.join("assets", "sounds", "start_game.ogg")
    sonido_start_game = pygame.mixer.Sound(ruta_sonido)
    sonido_start_game.play()

#Clases usadas por la interfaz
class Boton:
    def __init__(self, x, y, ancho, alto, texto, color, color_hover, accion=None):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.color = color
        self.color_hover = color_hover
        self.texto = texto
        self.accion = accion
        self.fuente = pygame.font.Font(None, 36)

    def dibujar(self, pantalla):
        mouse_pos = pygame.mouse.get_pos()
        current_color = self.color_hover if self.rect.collidepoint(mouse_pos) else self.color

        pygame.draw.rect(pantalla, current_color, self.rect, border_radius=5)
        
        texto_superficie = self.fuente.render(self.texto, True, BLANCO)
        rect_texto = texto_superficie.get_rect(center=self.rect.center)
        pantalla.blit(texto_superficie, rect_texto)

    def check_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            reproducir_click() 
            
            if self.accion:
                self.accion()
            return True
        return False

#Caja para ingresar texto. Usado para el nombre del jugador
class CuadroTexto:
    def __init__(self, x, y, w, h, texto=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactivo = GRIS
        self.color_activo = AZUL_CLARO
        self.color = self.color_inactivo
        self.texto = texto
        self.fuente = pygame.font.Font(None, 32)
        self.activo = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.activo = not self.activo
            else:
                self.activo = False
            self.color = self.color_activo if self.activo else self.color_inactivo
        
        if event.type == pygame.KEYDOWN:
            if self.activo:
                if event.key == pygame.K_RETURN:
                    self.activo = False
                    self.color = self.color_inactivo
                elif event.key == pygame.K_BACKSPACE:
                    self.texto = self.texto[:-1]
                else:
                    if len(self.texto) < 20:
                        self.texto += event.unicode

    def dibujar(self, pantalla):
        # Dibujar el cuadro
        pygame.draw.rect(pantalla, self.color, self.rect, border_radius=3)
        pygame.draw.rect(pantalla, BLANCO, self.rect, 2, border_radius=3) # Borde blanco
        
        # Dibujar el texto
        texto_superficie = self.fuente.render(self.texto, True, NEGRO)
        # Centrar el texto verticalmente y dejar un margen horizontal
        pantalla.blit(texto_superficie, (self.rect.x + 5, self.rect.y + 10))

### Funciones de dibujo del juego ###
def dibujar_mapa(pantalla, juego, tamaño_celda, offset_x, offset_y):
    for fila in range(juego.mapa.alto):
        for columna in range(juego.mapa.ancho):
            terreno = juego.mapa.obtenerTerreno(fila, columna)
            x = offset_x + columna * tamaño_celda
            y = offset_y + fila * tamaño_celda
            rect = pygame.Rect(x, y, tamaño_celda, tamaño_celda)
            
            if isinstance(terreno, Camino):
                pantalla.blit(CAMINO, rect)
            elif isinstance(terreno, Muro):
                pantalla.blit(MURO, rect)
            elif isinstance(terreno, Liana):
                pantalla.blit(LIANA, rect)
            elif isinstance(terreno, Tunel):
                pantalla.blit(TUNEL, rect)
            elif isinstance(terreno, Salida):
                pantalla.blit(SALIDA, rect)

            pygame.draw.rect(pantalla, BLANCO, rect, 1)

def dibujar_jugador(pantalla, juego, tamaño_celda, offset_x, offset_y):
    jugador=juego.jugador
    if juego.modo=="escape":
        textura=JUGADOR
    else:
        textura=CAZADOR
    x = offset_x + jugador.columna * tamaño_celda
    y = offset_y + jugador.fila * tamaño_celda
    pantalla.blit(textura, (x, y))


def dibujar_cazadores(pantalla, juego, tamaño_celda, offset_x, offset_y):
    if juego.modo=="escape":
        textura=CAZADOR
    else:
        textura=JUGADOR

    for cazador in juego.cazadores:
        if cazador.vivo:
            x= offset_x + cazador.columna * tamaño_celda
            y= offset_y + cazador.fila * tamaño_celda
            pantalla.blit(textura, (x, y))

def dibujar_trampas(pantalla, trampas, tamaño_celda, offset_x, offset_y):
    for trampa in trampas:
        if trampa.activa:
            x = offset_x + trampa.columna * tamaño_celda
            y = offset_y + trampa.fila * tamaño_celda
            pantalla.blit(TRAMPA, (x, y))

def dibujar_ui(pantalla, juego, ancho_pantalla):
    fuente=pygame.font.Font(None, 36)
    
    texto_energia=fuente.render(f"Energía: {juego.jugador.energia}", True, BLANCO)
    pantalla.blit(texto_energia, (10, 10))
    
    texto_puntos=fuente.render(f"Puntos: {juego.puntos}", True, BLANCO)
    pantalla.blit(texto_puntos, (10, 50))
    
    tiempo=int(juego.obtener_tiempo_transcurrido())
    texto_tiempo=fuente.render(f"Tiempo: {tiempo}s", True, BLANCO)
    pantalla.blit(texto_tiempo, (10, 90))
    
    if juego.modo == "cazador":
        texto_meta = fuente.render(
            f"Meta: {juego.meta_cazadores} capturas", True, BLANCO)
        pantalla.blit(texto_meta, (10, 130))

        texto_actual = fuente.render(
            f"Actual: {juego.cazadores_capturados}", True, BLANCO)
        pantalla.blit(texto_actual, (10, 170))

    else:
        texto_trampas=fuente.render(f"Trampas: {len([t for t in juego.jugador.trampas if t.activa])}/{juego.jugador.trampasmax}", True, BLANCO)
        pantalla.blit(texto_trampas, (10, 130))

def dibujar_game_over(pantalla, resultado, puntos):
    fuente_grande = pygame.font.Font(None, 74)
    fuente_pequena = pygame.font.Font(None, 36)
    
    if resultado == "ganaste":
        texto = fuente_grande.render("¡GANASTE!", True, VERDE)
    else:
        texto = fuente_grande.render("¡PERDISTE!", True, ROJO)
    
    rect_texto = texto.get_rect(center=(pantalla.get_width() // 2, pantalla.get_height() // 2 - 50))
    pantalla.blit(texto, rect_texto)
    
    texto_puntos = fuente_pequena.render(f"Puntos: {puntos}", True, BLANCO)
    rect_puntos = texto_puntos.get_rect(center=(pantalla.get_width() // 2, pantalla.get_height() // 2 + 20))
    pantalla.blit(texto_puntos, rect_puntos)
    
    texto_continuar = fuente_pequena.render("Presiona ESPACIO para continuar", True, BLANCO)
    rect_continuar = texto_continuar.get_rect(center=(pantalla.get_width() // 2, pantalla.get_height() // 2 + 70))
    pantalla.blit(texto_continuar, rect_continuar)

### Funciones de Interfaz (Pantallas Secundarias) ###

#Incio de juego - Modo Escapa
def iniciar_juego_escapa(pantalla, nombre_jugador, dificultad):
    nombre=nombre_jugador if nombre_jugador.strip() else "Invitado"
    juego=Juego(filas=15,columnas=15,cantidad_cazadores=3,modo="escape",nombre_jugador=nombre,dificultad=dificultad)
    
    tamaño_celda=30
    ancho_mapa=juego.mapa.ancho*tamaño_celda
    alto_mapa=juego.mapa.alto*tamaño_celda
    offset_x=(pantalla.get_width()-ancho_mapa)//2
    offset_y=(pantalla.get_height()-alto_mapa)//2
    
    reloj=pygame.time.Clock()
    ejecutando_juego=True
    
    while ejecutando_juego:
        for evento in pygame.event.get():
            if evento.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if evento.type==pygame.KEYDOWN:
                if juego.juego_terminado:
                    if evento.key==pygame.K_SPACE:
                        ejecutando_juego=False
                else:
                    if evento.key==pygame.K_ESCAPE:
                        ejecutando_juego=False

                    if evento.key==pygame.K_SPACE:
                        juego.jugador.corriendo=True

                    if evento.key==pygame.K_UP:
                        juego.mover_jugador(-1,0)
                    elif evento.key==pygame.K_DOWN:
                        juego.mover_jugador(1,0)
                    elif evento.key==pygame.K_LEFT:
                        juego.mover_jugador(0,-1)
                    elif evento.key==pygame.K_RIGHT:
                        juego.mover_jugador(0,1)

                    if evento.key==pygame.K_t:
                        juego.colocar_trampa()

            elif evento.type==pygame.KEYUP:
                if evento.key==pygame.K_SPACE:
                    juego.jugador.corriendo=False
        
        if not juego.juego_terminado:
            juego.tick()

        pantalla.fill(NEGRO)
        
        if not juego.juego_terminado:
            dibujar_mapa(pantalla,juego,tamaño_celda,offset_x,offset_y)
            dibujar_trampas(pantalla,juego.jugador.trampas,tamaño_celda,offset_x,offset_y)
            dibujar_jugador(pantalla,juego,tamaño_celda,offset_x,offset_y)
            dibujar_cazadores(pantalla,juego,tamaño_celda,offset_x,offset_y)
            dibujar_ui(pantalla,juego,pantalla.get_width())
        else:
            dibujar_game_over(pantalla,juego.resultado,juego.puntos)
        
        pygame.display.flip()
        reloj.tick(10)

#Inicio de juego - Modo Cazador
def iniciar_juego_caza(pantalla, nombre_jugador, dificultad):
    nombre = nombre_jugador if nombre_jugador.strip() else "Invitado"
    juego = Juego(filas=15,columnas=15,cantidad_cazadores=3,modo="cazador",nombre_jugador=nombre,dificultad=dificultad)

    tamaño_celda=30
    ancho_mapa=juego.mapa.ancho*tamaño_celda
    alto_mapa=juego.mapa.alto*tamaño_celda
    offset_x=(pantalla.get_width()-ancho_mapa)//2
    offset_y=(pantalla.get_height()-alto_mapa)//2
    
    reloj=pygame.time.Clock()
    ejecutando_juego=True
    
    while ejecutando_juego:
        for evento in pygame.event.get():
            if evento.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if evento.type==pygame.KEYDOWN:
                if juego.juego_terminado:
                    if evento.key==pygame.K_SPACE:
                        ejecutando_juego=False
                else:
                    if evento.key==pygame.K_ESCAPE:
                        ejecutando_juego=False

                    if evento.key==pygame.K_SPACE:
                        juego.jugador.corriendo=True

                    if evento.key==pygame.K_UP:
                        juego.mover_jugador(-1,0)
                    elif evento.key==pygame.K_DOWN:
                        juego.mover_jugador(1,0)
                    elif evento.key==pygame.K_LEFT:
                        juego.mover_jugador(0,-1)
                    elif evento.key==pygame.K_RIGHT:
                        juego.mover_jugador(0,1)

            elif evento.type==pygame.KEYUP:
                if evento.key==pygame.K_SPACE:
                    juego.jugador.corriendo=False
        
        if not juego.juego_terminado:
            juego.tick()
        
        pantalla.fill(NEGRO)
        
        if not juego.juego_terminado:
            dibujar_mapa(pantalla,juego,tamaño_celda,offset_x,offset_y)
            dibujar_jugador(pantalla,juego,tamaño_celda,offset_x,offset_y)
            dibujar_cazadores(pantalla,juego,tamaño_celda,offset_x,offset_y)
            dibujar_ui(pantalla,juego,pantalla.get_width())
        else:
            dibujar_game_over(pantalla,juego.resultado,juego.puntos)
        
        pygame.display.flip()
        reloj.tick(10)

#Al seleccionar un botón
def modo_escapa_seleccionado(pantalla):
    ANCHO, ALTO = pantalla.get_size()
    fuente_titulo = pygame.font.Font(None, 48)
    
    cuadro_nombre = CuadroTexto(ANCHO // 2 - 150, ALTO // 2 - 60, 300, 40)
    btn_siguiente = Boton(
        ANCHO // 2 - 100, cuadro_nombre.rect.bottom + 20,
        200, 50, "Continuar", VERDE, (0, 200, 0)
    )
    btn_regresar = Boton(
        ANCHO // 2 - 100, btn_siguiente.rect.bottom + 15,
        200, 50, "Regresar", ROJO, (200, 0, 0)
    )

    etapa = "nombre"
    nombre_final = ""
    dificultad_final = None

    btn_facil = Boton(ANCHO//2 - 150, ALTO//2 - 30, 300, 50, "Fácil", VERDE, (0,255,0))
    btn_medio = Boton(ANCHO//2 - 150, ALTO//2 + 40, 300, 50, "Medio", (200,200,0), (255,255,0))
    btn_dificil = Boton(ANCHO//2 - 150, ALTO//2 + 110, 300, 50, "Difícil", ROJO, (255,0,0))

    ejecutando = True

    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if etapa == "nombre":
                cuadro_nombre.handle_event(evento)

                if btn_siguiente.check_click(evento):
                    if cuadro_nombre.texto.strip():
                        nombre_final = cuadro_nombre.texto.strip()
                        etapa = "dificultad"

                if btn_regresar.check_click(evento):
                    ejecutando = False

            elif etapa == "dificultad":
                if btn_facil.check_click(evento):
                    dificultad_final = "facil"
                    ejecutando = False
                if btn_medio.check_click(evento):
                    dificultad_final = "medio"
                    ejecutando = False
                if btn_dificil.check_click(evento):
                    dificultad_final = "dificil"
                    ejecutando = False

        pantalla.fill(NEGRO)

        if etapa == "nombre":
            titulo = fuente_titulo.render("Nombre del Jugador", True, BLANCO)
            pantalla.blit(titulo, (ANCHO//2 - titulo.get_width()//2, cuadro_nombre.rect.y - 50))

            cuadro_nombre.dibujar(pantalla)
            btn_siguiente.dibujar(pantalla)
            btn_regresar.dibujar(pantalla)

        elif etapa == "dificultad":
            titulo = fuente_titulo.render("Selecciona Dificultad", True, BLANCO)
            pantalla.blit(titulo, (ANCHO//2 - titulo.get_width()//2, ALTO//2 - 120))

            btn_facil.dibujar(pantalla)
            btn_medio.dibujar(pantalla)
            btn_dificil.dibujar(pantalla)

        pygame.display.flip()

    if nombre_final and dificultad_final:
        juego = Juego(
            filas=15,
            columnas=15,
            cantidad_cazadores=3,
            modo="escape",
            nombre_jugador=nombre_final,
            dificultad=dificultad_final
        )
        iniciar_juego_escapa(pantalla, nombre_final, dificultad_final)

def modo_caza_seleccionado(pantalla):
    ANCHO, ALTO = pantalla.get_size()
    fuente_titulo = pygame.font.Font(None, 48)
    
    cuadro_nombre = CuadroTexto(ANCHO // 2 - 150, ALTO // 2 - 60, 300, 40)

    btn_siguiente = Boton(
        ANCHO // 2 - 100, cuadro_nombre.rect.bottom + 20,
        200, 50, "Continuar", VERDE, (0, 200, 0)
    )
    btn_regresar = Boton(
        ANCHO // 2 - 100, btn_siguiente.rect.bottom + 15,
        200, 50, "Regresar", ROJO, (200, 0, 0)
    )

    etapa = "nombre"
    nombre_final = ""
    dificultad_final = None

    btn_facil = Boton(ANCHO//2 - 150, ALTO//2 - 30, 300, 50, "Fácil", VERDE, (0,255,0))
    btn_medio = Boton(ANCHO//2 - 150, ALTO//2 + 40, 300, 50, "Medio", (200,200,0), (255,255,0))
    btn_dificil = Boton(ANCHO//2 - 150, ALTO//2 + 110, 300, 50, "Difícil", ROJO, (255,0,0))

    ejecutando = True

    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if etapa == "nombre":
                cuadro_nombre.handle_event(evento)

                if btn_siguiente.check_click(evento):
                    if cuadro_nombre.texto.strip():
                        nombre_final = cuadro_nombre.texto.strip()
                        etapa = "dificultad"

                if btn_regresar.check_click(evento):
                    ejecutando = False

            elif etapa == "dificultad":
                if btn_facil.check_click(evento):
                    dificultad_final = "facil"
                    ejecutando = False
                if btn_medio.check_click(evento):
                    dificultad_final = "medio"
                    ejecutando = False
                if btn_dificil.check_click(evento):
                    dificultad_final = "dificil"
                    ejecutando = False

        pantalla.fill(NEGRO)

        if etapa == "nombre":
            titulo = fuente_titulo.render("Nombre del Jugador", True, BLANCO)
            pantalla.blit(titulo, (ANCHO//2 - titulo.get_width()//2, cuadro_nombre.rect.y - 50))

            cuadro_nombre.dibujar(pantalla)
            btn_siguiente.dibujar(pantalla)
            btn_regresar.dibujar(pantalla)

        elif etapa == "dificultad":
            titulo = fuente_titulo.render("Selecciona Dificultad", True, BLANCO)
            pantalla.blit(titulo, (ANCHO//2 - titulo.get_width()//2, ALTO//2 - 120))

            btn_facil.dibujar(pantalla)
            btn_medio.dibujar(pantalla)
            btn_dificil.dibujar(pantalla)

        pygame.display.flip()

    if nombre_final and dificultad_final:
        iniciar_juego_caza(pantalla, nombre_final, dificultad_final)

def mostrar_donar(pantalla):
    pantalla_donar_loop(pantalla)

def mostrar_puntajes(pantalla):
    pantalla_puntajes_loop(pantalla)

def esperar_en_pantalla(tiempo_ms):
    inicio = pygame.time.get_ticks()
    while pygame.time.get_ticks() - inicio < tiempo_ms:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.time.wait(10)


#Funciones de los sub-menús
def dibujar_lista_puntajes(pantalla, titulo, lista_puntajes, x_centro, y_inicio, fuente_titulo, fuente_item, color_titulo):
    ANCHO_CONTENEDOR = 400
    x_inicio = x_centro - ANCHO_CONTENEDOR // 2

    texto_titulo = fuente_titulo.render(titulo, True, color_titulo)
    rect_titulo = texto_titulo.get_rect(center=(x_centro, y_inicio))
    pantalla.blit(texto_titulo, rect_titulo)

    pygame.draw.line(pantalla, color_titulo, (x_inicio, y_inicio+30), (x_inicio+ANCHO_CONTENEDOR, y_inicio+30), 2)

    y_actual = y_inicio + 60

    if not lista_puntajes:
        texto_vacio = fuente_item.render("Sin puntajes aún", True, BLANCO)
        pantalla.blit(texto_vacio, (x_inicio+10, y_actual))
        return y_actual + 40

    lista_ordenada = sorted(lista_puntajes, key=lambda x: x["puntos"], reverse=True)[:5]

    for i, item in enumerate(lista_ordenada):
        nombre = item.get("nombre", "???")
        puntos = item.get("puntos", 0)
        texto = fuente_item.render(f"{i+1}. {nombre} - {puntos}", True, BLANCO)
        pantalla.blit(texto, (x_inicio+10, y_actual))
        y_actual += 30

    return y_actual + 15

def pantalla_donar_loop(pantalla):
    ANCHO, ALTO = pantalla.get_size()
    ejecutando_donar = True
    def regresar():
        nonlocal ejecutando_donar
        ejecutando_donar = False
    btn_regresar = Boton(
        ANCHO // 2 - 150, ALTO - 100, 300, 50,
        "Volver al Menú Principal", ROJO, (200, 0, 0), regresar
    )
    fuente_titulo = pygame.font.Font(None, 74)
    fuente_mensaje = pygame.font.Font(None, 36)
    while ejecutando_donar:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            btn_regresar.check_click(evento)

        pantalla.fill(NEGRO)
        
        texto_titulo = fuente_titulo.render("¡Gracias por querer apoyar!", True, VERDE)
        rect_titulo = texto_titulo.get_rect(center=(ANCHO // 2, 100))
        pantalla.blit(texto_titulo, rect_titulo)

        mensaje = "Puedes seguir a los desarrolladores en Instagram:"
        texto_mensaje = fuente_mensaje.render(mensaje, True, BLANCO)
        rect_mensaje = texto_mensaje.get_rect(center=(ANCHO // 2, 180))
        pantalla.blit(texto_mensaje, rect_mensaje)

        mensaje = "@isaac_em13 y @brunobc03"
        texto_mensaje = fuente_mensaje.render(mensaje, True, BLANCO)
        rect_mensaje = texto_mensaje.get_rect(center=(ANCHO // 2, 220))
        pantalla.blit(texto_mensaje, rect_mensaje)
        btn_regresar.dibujar(pantalla)
        
        pygame.display.flip()

def pantalla_puntajes_loop(pantalla):
    ANCHO, ALTO = pantalla.get_size()
    puntajes_data = cargar_puntajes()

    lista_escape=puntajes_data.get("escape", [])
    lista_cazador=puntajes_data.get("cazador", [])
    
    fuente_titulo_modo = pygame.font.Font(None, 48)
    fuente_item = pygame.font.Font(None, 30)

    ejecutando_puntajes = True
    def regresar():
        nonlocal ejecutando_puntajes
        ejecutando_puntajes = False

    TAMANO_BOTON_PEQ = 80
    btn_regresar = Boton(
        15, ALTO - TAMANO_BOTON_PEQ - 20, 
        TAMANO_BOTON_PEQ, TAMANO_BOTON_PEQ,
        "Volver", ROJO, (200, 0, 0), regresar
    )
    
    #Bucle
    while ejecutando_puntajes:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            btn_regresar.check_click(evento)
        
        pantalla.fill(NEGRO)
        
        #Título
        fuente_principal = pygame.font.Font(None, 74)
        texto_principal = fuente_principal.render("RANKINGS", True, AZUL_CLARO)
        rect_principal = texto_principal.get_rect(center=(ANCHO // 2, 40))
        pantalla.blit(texto_principal, rect_principal)
        
        y_next = dibujar_lista_puntajes(
            pantalla, 
            "Top 5 - Modo Escapa", 
            lista_escape, 
            ANCHO // 2,
            90,
            fuente_titulo_modo, 
            fuente_item, 
            VERDE
        )

        dibujar_lista_puntajes(
            pantalla, 
            "Top 5 - Modo Cazador", 
            lista_cazador, 
            ANCHO // 2,
            y_next + 30,
            fuente_titulo_modo, 
            fuente_item, 
            ROJO
        )

        #Botón de regreso
        btn_regresar.dibujar(pantalla)
        
        pygame.display.flip()


### Ventana de Menú Principal ###
def menu_principal():
    pygame.init()

    ANCHO, ALTO = 800, 600
    PANTALLA = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Robo PATHS")
    

    #Logo
    logo_img = pygame.image.load(os.path.join("assets/textures", "logo.png"))
    logo_ancho = int(ANCHO * 0.7)
    logo_alto = int(logo_img.get_height() * (logo_ancho / logo_img.get_width()))
    logo_img = pygame.transform.scale(logo_img, (logo_ancho, logo_alto))
    logo_rect = logo_img.get_rect(center=(ANCHO // 2, logo_alto // 2 + 50))


    #Música
    pygame.mixer.init() 
    ruta_musica = os.path.join("assets", "sounds", "menu_music.ogg")
    pygame.mixer.music.load(ruta_musica)
    pygame.mixer.music.play(-1)

    #Dimensiones y posiciones de los botones
    ANCHO_BOTON_LARGO = ANCHO // 3
    ALTO_BOTON_LARGO = 50
    X_CENTRO = ANCHO // 2
    Y_INICIO = logo_rect.bottom + 40

    ANCHO_BOTON_PEQ = ALTO_BOTON_LARGO
    ALTO_BOTON_PEQ = ALTO_BOTON_LARGO
    ESPACIO_LATERAL = 20

    #Acciones de los botones
    def accion_escapa():
        modo_escapa_seleccionado(PANTALLA)

    def accion_cazador():
        modo_caza_seleccionado(PANTALLA)

    def accion_puntajes():
        mostrar_puntajes(PANTALLA)

    def accion_donar():
        mostrar_donar(PANTALLA)
    
    def accion_salir():
        pygame.quit()
        sys.exit()

    #Crear botones
    btn_escape = Boton(
        X_CENTRO - ANCHO_BOTON_LARGO // 2, Y_INICIO,
        ANCHO_BOTON_LARGO, ALTO_BOTON_LARGO,
        "Modo Escapa", GRIS, (100, 100, 100), accion_escapa
    )
    
    btn_cazador = Boton(
        X_CENTRO - ANCHO_BOTON_LARGO // 2, btn_escape.rect.bottom + 10,
        ANCHO_BOTON_LARGO, ALTO_BOTON_LARGO,
        "Modo Cazador", GRIS, (100, 100, 100), accion_cazador
    )
    
    btn_puntajes = Boton(
        X_CENTRO - ANCHO_BOTON_LARGO // 2, btn_cazador.rect.bottom + 10,
        ANCHO_BOTON_LARGO, ALTO_BOTON_LARGO,
        "Puntajes", GRIS, (100, 100, 100), accion_puntajes
    )

    # Botones laterales
    btn_donar = Boton(
        btn_puntajes.rect.left - ANCHO_BOTON_PEQ - ESPACIO_LATERAL, btn_puntajes.rect.centery - ALTO_BOTON_PEQ // 2,
        ANCHO_BOTON_PEQ, ALTO_BOTON_PEQ,
        "$", VERDE, (0, 200, 0), accion_donar
    )

    btn_salir = Boton(
        btn_puntajes.rect.right + ESPACIO_LATERAL, btn_puntajes.rect.centery - ALTO_BOTON_PEQ // 2,
        ANCHO_BOTON_PEQ, ALTO_BOTON_PEQ,
        "X", ROJO, (200, 0, 0), accion_salir
    )

    botones = [btn_escape, btn_cazador, btn_puntajes, btn_donar, btn_salir]

    #Bucle principal
    ejecutando = True
    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            
            for boton in botones:
                boton.check_click(evento)

        PANTALLA.fill(NEGRO)
        
        PANTALLA.blit(logo_img, logo_rect)
        
        for boton in botones:
            boton.dibujar(PANTALLA)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    menu_principal()