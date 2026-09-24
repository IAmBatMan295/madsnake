/*
 * madsnake.c — MadSnake terminal screensaver
 * P1: Black screen, exit on key/click
 * P2: Snake rendering — checkered opaque body, box-drawing border,
 *     ASCII head with perpendicular eyes, square tail
 *
 * Grid: 6 cols x 3 rows per cell (visually ~square)
 */

#define _XOPEN_SOURCE_EXTENDED 1

#include <ncurses.h>
#include <locale.h>
#include <stdio.h>
static void pick_color(void);
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <wchar.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <math.h>

/* ── Logging ─────────────────────────────────────────────── */

static FILE *logfp = NULL;

static void log_msg(const char *msg)
{
    if (!logfp) return;
    time_t t = time(NULL);
    struct tm *tm = localtime(&t);
    fprintf(logfp, "[%02d:%02d:%02d] %s\n",
            tm->tm_hour, tm->tm_min, tm->tm_sec, msg);
    fflush(logfp);
}

static void log_int(const char *label, int val)
{
    if (!logfp) return;
    time_t t = time(NULL);
    struct tm *tm = localtime(&t);
    fprintf(logfp, "[%02d:%02d:%02d] %s: %d\n",
            tm->tm_hour, tm->tm_min, tm->tm_sec, label, val);
    fflush(logfp);
}

/* ── Constants ───────────────────────────────────────────── */

static int cell_w = 12;
static int cell_h = 6;

enum { DIR_RIGHT = 0, DIR_DOWN, DIR_LEFT, DIR_UP };

static const int DX[] = { 1, 0, -1, 0 };
static const int DY[] = { 0, 1, 0, -1 };

static int cfg_speed_ms = 120;
static int cfg_max_length = 20;
static int cfg_default_length = 5;

static void load_config(void)
{
    const char *home = getenv("HOME");
    if (!home) return;
    
    char path[512];
    snprintf(path, sizeof(path), "%s/.config/madsnake/config", home);
    
    FILE *f = fopen(path, "r");
    if (!f) return;
    
    char line[256];
    while (fgets(line, sizeof(line), f)) {
        if (strncmp(line, "speed_ms=", 9) == 0) {
            cfg_speed_ms = atoi(line + 9);
        } else if (strncmp(line, "max_length=", 11) == 0) {
            cfg_max_length = atoi(line + 11);
        } else if (strncmp(line, "default_length=", 15) == 0) {
            cfg_default_length = atoi(line + 15);
        }
    }
    fclose(f);
    
    if (cfg_speed_ms < 10) cfg_speed_ms = 10;
    
    if (cfg_default_length < 1) {
        log_msg("Warning: default_length < 1. Clamping to 1.");
        cfg_default_length = 1;
    }
    if (cfg_max_length < cfg_default_length) {
        log_msg("Warning: max_length < default_length. Clamping max_length.");
        cfg_max_length = cfg_default_length;
    }
}

/* ── Snake data ──────────────────────────────────────────── */

#define SNAKE_MAX 8192


typedef struct { int x, y; } Pt;

static Pt   sbuf[SNAKE_MAX];
static int  shead;
static int  slen;
static int  sdir;
static int  grid_w, grid_h;
static int  offset_x, offset_y;

/* Color pairs */
enum {
    PAIR_SNAKE  = 1,   /* outline color */
    PAIR_FILL   = 2,   /* interior fill (slightly darker) */
    PAIR_EYE    = 3,   /* eyes */
    PAIR_FOOD   = 4,   /* food */
};

/* ── Helpers ──────────────────────────────────────────────── */

static Pt snake_at(int offset)
{
    return sbuf[(shead - slen + 1 + offset + SNAKE_MAX) % SNAKE_MAX];
}

/* Safe mvaddch */

/* Fill an entire block with solid color (borders drawn on top) */

static void put_border(int y, int x)
{
    if (y >= 0 && y < LINES && x >= 0 && x < COLS) {
        cchar_t cc;
        wchar_t wstr[2] = { L'\u2588', L'\0' };
        setcchar(&cc, wstr, COLOR_PAIR(PAIR_SNAKE), (short)PAIR_SNAKE, NULL);
        mvadd_wch(y, x, &cc);
    }
}

