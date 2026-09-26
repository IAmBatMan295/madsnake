import re

with open("src/madsnake.c", "r") as f:
    text = f.read()

# We want to replace everything from "/* ── AI & Pathfinding" or "/* ── BFS pathfinding" up to "/* ── Main ──"
start1 = text.find("/* ── AI & Pathfinding")
if start1 == -1:
    start1 = text.find("/* ── BFS pathfinding")

end1 = text.find("/* ── Main ──")

if start1 == -1 or end1 == -1:
    print("Could not find boundaries")
    exit(1)

new_ai = """/* ── AI & Pathfinding ──────────────────────────────────── */

#define MAX_GRID (300 * 120)

static int is_body(int gx, int gy, int ignore_tail)
{
    if (gx < 0 || gx >= grid_w || gy < 0 || gy >= grid_h) return 1;
    for (int i = ignore_tail; i < slen; i++) {
        Pt s = snake_at(i);
        if (s.x == gx && s.y == gy) return 1;
    }
    return 0;
}

static int bfs_dist(Pt start, Pt target, int ignore_tail)
{
    int total = grid_w * grid_h;
    if (total > MAX_GRID) total = MAX_GRID;

    static int visited[MAX_GRID];
    static int qx[MAX_GRID], qy[MAX_GRID], qd[MAX_GRID];

    memset(visited, 0, sizeof(int) * (size_t)total);

    int si = start.y * grid_w + start.x;
    visited[si] = 1;

    int qfront = 0, qback = 0;
    qx[qback] = start.x;
    qy[qback] = start.y;
    qd[qback] = 0;
    qback++;

    while (qfront < qback) {
        int cx = qx[qfront];
        int cy = qy[qfront];
        int cd = qd[qfront];
        qfront++;

        if (cx == target.x && cy == target.y) {
            return cd;
        }

        for (int d = 0; d < 4; d++) {
            int nx = cx + DX[d];
            int ny = cy + DY[d];
            if (nx < 0 || nx >= grid_w || ny < 0 || ny >= grid_h) continue;
            
            int ni = ny * grid_w + nx;
            if (visited[ni]) continue;
            if (is_body(nx, ny, ignore_tail)) continue;
            
            visited[ni] = 1;
            qx[qback] = nx;
            qy[qback] = ny;
            qd[qback] = cd + 1;
            qback++;
        }
    }
    return MAX_GRID;
}

/* ── Movement ────────────────────────────────────────────── */

static void snake_move(void)
{
    Pt head = snake_at(slen - 1);
    
    int best_dir = -1;
    int min_food_dist = MAX_GRID;
    int max_tail_dist = -1;
    
    for (int i = 0; i < 4; i++) {
        int d = (sdir + ((i == 0) ? 0 : (i == 1) ? 1 : (i == 2) ? 3 : 2)) % 4;
        int nx = head.x + DX[d];
        int ny = head.y + DY[d];
        
        int ate_food = (nx == food.x && ny == food.y);
        int ignore_tail = ate_food ? 0 : 1; 

        if (is_body(nx, ny, ignore_tail)) continue;
        
        Pt next = {nx, ny};
        int d_food = bfs_dist(next, food, ignore_tail);
        
        Pt next_tail = ate_food ? snake_at(0) : snake_at(1);
        int d_tail = bfs_dist(next, next_tail, ignore_tail); 
        
        int safe = (d_tail < MAX_GRID) || (nx == next_tail.x && ny == next_tail.y);
        
        if (safe) {
            if (d_food < min_food_dist) {
                min_food_dist = d_food;
                best_dir = d;
            }
        } else {
            if (best_dir == -1 && d_tail > max_tail_dist) {
                max_tail_dist = d_tail < MAX_GRID ? d_tail : 0;
                best_dir = d;
            }
        }
    }
    
    if (best_dir == -1) {
        for (int d = 0; d < 4; d++) {
            int nx = head.x + DX[d];
            int ny = head.y + DY[d];
            if (!is_body(nx, ny, 1)) {
                best_dir = d;
                break;
            }
        }
    }
    
    if (best_dir == -1) return;
    
    sdir = best_dir;
    int nx = head.x + DX[sdir];
    int ny = head.y + DY[sdir];
    int ate = (nx == food.x && ny == food.y);
    
    if (!ate) {
        Pt old_tail = snake_at(0);
        erase_cell(old_tail.x, old_tail.y);
    }
    
    shead = (shead + 1) % SNAKE_MAX;
    sbuf[shead].x = nx;
    sbuf[shead].y = ny;
    
    if (ate) {
        if (slen < SNAKE_MAX) slen++;
        food_spawn();
        draw_food();
    }
    
    if (slen >= cfg_max_length) {
        clear();
        pick_color();
        snake_init();
        food_spawn();
        snake_draw();
        draw_food();
        return;
    }
    
    snake_draw();
    draw_food();
}

"""

text = text[:start1] + new_ai + text[end1:]

with open("src/madsnake.c", "w") as f:
    f.write(text)
