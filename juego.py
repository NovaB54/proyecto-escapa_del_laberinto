import pygame
import sys
import os
import json
import time

# Importaciones necesarias del juego principal
from Escapa_del_Laberinto import (
    Terreno, Camino, Muro, Liana, Tunel, Mapa, 
    Entidad, Trampa, Jugador, Cazador, Juego,
    cargar_puntajes, guardar_puntajes
)

import Escapa_del_Laberinto

# --- Colores Globales ---
NEGRO = (0, 0, 0)
GRIS = (50, 50, 50)
BLANCO = (255, 255, 255)
VERDE = (0, 150, 0)
ROJO = (150, 0, 0)
AZUL_CLARO = (173, 216, 230)

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


### Funciones de Interfaz (Pantallas Secundarias) ###

#Incio de juego
def iniciar_juego_escapa(pantalla, nombre_jugador):
    nombre = nombre_jugador if nombre_jugador.strip() else "Invitado"
    juego = Juego(filas=15, columnas=15, cantidad_cazadores=3, modo="caza", nombre_jugador=nombre)
    
    tamaño_celda = 30
    ancho_mapa = juego.mapa.ancho * tamaño_celda
    alto_mapa = juego.mapa.alto * tamaño_celda
    offset_x = (pantalla.get_width() - ancho_mapa) // 2
    offset_y = (pantalla.get_height() - alto_mapa) // 2
    
    reloj = pygame.time.Clock()
    ejecutando_juego = True
    
    while ejecutando_juego:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if evento.type == pygame.KEYDOWN:
                if juego.juego_terminado:
                    if evento.key == pygame.K_SPACE:
                        ejecutando_juego = False
                else:
                    if evento.key == pygame.K_ESCAPE:
                        ejecutando_juego = False
                    elif evento.key == pygame.K_UP:
                        juego.mover_jugador(-1, 0)
                    elif evento.key == pygame.K_DOWN:
                        juego.mover_jugador(1, 0)
                    elif evento.key == pygame.K_LEFT:
                        juego.mover_jugador(0, -1)
                    elif evento.key == pygame.K_RIGHT:
                        juego.mover_jugador(0, 1)
                    elif evento.key == pygame.K_SPACE:
                        juego.correr_jugador(0, 1)
                    elif evento.key == pygame.K_t:
                        juego.colocar_trampa()
        
        #Actualiza el juego
        if not juego.juego_terminado:
            juego.tick()

        reproducir_start_game() 

        #Dibujado
        pantalla.fill(NEGRO)
        
        if not juego.juego_terminado:
            dibujar_mapa(pantalla, juego, tamaño_celda, offset_x, offset_y)
            dibujar_trampas(pantalla, juego.jugador.trampas, tamaño_celda, offset_x, offset_y)
            dibujar_jugador(pantalla, juego.jugador, tamaño_celda, offset_x, offset_y)
            dibujar_cazadores(pantalla, juego.cazadores, tamaño_celda, offset_x, offset_y)
            dibujar_ui(pantalla, juego, pantalla.get_width())
        else:
            dibujar_game_over(pantalla, juego.resultado, juego.puntos)
        
        pygame.display.flip()
        reloj.tick(10)

