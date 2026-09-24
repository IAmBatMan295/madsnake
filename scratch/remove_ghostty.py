import re

with open("madsnake.sh", "r") as f:
    text = f.read()

# Remove elif command -v ghostty...
text = re.sub(r'elif command -v ghostty >/dev/null; then\n\s*TERM_CMD="ghostty"\n', '', text)

# Remove *ghostty* case block
text = re.sub(r'\s*\*ghostty\*\)\n\s*# ghostty cli\n\s*ghostty --class=madsnake --font-size=4 -e "\$BIN_PATH" 2>/dev/null\s*;;\n', '\n', text)

with open("madsnake.sh", "w") as f:
    f.write(text)

with open("README.md", "r") as f:
    readme = f.read()

readme = readme.replace("Ghostty, ", "").replace("Ghostty", "").replace(", etc.", " etc.")
readme = readme.replace("Foot,  etc.", "Foot, etc.")

with open("README.md", "w") as f:
    f.write(readme)
