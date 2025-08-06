#!/bin/bash

# Nastavenie pre Nuitka kompiláciu
BASE_DIR=$(pwd)

# Skladovanie výstupov
OUTPUT_DIR="$BASE_DIR/Build"

# Zadefinuj súbory a zložky, ktoré je potrebné zahrnúť
CONFIG_FILE="$BASE_DIR/Modules/Singleplayer/SaveItems/v32/config.json"
LOG_FILE="$BASE_DIR/log.txt"
DATA_FILE="$BASE_DIR/data.ini"
ASSETS_DIR="$BASE_DIR/GUI/Assets"
CPRINT_CONFIG="$BASE_DIR/CustomTools/CPrint/cprint.ini"
ICON_PNG="$BASE_DIR/GUI/Assets/Icon/icon.png"  # Ikona pre Linux (.png)
ICON_ICO="$BASE_DIR/GUI/Assets/Icon/icon.ico"  # Ikona pre Windows (.ico)

# Vytvorenie adresárov pre výstupy ak neexistujú
mkdir -p "$OUTPUT_DIR/linux"
mkdir -p "$OUTPUT_DIR/windows"

# Kompilácia cez Nuitka pre Linux
nuitka \
  --standalone \
  --enable-plugin=pyside6 \
  --include-qt-plugins=platforms \
  --noinclude-qt-plugin=svg \
  --noinclude-qt-plugin=pdf \
  --noinclude-qt-plugin=printsupport \
  --noinclude-qt-plugin=dbus \
  --noinclude-qt-plugin=wayland \
  --noinclude-qt-translations \
  --nofollow-import-to=tkinter,unittest,tests \
  --noinclude-unittest-mode=error \
  --lto=yes \
  --clang \
  --show-modules \
  --remove-output \
  --output-dir="$OUTPUT_DIR/linux" \
  --output-filename="scum_linux.bin" \
  --include-data-dir="$ASSETS_DIR=GUI/Assets" \
  --include-data-file="$CONFIG_FILE=Modules/Singleplayer/SaveItems/v32/config.json" \
  --include-data-file="$LOG_FILE=log.txt" \
  --include-data-file="$DATA_FILE=data.ini" \
  --include-data-file="$CPRINT_CONFIG=CustomTools/CPrint/cprint.ini" \
  "$BASE_DIR/scum.py"


echo "✅ Linux kompilácia dokončená! Výstupy sú v adresári: $OUTPUT_DIR/linux"

# Kompilácia cez Nuitka pre Windows s pridanou ikonou
nuitka \
  --standalone \
  --enable-plugin=pyside6 \
  --include-qt-plugins=platforms,imageformats \
  --include-data-dir="$ASSETS_DIR=GUI/Assets" \
  --include-data-file="$CONFIG_FILE=Modules/Singleplayer/SaveItems/v32/config.json" \
  --include-data-file="$LOG_FILE=log.txt" \
  --include-data-file="$DATA_FILE=data.ini" \
  --include-data-file="$CPRINT_CONFIG=CustomTools/CPrint/cprint.ini" \
  --windows-icon-from-ico="$ICON_ICO" \
  --output-dir="$OUTPUT_DIR/windows" \
  --output-filename="scum_windows.exe" \
  "$BASE_DIR/scum.py"

echo "✅ Windows kompilácia dokončená! Výstupy sú v adresári: $OUTPUT_DIR/windows"

