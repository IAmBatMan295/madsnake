import re

with open("src/madsnake.c", "r") as f:
    code = f.read()

scale_func = """
/* Draw a bright scale pattern in the center of a block */
static void draw_scale(int sx, int sy)
{
    int sc_w = cell_w / 4;
    if (sc_w < 2) sc_w = 2;
    int sc_h = cell_h / 4;
    if (sc_h < 1) sc_h = 1;
    
    int cx = sx + cell_w / 2;
    int cy = sy + cell_h / 2;
    
    for (int r = -sc_h/2; r <= sc_h/2; r++) {
        for (int c = -sc_w/2; c <= sc_w/2; c++) {
            cchar_t cc;
            wchar_t wstr[2] = { L'\u2588', L'\0' };
            setcchar(&cc, wstr, COLOR_PAIR(PAIR_SNAKE), (short)PAIR_SNAKE, NULL);
            if (cy + r >= 0 && cy + r < LINES && cx + c >= 0 && cx + c < COLS)
                mvadd_wch(cy + r, cx + c, &cc);
        }
    }
}
"""
code = code.replace("static void draw_head(Pt p, Pt prev)", scale_func + "\nstatic void draw_head(Pt p, Pt prev)")

eyes_code = """
    /* Big eyes with directional pupils */
    int eye_y = sy + cell_h / 2;
    int eye_x1 = sx + cell_w / 4;
    int eye_x2 = sx + 3 * cell_w / 4;

    int ew = cell_w / 6;
    if (ew < 2) ew = 2;
    int eh = cell_h / 4;
    if (eh < 2) eh = 2;

    int facing_x = 0;
    int facing_y = 0;
    if (goes_right) facing_x = 1;
    if (goes_left) facing_x = -1;
    if (goes_down) facing_y = 1;
    if (goes_up) facing_y = -1;

    for (int r = -eh/2; r <= eh/2; r++) {
        for (int c = -ew/2; c <= ew/2; c++) {
            /* Left eye */
            if (c == facing_x && r == facing_y) {
                sputch(eye_y + r, eye_x1 + c, ' ');
            } else {
                cchar_t cc;
                wchar_t wstr[2] = { L'\u2588', L'\0' };
                setcchar(&cc, wstr, COLOR_PAIR(PAIR_EYE), (short)PAIR_EYE, NULL);
                if (eye_y + r >= 0 && eye_y + r < LINES && eye_x1 + c >= 0 && eye_x1 + c < COLS)
                    mvadd_wch(eye_y + r, eye_x1 + c, &cc);
            }
            
            /* Right eye */
            if (c == facing_x && r == facing_y) {
                sputch(eye_y + r, eye_x2 + c, ' ');
            } else {
                cchar_t cc;
                wchar_t wstr[2] = { L'\u2588', L'\0' };
                setcchar(&cc, wstr, COLOR_PAIR(PAIR_EYE), (short)PAIR_EYE, NULL);
                if (eye_y + r >= 0 && eye_y + r < LINES && eye_x2 + c >= 0 && eye_x2 + c < COLS)
                    mvadd_wch(eye_y + r, eye_x2 + c, &cc);
            }
        }
    }
}"""

old_eyes = """    /* Eyes — always inside on a middle row */
    int eye_y = sy + cell_h / 2;
    int eye_x1 = sx + cell_w / 4;
    int eye_x2 = sx + 3 * cell_w / 4;
    
    attron(COLOR_PAIR(PAIR_EYE) | A_BOLD);
    sputch(eye_y, eye_x1, 'o');
    sputch(eye_y, eye_x2, 'o');
    attroff(COLOR_PAIR(PAIR_EYE) | A_BOLD);
}"""

code = code.replace(old_eyes, eyes_code)

code = code.replace("fill_block(sx, sy);", "fill_block(sx, sy);\n    draw_scale(sx, sy);")

with open("src/madsnake.c", "w") as f:
    f.write(code)
