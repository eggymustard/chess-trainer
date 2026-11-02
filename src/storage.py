import json
import os
from pathlib import Path
from . import config


def _config_dir():
    base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(base) / "chess-trainer"


def _config_path():
    return _config_dir() / "config.json"


def cargar_config():
    """Devuelve la config guardada mezclada con los valores por defecto."""
    cfg = dict(config.CONFIG_DEFAULT)
    path = _config_path()
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                guardado = json.load(f)
            for clave, valor in guardado.items():
                if clave in cfg:
                    cfg[clave] = valor
        except Exception as e:
            print(f"No se pudo leer la config: {e}")
    return cfg


def guardar_config(cfg):
    """Guarda la config en ~/.config/chess-trainer/config.json"""
    path = _config_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"No se pudo guardar la config: {e}")
