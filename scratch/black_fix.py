with open("src/madsnake.c", "r") as f:
    text = f.read()

# In main():
#     if (has_colors()) {
#         start_color();
#         use_default_colors();
#         assume_default_colors(-1, COLOR_BLACK);
#     }

old_color_init = """    if (has_colors()) {
        start_color();
        use_default_colors();
        assume_default_colors(-1, COLOR_BLACK);
    }"""

new_color_init = """    if (has_colors()) {
        start_color();
        if (can_change_color()) {
            init_color(COLOR_BLACK, 0, 0, 0); /* Force absolute pitch black */
        }
        use_default_colors();
        assume_default_colors(-1, COLOR_BLACK);
    }"""

text = text.replace(old_color_init, new_color_init)

with open("src/madsnake.c", "w") as f:
    f.write(text)