def iniciar_juego_escapa(pantalla, nombre_jugador):
    nombre = nombre_jugador if nombre_jugador.strip() else "Invitado"
    juego = Juego(filas=15, columnas=15, cantidad_cazadores=3, modo="caza", nombre_jugador=nombre)
    
    tamaño_celda = 30
    ancho_mapa = juego.mapa.ancho * tamaño_celda
    alto_mapa = juego.mapa.alto * tamaño_celda
    offset_x = (pantalla.get_width() - ancho_mapa) // 2
    offset_y = (pantalla.get_height() - alto_mapa) // 2
    
    reloj = pygame.time.Clock()
    ejecutando_juego = True
    
    while ejecutando_juego:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if evento.type == pygame.KEYDOWN:
                if juego.juego_terminado:
                    if evento.key == pygame.K_SPACE:
                        ejecutando_juego = False
                else:
                    if evento.key == pygame.K_ESCAPE:
                        ejecutando_juego = False
                    elif evento.key == pygame.K_UP:
                        juego.mover_jugador(-1, 0)
                    elif evento.key == pygame.K_DOWN:
                        juego.mover_jugador(1, 0)
                    elif evento.key == pygame.K_LEFT:
                        juego.mover_jugador(0, -1)
                    elif evento.key == pygame.K_RIGHT:
                        juego.mover_jugador(0, 1)
                    elif evento.key == pygame.K_SPACE:
                        juego.correr_jugador(0, 1)
                    elif evento.key == pygame.K_t:
                        juego.colocar_trampa()
        
        #Actualiza el juego
        if not juego.juego_terminado:
            juego.tick()
        
        #Dibujado
        pantalla.fill(NEGRO)
        
        if not juego.juego_terminado:
            dibujar_mapa(pantalla, juego, tamaño_celda, offset_x, offset_y)
            dibujar_trampas(pantalla, juego.jugador.trampas, tamaño_celda, offset_x, offset_y)
            dibujar_jugador(pantalla, juego.jugador, tamaño_celda, offset_x, offset_y)
            dibujar_cazadores(pantalla, juego.cazadores, tamaño_celda, offset_x, offset_y)
            dibujar_ui(pantalla, juego, pantalla.get_width())
        else:
            dibujar_game_over(pantalla, juego.resultado, juego.puntos)
        
        pygame.display.flip()
        reloj.tick(10)

