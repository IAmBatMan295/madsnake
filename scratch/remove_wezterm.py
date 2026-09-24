import re

with open("madsnake.sh", "r") as f:
    text = f.read()

# Remove elif command -v wezterm...
text = re.sub(r'elif command -v wezterm >/dev/null; then\n\s*TERM_CMD="wezterm"\n', '', text)

# Remove *wezterm* case block
text = re.sub(r'\s*\*wezterm\*\)\n\s*# wezterm start blocks\n\s*wezterm --config font_size=4 start --class madsnake --always-new-process -- "\$BIN_PATH" 2>/dev/null \s*;;\n', '\n', text)

with open("madsnake.sh", "w") as f:
    f.write(text)

with open("README.md", "r") as f:
    readme = f.read()

readme = readme.replace("WezTerm, ", "")

with open("README.md", "w") as f:
    f.write(readme)
