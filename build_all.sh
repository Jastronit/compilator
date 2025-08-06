#!/bin/bash

set -e  # skonči akákoľvek chyba

ASSETS_DIR="$(pwd)/GUI/Assets"
LINUX_OUTPUT="dist_linux"
WINDOWS_OUTPUT="dist_windows"
MAIN_FILE="$(pwd)/Bin/scum.py"

# Zisti cestu k platform plugins cez Python (kompatibilné s venv aj systémovou inštaláciou)
QT_PLUGIN_SRC=$(python3 -c "import PySide6; import os; print(os.path.join(os.path.dirname(PySide6.__file__), 'Qt', 'plugins', 'platforms'))")

if [ ! -d "$QT_PLUGIN_SRC" ]; then
  echo "❌ Chyba: qt_plugins/platforms neboli nájdené na $QT_PLUGIN_SRC"
  exit 1
fi

# Overenie existencie hlavných súborov
if [ ! -f "$MAIN_FILE" ]; then
  echo "❌ Chyba: hlavný súbor $MAIN_FILE neexistuje"
  exit 1
fi

if [ ! -d "$ASSETS_DIR" ]; then
  echo "❌ Chyba: adresár Assets neexistuje na $ASSETS_DIR"
  exit 1
fi

echo "🔍 Kompilujem: $MAIN_FILE"
echo "📁 Assets: $ASSETS_DIR"
echo "🔌 Qt plugins: $QT_PLUGIN_SRC"

echo "🔧 Kompilujem pre Linux..."
nuitka \
  --standalone \
  --include-module=sqlite3 \
  --plugin-enable=pyside6 \
  --include-plugin-directory="$(pwd)/CustomTools" \
  --include-plugin-directory="$(pwd)/GUI" \
  --include-plugin-directory="$(pwd)/Logic" \
  --include-data-dir="$ASSETS_DIR=Assets" \
  --include-data-dir="$QT_PLUGIN_SRC=qt_plugins/platforms" \
  --remove-output \
  --output-dir="$LINUX_OUTPUT" \
  --output-filename="scum_qol_linux" \
  "$MAIN_FILE"

echo "🔧 Kompilujem pre Windows..."
nuitka \
  --standalone \
  --include-module=sqlite3 \
  --plugin-enable=pyside6 \
  --include-plugin-directory="$(pwd)/CustomTools" \
  --include-plugin-directory="$(pwd)/GUI" \
  --include-plugin-directory="$(pwd)/Logic" \
  --include-data-dir="$ASSETS_DIR=Assets" \
  --include-data-dir="$QT_PLUGIN_SRC=qt_plugins/platforms" \
  --remove-output \
  --mingw64 \
  --windows-disable-console \
  --output-dir="$WINDOWS_OUTPUT" \
  --output-filename="scum_qol_windows.exe" \
  "$MAIN_FILE"

echo ""
echo "✅ Hotovo. Výstupy sú v adresároch: $LINUX_OUTPUT  a  $WINDOWS_OUTPUT"

