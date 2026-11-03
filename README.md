Chess Trainer
----------------------------------------------------------------------------------

Un entrenador de ajedrez completo y gratuito que corre 100% en tu computadora. No requiere conexión a internet, no usa APIs de pago y respeta tu privacidad.

Características
----------------------------------------------------------------------------------
- Motor de ajedrez: Stockfish (dificultad ajustable).

- Coach IA: Qwen 2.5 (3B) ejecutado localmente con Ollama.

- Voz: Piper TTS (voz en español de alta calidad).

- Música y sonidos: Ambiente relajante y efectos al mover piezas.

- Interfaz: Pygame con tablero interactivo, coordenadas y pistas visuales.

Instalación (Linux)
----------------------------------------------------------------------------------

- Ve a la sección Releases y descarga las 3 partes del juego.

- Únelas con el comando cat (está explicado en la descripción del Release).

- Descomprime el ZIP.

- Abre una terminal en la carpeta descomprimida y da permisos de ejecución con: chmod +x iniciar.sh bin/*

  
- Ejecuta el juego con : ./iniciar.sh

  
---------------------------------------------------------------------------------
Requisitos del sistema
----------------------------------------------------------------------------------

- Linux (probado en Arch Linux / CachyOS).

- Python 3.10+ con pygame, chess y requests.

- ffmpeg instalado (para el audio del coach).


----------------------------------------------------------------------------------
Cómo jugar
----------------------------------------------------------------------------------

- Cooperativo local: Dos jugadores en el mismo teclado/ratón.

- Jugar con teclado: Introduce coordenadas (ej. e2e4).

- Juega vs Entrenador: Juega contra Stockfish y recibe consejos del Coach IA.

Sobre este proyecto
----------------------------------------------------------------------------------
Este es mi primer proyecto de desarrollo. Lo empecé con la idea de crear un entrenador de ajedrez gratuito, local y que no dependiera de servicios en la nube. A lo largo del camino conté con el apoyo de DeepSeek como asistente de programación, ya que aún no soy tan experimentado, me ayudó a resolver dudas, estructurar el código y reparar algunos errores.


**Si tienes algún consejo o mejora, escribeme a mi mail:**
kraushbailey@gmail.com
