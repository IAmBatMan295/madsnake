import re

with open("src/madsnake.c", "r") as f:
    code = f.read()

new_head = """static void draw_head(Pt p, Pt prev)
{
    int sx = p.x * cell_w + offset_x;
    int sy = p.y * cell_h + offset_y;

    /* Fill background first */
    fill_block(sx, sy);

    attron(COLOR_PAIR(PAIR_SNAKE));

    int from_dx = p.x - prev.x;
    int from_dy = p.y - prev.y;
    
    int goes_right = (from_dx < 0);
    int goes_left  = (from_dx > 0);
    int goes_down  = (from_dy < 0);
    int goes_up    = (from_dy > 0);

    if (!goes_up) {
        for (int c = 1; c < cell_w - 1; c++) sputch(sy, sx + c, ACS_HLINE);
    }
    if (!goes_down) {
        for (int c = 1; c < cell_w - 1; c++) sputch(sy + cell_h - 1, sx + c, ACS_HLINE);
    }
    if (!goes_left) {
        for (int r = 1; r < cell_h - 1; r++) sputch(sy + r, sx, ACS_VLINE);
    }
    if (!goes_right) {
        for (int r = 1; r < cell_h - 1; r++) sputch(sy + r, sx + cell_w - 1, ACS_VLINE);
    }

    if (!goes_up && !goes_left) sputch(sy, sx, ACS_ULCORNER);
    if (!goes_up && !goes_right) sputch(sy, sx + cell_w - 1, ACS_URCORNER);
    if (!goes_down && !goes_left) sputch(sy + cell_h - 1, sx, ACS_LLCORNER);
    if (!goes_down && !goes_right) sputch(sy + cell_h - 1, sx + cell_w - 1, ACS_LRCORNER);

    /* Fill in straight lines connecting to the open side */
    if (goes_up) {
        sputch(sy, sx, ACS_VLINE);
        sputch(sy, sx + cell_w - 1, ACS_VLINE);
    }
    if (goes_down) {
        sputch(sy + cell_h - 1, sx, ACS_VLINE);
        sputch(sy + cell_h - 1, sx + cell_w - 1, ACS_VLINE);
    }
    if (goes_left) {
        sputch(sy, sx, ACS_HLINE);
        sputch(sy + cell_h - 1, sx, ACS_HLINE);
    }
    if (goes_right) {
        sputch(sy, sx + cell_w - 1, ACS_HLINE);
        sputch(sy + cell_h - 1, sx + cell_w - 1, ACS_HLINE);
    }

    attroff(COLOR_PAIR(PAIR_SNAKE));

    /* Eyes — always inside on a middle row */
    int eye_y = sy + cell_h / 2;
    int eye_x1 = sx + cell_w / 4;
    int eye_x2 = sx + 3 * cell_w / 4;
    
    attron(COLOR_PAIR(PAIR_EYE) | A_BOLD);
    sputch(eye_y, eye_x1, 'o');
    sputch(eye_y, eye_x2, 'o');
    attroff(COLOR_PAIR(PAIR_EYE) | A_BOLD);
}"""

start_idx = code.find("static void draw_head(Pt p)")
end_idx = code.find("/*\n * BODY:")

if start_idx != -1 and end_idx != -1:
    code = code[:start_idx] + new_head + "\n\n" + code[end_idx:]
    
    # Fix the call
    code = code.replace("draw_head(p);", "Pt prev = snake_at(slen - 2);\n            draw_head(p, prev);")
    
    with open("src/madsnake.c", "w") as f:
        f.write(code)
else:
    print("Could not find draw_head.")
