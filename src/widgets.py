import pygame
from . import config


class Button:
    """Botón reutilizable para los menús."""

    def __init__(self, x, y, ancho, alto, texto, callback,
                 fuente=None, color=None, color_hover=None, sonido_click=None):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.callback = callback
        self.fuente = fuente or pygame.font.SysFont("DejaVu Sans", config.FUENTE_BOTON)
        self.color = color or config.PRIMARIO
        self.color_hover = color_hover or config.PRIMARIO_HOVER
        self.hover = False
        self.sonido_click = sonido_click

    def handle_event(self, evento):
        if evento.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(evento.pos)
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos):
                if self.sonido_click:
                    try:
                        self.sonido_click.play()
                    except Exception:
                        pass
                self.callback()

    def draw(self, pantalla):
        color = self.color_hover if self.hover else self.color
        pygame.draw.rect(pantalla, color, self.rect, border_radius=10)
        pygame.draw.rect(pantalla, config.TEXTO, self.rect, 2, border_radius=10)
        surf = self.fuente.render(self.texto, True, config.TEXTO)
        rect_texto = surf.get_rect(center=self.rect.center)
        pantalla.blit(surf, rect_texto)


class Stepper:
    def __init__(self, x, y, ancho, alto, etiqueta, valor, minimo, maximo, paso=1, on_change=None):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.etiqueta = etiqueta
        self.valor = valor
        self.minimo = minimo
        self.maximo = maximo
        self.paso = paso
        self.on_change = on_change
        self.fuente_label = pygame.font.SysFont("DejaVu Sans", 22)
        self.fuente_valor = pygame.font.SysFont("DejaVu Sans", 24, bold=True)
        tam = alto
        self.rect_mas = pygame.Rect(self.rect.right - tam, y, tam, tam)
        self.rect_menos = pygame.Rect(self.rect_mas.left - tam, y, tam, tam)
        self.rect_valor = pygame.Rect(self.rect_menos.left - 80, y, 80, tam)

    def _cambiar(self, delta):
        nuevo = max(self.minimo, min(self.maximo, self.valor + delta * self.paso))
        if nuevo != self.valor:
            self.valor = nuevo
            if self.on_change: self.on_change(nuevo)

    def handle_event(self, evento):
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect_menos.collidepoint(evento.pos): self._cambiar(-1)
            elif self.rect_mas.collidepoint(evento.pos): self._cambiar(+1)

    def draw(self, pantalla):
        label = self.fuente_label.render(self.etiqueta, True, config.TEXTO)
        pantalla.blit(label, label.get_rect(midleft=(self.rect.x + 10, self.rect.centery)))
        for rect, texto in [(self.rect_menos, "-"), (self.rect_mas, "+")]:
            pygame.draw.rect(pantalla, config.PRIMARIO, rect, border_radius=8)
            pygame.draw.rect(pantalla, config.TEXTO, rect, 2, border_radius=8)
            t = self.fuente_valor.render(texto, True, config.TEXTO)
            pantalla.blit(t, t.get_rect(center=rect.center))
        pygame.draw.rect(pantalla, (50, 50, 65), self.rect_valor, border_radius=8)
        pygame.draw.rect(pantalla, config.TEXTO, self.rect_valor, 2, border_radius=8)
        v = self.fuente_valor.render(str(self.valor), True, config.TEXTO)
        pantalla.blit(v, v.get_rect(center=self.rect_valor.center))


class Toggle:
    def __init__(self, x, y, ancho, alto, etiqueta, opciones, indice=0, on_change=None):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.etiqueta = etiqueta
        self.opciones = opciones
        self.indice = indice
        self.on_change = on_change
        self.fuente_label = pygame.font.SysFont("DejaVu Sans", 22)
        self.fuente_valor = pygame.font.SysFont("DejaVu Sans", 22, bold=True)
        self.hover = False

    @property
    def valor(self): return self.opciones[self.indice]

    def handle_event(self, evento):
        if evento.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(evento.pos)
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos):
                self.indice = (self.indice + 1) % len(self.opciones)
                if self.on_change: self.on_change(self.valor)

    def draw(self, pantalla):
        label = self.fuente_label.render(self.etiqueta, True, config.TEXTO)
        pantalla.blit(label, label.get_rect(midleft=(self.rect.x + 10, self.rect.centery)))
        color = config.PRIMARIO_HOVER if self.hover else config.PRIMARIO
        rect_val = pygame.Rect(self.rect.right - 200, self.rect.y, 200, self.rect.height)
        pygame.draw.rect(pantalla, color, rect_val, border_radius=8)
        pygame.draw.rect(pantalla, config.TEXTO, rect_val, 2, border_radius=8)
        v = self.fuente_valor.render(str(self.valor), True, config.TEXTO)
        pantalla.blit(v, v.get_rect(center=rect_val.center))
