with open("README.md", "r") as f:
    text = f.read()

# Update dependencies
text = text.replace(
    "- `foot`: Fast Wayland terminal emulator (used for high-res font scaling).",
    "- A modern terminal emulator (e.g., Kitty, Alacritty, Foot, WezTerm, Ghostty, etc.)"
)

# Update default behavior
text = text.replace(
    "- Launch `foot` in fullscreen mode on a pitch-black background with a tiny font size.",
    "- Detect your default terminal emulator and launch it in fullscreen mode with an absolute pitch-black background and a tiny font size for high-resolution graphics."
)

# Update Window Rule section
old_rule = """## Hyprland Window Rule (Fullscreen)

Since MadSnake launches inside your default terminal, you need to tell Hyprland to automatically make it fullscreen.
Add this window rule to your `~/.config/hypr/hyprland.conf`:

```ini
windowrulev2 = fullscreen, title:(madsnake)
```
*(Make sure your terminal sets its window title to the executed binary name, which most terminals do).*"""

new_rule = """## Hyprland Window Rule (Fullscreen Fallback)

The launcher script automatically passes native fullscreen arguments for modern terminals (Kitty, Alacritty, Foot, WezTerm, Ghostty). However, to guarantee the window is perfectly fullscreened regardless of the terminal you use, add this universal window rule to your `~/.config/hypr/hyprland.conf`:

```ini
windowrulev2 = fullscreen, title:(madsnake)
```"""

text = text.replace(old_rule, new_rule)

with open("README.md", "w") as f:
    f.write(text)
