#!/bin/bash

# MeTIMat Autostart Setup Script
# Configures the Raspberry Pi to start the firmware on login using the .desktop standard.

APP_DIR="$HOME/MeTIMat-Firmware"
AUTOSTART_DIR="$HOME/.config/autostart"
DESKTOP_FILE="$AUTOSTART_DIR/metimat.desktop"

echo "🚀 Setting up MeTIMat Autostart..."

# 1. Ensure the autostart directory exists
mkdir -p "$AUTOSTART_DIR"

# 2. Create the .desktop file with standard compliant fields
# Note: Standard desktop entries don't support 'Restart' or bash-style redirection directly.
# We wrap the call in a shell if logging is needed.
echo "📝 Creating desktop entry at $DESKTOP_FILE"

cat <<EOF > "$DESKTOP_FILE"
[Desktop Entry]
Type=Application
Name=MeTIMat Machine Interface
Comment=Starts the MeTIMat firmware on login
Exec=/bin/bash -c "cd $APP_DIR && ./run.sh > $HOME/metimat_stdout.log 2>&1"
Terminal=false
X-GNOME-Autostart-enabled=true
Categories=Utility;
EOF

# 3. Ensure run.sh and main scripts are executable
if [ -d "$APP_DIR" ]; then
    chmod +x "$APP_DIR/run.sh" 2>/dev/null
    echo "✅ Permissions updated for $APP_DIR/run.sh"
else
    echo "⚠️ Warning: $APP_DIR not found. Ensure your app is moved to ~/MeTIMat-Firmware"
fi

# 4. Prevent Screen Dimming / Screen Saver
# This is crucial for touch kiosks.
echo "💡 Configuring display for Kiosk mode (disabling screensaver)..."
XWRAPPER="$HOME/.xsessionrc"
touch "$XWRAPPER"

# Add xset commands if they aren't already there
if ! grep -q "xset s off" "$XWRAPPER"; then
    {
        echo ""
        echo "# MeTIMat: Disable screensaver and power management"
        echo "xset s off      # don't activate screensaver"
        echo "xset -dpms     # disable DPMS (Energy Star) features"
        echo "xset s noblank # don't blank the video device"
    } >> "$XWRAPPER"
fi

# 5. Fix for Raspberry Pi Wayland (Bookworm) vs X11
# If the Pi is using Wayland (default on Pi 5 / Bookworm), .desktop files in autostart
# are the right way, but xset won't work. The desktop file above covers both.

echo "✨ Setup complete!"
echo "🔄 Please reboot the system to verify the autostart."
echo "ℹ️  Logs can be found at: ~/metimat_stdout.log"