#Al seleccionar un botón
def modo_escapa_seleccionado(pantalla):
    ANCHO, ALTO = pantalla.get_size()
    fuente_titulo = pygame.font.Font(None, 48)
    
    cuadro_nombre = CuadroTexto(ANCHO // 2 - 150, ALTO // 2 - 50, 300, 40)
    
    def regresar():
        pass 

    def jugar():
        iniciar_juego_escapa(pantalla, cuadro_nombre.texto)
        
    btn_jugar = Boton(
        ANCHO // 2 - 100, cuadro_nombre.rect.bottom + 30, 200, 50,
        "Jugar", VERDE, (0, 200, 0), jugar
    )
    
    btn_regresar = Boton(
        ANCHO // 2 - 100, btn_jugar.rect.bottom + 10, 200, 50,
        "Regresar", ROJO, (200, 0, 0), regresar
    )
    
    elementos = [btn_jugar, btn_regresar]
    
    ejecutando_sub_menu = True
    while ejecutando_sub_menu:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            cuadro_nombre.handle_event(evento)
            
            if btn_regresar.check_click(evento):
                ejecutando_sub_menu = False
            
            if btn_jugar.check_click(evento):
                if cuadro_nombre.texto.strip():
                    ejecutando_sub_menu = False

        pantalla.fill(NEGRO)
        
        texto_titulo = fuente_titulo.render("Nombre del Jugador", True, BLANCO)
        rect_titulo = texto_titulo.get_rect(center=(ANCHO // 2, cuadro_nombre.rect.y - 30))
        pantalla.blit(texto_titulo, rect_titulo)
        
        cuadro_nombre.dibujar(pantalla)
        for elemento in elementos:
            elemento.dibujar(pantalla)

        pygame.display.flip()

def modo_caza_seleccionado(pantalla):
    ANCHO, ALTO = pantalla.get_size()
    fuente_titulo = pygame.font.Font(None, 48)
    
    #Elementos de la interfaz
    cuadro_nombre = CuadroTexto(ANCHO // 2 - 150, ALTO // 2 - 50, 300, 40)
    
    def regresar():
        pass 

    def jugar():
        iniciar_juego_caza(pantalla, cuadro_nombre.texto)
        
    btn_jugar = Boton(
        ANCHO // 2 - 100, cuadro_nombre.rect.bottom + 30, 200, 50,
        "Jugar", VERDE, (0, 200, 0), jugar
    )
    
    btn_regresar = Boton(
        ANCHO // 2 - 100, btn_jugar.rect.bottom + 10, 200, 50,
        "Regresar", ROJO, (200, 0, 0), regresar
    )
    
    elementos = [btn_jugar, btn_regresar]
    
    ejecutando_sub_menu = True
    while ejecutando_sub_menu:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            cuadro_nombre.handle_event(evento)
            
            if btn_regresar.check_click(evento):
                ejecutando_sub_menu = False
            
            if btn_jugar.check_click(evento):
                if cuadro_nombre.texto.strip():
                    ejecutando_sub_menu = False

        pantalla.fill(NEGRO)
        
        texto_titulo = fuente_titulo.render("Nombre del Jugador", True, BLANCO)
        rect_titulo = texto_titulo.get_rect(center=(ANCHO // 2, cuadro_nombre.rect.y - 30))
        pantalla.blit(texto_titulo, rect_titulo)
        
        cuadro_nombre.dibujar(pantalla)
        for elemento in elementos:
            elemento.dibujar(pantalla)

        pygame.display.flip()

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
    
    pygame.draw.line(pantalla, color_titulo, (x_inicio, y_inicio + 30), (x_inicio + ANCHO_CONTENEDOR, y_inicio + 30), 2)
    
    y_header = y_inicio + 45
    texto_header_nombre = fuente_item.render("Nombre:", True, BLANCO)
    pantalla.blit(texto_header_nombre, (x_inicio + 10, y_header))
    
    texto_header_puntos = fuente_item.render("Puntaje:", True, BLANCO)
    rect_header_puntos = texto_header_puntos.get_rect(right=x_inicio + ANCHO_CONTENEDOR - 10, top=y_header)
    pantalla.blit(texto_header_puntos, rect_header_puntos)
    
    y_actual = y_inicio + 75
    
    if not lista_puntajes:
        texto_vacio = fuente_item.render("Aún no hay puntajes en este modo.", True, GRIS)
        pantalla.blit(texto_vacio, (x_inicio + 10, y_actual))
        return y_actual + 40
        
    lista_puntajes_ordenada = sorted(
        lista_puntajes, 
        key=lambda x: x['puntos'], 
        reverse=True
    )[:5] 

    for i, item in enumerate(lista_puntajes_ordenada):
        nombre = item.get('nombre', 'Desconocido')
        puntos = item.get('puntos', 0)
        
        color_item = VERDE if i == 0 else BLANCO
        
        texto_nombre = fuente_item.render(f"{i+1}. {nombre}", True, color_item)
        pantalla.blit(texto_nombre, (x_inicio + 10, y_actual))
        
        texto_puntos = fuente_item.render(str(puntos), True, color_item)
        rect_puntos = texto_puntos.get_rect(right=x_inicio + ANCHO_CONTENEDOR - 10, top=y_actual)
        pantalla.blit(texto_puntos, rect_puntos)
        
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

        mensaje = "@issacem13 y @brunobc03"
        texto_mensaje = fuente_mensaje.render(mensaje, True, BLANCO)
        rect_mensaje = texto_mensaje.get_rect(center=(ANCHO // 2, 220))
        pantalla.blit(texto_mensaje, rect_mensaje)
        btn_regresar.dibujar(pantalla)
        
        pygame.display.flip()

def pantalla_puntajes_loop(pantalla):
    ANCHO, ALTO = pantalla.get_size()
    try:
        puntajes_data = cargar_puntajes()
    except Exception as e:
        print(f"No hay puntajes aún: {e}")
        puntajes_data = {"escape": [], "cazador": []}
        
    lista_escape = puntajes_data.get("escape", [])
    lista_cazador = puntajes_data.get("cazador", [])
    
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