#!/bin/bash

# MeTIMat Autostart Setup Script
# This script detects the current directory and sets up a reliable autostart.

# 1. Detect actual application directory
# Using the directory where this setup script is located as the source of truth
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
AUTOSTART_DIR="$HOME/.config/autostart"
DESKTOP_FILE="$AUTOSTART_DIR/metimat.desktop"
LOG_FILE="$HOME/metimat_autostart.log"

echo "🚀 Setting up MeTIMat Autostart..."
echo "📍 Detected App Directory: $SCRIPT_DIR"

# 2. Ensure autostart directory exists
mkdir -p "$AUTOSTART_DIR"

# 3. Create the .desktop file
# We use 'bash -c' to ensure environment variables like DISPLAY are available
# and to handle logging correctly. 'sleep 8' ensures the desktop environment
# and graphics drivers (especially on Pi 4/5) are fully initialized.
echo "📝 Creating desktop entry at $DESKTOP_FILE"

cat <<EOF > "$DESKTOP_FILE"
[Desktop Entry]
Type=Application
Name=MeTIMat Machine Interface
Comment=Starts MeTIMat Firmware on Boot
Exec=bash -c "sleep 8; cd $SCRIPT_DIR && ./run.sh >> $LOG_FILE 2>&1"
Terminal=false
X-GNOME-Autostart-enabled=true
Categories=Utility;
EOF

# 4. Make scripts executable
chmod +x "$DESKTOP_FILE"
chmod +x "$SCRIPT_DIR/run.sh"
echo "✅ Permissions updated."

# 5. Disable Screen Blanking / Power Management
# For X11 (Bullseye and older)
XWRAPPER="$HOME/.xsessionrc"
if ! grep -q "xset s off" "$XWRAPPER" 2>/dev/null; then
    {
        echo ""
        echo "# MeTIMat: Disable screensaver"
        echo "export DISPLAY=:0"
        echo "xset s off"
        echo "xset -dpms"
        echo "xset s noblank"
    } >> "$XWRAPPER"
    echo "✅ X11 Screen blanking disabled in .xsessionrc"
fi

# For Wayland (Bookworm/Pi 5)
if command -v gsettings >/dev/null 2>&1; then
    gsettings set org.gnome.desktop.session idle-delay 0 2>/dev/null
    gsettings set org.gnome.desktop.screensaver lock-enabled false 2>/dev/null
    echo "✅ Wayland Power Management disabled via gsettings"
fi

# 6. Verify run.sh content
if ! grep -q "export DISPLAY" "$SCRIPT_DIR/run.sh"; then
    echo "ℹ️  Tip: Ensure your run.sh contains 'export DISPLAY=:0' if the GUI fails to open."
fi

echo ""
echo "✨ Setup Complete!"
echo "🔄 Please REBOOT your Raspberry Pi now."
echo "📋 Logs will be written to: $LOG_FILE"
