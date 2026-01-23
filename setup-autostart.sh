#!/bin/bash

# MeTIMat Autostart Setup Script
# This script configures the Raspberry Pi to start the firmware on login.

APP_DIR="$HOME/MeTIMat-Firmware"
AUTOSTART_DIR="$HOME/.config/autostart"
DESKTOP_FILE="$AUTOSTART_DIR/metimat.desktop"

echo "🚀 Setting up MeTIMat Autostart..."

# 1. Ensure the directory exists
if [ ! -d "$AUTOSTART_DIR" ]; then
    echo "📁 Creating autostart directory..."
    mkdir -p "$AUTOSTART_DIR"
fi

# 2. Create the .desktop file
echo "📝 Creating desktop entry at $DESKTOP_FILE"

cat <<EOF > "$DESKTOP_FILE"
[Desktop Entry]
Type=Application
Name=MeTIMat Machine Interface
Exec=$APP_DIR/run.sh
WorkingDirectory=$APP_DIR
StandardOutput=append:$HOME/metimat_stdout.log
StandardError=append:$HOME/metimat_stderr.log
Restart=always
EOF

# 3. Ensure run.sh is executable
if [ -f "$APP_DIR/run.sh" ]; then
    chmod +x "$APP_DIR/run.sh"
    echo "✅ run.sh marked as executable."
else
    echo "⚠️ Warning: $APP_DIR/run.sh not found! Please ensure the app is in the correct folder."
fi

# 4. Disable Screen Blanking (Optional but recommended for Kiosks)
echo "💡 Disabling screen blanking..."
if ! grep -q "xset s off" "$HOME/.xsessionrc" 2>/dev/null; then
    echo "xset s off" >> "$HOME/.xsessionrc"
    echo "xset -dpms" >> "$HOME/.xsessionrc"
    echo "xset s noblank" >> "$HOME/.xsessionrc"
fi

echo "✨ Done! The MeTIMat app will now start automatically upon login."
echo "🔄 Please reboot or log out/in to test."