static void fill_block(int sx, int sy)
{
    for (int r = 0; r < cell_h; r++) {
        int y = sy + r;
        for (int c = 0; c < cell_w; c++) {
            int x = sx + c;
            cchar_t cc;
            wchar_t wstr[2] = { L'\u2588', L'\0' };
            setcchar(&cc, wstr, COLOR_PAIR(PAIR_FILL), (short)PAIR_FILL, NULL);
            if (y >= 0 && y < LINES && x >= 0 && x < COLS)
                mvadd_wch(y, x, &cc);
        }
    }
}

/* ── Snake tile rendering ────────────────────────────────── */

/*
 * HEAD: bordered box with perpendicular eyes and forked tongue.
 *
 * RIGHT:          LEFT:
 * +--o--+         +--o--+
 * |#xx#|<        >|#xx#|
 * +--o--+         +--o--+
 *
 * Eyes on top/bottom borders, tongue outside head.
 * Interior filled with checker.
 */

static void draw_head(Pt p, Pt prev)
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
                wchar_t wstr[2] = { L'\u2588', L'\0' };
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
                wchar_t wstr[2] = { L'\u2588', L'\0' };
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

/* Erase a grid cell */
static void erase_cell(int gx, int gy)
{
    int sx = gx * cell_w + offset_x;
    int sy = gy * cell_h + offset_y;
    for (int r = 0; r < cell_h; r++)
        for (int c = 0; c < cell_w; c++)
            if (sy + r < LINES && sx + c < COLS)
                mvaddch(sy + r, sx + c, ' ');
}

/* ── Full snake draw ─────────────────────────────────────── */

static void snake_draw(void)
{
    for (int i = 0; i < slen; i++) {
        Pt p = snake_at(i);

        if (i == slen - 1) {
            Pt prev = snake_at(slen - 2);
            draw_head(p, prev);
        } else if (i == 0) {
            Pt next = snake_at(1);
            draw_tail(p, next);
        } else {
            Pt prev = snake_at(i - 1);
            Pt next = snake_at(i + 1);
            draw_body(p, prev, next);
        }
    }
}

/* ── Grid / init ─────────────────────────────────────────── */

static void grid_init(void)
{
    /* Dynamically calculate visually square cells */
    struct winsize ws;
    if (ioctl(STDOUT_FILENO, TIOCGWINSZ, &ws) == 0 && ws.ws_xpixel > 0 && ws.ws_ypixel > 0 && ws.ws_col > 0 && ws.ws_row > 0) {
        double char_w = (double)ws.ws_xpixel / ws.ws_col;
        double char_h = (double)ws.ws_ypixel / ws.ws_row;
        
        /* Target the exact visual proportion the user liked (~1/26th of screen) */
        cell_w = COLS / 26;
        if (cell_w < 6) cell_w = 6;
        
        /* Calculate cell_h to make the physical block square */
        cell_h = (int)round((cell_w * char_w) / char_h);
        if (cell_h < 3) cell_h = 3;
    } else {
        /* Fallback if no pixel info */
        cell_w = COLS / 26;
        if (cell_w < 6) cell_w = 6;
        cell_h = cell_w / 2;
        if (cell_h < 3) cell_h = 3;
    }

    /* Floor division — only complete cells that fit on screen */
    grid_w = COLS / cell_w;
    grid_h = LINES / cell_h;
    
    /* Center the grid to distribute the remainder evenly (padding) */
    offset_x = (COLS - grid_w * cell_w) / 2;
    offset_y = (LINES - grid_h * cell_h) / 2;
    
    log_int("COLS", COLS);
    log_int("LINES", LINES);
    log_int("cell_w", cell_w);
    log_int("cell_h", cell_h);
    log_int("Grid W", grid_w);
    log_int("Grid H", grid_h);
    log_int("Offset X", offset_x);
    log_int("Offset Y", offset_y);
}

