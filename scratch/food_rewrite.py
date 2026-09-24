import re

with open("src/madsnake.c", "r") as f:
    code = f.read()

# 1. Replace in_egg with get_sphere_shade
old_in_egg = """static int in_egg(int c, int sub_r)
{
    double t = (double)sub_r / (2.0 * cell_h - 1.0);
    double y = t * 2.0 - 1.0;
    double max_term = 1.0 - y * y;
    if (max_term < 0) max_term = 0;
    
    /* Gentle, uniform egg curve using (1 + 0.2 * y) */
    double x_val = (1.0 + 0.2 * y) * sqrt(max_term);
    
    double hw = x_val * (cell_w / 2.0 - 1.0);
    double cx = cell_w / 2.0;
    double dist = fabs((c + 0.5) - cx);
    return dist <= hw;
}"""

new_shade = """/* Returns shade level: 0 (empty), 1 (light), 2 (medium), 3 (dark), 4 (highlight) */
static int get_sphere_shade(int c, int sub_r)
{
    double y = ((double)sub_r / (2.0 * cell_h - 1.0)) * 2.0 - 1.0;
    double cx = cell_w / 2.0;
    double x = (c + 0.5 - cx) / (cell_w / 2.0 - 1.0);
    
    if (x*x + y*y <= 1.0) {
        double z2 = 1.0 - x*x - y*y;
        double z = sqrt(z2 > 0 ? z2 : 0);
        
        double Lx = -0.5, Ly = -0.5, Lz = 0.707;
        double dot = x*Lx + y*Ly + z*Lz;
        
        if (dot > 0.4) return 4;
        if (dot > 0.0) return 3;
        if (dot > -0.4) return 2;
        return 1;
    }
    return 0;
}"""

code = code.replace(old_in_egg, new_shade)

# 2. Rewrite draw_food
old_draw_food_start = "static void draw_food(void)"
old_draw_food_end = "/* Erase a grid cell */"
start_idx = code.find(old_draw_food_start)
end_idx = code.find(old_draw_food_end)

if start_idx != -1 and end_idx != -1:
    new_draw_food = """static void draw_food(void)
{
    int sx = food.x * cell_w + offset_x;
    int sy = food.y * cell_h + offset_y;

    cchar_t cc_full, cc_lower, cc_upper, cc_dark, cc_mid, cc_light;
    wchar_t w_full[2]  = { L'\\u2588', L'\\0' };  /* █ full block  */
    wchar_t w_lower[2] = { L'\\u2584', L'\\0' };  /* ▄ lower half  */
    wchar_t w_upper[2] = { L'\\u2580', L'\\0' };  /* ▀ upper half  */
    wchar_t w_dark[2]  = { L'\\u2593', L'\\0' };  /* ▓ dark shade  */
    wchar_t w_mid[2]   = { L'\\u2592', L'\\0' };  /* ▒ mid shade   */
    wchar_t w_light[2] = { L'\\u2591', L'\\0' };  /* ░ light shade */

    setcchar(&cc_full,  w_full,  COLOR_PAIR(PAIR_FOOD), (short)PAIR_FOOD, NULL);
    setcchar(&cc_lower, w_lower, COLOR_PAIR(PAIR_FOOD), (short)PAIR_FOOD, NULL);
    setcchar(&cc_upper, w_upper, COLOR_PAIR(PAIR_FOOD), (short)PAIR_FOOD, NULL);
    setcchar(&cc_dark,  w_dark,  COLOR_PAIR(PAIR_FOOD), (short)PAIR_FOOD, NULL);
    setcchar(&cc_mid,   w_mid,   COLOR_PAIR(PAIR_FOOD), (short)PAIR_FOOD, NULL);
    setcchar(&cc_light, w_light, COLOR_PAIR(PAIR_FOOD), (short)PAIR_FOOD, NULL);

    for (int r = 0; r < cell_h; r++) {
        for (int c = 0; c < cell_w; c++) {
            int upper = get_sphere_shade(c, 2 * r);
            int lower = get_sphere_shade(c, 2 * r + 1);
            
            if (upper || lower) {
                if (sy + r >= 0 && sy + r < LINES && sx + c >= 0 && sx + c < COLS) {
                    if (upper && lower) {
                        int avg = (upper + lower) / 2;
                        if (avg >= 4) mvadd_wch(sy + r, sx + c, &cc_full);
                        else if (avg == 3) mvadd_wch(sy + r, sx + c, &cc_dark);
                        else if (avg == 2) mvadd_wch(sy + r, sx + c, &cc_mid);
                        else mvadd_wch(sy + r, sx + c, &cc_light);
                    }
                    else if (upper) mvadd_wch(sy + r, sx + c, &cc_upper);
                    else mvadd_wch(sy + r, sx + c, &cc_lower);
                }
            }
        }
    }
}

"""
    code = code[:start_idx] + new_draw_food + code[end_idx:]

# 3. Replace srand
code = code.replace("srand((unsigned)time(NULL));", "srand((unsigned)time(NULL) ^ (unsigned)getpid());")

with open("src/madsnake.c", "w") as f:
    f.write(code)
