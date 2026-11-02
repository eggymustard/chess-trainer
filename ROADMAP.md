# Roadmap — Chess Trainer

Proyecto de ajedrez open source con entrenador local y opcional.

## ✅ Hecho

- [x] Menú principal con navegación
- [x] Tablero con `python-chess` + Pygame
- [x] Coordenadas visibles (a-h, 1-8)
- [x] Movimiento de piezas con clics
- [x] Detección de jaque / jaque mate / tablas
- [x] Bot Stockfish (niveles de dificultad por Skill Level)
- [x] Elegir jugar con blancas o negras
- [x] Modo "Aprender casillas" (entrada por coordenadas)
- [x] Promoción automática a dama
- [x] Cierre limpio del motor Stockfish
- [x] Ajustes reales (dificultad, color, sonido) con persistencia en `~/.config/`
- [x] Sonidos (mover, capturar, jaque, jaque mate, enroque)

## 🚧 En progreso

- [ ] Coach / IA con voz y proveedores intercambiables

## 📅 Pendiente

### Coach / IA
- [ ] Capa de abstracción `src/coach/`
- [ ] Proveedor Qwen local vía Ollama
- [ ] Proveedor Groq API (gratuita)
- [ ] Proveedor Gemini API (opcional)
- [ ] Selector en Ajustes
- [ ] Prompt del coach: Stockfish evalúa + LLM explica
- [ ] Guardar API keys en `~/.config/chess-trainer/config.json`
- [ ] `.env.example`

### Voz
- [ ] Integración con Piper (TTS local)
- [ ] Fallback con `pyttsx3`
- [ ] Control de volumen y on/off en Ajustes

### Interfaz
- [ ] Resaltar movimientos legales
- [ ] Historial de jugadas (SAN)
- [ ] Deshacer / rehacer
- [ ] Diálogo de promoción visual
- [ ] Modo cooperativo local (2 humanos)
- [ ] Tamaño de ventana configurable

### Persistencia
- [ ] Guardar / cargar partida

### Calidad
- [ ] Tests con `pytest`
- [ ] README completo
- [ ] LICENSE
- [ ] Subida a GitHub