static void snake_init(void)
{
    grid_init();
    int cx = grid_w / 2;
    int cy = grid_h / 2;

    slen = cfg_default_length;
    sdir = DIR_RIGHT;
    shead = slen - 1;

    int start_x = cx - (slen - 1);
    if (start_x < 1) start_x = 1;
    if (start_x + slen - 1 >= grid_w - 1)
        start_x = grid_w - slen - 1;

    for (int i = 0; i < slen; i++) {
        sbuf[i].x = start_x + i;
        sbuf[i].y = cy;
    }
}

/* ── Cursor hiding (Hyprland) ────────────────────────────── */

static int orig_cursor_timeout = -1;

static void cursor_hide(void)
{
    FILE *pp = popen("hyprctl getoption cursor:inactive_timeout -j 2>/dev/null", "r");
    if (pp) {
        char buf[512];
        size_t n = fread(buf, 1, sizeof(buf) - 1, pp);
        buf[n] = '\0';
        pclose(pp);
        char *p = strstr(buf, "\"int\":");
        if (p) orig_cursor_timeout = atoi(p + 6);
    }
    system("hyprctl keyword cursor:inactive_timeout 1 > /dev/null 2>&1");
}

static void cursor_restore(void)
{
    if (orig_cursor_timeout >= 0) {
        char cmd[128];
        snprintf(cmd, sizeof(cmd),
                 "hyprctl keyword cursor:inactive_timeout %d > /dev/null 2>&1",
                 orig_cursor_timeout);
        system(cmd);
    }
}

/* ── Food ────────────────────────────────────────────────── */

static Pt food;

static int on_snake(int gx, int gy)
{
    for (int i = 0; i < slen; i++) {
        Pt s = snake_at(i);
        if (s.x == gx && s.y == gy) return 1;
    }
    return 0;
}

static int pos_valid(int gx, int gy)
{
    if (gx < 0 || gx >= grid_w || gy < 0 || gy >= grid_h)
        return 0;
    return !on_snake(gx, gy);
}

static void food_spawn(void)
{
    int attempts = 0;
    do {
        food.x = rand() % grid_w;
        food.y = rand() % grid_h;
        attempts++;
    } while (on_snake(food.x, food.y) && attempts < 10000);
    log_int("Food X", food.x);
    log_int("Food Y", food.y);
    log_int("Food grid_w", grid_w);
    log_int("Food grid_h", grid_h);
    log_int("Food screen_x", food.x * cell_w + offset_x);
    log_int("Food screen_y", food.y * cell_h + offset_y);
}

/* Returns shade level: 0 (empty), 1 (light), 2 (medium), 3 (dark), 4 (highlight) */
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
}

