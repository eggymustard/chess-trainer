import pygame
from .. import config
from ..widgets import Button

class MenuScreen:
    def __init__(self, app):
        self.app = app
        self.fuente_titulo = pygame.font.SysFont("DejaVu Sans", 56, bold=True)
        self.fuente_boton = pygame.font.SysFont("DejaVu Sans", config.FUENTE_BOTON)
        
        self.sonido_click = None
        try:
            self.sonido_click = pygame.mixer.Sound("assets/sounds/Click.wav")
        except Exception:
            pass

        ancho_boton = 380
        alto_boton = 55
        x = (config.ANCHO - ancho_boton) // 2 + 40
        y_inicial = 220
        espacio = 68

        opciones = [
            ("Cooperativo local", self._coop_local),
            ("Jugar con teclado", self._teclado),
            ("Juega vs Entrenador", self._entrenador),
            ("Ajustes", lambda: self.app.ir_a("settings")),
            ("Salir", self.app.salir),
        ]

        self.botones = [
            Button(x, y_inicial + i * espacio, ancho_boton, alto_boton,
                   texto, cb, fuente=self.fuente_boton, sonido_click=self.sonido_click)
            for i, (texto, cb) in enumerate(opciones)
        ]

    def _coop_local(self):
        self.app.config["modo"] = "coop_local"
        self.app.ir_a("game")

    def _teclado(self):
        self.app.config["modo"] = "coordenadas"
        self.app.ir_a("game")

    def _entrenador(self):
        self.app.config["modo"] = "entrenador"
        self.app.ir_a("game")

    def handle_event(self, evento):
        for b in self.botones:
            b.handle_event(evento)

    def _draw_robot(self, pantalla, cx, cy):
        pygame.draw.line(pantalla, (200, 200, 200), (cx, cy), (cx, cy - 25), 5)
        pygame.draw.circle(pantalla, (255, 100, 100), (cx, cy - 30), 8)
        rect_cabeza = pygame.Rect(cx - 40, cy, 80, 60)
        pygame.draw.rect(pantalla, (100, 160, 220), rect_cabeza, border_radius=15)
        pygame.draw.rect(pantalla, (255, 255, 255), rect_cabeza, 3, border_radius=15)
        pygame.draw.rect(pantalla, (80, 130, 180), (cx - 50, cy + 15, 10, 25), border_radius=5)
        pygame.draw.rect(pantalla, (80, 130, 180), (cx + 40, cy + 15, 10, 25), border_radius=5)
        pygame.draw.circle(pantalla, (40, 40, 40), (cx - 15, cy + 20), 8)
        pygame.draw.circle(pantalla, (40, 40, 40), (cx + 15, cy + 20), 8)
        pygame.draw.circle(pantalla, (255, 255, 255), (cx - 16, cy + 19), 3)
        pygame.draw.circle(pantalla, (255, 255, 255), (cx + 14, cy + 19), 3)
        pygame.draw.arc(pantalla, (40, 40, 40), (cx - 15, cy + 30, 30, 15), 3.14, 0, 3)
        pygame.draw.line(pantalla, (80, 130, 180), (cx + 40, cy + 25), (cx + 80, cy + 25), 8)
        pygame.draw.circle(pantalla, (80, 130, 180), (cx + 80, cy + 25), 6)

    def draw(self, pantalla):
        tam = 100
        for fila in range(config.ALTO // tam + 1):
            for col in range(config.ANCHO // tam + 1):
                color = (35, 35, 45) if (fila + col) % 2 == 0 else (25, 25, 35)
                pygame.draw.rect(pantalla, color, (col * tam, fila * tam, tam, tam))

        titulo = self.fuente_titulo.render("Chess Trainer", True, config.TEXTO)
        pantalla.blit(titulo, titulo.get_rect(center=(config.ANCHO // 2, 100)))

        boton_entrenador = self.botones[2]
        self._draw_robot(pantalla, boton_entrenador.rect.x - 60, boton_entrenador.rect.centery - 30)

        for b in self.botones:
            b.draw(pantalla)
