with open("madsnake.sh", "r") as f:
    text = f.read()

# Replace terminal launch commands with 2>/dev/null
text = text.replace(
    'foot -a madsnake -F -f "monospace:size=4" -e "$BIN_PATH"',
    'foot -a madsnake -F -f "monospace:size=4" -e "$BIN_PATH" 2>/dev/null'
)

text = text.replace(
    'kitty --class madsnake --start-as=fullscreen -o font_size=4 -o background=#000000 "$BIN_PATH"',
    'kitty --class madsnake --start-as=fullscreen -o font_size=4 -o background=#000000 "$BIN_PATH" 2>/dev/null'
)

text = text.replace(
    'alacritty --class madsnake -o "window.startup_mode=\'Fullscreen\'" -o "font.size=4" -o "colors.primary.background=\'#000000\'" -e "$BIN_PATH"',
    'alacritty --class madsnake -o "window.startup_mode=\'Fullscreen\'" -o "font.size=4" -o "colors.primary.background=\'#000000\'" -e "$BIN_PATH" 2>/dev/null'
)

text = text.replace(
    'wezterm start --class madsnake --always-new-process --config font_size=4 -- "$BIN_PATH"',
    'wezterm start --class madsnake --always-new-process --config font_size=4 -- "$BIN_PATH" 2>/dev/null'
)

text = text.replace(
    'ghostty --class=madsnake --font-size=4 --background=000000 --window-state=fullscreen -e "$BIN_PATH"',
    'ghostty --class=madsnake --font-size=4 --background=000000 --window-state=fullscreen -e "$BIN_PATH" 2>/dev/null'
)

with open("madsnake.sh", "w") as f:
    f.write(text)
