import re

with open("src/madsnake.c", "r") as f:
    code = f.read()

# 1. Change INIT_LEN
code = code.replace("#define INIT_LEN  10", "#define INIT_LEN  5")

# 2. Extract pick_color
pick_color_func = """static void pick_color(void)
{
    if (has_colors()) {
        int colors[] = { COLOR_RED, COLOR_GREEN, COLOR_BLUE };
        int pick = colors[rand() % 3];

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
"""

# Insert pick_color before main()
main_idx = code.find("int main(void)")
code = code[:main_idx] + pick_color_func + "\n" + code[main_idx:]

# Replace the color logic in main with pick_color()
color_logic_start = code.find("if (has_colors()) {")
color_logic_end = code.find("bkgd(COLOR_PAIR(0));")
code = code[:color_logic_start] + "pick_color();\n\n    " + code[color_logic_end:]


# 3. Modify snake_move to handle growth and reset
old_move_start = code.find("    /* Erase old tail */")
old_move_end = code.find("    /* Redraw snake + food */")

new_move = """    int ate = (nx == food.x && ny == food.y);

    if (!ate) {
        /* Erase old tail */
        Pt old_tail = snake_at(0);
        erase_cell(old_tail.x, old_tail.y);
    }

    /* Advance ring buffer */
    shead = (shead + 1) % SNAKE_MAX;
    sbuf[shead].x = nx;
    sbuf[shead].y = ny;

    if (ate) {
        if (slen < SNAKE_MAX) slen++;
        food_spawn();
        draw_food();
    }

    if (slen >= INIT_LEN * 4) {
        /* OLED protection reset */
        clear();
        pick_color();
        snake_init();
        food_spawn();
        snake_draw();
        draw_food();
        return;
    }

"""

code = code[:old_move_start] + new_move + code[old_move_end:]

with open("src/madsnake.c", "w") as f:
    f.write(code)
