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

# --- Colores Globales ---
NEGRO = (0, 0, 0)
GRIS = (50, 50, 50)
BLANCO = (255, 255, 255)
VERDE = (0, 150, 0)
ROJO = (150, 0, 0)
AZUL_CLARO = (173, 216, 230)

# --- Clases de Interfaz ---

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
            if self.accion:
                self.accion()
            return True
        return False

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
                    # No hace nada al presionar Enter, solo desactiva
                    self.activo = False
                    self.color = self.color_inactivo
                elif event.key == pygame.K_BACKSPACE:
                    self.texto = self.texto[:-1]
                else:
                    # Limita el texto a 20 caracteres para evitar desbordamiento
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


# --- Funciones de Interfaz (Pantallas Secundarias) ---

def iniciar_juego_escapa(pantalla, nombre_jugador):
    """Inicia el bucle de juego en modo 'escape'."""
    # Aseguramos un nombre válido si no se ingresó nada
    nombre = nombre_jugador if nombre_jugador.strip() else "Jugador Invitado"
    
    # Aquí es donde se inicializa la lógica del juego del archivo Escapa_del_Laberinto.py
    juego = Juego(filas=10, columnas=10, cantidad_cazadores=3, modo="escape", nombre_jugador=nombre)
    
    # --- Bucle de Juego de Prueba (Placeholder para el juego real) ---
    
    # En un juego real, aquí iría el bucle de Pygame que maneja la física, 
    # la actualización de los cazadores, el dibujo del mapa, etc.
    
    # Para la demostración, solo mostramos una pantalla de "Juego Iniciado"
    pantalla.fill((0, 100, 0)) # Fondo verde de juego
    fuente = pygame.font.Font(None, 48)
    
    texto_juego = fuente.render(f"JUEGO INICIADO (Modo: Escapa)", True, BLANCO)
    texto_nombre = fuente.render(f"Jugador: {nombre}", True, BLANCO)
    texto_continuar = pygame.font.Font(None, 36).render("Volviendo al menú en 5s...", True, BLANCO)
    
    rect_juego = texto_juego.get_rect(center=(pantalla.get_width() // 2, pantalla.get_height() // 2 - 50))
    rect_nombre = texto_nombre.get_rect(center=(pantalla.get_width() // 2, pantalla.get_height() // 2))
    rect_continuar = texto_continuar.get_rect(center=(pantalla.get_width() // 2, pantalla.get_height() // 2 + 50))

    pantalla.blit(texto_juego, rect_juego)
    pantalla.blit(texto_nombre, rect_nombre)
    pantalla.blit(texto_continuar, rect_continuar)
    
    pygame.display.flip()
    esperar_en_pantalla(5000) # Espera 5 segundos antes de volver al menú principal

def modo_escapa_seleccionado(pantalla):
    ANCHO, ALTO = pantalla.get_size()
    fuente_titulo = pygame.font.Font(None, 48)
    
    # Elementos de la interfaz
    cuadro_nombre = CuadroTexto(ANCHO // 2 - 150, ALTO // 2 - 50, 300, 40)
    
    # Función para regresar al menú principal
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
            
            # Chequear clicks de botones
            if btn_regresar.check_click(evento):
                ejecutando_sub_menu = False # Regresa al menu principal
            
            if btn_jugar.check_click(evento):
                if cuadro_nombre.texto.strip():
                    ejecutando_sub_menu = False # Inicia el juego y luego regresa al menú principal
                else:
                    # Opcional: Mostrar mensaje de error si el nombre está vacío
                    print("Por favor, ingresa tu nombre para jugar.")

        # Dibujo de la pantalla
        pantalla.fill(NEGRO) # Fondo oscuro para el submenú
        
        # Texto del título
        texto_titulo = fuente_titulo.render("Nombre del Jugador", True, BLANCO)
        rect_titulo = texto_titulo.get_rect(center=(ANCHO // 2, cuadro_nombre.rect.y - 30))
        pantalla.blit(texto_titulo, rect_titulo)
        
        # Dibujar elementos
        cuadro_nombre.dibujar(pantalla)
        for elemento in elementos:
            elemento.dibujar(pantalla)

        pygame.display.flip()

def modo_caza_seleccionado(pantalla):
    # Interfaz de modo Cazador (vacía)
    pantalla.fill((50, 0, 0))
    fuente = pygame.font.Font(None, 74)
    texto = fuente.render("MODO CAZADOR", True, BLANCO)
    rect_texto = texto.get_rect(center=(pantalla.get_width() // 2, pantalla.get_height() // 2))
    pantalla.blit(texto, rect_texto)
    pygame.display.flip()
    esperar_en_pantalla(3000)

def mostrar_puntajes(pantalla):
    # Interfaz de Puntajes (vacía)
    pantalla.fill((0, 0, 50))
    fuente = pygame.font.Font(None, 74)
    texto = fuente.render("PUNTAJES", True, BLANCO)
    rect_texto = texto.get_rect(center=(pantalla.get_width() // 2, pantalla.get_height() // 2))
    pantalla.blit(texto, rect_texto)
    pygame.display.flip()
    esperar_en_pantalla(3000)

def mostrar_donar(pantalla):
    # Interfaz de Donar (vacía)
    pantalla.fill((50, 50, 0))
    fuente = pygame.font.Font(None, 74)
    texto = fuente.render("PANTALLA DONAR", True, BLANCO)
    rect_texto = texto.get_rect(center=(pantalla.get_width() // 2, pantalla.get_height() // 2))
    pantalla.blit(texto, rect_texto)
    pygame.display.flip()
    esperar_en_pantalla(3000)

def esperar_en_pantalla(tiempo_ms):
    """Mantiene la pantalla actual por un tiempo determinado."""
    inicio = pygame.time.get_ticks()
    while pygame.time.get_ticks() - inicio < tiempo_ms:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.time.wait(10) # Espera un poco para evitar uso excesivo de CPU

### Ventana de Menú Principal ###
def menu_principal():
    pygame.init()

    # Configuración de la pantalla
    ANCHO, ALTO = 800, 600
    PANTALLA = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Robo PATHS")
    
    # Logo y dimensiones (código original)
    try:
        # Se asume la ruta correcta para tu logo
        logo_img = pygame.image.load(os.path.join("assets/gui", "logo.png"))
        logo_ancho = int(ANCHO * 0.7)
        logo_alto = int(logo_img.get_height() * (logo_ancho / logo_img.get_width()))
        logo_img = pygame.transform.scale(logo_img, (logo_ancho, logo_alto))
        logo_rect = logo_img.get_rect(center=(ANCHO // 2, logo_alto // 2 + 50))
    except pygame.error:
        print("Error: No se encontró 'assets/gui/logo.png'. Usando un placeholder.")
        # Placeholder si el logo falla
        logo_img = pygame.Surface((300, 100))
        logo_img.fill(BLANCO)
        fuente_ph = pygame.font.Font(None, 48)
        texto_ph = fuente_ph.render("LOGO", True, NEGRO)
        rect_ph_texto = texto_ph.get_rect(center=(150, 50))
        logo_img.blit(texto_ph, rect_ph_texto)
        logo_rect = logo_img.get_rect(center=(ANCHO // 2, 50 + 100 // 2 + 20))


    # Dimensiones y posiciones de los botones
    ANCHO_BOTON_LARGO = ANCHO // 3
    ALTO_BOTON_LARGO = 50
    X_CENTRO = ANCHO // 2
    Y_INICIO = logo_rect.bottom + 40

    ANCHO_BOTON_PEQ = ALTO_BOTON_LARGO
    ALTO_BOTON_PEQ = ALTO_BOTON_LARGO
    ESPACIO_LATERAL = 20

    # Funciones de acción para los botones
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

    # Creación de los botones
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

    # Bucle principal del juego
    ejecutando = True
    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            
            for boton in botones:
                boton.check_click(evento)

        PANTALLA.fill(NEGRO)
        
        PANTALLA.blit(logo_img, logo_rect)
            
        # Dibujar botones
        for boton in botones:
            boton.dibujar(PANTALLA)

        # Actualizar la pantalla
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    menu_principal()