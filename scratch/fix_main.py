with open("src/madsnake.c", "r") as f:
    text = f.read()

start_bad = text.find("static void pick_color(void)\n{\n    pick_color();\n\n    bkgd(COLOR_PAIR(0));")

if start_bad != -1:
    end_bad = start_bad + len("static void pick_color(void)\n{\n    pick_color();\n\n    ")
    
    correct = """
static void pick_color(void)
{
    if (has_colors()) {
        int colors[] = { COLOR_RED, COLOR_GREEN, COLOR_BLUE };
        int pick = colors[rand() % 3];
        log_int("Snake color", pick);

        init_pair(PAIR_SNAKE,  pick, COLOR_BLACK);
        init_pair(PAIR_FILL,   pick, COLOR_BLACK);
        init_pair(PAIR_EYE,    COLOR_WHITE, COLOR_BLACK);
        init_pair(PAIR_FOOD,   COLOR_WHITE, COLOR_BLACK);

        if (can_change_color()) {
            short r, g, b;
            color_content(pick, &r, &g, &b);
            init_color(16, (short)(r * 3 / 10), (short)(g * 3 / 10), (short)(b * 3 / 10));
            init_pair(PAIR_FILL, 16, COLOR_BLACK);
        }
    }
}

int main(void)
{
    logfp = fopen("/tmp/madsnake.log", "w");
    log_msg("Starting madsnake");
    cursor_hide();
    setlocale(LC_ALL, "");
    srand((unsigned)time(NULL) ^ (unsigned)getpid());

    initscr();
    cbreak();
    noecho();
    curs_set(0);
    leaveok(stdscr, TRUE);
    printf("\\033[?25l");
    fflush(stdout);
    nodelay(stdscr, TRUE);
    keypad(stdscr, TRUE);

    napms(500);
    {
        struct winsize ws;
        if (ioctl(STDOUT_FILENO, TIOCGWINSZ, &ws) == 0 &&
            (ws.ws_row != LINES || ws.ws_col != COLS)) {
            log_msg("Terminal resized after init — re-reading size");
            resize_term(ws.ws_row, ws.ws_col);
            clear();
        }
    }

    mousemask(BUTTON1_PRESSED | BUTTON2_PRESSED | BUTTON3_PRESSED |
              BUTTON4_PRESSED | BUTTON5_PRESSED, NULL);
    mouseinterval(0);
    
    if (has_colors()) {
        start_color();
        use_default_colors();
        assume_default_colors(-1, COLOR_BLACK);
    }

    pick_color();

    """
    
    text = text[:start_bad] + correct + text[end_bad:]
    with open("src/madsnake.c", "w") as f:
        f.write(text)

# We also need to add forward declaration for pick_color if we used it in snake_move
# Or just move pick_color to the top of the file.
