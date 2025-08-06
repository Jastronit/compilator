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

# Vytvorenie adresára pre výstupy ak neexistuje
mkdir -p "$OUTPUT_DIR"

# Kompilácia cez Nuitka s PySide6
nuitka \
  --standalone \
  --enable-plugin=pyside6 \
  --include-qt-plugins=platforms,imageformats \
  --include-data-dir="$ASSETS_DIR=GUI/Assets" \
  --include-data-file="$CONFIG_FILE=Modules/Singleplayer/SaveItems/v32/config.json" \
  --include-data-file="$LOG_FILE=log.txt" \
  --include-data-file="$DATA_FILE=data.ini" \
  --include-data-file="$CPRINT_CONFIG=CustomTools/CPrint/cprint.ini" \
  --output-dir="$OUTPUT_DIR" \
  --output-filename="scum.bin" \
  "$BASE_DIR/scum.py"  # Upravená cesta ku scum.py (už v hlavnej zložke)

echo "✅ Kompilácia dokončená! Výstupy sú v adresári: $OUTPUT_DIR"

