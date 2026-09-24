#!/bin/bash

# MadSnake Installer

echo "Building MadSnake..."
cmake -B build
cmake --build build

echo "Installing to /usr/local/bin (requires sudo)..."
sudo cp build/madsnake /usr/local/bin/madsnake-bin
sudo cp madsnake.sh /usr/local/bin/madsnake
sudo chmod +x /usr/local/bin/madsnake-bin /usr/local/bin/madsnake

echo "Setting up default config for user..."
CONFIG_DIR="$HOME/.config/madsnake"
mkdir -p "$CONFIG_DIR"

if [ ! -f "$CONFIG_DIR/config" ]; then
cat << 'CFG' > "$CONFIG_DIR/config"
dim_brightness=15%
speed_ms=120
default_length=5
max_length=20
CFG
    echo "Created default config at $CONFIG_DIR/config"
else
    echo "Config already exists at $CONFIG_DIR/config"
fi

echo "Installation complete!"
echo "Run 'madsnake' to launch the screensaver."
