with open("README.md", "r") as f:
    text = f.read()

# Add windowrule instructions
new_rule = """
## Hyprland Window Rule (Fullscreen)

Since MadSnake launches inside your default terminal, you need to tell Hyprland to automatically make it fullscreen.
Add this window rule to your `~/.config/hypr/hyprland.conf`:

```ini
windowrulev2 = fullscreen, title:(madsnake)
```
*(Make sure your terminal sets its window title to the executed binary name, which most terminals do).*

"""

# Insert before ## Hypridle Integration
idx = text.find("## Hypridle Integration")
text = text[:idx] + new_rule + text[idx:]

with open("README.md", "w") as f:
    f.write(text)
