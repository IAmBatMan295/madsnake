import re

with open("src/madsnake.c", "r") as f:
    code = f.read()

# 1. Darker PAIR_FILL
code = code.replace("init_color(16, (short)(r * 7 / 10), (short)(g * 7 / 10), (short)(b * 7 / 10));",
                    "init_color(16, (short)(r * 3 / 10), (short)(g * 3 / 10), (short)(b * 3 / 10));")

# 2. Add put_border
put_border_code = """
static void put_border(int y, int x)
{
    if (y >= 0 && y < LINES && x >= 0 && x < COLS) {
        cchar_t cc;
        wchar_t wstr[2] = { L'\\u2588', L'\\0' };
        setcchar(&cc, wstr, COLOR_PAIR(PAIR_SNAKE), (short)PAIR_SNAKE, NULL);
        mvadd_wch(y, x, &cc);
    }
}
"""
code = code.replace("static void fill_block(int sx, int sy)", put_border_code + "\nstatic void fill_block(int sx, int sy)")

# 3. Rewrite draw_head, draw_body, draw_tail
# I will just write a big regex replacement or find the blocks.

head_idx = code.find("static void draw_head(Pt p, Pt prev)")
tail_end = code.find("/* Erase a grid cell */")

new_drawing_code = """static void draw_head(Pt p, Pt prev)
{
    int sx = p.x * cell_w + offset_x;
    int sy = p.y * cell_h + offset_y;

    fill_block(sx, sy);

    int from_dx = p.x - prev.x;
    int from_dy = p.y - prev.y;
    
    int goes_right = (from_dx < 0);
    int goes_left  = (from_dx > 0);
    int goes_down  = (from_dy < 0);
    int goes_up    = (from_dy > 0);

    if (!goes_up) {
        for (int c = 0; c < cell_w; c++) put_border(sy, sx + c);
    }
    if (!goes_down) {
        for (int c = 0; c < cell_w; c++) put_border(sy + cell_h - 1, sx + c);
    }
    if (!goes_left) {
        for (int r = 0; r < cell_h; r++) put_border(sy + r, sx);
    }
    if (!goes_right) {
        for (int r = 0; r < cell_h; r++) put_border(sy + r, sx + cell_w - 1);
    }

    if (goes_up && goes_left) put_border(sy, sx);
    if (goes_up && goes_right) put_border(sy, sx + cell_w - 1);
    if (goes_down && goes_left) put_border(sy + cell_h - 1, sx);
    if (goes_down && goes_right) put_border(sy + cell_h - 1, sx + cell_w - 1);

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
    if (goes_right) facing_x = -1;
    if (goes_left) facing_x = 1;
    if (goes_down) facing_y = -1;
    if (goes_up) facing_y = 1;

    for (int r = -eh/2; r <= eh/2; r++) {
        for (int c = -ew/2; c <= ew/2; c++) {
            /* Left eye */
            if (c == facing_x && r == facing_y) {
                attron(COLOR_PAIR(PAIR_SNAKE));
                if (eye_y + r >= 0 && eye_y + r < LINES && eye_x1 + c >= 0 && eye_x1 + c < COLS)
                    mvaddch(eye_y + r, eye_x1 + c, ' ');
                attroff(COLOR_PAIR(PAIR_SNAKE));
            } else {
                cchar_t cc;
                wchar_t wstr[2] = { L'\\u2588', L'\\0' };
                setcchar(&cc, wstr, COLOR_PAIR(PAIR_EYE), (short)PAIR_EYE, NULL);
                if (eye_y + r >= 0 && eye_y + r < LINES && eye_x1 + c >= 0 && eye_x1 + c < COLS)
                    mvadd_wch(eye_y + r, eye_x1 + c, &cc);
            }
            
            /* Right eye */
            if (c == facing_x && r == facing_y) {
                attron(COLOR_PAIR(PAIR_SNAKE));
                if (eye_y + r >= 0 && eye_y + r < LINES && eye_x2 + c >= 0 && eye_x2 + c < COLS)
                    mvaddch(eye_y + r, eye_x2 + c, ' ');
                attroff(COLOR_PAIR(PAIR_SNAKE));
            } else {
                cchar_t cc;
                wchar_t wstr[2] = { L'\\u2588', L'\\0' };
                setcchar(&cc, wstr, COLOR_PAIR(PAIR_EYE), (short)PAIR_EYE, NULL);
                if (eye_y + r >= 0 && eye_y + r < LINES && eye_x2 + c >= 0 && eye_x2 + c < COLS)
                    mvadd_wch(eye_y + r, eye_x2 + c, &cc);
            }
        }
    }
}

static void draw_body(Pt p, Pt prev, Pt next)
{
    int sx = p.x * cell_w + offset_x;
    int sy = p.y * cell_h + offset_y;

    int from_dx = p.x - prev.x;
    int from_dy = p.y - prev.y;
    int to_dx   = next.x - p.x;
    int to_dy   = next.y - p.y;

    int horiz = (from_dy == 0 && to_dy == 0);
    int vert  = (from_dx == 0 && to_dx == 0);

    fill_block(sx, sy);

    if (horiz) {
        for (int c = 0; c < cell_w; c++) {
            put_border(sy, sx + c);
            put_border(sy + cell_h - 1, sx + c);
        }
    } else if (vert) {
        for (int r = 0; r < cell_h; r++) {
            put_border(sy + r, sx);
            put_border(sy + r, sx + cell_w - 1);
        }
    } else {
        int goes_right = (to_dx > 0 || from_dx < 0);
        int goes_left  = (to_dx < 0 || from_dx > 0);
        int goes_down  = (to_dy > 0 || from_dy < 0);
        int goes_up    = (to_dy < 0 || from_dy > 0);

        if (!goes_up) {
            for (int c = 0; c < cell_w; c++) put_border(sy, sx + c);
        }
        if (!goes_down) {
            for (int c = 0; c < cell_w; c++) put_border(sy + cell_h - 1, sx + c);
        }
        if (!goes_left) {
            for (int r = 0; r < cell_h; r++) put_border(sy + r, sx);
        }
        if (!goes_right) {
            for (int r = 0; r < cell_h; r++) put_border(sy + r, sx + cell_w - 1);
        }

        if (goes_up && goes_left) put_border(sy, sx);
        if (goes_up && goes_right) put_border(sy, sx + cell_w - 1);
        if (goes_down && goes_left) put_border(sy + cell_h - 1, sx);
        if (goes_down && goes_right) put_border(sy + cell_h - 1, sx + cell_w - 1);
    }
}

static void draw_tail(Pt p, Pt next)
{
    int sx = p.x * cell_w + offset_x;
    int sy = p.y * cell_h + offset_y;
    int dx = next.x - p.x;
    int dy = next.y - p.y;

    fill_block(sx, sy);
    
    int goes_right = (dx > 0);
    int goes_left  = (dx < 0);
    int goes_down  = (dy > 0);
    int goes_up    = (dy < 0);

    if (!goes_up) {
        for (int c = 0; c < cell_w; c++) put_border(sy, sx + c);
    }
    if (!goes_down) {
        for (int c = 0; c < cell_w; c++) put_border(sy + cell_h - 1, sx + c);
    }
    if (!goes_left) {
        for (int r = 0; r < cell_h; r++) put_border(sy + r, sx);
    }
    if (!goes_right) {
        for (int r = 0; r < cell_h; r++) put_border(sy + r, sx + cell_w - 1);
    }

    if (goes_up && goes_left) put_border(sy, sx);
    if (goes_up && goes_right) put_border(sy, sx + cell_w - 1);
    if (goes_down && goes_left) put_border(sy + cell_h - 1, sx);
    if (goes_down && goes_right) put_border(sy + cell_h - 1, sx + cell_w - 1);
}
"""

if head_idx != -1 and tail_end != -1:
    code = code[:head_idx] + new_drawing_code + "\n" + code[tail_end:]
    
# Finally remove draw_scale definition
start_scale = code.find("/* Draw a bright scale pattern in the center of a block */")
if start_scale != -1:
    end_scale = code.find("static void draw_head", start_scale)
    if end_scale != -1:
        code = code[:start_scale] + code[end_scale:]

with open("src/madsnake.c", "w") as f:
    f.write(code)
