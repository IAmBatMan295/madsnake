with open("madsnake.sh", "r") as f:
    text = f.read()

# Replace the foot command with terminal-agnostic launch
old_launch = 'foot -a madsnake -o colors.background=000000 -F -f "monospace:size=4" -e "$BIN_PATH"'

new_launch = """
# Try to find the user's default terminal
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
elif command -v konsole >/dev/null; then
    TERM_CMD="konsole"
elif command -v gnome-terminal >/dev/null; then
    TERM_CMD="gnome-terminal"
else
    TERM_CMD="xterm"
fi

# Launch the screensaver inside the terminal
# Most terminals support the -e flag to execute a binary
"$TERM_CMD" -e "$BIN_PATH"
"""

text = text.replace(old_launch, new_launch)

with open("madsnake.sh", "w") as f:
    f.write(text)
