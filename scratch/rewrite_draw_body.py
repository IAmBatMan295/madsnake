import re

with open("src/madsnake.c", "r") as f:
    code = f.read()

new_body = """static void draw_body(Pt p, Pt prev, Pt next)
{
    int sx = p.x * cell_w + offset_x;
    int sy = p.y * cell_h + offset_y;

    int from_dx = p.x - prev.x;
    int from_dy = p.y - prev.y;
    int to_dx   = next.x - p.x;
    int to_dy   = next.y - p.y;

    int horiz = (from_dy == 0 && to_dy == 0);
    int vert  = (from_dx == 0 && to_dx == 0);

    /* Fill background first */
    fill_block(sx, sy);

    attron(COLOR_PAIR(PAIR_SNAKE));

    if (horiz) {
        for (int c = 0; c < cell_w; c++) {
            sputch(sy, sx + c, ACS_HLINE);
            sputch(sy + cell_h - 1, sx + c, ACS_HLINE);
        }
    } else if (vert) {
        for (int r = 0; r < cell_h; r++) {
            sputch(sy + r, sx, ACS_VLINE);
            sputch(sy + r, sx + cell_w - 1, ACS_VLINE);
        }
    } else {
        int goes_right = (to_dx > 0 || from_dx < 0);
        int goes_left  = (to_dx < 0 || from_dx > 0);
        int goes_down  = (to_dy > 0 || from_dy < 0);
        int goes_up    = (to_dy < 0 || from_dy > 0);

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

        /* Draw necessary corners */
        if (!goes_up && !goes_left) sputch(sy, sx, ACS_ULCORNER);
        if (!goes_up && !goes_right) sputch(sy, sx + cell_w - 1, ACS_URCORNER);
        if (!goes_down && !goes_left) sputch(sy + cell_h - 1, sx, ACS_LLCORNER);
        if (!goes_down && !goes_right) sputch(sy + cell_h - 1, sx + cell_w - 1, ACS_LRCORNER);
        
        /* Fill in straight lines connecting to the open corners */
        if (goes_up && goes_left) {
            sputch(sy, sx + cell_w - 1, ACS_VLINE);
            sputch(sy + cell_h - 1, sx, ACS_HLINE);
        }
        if (goes_up && goes_right) {
            sputch(sy, sx, ACS_VLINE);
            sputch(sy + cell_h - 1, sx + cell_w - 1, ACS_HLINE);
        }
        if (goes_down && goes_left) {
            sputch(sy, sx, ACS_HLINE);
            sputch(sy + cell_h - 1, sx + cell_w - 1, ACS_VLINE);
        }
        if (goes_down && goes_right) {
            sputch(sy, sx + cell_w - 1, ACS_HLINE);
            sputch(sy + cell_h - 1, sx, ACS_VLINE);
        }
    }

    attroff(COLOR_PAIR(PAIR_SNAKE));
}"""

# Find the start of draw_body and the start of draw_tail
start_idx = code.find("static void draw_body(Pt p, Pt prev, Pt next)")
end_idx = code.find("/*\n * TAIL:")

if start_idx != -1 and end_idx != -1:
    code = code[:start_idx] + new_body + "\n\n" + code[end_idx:]
    with open("src/madsnake.c", "w") as f:
        f.write(code)
else:
    print("Could not find draw_body or TAIL comment.")
