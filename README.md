# MadSnake Screensaver

A highly optimized, ultra-lightweight terminal screensaver for Hyprland.

## Requirements (Dependencies)

- `hypridle`: For idle detection and triggering.
- A modern terminal emulator (e.g., Kitty, Alacritty, Foot, WezTerm, Ghostty, etc.)
- `brightnessctl`: For dimming screen brightness.
- `cmake` and `gcc`: For compiling.
- `ncurses`: C library for rendering.

## Installation

Run the provided installation script:

```bash
./install.sh
```

This will:
1. Compile the C binary.
2. Install the binary as `madsnake-bin` and the launcher script as `madsnake` into `/usr/local/bin`.
3. Create a default configuration file at `~/.config/madsnake/config`.

## Default Behavior

When launched, MadSnake will:
- Record your current absolute screen brightness.
- Dim the screen to the configured brightness (default 15%).
- Detect your default terminal emulator and launch it in fullscreen mode with an absolute pitch-black background and a tiny font size for high-resolution graphics.
- The snake will automatically move using AI pathfinding, eat food, and grow.
- When it reaches its maximum length, it instantly resets to its default length and picks a new color.
- Pressing any keyboard key or clicking any mouse button immediately exits the screensaver and restores your original screen brightness.
- The screensaver only consumes resources when active; it does not run silently in the background.

## Configuration

You can change the screensaver settings by editing `~/.config/madsnake/config`.

```ini
# The absolute screen brightness to set when the screensaver starts
dim_brightness=15%

# Movement speed (delay between frames in milliseconds)
speed_ms=120

# Starting length of the snake
default_length=5

# Maximum length the snake can reach before resetting to protect from OLED burn-in
max_length=20
```


## Hyprland Window Rule (Fullscreen Fallback)

The launcher script automatically passes native fullscreen arguments for modern terminals (Kitty, Alacritty, Foot, WezTerm, Ghostty). However, to guarantee the window is perfectly fullscreened regardless of the terminal you use, add this universal window rule to your `~/.config/hypr/hyprland.conf`:

```ini
windowrulev2 = fullscreen, title:(madsnake)
```

## Hypridle Integration

To automatically launch MadSnake after 30 seconds of inactivity, edit your `~/.config/hypr/hypridle.conf`:

```ini
general {
    lock_cmd = pidof madsnake || madsnake
    ignore_dbus_inhibit = false
}

listener {
    timeout = 30
    on-timeout = madsnake
}
```

Make sure `hypridle` runs automatically when Hyprland starts. Add this line to your `~/.config/hypr/hyprland.conf`:

```ini
exec-once = hypridle
```

## Manual Trigger (Keybind)

If you step away from your keyboard and want to trigger the screensaver immediately without waiting 30 seconds, you can bind it to a keyboard shortcut. Add this to your `~/.config/hypr/hyprland.conf`:

```ini
bind = SUPER, L, exec, madsnake
```
