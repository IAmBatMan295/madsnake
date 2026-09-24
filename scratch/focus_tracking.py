with open("src/madsnake.c", "r") as f:
    text = f.read()

# Add focus tracking init
init_code = """    printf("\\033[?25l");
    printf("\\033]0;madsnake\\007");"""

new_init_code = """    printf("\\033[?25l");
    printf("\\033]0;madsnake\\007");
    printf("\\033[?1004h"); /* Enable focus tracking */"""
text = text.replace(init_code, new_init_code)

# Add focus tracking cleanup
clean_code = """    printf("\\033[?25h");
    fflush(stdout);
    endwin();"""

new_clean_code = """    printf("\\033[?1004l"); /* Disable focus tracking */
    printf("\\033[?25h");
    fflush(stdout);
    endwin();"""
text = text.replace(clean_code, new_clean_code)

with open("src/madsnake.c", "w") as f:
    f.write(text)
