#!/bin/bash

# Pfad zur App - BITTE PRÜFEN ob dieser Ordner existiert!
APP_DIR="$HOME/MeTIMat-Firmware"
AUTOSTART_DIR="$HOME/.config/autostart"
DESKTOP_FILE="$AUTOSTART_DIR/metimat.desktop"

echo "🚀 MeTIMat Autostart Setup für Raspberry Pi OS..."

# 1. Verzeichnis erstellen
mkdir -p "$AUTOSTART_DIR"

# 2. .desktop Datei erstellen
# Wir fügen ein 'sleep 5' ein, um sicherzustellen, dass der Desktop/Grafiktreiber bereit ist
cat <<EOF > "$DESKTOP_FILE"
[Desktop Entry]
Type=Application
Name=MeTIMat
Exec=bash -c "sleep 5 && cd $APP_DIR && ./run.sh > $HOME/metimat.log 2>&1"
Terminal=false
X-GNOME-Autostart-enabled=true
EOF

# 3. Berechtigungen setzen
chmod +x "$DESKTOP_FILE"
if [ -d "$APP_DIR" ]; then
    chmod +x "$APP_DIR/run.sh" 2>/dev/null
    echo "✅ Berechtigungen für run.sh gesetzt."
else
    echo "⚠️  HINWEIS: Ordner $APP_DIR wurde nicht gefunden. Verschiebe deine Dateien dorthin!"
fi

# 4. Bildschirmschoner deaktivieren (für X11 Umgebungen)
XWRAPPER="$HOME/.xsessionrc"
if ! grep -q "xset" "$XWRAPPER" 2>/dev/null; then
    echo "xset s off -dpms s noblank" >> "$XWRAPPER"
    echo "✅ Bildschirmschoner-Deaktivierung zu .xsessionrc hinzugefügt."
fi

# 5. Wayland/Bookworm Spezifikum (Energiesparen via gsettings)
if command -v gsettings >/dev/null 2>&1; then
    gsettings set org.gnome.desktop.session idle-delay 0 2>/dev/null
    echo "✅ Wayland Idle-Delay auf 0 gesetzt."
fi

echo "✨ Setup abgeschlossen! Nach einem Neustart sollte die App erscheinen."
