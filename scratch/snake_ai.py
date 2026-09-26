import re

with open("src/madsnake.c", "r") as f:
    text = f.read()

start_idx = text.find("/* ── BFS pathfinding")
end_idx = text.find("/* ── Movement")

if start_idx == -1 or end_idx == -1:
    print("Could not find blocks")
    exit(1)

new_ai = """/* ── AI & Pathfinding ──────────────────────────────────── */

#define MAX_GRID (300 * 120)

/* Helper to check if a cell is on the current snake body.
   ignore_tail > 0 means we treat the last `ignore_tail` segments as empty. */
static int is_body(int gx, int gy, int ignore_tail)
{
    if (gx < 0 || gx >= grid_w || gy < 0 || gy >= grid_h) return 1; /* wall is solid */
    for (int i = ignore_tail; i < slen; i++) {
        Pt s = snake_at(i);
        if (s.x == gx && s.y == gy) return 1;
    }
    return 0;
}

/* Returns distance from start to target.
   If target cannot be reached, returns MAX_GRID.
   ignore_tail allows treating the tail as empty. */
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

"""

text = text[:start_idx] + new_ai + text[end_idx:]

with open("src/madsnake.c", "w") as f:
    f.write(text)
