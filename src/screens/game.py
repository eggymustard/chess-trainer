import shutil
import os
import pygame
import chess
import chess.engine
from .. import config
from ..widgets import Button
from ..coach import Coach

TAM_CASILLA = 60
TABLERO_X = 50
TABLERO_Y = 82

COACH_X = 560
COACH_Y = 82
COACH_W = 220
COACH_H = 480

PIEZAS_UNICODE = {
    'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
    'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚',
}

LETRAS_COL = "abcdefgh"
NUMEROS_FILA = "87654321"

class GameScreen:
    def __init__(self, app):
        self.app = app
        self.board = chess.Board()
        self.seleccion = None
        self.engine = None
        self.pensando = False
        
        self.modo_coordenadas = (app.config.get("modo") == "coordenadas")
        self.mostrar_coach = (app.config.get("modo") == "entrenador")
        # Ocultar el botón de pista en modo cooperativo local
        self.mostrar_pista = (app.config.get("modo") != "coop_local") 
        
        self.coach = Coach()
        
        self.pistas_usadas = 0
        self.pista_mov = None 
        
        self.entrada = ""
        self.mensaje_error = ""
        self.error_timer = 0

        self.fuente_pieza = pygame.font.SysFont("DejaVu Sans", 46)
        self.fuente_info = pygame.font.SysFont("DejaVu Sans", 22)
        self.fuente_coord = pygame.font.SysFont("DejaVu Sans", 18, bold=True)
        self.fuente_input = pygame.font.SysFont("DejaVu Sans Mono", 22)
        self.fuente_boton = pygame.font.SysFont("DejaVu Sans", config.FUENTE_BOTON)
        self.fuente_coach = pygame.font.SysFont("DejaVu Sans", 16)

        self.sonidos = {}
        try:
            pygame.mixer.init()
            self.sonidos["move"] = pygame.mixer.Sound("assets/sounds/Move.wav")
            self.sonidos["capture"] = pygame.mixer.Sound("assets/sounds/Capture.wav")
            self.sonidos["check"] = pygame.mixer.Sound("assets/sounds/Check.wav")
            self.sonidos["checkmate"] = pygame.mixer.Sound("assets/sounds/Checkmate.wav")
            self.sonidos["castle"] = pygame.mixer.Sound("assets/sounds/Castle.wav")
        except Exception as e:
            print(f"No se pudieron cargar los sonidos: {e}")

        self.rect_input = pygame.Rect(TABLERO_X, TABLERO_Y + 8 * TAM_CASILLA + 28, 8 * TAM_CASILLA, 32)
        
        self.boton_volver = Button(TABLERO_X, config.ALTO - 50, 150, 34, "Volver", self._volver_menu, fuente=self.fuente_boton)
        self.boton_pista = Button(TABLERO_X + 8 * TAM_CASILLA - 150, config.ALTO - 50, 150, 34, "Pista", self._dar_pista, fuente=self.fuente_boton)

        self._iniciar_motor()
        if self._modo_bot() and self.app.config.get("color_humano") == "negras":
            self._bot_mover()

    def _reproducir_sonido(self, tipo):
        if not self.app.config.get("sonido", True):
            return
        if tipo in self.sonidos:
            try:
                self.sonidos[tipo].play()
            except Exception:
                pass

    def _modo_bot(self):
        return self.app.config.get("modo") in ("vs_bot", "entrenador")

    def _iniciar_motor(self):
        if not self._modo_bot():
            return
        try:
            path = "bin/stockfish"
            if not os.path.exists(path):
                path = shutil.which("stockfish")
            if not path:
                return
            self.engine = chess.engine.SimpleEngine.popen_uci(path)
            nivel = self.app.config.get("dificultad", 5)
            self.engine.configure({"Skill Level": nivel})
        except Exception as e:
            print(f"No se pudo iniciar Stockfish: {e}")

    def _cerrar_motor(self):
        if self.engine is not None:
            try:
                self.engine.quit()
            except Exception:
                pass
            self.engine = None

    def _volver_menu(self):
        self._cerrar_motor()
        self.app.ir_a("menu")

    def _dar_pista(self):
        if self.engine is None:
            return
        
        if self.coach.pensando:
            return

        self.mostrar_coach = True
        
        try:
            info = self.engine.analyse(self.board, chess.engine.Limit(time=1.0))
            if isinstance(info, list):
                info = info[0]
                
            if "pv" in info and info["pv"]:
                mov = info["pv"][0]
                san = self.board.san(mov)
                self.pista_mov = mov
                self.pistas_usadas += 1
                
                contexto = f"Datos: La mejor jugada es {san}."
                self.coach.pedir_consejo(contexto, tipo="pista")
            else:
                self.coach.ultimo_consejo = "No encontré jugadas."
        except Exception as e:
            print(f"Error en Pista: {e}")
            self.coach.ultimo_consejo = "Error al calcular pista."

    def _es_turno_humano(self):
        if self.board.is_game_over():
            return False
        if not self._modo_bot():
            return True
        color_humano = self.app.config.get("color_humano", "blancas")
        return self.board.turn == (chess.WHITE if color_humano == "blancas" else chess.BLACK)

    def _bot_mover(self):
        if self.engine is None or self.board.is_game_over():
            return
        self.pensando = True
        self.app.pantalla.fill(config.FONDO)
        self.draw(self.app.pantalla)
        pygame.display.flip()
        try:
            result = self.engine.play(self.board, chess.engine.Limit(time=0.5))
            if result.move:
                es_captura = self.board.is_capture(result.move)
                self.board.push(result.move)
                self.pista_mov = None
                if self.board.is_checkmate(): self._reproducir_sonido("checkmate")
                elif self.board.is_check(): self._reproducir_sonido("check")
                elif es_captura: self._reproducir_sonido("capture")
                else: self._reproducir_sonido("move")
        except Exception as e:
            print(f"Error en el bot: {e}")
        self.pensando = False

    def _handle_key_coordenadas(self, evento):
        self.error_timer = 0
        if evento.key == pygame.K_BACKSPACE: self.entrada = self.entrada[:-1]
        elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER): self._procesar_entrada()
        elif evento.key == pygame.K_ESCAPE: self.entrada = ""
        else:
            if len(self.entrada) < 5:
                ch = evento.unicode
                if ch and ch.isprintable(): self.entrada += ch.lower()

    def _procesar_entrada(self):
        texto = self.entrada.strip().lower().replace("-", "").replace(" ", "")
        self.entrada = ""
        if not texto: return
        if self.board.is_game_over():
            self.mensaje_error = "Partida terminada"
            self.error_timer = 90
            return
        try:
            mov = chess.Move.from_uci(texto)
            if mov in self.board.legal_moves:
                es_captura = self.board.is_capture(mov)
                self.board.push(mov)
                self.pista_mov = None
                if self.board.is_checkmate(): self._reproducir_sonido("checkmate")
                elif self.board.is_check(): self._reproducir_sonido("check")
                elif es_captura: self._reproducir_sonido("capture")
                else: self._reproducir_sonido("move")
                self.mensaje_error = ""
                return
        except ValueError:
            pass
        if len(texto) == 4:
            try:
                mov = chess.Move.from_uci(texto + "q")
                if mov in self.board.legal_moves:
                    es_captura = self.board.is_capture(mov)
                    self.board.push(mov)
                    self.pista_mov = None
                    if self.board.is_checkmate(): self._reproducir_sonido("checkmate")
                    elif self.board.is_check(): self._reproducir_sonido("check")
                    elif es_captura: self._reproducir_sonido("capture")
                    else: self._reproducir_sonido("move")
                    self.mensaje_error = ""
                    return
            except ValueError:
                pass
        self.mensaje_error = "Movimiento invalido"
        self.error_timer = 90

    def _casilla_desde_pos(self, pos):
        x, y = pos
        if not (TABLERO_X <= x < TABLERO_X + 8 * TAM_CASILLA): return None
        if not (TABLERO_Y <= y < TABLERO_Y + 8 * TAM_CASILLA): return None
        return ((y - TABLERO_Y) // TAM_CASILLA, (x - TABLERO_X) // TAM_CASILLA)

    def _square_desde_fila_col(self, fila, col):
        return chess.square(col, 7 - fila)

    def _intentar_mover(self, origen, destino):
        for promo in [None, chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]:
            mov = chess.Move(origen, destino, promotion=promo) if promo else chess.Move(origen, destino)
            if mov in self.board.legal_moves:
                es_captura = self.board.is_capture(mov)
                
                if self.mostrar_coach and self.engine:
                    try:
                        jugada_san = self.board.san(mov)
                        
                        if self.pista_mov and mov == self.pista_mov:
                            self.board.push(mov)
                            self.pista_mov = None
                            self.coach.pedir_consejo("", tipo="feedback", jugada_san=jugada_san, es_mejor=True)
                        else:
                            info = self.engine.analyse(self.board, chess.engine.Limit(time=1.0))
                            if isinstance(info, list): info = info[0]
                            mejor_mov = info["pv"][0] if ("pv" in info and info["pv"]) else None
                            mejor_san = self.board.san(mejor_mov) if mejor_mov else "desconocida"
                            
                            self.board.push(mov)
                            self.pista_mov = None
                            
                            if mejor_mov and mov == mejor_mov:
                                self.coach.pedir_consejo("", tipo="feedback", jugada_san=jugada_san, es_mejor=True)
                            else:
                                self.coach.pedir_consejo("", tipo="feedback", jugada_san=jugada_san, mejor_san=mejor_san, es_mejor=False)
                    except Exception as e:
                        print(f"Error al generar contexto: {e}")
                        self.board.push(mov)
                        self.pista_mov = None
                else:
                    self.board.push(mov)
                    self.pista_mov = None

                if self.board.is_checkmate(): self._reproducir_sonido("checkmate")
                elif self.board.is_check(): self._reproducir_sonido("check")
                elif es_captura: self._reproducir_sonido("capture")
                else: self._reproducir_sonido("move")
                return True
        return False

    def handle_event(self, evento):
        self.boton_volver.handle_event(evento)
        
        # Solo procesar el botón de pista si está visible
        if self.mostrar_pista:
            self.boton_pista.handle_event(evento)

        if self.modo_coordenadas:
            if evento.type == pygame.KEYDOWN: self._handle_key_coordenadas(evento)
            return

        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            # Solo comprobar clic en pista si está visible
            if self.boton_volver.rect.collidepoint(evento.pos) or (self.mostrar_pista and self.boton_pista.rect.collidepoint(evento.pos)):
                return
            if not self._es_turno_humano(): return
            rc = self._casilla_desde_pos(evento.pos)
            if rc is None: return
            fila, col = rc
            square = self._square_desde_fila_col(fila, col)

            if self.seleccion is None:
                pieza = self.board.piece_at(square)
                if pieza and pieza.color == self.board.turn: self.seleccion = (fila, col)
            else:
                sf, sc = self.seleccion
                origen = self._square_desde_fila_col(sf, sc)
                if self._intentar_mover(origen, square):
                    self.seleccion = None
                    if not self.board.is_game_over() and not self._es_turno_humano(): self._bot_mover()
                else:
                    self.seleccion = None

    def _draw_coordenadas(self, pantalla):
        for col in range(8):
            letra = LETRAS_COL[col]
            x = TABLERO_X + col * TAM_CASILLA + TAM_CASILLA // 2
            y = TABLERO_Y + 8 * TAM_CASILLA + 12
            surf = self.fuente_coord.render(letra, True, config.TEXTO)
            pantalla.blit(surf, surf.get_rect(center=(x, y)))
        for fila in range(8):
            numero = NUMEROS_FILA[fila]
            x = TABLERO_X - 16
            y = TABLERO_Y + fila * TAM_CASILLA + TAM_CASILLA // 2
            surf = self.fuente_coord.render(numero, True, config.TEXTO)
            pantalla.blit(surf, surf.get_rect(center=(x, y)))

    def _draw_input(self, pantalla):
        border_color = (255, 100, 100) if self.error_timer > 0 else config.TEXTO
        pygame.draw.rect(pantalla, (50, 50, 65), self.rect_input, border_radius=6)
        pygame.draw.rect(pantalla, border_color, self.rect_input, 2, border_radius=6)

        if self.error_timer > 0:
            texto, color = self.mensaje_error, (255, 100, 100)
        elif self.entrada:
            cursor = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else " "
            texto, color = self.entrada + cursor, config.TEXTO
        else:
            texto, color = "escribe: e2e4  (Enter para mover)", (120, 120, 130)

        surf = self.fuente_input.render(texto, True, color)
        pantalla.blit(surf, surf.get_rect(midleft=(self.rect_input.x + 12, self.rect_input.centery)))

    def _draw_robot(self, pantalla):
        cx = COACH_X + COACH_W // 2
        cy = COACH_Y
        
        pygame.draw.line(pantalla, (200, 200, 200), (cx, cy), (cx, cy - 15), 3)
        pygame.draw.circle(pantalla, (255, 100, 100), (cx, cy - 18), 5)
        
        rect_cabeza = pygame.Rect(cx - 25, cy, 50, 40)
        pygame.draw.rect(pantalla, (100, 160, 220), rect_cabeza, border_radius=10)
        pygame.draw.rect(pantalla, (255, 255, 255), rect_cabeza, 2, border_radius=10)
        
        pygame.draw.rect(pantalla, (80, 130, 180), (cx - 32, cy + 10, 7, 15), border_radius=3)
        pygame.draw.rect(pantalla, (80, 130, 180), (cx + 25, cy + 10, 7, 15), border_radius=3)
        
        pygame.draw.circle(pantalla, (40, 40, 40), (cx - 10, cy + 15), 6)
        pygame.draw.circle(pantalla, (40, 40, 40), (cx + 10, cy + 15), 6)
        pygame.draw.circle(pantalla, (255, 255, 255), (cx - 11, cy + 14), 2)
        pygame.draw.circle(pantalla, (255, 255, 255), (cx + 9, cy + 14), 2)
        
        pygame.draw.arc(pantalla, (40, 40, 40), (cx - 10, cy + 20, 20, 12), 3.14, 0, 2)

    def _draw_coach_panel(self, pantalla):
        try:
            self._draw_robot(pantalla)

            bubble_y = COACH_Y + 55
            bubble_rect = pygame.Rect(COACH_X, bubble_y, COACH_W, COACH_H)
            pygame.draw.rect(pantalla, (45, 45, 60), bubble_rect, border_radius=15)
            pygame.draw.rect(pantalla, config.PRIMARIO, bubble_rect, 2, border_radius=15)

            pygame.draw.polygon(pantalla, config.PRIMARIO, [
                (COACH_X + COACH_W // 2 - 10, bubble_y),
                (COACH_X + COACH_W // 2 + 10, bubble_y),
                (COACH_X + COACH_W // 2, bubble_y - 15)
            ])
            pygame.draw.polygon(pantalla, (45, 45, 60), [
                (COACH_X + COACH_W // 2 - 8, bubble_y),
                (COACH_X + COACH_W // 2 + 8, bubble_y),
                (COACH_X + COACH_W // 2, bubble_y - 10)
            ])

            texto_coach = self.coach.ultimo_consejo
            if not texto_coach:
                texto_coach = "¡Hola! Soy tu entrenador. Haz una jugada o pídeme una pista."
            
            lineas = []
            for parrafo in texto_coach.split('\n'):
                palabras = parrafo.split()
                linea_actual = ""
                for p in palabras:
                    if self.fuente_coach.size(linea_actual + " " + p)[0] < bubble_rect.width - 20:
                        linea_actual += " " + p
                    else:
                        lineas.append(linea_actual)
                        linea_actual = p
                lineas.append(linea_actual)

            for i, linea in enumerate(lineas[:22]):
                surf = self.fuente_coach.render(linea, True, config.TEXTO)
                pantalla.blit(surf, (bubble_rect.x + 10, bubble_rect.y + 15 + i * 20))
        except Exception as e:
            print(f"Error dibujando coach: {e}")

    def draw(self, pantalla):
        if self.coach.nuevo_audio:
            try:
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                sonido_voz = pygame.mixer.Sound(self.coach.archivo_audio)
                sonido_voz.play()
                self.coach.nuevo_audio = False
            except Exception as e:
                print(f"Error al reproducir audio: {e}")
                self.coach.nuevo_audio = False

        if self.board.is_checkmate(): estado = "Jaque mate"
        elif self.board.is_stalemate(): estado = "Tablas (ahogado)"
        elif self.board.is_insufficient_material(): estado = "Tablas (material insuficiente)"
        elif self.board.is_check(): estado = "Jaque"
        else: estado = "Blancas" if self.board.turn == chess.WHITE else "Negras"

        info = self.fuente_info.render(f"Turno: {estado}", True, config.TEXTO)
        pantalla.blit(info, (TABLERO_X, 30))

        contador = self.fuente_info.render(f"Pistas: {self.pistas_usadas}", True, (255, 200, 0))
        pantalla.blit(contador, (TABLERO_X + 8 * TAM_CASILLA - contador.get_width(), 30))

        if self.modo_coordenadas:
            modo_txt_str = "Modo coordenadas - 2 jugadores"
        else:
            modo = self.app.config.get("modo", "cooperativo")
            color_humano = self.app.config.get("color_humano", "blancas")
            modo_txt_str = f"{modo} - tu: {color_humano}"
        modo_txt = self.fuente_info.render(modo_txt_str, True, config.TEXTO)
        pantalla.blit(modo_txt, (TABLERO_X, 55))

        if self.pensando:
            pen = self.fuente_info.render("Stockfish pensando...", True, (255, 200, 0))
            pantalla.blit(pen, (TABLERO_X + 8 * TAM_CASILLA // 2 - pen.get_width() // 2, 55))

        for fila in range(8):
            for col in range(8):
                x = TABLERO_X + col * TAM_CASILLA
                y = TABLERO_Y + fila * TAM_CASILLA
                color = config.COLOR_CLARO if (fila + col) % 2 == 0 else config.COLOR_OSCURO
                pygame.draw.rect(pantalla, color, (x, y, TAM_CASILLA, TAM_CASILLA))
                
                if self.seleccion == (fila, col):
                    pygame.draw.rect(pantalla, config.COLOR_SELECCION, (x, y, TAM_CASILLA, TAM_CASILLA))
                
                square = self._square_desde_fila_col(fila, col)
                pieza = self.board.piece_at(square)
                if pieza:
                    letra = PIEZAS_UNICODE[pieza.symbol()]
                    color_pieza = (255, 255, 255) if pieza.color == chess.WHITE else (0, 0, 0)
                    texto = self.fuente_pieza.render(letra, True, color_pieza)
                    pantalla.blit(texto, texto.get_rect(center=(x + TAM_CASILLA // 2, y + TAM_CASILLA // 2)))

        if self.pista_mov:
            origen = self.pista_mov.from_square
            destino = self.pista_mov.to_square
            for sq in [origen, destino]:
                col = chess.square_file(sq)
                fila = 7 - chess.square_rank(sq)
                x = TABLERO_X + col * TAM_CASILLA
                y = TABLERO_Y + fila * TAM_CASILLA
                pygame.draw.rect(pantalla, (50, 150, 255), (x, y, TAM_CASILLA, TAM_CASILLA), 4)

        self._draw_coordenadas(pantalla)
        
        if self.modo_coordenadas:
            self._draw_input(pantalla)
            if self.error_timer > 0: self.error_timer -= 1

        if self.mostrar_coach:
            self._draw_coach_panel(pantalla)

        self.boton_volver.draw(pantalla)
        
        # Solo dibujar el botón de pista si está visible
        if self.mostrar_pista:
            self.boton_pista.draw(pantalla)
