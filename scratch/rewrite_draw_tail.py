import re

with open("src/madsnake.c", "r") as f:
    code = f.read()

new_tail = """static void draw_tail(Pt p, Pt next)
{
    int sx = p.x * cell_w + offset_x;
    int sy = p.y * cell_h + offset_y;
    int dx = next.x - p.x;
    int dy = next.y - p.y;

    /* Fill background first */
    fill_block(sx, sy);

    attron(COLOR_PAIR(PAIR_SNAKE));

    if (dx != 0) {
        /* Horizontal segment with end cap */
        for (int c = 0; c < cell_w; c++) {
            sputch(sy, sx + c, ACS_HLINE);
            sputch(sy + cell_h - 1, sx + c, ACS_HLINE);
        }
        if (dx > 0) {
            /* body to right → cap on left */
            sputch(sy, sx, ACS_ULCORNER);
            for (int r = 1; r < cell_h - 1; r++)
                sputch(sy + r, sx, ACS_VLINE);
            sputch(sy + cell_h - 1, sx, ACS_LLCORNER);
        } else {
            /* body to left → cap on right */
            sputch(sy, sx + cell_w - 1, ACS_URCORNER);
            for (int r = 1; r < cell_h - 1; r++)
                sputch(sy + r, sx + cell_w - 1, ACS_VLINE);
            sputch(sy + cell_h - 1, sx + cell_w - 1, ACS_LRCORNER);
        }
    } else {
        /* Vertical segment with end cap */
        for (int r = 0; r < cell_h; r++) {
            sputch(sy + r, sx, ACS_VLINE);
            sputch(sy + r, sx + cell_w - 1, ACS_VLINE);
        }
        if (dy > 0) {
            /* body below → cap on top */
            for (int c = 0; c < cell_w; c++) sputch(sy, sx + c, ACS_HLINE);
            sputch(sy, sx, ACS_ULCORNER);
            sputch(sy, sx + cell_w - 1, ACS_URCORNER);
        } else {
            /* body above → cap on bottom */
            for (int c = 0; c < cell_w; c++) sputch(sy + cell_h - 1, sx + c, ACS_HLINE);
            sputch(sy + cell_h - 1, sx, ACS_LLCORNER);
            sputch(sy + cell_h - 1, sx + cell_w - 1, ACS_LRCORNER);
        }
    }

    attroff(COLOR_PAIR(PAIR_SNAKE));
}"""

start_idx = code.find("static void draw_tail(Pt p, Pt next)")
end_idx = code.find("/* Erase a grid cell */")

if start_idx != -1 and end_idx != -1:
    code = code[:start_idx] + new_tail + "\n\n" + code[end_idx:]
    with open("src/madsnake.c", "w") as f:
        f.write(code)
else:
    print("Could not find draw_tail or Erase comment.")
