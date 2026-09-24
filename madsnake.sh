#!/bin/bash
# MadSnake Launcher

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
CONFIG_FILE="$HOME/.config/madsnake/config"

# Do not trigger if the laptop lid is closed
if grep -iq closed /proc/acpi/button/lid/*/state 2>/dev/null; then
    exit 0
fi


dim_brightness="10%"

if [ -f "$CONFIG_FILE" ]; then
    while IFS='=' read -r key val; do
        if [ "$key" == "dim_brightness" ]; then
            dim_brightness="$val"
        fi
    done < "$CONFIG_FILE"
fi

# Ensure brightness is restored even if script is killed (Ctrl+C)
if command -v brightnessctl >/dev/null 2>&1; then
    ORIG_BRIGHTNESS=$(brightnessctl get)
    trap 'brightnessctl set "$ORIG_BRIGHTNESS" -q' EXIT INT TERM
    brightnessctl set "$dim_brightness" -q
fi

if [ -x "$SCRIPT_DIR/build/madsnake" ]; then
    BIN_PATH="$SCRIPT_DIR/build/madsnake"
else
    BIN_PATH="madsnake-bin"
fi

# Find terminal
if [ -n "$TERMINAL" ]; then
    TERM_CMD="$TERMINAL"
elif command -v kitty >/dev/null; then
    TERM_CMD="kitty"
elif command -v alacritty >/dev/null; then
    TERM_CMD="alacritty"
elif command -v foot >/dev/null; then
    TERM_CMD="foot"
elif command -v wezterm >/dev/null; then
    TERM_CMD="wezterm"
elif command -v ghostty >/dev/null; then
    TERM_CMD="ghostty"
else
    TERM_CMD="xterm"
fi

# Launch with specific configurations for tiny font and fullscreen
case "$TERM_CMD" in
    *foot*)
        foot -a madsnake -F -f "monospace:size=4" -e "$BIN_PATH" 2>/dev/null
        ;;
    *kitty*)
        # kitty requires --single-instance to not background sometimes, but we want it to block.
        # Actually kitty blocks by default unless detached.
        kitty --class madsnake --start-as=fullscreen -o font_size=4 -o background=#000000 "$BIN_PATH" 2>/dev/null
        ;;
    *alacritty*)
        # alacritty blocks by default.
        alacritty --class madsnake -o "window.startup_mode='Fullscreen'" -o "font.size=4" -o "colors.primary.background='#000000'" -e "$BIN_PATH" 2>/dev/null
        ;;
    *wezterm*)
        # wezterm start blocks
        wezterm start --class madsnake --always-new-process --config font_size=4 -- "$BIN_PATH" 2>/dev/null 
        ;;
    *ghostty*)
        # ghostty cli
        ghostty --class=madsnake --font-size=4 --background=000000 --window-state=fullscreen -e "$BIN_PATH" 2>/dev/null
        ;;
    *)
        # Fallback for unknown terminals
        "$TERM_CMD" -e "$BIN_PATH"
        ;;
esac
