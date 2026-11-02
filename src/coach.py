import requests
import threading
import subprocess
import os
import pygame
import random  # <-- Importante para elegir motivos al azar

class Coach:
    def __init__(self, url="http://localhost:11434", modelo="qwen2.5:3b"):
        self.url = url
        self.modelo = modelo
        self.ultimo_consejo = ""
        self.pensando = False
        self.modelo_voz = "assets/models/piper/es_MX-claude-high.onnx"
        self.archivo_audio = "coach_voice.wav"
        self.piper_bin = "bin/piper_bin"
        self.nuevo_audio = False

        # Lista de motivos variados para que Python elija al azar
        self.motivos = [
            "desarrolla una pieza",
            "protege al rey",
            "ataca una pieza enemiga",
            "defiende una pieza propia",
            "crea una amenaza",
            "prepara un ataque",
            "gana espacio",
            "mejora la posición de la pieza",
            "obliga al rival a retroceder",
            "controla una casilla clave",
            "abre líneas para las piezas",
        ]

    def pedir_consejo(self, contexto, tipo="feedback", jugada_san="", mejor_san="", es_mejor=False):
        if self.pensando:
            return
        
        self.pensando = True
        self.nuevo_audio = False
        
        # Si es feedback, NO usamos el LLM. Lo hacemos todo en Python al instante.
        if tipo == "feedback":
            motivo = random.choice(self.motivos)
            if es_mejor:
                self.ultimo_consejo = f"¡Excelente! {jugada_san} es la mejor porque {motivo}."
            else:
                self.ultimo_consejo = f"{jugada_san} no es la mejor. {mejor_san} era mejor porque {motivo}."
            
            self._generar_audio(self.ultimo_consejo)
            self.pensando = False
            return

        # Si es pista, sí usamos el LLM para que dé una respuesta variada
        self.ultimo_consejo = "Pensando..."
        
        def _worker():
            prompt = (
                "Eres un entrenador de ajedrez conciso y directo. "
                f"{contexto}\n"
                "Instrucción: Responde ÚNICAMENTE con esta estructura exacta, sin añadir nada más:\n"
                "La mejor jugada es [nombre de la jugada]."
            )

            try:
                respuesta = requests.post(
                    f"{self.url}/api/generate",
                    json={
                        "model": self.modelo,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.0, "num_predict": 20}
                    },
                    timeout=15
                )
                if respuesta.status_code == 200:
                    texto = respuesta.json().get("response", "").strip()
                    texto = texto.replace("*", "").replace("#", "").replace("`", "")
                    self.ultimo_consejo = texto
                    self._generar_audio(texto)
                else:
                    self.ultimo_consejo = "Hubo un error."
            except Exception as e:
                print(f"Error en Coach: {e}")
                self.ultimo_consejo = "Mi cerebro no está disponible."
            finally:
                self.pensando = False

        hilo = threading.Thread(target=_worker)
        hilo.daemon = True
        hilo.start()

    def _generar_audio(self, texto):
        try:
            env = os.environ.copy()
            env["LD_LIBRARY_PATH"] = os.path.abspath("bin")
            
            if not os.path.exists(self.modelo_voz):
                print(f"DEBUG: ¡El modelo de voz NO existe en {self.modelo_voz}!")
                return

            subprocess.run(
                [self.piper_bin, "--model", self.modelo_voz, "--length_scale", "1.1", "--noise_scale", "0.7", "--output_file", self.archivo_audio],
                input=texto.encode("utf-8"), check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env
            )
            
            temp_wav = "coach_voice_padded.wav"
            subprocess.run(
                ["ffmpeg", "-y", "-i", self.archivo_audio, "-af", "adelay=200:all=1", temp_wav],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            os.replace(temp_wav, self.archivo_audio)
            self.nuevo_audio = True
        except Exception as e:
            print(f"Error al generar audio: {e}")
