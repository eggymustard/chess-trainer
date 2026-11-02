import pygame
from .. import config
from ..widgets import Button, Stepper, Toggle
from ..storage import guardar_config


class SettingsScreen:
    def __init__(self, app):
        self.app = app
        self.fuente_titulo = pygame.font.SysFont("DejaVu Sans", 36, bold=True)
        self.fuente_boton = pygame.font.SysFont("DejaVu Sans", config.FUENTE_BOTON)

        x = (config.ANCHO - 560) // 2
        y = 120
        alto = 44
        espacio = 60

        cfg = self.app.config

        self.stepper_dificultad = Stepper(
            x, y, 560, alto, "Dificultad del bot (0-20)",
            cfg.get("dificultad", 5), 0, 20,
            on_change=lambda v: self._set("dificultad", v),
        )

        colores = ["blancas", "negras"]
        idx_color = colores.index(cfg.get("color_humano", "blancas")) if cfg.get("color_humano") in colores else 0
        self.toggle_color = Toggle(
            x, y + espacio, 560, alto, "Color por defecto",
            colores, idx_color, on_change=lambda v: self._set("color_humano", v),
        )

        sonido_opciones = ["on", "off"]
        idx_sonido = 0 if cfg.get("sonido", True) else 1
        self.toggle_sonido = Toggle(
            x, y + 2 * espacio, 560, alto, "Sonidos de piezas",
            sonido_opciones, idx_sonido, on_change=lambda v: self._set("sonido", v == "on"),
        )

        idx_musica = 0 if cfg.get("musica_activa", True) else 1
        self.toggle_musica = Toggle(
            x, y + 3 * espacio, 560, alto, "Música ambiental",
            sonido_opciones, idx_musica, on_change=lambda v: self._set_musica(v == "on"),
        )

        self.stepper_volumen = Stepper(
            x, y + 4 * espacio, 560, alto, "Volumen música (0-10)",
            cfg.get("volumen_musica", 3), 0, 10,
            on_change=lambda v: self._set_volumen(v),
        )

        pista_opciones = ["Pista 1", "Pista 2"]
        idx_pista = 0 if cfg.get("pista_musica", 1) == 1 else 1
        self.toggle_pista = Toggle(
            x, y + 5 * espacio, 560, alto, "Canción de fondo",
            pista_opciones, idx_pista, on_change=lambda v: self._cambiar_pista(v),
        )

        self.boton_volver = Button(
            config.ANCHO // 2 - 110, config.ALTO - 70, 220, 50,
            "Volver al menu", self._volver, fuente=self.fuente_boton
        )

    def _set(self, clave, valor): self.app.config[clave] = valor
    def _set_musica(self, valor):
        self.app.config["musica_activa"] = valor
        self.app.actualizar_musica()
    def _set_volumen(self, valor):
        self.app.config["volumen_musica"] = valor
        self.app.actualizar_musica()
    def _cambiar_pista(self, valor):
        self.app.cambiar_pista(1 if valor == "Pista 1" else 2)
    def _volver(self):
        guardar_config(self.app.config)
        self.app.ir_a("menu")

    def handle_event(self, evento):
        self.stepper_dificultad.handle_event(evento)
        self.toggle_color.handle_event(evento)
        self.toggle_sonido.handle_event(evento)
        self.toggle_musica.handle_event(evento)
        self.stepper_volumen.handle_event(evento)
        self.toggle_pista.handle_event(evento)
        self.boton_volver.handle_event(evento)

    def draw(self, pantalla):
        titulo = self.fuente_titulo.render("Ajustes", True, config.TEXTO)
        pantalla.blit(titulo, titulo.get_rect(center=(config.ANCHO // 2, 70)))

        self.stepper_dificultad.draw(pantalla)
        self.toggle_color.draw(pantalla)
        self.toggle_sonido.draw(pantalla)
        self.toggle_musica.draw(pantalla)
        self.stepper_volumen.draw(pantalla)
        self.toggle_pista.draw(pantalla)
        self.boton_volver.draw(pantalla)
