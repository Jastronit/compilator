#//////////////////////////////////////////////////////////////////////////////////////////////
#////---- DEFAULT SETTINGS ----
#//////////////////////////////////////////////////////////////////////////////////////////////

#////---- IMPORT ----//////////////////////////////////////////////////////////////////////////
import configparser
import sys
import os

#////---- BASE DIR ----////////////////////////////////////////////////////////////////////////
if getattr(sys, 'frozen', False):
    # Binárka (Nuitka alebo PyInstaller)
    base_dir = os.path.dirname(sys.executable)
    config_path = os.path.join(base_dir, "cprint.ini")
else:
    # Normálne .py spúšťanie base dir o dve zložky nad
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    this_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(this_dir, "cprint.ini")

#////---- cprint.ini ----//////////////////////////////////////////////////////////////////////
DEFAULT_CONFIG = {
    "cprint": {
        "debug": "true",
        "info": "true",
        "warning": "true",
        "error": "true",
        "loading": "true"
    }
}
# Načíta alebo vytvorí config.ini
config = configparser.ConfigParser()

if not os.path.exists(config_path):
    config.read_dict(DEFAULT_CONFIG)
    with open(config_path, "w") as configfile:
        config.write(configfile)
else:
    try:
        config.read(config_path)
    except configparser.Error as e:
        print(f"[CPRINT] Chyba pri čítaní cprint.ini: {e}")
        config.read_dict(DEFAULT_CONFIG)

#////---- COLORS ----//////////////////////////////////////////////////////////////////////////
# ANSI reset
RESET = "\033[0m"

# Farby pre úrovne
LEVEL_COLORS = {
    "debug": "\033[38;2;127;127;127m",
    "info": "\033[38;2;255;255;0m",
    "warning": "\033[38;2;255;165;0m",
    "error": "\033[38;2;255;50;50m",
    "loading": "\033[38;2;20;255;20m"
}

def _hex_to_ansi(hex_color: str, background=False) -> str:
    try:
        hex_color = hex_color.lstrip("#")
        if len(hex_color) != 6:
            raise ValueError("HEX musí mať 6 znakov")
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except ValueError as e:
        print(f"[CPRINT] Neplatný HEX kód: '{hex_color}' ({e})")
        return ""
    prefix = "48" if background else "38"
    return f"\033[{prefix};2;{r};{g};{b}m"

#//////////////////////////////////////////////////////////////////////////////////////////////
#////---- MAIN LOGIC ----
#//////////////////////////////////////////////////////////////////////////////////////////////

#////---- def console ----/////////////////////////////////////////////////////////////////////
def console(level, text, textColor="#FFFFFF", backgroundColor=None, highlight=None, **kwargs):
    level = level.lower()

    if not config.getboolean("cprint", level, fallback=False):
        return

    highlight = highlight or {}

    # Farby
    level_color = LEVEL_COLORS.get(level, "")
    text_color = _hex_to_ansi(textColor)

    # Pozadie použijeme iba ak bolo zadané
    bg_color = _hex_to_ansi(backgroundColor, background=True) if backgroundColor else ""

    # Príprava hodnot: farbíme hodnoty podľa highlight
    colored_kwargs = {}
    for key, value in kwargs.items():
        if key in highlight:
            color = _hex_to_ansi(highlight[key])
            colored_kwargs[key] = f"{color}{value}{RESET}{bg_color}{text_color}"
        else:
            colored_kwargs[key] = f"{value}"

    # Formátovanie
    formatted_text = text.format(**colored_kwargs)

    # Výsledný výstup
    full_output = f"{bg_color}{level_color}[{level.upper():<7}] {text_color}{formatted_text}{RESET}"
    print(full_output)

#//// test
console("info", "Spúšťam test cprint...",backgroundColor='#FF8000')
console("debug", "\033[38;2;255;32;32mdef \033[38;2;255;127;0mfunkcia\033[0m(hodnota={val})", val=123, highlight={"val": "#00FFFF"})
console("info", "Info správa.")
console("warning", "Toto je len test warningu\033[38;2;255;32;32m! zmena farby cez ANSI bez resetu")
console("error", "Chyba: {msg}", msg="Niečo sa pokazilo cez highlight", highlight={"msg": "#FF0000"})
console("loading", "Zvýraznenie hodnoty x = {x}", x=64, highlight={"x": "#FF8000"})
console("x", "toto nezobrazí")
console("info", "Koniec testu.",backgroundColor='#FF8000')

