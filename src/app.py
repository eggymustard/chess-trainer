import os
import pygame
import sys
from . import config
from .storage import cargar_config


class App:
    def __init__(self):
        pygame.init()
        self.config = cargar_config()
        
        self.pantalla = pygame.display.set_mode((config.ANCHO, config.ALTO))
        pygame.display.set_caption(config.TITULO)
        self.reloj = pygame.time.Clock()
        
        self.musica_cargada = False
        self.cargar_musica_actual()
        self.actualizar_musica()

        self.screen = None
        self._ir_a("menu")

    def cargar_musica_actual(self):
        pista = self.config.get("pista_musica", 1)
        archivo = "assets/sounds/menu_music.mp3" if pista == 1 else "assets/sounds/menu_music_2.mp3"
        try:
            pygame.mixer.music.load(archivo)
            self.musica_cargada = True
        except Exception as e:
            print(f"No se pudo cargar la música: {e}")
            self.musica_cargada = False

    def actualizar_musica(self):
        if not self.musica_cargada:
            return
        vol = self.config.get("volumen_musica", 3) / 10.0
        pygame.mixer.music.set_volume(vol)
        if self.config.get("musica_activa", True):
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play(-1)
            else:
                pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()

    def cambiar_pista(self, nueva_pista):
        self.config["pista_musica"] = nueva_pista
        pygame.mixer.music.stop()
        self.cargar_musica_actual()
        self.actualizar_musica()

    def _ir_a(self, nombre):
        from .screens.menu import MenuScreen
        from .screens.game import GameScreen
        from .screens.settings import SettingsScreen

        pantallas = {
            "menu": MenuScreen,
            "game": GameScreen,
            "settings": SettingsScreen,
        }
        if self.screen is not None and hasattr(self.screen, "_cerrar_motor"):
            self.screen._cerrar_motor()
        self.screen = pantallas[nombre](self)

    def ir_a(self, nombre):
        self._ir_a(nombre)

    def salir(self):
        if self.screen is not None and hasattr(self.screen, "_cerrar_motor"):
            try:
                self.screen._cerrar_motor()
            except Exception:
                pass
        pygame.quit()
        sys.exit()

    def run(self):
        while True:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.salir()
                self.screen.handle_event(evento)

            self.pantalla.fill(config.FONDO)
            self.screen.draw(self.pantalla)
            pygame.display.flip()
            self.reloj.tick(config.FPS)