static void draw_food(void)
{
    int sx = food.x * cell_w + offset_x;
    int sy = food.y * cell_h + offset_y;

    cchar_t cc_full, cc_lower, cc_upper, cc_dark, cc_mid, cc_light;
    wchar_t w_full[2]  = { L'\u2588', L'\0' };  /* █ full block  */
    wchar_t w_lower[2] = { L'\u2584', L'\0' };  /* ▄ lower half  */
    wchar_t w_upper[2] = { L'\u2580', L'\0' };  /* ▀ upper half  */
    wchar_t w_dark[2]  = { L'\u2593', L'\0' };  /* ▓ dark shade  */
    wchar_t w_mid[2]   = { L'\u2592', L'\0' };  /* ▒ mid shade   */
    wchar_t w_light[2] = { L'\u2591', L'\0' };  /* ░ light shade */

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

/* ── BFS pathfinding ─────────────────────────────────────── */

#define MAX_GRID (300 * 120)

static int bfs_find_dir(Pt start, Pt target)
{
    /* Allocate BFS arrays on stack (bounded by MAX_GRID) */
    int total = grid_w * grid_h;
    if (total > MAX_GRID) total = MAX_GRID;

    static int visited[MAX_GRID];
    static int parent_dir[MAX_GRID]; /* direction taken to reach this cell */
    static int qx[MAX_GRID], qy[MAX_GRID];

    memset(visited, 0, sizeof(int) * (size_t)total);

    int si = start.y * grid_w + start.x;
    visited[si] = 1;

    int qfront = 0, qback = 0;
    qx[qback] = start.x;
    qy[qback] = start.y;
    parent_dir[si] = -1;
    qback++;

    while (qfront < qback) {
        int cx = qx[qfront];
        int cy = qy[qfront];
        qfront++;

        if (cx == target.x && cy == target.y) {
            /* Trace back to find the first step direction */
            int tx = cx, ty = cy;
            while (1) {
                int idx = ty * grid_w + tx;
                int d = parent_dir[idx];
                /* Reverse one step */
                int px = tx - DX[d];
                int py = ty - DY[d];
                if (px == start.x && py == start.y)
                    return d; /* this is the direction from start */
                tx = px;
                ty = py;
            }
        }

        for (int d = 0; d < 4; d++) {
            int nx = cx + DX[d];
            int ny = cy + DY[d];
            if (nx < 0 || nx >= grid_w || ny < 0 || ny >= grid_h) continue;
            int ni = ny * grid_w + nx;
            if (ni >= total) continue;
            if (visited[ni]) continue;
            if (on_snake(nx, ny)) continue;
            visited[ni] = 1;
            parent_dir[ni] = d;
            qx[qback] = nx;
            qy[qback] = ny;
            qback++;
            if (qback >= total) break;
        }
    }

    return -1; /* no path found */
}

/* ── Movement ────────────────────────────────────────────── */

static void snake_move(void)
{
    Pt head = snake_at(slen - 1);

    /* Try BFS to food */
    int dir = bfs_find_dir(head, food);

    if (dir >= 0) {
        sdir = dir;
    } else {
        /* No path to food — wander: pick any valid direction */
        int dirs[4] = { sdir, (sdir + 1) % 4, (sdir + 3) % 4, (sdir + 2) % 4 };
        int found = 0;
        for (int i = 0; i < 4; i++) {
            int nx = head.x + DX[dirs[i]];
            int ny = head.y + DY[dirs[i]];
            if (pos_valid(nx, ny)) {
                sdir = dirs[i];
                found = 1;
                break;
            }
        }
        if (!found) return; /* completely stuck — skip frame */
    }

    int nx = head.x + DX[sdir];
    int ny = head.y + DY[sdir];

    int ate = (nx == food.x && ny == food.y);

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

    if (slen >= cfg_max_length) {
        /* OLED protection reset */
        clear();
        pick_color();
        snake_init();
        food_spawn();
        snake_draw();
        draw_food();
        return;
    }

    /* Redraw snake + food */
    snake_draw();
    draw_food();
}

/* ── Main ────────────────────────────────────────────────── */


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
    load_config();
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
    printf("\033[?25l");
    printf("\033]0;madsnake\007");
    printf("\033[?1004h"); /* Enable focus tracking */
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
        if (can_change_color()) {
            init_color(COLOR_BLACK, 0, 0, 0); /* Force absolute pitch black */
        }
        use_default_colors();
        assume_default_colors(-1, COLOR_BLACK);
    }

    pick_color();

    bkgd(COLOR_PAIR(0));
    clear();
    snake_init();
    food_spawn();
    snake_draw();
    draw_food();
    refresh();

    log_int("COLS", COLS);
    log_int("LINES", LINES);
    log_msg("Entering main loop");

    napms(100);
    while (getch() != ERR) {}

    int speed_ms = cfg_speed_ms;
    for (;;) {
        /* Check for exit input (drain all queued events) */
        int quit = 0;
        int ch;
        while ((ch = getch()) != ERR) {
            if (ch == KEY_MOUSE) {
                MEVENT me;
                if (getmouse(&me) == OK &&
                    (me.bstate & (BUTTON1_PRESSED | BUTTON2_PRESSED |
                                  BUTTON3_PRESSED | BUTTON4_PRESSED |
                                  BUTTON5_PRESSED)))
                    quit = 1;
            } else {
                /* Any other key, including KEY_RESIZE, terminates */
                quit = 1;
            }
        }
        if (quit) break;

        snake_move();
        refresh();
        napms(speed_ms);
    }

    printf("\033[?1004l"); /* Disable focus tracking */
    printf("\033[?25h");
    fflush(stdout);
    endwin();
    cursor_restore();

    log_msg("Done");
    if (logfp) fclose(logfp);
    return 0;
}
